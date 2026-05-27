"""User repository — DB access layer for users."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model queries."""

    model = User

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The email to look up.

        Returns:
            User instance or None.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username.

        Args:
            username: The username to look up.

        Returns:
            User instance or None.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered.

        Args:
            email: The email address to check.

        Returns:
            True if the email is taken.
        """
        return bool(await self.get_by_email(email))

    async def username_exists(self, username: str) -> bool:
        """Check if a username is already taken.

        Args:
            username: The username to check.

        Returns:
            True if the username is taken.
        """
        return bool(await self.get_by_username(username))
