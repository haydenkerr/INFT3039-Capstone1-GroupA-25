import os
import numpy as np
import pandas as pd
import hashlib
from sentence_transformers import SentenceTransformer
from vector_db import VectorDatabase

# Initialize the sentence transformer embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize the FAISS vector database with the correct embedding dimension
vector_db = VectorDatabase(embedding_dim=384)

# Default GitHub CSV URL for data ingestion
CSV_URL = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_train_data.csv"

def compute_content_hash(content):
    """
    Generate a hash for document content to check for duplicates.

    Args:
        content (str): The document content.

    Returns:
        str: MD5 hash of the content.
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def load_document_hashes():
    """
    Load existing document hashes from the vector database metadata.

    Returns:
        dict: Mapping of content hash to document index.
    """
    hashes = {}
    for idx, metadata in vector_db.metadata.items():
        if isinstance(metadata, str) and "hash:" in metadata:
            hash_start = metadata.find("hash:") + 5
            hash_end = metadata.find(" ", hash_start) if " " in metadata[hash_start:] else len(metadata)
            doc_hash = metadata[hash_start:hash_end].strip()
            hashes[doc_hash] = idx
    return hashes

def ingest_csv_documents(max_rows=10000, csv_url=None):
    """
    Batch processes and stores CSV data into the FAISS vector database with duplicate checking.

    Args:
        max_rows (int): Maximum number of rows to process from the CSV.
        csv_url (str, optional): URL to the CSV file. If None, uses the default CSV_URL.
    """
    if csv_url is None:
        csv_url = CSV_URL
        
    print(f"📊 Loading CSV data from {csv_url}...")
    
    try:
        # Load existing document hashes for duplicate detection
        existing_hashes = load_document_hashes()
        print(f"🔍 Found {len(existing_hashes)} existing documents")
        
        # Load the CSV data into a DataFrame
        df = pd.read_csv(csv_url)
        
        # Select and rename relevant columns
        df = df[['prompt', 'essay', 'band', 'cleaned_evaluation', 
                'Task Achievement', 'Coherence', 'Lexical Resource', 
                'Grammar', 'Overall Band Score']]
        df.rename(columns={'prompt': 'question'}, inplace=True)
        
        print(f"✅ Loaded CSV with {len(df)} rows")
        
        # Initialize counters
        processed_rows = 0
        new_docs = 0
        skipped_docs = 0
        
        # Iterate through DataFrame rows
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
            
            # Check for duplicates using content hash
            content_hash = compute_content_hash(content)
            if content_hash in existing_hashes:
                skipped_docs += 1
                processed_rows += 1
                continue
                
            # Generate embedding for the document
            embedding = embedding_model.encode(content, normalize_embeddings=True)
            
            # Use row index as document ID
            doc_id = f"row_{idx}"
            
            # Include hash in metadata for future duplicate checks
            metadata_preview = f"{content[:150].replace('\n', ' ')} hash:{content_hash}"
            
            # Add document to vector database
            vector_db.add_document(np.array(embedding), doc_id, metadata_preview)
            existing_hashes[content_hash] = str(vector_db.index.ntotal - 1)
            
            new_docs += 1
            processed_rows += 1
            
            if processed_rows % 100 == 0:
                print(f"📊 Processed {processed_rows} rows, added {new_docs}, skipped {skipped_docs}")
        
        print(f"✅ Processing complete: added {new_docs} new documents, skipped {skipped_docs} duplicates")
        print(f"📊 Vector DB now contains {vector_db.index.ntotal} total documents")
        
    except Exception as e:
        print(f"❌ Error ingesting CSV data: {str(e)}")

if __name__ == "__main__":
    ingest_csv_documents()