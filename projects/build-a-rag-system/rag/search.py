import numpy as np 

def cosine(a, b):
    """Calculate the cosine similarity between two vectors a and b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    
    # Prevent division by zero if either vector is a zero vector
    if a_norm == 0.0 or b_norm == 0.0:
        return 0.0 
        
    dot_product = np.dot(a, b)
    cosine_product = dot_product / (a_norm * b_norm)
    
    # Return as a standard Python float
    return float(cosine_product)
