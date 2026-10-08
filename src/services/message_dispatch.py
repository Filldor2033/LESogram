from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Message
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
    # Validate message text
    text = normalize_message_text(
        text,
        allow_empty=False,
    )

    # Replies must reference messages from the same room
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

    # Save the message
    message = await save_message(
        db,
        username=username,
        room=room,
        text=text,
        content_type="text",
        reply_to_id=reply_to_id,
    )

    # Add author profile information
    await enrich_messages_with_authors(
        db,
        [message],
    )

    # Prepare the existing LESogram WebSocket format
    payload = serialize_message(message)

    # Notify connected clients
    await manager.broadcast_json(
        payload,
        room,
    )

    return payload
