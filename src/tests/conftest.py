import asyncio
import os
import sys
from pathlib import Path

os.environ["SECRET_KEY"] = "test-secret-key"

SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import api.deps as deps
import core.lifespan as lifespan_module
import core.schema_migrations as schema_migrations
import main
import services.uploads as uploads_module
import ws.routes as ws_routes
from core.rate_limit import rate_limiter
from models import Base
from services.rooms import room_members
from ws.manager import manager


@pytest.fixture()
def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())

    yield TestingSessionLocal, engine

    asyncio.run(engine.dispose())


@pytest.fixture()
def client(session_factory, tmp_path, monkeypatch):
    TestingSessionLocal, test_engine = session_factory

    async def override_get_db():
        async with TestingSessionLocal() as db:
            yield db

    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()

    monkeypatch.setattr(lifespan_module, "engine", test_engine)
    monkeypatch.setattr(schema_migrations, "engine", test_engine)
    monkeypatch.setattr(uploads_module, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(ws_routes, "SessionLocal", TestingSessionLocal)

    main.app.dependency_overrides[deps.get_db] = override_get_db

    room_members.clear()
    manager.active_connections.clear()
    rate_limiter.events.clear()

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()
    room_members.clear()
    manager.active_connections.clear()
    rate_limiter.events.clear()
