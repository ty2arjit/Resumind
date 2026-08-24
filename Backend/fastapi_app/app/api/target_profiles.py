"""Standalone endpoints exercising the Target Profile Intelligence Engine
(spec Phase 9 §27-28). Like /resumes/parse, /jobs/parse, and
/resume-quality: not wired into the production /analyze flow, persists
nothing yet (Phase 1's `target_profiles` table exists for this, but
Postgres/Neon is unreachable from this environment — see Phase 9's final
report), and calls no LLM.
"""

import json

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from app.core.errors import UnsupportedDocumentError, ValidationError
from app.core.upload_limits import check_upload_size
from app.modules.resume import parse_docx_bytes, parse_pdf_bytes
from app.modules.target_profile import (
    CustomRequirements,
    EffectiveTargetProfile,
    TargetAnalysisResult,
    TargetProfileRegistry,
    TargetProfileService,
)

router = APIRouter(prefix="/target-profiles", tags=["target-profiles"])

_SUPPORTED_CONTENT_TYPES = {
    "application/pdf": parse_pdf_bytes,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx_bytes,
}

_registry = TargetProfileRegistry()
_service = TargetProfileService(registry=_registry)


class PreviewRequest(BaseModel):
    position: str
    domain: str | None = None
    custom_requirements: CustomRequirements = CustomRequirements()


@router.get("/positions")
async def list_positions() -> list[str]:
    return _registry.list_positions()


@router.get("/domains")
async def list_domains() -> list[str]:
    return _registry.list_domains()


@router.post("/preview", response_model=EffectiveTargetProfile)
async def preview_target_profile(body: PreviewRequest) -> EffectiveTargetProfile:
    return _registry.build_effective_profile(body.position, body.domain, body.custom_requirements)


@router.post("/analyze", response_model=TargetAnalysisResult)
async def analyze_target_fit(
    file: UploadFile = File(...),
    position: str = Form(...),
    domain: str | None = Form(default=None),
    custom_requirements: str | None = Form(default=None),
) -> TargetAnalysisResult:
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

    parsed_custom_requirements = CustomRequirements()
    if custom_requirements:
        try:
            parsed_custom_requirements = CustomRequirements(**json.loads(custom_requirements))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid custom_requirements JSON: {exc}") from exc

    file_bytes = await file.read()
    check_upload_size(file_bytes)
    resume = parse_fn(file_bytes)
    return _service.analyze(position, resume, domain, parsed_custom_requirements)
