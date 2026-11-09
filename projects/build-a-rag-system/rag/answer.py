def ask_model(model, system, messages, max_tokens=300):
    """Makes one call to model.chat and returns the joined and stripped text from text blocks."""
    reply = model.chat(messages, system=system, max_tokens=max_tokens)
    
    # Extract the "text" of every block whose "type" is "text"
    text_parts = [
        block.get("text", "") 
        for block in reply.get("content", []) 
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    
    # Join and strip the resulting string
    return "".join(text_parts).strip()


import re

def citations(answer):
    """Returns the source numbers an answer cites, as a sorted list of distinct ints."""
    if not answer:
        return []
    
    # Find all occurrences of one or more digits inside brackets (e.g., [1], [2])
    matches = re.findall(r'\[(\d+)\]', answer)
    
    # Convert to integers, remove duplicates using a set, and sort
    distinct_citations = sorted({int(m) for m in matches})
    
    return distinct_citations


def cited_chunks(chunks, answer):
    """Returns the chunks the answer cites, in citation order, skipping invalid indices."""
    if not chunks or not answer:
        return []
    
    # Get the sorted list of distinct citation numbers from citations()
    cited_nums = citations(answer)
    
    result = []
    for num in cited_nums:
        # Convert 1-based citation number to 0-based index
        idx = num - 1
        # Check if the index exists within the chunks list bounds
        if 0 <= idx < len(chunks):
            result.append(chunks[idx])
            
    return result


def answer_question(model, embedder, index, question, k=3):
    """Answers a question by performing hybrid search, fitting context, querying the model, and extracting cited sources."""
    # Step 1 : Retrieve relevant chunks using hybrid_search
    retrieved_chunks = hybrid_search(embedder, index, question, k=k)
    
    # Step 2 : Keep chunks that fit within the CONTEXT_WORDS budget using fit
    kept = fit(retrieved_chunks, CONTEXT_WORDS)
    
    # Step 3 : Build the RAG system prompt and messages
    rag_data = rag_messages(question, kept)
    system_prompt = rag_data["system"]
    messages = rag_data["messages"]
    
    # 4. Ask the model using ask_model
    answer = ask_model(model, system_prompt, messages)
    
    # 5. Extract cited sources from the answer text relative to the kept chunks
    sources = cited_chunks(kept, answer)
    
    return {
        "answer": answer,
        "sources": sources
    }
