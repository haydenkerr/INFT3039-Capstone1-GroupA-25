from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
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

from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, Template

import smtplib
import dotenv
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pdfkit

from pdf_extract import router as pdf_router

app = FastAPI(
    title="ELA RAG API",
    description="This API allows question/essay pairing to query with RAG context system with Gemini LLM.",
    version="1.0.13",
    # docs_url= "/mydocs",  # Change the Swagger docs URL
    # redoc_url= "/myredoc"  # Change the Redoc docs URL
)

# Allow CORS (Adjust origins as per your security requirements)
app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

vector_db = VectorDatabase(embedding_dim=384)


# API_KEY and Amplify UI base URL and credentials for fetching templates
API_KEY = dotenv.get_key(dotenv.find_dotenv(), "API_KEY")
AMPLIFY_BASE_URL = dotenv.get_key(dotenv.find_dotenv(), "AMPLIFY_BASE_URL") or "https://main.d3f79dfa9zi46n.amplifyapp.com/"
AMPLIFY_UNAME = dotenv.get_key(dotenv.find_dotenv(), "AMPLIFY_UNAME")
AMPLIFY_PWORD = dotenv.get_key(dotenv.find_dotenv(), "AMPLIFY_PWORD")

def fetch_template(template_name):
    """
    Fetch an HTML template from the Amplify UI server.
    Uses basic auth for staging environments.

    Args:
        template_name (str): The template filename.

    Returns:
        str: The template content as a string.
    """
    url = f"{AMPLIFY_BASE_URL}/templates/{template_name}"
    if "staging" in AMPLIFY_BASE_URL:
        resp = requests.get(url, auth=(AMPLIFY_UNAME, AMPLIFY_PWORD))
    else:
        resp = requests.get(url)
    resp.raise_for_status()
    return resp.text



