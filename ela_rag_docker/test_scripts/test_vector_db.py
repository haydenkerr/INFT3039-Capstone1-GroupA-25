import unittest
import numpy as np
from vector_db import VectorDatabase

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        self.db = VectorDatabase(embedding_dim=3)
    
    def test_add_and_search_document(self):
        embedding = np.array([0.1, 0.2, 0.3])
        self.db.add_document(embedding, 'doc1', 'metadata')
        results = self.db.search(embedding, top_k=1)
        self.assertTrue(len(results) > 0)
