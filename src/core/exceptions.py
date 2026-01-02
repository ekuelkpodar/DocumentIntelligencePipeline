"""Custom exceptions for document intelligence pipeline."""


class DocumentIntelligenceError(Exception):
    """Base exception for all document intelligence errors."""

    pass


class ValidationError(DocumentIntelligenceError):
    """Raised when validation fails."""

    pass


class ProcessingError(DocumentIntelligenceError):
    """Raised when document processing fails."""

    pass


class ExtractionError(DocumentIntelligenceError):
    """Raised when data extraction fails."""

    pass


class StorageError(DocumentIntelligenceError):
    """Raised when storage operations fail."""

    pass


# File-related exceptions
class FileSizeExceededError(ValidationError):
    """Raised when file size exceeds maximum allowed."""

    def __init__(self, size_mb: float, max_mb: int) -> None:
        self.size_mb = size_mb
        self.max_mb = max_mb
        super().__init__(f"File size {size_mb:.2f}MB exceeds maximum allowed {max_mb}MB")


class UnsupportedFileTypeError(ValidationError):
    """Raised when file type is not supported."""

    def __init__(self, mime_type: str, allowed_types: list[str]) -> None:
        self.mime_type = mime_type
        self.allowed_types = allowed_types
        super().__init__(
            f"File type '{mime_type}' is not supported. Allowed types: {', '.join(allowed_types)}"
        )


class DuplicateDocumentError(ValidationError):
    """Raised when a duplicate document is detected."""

    def __init__(self, file_hash: str, existing_document_id: str) -> None:
        self.file_hash = file_hash
        self.existing_document_id = existing_document_id
        super().__init__(
            f"Document with hash {file_hash} already exists (ID: {existing_document_id})"
        )


# PDF-specific exceptions
class PDFProcessingError(ProcessingError):
    """Base exception for PDF processing errors."""

    pass


class EncryptedPDFError(PDFProcessingError):
    """Raised when PDF is encrypted."""

    def __init__(self) -> None:
        super().__init__("PDF is encrypted and cannot be processed")


class PasswordProtectedPDFError(PDFProcessingError):
    """Raised when PDF is password protected."""

    def __init__(self) -> None:
        super().__init__("PDF is password protected")


class CorruptedPDFError(PDFProcessingError):
    """Raised when PDF is corrupted."""

    def __init__(self) -> None:
        super().__init__("PDF file is corrupted or malformed")


class TooManyPagesError(PDFProcessingError):
    """Raised when PDF has too many pages."""

    def __init__(self, page_count: int, max_pages: int) -> None:
        self.page_count = page_count
        self.max_pages = max_pages
        super().__init__(
            f"PDF has {page_count} pages, exceeding maximum allowed {max_pages} pages"
        )


# Image-specific exceptions
class ImageProcessingError(ProcessingError):
    """Base exception for image processing errors."""

    pass


class UnsupportedImageFormatError(ImageProcessingError):
    """Raised when image format is not supported."""

    def __init__(self, format: str) -> None:
        self.format = format
        super().__init__(f"Image format '{format}' is not supported")


class ImageTooLargeError(ImageProcessingError):
    """Raised when image dimensions are too large."""

    def __init__(self, width: int, height: int, max_dimension: int) -> None:
        self.width = width
        self.height = height
        self.max_dimension = max_dimension
        super().__init__(
            f"Image dimensions {width}x{height} exceed maximum dimension {max_dimension}px"
        )


# Extraction exceptions
class ModelTimeoutError(ExtractionError):
    """Raised when AI model times out."""

    def __init__(self, timeout_seconds: int) -> None:
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Model extraction timed out after {timeout_seconds} seconds")


class ModelAPIError(ExtractionError):
    """Raised when AI model API returns an error."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"{provider} API error: {message}")


class InvalidExtractionResponseError(ExtractionError):
    """Raised when extraction response cannot be parsed."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid extraction response: {reason}")


# Storage exceptions
class FileNotFoundError(StorageError):
    """Raised when file is not found in storage."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"File not found in storage: {path}")


class StorageConnectionError(StorageError):
    """Raised when storage connection fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Storage connection error: {message}")


# Database exceptions
class DatabaseError(DocumentIntelligenceError):
    """Base exception for database errors."""

    pass


class RecordNotFoundError(DatabaseError):
    """Raised when database record is not found."""

    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with identifier '{identifier}' not found")


class RecordAlreadyExistsError(DatabaseError):
    """Raised when trying to create a duplicate record."""

    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with identifier '{identifier}' already exists")
