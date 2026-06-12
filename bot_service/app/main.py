"""FastAPI-приложение Bot Service: только служебные ручки.

Бот (aiogram) и Celery worker запускаются отдельными процессами
в docker-compose. Здесь нет логики LLM и работы с Redis.
"""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
