"""Custom exception classes and FastAPI exception handlers."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AppException(HTTPException):
    """Base application exception with a machine-readable code."""

    def __init__(self, status_code: int, detail: str, code: str) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    """Authentication required."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """Insufficient permissions."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="FORBIDDEN",
        )


class ConflictError(AppException):
    """Resource conflict (duplicate)."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code="CONFLICT",
        )


class ValidationError(AppException):
    """Business-logic validation failure."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code="VALIDATION_ERROR",
        )


class RateLimitError(AppException):
    """Too many requests."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down.",
            code="RATE_LIMITED",
        )


def _error_body(detail: str, code: str) -> dict[str, str]:
    return {
        "detail": detail,
        "code": code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for application-level exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.detail, exc.code),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for generic FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(str(exc.detail), f"HTTP_{exc.status_code}"),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic request validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(f"{field}: {error['msg']}")
    detail = "; ".join(errors) if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(detail, "VALIDATION_ERROR"),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handler for database errors — logs details, returns generic 500."""
    logger.error(f"Database error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("An internal database error occurred", "DB_ERROR"),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("An unexpected error occurred", "INTERNAL_ERROR"),
    )
