def format_chat(messages):
    """The prompt string, ready for the assistant to continue."""
    # add_generation_prompt=True appends the assistant generation prompt at the end
    # so the model is primed to respond.
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def format_for_training(messages):
    """The full conversation including the assistant's reply."""
    # add_generation_prompt=False renders the complete conversation history
    # (including the final assistant message) for training purposes.
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
