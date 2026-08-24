"""Resume parsing pipeline: text extraction -> section detection -> entity
extraction -> structured resume (spec Phase 2).
"""

from app.modules.resume.parser import parse_docx_bytes, parse_pdf_bytes
from app.modules.resume.schemas import StructuredResume

__all__ = ["parse_pdf_bytes", "parse_docx_bytes", "StructuredResume"]
