from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_user_model
from core.rate_limit import enforce_http_rate_limit
from auth import create_access_token, hash_password, verify_password
from models import User
from schemas import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter()


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user_model),
):
    return {
        "username": current_user.username,
        "is_admin": bool(current_user.is_admin),
    }


@router.post("/register")
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "register", 8, 60)

    username = payload.username.strip()

    result = await db.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=username,
        hashed_password=hash_password(payload.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "login", 10, 60)

    username = payload.username.strip()

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)
