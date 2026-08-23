from tests.fixtures.builders import build_pdf


def test_parse_resume_endpoint_returns_structured_json(client):
    pdf_bytes = build_pdf(["Jane Doe\njane@example.com\n\nSKILLS\nPython, FastAPI\n"])
    response = client.post(
        "/resumes/parse",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["contact"]["email"] == "jane@example.com"
    assert body["document"]["format"] == "pdf"
    assert any("Python" in c["items"] for c in body["skills"])


def test_parse_resume_endpoint_rejects_unsupported_file_type(client):
    response = client.post(
        "/resumes/parse",
        files={"file": ("resume.txt", b"plain text resume", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_document"
