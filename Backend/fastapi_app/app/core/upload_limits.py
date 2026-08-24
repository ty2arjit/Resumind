"""Shared upload size limit (spec Phase 14 §8 — file security audit).
Every endpoint that accepts a resume/JD upload must enforce this so a
single oversized file can't exhaust server memory (`UploadFile.read()`
loads the whole body into memory with no cap otherwise).
"""

from app.core.errors import ValidationError

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def check_upload_size(file_bytes: bytes) -> None:
    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f"File is too large ({len(file_bytes) / (1024 * 1024):.1f} MB). "
            f"Maximum allowed size is {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
        )
