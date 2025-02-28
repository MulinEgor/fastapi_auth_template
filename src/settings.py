"""Настройки конфигурации основного API."""

import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


class Settings(BaseSettings):
    """Класс переменных окружения основного API."""

    MODE: Literal["DEV", "TEST", "PROD"]
    APP_VERSION: str = "0.1.0"

    # Security
    CORS_ORIGINS: list[str]

    # Postgres
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # JWT
    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_EXPIRE_MINUTES: int
    JWT_REFRESH_EXPIRE_MINUTES: int

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)


settings = Settings()
