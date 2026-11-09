def ask_model(model, system, messages, max_tokens=300):
    """Makes one call to model.chat and returns the joined and stripped text from text blocks."""
    reply = model.chat(messages, system=system, max_tokens=max_tokens)
    
    # Extract the "text" of every block whose "type" is "text"
    text_parts = [
        block.get("text", "") 
        for block in reply.get("content", []) 
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    
    # Join and strip the resulting string
    return "".join(text_parts).strip()
