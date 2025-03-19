"""Модуль для сервиса пользователей."""

import uuid

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.modules.users.schemas as schemas
from src.core import exceptions
from src.core.base import BaseService
from src.core.services import HashService
from src.modules.users.models import UserModel
from src.modules.users.repository import UserRepository


class UserService(
    BaseService[
        UserModel,
        schemas.UserCreateSchema,
        schemas.UserGetAdminSchema,
        schemas.UsersQuerySchema,
        schemas.UserListGetSchema,
        schemas.UserUpdateSchema,
    ],
):
    """Сервис для работы с пользователями."""

    repository = UserRepository

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: schemas.UserCreateSchema | schemas.UserCreateAdminSchema,
    ) -> schemas.UserGetAdminSchema:
        """
        Создать пользователя в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (UserCreateSchema | UserCreateAdminSchema):
                Данные для создания пользователя.

        Returns:
            UserReadAdminSchema: Добавленный пользователь.

        Raises:
            ConflictException: Пользователь уже существует.
        """

        logger.info(f"Создание пользователя: {data}")

        try:
            # Хэширование пароля
            hashed_password = HashService.generate(data.password)
            data = schemas.UserCreateRepositorySchema(
                email=data.email,
                hashed_password=hashed_password,
            )

            # Добавление пользователя в БД
            user = await cls.repository.create(
                session=session,
                obj_in=data,
            )
            await session.commit()
            return schemas.UserGetAdminSchema.model_validate(user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        data: schemas.UserUpdateSchema | schemas.UserUpdateAdminSchema,
    ) -> schemas.UserGetAdminSchema:
        """
        Обновить данные пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.
            data (UserUpdateSchema | UserUpdateAdminSchema):
                Данные для обновления пользователя.

        Returns:
            UserReadAdminSchema: Обновленный пользователь.

        Raises:
            NotFoundException: Пользователь не найден.
            ConflictException: Пользователь с такими данными уже существует.
        """

        logger.info(f"Обновление пользователя: {user_id} - {data}")

        # Поиск пользователя в БД
        await cls.get_by_id(session, user_id)

        hashed_password = None
        if data.password:
            hashed_password = HashService.generate(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=schemas.UserUpdateRepositoryAdminSchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    is_admin=data.is_admin
                    if isinstance(data, schemas.UserUpdateAdminSchema)
                    else None,
                ),
            )
            await session.commit()

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserGetAdminSchema.model_validate(updated_user)
