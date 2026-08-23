from app.modules.job.metadata import extract_metadata


def test_extracts_labeled_fields():
    text = "Company: Example Corp\nLocation: Bengaluru\nEmployment Type: Full-time\n"
    metadata = extract_metadata(text, [])
    assert metadata.company == "Example Corp"
    assert metadata.location == "Bengaluru"
    assert metadata.employment_type == "Full-time"


def test_title_falls_back_to_leading_line():
    metadata = extract_metadata("Backend Software Engineer\n", ["Backend Software Engineer"])
    assert metadata.title == "Backend Software Engineer"


def test_does_not_invent_title_when_leading_line_is_not_title_like():
    metadata = extract_metadata("we are hiring for a great role\n", ["we are hiring for a great role"])
    assert metadata.title is None


def test_detects_work_mode():
    metadata = extract_metadata("This is a Remote position.", [])
    assert metadata.work_mode is not None
    assert "remote" in metadata.work_mode.lower()


def test_detects_experience_hint_when_not_explicitly_labeled():
    metadata = extract_metadata("Looking for a candidate with 2-4 years of experience.", [])
    assert metadata.experience is not None


def test_no_metadata_present():
    metadata = extract_metadata("A job description with no clear metadata fields.", [])
    assert metadata.company is None
    assert metadata.location is None
