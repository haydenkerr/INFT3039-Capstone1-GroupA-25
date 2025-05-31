# ELA Capstone 1 Project

This repository contains the source code for the ELA (English Language Assessment) Capstone 1 project, which provides an end-to-end system for automated IELTS essay grading and feedback using Retrieval-Augmented Generation (RAG) and Google Gemini LLM. The project consists of two main components:

- **ela_ui**: The frontend web user interface (HTML/JS/CSS).
- **ela_rag_docker**: The backend FastAPI application, vector database, document ingestion, and LLM integration.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Document Ingestion](#document-ingestion)
- [PDF Extraction](#pdf-extraction)
- [Batch Ingestion Scripts](#batch-ingestion-scripts)
- [Environment Variables](#environment-variables)
- [Development Notes](#development-notes)
- [License](#license)

---

## Project Structure

```
.
├── ela_ui/                  # Frontend web UI (HTML, JS, CSS)
│   ├── index.html
│   ├── script.js
│   └── ... (other assets)
└── ela_rag_docker/          # Backend FastAPI app and supporting modules
    ├── main.py              # FastAPI application
    ├── vector_db.py         # FAISS vector database wrapper
    ├── hf_embeddings.py     # Embedding model utilities
    ├── gemini_client.py     # Google Gemini LLM client
    ├── pdf_extract.py       # PDF text extraction API
    ├── batch_ingest.py      # Batch ingestion for text files
    ├── csv_batch_ingestion.py # Batch ingestion for CSV datasets
    ├── test_scripts/        # Test scripts for API endpoints
    ├── documents/           # Directory for ingestible documents
    ├── vector_store/        # FAISS index and metadata storage
    └── ... (other modules)
```

---

## Features

- **Automated IELTS Essay Grading** using Gemini LLM and RAG context.
- **Vector Search** for retrieving similar essays/examples.
- **PDF and DOCX Extraction** for student uploads.
- **Batch Ingestion** of documents and CSV datasets.
- **User Submission Tracking** and results retrieval.
- **Email Results** with PDF attachments.
- **Admin/Debug Endpoints** for document and result inspection.

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- Node.js (for frontend development, optional)
- Docker (optional, for containerized deployment)
- [FAISS](https://github.com/facebookresearch/faiss) (installed via pip)
- [Google Gemini API Key](https://ai.google.dev/)

### Backend Setup (`ela_rag_docker`)

1. **Clone the repository**  
   ```sh
   git clone https://github.com/<your-org>/INFT3039-Capstone1-GroupA-25.git
   cd ela-capstone1/ela_rag_docker
   ```

2. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables**  
   Create a `.env` file in `ela_rag_docker/` with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   smtp_user=your_smtp_user
   smtp_password=your_smtp_password
   AMPLIFY_BASE_URL=https://main.d3f79dfa9zi46n.amplifyapp.com/
   AMPLIFY_UNAME=your_amplify_username
   AMPLIFY_PWORD=your_amplify_password
   ```

4. **Run the FastAPI server**  
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8008
   ```

### Frontend Setup (`ela_ui`)

1. Open `ela_ui/index.html` in your browser, or serve the directory using a static file server.

---

## Usage

- Access the web UI via your browser (`ela_ui/index.html`).
- The backend API runs at `http://127.0.0.1:8008` by default.
- Submit essays, upload PDFs, and view results via the UI.

---

## API Endpoints

- `POST /grade` — Grade an essay (requires API key)
- `GET /results/{tracking_id}` — Retrieve grading results as HTML
- `GET /questions?task_name=...` — Get a random IELTS question
- `GET /submissions/{email}` — List all submissions for a user
- `POST /extract-pdf-text` — Extract and clean text from a base64-encoded PDF
- `POST /ingest-from-url` — Ingest a document from a public URL (requires API key)
- `GET /debug/documents` — Debug: List loaded documents
- `GET /debug/test` — Debug: Test endpoint

See `main.py` and `pdf_extract.py` for full details.

---

## Document Ingestion

- Place `.txt` files in `ela_rag_docker/documents/` and run `batch_ingest.py` to add them to the vector database.
- Use `csv_batch_ingestion.py` to ingest CSV datasets (see script for column requirements).

---

## PDF Extraction

- The `/extract-pdf-text` endpoint accepts a base64-encoded PDF and returns cleaned text.
- Used by the frontend for student PDF uploads.

---

## Batch Ingestion Scripts

- `batch_ingest.py`: Ingests all `.txt` files in the `documents/` directory.
- `csv_batch_ingestion.py`: Ingests essays and metadata from a CSV file, with duplicate detection.

---

## Environment Variables

See `.env.example` or the [Setup & Installation](#setup--installation) section for required variables.

---

## Development Notes

- **Vector Database**: Uses FAISS for fast similarity search. Embeddings are generated using `sentence-transformers/all-MiniLM-L6-v2`.
- **LLM Integration**: Uses Google Gemini via the `google-generativeai` Python SDK.
- **PDF Extraction**: Uses PyMuPDF (`fitz`) for robust PDF text extraction.
- **Frontend**: Pure HTML/JS, communicates with backend via REST API.
- **Security**: API key required for grading and ingestion endpoints. CORS is enabled for all origins by default (adjust for production).

---

## License

This project is for educational purposes. See `LICENSE` for details.

---
