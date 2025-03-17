from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import numpy as np
import json
from vector_db import VectorDatabase
from hf_embeddings import get_embedding
from gemini_client import query_gemini
import os
import regex as re

app = FastAPI(    title="ELA Finetuned RAG API",
    description="This API allows quesiton/essay pairing to query a finetune model with RAG system with Gemini.",
    version="1.0.0",
    # docs_url= "/mydocs",  # Change the Swagger docs URL
    # redoc_url= "/myredoc"  # Change the Redoc docs URL
)
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
    
    # Pass to gemini_client with question and essay
    llm_response = query_gemini(
        user_prompt="",
        examples_context=examples_context,
        question=request.question,
        essay=request.essay
    )
    
    # First try direct JSON parsing
    try:
        grading_result = json.loads(llm_response)
        return grading_result
    except json.JSONDecodeError:
        # Use the parsing function when JSON extraction fails
        import re
        try:
            formatted_json = parse_grading_response(llm_response)
            return formatted_json
        except Exception as e:
            # Return formatted error if parsing fails
            return {
                "error": "Could not parse LLM response",
                "message": str(e),
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

def parse_grading_response(raw_response):
    # Extract band scores from the response
    task_response_score = re.search(r"Task Response\s*\|\s*(\d+)", raw_response)
    coherence_score = re.search(r"Coherence and Cohesion\s*\|\s*(\d+)", raw_response)
    lexical_score = re.search(r"Lexical Resource\s*\|\s*(\d+)", raw_response)
    grammar_score = re.search(r"Grammatical Range & Accuracy\s*\|\s*(\d+)", raw_response)
    overall_score = re.search(r"\*\*Overall Band Score\*\*\s*\|\s*\*\*(\d+)\*\*", raw_response)
    
    # Extract feedback sections
    task_response_feedback = re.search(r"\*\*Task Response:\*\*\s*(.*?)(?=\*\*Coherence and Cohesion:|$)", raw_response, re.DOTALL)
    coherence_feedback = re.search(r"\*\*Coherence and Cohesion:\*\*\s*(.*?)(?=\*\*Lexical Resource:|$)", raw_response, re.DOTALL)
    lexical_feedback = re.search(r"\*\*Lexical Resource:\*\*\s*(.*?)(?=\*\*Grammatical Range and Accuracy:|$)", raw_response, re.DOTALL)
    grammar_feedback = re.search(r"\*\*Grammatical Range and Accuracy:\*\*\s*(.*?)$", raw_response, re.DOTALL)
    
    # Format the JSON response
    formatted_json = {
        "bands": {
            "task_response": int(task_response_score.group(1)) if task_response_score else None,
            "coherence_cohesion": int(coherence_score.group(1)) if coherence_score else None,
            "lexical_resource": int(lexical_score.group(1)) if lexical_score else None,
            "grammatical_range": int(grammar_score.group(1)) if grammar_score else None,
            "overall": int(overall_score.group(1)) if overall_score else None
        },
        "feedback": {
            "task_response": task_response_feedback.group(1).strip() if task_response_feedback else "",
            "coherence_cohesion": coherence_feedback.group(1).strip() if coherence_feedback else "",
            "lexical_resource": lexical_feedback.group(1).strip() if lexical_feedback else "",
            "grammatical_range": grammar_feedback.group(1).strip() if grammar_feedback else ""
        }
    }
    
    return formatted_json

