from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.exceptions import (
    ConcurrencyConflictError,
    DomainError,
    InvalidTransitionError,
    MissingDocumentError,
    NotFoundError,
)


ERROR_MAP: dict[type[DomainError], tuple[int, str]] = {
    NotFoundError: (404, "NOT_FOUND"),
    InvalidTransitionError: (400, "INVALID_TRANSITION"),
    MissingDocumentError: (400, "MISSING_DOCUMENT"),
    ConcurrencyConflictError: (409, "VERSION_CONFLICT"),
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code, code = ERROR_MAP.get(
            type(exc), (500, "INTERNAL_ERROR")
        )
        return JSONResponse(
            status_code=status_code,
            content={"code": code, "message": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
            },
        )
