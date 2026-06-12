"""Модульные тесты функций безопасности (без БД и FastAPI)."""

import pytest

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_not_plaintext():
    password = "super_secret_123"
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2")  # bcrypt-формат


def test_verify_password_correct():
    password = "super_secret_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correct_password")
    assert verify_password("wrong_password", hashed) is False


def test_create_and_decode_token_payload():
    token = create_access_token(sub=42, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]


def test_decode_garbage_token_raises():
    with pytest.raises(InvalidTokenError):
        decode_token("definitely.not.a.jwt")


def test_decode_expired_token_raises():
    token = create_access_token(sub=1, role="user", expires_minutes=-5)
    with pytest.raises(TokenExpiredError):
        decode_token(token)
