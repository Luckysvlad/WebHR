# app/core/config.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]  # корень репозитория


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # окружение: local/dev/prod
    ENV: str = Field(default="local", description="local|dev|prod")
    # разрешать ли прямое подключение к MySQL локально
    ALLOW_MYSQL_LOCAL: bool = Field(default=False)

    # базовые параметры приложения
    APP_NAME: str = "WebHR"
    DEBUG: bool = False

    # секреты/сессии
    SECRET_KEY: str = "change_me_in_.env"
    SESSION_COOKIE_NAME: str = "webhr_session"

    # БД: либо готовый DATABASE_URL, либо конструктор через MYSQL_*
    DATABASE_URL: str = Field(default="sqlite:///data/app.db")

    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: int = 3306
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DB: Optional[str] = None

    # директории фронта
    TEMPLATES_DIR: str = str(ROOT_DIR / "templates")
    STATIC_DIR: str = str(ROOT_DIR / "static")

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Единая точка получения URL для SQLAlchemy.
        Приоритет:
            1) DATABASE_URL, если указан
            2) сборка из MYSQL_*
            3) SQLite по умолчанию
        Плюс защита: в ENV=local|dev и ALLOW_MYSQL_LOCAL=false — принудительно SQLite.
        """
        # если запретили mysql в локалке — форсим SQLite
        if self.ENV.lower() in {"local", "dev"} and not self.ALLOW_MYSQL_LOCAL:
            return "sqlite:///data/app.db"

        # явный DATABASE_URL
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            return self.DATABASE_URL

        # сборка mysql
        if self.MYSQL_HOST and self.MYSQL_USER and self.MYSQL_DB:
            pwd = self.MYSQL_PASSWORD or ""
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{pwd}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )

        # дефолт
        return "sqlite:///data/app.db"


settings = Settings()
