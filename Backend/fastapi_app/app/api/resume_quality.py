"""Standalone endpoint to exercise the Resume Quality Engine (spec Phase 8
§31). Like /resumes/parse and /jobs/parse: not wired into the production
/analyze flow, persists nothing, calls no LLM. Analyzes a resume
independently of any Job Description.
"""

from fastapi import APIRouter, File, UploadFile

from app.core.errors import UnsupportedDocumentError
from app.core.upload_limits import check_upload_size
from app.modules.resume import parse_docx_bytes, parse_pdf_bytes
from app.modules.resume_quality import ResumeQualityResult, ResumeQualityService

router = APIRouter(prefix="/resume-quality", tags=["resume-quality"])

_SUPPORTED_CONTENT_TYPES = {
    "application/pdf": parse_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx_bytes,
}

_service = ResumeQualityService()


@router.post("", response_model=ResumeQualityResult)
async def analyze_resume_quality(file: UploadFile = File(...)) -> ResumeQualityResult:
    parse_fn = _SUPPORTED_CONTENT_TYPES.get(file.content_type)
    if parse_fn is None:
        filename = (file.filename or "").lower()
        if filename.endswith(".pdf"):
            parse_fn = parse_pdf_bytes
        elif filename.endswith(".docx"):
            parse_fn = parse_docx_bytes
        else:
            raise UnsupportedDocumentError(
                f"Unsupported file type: {file.content_type or 'unknown'}. Only PDF and DOCX are supported."
            )

    file_bytes = await file.read()
    check_upload_size(file_bytes)
    resume = parse_fn(file_bytes)
    return _service.analyze(resume)
