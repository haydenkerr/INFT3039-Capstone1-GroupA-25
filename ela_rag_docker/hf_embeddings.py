from sentence_transformers import SentenceTransformer

# Ensure both ingestion and querying use the same model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    """Generates embeddings from the given text using Hugging Face transformers."""
    return model.encode(text, normalize_embeddings=True).tolist()