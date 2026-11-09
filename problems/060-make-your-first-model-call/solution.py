def first_call(llm, question, system, max_tokens=100):
    """Ask one question. Return the text, the stop reason and the token counts."""
    response = llm.messages.create(
        system=system,
        messages=[
            {
                "role": "user", 
                "content": question
            }
        ],
        max_tokens=max_tokens
    )
    
    return {
        "text": response.text.strip(),
        "stop_reason": response.stop_reason,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
