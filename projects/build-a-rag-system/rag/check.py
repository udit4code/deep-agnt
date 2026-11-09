import re

def sentences(text):
    """Splits text into sentences after a ., !, or ? followed by whitespace, stripping and dropping empty ones."""
    if not text:
        return []
    
    # Split after a ., !, or ? that is followed by one or more whitespace characters
    parts = re.split(r'(?<=[.!?])\s+', text)
    
    # Strip each piece and filter out any empty strings
    return [p.strip() for p in parts if p.strip()]


def is_supported(model, sentence, sources):
    """Determines whether a sentence follows from the provided sources using the model."""
    system = "Determine whether the sentence follows from the provided numbered sources. Reply with only YES or NO."
    
    # Lay out the sources using the provided numbered() function
    user_content = f"{numbered(sources)}\n\nSentence: {sentence}"
    messages = [{"role": "user", "content": user_content}]
    
    # Ask the model via ask_model
    reply = ask_model(model, system, messages, max_tokens=10)
    
    # Treat a reply starting with 'yes' (any case) as True, anything else as False
    return reply.strip().lower().startswith("yes")


def unsupported(model, answer, sources):
    """Returns the sentences of answer that are not supported by the sources, in order."""
    if not answer or abstained(answer):
        return []
    
    # Split the answer into individual sentences
    answer_sentences = sentences(answer)
    
    unsupported_list = []
    for sentence in answer_sentences:
        # Check if the sentence is supported by the sources
        if not is_supported(model, sentence, sources):
            unsupported_list.append(sentence)
            
    return unsupported_list
