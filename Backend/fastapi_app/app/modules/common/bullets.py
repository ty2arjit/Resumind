"""Bullet-line detection shared by the resume and JD parsers."""

import re

_BULLET_PREFIX_RE = re.compile(r"^[•‣◦⁃∙\-*–—]\s*")


def is_bullet(line: str) -> bool:
    return bool(_BULLET_PREFIX_RE.match(line.strip()))


def strip_bullet(line: str) -> str:
    return _BULLET_PREFIX_RE.sub("", line.strip()).strip()
