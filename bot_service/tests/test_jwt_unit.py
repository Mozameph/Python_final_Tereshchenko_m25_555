"""Модульные тесты валидации JWT в Bot Service.

Токены здесь создаются тем же секретом/алгоритмом, что использует
Auth Service, — сам Bot Service токены НЕ создаёт.
"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import TokenValidationError, decode_and_validate


def make_token(sub="42", role="user", expires_in_minutes=60):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def test_valid_token_decodes_and_returns_sub():
    token = make_token(sub="42", role="admin")
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_garbage_string_raises():
    with pytest.raises(TokenValidationError):
        decode_and_validate("this-is-not-a-jwt-at-all")


def test_expired_token_raises():
    token = make_token(expires_in_minutes=-10)
    with pytest.raises(TokenValidationError):
        decode_and_validate(token)


def test_token_signed_with_wrong_secret_raises():
    now = datetime.now(timezone.utc)
    bad = jwt.encode(
        {"sub": "1", "exp": int((now + timedelta(minutes=5)).timestamp())},
        "another_secret",
        algorithm=settings.jwt_alg,
    )
    with pytest.raises(TokenValidationError):
        decode_and_validate(bad)


def test_token_without_sub_raises():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"exp": int((now + timedelta(minutes=5)).timestamp())},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )
    with pytest.raises(TokenValidationError):
        decode_and_validate(token)
