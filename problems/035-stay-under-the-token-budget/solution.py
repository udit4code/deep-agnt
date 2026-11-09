def answer_with_context(llm, question, docs):
    """Answer the question using only the relevant document to stay under budget."""
    question_words = set(question.lower().split())
    
    best_doc = docs[0]
    max_overlap = -1
    
    for doc in docs:
        doc_words = set(doc.lower().split())
        overlap = len(question_words.intersection(doc_words))
        if overlap > max_overlap:
            max_overlap = overlap
            best_doc = doc
            
    context = best_doc
    prompt = "Context:\n" + context + "\n\nQuestion: " + question
    return llm.ask(prompt)
