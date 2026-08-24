"""Target Profile-specific errors (spec §23-24). An unknown position/domain
must return a clear, distinct state — never a silent fallback to an
unrelated role/domain."""

from app.core.errors import ResumindError


class PositionNotSupportedError(ResumindError):
    status_code = 422
    error_code = "POSITION_NOT_SUPPORTED"


class DomainNotSupportedError(ResumindError):
    status_code = 422
    error_code = "DOMAIN_NOT_SUPPORTED"
