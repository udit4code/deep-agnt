def cost_micros(input_tokens, output_tokens, price_in, price_out):
    """Return the total cost in micro-dollars given token counts and prices per million tokens."""
    total = (input_tokens * price_in) + (output_tokens * price_out)
    return int(round(total))


class Budget:
    def __init__(self):
        self.calls = 0
        self.tokens = 0

    def record(self, input_tokens, output_tokens):
        """Record a model call, incrementing the call count and total token usage."""
        self.calls += 1
        self.tokens += input_tokens + output_tokens


def exceeded(budget, max_calls=None, max_tokens=None):
    """Check if the budget has exceeded the max_calls or max_tokens limits, checking calls first."""
    if max_calls is not None and budget.calls > max_calls:
        return f"calls: {budget.calls} of {max_calls}"
    if max_tokens is not None and budget.tokens > max_tokens:
        return f"tokens: {budget.tokens} of {max_tokens}"
    return None
