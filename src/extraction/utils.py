"""
Utility functions for filename sanitization and string manipulations.

Provides helper routines to sanitize file and folder names across different filesystems.
"""

import re
import unicodedata


def sanitizeFilename(filename: str) -> str:
    """
    Sanitizes a string for use as a valid filename across operating systems.

    Normalizes Unicode characters, strips reserved characters and emojis, and
    replaces whitespace sequences with underscores.

    Args:
        filename (str): The raw string to sanitize.

    Returns:
        str: The sanitized, filesystem-safe filename string.
    """
    # Normalizes Unicode characters to their closest ASCII equivalents.
    normalized_text = unicodedata.normalize('NFKD', filename)
    ascii_text = normalized_text.encode('ascii', 'ignore').decode('ascii')

    # Strips filesystem reserved symbols to avoid path traversal and invalid characters.
    cleaned_text = re.sub(r'[\\/*?:",<>|]', "", ascii_text)

    # Removes remaining non-alphanumeric characters while preserving hyphens and underscores.
    cleaned_text = re.sub(r'[^\w\s-]', '', cleaned_text).strip()

    # Converts whitespace sequences to underscores for consistent cross-platform naming.
    sanitized = re.sub(r'\s+', '_', cleaned_text)

    # Enforces a fallback default name if all characters were stripped.
    if not sanitized:
        sanitized = "video"

    return sanitized
