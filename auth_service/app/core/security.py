"""Функции безопасности: хеширование паролей и работа с JWT."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Проверяет пароль против сохранённого хеша."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    sub: str | int,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    """Создаёт JWT c обязательными полями sub, role, iat, exp."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(sub),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> dict[str, Any]:
    """Декодирует и валидирует JWT (подпись + срок действия).

    Бросает TokenExpiredError, если токен истёк,
    и InvalidTokenError при любой другой проблеме с токеном.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        raise InvalidTokenError() from exc
    if "sub" not in payload:
        raise InvalidTokenError("У токена нет субъекта")
    return payload
