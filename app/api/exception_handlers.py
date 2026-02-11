from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas import ErrorResponse
from app.domain.exceptions import (
    AuthenticationError,
    InvalidOrderStatusTransition,
    NotFoundError,
    PermissionDenied,
    UserAlreadyExists,
)


def _build_detail(message: str, exc: BaseException) -> str:
    """Безопасно формирует detail для ответа."""
    error_type = exc.__class__.__name__
    reason = str(exc)
    safe_reason = reason[:300] if reason else ""
    if safe_reason:
        return f"{message} ({error_type}): {safe_reason}"
    return f"{message} ({error_type})"


def setup_exception_handlers(app):
    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(detail=_build_detail("Authentication failed", exc)).model_dump(),
        )

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=_build_detail("User already exists", exc)).model_dump(),
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(detail=_build_detail("Resource not found", exc)).model_dump(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(detail=_build_detail("Database error", exc)).model_dump(),
        )

    @app.exception_handler(PermissionDenied)
    async def permission_denied_handler(request: Request, exc: PermissionDenied):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(detail=_build_detail("Access denied", exc)).model_dump(),
        )

    @app.exception_handler(InvalidOrderStatusTransition)
    async def invalid_order_status_transition_handler(request: Request, exc: InvalidOrderStatusTransition):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=_build_detail("Invalid order status transition", exc)).model_dump(),
        )
