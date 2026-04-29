import os
import time
import asyncio
import secrets
import mimetypes

from pathlib import Path
from threading import Lock
from typing import Optional
from urllib.parse import urlparse
from collections import Counter, defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth import ALGORITHM, SECRET_KEY, create_access_token, hash_password, verify_password, verify_token
from database import SessionLocal, engine
from models import Base, Message, Room, User
from schemas import (
    CreateRoomRequest,
    JoinRoomRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

MAX_MESSAGE_LENGTH = 1000
MAX_UPLOAD_SIZE = 20 * 1024 * 1024

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
}
ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
    "video/mpeg",
    "video/ogg",
}
ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".csv",
    ".json",
    ".zip",
    ".7z",
    ".rar",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
}
DANGEROUS_FILE_EXTENSIONS = {
    ".apk",
    ".app",
    ".bat",
    ".cmd",
    ".com",
    ".dll",
    ".exe",
    ".hta",
    ".html",
    ".htm",
    ".iso",
    ".jar",
    ".js",
    ".jse",
    ".mjs",
    ".msi",
    ".php",
    ".ps1",
    ".py",
    ".scr",
    ".sh",
    ".svg",
    ".vbs",
    ".xhtml",
}
DANGEROUS_MIME_TYPES = {
    "application/javascript",
    "application/x-msdownload",
    "text/html",
    "text/javascript",
    "image/svg+xml",
}

def utc_now():
    return datetime.now(timezone.utc)

class SlidingWindowRateLimiter:
    def __init__(self, cleanup_interval: int = 60, fallback_window: int = 300):
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.key_windows: dict[str, int] = {}
        self.lock = Lock()
        self.cleanup_interval = cleanup_interval
        self.fallback_window = fallback_window
        self._cleanup_task: Optional[asyncio.Task] = None

    def hit(self, bucket: str, identifier: str, limit: int, window_seconds: int) -> int | None:
        now = time.monotonic()
        key = f"{bucket}:{identifier}"

        with self.lock:
            self.key_windows[key] = window_seconds
            entries = self.events[key]

            while entries and now - entries[0] > window_seconds:
                entries.popleft()

            if len(entries) >= limit:
                retry_after = max(1, int(window_seconds - (now - entries[0])) + 1)
                return retry_after

            entries.append(now)

        return None

    async def _cleanup_loop(self):
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
            except asyncio.CancelledError:
                break

    def _cleanup_expired(self):
        now = time.monotonic()
        with self.lock:
            keys_to_remove = []
            for key, entries in self.events.items():
                window = self.key_windows.get(key, self.fallback_window)
                while entries and now - entries[0] > window:
                    entries.popleft()
                if not entries:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.events[key]
                self.key_windows.pop(key, None)

    def start_cleanup(self):
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def stop_cleanup(self):
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


rate_limiter = SlidingWindowRateLimiter(cleanup_interval=120)

async def ensure_user_schema():
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in result.fetchall()}

        if "users" not in tables:
            return

        result = await conn.exec_driver_sql("PRAGMA table_info(users)")
        columns = {row["name"] for row in result.mappings().all()}

        if "is_admin" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"
            )

async def ensure_message_schema():
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in result.fetchall()}

        if "messages" not in tables:
            return

        result = await conn.exec_driver_sql("PRAGMA table_info(messages)")
        columns = {row["name"] for row in result.mappings().all()}

        if "content_type" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN content_type VARCHAR(20) NOT NULL DEFAULT 'text'"
            )

        if "media_url" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN media_url VARCHAR(500)"
            )

        if "file_name" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_name VARCHAR(255)"
            )

        if "mime_type" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN mime_type VARCHAR(255)"
            )

        if "file_size" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_size INTEGER"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await ensure_user_schema()
    await ensure_message_schema()

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    rate_limiter.start_cleanup()

    yield

    rate_limiter.stop_cleanup()


app = FastAPI(title="Realtime Chat", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self' ws: wss:; "
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none';"
    )

    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    if request.url.path in {"/login", "/register", "/rooms/join"}:
        response.headers["Cache-Control"] = "no-store"

    return response


