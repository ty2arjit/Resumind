from fastapi import APIRouter, UploadFile, File, Form
from utils.pdf_parser import extract_text_from_pdf
from services.gemini_service import analyze_resume_with_gemini

router = APIRouter()

@router.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_type: str = Form(...),
    job_domain: str = Form(...)
):
    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)
    result = analyze_resume_with_gemini(resume_text, job_type, job_domain)
    return {"analysis": result}
