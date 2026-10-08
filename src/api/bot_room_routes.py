from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user_model, get_db
from core.rate_limit import enforce_http_rate_limit_for_user
from models import Bot, BotRoomAccess, Room, User
from services.bot_updates import discard_bot_room_updates
from services.permissions import can_delete_room


router = APIRouter(prefix="/rooms", tags=["Room bots"])

class AddRoomBotRequest(BaseModel):
    username: str = Field(min_length=7, max_length=50)
    can_read_messages: bool = False
    can_send_messages: bool = False


class UpdateRoomBotRequest(BaseModel):
    can_read_messages: bool | None = None
    can_send_messages: bool | None = None


class RoomBotInfo(BaseModel):
    room_id: int
    bot_id: int
    username: str
    display_name: str | None
    is_active: bool
    can_read_messages: bool
    can_send_messages: bool


def room_bot_info(
    access: BotRoomAccess,
    bot: Bot,
    user: User,
) -> dict:
    return {
        "room_id": access.room_id,
        "bot_id": bot.id,
        "username": user.username,
        "display_name": user.display_name,
        "is_active": bot.is_active,
        "can_read_messages": access.can_read_messages,
        "can_send_messages": access.can_send_messages,
    }


async def require_room_manager(
    db: AsyncSession,
    room_id: int,
    user: User,
) -> Room:
    room = await db.get(Room, room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    if not can_delete_room(user, room):
        raise HTTPException(
            status_code=403,
            detail="Room creator or admin required",
        )

    return room


async def find_room_bot(
    db: AsyncSession,
    room_id: int,
    bot_id: int,
):
    result = await db.execute(
        select(BotRoomAccess, Bot, User)
        .join(Bot, Bot.id == BotRoomAccess.bot_id)
        .join(User, User.id == Bot.user_id)
        .where(
            BotRoomAccess.room_id == room_id,
            BotRoomAccess.bot_id == bot_id,
        )
    )
    return result.one_or_none()


@router.post(
    "/{room_id}/bots",
    response_model=RoomBotInfo,
    status_code=201,
)
async def add_room_bot(
    room_id: int,
    payload: AddRoomBotRequest,
    request: Request,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await require_room_manager(db, room_id, current_user)

    await enforce_http_rate_limit_for_user(
        request, "room_bots_manage", 30, 300, current_user
    )

    username = payload.username.strip().lower()

    result = await db.execute(
        select(Bot, User)
        .join(User, User.id == Bot.user_id)
        .where(
            func.lower(User.username) == username,
            User.is_bot.is_(True),
        )
    )
    row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Bot not found",
        )

    bot, bot_user = row

    existing = await db.scalar(
        select(BotRoomAccess.id).where(
            BotRoomAccess.room_id == room_id,
            BotRoomAccess.bot_id == bot.id,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Bot already in this room",
        )

    access = BotRoomAccess(
        room_id=room_id,
        bot_id=bot.id,
        can_read_messages=payload.can_read_messages,
        can_send_messages=payload.can_send_messages,
    )

    db.add(access)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot add bot",
        ) from exc

    return room_bot_info(access, bot, bot_user)


@router.get(
    "/{room_id}/bots",
    response_model=list[RoomBotInfo],
)
async def list_room_bots(
    room_id: int,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await require_room_manager(db, room_id, current_user)

    result = await db.execute(
        select(BotRoomAccess, Bot, User)
        .join(Bot, Bot.id == BotRoomAccess.bot_id)
        .join(User, User.id == Bot.user_id)
        .where(BotRoomAccess.room_id == room_id)
        .order_by(BotRoomAccess.id)
    )

    return [
        room_bot_info(access, bot, user)
        for access, bot, user in result.all()
    ]


@router.patch(
    "/{room_id}/bots/{bot_id}",
    response_model=RoomBotInfo,
)
async def update_room_bot(
    room_id: int,
    bot_id: int,
    payload: UpdateRoomBotRequest,
    request: Request,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await require_room_manager(db, room_id, current_user)

    await enforce_http_rate_limit_for_user(
        request, "room_bots_manage", 30, 300, current_user
    )

    if (
        payload.can_read_messages is None
        and payload.can_send_messages is None
    ):
        raise HTTPException(
            status_code=422,
            detail="No permissions to update",
        )

    row = await find_room_bot(db, room_id, bot_id)

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Bot not in this room",
        )

    access, bot, bot_user = row

    if payload.can_read_messages is not None:
        access.can_read_messages = payload.can_read_messages

        if payload.can_read_messages is False:
            await discard_bot_room_updates(
                db,
                bot_id=bot_id,
                room_id=room_id,
            )

    if payload.can_send_messages is not None:
        access.can_send_messages = payload.can_send_messages

    await db.commit()

    await db.commit()

    return room_bot_info(access, bot, bot_user)


@router.delete("/{room_id}/bots/{bot_id}")
async def remove_room_bot(
    room_id: int,
    bot_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    await require_room_manager(db, room_id, current_user)

    await enforce_http_rate_limit_for_user(
        request, "room_bots_manage", 30, 300, current_user
    )

    row = await find_room_bot(db, room_id, bot_id)

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Bot not in this room",
        )

    access, _, _ = row

    await discard_bot_room_updates(
        db,
        bot_id=bot_id,
        room_id=room_id,
    )

    await db.delete(access)
    await db.commit()

    return {
        "status": "removed",
        "room_id": room_id,
        "bot_id": bot_id,
    }
