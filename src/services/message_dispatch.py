from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Message, Room
from services.bot_updates import enqueue_message_updates
from services.messages import (
    enrich_messages_with_authors,
    normalize_message_text,
    save_message,
    serialize_message,
)
from ws.manager import manager


async def publish_text_message(
    db: AsyncSession,
    *,
    username: str,
    room: str,
    text: str,
    reply_to_id: int | None = None,
) -> dict:
    # 1. Validate text
    text = normalize_message_text(
        text,
        allow_empty=False,
    )

    # 2. Resolve the room
    room_record = await db.scalar(
        select(Room).where(Room.name == room)
    )

    if room_record is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    # 3. Validate reply
    if reply_to_id is not None:
        reply_exists = await db.scalar(
            select(Message.id).where(
                Message.id == reply_to_id,
                Message.room == room,
            )
        )

        if reply_exists is None:
            raise HTTPException(
                status_code=400,
                detail="Reply message not found in this room",
            )

    # 4. Save message and updates atomically
    try:
        message = await save_message(
            db,
            username=username,
            room=room,
            text=text,
            content_type="text",
            reply_to_id=reply_to_id,
            commit=False,
        )

        await enqueue_message_updates(
            db,
            message=message,
            room=room_record,
        )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    # 5. Prepare WebSocket payload
    await enrich_messages_with_authors(
        db,
        [message],
    )

    payload = serialize_message(message)

    # 6. Notify connected users after commit
    await manager.broadcast_json(
        payload,
        room,
    )

    return payload
