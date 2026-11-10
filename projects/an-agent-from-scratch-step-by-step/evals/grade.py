import re

def parse_trace_line(line):
    """Parse a trace line starting with [n], returning a tuple of (n, rest) or None if it doesn't match."""
    # Match an opening bracket, one or more digits captured in group 1, a closing bracket,
    # and the remaining string captured in group 2
    match = re.match(r"^\[(\d+)\](.*)$", line)
    
    # Return None if the line does not match the '[n]' format (e.g., summary or total lines)
    if not match:
        return None
    
    # Extract turn number as an integer and strip leading/trailing whitespace from the remainder
    n = int(match.group(1))
    rest = match.group(2).strip()
    
    return (n, rest)
