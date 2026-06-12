"""Доменные HTTP-исключения Auth Service.

Все прикладные ошибки наследуются от BaseHTTPException и используются
в usecase-слое и dependencies вместо ручных raise HTTPException.
"""

from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение сервиса."""

    status_code: int = 500
    detail: str = "Internal server error"
    headers: dict[str, str] | None = None

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers,
        )


class UserAlreadyExistsError(BaseHTTPException):
    status_code = 409
    detail = "User with this email already exists"


class InvalidCredentialsError(BaseHTTPException):
    status_code = 401
    detail = "Invalid email or password"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenError(BaseHTTPException):
    status_code = 401
    detail = "Invalid token"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredError(BaseHTTPException):
    status_code = 401
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundError(BaseHTTPException):
    status_code = 404
    detail = "User not found"


class PermissionDeniedError(BaseHTTPException):
    status_code = 403
    detail = "Permission denied"
