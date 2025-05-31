import os
import faiss
import numpy as np
import pickle

DB_PATH = "vector_store/index.faiss"
META_PATH = "vector_store/metadata.pkl"

class VectorDatabase:
    """
    A simple wrapper for a FAISS vector database with metadata storage.

    Handles adding, searching, saving, and loading document embeddings and their metadata.
    """
    def __init__(self, embedding_dim=384):
        """
        Initialize the FAISS index and metadata store.

        Args:
            embedding_dim (int): Dimension of the embedding vectors.
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)  # FAISS index for L2 similarity
        self.metadata = {}  # Dictionary to store document metadata

        # Ensure the vector_store directory exists
        if not os.path.exists("vector_store"):
            os.makedirs("vector_store")

        # Load existing index and metadata if available
        if os.path.exists(DB_PATH):
            self.load()

    def add_document(self, embedding: np.ndarray, doc_id: str, metadata: str):
        """
        Add an embedding and its metadata to the FAISS index.

        Args:
            embedding (np.ndarray): The embedding vector.
            doc_id (str): The document identifier (not used for lookup, but can be included in metadata).
            metadata (str): Metadata or preview text for the document.
        """
        index_position = self.index.ntotal  # Track current index position
        self.index.add(np.array([embedding]).astype('float32'))
        self.metadata[str(index_position)] = metadata  # Ensure FAISS index matches metadata
        self.save()

    def search(self, query_embedding: np.ndarray, top_k=3):
        """
        Search the FAISS index for the top_k most similar embeddings.

        Args:
            query_embedding (np.ndarray): The query embedding vector.
            top_k (int): Number of top results to return.

        Returns:
            list: List of tuples (index, metadata, distance) for the top_k results.
        """
        if self.index.ntotal == 0:
            print("⚠️ No vectors in FAISS index.")
            return [("No data available", 0.0)]  # Handle empty database

        print(f"🔍 Querying FAISS with {query_embedding.shape} embedding")
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            doc_metadata = self.metadata.get(str(idx), "Unknown")
            results.append((idx, doc_metadata, float(distances[0][i])))

        return results

    def save(self):
        """
        Save the FAISS index and metadata to disk.
        """
        faiss.write_index(self.index, DB_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        """
        Load the FAISS index and metadata from disk.
        """
        if os.path.exists(DB_PATH):
            self.index = faiss.read_index(DB_PATH)
            print(f"✅ Loaded index with {self.index.ntotal} vectors")

        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.metadata = {}  # Ensure metadata exists if missing
            print("⚠️ No metadata file found, creating empty metadata.")

    def list_stored_documents(self):
        """
        List all stored documents' metadata in the FAISS index.

        Returns:
            dict: Mapping of FAISS index positions to metadata.
        """
        return self.metadata