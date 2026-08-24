from tests.fixtures.builders import build_pdf


def test_parse_job_via_text_field(client):
    response = client.post("/jobs/parse", data={"text": "Backend Engineer\n\nSKILLS\nPython, FastAPI\n"})
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["title"] == "Backend Engineer"
    assert "Python" in body["skills"]


def test_parse_job_via_pdf_upload(client):
    pdf_bytes = build_pdf(["Backend Engineer\n\nSKILLS\nPython, FastAPI\n"])
    response = client.post("/jobs/parse", files={"file": ("jd.pdf", pdf_bytes, "application/pdf")})
    assert response.status_code == 200
    assert response.json()["document"]["format"] == "pdf"


def test_parse_job_requires_file_or_text(client):
    response = client.post("/jobs/parse")
    assert response.status_code == 422


def test_parse_job_rejects_unsupported_file_type(client):
    response = client.post("/jobs/parse", files={"file": ("jd.txt", b"plain text", "text/plain")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_document"
