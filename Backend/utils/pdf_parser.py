import fitz  # PyMuPDF
from fastapi import UploadFile

def extract_text(file: UploadFile) -> str:
    doc = fitz.open(stream=file.file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text
