def is_retryable(error):
    """Return True for an error whose .status is 429 or 529, and False otherwise."""
    status = getattr(error, "status", None)
    return status in (429, 529)
