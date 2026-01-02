"""Invoice extraction prompt and examples."""

INVOICE_EXTRACTION_PROMPT = """You are a document extraction specialist. Analyze this invoice image and extract all relevant information into a structured format.

Extract the following information:

## Header Information
- Invoice number
- Invoice date (YYYY-MM-DD format)
- Due date (YYYY-MM-DD format)
- Purchase order number (if present)

## Vendor Information
- Vendor/Supplier name
- Vendor address (full address as single string)
- Vendor tax ID / VAT number
- Vendor email
- Vendor phone

## Customer/Bill To Information
- Customer name
- Customer address
- Customer account number

## Line Items
For each item, extract:
- Line number
- Item code/SKU (if present)
- Description
- Quantity
- Unit (each, hour, kg, etc.)
- Unit price
- Discount percentage (if any)
- Tax percentage (if any)
- Line total

## Financial Summary
- Subtotal (before tax)
- Tax amount
- Tax rate/percentage
- Discount amount
- Shipping/freight amount
- Total amount
- Currency (3-letter code, e.g., USD, EUR)

## Payment Information
- Payment terms (e.g., Net 30, Due on Receipt)
- Payment method
- Bank account / routing info (if present)

## Additional
- Notes or comments

Respond with a JSON object matching this exact schema:
```json
{
    "invoice_number": "string or null",
    "invoice_date": "YYYY-MM-DD or null",
    "due_date": "YYYY-MM-DD or null",
    "purchase_order_number": "string or null",

    "vendor": {
        "name": "string",
        "address": "string or null",
        "tax_id": "string or null",
        "email": "string or null",
        "phone": "string or null"
    },

    "customer": {
        "name": "string or null",
        "address": "string or null",
        "account_number": "string or null"
    },

    "line_items": [
        {
            "line_number": 1,
            "item_code": "string or null",
            "description": "string",
            "quantity": 1.0,
            "unit": "string or null",
            "unit_price": 0.00,
            "discount_percent": 0.00,
            "tax_percent": 0.00,
            "line_total": 0.00
        }
    ],

    "subtotal": 0.00,
    "tax_amount": 0.00,
    "tax_rate": 0.00,
    "discount_amount": 0.00,
    "shipping_amount": 0.00,
    "total_amount": 0.00,
    "currency": "USD",

    "payment_terms": "string or null",
    "payment_method": "string or null",
    "bank_account": "string or null",

    "notes": "string or null",

    "extraction_confidence": 0.95,
    "warnings": ["List any issues or uncertainties"]
}
```

Important:
- Use null for any fields you cannot find or are uncertain about
- Ensure all monetary values are numbers, not strings
- Ensure dates are in YYYY-MM-DD format
- If a value is unclear, include a warning explaining the uncertainty
- Calculate line totals if not explicitly shown
- Verify that line items sum to subtotal (note discrepancy in warnings if not)
"""

INVOICE_FEW_SHOT_EXAMPLES = [
    {
        "description": "Standard commercial invoice",
        "context": "Professional invoice from ACME Corp with 5 line items, clear structure",
    },
]
