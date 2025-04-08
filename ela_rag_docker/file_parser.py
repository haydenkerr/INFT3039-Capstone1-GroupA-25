from docx import Document as DocxDocument
import pdfplumber
import pandas as pd
from bs4 import BeautifulSoup

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file_path.endswith(".docx"):
        return "\n".join([para.text for para in DocxDocument(file_path).paragraphs])
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
        return df.to_string()
    elif file_path.endswith(".html"):
        with open(file_path, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "html.parser").get_text()
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format")
