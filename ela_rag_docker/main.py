from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import numpy as np
from vector_db import VectorDatabase
from hf_embeddings import get_embedding
from gemini_client import query_gemini  # Keep Gemini for LLM responses
import os

app = FastAPI()
vector_db = VectorDatabase(embedding_dim=384)  # Adjusted for Hugging Face embeddings

# API Key for authentication
API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class QueryRequest(BaseModel):
    query_text: str

@app.post("/query", dependencies=[Depends(verify_api_key)])
def search_vector_db(request: QueryRequest):
    query_embedding = np.array(get_embedding(request.query_text)).astype('float32')
    results = vector_db.search(query_embedding, top_k=3)

    # Construct a prompt for Google Gemini
    context = "\n".join([f"{res[0]} (score: {res[1]})" for res in results])
    prompt = f"Based on this context:\n{context}\nAnswer the query: {request.query_text}"
    
    gemini_response = query_gemini(prompt)
    
    return {"retrieved_context": results, "llm_response": gemini_response}
