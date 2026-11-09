from agentkit import ToolError

def dispatch(response, registry):
    """Run every tool call in a response and return one result per call."""
    results = []
    
    for call in response.tool_calls:
        try:
            # Execute the tool using registry.call with name and input arguments
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
