import re
import unicodedata

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
