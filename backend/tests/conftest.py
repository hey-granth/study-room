"""Pytest fixtures for all backend tests."""

import asyncio
import uuid
from typing import Any, AsyncGenerator

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base, get_db
from app.main import app
from app.models.room import Room
from app.models.user import User
from app.redis.client import get_redis_client


# Use in-memory SQLite for unit/integration tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session")
async def setup_db() -> AsyncGenerator[None, None]:
    """Create all tables in the test database once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db(setup_db: None) -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session, rolling back after each test."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def test_redis() -> AsyncGenerator[Any, None]:
    """Yield a fakeredis async instance for test isolation."""
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest_asyncio.fixture
async def async_client(db: AsyncSession, test_redis: Any) -> AsyncGenerator[AsyncClient, None]:
    """Yield an HTTPX AsyncClient wired to the test app with overridden dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    def override_get_redis() -> Any:
        return test_redis

    app.dependency_overrides[get_db] = override_get_db
    # Override redis client used in dependencies
    import app.redis.client as redis_module
    original = redis_module.get_redis_client
    redis_module.get_redis_client = override_get_redis  # type: ignore[assignment]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    redis_module.get_redis_client = original


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create and return a test user."""
    from app.repositories.user import UserRepository
    repo = UserRepository(db)
    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        hashed_password=hash_password("TestPass1"),
        display_name="Test User",
        is_active=True,
    )
    return await repo.create(user)


@pytest_asyncio.fixture
async def test_room(db: AsyncSession, test_user: User) -> Room:
    """Create and return a test room owned by test_user."""
    from app.repositories.room import RoomRepository
    repo = RoomRepository(db)
    room = Room(
        id=str(uuid.uuid4()),
        name="Test Room",
        description="A test study room",
        invite_code="TESTCODE",
        is_public=True,
        max_participants=20,
        owner_id=str(test_user.id),
    )
    room = await repo.create(room)
    await repo.add_member(str(room.id), str(test_user.id))
    return room


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Return Authorization headers for the test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
