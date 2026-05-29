"""Async Redis client factory and connection management."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_redis_pool: aioredis.ConnectionPool | None = None
_redis_client_override: Redis | None = None


def create_redis_pool() -> aioredis.ConnectionPool:
    """Create a new Redis connection pool from settings.

    Upstash requires TLS (rediss:// scheme). The ssl=True flag is
    automatically inferred by redis-py from the rediss:// URL prefix,
    so no explicit ssl argument is needed.
    """
    return aioredis.ConnectionPool.from_url(
        str(settings.REDIS_URL),
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
        socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
        retry=Retry(ExponentialBackoff(cap=10, base=1), retries=3),
        health_check_interval=30,
    )


def get_redis_pool() -> aioredis.ConnectionPool:
    """Return singleton Redis connection pool, creating it on first call."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = create_redis_pool()
        logger.info("Redis connection pool created")
    return _redis_pool


def get_redis_client() -> Redis:  # type: ignore[type-arg]
    """Return an async Redis client backed by the singleton pool."""
    global _redis_client_override
    if _redis_client_override is not None:
        return _redis_client_override
    return aioredis.Redis(connection_pool=get_redis_pool())


async def get_redis() -> AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    """FastAPI dependency that yields an async Redis client."""
    global _redis_client_override
    if _redis_client_override is not None:
        yield _redis_client_override
        return

    client: Redis = aioredis.Redis(connection_pool=get_redis_pool())  # type: ignore[type-arg]
    try:
        yield client
    finally:
        await client.aclose()


async def ping_redis() -> bool:
    """Health check — returns True if Redis is reachable."""
    try:
        client: Redis = aioredis.Redis(connection_pool=get_redis_pool())  # type: ignore[type-arg]
        result = bool(await client.ping())
        await client.aclose()
        return result
    except Exception as e:
        logger.error(f"Redis ping failed: {e}")
        return False


# Alias for backwards compatibility with existing call sites
check_redis_connection = ping_redis


async def close_redis_pool() -> None:
    """Drain and close the Redis connection pool on application shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Redis connection pool closed")


# Alias for backwards compatibility
close_redis = close_redis_pool
