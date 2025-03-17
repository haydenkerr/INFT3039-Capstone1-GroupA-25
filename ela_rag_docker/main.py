from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import numpy as np
import json
from vector_db import VectorDatabase
from hf_embeddings import get_embedding
from gemini_client import query_gemini
import os

app = FastAPI()
vector_db = VectorDatabase(embedding_dim=384)

# API Key for authentication
API_KEY = "1234abcd"

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


class QueryRequest(BaseModel):
    query_text: str

class EssayRequest(BaseModel):
    question: str
    essay: str

class Document:
    def __init__(self, page_content):
        self.page_content = page_content

@app.post("/grade", dependencies=[Depends(verify_api_key)])
def grade_essay(request: EssayRequest):
    # Get similar examples using vector search
    query_embedding = np.array(get_embedding(request.question)).astype('float32')
    results = vector_db.search(query_embedding, top_k=5)
    
    # Format examples into context
    examples_context = "\n\n".join([content for content, score in results])
    
    # Pass to updated gemini_client with question and essay
    llm_response = query_gemini(
        user_prompt="",  # No additional prompt needed
        examples_context=examples_context,
        question=request.question,
        essay=request.essay
    )
    
    try:
        # Parse JSON response
        grading_result = json.loads(llm_response)
        return grading_result
    except json.JSONDecodeError:
        # Handle non-JSON response
        cleaned_response = llm_response.strip()
        if cleaned_response.find('{') >= 0 and cleaned_response.rfind('}') > 0:
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            cleaned_json = cleaned_response[json_start:json_end]
            try:
                grading_result = json.loads(cleaned_json)
                return grading_result
            except:
                pass
        
        return {
            "error": "Could not parse LLM response as JSON",
            "raw_response": llm_response
        }

@app.get("/debug/documents")
def list_documents():
    """Debug endpoint to check loaded documents"""
    return {
        "total_documents": vector_db.index.ntotal, 
        "metadata_count": len(vector_db.metadata),
        "metadata_sample": list(vector_db.metadata.items())[:5] if vector_db.metadata else []
    }
@app.post("/query", dependencies=[Depends(verify_api_key)])
def search_vector_db(request: QueryRequest):
    query_embedding = np.array(get_embedding(request.query_text)).astype('float32')
    results = vector_db.search(query_embedding, top_k=3)

    # Ensure conversion of NumPy float32 to Python float
    formatted_results = [
        {"text": res[0], "score": float(res[1])}  # Convert numpy.float32 to float
        for res in results
    ]

    # Construct a prompt for Google Gemini
    context = "\n".join([f"{res['text']} (score: {res['score']})" for res in formatted_results])
    prompt = f"Based on this context:\n{context}\nAnswer the query: {request.query_text}"
    gemini_response = query_gemini(prompt)
    return {"retrieved_context": formatted_results, "llm_response": gemini_response}

@app.get("/debug/test")
def test_response():
    return {"This is a test": "response"}