import os
import faiss
import numpy as np
import pickle

DB_PATH = "vector_store/index.faiss"
META_PATH = "vector_store/metadata.pkl"

class VectorDatabase:
    def __init__(self, embedding_dim=384):  # Adjust for Hugging Face embeddings
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(self.embedding_dim)  # FAISS index
        self.metadata = {}  # Store document metadata

        # Ensure directory exists
        if not os.path.exists("vector_store"):
            os.makedirs("vector_store")

        if os.path.exists(DB_PATH):
            self.load()

    def add_document(self, embedding: np.ndarray, doc_id: str, metadata: str):
        """Adds an embedding + metadata to FAISS"""
        index_position = self.index.ntotal  # ✅ Correct way to track FAISS index
        self.index.add(np.array([embedding]).astype('float32'))
        
        self.metadata[str(index_position)] = metadata  # ✅ Ensure FAISS index matches metadata
        self.save()

    def search(self, query_embedding: np.ndarray, top_k=3):
        """Search FAISS for similar embeddings"""
        if self.index.ntotal == 0:
            print("⚠️ No vectors in FAISS index.")
            return [("No data available", 0.0)]  # Handle empty database

        print(f"🔍 Querying FAISS with {query_embedding.shape} embedding")
        
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), top_k)

        # print(f"🔍 FAISS Search Results: indices={indices[0]}, distances={distances[0]}")       # debug

        results = []
        for i, idx in enumerate(indices[0]):
            doc_metadata = self.metadata.get(str(idx), "Unknown")
            results.append((idx, doc_metadata, float(distances[0][i])))

        # print(f"📖 Retrieved Metadata: {results}")

        return results


    def save(self):
        """Save FAISS index and metadata"""
        faiss.write_index(self.index, DB_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        """Load FAISS index and metadata"""
        if os.path.exists(DB_PATH):
            self.index = faiss.read_index(DB_PATH)
            print(f"✅ Loaded index with {self.index.ntotal} vectors")

        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            # print("📂 Loaded metadata:", self.metadata)
        else:
            self.metadata = {}  # Ensure metadata exists if missing
            print("⚠️ No metadata file found, creating empty metadata.")

    def list_stored_documents(self):
        """Lists all stored documents in FAISS"""
        return self.metadata
