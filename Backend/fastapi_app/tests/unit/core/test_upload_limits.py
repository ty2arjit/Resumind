import pytest

from app.core.errors import ValidationError
from app.core.upload_limits import MAX_UPLOAD_SIZE_BYTES, check_upload_size


def test_upload_within_limit_is_accepted():
    check_upload_size(b"x" * 1024)


def test_upload_over_limit_is_rejected():
    with pytest.raises(ValidationError):
        check_upload_size(b"x" * (MAX_UPLOAD_SIZE_BYTES + 1))
