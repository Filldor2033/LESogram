import mimetypes
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from core.config import *
from models import Message


def sanitize_filename(filename: str | None) -> str:
    original = Path(filename or "").name or "attachment"
    safe = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in original)
    safe = safe.strip(" .")
    if not safe:
        safe = "attachment"
    return safe[:255]


def determine_upload_content_type(filename: str, mime_type: str | None) -> str:
    mime = (
        mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    ).lower()
    ext = Path(filename).suffix.lower()

    if mime == "image/gif" or ext == ".gif":
        raise HTTPException(status_code=400, detail="GIF uploads are disabled")

    if ext in DANGEROUS_FILE_EXTENSIONS or mime in DANGEROUS_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type is not allowed")

    if mime in ALLOWED_IMAGE_MIME_TYPES:
        return "image"

    if mime in ALLOWED_VIDEO_MIME_TYPES:
        return "video"

    if ext in ALLOWED_FILE_EXTENSIONS:
        return "file"

    raise HTTPException(status_code=400, detail="File type is not allowed")


def build_attachment_path(media_url: str | None) -> Path | None:
    if not media_url or not media_url.startswith("/uploads/"):
        return None

    candidate = (UPLOADS_DIR / Path(media_url).name).resolve()
    try:
        candidate.relative_to(UPLOADS_DIR.resolve())
    except ValueError:
        return None

    return candidate


def remove_room_uploads(messages: list[Message]):
    for message in messages:
        candidate = build_attachment_path(message.media_url)
        if not candidate:
            continue

        if candidate.exists() and candidate.is_file():
            try:
                candidate.unlink()
            except OSError:
                pass


def validate_image_content(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )
