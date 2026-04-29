import asyncio
import mimetypes
import secrets

from fastapi import APIRouter, Depends, File, Form, Request, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_user_model
from core.config import *
from core.rate_limit import enforce_http_rate_limit, enforce_http_rate_limit_for_user
from services.messages import normalize_message_text, save_message, serialize_message
from services.rooms import require_room_access
from models import Message, User
from services.uploads import (
    build_attachment_path,
    determine_upload_content_type,
    sanitize_filename,
    validate_image_content,
)
from ws.manager import manager

router = APIRouter()


@router.get("/attachments/{message_id}")
async def get_attachment(
    message_id: int,
    room_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "get_attachment", 240, 60)

    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()

    if not message or not message.media_url:
        raise HTTPException(status_code=404, detail="Attachment not found")

    username = await require_room_access(message.room, room_token, db)
    del username

    file_path = build_attachment_path(message.media_url)
    if not file_path or not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Attachment not found")

    disposition = (
        "inline" if message.content_type in {"image", "video"} else "attachment"
    )

    response = FileResponse(
        file_path,
        media_type=message.mime_type or "application/octet-stream",
        filename=message.file_name or file_path.name,
        content_disposition_type=disposition,
    )

    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


@router.post("/rooms/{room}/attachments")
async def upload_attachment(
    room: str,
    request: Request,
    room_token: str = Form(...),
    text: str = Form(default=""),
    reply_to_id: int | None = Form(default=None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(
        request,
        "upload_attachment",
        20,
        300,
        current_user,
    )

    username = await require_room_access(room, room_token, db)
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="No access to this room")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Attachment is missing a file name")

    caption = normalize_message_text(text, allow_empty=True)
    safe_filename = sanitize_filename(file.filename)

    mime_type = (
        file.content_type
        or mimetypes.guess_type(safe_filename)[0]
        or "application/octet-stream"
    ).lower()

    content_type = determine_upload_content_type(safe_filename, mime_type)

    content = await file.read(MAX_UPLOAD_SIZE + 1)
    await file.close()

    if not content:
        raise HTTPException(status_code=400, detail="Attachment is empty")

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Attachment is too large. Max size is {MAX_UPLOAD_SIZE // (1024 * 1024)} MB",
        )

    if content_type == "image":
        validate_image_content(content)

    suffix = Path(safe_filename).suffix[:20]
    stored_name = f"{secrets.token_hex(16)}{suffix}"
    stored_path = UPLOADS_DIR / stored_name

    await asyncio.to_thread(stored_path.write_bytes, content)
    
    if reply_to_id is not None:
        reply_result = await db.execute(
            select(Message).where(
                Message.id == reply_to_id,
                Message.room == room,
            )
        )

        if not reply_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Reply message not found")

    message = await save_message(
        db,
        username=username,
        room=room,
        text=caption,
        content_type=content_type,
        media_url=f"/uploads/{stored_name}",
        file_name=safe_filename,
        mime_type=mime_type,
        file_size=len(content),
        reply_to_id=reply_to_id,
    )

    payload = serialize_message(message)
    await manager.broadcast_json(payload, room)

    return payload
