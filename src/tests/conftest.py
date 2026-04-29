import os
import sys
from pathlib import Path

os.environ["SECRET_KEY"] = "test-secret-key"

SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

import main
from database import Base


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

    yield TestingSessionLocal, engine


@pytest.fixture()
def client(session_factory, tmp_path, monkeypatch):
    TestingSessionLocal, test_engine = session_factory

    async def override_get_db():
        async with TestingSessionLocal() as db:
            yield db

    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()

    monkeypatch.setattr(main, "engine", test_engine)
    monkeypatch.setattr(main, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(main, "UPLOADS_DIR", uploads_dir)

    main.app.dependency_overrides[main.get_db] = override_get_db
    main.room_members.clear()
    main.manager.active_connections.clear()
    main.rate_limiter.events.clear()

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()
    main.room_members.clear()
    main.manager.active_connections.clear()
    main.rate_limiter.events.clear()