"""Celery-задача обработки LLM-запроса.

Цепочка: handler бота публикует задачу в RabbitMQ -> Celery worker
вызывает OpenRouter -> результат сохраняется в Redis (result backend +
явный ключ result:<chat_id>) -> ответ отправляется пользователю в Telegram.
"""

import asyncio
import logging

import httpx
import redis as redis_sync

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import OpenRouterError, call_openrouter

logger = logging.getLogger(__name__)

TELEGRAM_MESSAGE_LIMIT = 4096


def _send_telegram_message(chat_id: int, text: str) -> None:
    """Отправляет сообщение пользователю напрямую через Telegram Bot API."""
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — пропускаю отправку сообщения")
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    resp = httpx.post(url, json={"chat_id": chat_id, "text": text[:TELEGRAM_MESSAGE_LIMIT]}, timeout=30.0)
    if resp.status_code != 200:
        logger.error("Telegram sendMessage failed: %s %s", resp.status_code, resp.text[:200])


@celery_app.task(name="llm_request", bind=True, max_retries=2, default_retry_delay=5)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:
    """Выполняет запрос к LLM и доставляет ответ пользователю."""
    logger.info("LLM task started: chat_id=%s", tg_chat_id)
    try:
        answer = asyncio.run(call_openrouter(prompt))
    except OpenRouterError as exc:
        logger.exception("OpenRouter error")
        answer = f"Не удалось получить ответ от LLM: {exc}"

    # Redis используется и как result backend Celery, и как явное хранилище
    # последнего результата для пользователя.
    try:
        r = redis_sync.Redis.from_url(settings.redis_url, decode_responses=True)
        r.set(f"result:{tg_chat_id}", answer, ex=3600)
    except Exception:  # noqa: BLE001 — кэш не должен ронять доставку ответа
        logger.exception("Failed to cache result in Redis")

    _send_telegram_message(tg_chat_id, answer)
    return answer
