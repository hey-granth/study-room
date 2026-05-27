"""Shared FastAPI dependencies."""

import logging
from typing import Annotated, Any

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.base import get_db
from app.exceptions import UnauthorizedError
from app.redis.client import get_redis_client
from app.constants import REDIS_TOKEN_BLACKLIST_KEY

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Validate Bearer JWT and return the user_id (sub).

    Args:
        credentials: HTTP Bearer token from Authorization header.

    Returns:
        User ID string from token subject.

    Raises:
        UnauthorizedError: If token is missing, invalid, expired, or blacklisted.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e

    if payload.get("type") != "access":
        raise UnauthorizedError("Token type must be 'access'")

    user_id: str | None = payload.get("sub")
    jti: str | None = payload.get("jti")
    if not user_id or not jti:
        raise UnauthorizedError("Token missing required claims")

    # Check blacklist
    redis = get_redis_client()
    blacklist_key = REDIS_TOKEN_BLACKLIST_KEY.format(jti=jti)
    if await redis.exists(blacklist_key):
        raise UnauthorizedError("Token has been revoked")

    return user_id


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Load and return the authenticated User ORM object.

    Args:
        user_id: Validated user ID from JWT.
        db: Async database session.

    Returns:
        User ORM object.

    Raises:
        UnauthorizedError: If user not found or inactive.
    """
    from app.repositories.user import UserRepository

    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")
    return user


def get_pagination(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> tuple[int, int]:
    """FastAPI dependency for pagination query parameters.

    Returns:
        Tuple of (page, size).
    """
    return page, size
