import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime, Boolean, Text, insert, select, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker


# Load environment variables from .env file
load_dotenv()

# Database connection string from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Define metadata
metadata = MetaData()

# Define database tables
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
    Column("essay_response", Text, nullable=False)
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

# Function to add a log to the submissions_log table
def create_log(tracking_id: str, log_type: str, log_message: str, submission_id: int = None):
    session = SessionLocal()
    try:
        stmt = insert(submissions_log).values(
            tracking_id=tracking_id,
            submission_id=submission_id,
            log_type=log_type,
            log_message=log_message,
            log_timestamp=datetime.utcnow()
        )
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error in create_log:", e)
        raise
    finally:
        session.close()

# Function to get or insert user
def get_or_create_user(email: str):
    session = SessionLocal()
    try:
        stmt = select(users).where(users.c.email == email)
        result = session.execute(stmt).fetchone()
        if result:
            return result[0]  # return user_id
        stmt = insert(users).values(email=email, created_at=datetime.utcnow()).returning(users.c.user_id)
        result = session.execute(stmt).fetchone()
        session.commit()
        return result[0]  # return new user_id
    except Exception as e:
        session.rollback()
        print("Error in get_or_create_user:", e)
        raise
    finally:
        session.close()


# Function to get task_id by task_name
def get_task_id(task_name: str):
    session = SessionLocal()
    try:
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


# Function to get or insert question
def get_or_create_question(question_text: str, task_id: int):
    session = SessionLocal()
    try:
        stmt = select(questions.c.question_id).where(questions.c.question_text == question_text)
        result = session.execute(stmt).fetchone()
        if result:
            return result[0]
        stmt = insert(questions).values(
            question_text=question_text,
            task_id=task_id,
            iscustom=None,
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


# Function to insert submission
def insert_submission(user_id: int, task_id: int, question_id: int, submission_group: int, essay_response: str):
    session = SessionLocal()
    try:
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

# Function to insert results
def insert_results(submission_id: int, results_data: list):
    session = SessionLocal()
    try:
        stmt = insert(results)
        session.execute(stmt, results_data)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error in insert_results:", e)
        raise
    finally:
        session.close()

# Function to convert grading_result dict to results_data format
def prepare_results_from_grading_data(submission_id: int, grading_result: dict) -> list:
    competency_map = {
        "task_response": "Task Response",
        "coherence_cohesion": "Coherence and Cohesion",
        "lexical_resource": "Lexical Resource",
        "grammatical_range": "Grammatical Range and Accuracy"
    }

    results_data = []
    for key, label in competency_map.items():
        score = grading_result["bands"].get(key)
        feedback = grading_result["feedback"].get(key, "")
        results_data.append({
            "submission_id": submission_id,
            "competency_name": label,
            "score": score if score is not None else 0.0,
            "feedback_summary": feedback
        })

    return results_data
