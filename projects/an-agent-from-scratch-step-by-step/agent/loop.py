def user_message(text):
    """Return a user role message dictionary with the given text content."""
    return {"role": "user", "content": text}


def results_message(results):
    """Return a user message whose content is the list of tool_result blocks."""
    return {"role": "user", "content": results}


def handle_tool_turn(reply, messages, tools):
    """Handle a model reply with tool calls, executing them and updating the conversation history."""
    # Step 1 : Append the assistant's message containing the tool calls to the conversation history
    messages.append(assistant_message(reply))
    
    # Step 2 : Extract all tool use blocks and execute them using the tools registry
    blocks = tool_uses(reply)
    results = [run_tool(block, tools) for block in blocks]
    
    # Step 3 : Append the aggregated tool results as a user message back to the conversation history
    messages.append(results_message(results))
    
    return results
