from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from file_parser import extract_text
import numpy as np
import json
from vector_db import VectorDatabase
from hf_embeddings import get_embedding
from gemini_client import query_gemini
import os

import regex as re

from fastapi import Query
import requests
import tempfile
import shutil

from database import *
from typing import Optional
import uuid

app = FastAPI(    title="ELA Finetuned RAG API",
    description="This API allows quesiton/essay pairing to query a finetune model with RAG system with Gemini.",
    version="1.0.0",
    # docs_url= "/mydocs",  # Change the Swagger docs URL
    # redoc_url= "/myredoc"  # Change the Redoc docs URL
)


# Allow CORS (Adjust origins as per your security requirements)
#  need to check this , as
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
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
    email: str
    question: str
    essay: str
    wordCount: Optional[int] = None
    submissionGroup: Optional[int] = None
    taskType: Optional[str] = None

class Document:
    def __init__(self, page_content):
        self.page_content = page_content

@app.post("/grade", dependencies=[Depends(verify_api_key)])
def grade_essay(request: EssayRequest):

    # Create unique tracking id & initial log
    tracking_id = str(uuid.uuid4())
    create_log(tracking_id, "API receives request", "Request received and parsing started")

    # Perform initial database retrievals and insertions
    try:
        
        # Step 1: Get or insert user
        user_id = get_or_create_user(request.email)

        # Step 2: Get task_id from task_name
        task_id = get_task_id(request.taskType)

        # Step 3: Get or insert question
        question_id = get_or_create_question(request.question, task_id)

        # Step 4: Insert submission
        submission_id = insert_submission(
            user_id=user_id,
            task_id=task_id,
            question_id=question_id,
            submission_group=request.submissionGroup,
            essay_response=request.essay
        )

        # Step 5: Add log for successful insertion
        create_log(
            tracking_id,
            "Pre-Gemini database insertions",
            f"User ID: {user_id}, Task ID: {task_id}, Question ID: {question_id}, Submission ID: {submission_id}",
            submission_id=submission_id
        )

    except Exception as e:
        # Add error to log if not successfully inserted
        create_log(
            tracking_id,
            "Error",
            f"Pre-Gemini Database Error: {str(e)}"
        )

        raise HTTPException(status_code=500, detail="Error performing pre-gemini database insertions.")

    # Get similar examples using vector search
    query_embedding = np.array(get_embedding(request.question)).astype('float32')
    results = vector_db.search(query_embedding, top_k=5)
    
    # Format examples into context
    examples_context = "\n\n".join([content for content, score in results])
    
    print(f"📨 Input to Gemini:\nQuestion: {request.question}\nEssay: {request.essay}")
    create_log(tracking_id, "Sent to Gemini", "Sending question, essay, and similar examples to model", submission_id)

    try:
        # Pass to gemini_client with question and essay
        llm_response = query_gemini(
            user_prompt="",
            examples_context=examples_context,
            question=request.question,
            essay=request.essay
        )

        if not llm_response:
            create_log(
                tracking_id,
                "Error",
                "No response received from Gemini",
                submission_id = submission_id
            )
            raise HTTPException(status_code=502, detail="No response from Gemini model")
        
    except Exception as e:
        create_log(
            tracking_id,
            "Error",
            f"Gemini model call failed: {str(e)}",
            submission_id = submission_id
        )
        raise HTTPException(status_code=500, detail = "Error communicating with Gemini model")
    
    print(f"LLM Response: {llm_response}")  # Log the raw Gemini response
    create_log(tracking_id, "Receive model response", "Received response from Gemini", submission_id)
    
    # First try direct JSON parsing
    try:
        grading_result = json.loads(llm_response)
        print(grading_result)

        try:
            results_data = prepare_results_from_grading_data(submission_id, grading_result)
            insert_results(submission_id, results_data)

            create_log(
                tracking_id,
                "Post-Gemini Database Insertions",
                "Results successfully inserted into database",
                submission_id = submission_id
            )
        
        except Exception as db_error:
            create_log(
                tracking_id,
                "Error",
                f"Error inserting results into database {str(db_error)}",
                submission_id = submission_id
            )

            raise HTTPException(status_code=500, detail="Error saving results to database.")

        return grading_result
    
    except json.JSONDecodeError:
        # Use the parsing function when JSON extraction fails
        import re
        try:
            formatted_json = parse_grading_response(llm_response)

            try:
                results_data = prepare_results_from_grading_data(submission_id, formatted_json)
                insert_results(submission_id, results_data)

                create_log(
                    tracking_id,
                    "Post-Gemini Database Insertions",
                    "Results successfully inserted into database",
                    submission_id = submission_id
                )

            except Exception as db_error:
                create_log(
                    tracking_id,
                    "Error",
                    f"Error inserting results into database {str(db_error)}",
                    submission_id = submission_id
                )

                raise HTTPException(status_code=500, detail = "Error saving results to database.")

            return formatted_json
        except Exception as e:

            create_log(
                tracking_id,
                "Error",
                "LLM response parsing failed: {str(e)}",
                submission_id = submission_id
            )

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


@app.post("/ingest-from-url", dependencies=[Depends(verify_api_key)])
def ingest_file_from_url(url: str = Query(..., description="Public GitHub or raw file URL")):
    try:
        # Download file to temp
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download file")

        suffix = os.path.splitext(url)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(response.raw, tmp)
            file_path = tmp.name

        content = extract_text(file_path)
        embedding = get_embedding(content)
        vector_db.add_document(np.array(embedding), doc_id=os.path.basename(url), metadata=content[:200])
        
        return {"message": f"Successfully ingested: {url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")