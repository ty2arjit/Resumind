"""Standalone endpoint exercising the Analysis & Recommendation Engine
(spec Phase 10 §27). Like every other Phase 2-9 endpoint in this API:
not wired into the production /analyze flow, persists nothing yet (see
Phase 10's final report), calls no LLM.

Validation (spec §27): resume is always required; at least one of
job_description_text or position must be supplied; if both are supplied,
combined mode runs.
"""

import json

from fastapi import APIRouter, File, Form, UploadFile

from app.core.errors import UnsupportedDocumentError, ValidationError
from app.core.upload_limits import check_upload_size
from app.modules.analysis import Analysis, AnalysisService
from app.modules.job.parser import parse_docx_bytes as parse_jd_docx_bytes
from app.modules.job.parser import parse_pdf_bytes as parse_jd_pdf_bytes
from app.modules.job.parser import parse_text as parse_jd_text
from app.modules.resume import parse_docx_bytes, parse_pdf_bytes
from app.modules.target_profile import CustomRequirements

router = APIRouter(prefix="/analysis", tags=["analysis"])

_RESUME_CONTENT_TYPES = {
    "application/pdf": parse_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx_bytes,
}
_JD_CONTENT_TYPES = {
    "application/pdf": parse_jd_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_jd_docx_bytes,
}

_service = AnalysisService()


def _parse_resume(file: UploadFile, file_bytes: bytes):
    parse_fn = _RESUME_CONTENT_TYPES.get(file.content_type)
    if parse_fn is None:
        filename = (file.filename or "").lower()
        if filename.endswith(".pdf"):
            parse_fn = parse_pdf_bytes
        elif filename.endswith(".docx"):
            parse_fn = parse_docx_bytes
        else:
            raise UnsupportedDocumentError(
                f"Unsupported resume file type: {file.content_type or 'unknown'}. Only PDF and DOCX are supported."
            )
    return parse_fn(file_bytes)


@router.post("", response_model=Analysis)
async def run_analysis(
    resume_file: UploadFile = File(...),
    job_description_text: str | None = Form(default=None),
    position: str | None = Form(default=None),
    domain: str | None = Form(default=None),
    custom_requirements: str | None = Form(default=None),
) -> Analysis:
    if not job_description_text and not position:
        raise ValidationError("Provide either 'job_description_text' or 'position' (or both for combined mode).")

    resume_bytes = await resume_file.read()
    check_upload_size(resume_bytes)
    resume = _parse_resume(resume_file, resume_bytes)

    parsed_custom_requirements = CustomRequirements()
    if custom_requirements:
        try:
            parsed_custom_requirements = CustomRequirements(**json.loads(custom_requirements))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid custom_requirements JSON: {exc}") from exc

    if job_description_text and position:
        jd = parse_jd_text(job_description_text)
        return _service.run_combined_analysis(jd, resume, position, domain, parsed_custom_requirements)

    if job_description_text:
        jd = parse_jd_text(job_description_text)
        return _service.run_jd_analysis(jd, resume)

    return _service.run_target_analysis(position, resume, domain, parsed_custom_requirements)
