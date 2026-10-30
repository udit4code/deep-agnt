"""
When dealing with chat models, formatting messages correctly is critical because large language models don't understand 
raw Python lists of dictionaries—they only understand a continuous string of text containing special markup 
tags that tell them who is speaking.

Under the hood, Hugging Face tokenizers use a templating engine called Jinja2 (the same engine used in web development).

Step 1 : The Template String (tokenizer.chat_template) ->
We have defined a blueprint (template) that looks like this : 

{% for m in messages %}
<|{{ m['role'] }}|>
{{ m['content'] }}<|end|>
{% endfor %}
{% if add_generation_prompt %}<|assistant|>{% endif %}

Step 2 : How apply_chat_template executes it ->

2.1 The Loop (for m in messages): It loops through each message in our Python list.
2.2 Variable Substitution: It extracts the dictionary values (m['role'] and m['content']) and injects them into the template brackets {{ ... }}.
2.3 Conditional Logic (if add_generation_prompt):
If True (used for inference/chatting), it appends <|assistant|>\n at the very end. 
This acts as a cue card telling the model: "It's your turn to talk now!"

If False (used for training), it leaves the prompt suffix off because the assistant's response is already provided in the conversation history.


"""

def format_chat(messages):
    """Formats a conversation history into a prompt string ready for inference.

    Under the Hood:
      - Uses Jinja2 chat template rendering via tokenizer.apply_chat_template.
      - Iterates through the list of message dictionaries.
      - set add_generation_prompt=True to append '<|assistant|>\n' at the end,
        signaling the model that it is expected to generate a response.
    """
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,  # Return raw text string instead of token ID integers
        add_generation_prompt=True,  # Prime the model to start generating
    )


def format_for_training(messages):
    """Formats a complete conversation (including the assistant reply) for training.

    Under the Hood:
      - Renders all messages including the final assistant response.
      - set add_generation_prompt=False because the conversation is already complete;
        no trailing generation prompt cue is needed.
    """
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,  # Return raw text string
        add_generation_prompt=False,  # Do not append generation prompt
    )
