def cost_micros(input_tokens, output_tokens, price_in, price_out):
    """Return the total cost in micro-dollars given token counts and prices per million tokens."""
    total = (input_tokens * price_in) + (output_tokens * price_out)
    return int(round(total))
