"""Core application logic and exceptions."""

from src.core.exceptions import (
    CorruptedPDFError,
    DocumentIntelligenceError,
    DuplicateDocumentError,
    EncryptedPDFError,
    ExtractionError,
    FileSizeExceededError,
    ProcessingError,
    StorageError,
    UnsupportedFileTypeError,
    ValidationError,
)

__all__ = [
    "DocumentIntelligenceError",
    "ValidationError",
    "ProcessingError",
    "ExtractionError",
    "StorageError",
    "FileSizeExceededError",
    "UnsupportedFileTypeError",
    "DuplicateDocumentError",
    "EncryptedPDFError",
    "CorruptedPDFError",
]
