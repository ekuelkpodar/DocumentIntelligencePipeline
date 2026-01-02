"""Document classification prompt."""

CLASSIFICATION_PROMPT = """Look at this document image and determine what type of document it is.

Analyze the document carefully and identify its type based on layout, content, and common document patterns.

**Document Types:**
- **invoice**: Commercial invoices with vendor/customer info, line items, totals, payment terms
- **receipt**: Purchase receipts from stores/restaurants with merchant info, items, payment details
- **menu**: Restaurant menus with dishes, descriptions, prices
- **form**: Structured forms with labeled fields (applications, surveys, etc.)
- **contract**: Legal contracts with parties, terms, signatures
- **unknown**: Cannot determine or doesn't fit other categories

Respond with a JSON object:
```json
{
    "document_type": "invoice" | "receipt" | "menu" | "form" | "contract" | "unknown",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why you classified it this way"
}
```

Important:
- Base classification on visual layout and content structure
- Use confidence score between 0.0 and 1.0
- Provide clear reasoning for your classification
"""
