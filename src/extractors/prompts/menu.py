"""Menu extraction prompt."""

MENU_EXTRACTION_PROMPT = """You are analyzing a restaurant menu image. Extract all menu items with details.

## Restaurant Information
- Restaurant name
- Cuisine type (italian, mexican, american, etc.)
- Menu type (lunch, dinner, drinks, dessert, full)

## Menu Items
For each item, extract:
- Category (Appetizers, Salads, Entrees, etc.)
- Item name
- Description
- Price
- Currency

## Dietary Information (when indicated)
- Is vegetarian (V symbol, "vegetarian", etc.)
- Is vegan
- Is gluten-free (GF symbol)
- Is spicy (chili symbol, "spicy")
- Spice level (1-5 if indicated)
- Allergens mentioned (nuts, dairy, shellfish, etc.)
- Calories (if shown)

Respond with JSON:
```json
{
    "restaurant": {
        "name": "string or null",
        "cuisine_type": "string or null",
        "menu_type": "string"
    },

    "items": [
        {
            "category": "string",
            "name": "string",
            "description": "string or null",
            "price": 0.00,
            "currency": "USD",
            "is_vegetarian": false,
            "is_vegan": false,
            "is_gluten_free": false,
            "is_spicy": false,
            "spice_level": null,
            "allergens": [],
            "calories": null
        }
    ],

    "extraction_confidence": 0.95,
    "warnings": []
}
```

Important:
- List ALL menu items visible
- Preserve the category organization
- Note any items with unclear prices in warnings
- Handle market price items (price = null, note in description)
- Look for dietary symbols and indicators
"""
