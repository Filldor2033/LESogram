from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_token
from database import SessionLocal
from models import User


async def get_db():
    async with SessionLocal() as db:
        yield db


bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme
    ),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing token",
        )

    username = verify_token(credentials.credentials)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    return username


async def get_current_user_model(
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or user.is_bot:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
