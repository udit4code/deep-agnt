def chunk_document(text, chunk_size, overlap):
    """Split text into overlapping word chunks.

    Parameters:
      - text (str): The input text to be chunked.
      - chunk_size (int): Maximum number of words per chunk.
      - overlap (int): Number of overlapping words between consecutive chunks.

    Returns:
      - list of str: A list where each element is a chunk of text.

    Time Complexity: O(N)
      - N: total number of words in the text.
      - Splitting the text and sliding through the word list takes linear time.
    """
    if not text or chunk_size <= 0:
        return []

    # Step 1: Split the text into individual words by whitespace
    words = text.split()
    if not words:
        return []

    # Step 2: Determine the step size, ensuring it's at least 1 to avoid infinite loops
    step = chunk_size - overlap
    if step <= 0:
        step = 1

    chunks = []
    i = 0
    n = len(words)

    # Step 3: Slide a window across the words list with the calculated step size
    while i < n:
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))

        # Break out of the loop if we've processed the final words
        if i + chunk_size >= n:
            break
        i += step

    return chunks
