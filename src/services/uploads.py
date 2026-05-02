import mimetypes
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from core.config import *
from models import Message

OFFICE_MIME_BY_EXTENSION = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".doc": "application/msword",
    ".xls": "application/vnd.ms-excel",
    ".ppt": "application/vnd.ms-powerpoint",
}


def sanitize_filename(filename: str | None) -> str:
    original = Path(filename or "").name or "attachment"
    safe = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in original)
    safe = safe.strip(" .")

    if not safe:
        safe = "attachment"

    return safe[:255]


def detect_mime_by_magic(content: bytes) -> str | None:
    head = content[:512]

    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "image/gif"

    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    
    if head.startswith(b"ID3"):
        return "audio/mpeg"

    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
        return "audio/mpeg"

    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"

    if head.startswith(b"OggS"):
        return "audio/ogg"

    if head.startswith(b"fLaC"):
        return "audio/flac"

    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xF6) == 0xF0:
        return "audio/aac"

    if len(head) >= 12 and head[4:8] == b"ftyp":
        brand = head[8:12]

        if brand == b"qt  ":
            return "video/quicktime"

        if brand in {b"M4A ", b"M4B "}:
            return "audio/mp4"

        return "video/mp4"

    if head.startswith(b"%PDF-"):
        return "application/pdf"

    if head.startswith(b"PK\x03\x04") or head.startswith(b"PK\x05\x06") or head.startswith(b"PK\x07\x08"):
        return "application/zip"

    if head.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "application/x-7z-compressed"

    if head.startswith(b"Rar!\x1a\x07\x00") or head.startswith(b"Rar!\x1a\x07\x01\x00"):
        return "application/vnd.rar"

    if head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "application/octet-stream"

    try:
        content[:4096].decode("utf-8")
        return "text/plain"
    except UnicodeDecodeError:
        return None


def validate_upload_file_type(
    filename: str,
    declared_mime: str | None,
    content: bytes,
) -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    declared_mime = (declared_mime or "").split(";")[0].lower().strip()

    if ext in DANGEROUS_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File extension is not allowed")

    detected_mime = detect_mime_by_magic(content)

    if not detected_mime:
        raise HTTPException(status_code=400, detail="Unknown or unsupported file type")

    if detected_mime in DANGEROUS_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type is not allowed")

    if detected_mime in ALLOWED_IMAGE_MIME_TYPES:
        return detected_mime, "image"

    if detected_mime in ALLOWED_VIDEO_MIME_TYPES:
        return detected_mime, "video"
    
    if detected_mime in ALLOWED_AUDIO_MIME_TYPES:
        return detected_mime, "file"

    guessed_mime = OFFICE_MIME_BY_EXTENSION.get(ext)

    if guessed_mime is None:
        guessed_mime = (
            mimetypes.guess_type(filename)[0] or "application/octet-stream"
        ).lower()

    if ext in {".docx", ".xlsx", ".pptx"} and detected_mime == "application/zip":
        return guessed_mime, "file"

    if ext in {".doc", ".xls", ".ppt"} and detected_mime == "application/octet-stream":
        return guessed_mime, "file"

    if ext in ALLOWED_FILE_EXTENSIONS and detected_mime in ALLOWED_FILE_MIME_TYPES:
        return detected_mime, "file"

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

        with Image.open(BytesIO(content)) as image:
            width, height = image.size

            if width <= 0 or height <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image dimensions",
                )

            if width * height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image is too large",
                )

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )
