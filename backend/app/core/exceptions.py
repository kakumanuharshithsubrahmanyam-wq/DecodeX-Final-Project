from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: list[dict] | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


def not_found(message: str = "Resource not found") -> AppError:
    return AppError("NOT_FOUND", message, 404)


def forbidden(message: str = "Forbidden") -> AppError:
    return AppError("FORBIDDEN", message, 403)


def unauthorized(message: str = "Unauthorized") -> AppError:
    return AppError("UNAUTHORIZED", message, 401)


def conflict(message: str) -> AppError:
    return AppError("CONFLICT", message, 409)


def validation_error(message: str, details: list[dict[str, Any]] | None = None) -> AppError:
    return AppError("VALIDATION_ERROR", message, 400, details)
