"""FastAPI application factory with lifespan, middleware, and exception handlers."""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.config import get_settings
from app.core.ws_manager import manager
from app.db.base import engine
from app.exceptions import (
    AppException,
    RateLimitError,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.redis.client import close_redis, get_redis_client, ping_redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup → yield → shutdown."""
    logger.info("Starting StudyRoom API")

    # Start WebSocket pub/sub background listener
    pubsub_task = asyncio.create_task(manager.start_pubsub_listener())

    yield

    # Shutdown
    logger.info("Shutting down StudyRoom API")
    pubsub_task.cancel()
    try:
        await pubsub_task
    except asyncio.CancelledError:
        pass

    await engine.dispose()
    await close_redis()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Collaborative Study Room Platform API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next: Any) -> Response:
        """Log every HTTP request with method, path, status, and duration."""
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} "
            f"({duration_ms:.1f}ms)"
        )
        return response

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next: Any) -> Response:
        """Redis-backed per-IP rate limiting (60 req/min by default)."""
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)  # type: ignore[return-value]

        client_ip = request.client.host if request.client else "unknown"
        minute = int(time.time() // 60)
        key = f"rate_limit:{client_ip}:{minute}"

        redis = get_redis_client()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)

        if count > settings.RATE_LIMIT_PER_MINUTE:
            from fastapi.responses import JSONResponse
            from datetime import datetime, timezone

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "code": "RATE_LIMITED",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        return await call_next(request)  # type: ignore[return-value]

    # --- Exception handlers ---
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)

    # --- Routers ---
    app.include_router(api_router, prefix="/api/v1")

    # --- Health check ---
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Return service health — checks DB and Redis connectivity."""
        from app.db.base import AsyncSessionLocal

        db_status = "ok"
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"DB health check failed: {e}")
            db_status = "error"

        redis_status = "ok" if await ping_redis() else "error"

        from datetime import datetime, timezone

        return {
            "status": "ok",
            "db": db_status,
            "redis": redis_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return app


app = create_app()