async def get_db():
    async with SessionLocal() as db:
        yield db


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


async def get_current_user_model(
    username: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def get_client_ip_from_request(request: Request) -> str:
    return request.client.host if request.client and request.client.host else "unknown"


def get_client_ip_from_websocket(websocket: WebSocket) -> str:
    return websocket.client.host if websocket.client and websocket.client.host else "unknown"


def enforce_http_rate_limit(request: Request, bucket: str, limit: int, window_seconds: int):
    retry_after = rate_limiter.hit(bucket, get_client_ip_from_request(request), limit, window_seconds)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Retry in {retry_after} seconds",
        )


def enforce_http_rate_limit_for_user(
    request: Request,
    bucket: str,
    limit: int,
    window_seconds: int,
    user: User,
):
    if user.is_admin:
        return

    enforce_http_rate_limit(request, bucket, limit, window_seconds)


def enforce_websocket_rate_limit(websocket: WebSocket, bucket: str, identifier: str, limit: int, window_seconds: int) -> bool:
    retry_after = rate_limiter.hit(bucket, identifier, limit, window_seconds)
    return retry_after is None


class ConnectionManager:
    def __init__(self, concurrent_threshold: int = 10):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.concurrent_threshold = concurrent_threshold

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_json(self, data: dict, room: str):
        connections = [
            conn for conn in self.active_connections.get(room, [])
            if conn.client_state == WebSocketState.CONNECTED
        ]

        if not connections:
            return

        if len(connections) < self.concurrent_threshold:
            dead = await self._broadcast_sequential(data, room, connections)
        else:
            dead = await self._broadcast_concurrent(data, room, connections)

        for conn in dead:
            self.disconnect(conn, room)

    async def _broadcast_sequential(
        self,
        data: dict,
        room: str,
        connections: list[WebSocket],
    ) -> list[WebSocket]:
        dead = []

        for conn in connections:
            ok = await self._send_safe(conn, data)
            if not ok:
                dead.append(conn)

        return dead

    async def _broadcast_concurrent(
        self,
        data: dict,
        room: str,
        connections: list[WebSocket],
    ) -> list[WebSocket]:
        dead = []

        async with asyncio.TaskGroup() as tg:
            for conn in connections:
                tg.create_task(
                    self._send_and_track(conn, data, dead)
                )

        return dead

    async def _send_and_track(
        self,
        websocket: WebSocket,
        data: dict,
        dead_list: list[WebSocket],
    ):
        ok = await self._send_safe(websocket, data)
        if not ok:
            dead_list.append(websocket)

    async def _send_safe(
        self,
        websocket: WebSocket,
        data: dict,
    ) -> bool:
        try:
            await asyncio.wait_for(websocket.send_json(data), timeout=5.0)
            return True
        except (
            WebSocketDisconnect,
            ConnectionResetError,
            asyncio.TimeoutError,
            OSError,
            RuntimeError,
        ):
            return False

    async def close_room(self, room: str, code: int = 1008):
        connections = list(self.active_connections.get(room, []))
        for connection in connections:
            try:
                await connection.close(code=code)
            except Exception:
                pass
        self.active_connections.pop(room, None)


manager = ConnectionManager()

# room -> set(username)
room_members: dict[str, Counter[str]] = defaultdict(Counter)


def verify_room_token(token: str | None, room: str) -> str | None:
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "room_access":
            return None
        if payload.get("room") != room:
            return None
        return payload.get("sub")
    except JWTError:
        return None


async def require_room_access(room: str, room_token: str, db: AsyncSession):
    username = verify_room_token(room_token, room)
    if not username:
        raise HTTPException(status_code=403, detail="No access to this room")

    result = await db.execute(select(Room).where(Room.name == room))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Room not found")

    return username


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


def sanitize_filename(filename: str | None) -> str:
    original = Path(filename or "").name or "attachment"
    safe = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in original)
    safe = safe.strip(" .")
    if not safe:
        safe = "attachment"
    return safe[:255]


def determine_upload_content_type(filename: str, mime_type: str | None) -> str:
    mime = (mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream").lower()
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
    }


