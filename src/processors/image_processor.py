"""Image document processor with preprocessing capabilities."""

import io
import time
from typing import BinaryIO

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from PIL.ExifTags import TAGS

from src.core.exceptions import ImageProcessingError, UnsupportedImageFormatError
from src.processors.base import BaseProcessor, ProcessedDocument, ProcessedPage
from src.utils.hashing import calculate_file_hash
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ImageProcessor(BaseProcessor):
    """Processor for image documents (JPEG, PNG, WebP, TIFF)."""

    SUPPORTED_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
    ]

    def __init__(
        self,
        max_dimension: int = 2000,
        target_dpi: int = 200,
        auto_rotate: bool = True,
        deskew: bool = True,
        enhance_contrast: bool = False,
        denoise: bool = False,
        jpeg_quality: int = 85,
    ):
        """
        Initialize image processor.

        Args:
            max_dimension: Maximum dimension for resized images
            target_dpi: Target DPI for output
            auto_rotate: Apply EXIF rotation
            deskew: Correct slight rotations
            enhance_contrast: Apply contrast enhancement
            denoise: Apply denoising
            jpeg_quality: JPEG compression quality
        """
        self.max_dimension = max_dimension
        self.target_dpi = target_dpi
        self.auto_rotate = auto_rotate
        self.deskew = deskew
        self.enhance_contrast = enhance_contrast
        self.denoise = denoise
        self.jpeg_quality = jpeg_quality

    def supports(self, mime_type: str) -> bool:
        """Check if image MIME type is supported."""
        return mime_type in self.SUPPORTED_MIME_TYPES

    async def process(self, file: BinaryIO, filename: str) -> ProcessedDocument:
        """
        Process image document.

        Args:
            file: Image file object
            filename: Original filename

        Returns:
            ProcessedDocument with processed image

        Raises:
            UnsupportedImageFormatError: If image format not supported
            ImageProcessingError: If processing fails
        """
        start_time = time.time()
        logger.info("processing_image", filename=filename)

        # Read file bytes
        file.seek(0)
        image_bytes = file.read()
        file.seek(0)

        # Calculate file hash
        file_hash = calculate_file_hash(file)

        # Load image with PIL
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error("image_load_failed", filename=filename, error=str(e))
            raise ImageProcessingError(f"Failed to load image: {str(e)}")

        # Extract EXIF metadata
        metadata = self._extract_exif(image)
        original_format = image.format

        if not original_format:
            raise UnsupportedImageFormatError("unknown")

        logger.info(
            "image_loaded",
            filename=filename,
            format=original_format,
            size=image.size,
            mode=image.mode,
        )

        # Apply auto-rotation based on EXIF
        if self.auto_rotate:
            image = self._apply_exif_rotation(image)

        # Convert to RGB
        if image.mode not in ("RGB", "L"):
            logger.debug("converting_to_rgb", original_mode=image.mode)
            if image.mode == "RGBA":
                # Create white background for transparent images
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert("RGB")

        # Apply preprocessing
        if self.deskew or self.enhance_contrast or self.denoise:
            image = await self._preprocess_image(image)

        # Resize if needed
        image = self._resize_image(image)

        # Optimize and convert to bytes
        optimized_bytes, output_format = self._optimize_image(image)

        # Create ProcessedPage
        processed_page = ProcessedPage(
            page_number=1,
            image_bytes=optimized_bytes,
            image_format=output_format,
            width=image.width,
            height=image.height,
            dpi=self.target_dpi,
            text_content=None,  # Will be filled by OCR if needed
            is_scanned=True,  # Images are always considered scanned
            metadata={
                "original_format": original_format,
                "exif": metadata,
            },
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "image_processing_complete",
            filename=filename,
            duration_ms=processing_time_ms,
        )

        # Determine MIME type from original format
        mime_type = self._get_mime_type(original_format)

        return ProcessedDocument(
            original_filename=filename,
            mime_type=mime_type,
            file_hash=file_hash,
            total_pages=1,
            pages=[processed_page],
            metadata=metadata,
            processing_time_ms=processing_time_ms,
        )

    def _extract_exif(self, image: Image.Image) -> dict:
        """Extract EXIF metadata from image."""
        metadata = {}

        try:
            exif = image.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        try:
                            value = value.decode()
                        except:
                            value = str(value)
                    metadata[tag] = value
        except Exception as e:
            logger.debug("exif_extraction_failed", error=str(e))

        return metadata

    def _apply_exif_rotation(self, image: Image.Image) -> Image.Image:
        """Apply EXIF orientation rotation."""
        try:
            exif = image.getexif()
            orientation = exif.get(274)  # Orientation tag

            if orientation:
                rotation_map = {
                    3: 180,
                    6: 270,
                    8: 90,
                }
                if orientation in rotation_map:
                    degrees = rotation_map[orientation]
                    logger.debug("rotating_image", degrees=degrees)
                    image = image.rotate(degrees, expand=True)
        except Exception as e:
            logger.debug("exif_rotation_failed", error=str(e))

        return image

    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Apply preprocessing to enhance image quality."""
        # Convert PIL Image to OpenCV format
        img_array = np.array(image)

        if self.deskew:
            img_array = self._deskew_image(img_array)

        if self.denoise:
            img_array = self._denoise_image(img_array)

        # Convert back to PIL Image
        image = Image.fromarray(img_array)

        if self.enhance_contrast:
            image = self._enhance_contrast(image)

        return image

    def _deskew_image(self, img_array: np.ndarray) -> np.ndarray:
        """
        Deskew image using Hough line transform.

        Args:
            img_array: Image as numpy array

        Returns:
            Deskewed image array
        """
        try:
            # Convert to grayscale for processing
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

            if lines is not None and len(lines) > 0:
                # Calculate median angle
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = np.degrees(theta) - 90
                    angles.append(angle)

                median_angle = np.median(angles)

                # Only deskew if angle is small (< 10 degrees)
                if abs(median_angle) < 10 and abs(median_angle) > 0.5:
                    logger.debug("deskewing_image", angle=median_angle)
                    # Get image dimensions
                    (h, w) = img_array.shape[:2]
                    center = (w // 2, h // 2)

                    # Perform rotation
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    img_array = cv2.warpAffine(
                        img_array,
                        M,
                        (w, h),
                        flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_REPLICATE,
                    )
        except Exception as e:
            logger.debug("deskew_failed", error=str(e))

        return img_array

    def _denoise_image(self, img_array: np.ndarray) -> np.ndarray:
        """Apply denoising to image."""
        try:
            if len(img_array.shape) == 3:
                img_array = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
            else:
                img_array = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
            logger.debug("denoising_applied")
        except Exception as e:
            logger.debug("denoise_failed", error=str(e))

        return img_array

    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance contrast using PIL."""
        try:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)  # Increase contrast by 50%
            logger.debug("contrast_enhanced")
        except Exception as e:
            logger.debug("contrast_enhancement_failed", error=str(e))

        return image

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image if dimensions exceed maximum."""
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

        return image

    def _optimize_image(self, image: Image.Image) -> tuple[bytes, str]:
        """Optimize image for storage and API transmission."""
        buffer = io.BytesIO()

        # Always use JPEG for processed images to reduce size
        image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)

        return buffer.getvalue(), "jpeg"

    def _get_mime_type(self, image_format: str) -> str:
        """Get MIME type from image format."""
        format_map = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
            "TIFF": "image/tiff",
        }
        return format_map.get(image_format.upper(), "image/jpeg")
