import json


def parse_stream(chunks):
    """Return (parsed_json, chunks_consumed), or (None, len(chunks)) if incomplete."""
    accumulated = ""
    decoder = json.JSONDecoder()
    
    # Iterate through each chunk in the stream, tracking the count of chunks consumed (1-indexed)
    for i, chunk in enumerate(chunks, 1):
        accumulated += chunk
        
        try:
            # Strip leading whitespace to correctly detect markdown fences or JSON structures
            text = accumulated.lstrip()
            
            # 1. Handle potential markdown code block wrappers (e.g., ```json ... ```)
            if text.startswith("```"):
                newline_idx = text.find("\n")
                if newline_idx == -1:
                    # The fence header is incomplete (e.g., just "```js"), so wait for more chunks
                    continue  
                # Slice past the opening fence line to extract the inner content
                content = text[newline_idx + 1:]
            else:
                content = text
                
            # 2. Parse using raw_decode
            # json.JSONDecoder().raw_decode() parses a valid JSON object starting from 
            # the beginning of the string and returns (parsed_object, end_index).
            # This automatically ignores any trailing prose or closing markdown fences 
            # without requiring manual brace-counting.
            obj, _ = decoder.raw_decode(content)
            
            # 3. Early stopping: As soon as a complete JSON object is parsed, 
            # return it along with the exact number of chunks consumed.
            return (obj, i)
            
        except (json.JSONDecodeError, ValueError):
            # 4. Handle incomplete streams
            # If the JSON is incomplete or invalid so far, raw_decode raises an error.
            # We catch it and continue the loop to accumulate the next chunk.
            continue
            
    # If the loop finishes and a complete JSON object was never formed, return None
    return (None, len(chunks))
