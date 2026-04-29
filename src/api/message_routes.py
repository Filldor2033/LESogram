from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user_model, get_db
from core.rate_limit import enforce_http_rate_limit, enforce_http_rate_limit_for_user
from models import Message, User
from schemas import EditMessageRequest
from services.messages import normalize_message_text, serialize_message
from services.permissions import can_delete_message
from services.rooms import require_room_access
from services.uploads import build_attachment_path
from utils.time import utc_now
from ws.manager import manager

router = APIRouter()


@router.get("/messages/{room}")
async def get_messages(
    room: str,
    room_token: str,
    request: Request,
    before_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "get_messages", 120, 60)

    username = await require_room_access(room, room_token, db)
    del username

    query = select(Message).where(Message.room == room)

    if before_id is not None:
        query = query.where(Message.id < before_id)

    query = query.order_by(Message.id.desc()).limit(limit + 1)

    result = await db.execute(query)
    messages = list(result.scalars().all())

    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()

    next_before_id = messages[0].id if messages else None

    return {
        "messages": [serialize_message(message) for message in messages],
        "has_more": has_more,
        "next_before_id": next_before_id,
    }


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit(request, "delete_message", 60, 60)

    if not can_delete_message(current_user):
        raise HTTPException(status_code=403, detail="Only admins can delete messages")

    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    room_name = message.room
    deleted_message_id = message.id

    file_path = build_attachment_path(message.media_url)
    if file_path and file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except OSError:
            pass

    await db.delete(message)
    await db.commit()

    await manager.broadcast_json(
        {
            "type": "message_deleted",
            "room": room_name,
            "message_id": deleted_message_id,
            "deleted_by": current_user.username,
            "timestamp": utc_now().isoformat(),
        },
        room_name,
    )

    return {
        "status": "deleted",
        "message_id": deleted_message_id,
    }


@router.patch("/messages/{message_id}")
async def edit_message(
    message_id: int,
    payload: EditMessageRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(
        request,
        "edit_message",
        60,
        60,
        current_user,
    )

    new_text = normalize_message_text(payload.text, allow_empty=False)

    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="Only the author can edit this message",
        )

    message.text = new_text
    message.edited_at = utc_now()

    await db.commit()
    await db.refresh(message)

    payload_data = {
        "type": "message_edited",
        "room": message.room,
        "message": serialize_message(message),
        "timestamp": utc_now().isoformat(),
    }

    await manager.broadcast_json(payload_data, message.room)

    return payload_data
