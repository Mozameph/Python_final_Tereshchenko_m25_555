"""Интеграционные тесты клиента OpenRouter через respx (без интернета)."""

import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import OpenRouterError, call_openrouter

CHAT_URL = f"{settings.openrouter_base_url}/chat/completions"


@respx.mock
async def test_call_openrouter_returns_text_and_makes_http_call():
    route = respx.post(CHAT_URL).mock(
        return_value=Response(
            200,
            json={"choices": [{"message": {"role": "assistant", "content": "Привет! Я LLM."}}]},
        )
    )

    answer = await call_openrouter("Скажи привет")

    assert answer == "Привет! Я LLM."
    assert route.called
    request = route.calls.last.request
    sent = request.read().decode()
    assert "Скажи привет" in sent
    assert settings.openrouter_model in sent


@respx.mock
async def test_call_openrouter_non_200_raises():
    respx.post(CHAT_URL).mock(return_value=Response(500, text="internal error"))
    with pytest.raises(OpenRouterError):
        await call_openrouter("test")


@respx.mock
async def test_call_openrouter_bad_payload_raises():
    respx.post(CHAT_URL).mock(return_value=Response(200, json={"unexpected": True}))
    with pytest.raises(OpenRouterError):
        await call_openrouter("test")
