import re

def parse_trace_line(line):
    """Parse a trace line starting with [n], returning a tuple of (n, rest) or None if it doesn't match."""
    match = re.match(r"^\[(\d+)\](.*)$", line)
    if not match:
        return None
    n = int(match.group(1))
    rest = match.group(2).strip()
    return (n, rest)
