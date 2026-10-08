from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user_model, get_db
from core.rate_limit import enforce_http_rate_limit
from models import Bot, User
from services.bots import (
    BotUsernameTaken,
    create_bot as create_bot_account,
    list_owned_bots,
    rotate_bot_token as rotate_bot_secret,
    set_bot_active,
)


router = APIRouter(prefix="/bots", tags=["Bots"])

MAX_BOTS_PER_USER = 3

class CreateBotRequest(BaseModel):
    username: str = Field(min_length=7, max_length=50)
    display_name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(
        default=None,
        max_length=200,
    )


class BotInfo(BaseModel):
    id: int
    username: str
    display_name: str | None
    description: str | None
    is_active: bool
    created_at: datetime


class BotCreated(BotInfo):
    token: str


class BotTokenResponse(BaseModel):
    bot_id: int
    token: str


class ChangeBotStatusRequest(BaseModel):
    is_active: bool


class BotStatusResponse(BaseModel):
    bot_id: int
    is_active: bool


def bot_info(bot: Bot, bot_user: User) -> dict:
    return {
        "id": bot.id,
        "username": bot_user.username,
        "display_name": bot_user.display_name,
        "description": bot_user.bio,
        "is_active": bot.is_active,
        "created_at": bot.created_at,
    }


@router.post("", response_model=BotCreated, status_code=201)
async def create_bot(
    payload: CreateBotRequest,
    request: Request,
    response: Response,
    owner: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await enforce_http_rate_limit(
        request, "bot_create", 5, 3600
    )

    count = await db.scalar(
        select(func.count(Bot.id)).where(
            Bot.owner_id == owner.id
        )
    )

    if count >= MAX_BOTS_PER_USER:
        raise HTTPException(
            status_code=403,
            detail="Bot limit reached",
        )

    try:
        bot, token = await create_bot_account(
            db,
            owner=owner,
            username=payload.username,
            display_name=payload.display_name,
            description=payload.description,
        )
    except BotUsernameTaken:
        raise HTTPException(
            status_code=409,
            detail="Username already taken",
        ) from None
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    bot_user = await db.get(User, bot.user_id)

    response.headers["Cache-Control"] = "no-store"

    return {
        **bot_info(bot, bot_user),
        "token": token,
    }


@router.get("", response_model=list[BotInfo])
async def list_bots(
    owner: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_owned_bots(db, owner.id)

    return [
        bot_info(bot, user)
        for bot, user in rows
    ]


@router.post(
    "/{bot_id}/rotate-token",
    response_model=BotTokenResponse,
)
async def rotate_bot_token(
    bot_id: int,
    request: Request,
    response: Response,
    owner: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await enforce_http_rate_limit(
        request, "bot_rotate", 10, 3600
    )

    token = await rotate_bot_secret(
        db,
        owner_id=owner.id,
        bot_id=bot_id,
    )

    if token is None:
        raise HTTPException(
            status_code=404,
            detail="Bot not found",
        )

    response.headers["Cache-Control"] = "no-store"

    return {
        "bot_id": bot_id,
        "token": token,
    }


@router.patch(
    "/{bot_id}/status",
    response_model=BotStatusResponse,
)
async def change_bot_status(
    bot_id: int,
    payload: ChangeBotStatusRequest,
    owner: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    changed = await set_bot_active(
        db,
        owner_id=owner.id,
        bot_id=bot_id,
        enabled=payload.is_active,
    )

    if not changed:
        raise HTTPException(
            status_code=404,
            detail="Bot not found",
        )

    return {
        "bot_id": bot_id,
        "is_active": payload.is_active,
    }
