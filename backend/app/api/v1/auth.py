"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.base import get_db
from app.dependencies import get_current_user_id
from app.exceptions import UnauthorizedError
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserWithToken
from app.services.auth import AuthService

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserWithToken, status_code=201)
async def register(
    schema: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserWithToken:
    """Register a new user account and return JWT tokens."""
    svc = AuthService(db)
    return await svc.register(schema)


@router.post("/login", response_model=UserWithToken)
async def login(
    schema: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserWithToken:
    """Authenticate with email/password and return JWT tokens."""
    svc = AuthService(db)
    return await svc.login(schema)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    schema: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    """Exchange a valid refresh token for a new token pair."""
    svc = AuthService(db)
    return await svc.refresh(schema)


@router.post("/logout", status_code=204)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Revoke the current access token (add to blacklist)."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e

    jti: str = payload.get("jti", "")
    svc = AuthService(db)
    await svc.logout(user_id, jti)