def verify_api_key(x_api_key: str = Header(None)):
    """
    Dependency to verify the API key in request headers.
    Raises HTTPException if the key is invalid.
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class QueryRequest(BaseModel):
    """Request model for vector DB query endpoint."""
    query_text: str

class EssayRequest(BaseModel):
    """Request model for essay grading endpoint."""
    email: str
    question: str
    essay: str
    wordCount: Optional[int] = None
    submissionGroup: Optional[int] = None
    taskType: Optional[str] = None

class Document:
    """Simple document class for page content."""
    def __init__(self, page_content):
        self.page_content = page_content

@app.get("/questions",
         summary="Get a random question",
         description="Returns a random question from the database for a specific task.")
def get_random_question(task_name: str):
    """
    Retrieve a random approved question for a given task type.

    Args:
        task_name (str): The name of the task.

    Returns:
        dict: A dictionary with a random question.
    """
    session = SessionLocal()
    try:
        task_id = get_task_id(task_name)
        stmt = (
            select(questions.c.question_text)
            .where(
                questions.c.task_id == task_id,
                questions.c.iscustom == False
            ).order_by(func.random())
            .limit(1)
        )
        result = session.execute(stmt).scalar()
        if result is None:
            raise ValueError(f"No approved questions found for task id {task_id}")
        return {"question": result}
    except Exception as e:
        print("Error in get_random_question", e)
        raise
    finally:
        session.close()

@app.post("/grade", dependencies=[Depends(verify_api_key)],
          summary="Grade an essay",
          description="Grades an essay based on the provided question and returns the grading result.")
def grade_essay(request: EssayRequest):
    """
    Grade an essay using Gemini LLM and store results in the database.

    Args:
        request (EssayRequest): The essay grading request.

    Returns:
        dict: Tracking ID, grading result, and overall score.
    """
    # Create unique tracking id & initial log
    tracking_id = str(uuid.uuid4())
    create_log(tracking_id, "API receives request", "Request received and parsing started")

    # Pre-gemini database insertions
    try:
        user_id = get_or_create_user(request.email)
        task_id = get_task_id(request.taskType)
        question_id = get_or_create_question(request.question, task_id)
        submission_id = insert_submission(
            user_id=user_id,
            task_id=task_id,
            question_id=question_id,
            submission_group=request.submissionGroup,
            essay_response=request.essay
        )
        create_log(
            tracking_id,
            "Pre-Gemini database insertions",
            f"User ID: {user_id}, Task ID: {task_id}, Question ID: {question_id}, Submission ID: {submission_id}",
            submission_id=submission_id
        )
    except Exception as e:
        create_log(tracking_id, "Error", f"Pre-Gemini Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error performing pre-gemini database insertions.")

    # Get similar examples using vector search
    query_embedding = np.array(get_embedding(request.question)).astype('float32')
    results = vector_db.search(query_embedding, top_k=5)
    examples_context = "\n\n".join([content for index, content, score in results])

    # Log vector DB results
    vector_db_logs = []
    for index_position, metadata, distance in results:
        vector_db_logs.append({
            "index_position": int(index_position),
            "metadata": metadata,
            "distance": distance
        })
    try:
        create_vector_db_log(submission_id, vector_db_logs)
        create_log(tracking_id, "Created vector_db_logs", "Logged the vector_db examples", submission_id)
    except Exception as e:
        create_log(tracking_id, "Error", f"Vector_db logging failed: {str(e)}", submission_id=submission_id)
        raise HTTPException(status_code=500, detail="Error logging vector db examples")

    print(f"📨 Input to Gemini:\nQuestion: {request.question}\nEssay: {request.essay}")
    create_log(tracking_id, "Sent to Gemini", "Sending question, essay, and similar examples to model", submission_id)

    try:
        llm_response = query_gemini(
            task_id=task_id,
            user_prompt="",
            examples_context=examples_context,
            question=request.question,
            essay=request.essay
        )
        if not llm_response:
            create_log(tracking_id, "Error", "No response received from Gemini", submission_id=submission_id)
            raise HTTPException(status_code=502, detail="No response from Gemini model")
    except Exception as e:
        create_log(tracking_id, "Error", f"Gemini model call failed: {str(e)}", submission_id=submission_id)
        raise HTTPException(status_code=500, detail="Error communicating with Gemini model")

    print(f"LLM Response: {llm_response}")
    create_log(tracking_id, "Receive model response", "Received response from Gemini", submission_id)

    # Try direct JSON parsing first
    try:
        grading_result = json.loads(llm_response)
        try:
            results_data = prepare_results_from_grading_data(submission_id, grading_result)
            overall_score = insert_results(submission_id, results_data)
            create_log(tracking_id, "Post-Gemini Database Insertions", "Results successfully inserted into database", submission_id=submission_id)
            send_results_email(request.email, tracking_id)
        except Exception as db_error:
            create_log(tracking_id, "Error", f"Error inserting results into database {str(db_error)}", submission_id=submission_id)
            raise HTTPException(status_code=500, detail="Error saving results to database.")
        return {"tracking_id": tracking_id, "grading_result": grading_result, "overall_score": overall_score}
    except json.JSONDecodeError:
        import re
        try:
            formatted_json = parse_grading_response(llm_response)
            try:
                results_data = prepare_results_from_grading_data(submission_id, formatted_json)
                overall_score = insert_results(submission_id, results_data)
                create_log(tracking_id, "Post-Gemini Database Insertions", "Results successfully inserted into database", submission_id=submission_id)
                send_results_email(request.email, tracking_id)
            except Exception as db_error:
                create_log(tracking_id, "Error", f"Error inserting results into database {str(db_error)}", submission_id=submission_id)
                raise HTTPException(status_code=500, detail="Error saving results to database.")
            return {"tracking_id": tracking_id, "grading_result": formatted_json, "overall_score": overall_score}
        except Exception as e:
            create_log(tracking_id, "Error", f"LLM response parsing failed: {str(e)}", submission_id=submission_id)
            return {
                "tracking_id": tracking_id,
                "error": "Could not parse LLM response",
                "message": str(e),
                "raw_response": llm_response
            }

@app.get("/results/{tracking_id}", response_class=HTMLResponse,
         summary="Get results for a specific tracking ID",
         description="Returns the results of the essay grading process for a specific tracking ID.")
def show_results(tracking_id: str):
    """
    Retrieve and render the grading results for a specific tracking ID.

    Args:
        tracking_id (str): The unique tracking ID for the submission.

    Returns:
        HTMLResponse: Rendered HTML page with grading results.
    """
    session = SessionLocal()
    try:
        submission = session.execute(
            select(submissions)
            .join(submissions_log, submissions.c.submission_id == submissions_log.c.submission_id)
            .where(submissions_log.c.tracking_id == tracking_id)
        ).fetchone()
        if not submission:
            return HTMLResponse(content="No results found", status_code=404)
        submission_id = submission.submission_id
        question_id = submission.question_id 
        overall_score = submission.overall_score
        question = session.execute(
            select(questions.c.question_text)
            .where(questions.c.question_id == question_id)
        ).scalar()
        essay = submission.essay_response
        results_data = session.execute(
            select(results)
            .where(results.c.submission_id == submission_id)
        ).fetchall()
        # Format and return results
        response_data = {
            "question": question,
            "essay": essay,
            "overall_score": overall_score,
            "results": [{
                "competency_name": result.competency_name,
                "score": result.score,
                "feedback_summary": result.feedback_summary,
            } for result in results_data]
        }
        # Fetch template from Amplify
        template_str = fetch_template('result_template.html')
        template = Template(template_str)
        html_content = template.render(response_data)
        create_log(
            tracking_id=tracking_id, 
            log_type="Results Accessed", 
            log_message="Results returned to the API for the user", 
            submission_id=submission_id
        )
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        create_log(
            tracking_id=tracking_id, 
            log_type="Error", 
            log_message=f"Error occurred while returning results to the API: {str(e)}", 
            submission_id=submission_id
        )
        return HTMLResponse(content=f"An error occurred: {str(e)}", status_code=500)
    finally:
        session.close()

@app.get("/debug/documents",
         summary="Debug endpoint to check loaded documents",
         description="Returns the total number of documents and a sample of metadata.")
def list_documents():
    """
    Debug endpoint to check loaded documents in the vector database.

    Returns:
        dict: Total document count and a sample of metadata.
    """
    return {
        "total_documents": vector_db.index.ntotal, 
        "metadata_count": len(vector_db.metadata),
        "metadata_sample": list(vector_db.metadata.items())[:5] if vector_db.metadata else []
    }

def send_results_email(to_email, tracking_id, host_url="https://ielts-unisa-groupa.me"):
    """
    Send results email to the user with a link to their results and a PDF attachment.

    Args:
        to_email (str): Recipient's email address.
        tracking_id (str): Submission tracking ID.
        host_url (str): Base URL for results page.
    """
    subject = "Your ELA Results Are Ready"
    results_link = f"{host_url}/results/{tracking_id}"
    body = f"Thank you for your submission. You can view your results here:\n{results_link}"

    # Generate PDF from the results page
    pdf_filename = f"results_{tracking_id}.pdf"
    pdf_url = results_link
    try:
        pdfkit.from_url(pdf_url, pdf_filename)
    except Exception as e:
        print(f"Failed to generate PDF: {e}")
        pdf_filename = None

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "ela.ielts.project@gmail.com"
    msg["To"] = to_email

    # If PDF was generated, attach it
    if pdf_filename and os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_filename))
            from email.mime.multipart import MIMEMultipart
            multipart_msg = MIMEMultipart()
            multipart_msg.attach(MIMEText(body, "plain"))
            multipart_msg.attach(part)
            multipart_msg["Subject"] = subject
            multipart_msg["From"] = msg["From"]
            multipart_msg["To"] = msg["To"]
            msg = multipart_msg

    smtp_server = "email-smtp.ap-southeast-2.amazonaws.com"
    smtp_port = 587
    smtp_user = dotenv.get_key(dotenv.find_dotenv(), "smtp_user")
    smtp_password = dotenv.get_key(dotenv.find_dotenv(), "smtp_password")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], [to_email], msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        # Clean up the PDF file
        if pdf_filename and os.path.exists(pdf_filename):
            os.remove(pdf_filename)

@app.get("/debug/test",
         summary="Test Endpoint",
         description="Returns a simple test response to verify the API is running.")
def test_response():
    """Simple test endpoint to verify API is running."""
    return {"This is a test": "response"}

def build_score_table(bands: dict) -> str:
    """
    Build a Markdown table for band scores.

    Args:
        bands (dict): Dictionary of band scores.

    Returns:
        str: Markdown table as a string.
    """
    if not all(bands.get(k) is not None for k in ["task_response", "coherence_cohesion", "lexical_resource", "grammatical_range", "overall"]):
        return ""
    table = [
        "| Criterion | Band Score |",
        "| --------- | ---------- |",
        f"| Task Response | {bands['task_response']} |",
        f"| Coherence and Cohesion | {bands['coherence_cohesion']} |",
        f"| Lexical Resource | {bands['lexical_resource']} |",
        f"| Grammatical Range & Accuracy | {bands['grammatical_range']} |",
        f"| **Overall Band Score** | **{bands['overall']}** |"
    ]
    return "\n".join(table)

def parse_grading_response(raw_response):
    # Extract band scores from the response
    #task_response_score = re.search(r"Task Response\s*\|\s*(\d+)", raw_response)
    task_response_score = re.search(r"(?:Task Response|Task Achievement)\s*\|\s*(\d+)", raw_response)
    coherence_score = re.search(r"Coherence and Cohesion\s*\|\s*(\d+)", raw_response)
    lexical_score = re.search(r"Lexical Resource\s*\|\s*(\d+)", raw_response)
    grammar_score = re.search(r"Grammatical Range & Accuracy\s*\|\s*(\d+)", raw_response)
    overall_score = re.search(r"\*\*Overall Band Score\*\*\s*\|\s*\*\*(\d+)\*\*", raw_response)
    
   
    task_response_feedback = re.search(
    r"(?:^|\n)\s*(?:\*\*\s*)?(?:1\.\s*)?(?:\*\*)?\s*(Task Response|Task Achievement)\s*(?:\*\*)?\s*\n+(.*?)(?=\n\s*(?:\*\*\s*)?(?:2\.\s*)?(?:\*\*)?\s*Coherence and Cohesion)",
    raw_response,
    re.DOTALL | re.IGNORECASE
)

    coherence_feedback = re.search(
    r"\*\*\s*(?:2\.\s*)?Coherence and Cohesion\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:3\.\s*)?Lexical Resource\s*\*\*)",
    raw_response, re.DOTALL)

    # lexical_feedback = re.search(
    # r"\*\*\s*3\.\s*Lexical Resource\s*\*\*\s*(.*?)(?=\n\*\*\s*4\.\s*Grammatical Range\s*&\s*Accuracy\s*\*\*)",
    # raw_response, re.DOTALL)
    lexical_feedback = re.search(
    r"\*\*\s*(?:3\.\s*)?Lexical Resource\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:4\.\s*)?Grammatical Range\s*(?:&|and)\s*Accuracy\s*\*\*)",
    raw_response, re.DOTALL | re.IGNORECASE)

    # grammar_feedback = re.search(
    # r"\*\*\s*4\.\s*Grammatical Range\s*&\s*Accuracy\s*\*\*\s*(.*?)(?=\n\*\*\s*5\.\s*Overall Band Score Summary\s*\*\*)",
    # raw_response, re.DOTALL)
    grammar_feedback = re.search(
    r"\*\*\s*(?:4\.?)?\s*Grammatical Range\s*(?:&|and)\s*Accuracy\*\*\s*(.*?)(?=\n\*\*\s*(?:5\.?)?\s*Overall Band Score Summary\*\*)",
    raw_response, re.DOTALL | re.IGNORECASE)

    overall_summary_feedback = re.search(
    r"\*\*\s*(?:5\.\s*)?Overall Band Score Summary\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:6\.\s*)?Feedback\s*\*\*)",
    raw_response, re.DOTALL)

    general_feedback = re.search(
    r"\*\*\s*(?:6\.\s*)?Feedback\s*\*\*\s*(.*?)(?=\n\*\*\s*(?:7\.\s*)?Scoring Table\s*\*\*)",
    raw_response, re.DOTALL)


    def safe_extract(regex_match, group_num=1):
        try:
            return regex_match.group(group_num).strip()
        except:
            return ""
    
    print("🧪 Raw regex matches:")
    print("  cohrence_feedback:", bool(coherence_feedback))
    print("  lexical_feedback:", bool(lexical_feedback))
    print("  grammar_feedback:", bool(grammar_feedback))
    print("  overall_summary_feedback:", bool(overall_summary_feedback))
    print("  general_feedback:", bool(general_feedback))
    print("📥 Matched Task Feedback:", task_response_feedback.group(1) if task_response_feedback else "❌ Not found")
    print("📥 Matched Coherence Feedback:", coherence_feedback.group(1) if coherence_feedback else "❌ Not found")
    print("📥 Matched Lexical Feedback:", lexical_feedback.group(1) if lexical_feedback else "❌ Not found")
    print("📥 Matched Grammer Feedback:", grammar_feedback.group(1) if grammar_feedback else "❌ Not found")
    print("📥 Matched Overall Feedback:", overall_summary_feedback.group(1) if overall_summary_feedback else "❌ Not found")
    print("📥 Matched General Feedback:", general_feedback.group(1) if general_feedback else "❌ Not found")


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
            "task_response": safe_extract(task_response_feedback,group_num=2),
            "coherence_cohesion": safe_extract(coherence_feedback),
            "lexical_resource": safe_extract(lexical_feedback),
            "grammatical_range": safe_extract(grammar_feedback),
            "overall_summary": safe_extract(overall_summary_feedback),
            "general_feedback": safe_extract(general_feedback)
        },
        "score_table": build_score_table({
            "task_response": task_response_score.group(1) if task_response_score else None,
            "coherence_cohesion": coherence_score.group(1) if coherence_score else None,
            "lexical_resource": lexical_score.group(1) if lexical_score else None,
            "grammatical_range": grammar_score.group(1) if grammar_score else None,
            "overall": overall_score.group(1) if overall_score else None
        })
    }
    print("🧪 Feedback Values:")
    for k, v in formatted_json["feedback"].items():
        print(f"{k}: {v[:100]}{'...' if len(v) > 100 else ''}")
    
    print("🧪 Parsed scores:", {
        "task": task_response_score.group(1) if task_response_score else None,
        "coherence": coherence_score.group(1) if coherence_score else None,
        "lexical": lexical_score.group(1) if lexical_score else None,
        "grammar": grammar_score.group(1) if grammar_score else None,
        "overall": overall_score.group(1) if overall_score else None
    })
    return formatted_json


@app.get("/submissions/{email}", response_class=HTMLResponse,
         summary="List all submissions for a user",
         description="Returns a table of all previous submissions for the given email address.")
def list_user_submissions(email: str):
    """
    List all previous submissions for a given user email.

    Args:
        email (str): The user's email address.

    Returns:
        HTMLResponse: Rendered HTML page with submissions table.
    """
    session = SessionLocal()
    try:
        # Get user_id for the email
        user = session.execute(
            select(users.c.user_id).where(users.c.email == email)
        ).fetchone()
        if not user:
            return HTMLResponse(content=f"No submissions found for {email}", status_code=404)
        user_id = user.user_id

        # Get all submissions for this user
        submissions_data = session.execute(
            select(
                submissions.c.submission_timestamp,
                submissions.c.submission_id,
                submissions.c.question_id,
                submissions.c.essay_response,
                submissions.c.overall_score
            ).where(submissions.c.user_id == user_id)
            .order_by(submissions.c.submission_timestamp.desc())
        ).fetchall()

        # Get tracking_ids for each submission
        tracking_ids = {}
        for row in submissions_data:
            log = session.execute(
                select(submissions_log.c.tracking_id)
                .where(submissions_log.c.submission_id == row.submission_id)
                .order_by(submissions_log.c.log_timestamp.asc())
            ).fetchone()
            tracking_ids[row.submission_id] = log.tracking_id if log else None

        # Get questions for each question_id
        question_texts = {}
        for row in submissions_data:
            if row.question_id not in question_texts:
                q = session.execute(
                    select(questions.c.question_text)
                    .where(questions.c.question_id == row.question_id)
                ).scalar()
                question_texts[row.question_id] = q

        # Prepare data for template
        submissions_list = []
        for row in submissions_data:
            submitted_date = row.submission_timestamp.strftime("%Y-%m-%d %H:%M")
            tracking_id = tracking_ids.get(row.submission_id, "")
            question = question_texts.get(row.question_id, "")
            essay = (row.essay_response[:100] + "...") if len(row.essay_response) > 100 else row.essay_response
            overall_score = row.overall_score if row.overall_score is not None else ""
            submissions_list.append({
                "submitted_date": submitted_date,
                "tracking_id": tracking_id,
                "question": question,
                "essay": essay,
                "overall_score": overall_score
            })

        # Fetch template from Amplify
        template_str = fetch_template('submissions_template.html')
        template = Template(template_str)
        html_content = template.render(email=email, submissions=submissions_list)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)
    finally:
        session.close()

@app.post("/ingest-from-url", dependencies=[Depends(verify_api_key)],
          summary="Ingest a file from a URL",
          description="Ingests a file from a public GitHub or raw file URL and adds it to the vector database.")
def ingest_file_from_url(url: str = Query(..., description="Public GitHub or raw file URL")):
    """
    Ingest a file from a public URL and add its content to the vector database.

    Args:
        url (str): The public file URL.

    Returns:
        dict: Success message.
    """
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

# Include PDF extraction router
app.include_router(pdf_router)