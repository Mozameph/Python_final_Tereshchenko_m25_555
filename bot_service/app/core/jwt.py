"""Проверка JWT в Bot Service.

Здесь токены ТОЛЬКО валидируются. Создание токенов — зона ответственности
Auth Service. Bot Service знает общий секрет (HS256) и проверяет подпись,
срок действия и наличие sub.
"""

from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings


class TokenValidationError(ValueError):
    """Токен отсутствует, неверен или истёк."""


def decode_and_validate(token: str) -> dict[str, Any]:
    """Проверяет подпись и exp, возвращает payload.

    Бросает TokenValidationError, если токен неверный или истёк.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except ExpiredSignatureError as exc:
        raise TokenValidationError("Token has expired") from exc
    except JWTError as exc:
        raise TokenValidationError("Invalid token") from exc

    if not payload.get("sub"):
        raise TokenValidationError("Token has no subject")
    return payload
