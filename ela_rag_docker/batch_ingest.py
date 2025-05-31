import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from vector_db import VectorDatabase  # Import the FAISS database class

# Initialize the sentence transformer embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize the FAISS vector database with the correct embedding dimension
vector_db = VectorDatabase(embedding_dim=384)

# Directory containing the text documents to ingest
DOCS_DIR = r"C:\Users\hayde\OneDrive - Logical Aspect\Education\UniSA\INFT3039 - Capstone 1\ela_rag_docker\documents"  # Update this path as needed


def load_documents(directory):
    """
    Loads all text documents from the specified directory.

    Args:
        directory (str): Path to the directory containing text files.

    Returns:
        list of tuple: List of (filename, file_content) tuples.
    """
    documents = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            documents.append((filename, file.read()))
    return documents

def ingest_documents():
    """
    Batch processes and stores documents into the FAISS vector database.

    Loads documents, generates embeddings, and adds them to the vector database.
    """
    documents = load_documents(DOCS_DIR)

    if not documents:
        print("⚠️ No documents found for ingestion!")
        return

    for doc_id, content in documents:
        embedding = embedding_model.encode(content, normalize_embeddings=True)
        print(f"📂 Adding document: {doc_id}")
        # Store the embedding, document ID, and a preview of the content as metadata
        vector_db.add_document(np.array(embedding), doc_id, content[:200])  # Store first 200 chars as metadata

    print(f"✅ Ingested {len(documents)} documents into FAISS.")

    # Debug: List stored documents for verification
    print(f"📖 Stored documents: {vector_db.list_stored_documents()}")


if __name__ == "__main__":
    ingest_documents()