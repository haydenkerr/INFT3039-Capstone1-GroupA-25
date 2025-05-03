import unittest
from unittest.mock import patch, mock_open
import batch_ingest

class TestBatchIngest(unittest.TestCase):
    @patch('batch_ingest.os.listdir', return_value=['file1.txt'])
    @patch('builtins.open', new_callable=mock_open, read_data='test content')
    @patch('batch_ingest.vector_db.add_document')
    def test_ingest_documents(self, mock_add_doc, mock_file, mock_listdir):
        batch_ingest.DOCS_DIR = '.'  # mock directory
        batch_ingest.ingest_documents()
        mock_add_doc.assert_called()
