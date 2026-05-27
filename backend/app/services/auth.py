"""Authentication business logic."""

import logging
import uuid
from datetime import datetime, timezone

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.constants import REDIS_TOKEN_BLACKLIST_KEY
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions import ConflictError, UnauthorizedError
from app.models.user import User
from app.redis.client import get_redis_client
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserWithToken

logger = logging.getLogger(__name__)


class AuthService:
    """Handles registration, login, token refresh, and logout."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.redis = get_redis_client()

    async def register(self, schema: RegisterRequest) -> UserWithToken:
        """Register a new user and return tokens.

        Args:
            schema: Registration payload.

        Returns:
            User data with access and refresh tokens.

        Raises:
            ConflictError: If email or username is already taken.
        """
        if await self.user_repo.email_exists(schema.email):
            raise ConflictError("Email is already registered")
        if await self.user_repo.username_exists(schema.username):
            raise ConflictError("Username is already taken")

        user = User(
            id=str(uuid.uuid4()),
            email=schema.email,
            username=schema.username,
            hashed_password=hash_password(schema.password),
            display_name=schema.display_name,
            is_active=True,
        )
        user = await self.user_repo.create(user)

        from app.schemas.user import UserResponse
        user_response = UserResponse.model_validate(user)
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"User registered: {user.username}")
        return UserWithToken(user=user_response, access_token=access_token, refresh_token=refresh_token)

    async def login(self, schema: LoginRequest) -> UserWithToken:
        """Authenticate a user and return tokens.

        Args:
            schema: Login payload with email and password.

        Returns:
            User data with access and refresh tokens.

        Raises:
            UnauthorizedError: If credentials are invalid or account is inactive.
        """
        user = await self.user_repo.get_by_email(schema.email)
        if not user or not verify_password(schema.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")

        from app.schemas.user import UserResponse
        user_response = UserResponse.model_validate(user)
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"User logged in: {user.username}")
        return UserWithToken(user=user_response, access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, schema: RefreshRequest) -> TokenPair:
        """Issue a new token pair from a valid refresh token.

        Args:
            schema: Payload containing the refresh token.

        Returns:
            New access and refresh token pair.

        Raises:
            UnauthorizedError: If the refresh token is invalid or blacklisted.
        """
        try:
            payload = decode_token(schema.refresh_token)
        except JWTError as e:
            raise UnauthorizedError(f"Invalid refresh token: {e}") from e

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Token type must be 'refresh'")

        old_jti: str = payload.get("jti", "")
        blacklist_key = REDIS_TOKEN_BLACKLIST_KEY.format(jti=old_jti)
        if await self.redis.exists(blacklist_key):
            raise UnauthorizedError("Refresh token has been revoked")

        user_id: str = payload.get("sub", "")
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        # Blacklist old refresh token
        settings = get_settings()
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        await self.redis.setex(blacklist_key, ttl, "1")

        new_access = create_access_token(user_id)
        new_refresh = create_refresh_token(user_id)
        return TokenPair(access_token=new_access, refresh_token=new_refresh)

    async def logout(self, user_id: str, access_jti: str) -> None:
        """Blacklist the user's current access token.

        Args:
            user_id: The user's UUID string.
            access_jti: JWT ID of the access token to revoke.
        """
        settings = get_settings()
        ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        blacklist_key = REDIS_TOKEN_BLACKLIST_KEY.format(jti=access_jti)
        await self.redis.setex(blacklist_key, ttl, "1")
        logger.info(f"User logged out: {user_id}")
