# utils.py Documentation

## Navigation Table

| Name | Type | Description |
|------|------|-------------|
| [sanitizeFilename](#sanitizefilename) | Function | Sanitizes a string for use as a valid filename. |

## Overview
The `utils` module provides helper functions used across the application. Currently, it focuses on string sanitization to ensure compliance with filesystem naming conventions.

## Detailed Breakdown

### sanitizeFilename

**Signature:**
```python
def sanitizeFilename(filename: str) -> str
```

**Purpose:** Sanitizes a string for use as a valid filename.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| filename | str | Yes | — | The string to sanitize. |

**Returns:**
| Type | Description |
|------|-------------|
| str | The sanitized filename. |

**Source Code:**
```python
def sanitizeFilename(filename):
    """
    Sanitizes a string for use as a valid filename.

    Removes illegal characters, emojis, and extra whitespace, and replaces
    spaces with underscores to ensure compatibility across filesystems.

    Args:
        filename (str): The string to sanitize.

    Returns:
        str: The sanitized filename.
    """
    # Normalize Unicode characters to closest ASCII equivalents
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove illegal characters: \ / : * ? " < > |
    filename = re.sub(r'[\\/*?:",<>|]', "", filename)
    
    # Remove any remaining non-alphanumeric characters (keep spaces, hyphens, underscores)
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    
    # Replace whitespace sequences with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Ensure filename is not empty
    if not filename:
        filename = "video"
    
    return filename
```

**Implementation (Executable Logic Only):**
* **Line 18:** `filename = unicodedata.normalize('NFKD', filename)` — Decomposes unicode characters.
* **Line 19:** `filename = filename.encode('ascii', 'ignore').decode('ascii')` — Strips non-ASCII chars.
* **Line 22:** `filename = re.sub(r'[\\/*?:",<>|]', "", filename)` — Removes filesystem reserved chars.
* **Line 25:** `filename = re.sub(r'[^\w\s-]', '', filename).strip()` — Cleans special symbols.
* **Line 28:** `filename = re.sub(r'\s+', '_', filename)` — Standardizes spacing.
* **Line 31:** `if not filename:` — Checks validation result.
* **Line 32:** `filename = "video"` — Provides fallback default.
* **Line 34:** `return filename` — Returns safe string.

**Dependencies:**
| Symbol | Kind | Purpose | Source |
|--------|------|---------|--------|
| re | External | Regex operations | re |
| unicodedata | External | Unicode normalization | unicodedata |