"""Эндпоинты для проверки состояние работы API."""

from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.settings import settings


# MARK: Schema
class HealthCheckSchema(BaseModel):
    """Схема ответа для проверки состояния работы API."""

    mode: Literal["DEV", "TEST", "PROD"] = Field(
        default=settings.MODE,
        description="Режим, в котором работает API.",
    )
    version: str = Field(
        default=settings.APP_VERSION,
        description="Версия API. Соответствует хэшу актуального коммита.",
    )
    status: str = Field(
        default="OK",
        description="Статус API.",
    )


# MARK: Router
health_check_router = APIRouter(prefix="/health_check", tags=["Health Check"])


@health_check_router.get(
    path="",
    summary="Проверить состояние работы API",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthCheckSchema:
    """Проверить состояние работы API."""

    return HealthCheckSchema()
