import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from vector_db import VectorDatabase

# Initialize embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Define FAISS vector store
vector_db = VectorDatabase(embedding_dim=384)

# GitHub CSV URL
CSV_URL = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_train_data.csv"

def ingest_csv_documents(max_rows=5000):
    """Batch processes and stores CSV data into FAISS."""
    print(f"📊 Loading CSV data from {CSV_URL}...")
    
    try:
        # Load the CSV data
        df = pd.read_csv(CSV_URL)
        
        # Select and rename columns
        df = df[['prompt', 'essay', 'band', 'cleaned_evaluation', 
                'Task Achievement', 'Coherence', 'Lexical Resource', 
                'Grammar', 'Overall Band Score']]
        df.rename(columns={'prompt': 'question'}, inplace=True)
        
        print(f"✅ Loaded CSV with {len(df)} rows")
        
        # Process rows up to max_rows limit
        processed_rows = 0
        for idx, row in df.iterrows():
            if processed_rows >= max_rows:
                break
            
            # Create document content from row data
            content = (
                f"question: {row['question']}\n"
                f"essay: {row['essay']}\n"
                f"band: {row['band']}\n"
                f"cleaned_evaluation: {row['cleaned_evaluation']}\n"
                f"Task Achievement: {row['Task Achievement']}\n"
                f"Coherence: {row['Coherence']}\n"
                f"Lexical Resource: {row['Lexical Resource']}\n"
                f"Grammar: {row['Grammar']}\n"
                f"Overall Band Score: {row['Overall Band Score']}"
            )
            
            # Generate embedding
            embedding = embedding_model.encode(content, normalize_embeddings=True)
            
            # Use row index as document ID
            doc_id = f"row_{idx}"
            
            # Store first 200 chars as metadata preview
            metadata_preview = content[:200].replace('\n', ' ')
            
            print(f"📂 Adding document: {doc_id}")
            vector_db.add_document(np.array(embedding), doc_id, metadata_preview)
            
            processed_rows += 1
        
        print(f"✅ Ingested {processed_rows} documents into FAISS.")
        
        # Debug: Verify stored documents
        print(f"📖 Stored documents: {vector_db.list_stored_documents()}")
        
    except Exception as e:
        print(f"❌ Error ingesting CSV data: {str(e)}")

if __name__ == "__main__":
    ingest_csv_documents()