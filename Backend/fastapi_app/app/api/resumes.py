"""Minimal endpoint to exercise the new resume parser (spec §23).

Deliberately NOT wired into the production /analyze flow yet — this is a
standalone route for testing/validating Phase 2's output shape. It does
not persist anything (no Resume/ResumeVersion row) and does not call
Gemini.
"""

from fastapi import APIRouter, File, UploadFile

from app.core.errors import UnsupportedDocumentError
from app.core.upload_limits import check_upload_size
from app.modules.resume import StructuredResume, parse_docx_bytes, parse_pdf_bytes

router = APIRouter(prefix="/resumes", tags=["resumes"])

_SUPPORTED_CONTENT_TYPES = {
    "application/pdf": parse_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx_bytes,
}


@router.post("/parse", response_model=StructuredResume)
async def parse_resume(file: UploadFile = File(...)) -> StructuredResume:
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
    return parse_fn(file_bytes)
