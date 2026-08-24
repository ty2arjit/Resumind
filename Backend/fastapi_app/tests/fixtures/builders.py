"""Builds real PDF/DOCX bytes for parser tests, so tests exercise the
actual PyMuPDF/python-docx extraction path rather than only the
string-processing stages."""

import docx
import fitz


def build_pdf(pages: list[str], font_size: int = 10) -> bytes:
    """One page of plain single-column text per entry in `pages`."""
    doc = fitz.open()
    for page_text in pages:
        page = doc.new_page()
        page.insert_text((50, 50), page_text, fontsize=font_size)
    return doc.tobytes()


def build_two_column_pdf(left_lines: list[str], right_lines: list[str]) -> bytes:
    """A crude two-column layout: left_lines placed at low x, right_lines
    at high x, each block written as one text insertion so PyMuPDF creates
    two separate blocks at different x-positions."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((40, 50), "\n".join(left_lines), fontsize=10)
    page.insert_text((320, 50), "\n".join(right_lines), fontsize=10)
    return doc.tobytes()


def build_empty_pdf() -> bytes:
    doc = fitz.open()
    doc.new_page()
    return doc.tobytes()


def build_docx(lines: list[str]) -> bytes:
    import io

    document = docx.Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
