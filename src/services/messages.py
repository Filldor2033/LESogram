from fastapi import HTTPException

from core.config import MAX_MESSAGE_LENGTH
from models import Message


def normalize_message_text(text: str | None, *, allow_empty: bool) -> str:
    normalized = (text or "").strip()

    if len(normalized) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message must be at most {MAX_MESSAGE_LENGTH} characters",
        )

    if not normalized and not allow_empty:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return normalized


def serialize_message(message: Message) -> dict:
    attachment_url = f"/attachments/{message.id}" if message.media_url else None

    return {
        "id": message.id,
        "type": "message",
        "username": message.username,
        "text": message.text or "",
        "room": message.room,
        "timestamp": message.timestamp.isoformat(),
        "content_type": message.content_type or "text",
        "media_url": attachment_url,
        "file_name": message.file_name,
        "mime_type": message.mime_type,
        "file_size": message.file_size,
        "reply_to_id": message.reply_to_id
    }


async def save_message(
    db,
    *,
    username: str,
    room: str,
    text: str = "",
    content_type: str = "text",
    media_url: str | None = None,
    file_name: str | None = None,
    mime_type: str | None = None,
    file_size: int | None = None,
    reply_to_id: int | None = None,
) -> Message:
    message = Message(
        username=username,
        room=room,
        text=text,
        content_type=content_type,
        media_url=media_url,
        file_name=file_name,
        mime_type=mime_type,
        file_size=file_size,
        reply_to_id=reply_to_id
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message
