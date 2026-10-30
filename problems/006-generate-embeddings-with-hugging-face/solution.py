import numpy as np
import torch
import torch.nn.functional as F

def custom_l2_normalize(tensor, dim=1, eps=1e-12):
    """Custom L2 normalization method:

    1. Computes the Euclidean norm: sqrt(sum(x^2))
    2. Safely divides the tensor by its norm using broadcasting.
    """
    # Step A: Square every element, then sum along the feature dimension (dim=1).
    # keepdim=True preserves the dimension as (n, 1) instead of collapsing it to (n,).
    squared_sum = torch.sum(tensor**2, dim=dim, keepdim=True)

    # Step B: Take the square root to get the final L2 norm magnitude for each row.
    norm = torch.sqrt(squared_sum)

    # Step C: Clamp the norm to a tiny epsilon value to prevent division by zero
    # if a sentence embedding vector happens to be all zeros.
    norm = torch.clamp(norm, min=eps)

    # Step D: Divide the tensor by the norm.
    # BROADCASTING: tensor has shape (n, d) and norm has shape (n, 1).
    # PyTorch automatically stretches the (n, 1) norm horizontally across all d columns.
    return tensor / norm

def embed(sentences, tokenizer, model):
    """Return normalized sentence embeddings, shape (n, d), as a NumPy array."""

    # STEP 1: TOKENIZATION (Under the Hood)
    # Under the hood, the tokenizer:
    # 1. Looks up words/subwords in its vocabulary table to convert text into integer IDs ('input_ids').
    # 2. Automatically injects special model tokens (e.g., [CLS] at the start, [SEP] at the end).
    # 3. Pads shorter sentences with special token IDs so every row matches the longest sentence ('seq_len').
    # 4. Generates an 'attention_mask' (1 for real tokens, 0 for padding tokens).
    # return_tensors="pt" packages these structures into PyTorch tensors.
    batch = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")


    # STEP 2: MODEL FORWARD PASS (Under the Hood)
    # torch.no_grad() disables PyTorch's autograd engine (gradient tracking).
    # Under the hood, this stops PyTorch from building a massive dynamic computation graph
    # in memory. Since we are only doing inference (not training), this drastically reduces
    # RAM consumption and speeds up computation.
    with torch.no_grad():
        # **batch unpacks the dictionary keys ('input_ids', 'attention_mask')
        # and passes them as individual keyword arguments into the model.
        outputs = model(**batch)

    # outputs.last_hidden_state contains the transformer's final layer output.
    # Under the hood, tokens pass through multi-head self-attention layers where they
    # dynamically "look at" surrounding words to capture rich, context-aware meanings.
    # Shape: (batch_size [n], sequence_length [seq_len], hidden_dimension [384])
    token_embeddings = outputs.last_hidden_state

    
    # STEP 3: MASKED MEAN POOLING (Under the Hood)
    # Why do we need this? Transformers output a vector for EVERY token, including padding.
    # If we blindly average all tokens, meaningless padding tokens (value 0) pull sentence embeddings
    # toward a distorted average point, ruining similarity metrics for short sentences.

    # Extract attention mask. Shape: (n, seq_len) -> e.g., [[1, 1, 0], [1, 0, 0]]
    attention_mask = batch["attention_mask"]

    # BROADCASTING PREPARATION:
    # token_embeddings has shape (n, seq_len, 384).
    # attention_mask has shape (n, seq_len).
    # To multiply them element-wise, we use .unsqueeze(-1) to add a singleton dimension at the end.
    # New mask shape: (n, seq_len, 1).
    # Under the hood, PyTorch automatically stretches (broadcasts) this (n, seq_len, 1)
    # across all 384 columns of the hidden features.
    input_mask_expanded = attention_mask.unsqueeze(-1).float()

    # Element-wise multiplication zeroes out all padding token vectors,
    # then torch.sum collapses the sequence length dimension (dim=1).
    # Shape changes from (n, seq_len, 384) -> (n, 384) [sum of real token vectors]
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)

    # Count how many *real* tokens exist per sentence by summing the mask along dim=1.
    # torch.clamp ensures that if a sentence somehow has 0 real tokens, we don't divide by zero.
    sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)

    # Compute the true mean by dividing the sum of embeddings by the count of real tokens.
    # Shape remains: (n, 384)
    sentence_embeddings = sum_embeddings / sum_mask

   
    # STEP 4: L2 NORMALIZATION (Under the Hood)
    # F.normalize scales each sentence vector so its Euclidean length (norm) equals 1.
    # Under the hood, it computes the magnitude of each vector: sqrt(sum(x_i^2))
    # and divides every element by that magnitude.
    # This projects all embeddings onto a unit hypersphere, making cosine similarity
    # mathematically equivalent to a simple vector dot product (u . v).
    # We will be using our custom normalisation util.
    # normalized_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
    normalized_embeddings = custom_l2_normalize(sentence_embeddings, dim=1)  # Shape: (n, 384)
    
    # STEP 5: CONVERSION TO NUMPY (Under the Hood)
    # .cpu() ensures the tensor is moved from GPU memory to CPU RAM (if a GPU was used),
    # and .numpy() converts the PyTorch Tensor into a standard NumPy ndarray of shape (n, d).
    return normalized_embeddings.cpu().numpy()
