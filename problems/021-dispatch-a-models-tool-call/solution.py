from agentkit import ToolError

def dispatch(response, registry):
    """Run every tool call in a response and return one result per call."""
    results = []
    
    # Iterate through each tool_call of a response
    for call in response.tool_calls:
        try:
            # For each tool_call, execute the tool using registry.call with name and input arguments
            output = registry.call(call.name, call.input)
            results.append({
                'tool_use_id': call.id,
                'content': output,
                'is_error': False
            })
        except ToolError as e:
            # Catch ToolError as model information instead of aborting
            results.append({
                'tool_use_id': call.id,
                'content': str(e),
                'is_error': True
            })
            
    return results
