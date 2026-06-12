"""Celery-приложение Bot Service.

Broker - RabbitMQ, result backend — Redis. Задачи регистрируются через
include + autodiscover, чтобы задача `llm_request` была видна воркеру.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=["app.tasks.llm_tasks"],
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    task_default_queue="llm",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)
