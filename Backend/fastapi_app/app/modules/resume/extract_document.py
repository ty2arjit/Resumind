"""Document ingestion: PDF/DOCX -> raw text with page boundaries preserved.

PDF extraction reuses PyMuPDF (already a project dependency —
Backend/utils/pdf_parser.py), but reads text via layout-aware `blocks`
instead of the old plain `get_text()` concatenation, to reduce column
interleaving on multi-column resumes (spec §17). This is a heuristic
column-bucketing, not a real layout engine — good enough to stop two
columns reading as one interleaved mess, not a substitute for OCR/CV.
"""

import io

import docx
import fitz  # PyMuPDF

from app.modules.resume.schemas import DocumentFormat, ExtractionStatus

MIN_CHARS_PER_PAGE_OK = 40
MIN_TOTAL_CHARS_OK = 100


class DocumentExtraction:
    def __init__(
        self,
        format: DocumentFormat,
        page_count: int | None,
        pages: list[str],
        raw_text: str,
        extraction_status: ExtractionStatus,
    ):
        self.format = format
        self.page_count = page_count
        self.pages = pages
        self.raw_text = raw_text
        self.extraction_status = extraction_status


def _bucket_blocks_by_column(blocks: list[tuple], page_width: float) -> list[tuple]:
    """Reorder text blocks so a left column is read fully before a right
    column, instead of interleaving by raw y-position.

    `blocks` entries are PyMuPDF's (x0, y0, x1, y1, text, block_no, block_type).
    Heuristic: bucket each block into a column by which half of the page
    its left edge (x0) falls in, then sort column-major (column, y0). For a
    genuine single-column resume this reduces to a normal top-to-bottom
    sort since every block lands in the same bucket.
    """
    midpoint = page_width / 2

    def column_of(block) -> int:
        x0 = block[0]
        return 0 if x0 < midpoint else 1

    return sorted(blocks, key=lambda b: (column_of(b), round(b[1], 1), b[0]))


def extract_pdf(file_bytes: bytes) -> DocumentExtraction:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[str] = []

    for page in doc:
        blocks = [b for b in page.get_text("blocks") if b[6] == 0]  # text blocks only
        ordered = _bucket_blocks_by_column(blocks, page.rect.width)
        page_text = "\n".join(b[4].strip("\n") for b in ordered if b[4].strip())
        pages.append(page_text)

    page_count = len(pages)
    raw_text = "\n\f\n".join(pages)  # form-feed marks a page boundary in raw_text
    status = _classify_extraction(raw_text, page_count)
    return DocumentExtraction(DocumentFormat.PDF, page_count, pages, raw_text, status)


def extract_docx(file_bytes: bytes) -> DocumentExtraction:
    document = docx.Document(io.BytesIO(file_bytes))
    lines = [p.text for p in document.paragraphs]

    # DOCX has no fixed "page" concept at the paragraph level; treated as a
    # single logical page so downstream code has one code path for both
    # formats.
    raw_text = "\n".join(lines)
    status = _classify_extraction(raw_text, page_count=1)
    return DocumentExtraction(DocumentFormat.DOCX, None, [raw_text], raw_text, status)


def _classify_extraction(raw_text: str, page_count: int) -> ExtractionStatus:
    stripped = raw_text.strip()
    if not stripped:
        return ExtractionStatus.EMPTY
    avg_chars_per_page = len(stripped) / max(page_count, 1)
    if len(stripped) < MIN_TOTAL_CHARS_OK or avg_chars_per_page < MIN_CHARS_PER_PAGE_OK:
        return ExtractionStatus.LOW_TEXT
    return ExtractionStatus.OK
