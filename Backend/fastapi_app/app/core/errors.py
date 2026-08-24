"""Centralized error handling.

Domain code should raise one of these instead of a bare Exception or an
inline HTTPException, so every module reports errors the same shape and
API responses stay consistent as new routers are added in later phases.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ResumindError(Exception):
    """Base class for all application-raised errors."""

    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(ResumindError):
    status_code = 404
    error_code = "not_found"


class ValidationError(ResumindError):
    status_code = 422
    error_code = "validation_error"


class UnauthorizedError(ResumindError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(ResumindError):
    status_code = 403
    error_code = "forbidden"


class UnsupportedDocumentError(ResumindError):
    """Raised by resume/JD ingestion for unsupported file types, sizes, etc."""

    status_code = 400
    error_code = "unsupported_document"


def _error_body(error: ResumindError) -> dict:
    return {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "details": error.details,
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ResumindError)
    async def handle_resumind_error(request: Request, exc: ResumindError):
        if exc.status_code >= 500:
            logger.exception("Unhandled domain error on %s", request.url.path)
        return JSONResponse(status_code=exc.status_code, content=_error_body(exc))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Internal server error",
                    "details": {},
                }
            },
        )
