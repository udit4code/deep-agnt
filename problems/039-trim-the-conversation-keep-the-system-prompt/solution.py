from agentkit.tokenizer import count_tokens


def trim_history(messages, max_tokens):
    """Drop old turns until the conversation fits. Never the system prompt."""
    if not messages:
        return messages
        
    # Return unchanged if it already fits within the token budget
    if count_tokens(messages) <= max_tokens:
        return messages
        
    # 1. Identify and separate the system prompt if present
    has_system = messages[0].get("role") == "system"
    system_msgs = [messages[0]] if has_system else []
    rest = messages[1:] if has_system else messages
    
    if not rest:
        return messages
        
    # 2. The most recent user message is never dropped
    last_msg = rest[-1]
    pairs_flat = rest[:-1]
    
    # Group the intermediate history into (user, assistant) pairs
    pairs = []
    i = 0
    while i < len(pairs_flat) - 1:
        pairs.append([pairs_flat[i], pairs_flat[i+1]])
        i += 2
        
    # 3. Drop pairs from the oldest end one by one until it fits
    for i in range(len(pairs) + 1):
        current_pairs = []
        for p in pairs[i:]:
            current_pairs.extend(p)
            
        candidate = system_msgs + current_pairs + [last_msg]
        if count_tokens(candidate) <= max_tokens:
            return candidate
            
    # 4. If system prompt + last user message alone still exceed the budget,
    # truncate the last user message from the front, keeping its tail.
    content = last_msg.get("content", "")
    role = last_msg.get("role", "user")
    
    while len(content) > 0:
        candidate = system_msgs + [{"role": role, "content": content}]
        if count_tokens(candidate) <= max_tokens:
            return candidate
        content = content[1:]
        
    return system_msgs + [{"role": role, "content": ""}]
