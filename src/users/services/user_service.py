"""Модуль для сервиса пользователей."""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.schemas as user_schemas
from src import exceptions, utils
from src.users.models import UserModel
from src.users.repositories import UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: user_schemas.UserCreateSchema | user_schemas.UserCreateAdminSchema,
    ) -> user_schemas.UserReadAdminSchema:
        """
        Создать пользователя в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (UserCreateSchema | UserCreateAdminSchema):
                Данные для создания пользователя.

        Returns:
            UserReadAdminSchema: Добавленный пользователь.

        Raises:
            UserAlreadyExistsException: Пользователь уже существует.
        """

        try:
            # Хэширование пароля
            hashed_password = utils.get_hash(data.password)
            data = user_schemas.UserCreateRepositorySchema(
                email=data.email,
                hashed_password=hashed_password,
            )

            # Добавление пользователя в БД
            user = await UserRepository.add(
                session=session,
                obj_in=data,
            )
            await session.commit()
            return user_schemas.UserReadAdminSchema.model_validate(user)

        except IntegrityError as ex:
            print(ex)
            raise exceptions.UserAlreadyExistsException(exc=ex)

    # MARK: Get
    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> user_schemas.UserReadAdminSchema:
        """
        Поиск пользователя по ID.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.

        Returns:
            UserReadAdminSchema: Найденный пользователь.

        Raises:
            UserNotFoundException: Пользователь не найден.
        """

        # Поиск пользователя в БД
        user_db = await UserRepository.find_one_or_none(session=session, id=user_id)

        if user_db is None:
            raise exceptions.UserNotFoundException

        return user_schemas.UserReadSchema.model_validate(user_db)

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        query_params: user_schemas.UsersQuerySchema,
    ) -> user_schemas.UserListReadSchema:
        """
        Получить список пользователей и их общее количество
        с фильтрацией по query параметрам, отличным от None.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            query_params (UsersQuerySchema): Query параметры для фильтрации.

        Returns:
            UserListReadSchema: список пользователей и их общее количество.

        Raises:
            UserNotFoundException: Пользователи не найдены.
        """

        base_stmt = await UserRepository.get_users_stmt_by_query(
            query_params=query_params,
        )
        users = await UserRepository.get_all_with_pagination_from_stmt(
            session=session,
            limit=query_params.limit,
            offset=query_params.offset,
            stmt=base_stmt,
        )

        if not users:
            raise exceptions.UserNotFoundException

        users_count = await UserRepository.count_subquery(
            session=session,
            stmt=base_stmt,
        )

        return user_schemas.UserListReadSchema(
            count=users_count,
            users=users,
        )

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        data: user_schemas.UserUpdateSchema | user_schemas.UserUpdateAdminSchema,
    ) -> user_schemas.UserReadAdminSchema:
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
            UserNotFoundException: Пользователь не найден.
            UserAlreadyExistsException: Пользователь с такими данными уже существует.
        """

        # Поиск пользователя в БД
        await cls.get_by_id(session=session, user_id=user_id)

        hashed_password = None
        if data.password:
            hashed_password = utils.get_hash(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=user_schemas.UserUpdateRepositoryAdminSchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    is_admin=data.is_admin
                    if isinstance(data, user_schemas.UserUpdateAdminSchema)
                    else None,
                ),
            )
            await session.commit()

        except IntegrityError as ex:
            print(ex)
            raise exceptions.UserAlreadyExistsException(exc=ex)

        return user_schemas.UserReadAdminSchema.model_validate(updated_user)

    # MARK: Delete
    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> None:
        """
        Удалить пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.

        Raises:
            UserNotFoundException: Пользователь не найден.
        """

        # Поиск пользователя в БД
        await cls.get_by_id(session=session, user_id=user_id)

        # Удаление пользователя из БД
        await UserRepository.delete(
            id=user_id,
            session=session,
        )
        await session.commit()
