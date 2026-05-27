"""Async Redis client factory and connection management."""

import logging
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None
_client: Redis[Any] | None = None


def get_redis_pool() -> ConnectionPool:
    """Return a singleton Redis connection pool."""
    global _pool
    if _pool is None:
        settings = get_settings()
        url = str(settings.REDIS_URL)
        _pool = aioredis.ConnectionPool.from_url(
            url,
            decode_responses=True,
            max_connections=20,
        )
        logger.info("Redis connection pool created")
    return _pool


def get_redis_client() -> Redis[Any]:
    """Return a singleton async Redis client."""
    global _client
    if _client is None:
        pool = get_redis_pool()
        _client = aioredis.Redis(connection_pool=pool)
    return _client


async def close_redis() -> None:
    """Close the Redis connection pool on shutdown."""
    global _pool, _client
    if _client is not None:
        await _client.aclose()
        _client = None
    if _pool is not None:
        await _pool.aclose()
        _pool = None
    logger.info("Redis connection closed")


async def ping_redis() -> bool:
    """Health check — returns True if Redis is reachable."""
    try:
        client = get_redis_client()
        return bool(await client.ping())
    except Exception as e:
        logger.error(f"Redis ping failed: {e}")
        return False
