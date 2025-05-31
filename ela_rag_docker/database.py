"""
database.py

This module handles all database connections and operations using SQLAlchemy

It contains:
- Session creation and management
- Table definitions
- Functions for interacting with the database

This module is used by: 
- main.py (for the main submission and grading workflow)
- teacher_updates.py (for database updates based on teacher validation feedback)

"""

import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, DateTime, Boolean, Text, insert, select, update, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


# Load environment variables from .env file

# os.chdir("./ela_rag_docker")
# os.getcwd()
load_dotenv()

# Database connection string from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Define metadata
metadata = MetaData()

# ----------------------------------------------------------------------------------------------
# Define database tables
# ----------------------------------------------------------------------------------------------

tasks = Table(
    "tasks", metadata,
    Column("task_id", Integer, primary_key=True),
    Column("task_name", Text, nullable=False),
    Column("min_word_count", Integer, nullable=False),
    Column("task_instruction", Text, nullable=False)
)

users = Table(
    "users", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)

questions = Table(
    "questions", metadata,
    Column("question_id", Integer, primary_key=True),
    Column("task_id", Integer, nullable=False),
    Column("question_text", Text, nullable=False),
    Column("iscustom", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.utcnow)
)

submissions = Table(
    "submissions", metadata,
    Column("submission_id", Integer, primary_key=True),
    Column("question_id", Integer, nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("task_id", Integer, nullable=False),
    Column("submission_group", Integer, nullable=False),
    Column("submission_timestamp", DateTime, default=datetime.utcnow),
    Column("essay_response", Text, nullable=False),
    Column("overall_score", Float, nullable=True),
    Column("validated", Boolean, nullable=True)
)

results = Table(
    "results", metadata,
    Column("id", Integer, primary_key=True),
    Column("submission_id", Integer, ForeignKey("submissions.submission_id", ondelete="CASCADE")),
    Column("competency_name", String(255), nullable=False),
    Column("score", DECIMAL(3, 2), nullable=False),
    Column("feedback_summary", Text, nullable=False)
)

submissions_log = Table(
    "submissions_log", metadata,
    Column("log_id", Integer, primary_key=True),
    Column("submission_id", Integer, ForeignKey("submissions.submission_id", ondelete="CASCADE"), nullable=True),
    Column("log_type", String(50), nullable=True),
    Column("log_message", Text, nullable=True),
    Column("log_timestamp", DateTime(timezone=True), default=datetime.utcnow),
    Column("tracking_id", String(36), nullable=False)
)

vector_db_log = Table(
    "vector_db_log", metadata,
    Column("vector_db_log_id", Integer, primary_key=True, autoincrement=True),
    Column("submission_id", Integer, nullable=False),
    Column("index_position", Integer, nullable=False),
    Column("metadata", Text, nullable=False),
    Column("distance", Float),
    Column("created_at", DateTime, default=datetime.utcnow)
)

results_log = Table(
    "results_log", metadata,
    Column("results_log_id", Integer, primary_key=True, autoincrement=True),
    Column("submission_id", Integer, nullable=False),
    Column("competency_name", Text, nullable = False),
    Column("original_score", DECIMAL(3, 2)),
    Column("corrected_score", DECIMAL(3, 2)),
    Column("original_feedback", Text),
    Column("corrected_feedback", Text),
    Column("updated_by", Text),
    Column("timestamp", DateTime, default=datetime.utcnow)
)

# ----------------------------------------------------------------------------------------------
# Define database functions
# ----------------------------------------------------------------------------------------------

def create_vector_db_log(submission_id: int, vector_db_logs: list):
    """
    Insert new log entries to the vector_db_log table for each submission.

    Parameters:
        submission_id (int): The submission ID to log against
        vector_db_logs (list): A list of examples from the vector_db containing:
         - Index Position
         - Metadata
         - Distance
    """

    session = SessionLocal()

    try:
        for log_entry in vector_db_logs:

            # Extract the required data
            index_position = log_entry['index_position']
            metadata = log_entry['metadata']
            distance = log_entry['distance']

            # Prepare the statement
            stmt = insert(vector_db_log).values(
                submission_id = submission_id,
                index_position = index_position,
                metadata = metadata,
                distance = distance,
                created_at = datetime.utcnow()
            )

            session.execute(stmt)
        
        session.commit()

    except Exception as e:
        session.rollback()
        print("Error in create_vector_db_log:", e)
        raise

    finally:
        session.close()


def create_log(tracking_id: str, log_type: str, log_message: str, submission_id: int = None):
    """
    Insert new log entries to the submissions_log table.

    Parameters:
        tracking_id (str): the uuid for each main submission workflow
        log_type (str): the category of log
        log_message (str): the detailed log message
        submission_id (int): the submission ID to log against

    """

    session = SessionLocal()

    try:
        # Prepare the statement
        stmt = insert(submissions_log).values(
            tracking_id=tracking_id,
            submission_id=submission_id,
            log_type=log_type,
            log_message=log_message,
            log_timestamp=datetime.utcnow()
        )
        results = session.execute(stmt)
        session.commit()

    except Exception as e:
        session.rollback()
        print("Error in create_log:", e)
        raise

    finally:
        session.close()


def get_or_create_user(email: str) -> int:
    """
    Insert new user to users table if they don't already exist.

    Parameters:
        email (str): the user's given email address

    Returns:
        user_id (int): unique ID of the newly created user, or existing user id if already exists

    """

    session = SessionLocal()

    try:
        # Retrieve and return existing user id if email already exists
        stmt = select(users).where(users.c.email == email)
        result = session.execute(stmt).fetchone()
        if result:
            return result[0] 
        
        # Create new record for new user email and return new user id
        stmt = insert(users).values(email=email, created_at=datetime.utcnow()).returning(users.c.user_id)
        result = session.execute(stmt).fetchone()
        session.commit()
        return result[0] 
    
    except Exception as e:
        session.rollback()
        print("Error in get_or_create_user:", e)
        raise

    finally:
        session.close()


def get_task_id(task_name: str) -> int:
    """
    Retrieve the unique task_id for the given task name.

    Parameters:
        task_name (str): the name of the IELTS task

    Returns:
        task_id (int): unique ID of the relevant task

    """

    session = SessionLocal()

    try:
        # Prepare and execute the statement
        stmt = select(tasks.c.task_id).where(tasks.c.task_name == task_name)
        result = session.execute(stmt).fetchone()

        if result:
            return result[0]
        else:
            raise ValueError(f"Task name '{task_name}' not found in database.")
        
    except Exception as e:
        print("Error in get_task_id:", e)
        raise

    finally:
        session.close()


def get_or_create_question(question_text: str, task_id: int) -> int:
    """
    Insert new question to the questions table if it doesn't already exist.

    Parameters:
        question_text (str): the IELTS task question
        task_id (int): the unique id of the IELTS task the question relates to

    Returns:
        question_id (int): unique ID of the newly created question, or existing question if already exists

    """

    session = SessionLocal()

    try:
        # Retrieve and return the existing question id if question already exists
        stmt = select(questions.c.question_id).where(questions.c.question_text == question_text)
        result = session.execute(stmt).fetchone()
        if result:
            return result[0]
        
        # Create new record for new question and return new question id
        stmt = insert(questions).values(
            question_text=question_text,
            task_id=task_id,
            iscustom=True,
            created_at=datetime.utcnow()
        ).returning(questions.c.question_id)

        result = session.execute(stmt).fetchone()
        session.commit()
        return result[0]
    
    except Exception as e:
        session.rollback()
        print("Error in get_or_create_question:", e)
        raise

    finally:
        session.close()


def insert_submission(user_id: int, task_id: int, question_id: int, submission_group: int, essay_response: str) -> int:
    """
    Insert new record to the submissions table for each student submission.

    Parameters:
        user_id (int): the unique ID of the submitting user
        task_id (int): the unique id of the IELTS task the submission is for
        question_id (int): the unique id of the question used in the submission
        submission_group (int): the submission group this task submission relates to
        essay_response (str): the full essay response submitted by the user

    Returns:
        submission_id (int): the unique identifier for the submission
    """

    session = SessionLocal()

    try:
        # Prepare the statement
        stmt = insert(submissions).values(
            user_id=user_id,
            task_id=task_id,
            question_id=question_id,
            submission_group=submission_group,
            essay_response=essay_response,
            submission_timestamp=datetime.utcnow()
        ).returning(submissions.c.submission_id)

        result = session.execute(stmt).fetchone()
        session.commit()
        return result[0]
    
    except Exception as e:
        session.rollback()
        print("Error in insert_submission:", e)
        raise

    finally:
        session.close()


def calculate_overall_score(results_data: list) -> float:
    """
    Calculate the overall task score from the given competency scores and apply IELTS specific rounding rules.

    Parameters:
        results_data (list): a list of results with each item containing:
         - submission_id
         - competency_name
         - score
         - feedback_summary

    Returns:
        overall_score (float): the rounded, overall task score 
    """

    # Only average the 4 IELTS scoring criteria
    core_keys = {
        "Task Response",
        "Coherence and Cohesion",
        "Lexical Resource",
        "Grammatical Range and Accuracy"
    }

    core_scores = [
        item["score"]
        for item in results_data
        if item["competency_name"] in core_keys and item["score"] is not None
    ]

    if len(core_scores) != 4:
        raise ValueError("Expected scores for the 4 IELTS core competencies")

    average = sum(core_scores) / 4

    # IELTS-specific rounding
    if average % 1 == 0.25:
        overall_score = round(average + 0.25, 1)
    elif average % 1 == 0.75:
        overall_score = round(average + 0.25, 1)
    else:
        overall_score = round(average * 2) / 2

    return overall_score


def insert_results(submission_id: int, results_data: list) -> float:
    """
    Insert the initial, model generated results to the results table for a submission. Also call the
    calculate_overall_score function and update the submissions table with the result.

    Parameters:
        submission_id (int): the unique id of the submission
        results_data (list): a list of results with each item containing:
         - submission_id
         - competency_name
         - score
         - feedback_summary

    Returns:
        overall_score (float): the rounded, overall task score 
    """

    session = SessionLocal()

    try:
        # Prepare and execute the statement to insert results
        stmt = insert(results)
        session.execute(stmt, results_data)

        # Call the calculate overall score function and store result
        overall_score = calculate_overall_score(results_data)

        # Update the submissions table with the calculated overall score
        session.execute(
            update(submissions)
            .where(submissions.c.submission_id == submission_id)
            .values(overall_score = overall_score)
        )

        session.commit()
        return overall_score
    
    except Exception as e:
        session.rollback()
        print("Error in insert_results:", e)
        raise

    finally:
        session.close()


def prepare_results_from_grading_data(submission_id: int, grading_result: dict) -> list:
    """
    Format the model response to prepare for insertion into the results database table.

    Parameters:
        submission_id (int): the unique id of the submission
        gradint_result (dict): a dictionary containing band scores, feedback text and a formatted score table

    Returns:
        results_data (list): a list of results with each item containing:
         - submission_id
         - competency_name
         - score
         - feedback_summary
    """

    competency_map = {
        "task_response": "Task Response",
        "coherence_cohesion": "Coherence and Cohesion",
        "lexical_resource": "Lexical Resource",
        "grammatical_range": "Grammatical Range and Accuracy",
        "overall_summary": "Overall Summary",
        "general_feedback": "Overall Feedback"
    }

    results_data = []

    for key, label in competency_map.items():
        score = grading_result["bands"].get(key)
        feedback = grading_result["feedback"].get(key, "")

        # Only skip if both score and feedback are missing (important for non-scored ones)
        if score is None and not feedback.strip():
            continue

        results_data.append({
            "submission_id": submission_id,
            "competency_name": label,
            "score": score if score is not None else 0.0,
            "feedback_summary": feedback
        })

    return results_data


def update_validated(submission_id: int, valid: bool):
    """
    Update the validated status of a submission from teacher feedback.

    Parameters:
        submission_id (int): the unique id of the submission
        valid (bool): TRUE if model response was valid, FALSE if teacher made changes
    """

    session = SessionLocal()

    try:
        # Prepare the statement
        stmt = update(submissions).where(submissions.c.submission_id == submission_id).values(validated = valid)

        session.execute(stmt)
        session.commit()

    except Exception as e:
        session.rollback()
        print("Error in update_validated:", e)
        raise

    finally:
        session.close()


def get_validated_value(submission_id: int) -> bool:
    """
    Retrieve the current validated value from the submissions table for the given submission, to determine
    if a submission has already been validated.

    Parameters:
        submission_id (int): the unique id of the submission

    Returns:
        validated_value (bool): existing value from the validated field of submissions table
    """

    session = SessionLocal()

    try:
        # Prepare the statement
        stmt = select(submissions.c.validated).where(submissions.c.submission_id == submission_id)

        validated_value = session.execute(stmt).scalar()
        return validated_value

    except Exception as e:
        session.rollback()
        print("Error in get_validated_value:", e)
        raise

    finally:
        session.close()


def create_result_logs(submission_id: int, results_logs: dict):
    """
    Insert new log entries to the results_log table to track each result (score or feedback)
    that has been changed based on teacher feedback.

    Parameters:
        submission_id (int): the unique id of the submission
        results_logs (dict): a dictionary containing old and new scores and feedback
    """

    session = SessionLocal()

    try:
        for key, log in results_logs.items():
            try:
                # Extract the competency name, original & new score, original & new feedback
                competency = log["competency_name"]
                original_score = log["original_score"]
                new_score = log["new_score"]
                original_feedback = log["original_feedback"]
                new_feedback = log["new_feedback"]

                stmt = insert(results_log).values(
                    submission_id=submission_id,
                    competency_name = competency,
                    original_score = original_score,
                    corrected_score = new_score,
                    original_feedback = original_feedback,
                    corrected_feedback = new_feedback,
                    updated_by = "Teacher validation automated process",
                    timestamp=datetime.utcnow())

                session.execute(stmt)

            except Exception as e:
                print(f"Error inserting results log entry: {e}")

        session.commit()

    except Exception as e:
        session.rollback()
        print("Error in create_result_logs:", e)
        raise

    finally:
        session.close()


def get_results(submission_id: int) -> dict:
    """
    Retrieve existing results data from the results table for a given submission.

    Parameters:
        submission_id (int): the unique id of the submission

    Returns:
        original_results (dict): a dictionary containing scores and feedback for the 4 IELTS competencies
    """

    session = SessionLocal()

    try:
        # Prepare the statement
        stmt = select(
            results.c.competency_name, 
            results.c.score,
            results.c.feedback_summary).where(results.c.submission_id == submission_id)

        # Execute and store all retrieved results
        retrieved_results = session.execute(stmt).fetchall()

        # Only want the 4 IELTS competencies
        skip_names = {"Overall Summary", "Overall Feedback"}

        original_results = {}

        for row in retrieved_results:

            # Don't action for overall summary or overall feedback
            if row.competency_name in skip_names:
                continue

            original_results[row.competency_name] = {
                "score": float(row.score),
                "feedback": row.feedback_summary
            }

        return original_results

    except Exception as e:
        session.rollback()
        print("Error in get_results:", e)
        raise

    finally:
        session.close()


def update_results(submission_id: int, new_data: list) -> list:
    """
    Update the results table for a given submission with new scores and/or feedback.

    Parameters:
        submission_id (int): the unique id of the submission
        new_data (list): a list of dictionaries containing:
        - competency name
        - score
        - feedback summary

    Returns:
        results_data (list): a list of the latest results records for the given submission containing:
        - competency name
        - score
    """

    session = SessionLocal()

    try:
        # For each competency, check if scores and/or feedback need to be updated
        for entry in new_data:

            updates = {}

            if entry["score"] is not None:
                updates["score"] = entry["score"]
            
            if entry["feedback_summary"] is not None:
                updates["feedback_summary"] = entry["feedback_summary"]

            # Define statement to update results table only with new data
            if updates:
                stmt = (
                    update(results)
                    .where(
                        results.c.submission_id == submission_id, 
                        results.c.competency_name == entry["competency_name"]
                    )
                    .values(
                        score = updates.get("score", results.c.score), 
                        feedback_summary = updates.get("feedback_summary", results.c.feedback_summary)
                    )
                )   

            session.execute(stmt) 

        session.commit()

        # Fetch the full list of competency scores from the results table for the submission
        stmt = select(
            results.c.competency_name,
            results.c.score
        ).where(results.c.submission_id == submission_id)

        updated_results = session.execute(stmt).fetchall()

        results_data = []

        for row in updated_results:
            results_data.append({
                "competency_name": row.competency_name,
                "score": float(row.score) 
            })

        return results_data

    except Exception as e:
        session.rollback()
        print("Error in update_results:", e)
        raise

    finally:
        session.close()


def update_overall_score(submission_id: int, new_overall_score: float):
    """
    Update the overall_score in the submissions table for the given submission.

    Parameters:
        submission_id (int): the unique id of the submission
        new_overall_score (float): the overall score to update in the submissions table
    """

    session = SessionLocal()
    
    try:
        # Prepare and execute the statement
        stmt = update(submissions).where(
            submissions.c.submission_id == submission_id).values(overall_score = new_overall_score)  
        
        session.execute(stmt) 
        session.commit()

    except Exception as e:
        session.rollback()
        print("Error in update_overall_score:", e)
        raise

    finally:
        session.close()
