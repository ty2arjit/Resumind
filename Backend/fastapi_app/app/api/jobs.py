"""Minimal endpoint to exercise the new JD parser (spec §23).

Accepts either a PDF/DOCX upload OR a plain-text field — not both.
Standalone, like /resumes/parse: not wired into the production /analyze
flow, persists nothing, calls no LLM.
"""

from fastapi import APIRouter, File, Form, UploadFile

from app.core.errors import UnsupportedDocumentError, ValidationError
from app.core.upload_limits import check_upload_size
from app.modules.job import StructuredJD, parse_docx_bytes, parse_pdf_bytes, parse_text

router = APIRouter(prefix="/jobs", tags=["jobs"])

_SUPPORTED_CONTENT_TYPES = {
    "application/pdf": parse_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx_bytes,
}


@router.post("/parse", response_model=StructuredJD)
async def parse_job_description(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
) -> StructuredJD:
    if file is None and not text:
        raise ValidationError("Provide either a file upload or a 'text' field.")

    if file is not None:
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

    return parse_text(text)
