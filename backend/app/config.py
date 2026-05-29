"""Application configuration via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "StudyRoom"
    APP_ENV: str = "development"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database — constructed and injected by docker-compose environment block.
    # Must use postgresql+asyncpg:// prefix for async driver (asyncpg).
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800  # 30 min — prevents stale connections
    DATABASE_POOL_PRE_PING: bool = True  # detect dropped connections

    # Redis — constructed and injected by docker-compose environment block.
    # Uses redis:// (no TLS) because traffic stays on the Docker bridge network.
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: float = 5.0
    REDIS_SOCKET_CONNECT_TIMEOUT: float = 5.0
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_DECODE_RESPONSES: bool = True

    # JWT
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Any) -> list[str]:
        """Parse ALLOWED_ORIGINS from JSON string or list."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v  # type: ignore[return-value]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use postgresql+asyncpg:// prefix. "
                "SQLite is not supported in production."
            )
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://") and not v.startswith("rediss://"):
            raise ValueError("REDIS_URL must use redis:// or rediss:// scheme.")
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()  # type: ignore[call-arg]
