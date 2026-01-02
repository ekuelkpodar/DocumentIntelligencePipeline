"""Base processor interface for document processing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import BinaryIO


@dataclass
class ProcessedPage:
    """Represents a single processed page from a document."""

    page_number: int
    image_bytes: bytes
    image_format: str  # jpeg, png
    width: int
    height: int
    dpi: int
    text_content: str | None = None  # OCR or extracted text
    is_scanned: bool = False  # True if image-based (needs OCR)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProcessedDocument:
    """Represents a fully processed document with all pages."""

    original_filename: str
    mime_type: str
    file_hash: str
    total_pages: int
    pages: list[ProcessedPage]
    metadata: dict = field(default_factory=dict)
    processing_time_ms: int = 0


class BaseProcessor(ABC):
    """Abstract base class for document processors."""

    @abstractmethod
    async def process(self, file: BinaryIO, filename: str) -> ProcessedDocument:
        """
        Process a document and return normalized pages.

        Args:
            file: Binary file object to process
            filename: Original filename

        Returns:
            ProcessedDocument containing all pages and metadata

        Raises:
            ProcessingError: If processing fails
        """
        pass

    @abstractmethod
    def supports(self, mime_type: str) -> bool:
        """
        Check if this processor supports the given MIME type.

        Args:
            mime_type: MIME type to check

        Returns:
            True if supported, False otherwise
        """
        pass
