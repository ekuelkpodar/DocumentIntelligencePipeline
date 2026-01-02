"""PDF document processor."""

import io
import time
from typing import BinaryIO

from pdf2image import convert_from_bytes
from PIL import Image
from pypdf import PdfReader

from src.core.exceptions import (
    CorruptedPDFError,
    EncryptedPDFError,
    PasswordProtectedPDFError,
    TooManyPagesError,
)
from src.processors.base import BaseProcessor, ProcessedDocument, ProcessedPage
from src.utils.hashing import calculate_file_hash
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents."""

    SUPPORTED_MIME_TYPES = ["application/pdf"]
    MIN_TEXT_CHARS_PER_PAGE = 100  # Threshold for scanned PDF detection

    def __init__(
        self,
        dpi: int = 200,
        max_dimension: int = 2000,
        max_pages: int = 100,
        jpeg_quality: int = 85,
    ):
        """
        Initialize PDF processor.

        Args:
            dpi: DPI for PDF to image conversion
            max_dimension: Maximum dimension for resized images
            max_pages: Maximum number of pages allowed
            jpeg_quality: JPEG compression quality (1-100)
        """
        self.dpi = dpi
        self.max_dimension = max_dimension
        self.max_pages = max_pages
        self.jpeg_quality = jpeg_quality

    def supports(self, mime_type: str) -> bool:
        """Check if PDF MIME type is supported."""
        return mime_type in self.SUPPORTED_MIME_TYPES

    async def process(self, file: BinaryIO, filename: str) -> ProcessedDocument:
        """
        Process PDF document.

        Args:
            file: PDF file object
            filename: Original filename

        Returns:
            ProcessedDocument with all pages

        Raises:
            EncryptedPDFError: If PDF is encrypted
            PasswordProtectedPDFError: If PDF is password protected
            CorruptedPDFError: If PDF is corrupted
            TooManyPagesError: If PDF exceeds max pages
        """
        start_time = time.time()
        logger.info("processing_pdf", filename=filename)

        # Read file bytes
        file.seek(0)
        pdf_bytes = file.read()
        file.seek(0)

        # Calculate file hash
        file_hash = calculate_file_hash(file)

        # Extract metadata and validate PDF
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
        except Exception as e:
            logger.error("pdf_read_failed", filename=filename, error=str(e))
            raise CorruptedPDFError()

        # Check for encryption
        if reader.is_encrypted:
            logger.error("pdf_encrypted", filename=filename)
            raise EncryptedPDFError()

        # Get page count
        page_count = len(reader.pages)
        logger.info("pdf_page_count", filename=filename, pages=page_count)

        if page_count > self.max_pages:
            raise TooManyPagesError(page_count, self.max_pages)

        # Extract PDF metadata
        metadata = self._extract_metadata(reader)

        # Convert pages to images
        try:
            images = convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt="jpeg",
                thread_count=4,
            )
        except Exception as e:
            logger.error("pdf_to_image_failed", filename=filename, error=str(e))
            raise CorruptedPDFError()

        # Process each page
        processed_pages: list[ProcessedPage] = []
        for page_num, image in enumerate(images, start=1):
            # Extract text from PDF page
            try:
                text_content = reader.pages[page_num - 1].extract_text()
            except Exception as e:
                logger.warning(
                    "text_extraction_failed",
                    filename=filename,
                    page=page_num,
                    error=str(e),
                )
                text_content = ""

            # Determine if page is scanned
            is_scanned = self._is_scanned_page(text_content, page_num)

            # Optimize image
            optimized_image, image_format = self._optimize_image(image, is_scanned)

            # Create ProcessedPage
            page = ProcessedPage(
                page_number=page_num,
                image_bytes=optimized_image,
                image_format=image_format,
                width=image.width,
                height=image.height,
                dpi=self.dpi,
                text_content=text_content if text_content else None,
                is_scanned=is_scanned,
                metadata={
                    "original_width": image.width,
                    "original_height": image.height,
                },
            )
            processed_pages.append(page)

            logger.debug(
                "page_processed",
                filename=filename,
                page=page_num,
                is_scanned=is_scanned,
                text_length=len(text_content) if text_content else 0,
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "pdf_processing_complete",
            filename=filename,
            pages=page_count,
            duration_ms=processing_time_ms,
        )

        return ProcessedDocument(
            original_filename=filename,
            mime_type="application/pdf",
            file_hash=file_hash,
            total_pages=page_count,
            pages=processed_pages,
            metadata=metadata,
            processing_time_ms=processing_time_ms,
        )

    def _extract_metadata(self, reader: PdfReader) -> dict:
        """Extract metadata from PDF."""
        metadata = {}

        if reader.metadata:
            metadata.update(
                {
                    "title": reader.metadata.get("/Title"),
                    "author": reader.metadata.get("/Author"),
                    "subject": reader.metadata.get("/Subject"),
                    "creator": reader.metadata.get("/Creator"),
                    "producer": reader.metadata.get("/Producer"),
                    "creation_date": str(reader.metadata.get("/CreationDate")),
                    "modification_date": str(reader.metadata.get("/ModDate")),
                }
            )

        # Remove None values
        return {k: v for k, v in metadata.items() if v is not None}

    def _is_scanned_page(self, text: str, page_number: int) -> bool:
        """
        Determine if a page is scanned (image-based) based on extracted text.

        Args:
            text: Extracted text from page
            page_number: Page number

        Returns:
            True if page appears to be scanned
        """
        if not text or len(text.strip()) < self.MIN_TEXT_CHARS_PER_PAGE:
            logger.debug(
                "page_detected_as_scanned",
                page=page_number,
                text_length=len(text) if text else 0,
            )
            return True
        return False

    def _optimize_image(
        self, image: Image.Image, is_scanned: bool
    ) -> tuple[bytes, str]:
        """
        Optimize image for API transmission.

        Args:
            image: PIL Image object
            is_scanned: Whether image is from scanned document

        Returns:
            Tuple of (optimized_image_bytes, format)
        """
        # Convert to RGB if necessary
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # Resize if dimensions exceed maximum
        width, height = image.size
        max_dim = max(width, height)

        if max_dim > self.max_dimension:
            scale = self.max_dimension / max_dim
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.debug(
                "image_resized",
                original_size=(width, height),
                new_size=(new_width, new_height),
            )

        # Choose format based on content
        # Use PNG for text-heavy documents to preserve clarity
        # Use JPEG for scanned images to reduce size
        if is_scanned:
            # JPEG compression for scanned images
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)
            return buffer.getvalue(), "jpeg"
        else:
            # PNG for digital PDFs with text
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            return buffer.getvalue(), "png"
