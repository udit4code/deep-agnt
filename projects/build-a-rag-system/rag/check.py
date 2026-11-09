import re

def sentences(text):
    """Splits text into sentences after a ., !, or ? followed by whitespace, stripping and dropping empty ones."""
    if not text:
        return []
    
    # Split after a ., !, or ? that is followed by one or more whitespace characters
    parts = re.split(r'(?<=[.!?])\s+', text)
    
    # Strip each piece and filter out any empty strings
    return [p.strip() for p in parts if p.strip()]
