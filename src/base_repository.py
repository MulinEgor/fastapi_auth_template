"""Модуль интерфейсов для CRUD операций с моделям БД."""

from typing import Any, Generic, Tuple, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import Select, asc, delete, desc, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src import constants
from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Основной класс интерфейсов для CRUD операций с моделям БД.

    Args:
        model (Type[ModelType]): модель SQLAlchemy.
    """

    model = None

    # MARK: Create
    @classmethod
    async def add(
        cls,
        session: AsyncSession,
        obj_in: Union[CreateSchemaType, dict[str, Any]],
    ) -> ModelType:
        """
        Добавить запись в текущую сессию.

        Если `obj_in` является моделью Pydantic,
        из него удаляются не заданные явно поля.

        Returns:
            ModelType: созданный экземпляр модели.
        """

        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        stmt = insert(cls.model).values(**create_data).returning(cls.model)
        result = await session.execute(stmt)
        return result.scalars().one()

    @classmethod
    async def add_bulk(
        cls,
        session: AsyncSession,
        data: list[dict[str, Any]],
    ) -> list[ModelType]:
        """
        Добавить несколько записей в текущую сессию.

        Returns:
            list[ModelType]: список созданных моделей.
        """

        stmt = insert(cls.model).returning(cls.model)
        result = await session.execute(stmt, data)
        return result.scalars().all()

    # MARK: Read
    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        *filter,
        **filter_by,
    ) -> ModelType | None:
        """
        Возвращает как максимум один объект или выбрасывает исключение.

        Returns:
            ModelType:
                Найденная модель данных или `None`, если совпадений не было найдено.
        """

        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        offset: int = constants.DEFAULT_QUERY_OFFSET,
        limit: int = constants.DEFAULT_QUERY_LIMIT,
        *filter,
        **filter_by,
    ) -> list[ModelType]:
        """
        Возвращает все модели, соответствующие параметрам поиска.
        Если совпадений не найдено, возвращает пустой список.

        Returns:
            list[ModelType]: модели, соответствующие параметрам поиска.
        """

        stmt = (
            select(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def find_all_ilike(
        cls,
        session: AsyncSession,
        search_fields: dict[str, Any],
        offset: int = constants.DEFAULT_QUERY_OFFSET,
        limit: int = constants.DEFAULT_QUERY_LIMIT,
        *filter,
        **filter_by,
    ) -> list[ModelType]:
        """
        Гибкий поиск всех записей с использованием ilike.

        Returns:
            list[ModelType]: модели, соответствующие параметрам поиска.
        """

        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)

        if search_fields:
            search_conditions = []
            for field, value in search_fields.items():
                search_conditions.append(getattr(cls.model, field).ilike(f"%{value}%"))
            if search_conditions:
                stmt = stmt.filter(or_(*search_conditions))

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def find_all_sorted(
        cls,
        session: AsyncSession,
        sort_field,
        ascending: bool = True,
        limit: int | None = None,
        *filter,
        **filter_by,
    ) -> list[ModelType]:
        """
        Поиск всех записей, отсортированных по указанному полю.

        По умолчанию сортировка происходит по возрастанию.

        Returns:
            list[ModelType]: модели, соответствующие параметрам поиска.
        """

        sort_order = asc(sort_field) if ascending else desc(sort_field)
        stmt = (
            select(cls.model)
            .filter(sort_field.isnot(None))
            .filter(*filter)
            .filter_by(**filter_by)
            .order_by(sort_order)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_all_with_pagination_from_stmt(
        cls,
        session: AsyncSession,
        limit: int | None,
        offset: int | None,
        stmt: Select[Tuple[ModelType]],
    ) -> list[ModelType]:
        """
        Применить пагинацию к финальному выражению
        для запроса в БД, предварительно составленному с учетом фильтрации,
        и вернуть список сущностей.

        Returns:
            list[ModelType]:
                модели, соответствующие параметрам поиска, с учетом пагинации.
        """

        stmt = stmt.limit(limit=limit).offset(offset=offset)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_all_non_scalars_with_pagination_from_stmt(
        cls,
        session: AsyncSession,
        limit: int | None,
        offset: int | None,
        stmt: Select[Tuple[ModelType]],
    ) -> list[any]:
        """
        Применить пагинацию к финальному выражению
        для запроса в БД, предварительно составленному с учетом фильтрации,
        и вернуть список сущностей.

        Returns:
            list[ModelType]:
                модели, соответствующие параметрам поиска, с учетом пагинации.
        """

        stmt = stmt.limit(limit=limit).offset(offset=offset)
        result = await session.execute(stmt)
        return result.all()

    # MARK: Update
    @classmethod
    async def update(
        cls,
        *where,
        session: AsyncSession,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Обновить запись в текущей сессии.

        Если `obj_in` является моделью Pydantic,
        из него удаляются не заданные явно поля.

        Returns:
            ModelType: обновленный экземпляр модели.
        """

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

        stmt = (
            update(cls.model).where(*where).values(**update_data).returning(cls.model)
        )
        result = await session.execute(stmt)
        return result.scalars().one()

    @classmethod
    async def update_bulk(
        cls,
        session: AsyncSession,
        data: list[dict[str, Any]],
    ) -> list[ModelType]:
        """
        Обновить несколько записей в текущей сессии.

        Returns:
            list[ModelType](list[Base]): список обновленных  моделей.
        """

        stmt = update(cls.model).returning(cls.model)
        result = await session.execute(stmt, data)

        return result.scalars().all()

    # MARK: Delete
    @classmethod
    async def delete(
        cls,
        *filter,
        session: AsyncSession,
        **filter_by,
    ) -> None:
        """Удалить запись, соответствующую критериям."""

        stmt = delete(cls.model).filter(*filter).filter_by(**filter_by)
        await session.execute(stmt)

    # MARK: Count
    @classmethod
    async def count(
        cls,
        session: AsyncSession,
        *filter,
        **filter_by,
    ) -> int:
        """
        Посчитать строки в БД, соответствующий критериям.

        Returns:
            rows_count: количество найденных строк или 0 если совпадений не найдено.
        """

        stmt = (
            select(func.count())
            .select_from(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await session.execute(stmt)
        rows_count = result.scalar()
        if rows_count is None:
            return 0
        return rows_count

    @classmethod
    async def count_all_ilike(
        cls,
        session: AsyncSession,
        search_fields: dict[str, Any],
        *filter,
        **filter_by,
    ) -> int:
        """
        Посчитать строки в БД, соответствующий критериям. с использованием ilike.

        Returns:
            rows_count: количество найденных строк или 0 если совпадений не найдено.
        """

        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)

        if search_fields:
            search_conditions = []
            for field, value in search_fields.items():
                search_conditions.append(getattr(cls.model, field).ilike(f"%{value}%"))
            if search_conditions:
                stmt = stmt.filter(or_(*search_conditions))

        result = await session.execute(stmt)
        return len(result.scalars().all())

    @classmethod
    async def count_subquery(
        cls,
        session: AsyncSession,
        stmt: Select[Tuple[ModelType]],
    ) -> int:
        """
        Получить общее количество сущностей в БД, используя финальное выражение
        для запроса в БД, предварительно составленное с учетом фильтрации.

        Returns:
            total_count: общее количество сущностей.
        """

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count_result = await session.execute(count_stmt)
        total_count = total_count_result.scalar()

        if total_count is None:
            return 0

        return total_count
