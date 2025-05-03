import unittest
from unittest.mock import patch, MagicMock
import csv_batch_ingestion

class TestCsvBatchIngestion(unittest.TestCase):
    @patch('csv_batch_ingestion.pd.read_csv')
    @patch('csv_batch_ingestion.vector_db.add_document')
    @patch('csv_batch_ingestion.load_document_hashes', return_value={})
    def test_ingest_csv_documents(self, mock_load_hashes, mock_add_doc, mock_read_csv):
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [(0, {
            'prompt': 'Q', 'essay': 'E', 'band': '7', 'cleaned_evaluation': 'clean',
            'Task Achievement': 'good', 'Coherence': 'ok', 'Lexical Resource': 'ok',
            'Grammar': 'ok', 'Overall Band Score': '7'
        })]
        mock_df.__len__.return_value = 1
        mock_read_csv.return_value = mock_df
        csv_batch_ingestion.ingest_csv_documents(max_rows=1)
        mock_add_doc.assert_called()
