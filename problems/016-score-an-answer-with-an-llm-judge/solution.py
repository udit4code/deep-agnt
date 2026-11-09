import re


def judge(llm, question, answer):
    """Score `answer` against `question` from 1 (useless) to 5 (excellent)."""
    prompt = (
        "Score the answer to the question on a scale of 1 to 5.\n"
        "1 = wrong or irrelevant. 3 = partially correct. 5 = correct and complete.\n"
        "Reply with only the digit.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        "Score:"
    )
    reply = llm.ask(prompt, max_tokens=10)
    match = re.search(r"[1-5]", reply)
    if not match:
        return 1
    return max(1, min(5, int(match.group())))
