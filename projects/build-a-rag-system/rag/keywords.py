import re

def words(text):
    """Returns the words of text as a list, lowercased: runs of letters and digits, nothing else."""
    return re.findall(r'[a-zA-Z0-9]+', text.lower())
