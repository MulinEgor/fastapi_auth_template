"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core import constants, handlers, middlewares
from src.core.logger import setup_logging
from src.core.settings import settings
from src.modules.auth import auth_router
from src.modules.healthcheck import health_check_router
from src.modules.users import user_router


def setup_middlewares(app: FastAPI) -> None:
    """Настройка middleware."""

    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=constants.CORS_METHODS,
        allow_headers=constants.CORS_HEADERS,
    )
    app.add_middleware(middlewares.ORJSONRequestMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """Настройка обработчиков исключений"""
    app.add_exception_handler(HTTPException, handlers.http_exception_handler)
    app.add_exception_handler(Exception, handlers.exception_handler)


def setup_routers(app: FastAPI) -> None:
    """Настройка маршрутов."""

    available_routers = [
        health_check_router,
        auth_router,
        user_router,
    ]

    for router in available_routers:
        app.include_router(router=router, prefix="/api/v1")


app = FastAPI(
    title="FastAPI Template",
    version=settings.APP_VERSION,
)

setup_logging()
setup_middlewares(app)
setup_exception_handlers(app)
setup_routers(app)
