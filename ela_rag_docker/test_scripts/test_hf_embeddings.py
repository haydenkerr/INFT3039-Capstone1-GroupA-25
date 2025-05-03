import unittest
from unittest.mock import patch
import hf_embeddings

class TestHFEmbeddings(unittest.TestCase):
    @patch('hf_embeddings.model.encode', return_value=[0.1, 0.2, 0.3])
    def test_get_embedding(self, mock_encode):
        embedding = hf_embeddings.get_embedding('text')
        self.assertIsInstance(embedding, list)