def build_system_payload(room: str, actor: str, event: str) -> dict:
    fallback_text = f"{actor} {event}"
    return {
        "type": "system",
        "text": fallback_text,
        "room": room,
        "timestamp": utc_now().isoformat(),
        "system_event": event,
        "system_actor": actor,
    }


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


async def save_message(
    db: AsyncSession,
    *,
    username: str,
    room: str,
    text: str = "",
    content_type: str = "text",
    media_url: str | None = None,
    file_name: str | None = None,
    mime_type: str | None = None,
    file_size: int | None = None,
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
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


def websocket_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host")

    if not origin or not host:
        return True

    parsed = urlparse(origin)
    origin_host = parsed.netloc.lower()
    return origin_host == host.lower()

@app.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user_model),
):
    return {
        "username": current_user.username,
        "is_admin": bool(current_user.is_admin),
    }


@app.post("/register")
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "register", 8, 60)

    username = payload.username.strip()

    result = await db.execute(
        select(User).where(User.username == username)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=username,
        hashed_password=hash_password(payload.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@app.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "login", 10, 60)

    username = payload.username.strip()

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@app.get("/rooms")
async def list_rooms(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(get_current_user),
):
    del username
    enforce_http_rate_limit(request, "list_rooms", 120, 60)

    result = await db.execute(
        select(Room).order_by(Room.created_at.desc())
    )
    rooms = result.scalars().all()

    return [
        {
            "name": room.name,
            "created_by": room.created_by,
            "created_at": room.created_at.isoformat(),
            "online": len(room_members.get(room.name, {})),
        }
        for room in rooms
    ]


@app.post("/rooms")
async def create_room(
    payload: CreateRoomRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(
        request,
        "create_room",
        20,
        300,
        current_user,
    )

    room_name = payload.name.strip()

    result = await db.execute(
        select(Room).where(Room.name == room_name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")

    room = Room(
        name=room_name,
        password_hash=hash_password(payload.password),
        created_by=current_user.username,
    )

    db.add(room)
    await db.commit()

    return {"status": "created", "room": room_name}


@app.get("/rooms/{room}/users")
async def list_room_users(
    room: str,
    room_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "list_room_users", 120, 60)

    username = await require_room_access(room, room_token, db)
    del username

    result = await db.execute(
        select(Room).where(Room.name == room)
    )
    existing_room = result.scalar_one_or_none()

    if not existing_room:
        raise HTTPException(status_code=404, detail="Room not found")

    usernames = sorted(room_members.get(room, {}).keys(), key=str.lower)

    admin_map = {}

    if usernames:
        result = await db.execute(
            select(User.username, User.is_admin)
            .where(User.username.in_(usernames))
        )
        rows = result.all()

        admin_map = {
            row.username: bool(row.is_admin)
            for row in rows
        }

    users = [
        {
            "username": name,
            "is_admin": admin_map.get(name, False),
        }
        for name in usernames
    ]

    return {
        "room": room,
        "count": len(users),
        "users": users,
    }


@app.delete("/rooms/{room_name}")
async def delete_room(
    room_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(
        request,
        "delete_room",
        10,
        300,
        current_user,
    )

    result = await db.execute(
        select(Room).where(Room.name == room_name)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.created_by != current_user.username and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only the creator or admin can delete this room",
        )

    result = await db.execute(
        select(Message).where(Message.room == room_name)
    )
    messages = list(result.scalars().all())

    remove_room_uploads(messages)

    await db.execute(
        delete(Message).where(Message.room == room_name)
    )

    await db.delete(room)
    await db.commit()

    await manager.broadcast_json(
        build_system_payload(room_name, current_user.username, "room_deleted"),
        room_name,
    )
    await asyncio.sleep(0)
    await manager.close_room(room_name)

    room_members.pop(room_name, None)
    await manager.close_room(room_name)

    return {"status": "deleted", "room": room_name}


@app.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit(request, "delete_message", 60, 60)

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete messages")

    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
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


@app.post("/rooms/join")
async def join_room(
    payload: JoinRoomRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(
        request,
        "join_room",
        30,
        300,
        current_user
    )

    room_name = payload.room.strip()

    result = await db.execute(
        select(Room).where(Room.name == room_name)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not current_user.is_admin:
        if not verify_password(payload.password, room.password_hash):
            raise HTTPException(status_code=403, detail="Wrong room password")

    access_token = create_access_token({
        "sub": current_user.username,
        "room": room_name,
        "type": "room_access",
    })

    return {
        "status": "ok",
        "room": room_name,
        "room_token": access_token,
    }


@app.get("/messages/{room}")
async def get_messages(
    room: str,
    room_token: str,
    request: Request,
    before_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "get_messages", 120, 60)

    username = await require_room_access(room,room_token,db)
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


@app.get("/attachments/{message_id}")
async def get_attachment(
    message_id: int,
    room_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "get_attachment", 240, 60)

    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if not message or not message.media_url:
        raise HTTPException(status_code=404, detail="Attachment not found")

    username = await require_room_access(message.room, room_token, db)
    del username

    file_path = build_attachment_path(message.media_url)
    if not file_path or not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Attachment not found")

    disposition = "inline" if message.content_type in {"image", "video"} else "attachment"

    response = FileResponse(
        file_path,
        media_type=message.mime_type or "application/octet-stream",
        filename=message.file_name or file_path.name,
        content_disposition_type=disposition,
    )

    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


@app.post("/rooms/{room}/attachments")
async def upload_attachment(
    room: str,
    request: Request,
    room_token: str = Form(...),
    text: str = Form(default=""),
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

    suffix = Path(safe_filename).suffix[:20]
    stored_name = f"{secrets.token_hex(16)}{suffix}"
    stored_path = UPLOADS_DIR / stored_name

    await asyncio.to_thread(stored_path.write_bytes, content)

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
    )

    payload = serialize_message(message)
    await manager.broadcast_json(payload, room)

    return payload


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    if not websocket_origin_allowed(websocket):
        await websocket.close(code=1008)
        return

    client_ip = get_client_ip_from_websocket(websocket)
    if not enforce_websocket_rate_limit(websocket, "ws_connect", client_ip, 25, 60):
        await websocket.close(code=1013)
        return

    token = websocket.query_params.get("room_token")
    username = verify_room_token(token, room)

    if not username:
        await websocket.close(code=1008)
        return
    
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

    if not user:
        await websocket.close(code=1008)
        return
    
    result = await db.execute(
        select(Room).where(Room.name == room)
    )
    existing_room = result.scalar_one_or_none()

    if not existing_room:
        await websocket.close(code=1008)
        return

    is_admin = bool(user.is_admin)

    await manager.connect(websocket, room)

    was_offline = room_members[room][username] == 0
    room_members[room][username] += 1

    if was_offline:
        await manager.broadcast_json(build_system_payload(room, username, "joined"), room)

    try:
        while True:
            data = await websocket.receive_json()
            text = (data.get("text") or "").strip()

            if not text or len(text) > MAX_MESSAGE_LENGTH:
                continue

            message_bucket = f"{room}:{username}:{client_ip}"
            if not is_admin and not enforce_websocket_rate_limit(websocket, "ws_message", message_bucket, 25, 10):
                await websocket.send_json({
                    "type": "system",
                    "text": "Rate limit exceeded",
                    "room": room,
                    "timestamp": utc_now().isoformat(),
                    "system_event": "rate_limited",
                    "system_actor": username,
                })
                continue

            async with SessionLocal() as db:
                message = await save_message(
                    db,
                    username=username,
                    room=room,
                    text=text,
                    content_type="text",
                )

            await manager.broadcast_json(serialize_message(message), room)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print("WebSocket error:", repr(exc))
    finally:
        manager.disconnect(websocket, room)

        went_offline = False

        if room in room_members and username in room_members[room]:
            room_members[room][username] -= 1

            if room_members[room][username] <= 0:
                del room_members[room][username]
                went_offline = True

            if not room_members[room]:
                del room_members[room]

        if went_offline:
            await manager.broadcast_json(build_system_payload(room, username, "left"), room)


@app.get("/")
async def get_index():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
