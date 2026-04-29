from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import UPLOADS_DIR
from core.schema_migrations import ensure_message_schema, ensure_user_schema
from database import Base, engine
from core.rate_limit import rate_limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await ensure_user_schema()
    await ensure_message_schema()

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    rate_limiter.start_cleanup()

    yield

    await rate_limiter.stop_cleanup()
    await engine.dispose()
