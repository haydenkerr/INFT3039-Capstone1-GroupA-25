"""
End-to-End API Testing for ELA RAG FastAPI Application

This script uses pytest to perform integration tests on the main API endpoints,
including essay grading, document listing, and results retrieval.

Requirements:
    - pytest
    - requests
    - pandas

To run:
    pytest test_end_to_end.py

Author: Group A, INFT3039 Capstone 1
"""

import pytest
import requests
import pandas as pd
import random
import time
import dotenv

dotenv.load_dotenv()

# Configuration for the API endpoint and test data
API_KEY = dotenv.get_key(dotenv.find_dotenv(), "API_KEY")
# BASE_URL = "https://ielts-unisa-groupa.me"
BASE_URL = "http://127.0.0.1:8008" # Local Fast API testing URL
# BASE_URL = "http://127.0.0.1:8002" # Local DOCKER IMAGE testing URL

# Download and prepare test data
TEST_XLSX_URL = (
    "https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25/raw/refs/heads/"
    "staging/ela_rag_docker/test_scripts/question_list_with_all_essays.xlsx"
)

@pytest.fixture(scope="session")
def test_data():
    """Load and prepare the test data from the provided XLSX file."""
    df = pd.read_excel(TEST_XLSX_URL, sheet_name='Sheet1')
    df = df[['task_id', 'question_text', 'complete_essay']]
    df['taskType'] = df['task_id'].map({
        1: "General Task 1",
        2: "General Task 2",
        3: "Academic Task 1",
        4: "Academic Task 2"
    })
    return df

@pytest.fixture(scope="session")
def random_essay(test_data):
    """Return a random essay row from the test data."""
    idx = random.randint(0, len(test_data) - 1)
    return test_data.iloc[idx]

def test_grade_essay_endpoint(test_data):
    """
    Test the /grade endpoint with a sample essay from the test set.
    """
    row = test_data.iloc[0]
    payload = {
        "email": "test.user@example.com",
        "question": row["question_text"],
        "essay": row["complete_essay"],
        "wordCount": len(str(row["complete_essay"]).split()),
        "submissionGroup": 1,
        "taskType": row["taskType"]
    }
    response = requests.post(
        f"{BASE_URL}/grade",
        headers={"x-api-key": API_KEY},
        json=payload,
        timeout=60
    )
    assert response.status_code == 200
    data = response.json()
    assert "tracking_id" in data
    assert "grading_result" in data
    assert "overall_score" in data

@pytest.mark.parametrize("row_idx", [1, 2, 3])
def test_multiple_essays(test_data, row_idx):
    """
    Test grading multiple essays from the test set.
    """
    row = test_data.iloc[row_idx]
    payload = {
        "email": "test.user@example.com",
        "question": row["question_text"],
        "essay": row["complete_essay"],
        "wordCount": len(str(row["complete_essay"]).split()),
        "submissionGroup": 2,
        "taskType": row["taskType"]
    }
    response = requests.post(
        f"{BASE_URL}/grade",
        headers={"x-api-key": API_KEY},
        json=payload,
        timeout=60
    )
    assert response.status_code == 200
    data = response.json()
    assert "tracking_id" in data

def test_debug_documents():
    """
    Test the /debug/documents endpoint for document listing.
    """
    response = requests.get(
        f"{BASE_URL}/debug/documents",
        headers={"x-api-key": API_KEY},
        timeout=10
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "metadata_count" in data

def test_debug_test():
    """
    Test the /debug/test endpoint for a simple response.
    """
    response = requests.get(
        f"{BASE_URL}/debug/test",
        headers={"x-api-key": API_KEY},
        timeout=10
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("This is a test") == "response"

def test_results_and_submissions(test_data):
    """
    Test retrieving results and submissions for a user.
    """
    # Submit an essay and get tracking_id
    row = test_data.iloc[4]
    payload = {
        "email": "test.user@example.com",
        "question": row["question_text"],
        "essay": row["complete_essay"],
        "wordCount": len(str(row["complete_essay"]).split()),
        "submissionGroup": 3,
        "taskType": row["taskType"]
    }
    response = requests.post(
        f"{BASE_URL}/grade",
        headers={"x-api-key": API_KEY},
        json=payload,
        timeout=60
    )
    assert response.status_code == 200
    data = response.json()
    tracking_id = data.get("tracking_id")
    assert tracking_id

    # Wait for results to be processed (if async)
    time.sleep(5)

    # Test /results/{tracking_id}
    response = requests.get(
        f"{BASE_URL}/results/{tracking_id}",
        headers={"x-api-key": API_KEY},
        timeout=20
    )
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "")

    # Test /submissions/{email}
    response = requests.get(
        f"{BASE_URL}/submissions/test.user@example.com",
        headers={"x-api-key": API_KEY},
        timeout=20
    )
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "")

