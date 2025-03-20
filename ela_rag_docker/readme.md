# **ELA RAG Testing - Setup & Execution Guide**

## **1. Overview**
This document provides instructions for setting up the **ELA RAG Testing framework** locally, running test scripts, and setting up **Docker** for deployment.

## **2. Prerequisites**
Before proceeding, ensure the following dependencies are installed:
- Python 3.8+
- pip (Python package manager)
- Docker & Docker Compose (for containerized deployment)

## **3. Cloning the Repository**
Clone the project repository to your local machine:
```bash
git clone https://github.com/haydenkerr/INFT3039-Capstone1-GroupA-25.git
cd INFT3039-Capstone1-GroupA-25
```

## **4. Installing Python Dependencies**
Create and activate a Python virtual environment (optional but recommended):
```bash
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate on macOS/Linux
venv\Scripts\activate  # Activate on Windows
```
Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

## **5. Running the Test Scripts Locally**
Ensure FastAPI is running before executing the test scripts.

### **Start FastAPI Server**
Run the FastAPI application using Uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```
This will launch the server at `http://127.0.0.1:8001`.

### **Execute the Test Script**
Run the test script to process test cases and generate results:
```bash
python test_scripts/gemini_rag_testing.py
```
After execution, results will be saved in:
```bash
ela_rag_docker/test_scripts/gemini_rag_test_results.xlsx
```

## **6. Setting Up & Running with Docker**

### **Building the Docker Image**
Ensure Docker is installed, then build the image:
```bash
docker build -t ela-rag-api .
```

### **Running the Container**
Run the container using:
```bash
docker run -p 8001:8001 --name ela-rag-container ela-rag-api
```
This will expose the FastAPI service on `http://localhost:8001`.

### **Stopping and Removing the Container**
```bash
docker stop ela-rag-container
docker rm ela-rag-container
```

## **7. Running the Test Script Inside Docker**
If you want to run the test script inside the container, first get the container ID:
```bash
docker ps
```
Then execute the script inside the running container:
```bash
docker exec -it <container_id> python test_scripts/gemini_rag_testing.py
```

## **8. Verifying Results**
- The processed test results are stored in an **Excel file**.
- Open `gemini_rag_test_results.xlsx` to analyze predictions and feedback accuracy.

## **9. Troubleshooting**
- **No API response?** Ensure FastAPI is running.
- **Docker container not starting?** Check for conflicting ports using `docker ps`.
- **Missing dependencies?** Run `pip install -r requirements.txt` inside your virtual environment.

## **10. Contact & Support**
For any issues, contact the development team or open an issue in the GitHub repository.

