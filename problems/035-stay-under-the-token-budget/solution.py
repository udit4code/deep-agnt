def answer_with_context(llm, question, docs):
    """Answer the question using only the relevant document to stay under budget."""
    # Extract unique lowercase words from the question to use as search keywords
    question_words = set(question.lower().split())
    
    # Initialize variables to track the best-matching document and its overlap score
    best_doc = docs[0]
    max_overlap = -1
    
    # Iterate through the documents to find the one with the highest keyword overlap
    for doc in docs:
        doc_words = set(doc.lower().split())
        overlap = len(question_words.intersection(doc_words))
        
        # Update the best document if the current overlap exceeds the previous maximum
        if overlap > max_overlap:
            max_overlap = overlap
            best_doc = doc
            
    # Use only the single most relevant document as context to minimize token usage
    context = best_doc
    prompt = "Context:\n" + context + "\n\nQuestion: " + question
    
    # Send the optimized, budget-friendly prompt to the LLM
    return llm.ask(prompt)
