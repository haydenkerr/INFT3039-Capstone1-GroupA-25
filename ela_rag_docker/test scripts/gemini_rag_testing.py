import pandas as pd
import json
import re
from sentence_transformers import SentenceTransformer, util
import requests

# Load the test dataset
csv_url_test = "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/main/datasets/processed_dataset2_test_data.csv"
df_test = pd.read_csv(csv_url_test)

# Select relevant columns
df_test = df_test[['prompt', 'essay', 'band', 'cleaned_evaluation', 'Task Achievement', 'Coherence', 'Lexical Resource', 'Grammar', 'Overall Band Score']]
df_test.rename(columns={'prompt': 'question'}, inplace=True)

# Load embedding model for similarity calculations
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(reference, candidate):
    """Compute cosine similarity between reference and candidate feedback."""
    ref_embedding = embedding_model.encode(reference, convert_to_tensor=True)
    cand_embedding = embedding_model.encode(candidate, convert_to_tensor=True)
    return util.cos_sim(ref_embedding, cand_embedding).item()

def query_rag_model(question, essay):
    """Send a request to the RAG model API and return the graded response."""
    API_KEY = "1234abcd"  # Adjust to match FastAPI API key
    url = "http://192.168.1.15:8001/grade"  # Adjust to match FastAPI endpoint
    payload = {"question": question, "essay": essay}
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get response", "status_code": response.status_code}

# Store test results
rag_results = []
processed_rows = 0

for _, row in df_test.iterrows():
    if processed_rows >= 10:
        break
    
    result = query_rag_model(row['question'], row['essay'])
    
    if 'error' in result:
        continue  # Skip failed API responses
    
    # Compute feedback similarity
    overall_feedback_similarity = compute_similarity(row['cleaned_evaluation'], result['feedback']['task_response'])
    
    # Store test results
    new_row = (
        row['question'], row['essay'], row['cleaned_evaluation'],
        row['Overall Band Score'], result['bands']['overall'], overall_feedback_similarity,
        row['Task Achievement'], result['bands']['task_response'],
        row['Coherence'], result['bands']['coherence_cohesion'],
        row['Grammar'], result['bands']['grammatical_range'],
        row['Lexical Resource'], result['bands']['lexical_resource']
    )
    rag_results.append(new_row)
    processed_rows += 1

# Convert results to DataFrame
columns = ['question', 'essay', 'original_feedback', 'original_score', 'predicted_score', 'feedback_similarity',
           'original_task_achievement', 'predicted_task_achievement',
           'original_coherence', 'predicted_coherence',
           'original_grammar', 'predicted_grammar',
           'original_lexical', 'predicted_lexical']
rag_results_df = pd.DataFrame(rag_results, columns=columns)

# Save results to Excel
output_file = "./ela_rag_docker/Scripts/gemini_rag_test_results.xlsx"
rag_results_df.to_excel(output_file, index=False)
print(f"✅ Test results saved to {output_file}")
