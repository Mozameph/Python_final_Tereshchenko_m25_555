"""Настройки Bot Service через pydantic-settings.

Значения по умолчанию для Redis/RabbitMQ указывают на имена сервисов
docker-compose (redis, rabbitmq), а не на localhost.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "bot-service"
    env: str = "local"

    telegram_bot_token: str = ""
    auth_service_url: str = "http://auth_service:8000"

    # JWT: тот же секрет и алгоритм, что и в Auth Service (HS256)
    jwt_secret: str = "change_me_super_secret"
    jwt_alg: str = "HS256"

    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "stepfun/step-3.5-flash:free"
    openrouter_site_url: str = "https://example.com"
    openrouter_app_name: str = "bot-service"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
