import asyncio
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.bot_deps import get_current_bot
from api.deps import get_db
from core.rate_limit import rate_limiter
from models import Bot, BotRoomAccess, Room, User
from services.bot_updates import fetch_updates_for_bot
from services.message_dispatch import publish_text_message
from utils.time import utc_now


router = APIRouter(
    prefix="/bot",
    tags=["Bot API"],
)


class BotProfile(BaseModel):
    id: int
    bot_id: int
    is_bot: bool
    username: str
    display_name: str | None
    description: str | None


class GetMeResponse(BaseModel):
    ok: bool
    result: BotProfile


class SendMessageRequest(BaseModel):
    chat_id: int = Field(gt=0)
    text: str
    reply_to_id: int | None = Field(
        default=None,
        gt=0,
    )


class SentMessageInfo(BaseModel):
    message_id: int
    chat_id: int
    username: str
    text: str
    timestamp: str
    reply_to_id: int | None


class SendMessageResponse(BaseModel):
    ok: bool
    result: SentMessageInfo


class GetUpdatesRequest(BaseModel):
    offset: int = Field(
        default=0,
        ge=0,
        le=9223372036854775807,
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=100,
    )

    timeout: int = Field(
        default=0,
        ge=0,
        le=30,
    )


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[dict]


@router.get(
    "/getMe",
    response_model=GetMeResponse,
)
async def get_me(
    response: Response,
    bot: Bot = Depends(get_current_bot),
    db: AsyncSession = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"

    bot_user = await db.get(User, bot.user_id)

    if bot_user is None or not bot_user.is_bot:
        raise HTTPException(
            status_code=401,
            detail="Invalid bot token",
        )

    return {
        "ok": True,
        "result": {
            "id": bot_user.id,
            "bot_id": bot.id,
            "is_bot": True,
            "username": bot_user.username,
            "display_name": bot_user.display_name,
            "description": bot_user.bio,
        },
    }


@router.post(
    "/sendMessage",
    response_model=SendMessageResponse,
)
async def send_message(
    payload: SendMessageRequest,
    response: Response,
    bot: Bot = Depends(get_current_bot),
    db: AsyncSession = Depends(get_db),
):
    # 1. Find the target room
    room = await db.get(Room, payload.chat_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    # 2. Check permission to send
    can_send = await db.scalar(
        select(BotRoomAccess.id).where(
            BotRoomAccess.bot_id == bot.id,
            BotRoomAccess.room_id == room.id,
            BotRoomAccess.can_send_messages.is_(True),
        )
    )

    if can_send is None:
        raise HTTPException(
            status_code=403,
            detail="Bot cannot send to this room",
        )

    # 3. Rate limit per bot: 30 messages / minute
    retry_after = await rate_limiter.hit(
        "bot_send_message",
        str(bot.id),
        30,
        60,
    )

    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(retry_after),
            },
        )

    # 4. Resolve the bot's user account
    bot_user = await db.get(User, bot.user_id)

    if bot_user is None or not bot_user.is_bot:
        raise HTTPException(
            status_code=401,
            detail="Invalid bot token",
        )

    # 5. Save and broadcast the message
    message = await publish_text_message(
        db,
        username=bot_user.username,
        room=room.name,
        text=payload.text,
        reply_to_id=payload.reply_to_id,
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "ok": True,
        "result": {
            "message_id": message["id"],
            "chat_id": room.id,
            "username": message["username"],
            "text": message["text"],
            "timestamp": message["timestamp"],
            "reply_to_id": message["reply_to_id"],
        },
    }


@router.post(
    "/getUpdates",
    response_model=GetUpdatesResponse,
)
async def get_updates(
    payload: GetUpdatesRequest,
    response: Response,
    bot: Bot = Depends(get_current_bot),
    db: AsyncSession = Depends(get_db),
):
    # Save identifiers before any rollback
    # (ORM objects may become expired).
    bot_id = bot.id
    expected_hash = bot.token_hash

    # Request rate limit per bot
    retry_after = await rate_limiter.hit(
        "bot_get_updates",
        str(bot_id),
        120,
        60,
    )

    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many getUpdates requests",
            headers={
                "Retry-After": str(retry_after),
            },
        )

    response.headers["Cache-Control"] = "no-store"

    loop = asyncio.get_running_loop()

    # Monotonic deadline avoids system clock changes
    deadline = loop.time() + payload.timeout

    first_poll = True

    # Retain up to seven days of updates
    cleanup_before = utc_now() - timedelta(days=7)

    while True:
        updates = await fetch_updates_for_bot(
            db,
            bot_id=bot_id,
            expected_token_hash=expected_hash,
            offset=payload.offset,
            limit=payload.limit,
            acknowledge=first_poll,
            cleanup_before=(
                cleanup_before if first_poll else None
            ),
        )

        first_poll = False

        # Token rotated or bot disabled
        if updates is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid bot token",
            )

        # We found events or reached the timeout
        if updates or loop.time() >= deadline:
            return {
                "ok": True,
                "result": updates,
            }

        # Wait without holding a DB transaction
        await asyncio.sleep(
            min(0.5, deadline - loop.time())
        )
