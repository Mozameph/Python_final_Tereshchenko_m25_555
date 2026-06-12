"""Клиент OpenRouter (/chat/completions) на httpx.

Обрабатывает сетевые ошибки и не-200 ответы, чтобы Celery-воркер
не падал без понятного сообщения.
"""

from typing import Any

import httpx

from app.core.config import settings


class OpenRouterError(Exception):
    """Ошибка обращения к OpenRouter (сеть, статус, формат ответа)."""


def _build_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_app_name,
    }


def _build_payload(prompt: str, model: str | None = None) -> dict[str, Any]:
    return {
        "model": model or settings.openrouter_model,
        "messages": [{"role": "user", "content": prompt}],
    }


async def call_openrouter(prompt: str, model: str | None = None) -> str:
    """Отправляет prompt в OpenRouter и возвращает текст ответа модели."""
    url = f"{settings.openrouter_base_url}/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=_build_payload(prompt, model), headers=_build_headers())
    except httpx.HTTPError as exc:
        raise OpenRouterError(f"Network error while calling OpenRouter: {exc}") from exc

    if response.status_code != 200:
        raise OpenRouterError(
            f"OpenRouter returned status {response.status_code}: {response.text[:300]}"
        )

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError(f"Unexpected OpenRouter response format: {exc}") from exc
