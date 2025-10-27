"""Automatic transaction categorization logic."""
from typing import Optional

# Category rules: keyword matching
CATEGORY_RULES = {
    "food_snack": [
        "family mart", "familymart", "lawson", "7-eleven", "seven eleven",
        "starbucks", "mcdonald", "burger king", "yoshinoya", "sukiya",
        "restaurant", "cafe", "coffee", "ramen", "sushi", "izakaya"
    ],
    "utilities": [
        "japan post", "ntt", "tokyo electric", "tokyo gas", "tepco",
        "softbank", "docomo", "au", "electricity", "gas", "water", "internet"
    ],
    "shopping": [
        "amazon", "rakuten ichiba", "uniqlo", "muji", "daiso", "don quijote",
        "yodobashi", "bic camera", "yamada denki", "mercari"
    ],
    "transport": [
        "suica", "jr east", "metro", "tokyo metro", "train", "taxi",
        "uber", "bus", "parking"
    ],
    "entertainment": [
        "netflix", "spotify", "youtube", "cinema", "movie", "game",
        "nintendo", "playstation", "gym", "fitness"
    ],
    "health": [
        "hospital", "clinic", "pharmacy", "drug", "medical", "dental",
        "doctor", "matsumoto kiyoshi"
    ],
    "education": [
        "school", "university", "book", "course", "lesson", "tuition"
    ],
}


def categorize_transaction(vendor: str) -> Optional[str]:
    """
    Automatically categorize a transaction based on vendor name.

    Args:
        vendor: Vendor/merchant name

    Returns:
        Category name or None if no match found
    """
    vendor_lower = vendor.lower().strip()

    # Check each category's keywords
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in vendor_lower:
                return category

    # Default category if no match
    return "other"


def get_category_display_name(category: str) -> str:
    """
    Get human-readable display name for category.

    Args:
        category: Category internal name

    Returns:
        Display name
    """
    display_names = {
        "food_snack": "Food & Snacks",
        "utilities": "Utilities",
        "shopping": "Shopping",
        "transport": "Transportation",
        "entertainment": "Entertainment",
        "health": "Health & Medical",
        "education": "Education",
        "other": "Other",
    }
    return display_names.get(category, category.title())


def get_category_icon(category: str) -> str:
    """
    Get emoji icon for category.

    Args:
        category: Category internal name

    Returns:
        Emoji icon
    """
    icons = {
        "food_snack": "🍔",
        "utilities": "💡",
        "shopping": "🛍️",
        "transport": "🚇",
        "entertainment": "🎬",
        "health": "🏥",
        "education": "📚",
        "other": "📦",
    }
    return icons.get(category, "📦")


def get_category_color(category: str) -> str:
    """
    Get color code for category (for UI visualization).

    Args:
        category: Category internal name

    Returns:
        Hex color code
    """
    colors = {
        "food_snack": "#FF6B6B",      # Red
        "utilities": "#4ECDC4",       # Teal
        "shopping": "#FFE66D",        # Yellow
        "transport": "#95E1D3",       # Mint
        "entertainment": "#F38181",   # Pink
        "health": "#AA96DA",          # Purple
        "education": "#FCBAD3",       # Light Pink
        "other": "#A8DADC",           # Light Blue
    }
    return colors.get(category, "#CCCCCC")
