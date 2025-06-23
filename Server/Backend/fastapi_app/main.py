from fastapi import FastAPI, Request, UploadFile, File, Form
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gemini_service import generate_resume_analysis
from utils.pdf_parser import extract_text_from_pdf
from AI_Result_Styling import StyleResult

app = FastAPI()

# Allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or specify ["http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeData(BaseModel):
    resume_text: str
    position_type: str
    field: str

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    position_type: str= Form(...),
    field: str = Form(...)
):
    #Read and extract text from uploaded file
    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)

    # Generate analysis using your existing function

    analysis = generate_resume_analysis(
        resume_text = resume_text,
        position_type = position_type,
        field=field
    )

    finalResult = StyleResult(analysis)

    return {"result": analysis}

