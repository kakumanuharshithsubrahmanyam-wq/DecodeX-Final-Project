import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.entities import Department, GrievanceCategory, Profile, SLAPolicy
from app.models.enums import PriorityLevel, UserRole

TEST_DB = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        TEST_DB,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession):
    citizen_id = uuid.uuid4()
    officer_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    other_citizen = uuid.uuid4()
    db_session.add(
        Profile(id=citizen_id, email="citizen@test.com", role=UserRole.citizen, full_name="Citizen")
    )
    db_session.add(
        Profile(id=officer_id, email="officer@test.com", role=UserRole.officer, full_name="Officer")
    )
    db_session.add(
        Profile(
            id=admin_id,
            email="admin@test.com",
            role=UserRole.platform_administrator,
            full_name="Admin",
        )
    )
    db_session.add(
        Profile(id=other_citizen, email="other@test.com", role=UserRole.citizen, full_name="Other")
    )
    san = Department(name="Sanitation", code="SAN", description="San")
    road = Department(name="Roads", code="ROAD", description="Roads")
    db_session.add(san)
    db_session.add(road)
    await db_session.flush()
    from app.models.entities import DepartmentOfficer

    db_session.add(DepartmentOfficer(department_id=san.id, officer_id=officer_id))
    db_session.add(
        GrievanceCategory(code="SANITATION", name="Sanitation", default_department_id=san.id, sort_order=1)
    )
    db_session.add(SLAPolicy(name="Default medium", priority=PriorityLevel.medium, first_response_hours=48, resolution_hours=168))
    await db_session.commit()
    return {
        "citizen_id": citizen_id,
        "officer_id": officer_id,
        "admin_id": admin_id,
        "other_citizen": other_citizen,
        "san_id": san.id,
        "road_id": road.id,
    }


@pytest_asyncio.fixture(autouse=True)
def reset_auth_user(monkeypatch, seed_data):
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed_data["citizen_id"]))
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client(engine, session_factory, seed_data, monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", TEST_DB)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_DEV_BYPASS", "true")
    monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed_data["citizen_id"]))
    monkeypatch.setenv("AUTH_DEV_ROLE", "citizen")
    get_settings.cache_clear()

    import app.db.session as db_session_module

    db_session_module.engine = engine
    db_session_module.AsyncSessionLocal = session_factory

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, seed_data
        monkeypatch.setenv("AUTH_DEV_USER_ID", str(seed_data["citizen_id"]))
        get_settings.cache_clear()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def auth_headers(user_id: uuid.UUID):
    get_settings.cache_clear()
    import os

    os.environ["AUTH_DEV_USER_ID"] = str(user_id)
    get_settings.cache_clear()
    return {"Authorization": "Bearer test-token"}
