import sys
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import UPLOADS_DIR
from core.rate_limit import rate_limiter
from core.schema_migrations import ensure_message_schema, ensure_user_schema
from database import Base, engine


def _silence_proactor_pipe_errors(loop, context):
    exception = context.get("exception")
    if isinstance(exception, ConnectionResetError):
        return
    loop.default_exception_handler(context)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().set_exception_handler(_silence_proactor_pipe_errors)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await ensure_user_schema()
    await ensure_message_schema()

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    rate_limiter.start_cleanup()

    yield

    await rate_limiter.stop_cleanup()
    await engine.dispose()
