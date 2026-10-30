def count_tokens(text):
    """Number of tokens, excluding any special tokens.

    Time Complexity: O(N)
      - N: length of the text string.
    """
    if not isinstance(text, str) or not text:
        return 0

    # Encode text into IDs while omitting any model-specific special tokens
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    return len(token_ids)


def roundtrip(text):
    """Encode then decode, returning the original text.

    Time Complexity: O(N)
      - Linear encoding pass followed by a linear decoding pass.
    """
    if not isinstance(text, str) or not text:
        return ""

    # Step 1: Convert text to token IDs without special tokens
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    # Step 2: Decode token IDs back to text, skipping any stray special markers
    return tokenizer.decode(token_ids, skip_special_tokens=True)


def token_strings(text):
    """The individual tokens, in order, as strings.

    Time Complexity: O(N)
      - N: number of tokens produced.
    """
    if not isinstance(text, str) or not text:
        return []

    # Directly extract and return subword token strings using the tokenizer
    return tokenizer.tokenize(text)
