"""
Unit tests for database.py functions.

Tests rely on a connection to the project's PostgreSQL database and use pytest fixtures
for setup. Ensure the database is configured correctly before running.

To run:
    pytest test_database.py
"""

import pytest
import uuid
from database import *
from sqlalchemy import select, delete 
from datetime import datetime

@pytest.fixture
def sample_submission():

    session = SessionLocal()

    try:
        user_id = get_or_create_user("unit.test@testing.com")
        task_id = 1
        question_text = "This is a sample question for unit testing."
        question_id = get_or_create_question(question_text, task_id)
        submission_group = 6
        essay_response = "This is a sample essay response for unit testing."
        submission_id = insert_submission(user_id, task_id, question_id, submission_group, essay_response)

        yield {
            "submission_id": submission_id,
            "user_id": user_id,
            "task_id": task_id,
            "question_id": question_id,
            "submission_group": submission_group,
            "essay_response": essay_response
        }

    finally:
        session.execute(results_log.delete().where(results_log.c.submission_id == submission_id))
        session.execute(results.delete().where(results.c.submission_id == submission_id))
        session.execute(submissions.delete().where(submissions.c.submission_id == submission_id))
        session.execute(questions.delete().where(questions.c.question_id == question_id))
        session.execute(users.delete().where(users.c.user_id == user_id))
        session.commit()
        session.close()

# ------------------------------------------------------------------------------------------
# TEST database connection
# ------------------------------------------------------------------------------------------

def test_database_connection():

    session = SessionLocal()

    try:
        result = session.execute(select(users)).fetchone() # Try to fetch from any database table
        assert results is not None, "No data found in users table"

    finally:
        session.close()

# ------------------------------------------------------------------------------------------
# TEST get_or_create_user
# ------------------------------------------------------------------------------------------

def test_get_or_create_user_new():

    session = SessionLocal()

    email = "unit_test_new@test.com"

    try:
        user_id = get_or_create_user(email)

        result = session.execute(select(users).where(users.c.email == email)).fetchone()

        assert result is not None, "Assert is none"
        assert result[0] == user_id, "Result does not match user id"
    
    finally:

        session.execute(users.delete().where(users.c.email == email))
        session.commit()
        session.close()


def test_get_or_create_user_existing():

    session = SessionLocal()
    
    email = "unit_test_existing@test.com"

    try:
        # Add the new user using the function & store returned id
        first_id = get_or_create_user(email)

        # Call the function a second time for the same email and store returned id
        second_id = get_or_create_user(email)

        assert first_id == second_id, "Expected same user ID to be returned each time"
           
    finally:

        session.execute(users.delete().where(users.c.email == email))
        session.commit()
        session.close()


# ------------------------------------------------------------------------------------------
# TEST get_task_id
# ------------------------------------------------------------------------------------------

def test_get_task_id_valid():

    expected_tasks = {
        "General Task 1": 1,
        "General Task 2": 2,
        "Academic Task 1": 3,
        "Academic Task 2": 4
    }

    session = SessionLocal()

    try:
        for task_name, expected_id in expected_tasks.items():
            actual_id = get_task_id(task_name)
            assert actual_id == expected_id, f"Expected ID {expected_id} for {task_name}, got {actual_id}"
    
    finally:
        session.close()

def test_get_task_id_invalid():

    invalid_name = "Non-existent Task"

    with pytest.raises(ValueError) as e:
        get_task_id(invalid_name)

    assert f"Task name '{invalid_name}' not found in database." in str(e)


# ------------------------------------------------------------------------------------------
# TEST get_or_create_question
# ------------------------------------------------------------------------------------------

def test_get_or_create_question_new():

    session = SessionLocal()

    question = "This is a test new question."

    try:
        question_id = get_or_create_question(question, 1)

        result = session.execute(select(questions).where(questions.c.question_text == question)).fetchone()

        assert result is not None, "Assert is none"
        assert result[0] == question_id, "Result does not match question id"
    
    finally:

        session.execute(questions.delete().where(questions.c.question_text == question))
        session.commit()
        session.close()


