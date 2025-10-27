"""Deduplication logic for transactions."""
import hashlib
from datetime import datetime


def generate_transaction_hash(
    vendor: str,
    amount: float,
    timestamp: datetime,
    source: str
) -> str:
    """
    Generate a unique hash for a transaction to detect duplicates.

    Args:
        vendor: Vendor/merchant name
        amount: Transaction amount
        timestamp: Transaction timestamp
        source: Payment source (rakuten_card, paypay, etc.)

    Returns:
        SHA256 hash string
    """
    # Normalize vendor name (lowercase, strip whitespace)
    vendor_normalized = vendor.lower().strip()

    # Create hash input string
    # Format: vendor|amount|date|source
    # Using only date (not time) to catch duplicates across different notification times
    date_str = timestamp.strftime("%Y-%m-%d")
    hash_input = f"{vendor_normalized}|{amount}|{date_str}|{source}"

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(hash_input.encode('utf-8'))
    return hash_obj.hexdigest()


def calculate_string_similarity(str1: str, str2: str) -> float:
    """
    Calculate Levenshtein distance-based similarity between two strings.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    # Simple implementation of Levenshtein distance
    str1 = str1.lower().strip()
    str2 = str2.lower().strip()

    if str1 == str2:
        return 1.0

    len1, len2 = len(str1), len(str2)

    # Create distance matrix
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize first column and row
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j

    # Calculate distances
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,      # deletion
                matrix[i][j - 1] + 1,      # insertion
                matrix[i - 1][j - 1] + cost  # substitution
            )

    # Calculate similarity ratio
    distance = matrix[len1][len2]
    max_len = max(len1, len2)
    similarity = 1.0 - (distance / max_len) if max_len > 0 else 1.0

    return similarity


def is_vendor_similar(vendor1: str, vendor2: str, threshold: float = 0.8) -> bool:
    """
    Check if two vendor names are similar (for fuzzy duplicate detection).

    Args:
        vendor1: First vendor name
        vendor2: Second vendor name
        threshold: Similarity threshold (default 0.8 = 80%)

    Returns:
        True if vendors are similar enough
    """
    similarity = calculate_string_similarity(vendor1, vendor2)
    return similarity >= threshold
