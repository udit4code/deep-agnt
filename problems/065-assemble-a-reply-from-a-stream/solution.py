import json


def assemble(events):
    """Reconstructs a streamed response from a sequence of events.
    
    Returns a dict with:
    - 'text': joined text blocks in order
    - 'tool_calls': valid tool calls with parsed arguments
    - 'stop_reason': stop reason string or None
    - 'input_tokens': int (0 if none)
    - 'output_tokens': int (0 if none)
    - 'complete': True only if message_stop was received
    """
    input_tokens = 0
    output_tokens = 0
    stop_reason = None
    complete = False
    
    # Track blocks by their index to handle interleaving deltas correctly
    blocks = {}
    
    for event in events:
        if not isinstance(event, dict):
            continue
            
        etype = event.get("type")
        
        if etype == "message_start":
            # Extract input token usage
            message = event.get("message", {})
            usage = message.get("usage", {})
            input_tokens = usage.get("input_tokens", input_tokens)
            
        elif etype == "content_block_start":
            index = event.get("index")
            cb = event.get("content_block", {})
            cb_type = cb.get("type")
            
            if cb_type == "text":
                blocks[index] = {"type": "text", "pieces": []}
            elif cb_type == "tool_use":
                blocks[index] = {
                    "type": "tool_use",
                    "id": cb.get("id"),
                    "name": cb.get("name"),
                    "pieces": []
                }
                
        elif etype == "content_block_delta":
            index = event.get("index")
            delta = event.get("delta", {})
            if index in blocks:
                dtype = delta.get("type")
                if dtype == "text_delta":
                    blocks[index]["pieces"].append(delta.get("text", ""))
                elif dtype == "input_json_delta":
                    blocks[index]["pieces"].append(delta.get("partial_json", ""))
                    
        elif etype == "content_block_stop":
            # Block finished; accumulation is handled via deltas
            pass
            
        elif etype == "message_delta":
            delta = event.get("delta", {})
            if "stop_reason" in delta:
                stop_reason = delta["stop_reason"]
            usage = event.get("usage", {})
            if "output_tokens" in usage:
                output_tokens = usage["output_tokens"]
                
        elif etype == "message_stop":
            complete = True
            
        elif etype == "error":
            # Extract error message and raise StreamError
            err = event.get("error", "Stream error")
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            raise StreamError(msg)
            
        else:
            # Ignore pings and unrecognized event types
            pass
            
    text_pieces_list = []
    tool_calls_list = []
    
    # Process blocks in sequential block order (sorted by index)
    for index in sorted(blocks.keys()):
        block = blocks[index]
        if block["type"] == "text":
            text_pieces_list.append("".join(block["pieces"]))
        elif block["type"] == "tool_use":
            pieces = block["pieces"]
            if not pieces:
                # No fragments arrived for this tool call
                input_obj = {}
                tool_calls_list.append({
                    "id": block["id"],
                    "name": block["name"],
                    "input": input_obj
                })
            else:
                json_str = "".join(pieces)
                try:
                    # Attempt to parse accumulated argument fragments
                    input_obj = json.loads(json_str)
                    tool_calls_list.append({
                        "id": block["id"],
                        "name": block["name"],
                        "input": input_obj
                    })
                except (json.JSONDecodeError, ValueError):
                    # Truncated or malformed tool call arguments: leave out entirely
                    pass
                    
    return {
        "text": "".join(text_pieces_list),
        "tool_calls": tool_calls_list,
        "stop_reason": stop_reason,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "complete": complete
    }
