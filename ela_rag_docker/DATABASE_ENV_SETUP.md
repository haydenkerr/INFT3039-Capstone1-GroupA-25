# **ELA Database Environment Configuration Guide**

## **Overview**
This document provides instructions for creating and loading a .env file for database connectivity.

## **1. Create a .env file**
In the 'ela_rag_docker' folder, create a new file named: .env

## **2. Add the database URL**
The system expects a single variable called 'DATABASE_URL' which should contain the full connection string that SQLAlchemy requires. 

Format:
DATABASE_URL=postgresql://username:password@host:port/database_name

These credentials have been shared with the team. If you need access, please reach out to Kerryn. 

## **3. Load the environment variables**
Your database.py file should contain:

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
```

If you don't have the python-dotenv package already installed, you can install it with:
pip install python-dotenv 

## **4. Don't commit your .env file**
Make sure your .env is added to your gitignore. 

## **5. Troubleshooting**
DATABASE_URL is None: Make sure the .env file is in the correct directory and named exactly .env (no extensions). 

Connection refused: Ensure your PostgreSQL server is running and accepting connections on the specified port.
