"""Generic async CRUD repository."""

from typing import Any, Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository providing standard CRUD operations.

    Type Parameters:
        ModelT: The SQLAlchemy ORM model class.
    """

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            db: Async SQLAlchemy session.
        """
        self.db = db

    async def get(self, id: Any) -> ModelT | None:
        """Fetch a single record by primary key.

        Args:
            id: The primary key value.

        Returns:
            The model instance, or None if not found.
        """
        result = await self.db.execute(select(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 20) -> tuple[list[ModelT], int]:
        """Fetch multiple records with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Tuple of (list of models, total count).
        """
        count_result = await self.db.execute(select(func.count()).select_from(self.model))
        total = count_result.scalar_one()

        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        items = list(result.scalars().all())
        return items, total

    async def create(self, obj: ModelT) -> ModelT:
        """Persist a new model instance.

        Args:
            obj: The model instance to create.

        Returns:
            The persisted model instance with DB-generated fields populated.
        """
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: dict[str, Any]) -> ModelT:
        """Update a model instance with the provided field values.

        Args:
            obj: The model instance to update.
            data: Dictionary of field name → new value.

        Returns:
            The updated model instance.
        """
        for key, value in data.items():
            setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        """Delete a model instance from the database.

        Args:
            obj: The model instance to delete.
        """
        await self.db.delete(obj)
        await self.db.flush()

    async def exists(self, id: Any) -> bool:
        """Check if a record with the given ID exists.

        Args:
            id: The primary key value.

        Returns:
            True if the record exists.
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return (result.scalar_one() or 0) > 0
