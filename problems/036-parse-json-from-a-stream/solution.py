import json


def parse_stream(chunks):
    """Return (parsed_json, chunks_consumed), or (None, len(chunks)) if incomplete."""
    accumulated = ""
    decoder = json.JSONDecoder()
    
    for chunk_id, chunk in enumerate(chunks, 1):
        accumulated += chunk
        
        try:
            text = accumulated.lstrip()
            # Handle markdown code block fences if present
            if text.startswith("```"):
                newline_idx = text.find("\n")
                if newline_idx == -1:
                    continue  # Incomplete fence header, wait for more chunks
                content = text[newline_idx + 1:]
            else:
                content = text
                
            # raw_decode parses the JSON object from the start and ignores trailing text
            obj, _ = decoder.raw_decode(content)
            return (obj, chunk_id)
        except (json.JSONDecodeError, ValueError):
            # Incomplete or invalid JSON so far; continue accumulating chunks
            continue
            
    return (None, len(chunks))
