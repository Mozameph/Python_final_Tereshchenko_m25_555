"""Настройки Auth Service.

Единственный источник конфигурации приложения. Значения читаются из
переменных окружения и файла `.env` через pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "auth-service"
    env: str = "local"

    # JWT
    jwt_secret: str = "change_me_super_secret"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60

    # База данных: либо полный DATABASE_URL, либо путь до SQLite-файла
    sqlite_path: str = "./auth.db"
    database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        """Итоговая строка подключения для SQLAlchemy."""
        if self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{self.sqlite_path}"


settings = Settings()
