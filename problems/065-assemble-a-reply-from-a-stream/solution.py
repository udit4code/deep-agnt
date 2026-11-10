import json


def assemble(events):
    """Reconstructs a streamed response from a sequence of events.
    
    Approach:
    1. Iterate through the event stream, accumulating content into block buffers
       keyed by their index to handle interleaving deltas safely.
    2. Track token counts, stop reasons, and completion status from lifecycle events.
    3. Post-process blocks: join text pieces and attempt to parse tool call JSON arguments.
       If tool arguments are truncated or malformed, safely omit the tool call.
    """
    state = {
        "input_tokens": 0,
        "output_tokens": 0,
        "stop_reason": None,
        "complete": False,
        "blocks": {}
    }
    
    # Phase 1: Process and accumulate all incoming stream events
    for event in events:
        if not isinstance(event, dict):
            continue
        _process_event(event, state)
        
    # Phase 2: Finalize and structure the accumulated blocks into the final result
    return _build_final_result(state)


def _process_event(event, state):
    """Dispatches an individual event to its appropriate handler based on type."""
    etype = event.get("type")
    
    if etype == "message_start":
        message = event.get("message", {})
        usage = message.get("usage", {})
        state["input_tokens"] = usage.get("input_tokens", state["input_tokens"])
        
    elif etype == "content_block_start":
        _handle_content_block_start(event, state["blocks"])
        
    elif etype == "content_block_delta":
        _handle_content_block_delta(event, state["blocks"])
        
    elif etype == "message_delta":
        delta = event.get("delta", {})
        if "stop_reason" in delta:
            state["stop_reason"] = delta["stop_reason"]
        usage = event.get("usage", {})
        if "output_tokens" in usage:
            state["output_tokens"] = usage["output_tokens"]
            
    elif etype == "message_stop":
        state["complete"] = True
        
    elif etype == "error":
        _handle_error_event(event)


def _handle_content_block_start(event, blocks):
    """Initializes a new content block (text or tool_use) at the specified index."""
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


def _handle_content_block_delta(event, blocks):
    """Appends delta fragments (text pieces or partial JSON) to the correct block buffer."""
    index = event.get("index")
    delta = event.get("delta", {})
    
    if index in blocks:
        dtype = delta.get("type")
        if dtype == "text_delta":
            blocks[index]["pieces"].append(delta.get("text", ""))
        elif dtype == "input_json_delta":
            blocks[index]["pieces"].append(delta.get("partial_json", ""))


def _handle_error_event(event):
    """Extracts error details and raises a StreamError."""
    err = event.get("error", "Stream error")
    msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
    raise StreamError(msg)


def _build_final_result(state):
    """Assembles text blocks and safely parses tool arguments in block order."""
    text_pieces = []
    tool_calls = []
    
    # Process blocks sequentially by their index
    for index in sorted(state["blocks"].keys()):
        block = state["blocks"][index]
        
        if block["type"] == "text":
            text_pieces.append("".join(block["pieces"]))
            
        elif block["type"] == "tool_use":
            tool_call = _parse_tool_call(block)
            if tool_call is not None:
                tool_calls.append(tool_call)
                
    return {
        "text": "".join(text_pieces),
        "tool_calls": tool_calls,
        "stop_reason": state["stop_reason"],
        "input_tokens": state["input_tokens"],
        "output_tokens": state["output_tokens"],
        "complete": state["complete"]
    }


def _parse_tool_call(block):
    """Safely parses tool JSON arguments. Returns None if truncated or malformed."""
    pieces = block["pieces"]
    
    if not pieces:
        input_obj = {}
    else:
        json_str = "".join(pieces)
        try:
            # Attempt parsing; if the stream died mid-argument, JSONDecodeError is raised
            input_obj = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            # Drop malformed/truncated tool calls as required
            return None
            
    return {
        "id": block["id"],
        "name": block["name"],
        "input": input_obj
    }
