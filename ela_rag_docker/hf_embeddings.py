from sentence_transformers import SentenceTransformer

# Initialize the sentence transformer embedding model.
# Ensure both ingestion and querying use the same model for consistency.
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    """
    Generate an embedding vector from the given text using Hugging Face's SentenceTransformer.

    Args:
        text (str): The input text to encode.

    Returns:
        list: The embedding vector as a list of floats.
    """
    return model.encode(text, normalize_embeddings=True).tolist()