def test_get_or_create_user_existing():

    session = SessionLocal()
    
    question = "This is a test new question."

    try:
        # Add the new user using the function & store returned id
        first_id = get_or_create_question(question, 1)

        # Call the function a second time for the same email and store returned id
        second_id = get_or_create_question(question, 1)

        assert first_id == second_id, "Expected same question ID to be returned each time"
           
    finally:

        session.execute(questions.delete().where(questions.c.question_text == question))
        session.commit()
        session.close()


# ------------------------------------------------------------------------------------------
# TEST calculate_overall_score
# ------------------------------------------------------------------------------------------

def test_rounding_up_6_25():

    results = [
        {"competency_name": "Task Response", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Coherence and Cohesion", "score": 6.5, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Lexical Resource", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Grammatical Range and Accuracy", "score": 6.5, "feedback_summary": "", "submission_id": 1},
    ]

    assert calculate_overall_score(results) == 6.5

def test_rounding_up_6_75():

    results = [
        {"competency_name": "Task Response", "score": 7.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Coherence and Cohesion", "score": 6.5, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Lexical Resource", "score": 7.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Grammatical Range and Accuracy", "score": 6.5, "feedback_summary": "", "submission_id": 1},
    ]

    assert calculate_overall_score(results) == 7.0

def test_no_rounding_half_band():

    results = [
        {"competency_name": "Task Response", "score": 7.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Coherence and Cohesion", "score": 7.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Lexical Resource", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Grammatical Range and Accuracy", "score": 6.0, "feedback_summary": "", "submission_id": 1},
    ]

    assert calculate_overall_score(results) == 6.5

def test_rounding_exact_band():

    results = [
        {"competency_name": "Task Response", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Coherence and Cohesion", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Lexical Resource", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Grammatical Range and Accuracy", "score": 6.0, "feedback_summary": "", "submission_id": 1},
    ]

    assert calculate_overall_score(results) == 6.0

def test_missing_competency():

    # Define results with one missing competency
    results = [
        {"competency_name": "Task Response", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Coherence and Cohesion", "score": 6.0, "feedback_summary": "", "submission_id": 1},
        {"competency_name": "Lexical Resource", "score": 6.0, "feedback_summary": "", "submission_id": 1},
    ]

    with pytest.raises(ValueError) as e:
        calculate_overall_score(results)

    assert "Expected scores for the 4 IELTS core competencies" in str(e)

# ------------------------------------------------------------------------------------------
# TEST create_vector_db_log
# ------------------------------------------------------------------------------------------

def test_create_vector_db_log():

    session = SessionLocal()

    submission_id = 9999

    test_logs = [
        {
            "index_position": 0,
            "metadata": "Test example A",
            "distance": 0.23
        },
        {
            "index_position": 1,
            "metadata": "Test example B",
            "distance": 0.45           
        }
    ]

    try:
        create_vector_db_log(submission_id, test_logs)

        stmt = select(vector_db_log).where(vector_db_log.c.submission_id == submission_id)

        results = session.execute(stmt).fetchall()

        assert len(results) == 2, "Expected 2 log entries to be inserted."

        for i, row in enumerate(results):
            assert row.index_position == test_logs[i]["index_position"]
            assert row.metadata == test_logs[i]["metadata"]
            assert abs(row.distance - test_logs[i]["distance"]) < 1e-6 # to account for small changes in precision

    finally:
        
        session.execute(vector_db_log.delete().where(vector_db_log.c.submission_id == submission_id))
        session.commit()
        session.close()

# ------------------------------------------------------------------------------------------
# TEST create_log
# ------------------------------------------------------------------------------------------

def test_create_log():

    session = SessionLocal()

    tracking_id = uuid.uuid4()
    log_type = "INFO"
    log_message = "This is a test log message"
    submission_id = None

    try:
        create_log(tracking_id, log_type, log_message, submission_id)

        stmt = select(submissions_log).where(
            submissions_log.c.tracking_id == tracking_id,
            submissions_log.c.log_type == log_type,
            submissions_log.c.log_message == log_message)
        
        result = session.execute(stmt).fetchone()

        assert result is not None, "Log entry was not created"
        assert result.tracking_id == tracking_id, "Tracking id does not match"
        assert result.log_type == log_type, "Log type does not match"
        assert result.log_message == log_message, "Log message does not match"
        assert result.submission_id == submission_id, "Submission id does not match"

    finally:

        session.execute(submissions_log.delete().where(submissions_log.c.tracking_id == tracking_id))
        session.commit()
        session.close()


# ------------------------------------------------------------------------------------------
# TEST insert_submission
# ------------------------------------------------------------------------------------------

def test_insert_submission():

    session = SessionLocal()

    user_id = get_or_create_user("unit.test@testing.com")
    task_id = 1
    question_text = "This is a sample question for unit testing."
    question_id = get_or_create_question(question_text, task_id)
    submission_group = 6
    essay_response = "This is a test essay for unit testing."

    try:
        submission_id = insert_submission(user_id, task_id, question_id, submission_group, essay_response)

        stmt = select(submissions).where(submissions.c.submission_id == submission_id)
        result = session.execute(stmt).fetchone()

        assert result is not None, "Submission was not inserted"
        assert result.user_id == user_id, "User ID doesn't match"
        assert result.task_id == task_id, "Task ID doesn't match"
        assert result.question_id == question_id, "Question ID doesn't match"
        assert result.submission_group == submission_group, "Submission group doesn't match"
        assert result.essay_response == essay_response, "Essay response doesn't match"

    finally:

        session.execute(submissions.delete().where(submissions.c.submission_id == submission_id))
        session.execute(questions.delete().where(questions.c.question_id == question_id))
        session.execute(users.delete().where(users.c.user_id == user_id))
        session.commit()
        session.close()
    

# ------------------------------------------------------------------------------------------
# TEST update_validated
# ------------------------------------------------------------------------------------------

def test_update_validated(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    session = SessionLocal()

    try:
        update_validated(submission_id, True)

        result = session.execute(
            select(submissions.c.validated).where(submissions.c.submission_id == submission_id)
        ).scalar()

        assert result is True, "Expected validated field to be true"

        update_validated(submission_id, False)

        result = session.execute(
            select(submissions.c.validated).where(submissions.c.submission_id == submission_id)
        ).scalar()

        assert result is False, "Expected validated field to be false"   

    finally:
        session.close()    


# ------------------------------------------------------------------------------------------
# TEST get_validated_value
# ------------------------------------------------------------------------------------------

def test_get_validated_value(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    # Default value should be none - test that first
    result = get_validated_value(submission_id)
    assert result is None, f"Expected None, got {result}"

    # Set validated to true, then test that
    update_validated(submission_id, True)
    result = get_validated_value(submission_id)
    assert result is True, f"Expected true, got {result}"

    # Set validated to false, then test that
    update_validated(submission_id, False)
    result = get_validated_value(submission_id)
    assert result is False, f"Expected false, got {result}"


# ------------------------------------------------------------------------------------------
# TEST update_overall_score
# ------------------------------------------------------------------------------------------

def test_update_overall_score(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    new_score = 7.5

    # Default overall score is null - test that first
    session = SessionLocal()

    initial_score = session.execute(
        select(submissions.c.overall_score).where(submissions.c.submission_id == submission_id)
    ).scalar()

    session.close()

    assert initial_score is None, "Expected initial overall_score to be none"

    # Update the overall score, then test it
    update_overall_score(submission_id, new_score)

    session = SessionLocal()

    updated_score = session.execute(
        select(submissions.c.overall_score).where(submissions.c.submission_id == submission_id)
    ).scalar()
    
    session.close()

    assert updated_score == new_score, f"Expected overall score to be {new_score} but got {updated_score}"


# ------------------------------------------------------------------------------------------
# TEST insert_results
# ------------------------------------------------------------------------------------------

def test_insert_results(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    # Create dummy results data
    results_data = [
        {
            "submission_id": submission_id,
            "competency_name": "Task Response",
            "score": 6.0,
            "feedback_summary": "Good Task Response"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Coherence and Cohesion",
            "score": 7.0,
            "feedback_summary": "Good Coherence and Cohesion"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Lexical Resource",
            "score": 6.0,
            "feedback_summary": "Good Lexical Resource"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Grammatical Range and Accuracy",
            "score": 6.0,
            "feedback_summary": "Good Grammatical Range and Accuracy"
        },
    ]

    # First test correct overall score is returned
    overall_score = insert_results(submission_id, results_data)

    expected_score = calculate_overall_score(results_data)
    assert overall_score == expected_score, "Overall score did not match expected calculation"

    # Next test the overall score has been correctly updated in the submissions table
    session = SessionLocal()

    try:
        result = session.execute(
            select(submissions.c.overall_score).where(submissions.c.submission_id == submission_id)
        ).scalar()

        assert result == overall_score, "Overall score in database does not match returned value"

        # Next test all results were inserted into the results table
        result = session.execute(
            select(results).where(results.c.submission_id == submission_id)
        ).fetchall()

        assert len(result) == 4, "Number of inserted results does not match"

    finally:
        session.close()


# ------------------------------------------------------------------------------------------
# TEST prepare_results_from_grading_data
# ------------------------------------------------------------------------------------------

def test_prepare_results_from_grading_data():

    submission_id = 99

    # Create dummy model response data, intentionally including None and empty feedback to test skipping
    grading_result = {
        "bands": {
            "task_response": 6.0,
            "coherence_cohesion": 7.0,
            "lexical_resource": None,           
            "grammatical_range": 6.0,
            "overall_summary": None,
            "general_feedback": None
        },
        "feedback": {
            "task_response": "Good task completion",
            "coherence_cohesion": "Well connected ideas",
            "lexical_resource": "",             
            "grammatical_range": "Minor errors present",
            "overall_summary": "Good overall",              
            "general_feedback": "Keep practicing"
        }
    }

    results = prepare_results_from_grading_data(submission_id, grading_result)

    # Expected results has no lexical resource (as empty), and overall summary & general feedback scores should
    # be replaced with 0.0
    expected_results = [
        {
            "submission_id": submission_id,
            "competency_name": "Task Response",
            "score": 6.0,
            "feedback_summary": "Good task completion"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Coherence and Cohesion",
            "score": 7.0,
            "feedback_summary": "Well connected ideas"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Grammatical Range and Accuracy",
            "score": 6.0,
            "feedback_summary": "Minor errors present"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Summary",
            "score": 0.0,                     
            "feedback_summary": "Good overall"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Feedback",
            "score": 0.0,                     
            "feedback_summary": "Keep practicing"
        }
    ]

    assert len(results) == len(expected_results), f"Expected {len(expected_results)} results but got {len(results)}"

    for entry in results:
        assert entry in results, f"Expected entry missing: {entry}"


# ------------------------------------------------------------------------------------------
# TEST get_results
# ------------------------------------------------------------------------------------------

def test_get_results(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    # Create dummy results data
    results_data = [
        {
            "submission_id": submission_id,
            "competency_name": "Task Response",
            "score": 6.0,
            "feedback_summary": "Good Task Response"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Coherence and Cohesion",
            "score": 7.0,
            "feedback_summary": "Good Coherence and Cohesion"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Lexical Resource",
            "score": 6.0,
            "feedback_summary": "Good Lexical Resource"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Grammatical Range and Accuracy",
            "score": 6.0,
            "feedback_summary": "Good Grammatical Range and Accuracy"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Summary",
            "score": 0.0,
            "feedback_summary": "Overall summary feedback"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Feedback",
            "score": 0.0,
            "feedback_summary": "General feedback"
        }
    ]

    insert_results(submission_id, results_data)

    output = get_results(submission_id)

    expected_results = {
         "Task Response": {"score": 6.0, "feedback": "Good Task Response"},
        "Coherence and Cohesion": {"score": 7.0, "feedback": "Good Coherence and Cohesion"},
        "Lexical Resource": {"score": 6.0, "feedback": "Good Lexical Resource"},
        "Grammatical Range and Accuracy": {"score": 6.0, "feedback": "Good Grammatical Range and Accuracy"}       
    }

    assert output == expected_results, f"Expected results {expected_results} but got output {output}"

# ------------------------------------------------------------------------------------------
# TEST update_results
# ------------------------------------------------------------------------------------------

def test_update_results(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]

    session = SessionLocal()

    # Insert dummy results for this submission so there is something to update
    results_data = [
        {
            "submission_id": submission_id,
            "competency_name": "Task Response",
            "score": 6.0,
            "feedback_summary": "Good Task Response"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Coherence and Cohesion",
            "score": 7.0,
            "feedback_summary": "Good Coherence and Cohesion"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Lexical Resource",
            "score": 6.0,
            "feedback_summary": "Good Lexical Resource"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Grammatical Range and Accuracy",
            "score": 6.0,
            "feedback_summary": "Good Grammatical Range and Accuracy"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Summary",
            "score": 0.0,
            "feedback_summary": "Overall summary feedback"
        },
        {
            "submission_id": submission_id,
            "competency_name": "Overall Feedback",
            "score": 0.0,
            "feedback_summary": "General feedback"
        }
    ]

    try:
        insert_results(submission_id, results_data)

        # Prepare the new data to update
        new_data = [
            {
                "competency_name": "Task Response",
                "score": 7.0,
                "feedback_summary": "Updated feedback Task Response"
            },
            {
                "competency_name": "Lexical Resource",
                "score": 8.0,
                "feedback_summary": ""
            },
            {
                "competency_name": "Coherence and Cohesion",
                "score": None,
                "feedback_summary": "Updated feedback Coherence and Cohesion"                
            }
        ]

        updated_results = update_results(submission_id, new_data)

        for result in updated_results:

            if result["competency_name"] == "Task Response":
                assert result["score"] == 7.0
            elif result["competency_name"] == "Lexical Resource":
                assert result["score"] == 8.0
            elif result["competency_name"] == "Coherence and Cohesion":
                assert result["score"] == 7.0

    finally:
        session.execute(results.delete().where(results.c.submission_id == submission_id))
        session.commit()
        session.close()

# ------------------------------------------------------------------------------------------
# TEST create_result_logs
# ------------------------------------------------------------------------------------------

def test_create_result_logs(sample_submission):

    # Use the sample submission pytest fixture
    submission_id = sample_submission["submission_id"]
    
    sample_logs = {
        # Changed score only (feedback fields None)
        "competency_tr": {
            "competency_name": "Task Response",
            "original_score": 6.0,
            "new_score": 7.0,
            "original_feedback": None,
            "new_feedback": None
        },
        # Changed feedback only (score fields None)
        "competency_lr": {
            "competency_name": "Lexical Resource",
            "original_score": None,
            "new_score": None,
            "original_feedback": "Old lr feedback",
            "new_feedback": "Updated lr feedback"
        },
        # Changed both scores and feedback
         "competency_cc": {
            "competency_name": "Coherence and Cohesion",
            "original_score": 5.0,
            "new_score": 4.0,
            "original_feedback": "Old cc feedback",
            "new_feedback": "Updated cc feedback"
        },       
    }

    create_result_logs(submission_id, sample_logs)

    code_mapping = {
        "Task Response": "tr",
        "Lexical Resource": "lr",
        "Coherence and Cohesion": "cc",
        "Grammatical Range and Accuracy": "gr"
    }

    session = SessionLocal()

    try:
        stmt = select(results_log).where(results_log.c.submission_id == submission_id)
        entries = session.execute(stmt).fetchall()

        assert len(entries) == 3

        for entry in entries:

            code = code_mapping[entry.competency_name]
            log_data = sample_logs[f"competency_{code}"]
            
            if log_data["original_score"] is not None:
                assert float(entry.original_score) == log_data["original_score"]
                assert float(entry.corrected_score) == log_data["new_score"]
            else:
                assert entry.original_score is None
                assert entry.corrected_score is None

            if log_data["original_feedback"] is not None:
                assert entry.original_feedback == log_data["original_feedback"]
                assert entry.corrected_feedback == log_data["new_feedback"]
            else:
                assert entry.original_feedback is None
                assert entry.corrected_feedback is None

    finally:
        session.execute(results_log.delete().where(results_log.c.submission_id == submission_id))
        session.close()

