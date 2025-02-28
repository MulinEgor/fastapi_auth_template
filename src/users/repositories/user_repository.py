"""Модуль для репозиториев пользователей."""

from typing import Tuple

from sqlalchemy import Select, select

import src.users.schemas as user_schemas
from src.base_repository import BaseRepository
from src.users.models import UserModel


class UserRepository(
    BaseRepository[
        UserModel,
        user_schemas.UserCreateRepositorySchema
        | user_schemas.UserCreateRepositoryAdminSchema,
        user_schemas.UserUpdateRepositorySchema
        | user_schemas.UserUpdateRepositoryAdminSchema,
    ]
):
    """
    Основной репозиторий для работы с моделью UserModel.
    Наследуется от базового репозитория.
    """

    model = UserModel

    @classmethod
    async def get_users_stmt_by_query(
        cls,
        query_params: user_schemas.UsersQuerySchema,
    ) -> Select[Tuple[UserModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка пользователей.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(UserModel)

        # Фильтрация по username с использованием ilike.
        if query_params.email:
            stmt = stmt.where(UserModel.email.ilike(f"%{query_params.email}%"))

        # Фильтрация статусу пользователя на платформе.
        if query_params.is_admin is not None:
            if query_params.is_admin:
                stmt = stmt.where(UserModel.is_admin.is_(True))
            else:
                stmt = stmt.where(UserModel.is_admin.is_(False))

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(UserModel.created_at.desc())
        else:
            stmt = stmt.order_by(UserModel.created_at)

        return stmt
