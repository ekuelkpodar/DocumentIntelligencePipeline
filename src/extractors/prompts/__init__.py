"""Extraction prompts for different document types."""

from src.extractors.prompts.invoice import (
    INVOICE_EXTRACTION_PROMPT,
    INVOICE_FEW_SHOT_EXAMPLES,
)
from src.extractors.prompts.receipt import RECEIPT_EXTRACTION_PROMPT
from src.extractors.prompts.menu import MENU_EXTRACTION_PROMPT
from src.extractors.prompts.classification import CLASSIFICATION_PROMPT

__all__ = [
    "CLASSIFICATION_PROMPT",
    "INVOICE_EXTRACTION_PROMPT",
    "INVOICE_FEW_SHOT_EXAMPLES",
    "RECEIPT_EXTRACTION_PROMPT",
    "MENU_EXTRACTION_PROMPT",
]
