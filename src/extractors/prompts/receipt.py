"""Receipt extraction prompt."""

RECEIPT_EXTRACTION_PROMPT = """You are analyzing a receipt image. Extract all information into a structured format.

## Merchant Information
- Merchant/store name
- Address
- Phone number

## Transaction Details
- Receipt number
- Date (YYYY-MM-DD)
- Time (HH:MM:SS in 24h format)

## Items Purchased
For each item:
- Description/name
- Quantity
- Unit price
- Line total

## Payment Summary
- Subtotal
- Tax amount
- Tip amount (if applicable)
- Total
- Currency

## Payment Method
- Payment type (cash, credit, debit)
- Card last 4 digits (if shown)

## Category
Determine the receipt category:
- food_dining (restaurants, cafes)
- grocery (supermarkets)
- retail (clothing, electronics)
- travel (hotels, transport)
- entertainment (movies, events)
- services (dry cleaning, repairs)
- healthcare (pharmacy, medical)
- fuel (gas stations)
- other

Respond with JSON:
```json
{
    "merchant": {
        "name": "string",
        "address": "string or null",
        "phone": "string or null"
    },
    "receipt_number": "string or null",
    "transaction_date": "YYYY-MM-DD",
    "transaction_time": "HH:MM:SS or null",

    "line_items": [
        {
            "description": "string",
            "quantity": 1.0,
            "unit_price": 0.00,
            "line_total": 0.00
        }
    ],

    "subtotal": 0.00,
    "tax_amount": 0.00,
    "tip_amount": 0.00,
    "total_amount": 0.00,
    "currency": "USD",

    "payment_method": "string or null",
    "card_last_four": "string or null",

    "category": "string",

    "extraction_confidence": 0.95,
    "warnings": []
}
```

Important:
- Extract all visible line items
- Calculate totals if not clearly shown
- Identify payment method from receipt details
- Choose most appropriate category
"""
