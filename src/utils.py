import re

def sanitize_filename(filename):
    """
    Sanitizes a string to be used as a valid filename.
    - Removes illegal characters: \ / : * ? " < > |
    - Removes emojis and other symbols.
    - Replaces spaces with underscores.
    """
    # Remove illegal characters for filenames
    filename = re.sub(r'[\\/*?:",<>|]', "", filename)
    # Remove emojis and other non-word characters (leaving whitespace and hyphens)
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    return filename
