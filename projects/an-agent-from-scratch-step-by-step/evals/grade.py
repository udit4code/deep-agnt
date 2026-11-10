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


import re

def turn_stats(summary):
    """Parse trace summary output and return a list of turn statistics dictionaries."""
    if isinstance(summary, str):
        lines = summary.strip().splitlines()
    else:
      # If summary is already a collection of lines
        lines = summary
        
    turns_data = {}
    
    for line in lines:
        parsed = parse_trace_line(line)
        if not parsed:
            continue
            
        turn_num, rest = parsed
        
        # Initialize dictionary for this turn if not already present
        if turn_num not in turns_data:
            turns_data[turn_num] = {
                "turn": turn_num,
                "stop": None,
                "in": 0,
                "out": 0,
                "errors": 0
            }
            
        # Extract stop reason, input tokens, and output tokens
        stop_match = re.search(r"stop=([^\s]+)", rest)
        if stop_match:
            turns_data[turn_num]["stop"] = stop_match.group(1).strip("'\"")
            
        in_match = re.search(r"in=(\d+)", rest)
        if in_match:
            turns_data[turn_num]["in"] = int(in_match.group(1))
            
        out_match = re.search(r"out=(\d+)", rest)
        if out_match:
            turns_data[turn_num]["out"] = int(out_match.group(1))
            
        # Count tool result error lines
        if "tool_result" in rest and ("is_error" in rest.lower() or "error" in rest.lower()):
            turns_data[turn_num]["errors"] += 1
            
    # Return sorted by turn number order
    return [turns_data[t] for t in sorted(turns_data.keys())]


def first_error_turn(summary):
    """Return the turn number of the first turn that contains errors, or None if no errors exist."""
    for stat in turn_stats(summary):
        if stat.get("errors", 0) > 0:
            return stat["turn"]
    return None
