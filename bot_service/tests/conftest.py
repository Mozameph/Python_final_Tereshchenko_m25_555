"""Тестовая инфраструктура Bot Service.

Redis мокается через fakeredis. ВАЖНО: патчим get_redis именно в модуле
обработчиков (app.bot.handlers.get_redis), иначе тесты попытаются
подключиться к реальному redis:6379.
"""

from types import SimpleNamespace

import fakeredis.aioredis
import pytest


class FakeMessage:
    """Минимальный аналог aiogram.types.Message для прямого вызова хэндлеров."""

    def __init__(self, text: str, user_id: int = 111, chat_id: int = 222) -> None:
        self.text = text
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=chat_id)
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append(text)


@pytest.fixture
def fake_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def patched_redis(monkeypatch, fake_redis):
    """Подменяет get_redis в модуле хэндлеров на fakeredis."""
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: fake_redis)
    return fake_redis


@pytest.fixture
def make_message():
    def _make(text: str, user_id: int = 111, chat_id: int = 222) -> FakeMessage:
        return FakeMessage(text=text, user_id=user_id, chat_id=chat_id)

    return _make
