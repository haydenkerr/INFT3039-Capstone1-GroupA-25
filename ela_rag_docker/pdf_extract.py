# pdf_extract.py

import base64
import tempfile
import fitz  # PyMuPDF
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter()

class PDFRequest(BaseModel):
    """
    Pydantic model for PDF extraction requests.
    Expects a base64-encoded PDF file string.
    """
    file: str  # Base64 encoded PDF string

@router.post("/extract-pdf-text", summary="Extract clean text from a PDF file")
def extract_pdf_text(request: PDFRequest):
    """
    Extracts and cleans text from a base64-encoded PDF file.

    Args:
        request (PDFRequest): The request containing the base64-encoded PDF.

    Returns:
        dict: A dictionary with the cleaned extracted text.
    """
    try:
        file_bytes = base64.b64decode(request.file)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(file_bytes)
            f.flush()
            doc = fitz.open(f.name)
            text_blocks = []
            for page in doc:
                text_blocks.append(page.get_text("text"))

        full_text = "\n\n".join(text_blocks)
        cleaned = clean_text(full_text)
        return { "text": cleaned }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def clean_text(text):
    """
    Cleans extracted PDF text by joining hyphenated words, removing layout artifacts,
    and ensuring bullet points are on their own lines.

    Args:
        text (str): The raw extracted text.

    Returns:
        str: The cleaned text.
    """
    lines = text.splitlines()
    fixed_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()

        # Skip empty layout lines and flush buffer if needed
        if not line:
            if buffer:
                fixed_lines.append(buffer.strip())
                buffer = ""
            continue

        # Join hyphenated words across line breaks
        if line.endswith("-"):
            buffer += line[:-1]
        else:
            buffer += line + " "

    if buffer:
        fixed_lines.append(buffer.strip())

    # Ensure bullet points are on their own lines
    fixed_with_bullets = []
    for line in fixed_lines:
        bullet_split = re.split(r"(?=\s*[•\-]\s)", line)
        fixed_with_bullets.extend([item.strip() for item in bullet_split if item.strip()])

    return "\n\n".join(fixed_with_bullets)