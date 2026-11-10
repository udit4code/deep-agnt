def is_retryable(error):
    """Return True for an error whose .status is 429 or 529, and False otherwise."""
    status = getattr(error, "status", None)
    return status in (429, 529)


def backoff_delay(attempt, base=0.5):
    """Return base * 2 ** attempt for exponential backoff calculations."""
    return base * (2 ** attempt)
