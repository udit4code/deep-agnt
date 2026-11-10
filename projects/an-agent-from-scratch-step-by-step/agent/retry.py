def is_retryable(error):
    """Return True for an error whose .status is 429 or 529, and False otherwise."""
    status = getattr(error, "status", None)
    return status in (429, 529)


def backoff_delay(attempt, base=0.5):
    """Return base * 2 ** attempt for exponential backoff calculations."""
    return base * (2 ** attempt)


def retry_after(headers):
    """Return the Retry-After header as an int of seconds, or None when invalid/missing."""
    if headers is None:
        return None
    
    # Perform a case-insensitive lookup for the "Retry-After" header
    val = None
    for k, v in headers.items():
        if k.lower() == "retry-after":
            val = v
            break
            
    if val is None:
        return None
        
    try:
        # If it's already an integer
        if isinstance(val, int):
            return val
        
        # If it's a float, ensure it represents a whole number
        if isinstance(val, float):
            if val.is_integer():
                return int(val)
            return None
            
        # Parse string representation
        s = str(val).strip()
        f = float(s)
        if f.is_integer():
            return int(f)
        return None
    except (ValueError, TypeError):
        return None
