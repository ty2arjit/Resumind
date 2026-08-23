"""Contact information extraction (spec §5).

Deterministic pattern matching only. Name extraction is conservative: if
the top of the resume doesn't clearly look like a name line, we leave it
None rather than guess — a wrong invented name is worse than a missing
one.
"""

import re

from app.modules.resume.schemas import ContactInfo

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{3,4}\b")

# Requires either an explicit scheme/www, or a lowercase TLD from a known
# allowlist — a bare "[word].[word]" pattern (e.g. "B.Tech", "M.Sc") would
# otherwise match too, since it's structurally identical to a domain.
_KNOWN_TLDS = "com|org|net|io|dev|co|in|edu|ai|app|info|gov|us|uk|ca|de|xyz|so|ly"
_URL_RE = re.compile(
    rf"(?:https?://[^\s]+)|(?:www\.[\w-]+(?:\.[\w-]+)*\.(?:{_KNOWN_TLDS})(?:/[^\s]*)?)"
    rf"|(?:[\w-]+(?:\.[\w-]+)*\.(?:{_KNOWN_TLDS})(?:/[^\s]*)?)"
)

_LINKEDIN_DOMAIN = "linkedin.com"
_GITHUB_DOMAIN = "github.com"

_NAME_LINE_RE = re.compile(r"^[A-Za-z][A-Za-z.'\-]*(?:\s+[A-Za-z][A-Za-z.'\-]*){0,3}$")
_NAME_BLOCKLIST_WORDS = {"resume", "curriculum", "vitae", "cv", "portfolio"}


def _looks_like_name(line: str) -> bool:
    stripped = line.strip()
    words = stripped.split()
    if not (2 <= len(words) <= 4):
        return False
    if not _NAME_LINE_RE.match(stripped):
        return False
    # Real name lines are Title Case; an ordinary sentence ("Just some
    # unrelated text.") would otherwise also satisfy the length/character
    # checks above.
    if not all(word[0].isupper() for word in words):
        return False
    if any(word.lower().strip(".") in _NAME_BLOCKLIST_WORDS for word in words):
        return False
    return True


def _classify_url(url: str) -> str:
    lower = url.lower()
    if _LINKEDIN_DOMAIN in lower:
        return "linkedin"
    if _GITHUB_DOMAIN in lower:
        return "github"
    return "website"


def extract_contact(full_text: str, leading_lines: list[str]) -> ContactInfo:
    contact = ContactInfo()

    email_match = _EMAIL_RE.search(full_text)
    if email_match:
        contact.email = email_match.group(0)

    # Blank out the email span before URL scanning — otherwise the local
    # part of "john.doe@example.com" (i.e. "john.doe") matches the URL
    # pattern on its own, since it's a dot-separated word sequence too.
    text_for_urls = full_text
    if email_match:
        start, end = email_match.span()
        text_for_urls = full_text[:start] + " " * (end - start) + full_text[end:]

    for match in _URL_RE.finditer(text_for_urls):
        url = match.group(0)
        kind = _classify_url(url)
        if kind == "linkedin" and not contact.linkedin:
            contact.linkedin = url
        elif kind == "github" and not contact.github:
            contact.github = url
        elif kind == "website" and not contact.website:
            contact.website = url

    for match in _PHONE_RE.finditer(full_text):
        digits = re.sub(r"\D", "", match.group(0))
        if 7 <= len(digits) <= 13:
            contact.phone = match.group(0).strip()
            break

    for line in leading_lines[:3]:
        candidate = line.strip()
        if _EMAIL_RE.search(candidate) or _URL_RE.search(candidate) or _PHONE_RE.search(candidate):
            continue
        if _looks_like_name(candidate):
            contact.name = candidate
            break

    return contact
