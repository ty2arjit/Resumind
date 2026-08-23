from app.modules.resume.contact import extract_contact


def test_extracts_email():
    contact = extract_contact("Jane Doe\njane.doe@example.com", ["Jane Doe"])
    assert contact.email == "jane.doe@example.com"


def test_extracts_linkedin_and_github():
    text = "jane@example.com | linkedin.com/in/janedoe | github.com/janedoe"
    contact = extract_contact(text, [])
    assert contact.linkedin == "linkedin.com/in/janedoe"
    assert contact.github == "github.com/janedoe"


def test_extracts_phone_number():
    contact = extract_contact("Contact: +1 555-123-4567", [])
    assert contact.phone is not None
    assert "555" in contact.phone


def test_does_not_mistake_email_local_part_for_a_website():
    """Regression: 'john.doe@example.com' must not also produce
    website='john.doe' from the URL pattern matching the email's local
    part."""
    contact = extract_contact("john.doe@example.com", [])
    assert contact.website is None


def test_does_not_mistake_degree_abbreviation_for_a_url():
    """Regression: 'B.Tech' structurally looks like a bare domain
    ('word.word') and must not be picked up as a website."""
    contact = extract_contact("B.Tech in Computer Science", [])
    assert contact.website is None


def test_extracts_name_from_leading_line():
    contact = extract_contact("Jane Doe\njane@example.com", ["Jane Doe"])
    assert contact.name == "Jane Doe"


def test_does_not_invent_a_name_when_uncertain():
    contact = extract_contact("jane@example.com", ["jane@example.com"])
    assert contact.name is None


def test_no_contact_info_present():
    contact = extract_contact("Just some unrelated text.", ["Just some unrelated text."])
    assert contact.email is None
    assert contact.phone is None
    assert contact.linkedin is None
