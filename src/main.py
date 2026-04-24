from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime
import json
import mimetypes
import os
from pathlib import Path
import secrets

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from sqlalchemy.orm import Session

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


def ensure_message_schema():
    with engine.begin() as conn:
        tables = {
            row[0]
            for row in conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        if "messages" not in tables:
            return

        columns = {
            row["name"]
            for row in conn.exec_driver_sql("PRAGMA table_info(messages)").mappings().all()
        }

        if "content_type" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN content_type VARCHAR(20) NOT NULL DEFAULT 'text'"
            )

        if "media_url" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN media_url VARCHAR(500)"
            )

        if "file_name" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_name VARCHAR(255)"
            )

        if "mime_type" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN mime_type VARCHAR(255)"
            )

        if "file_size" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_size INTEGER"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_message_schema()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Realtime Chat", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR), check_dir=False), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_json(self, data: dict, room: str):
        dead = []
        for connection in self.active_connections.get(room, []):
            try:
                await connection.send_json(data)
            except Exception:
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection, room)


manager = ConnectionManager()

# room -> set(username)
room_members: dict[str, set[str]] = defaultdict(set)


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


def detect_message_content_type(filename: str, mime_type: str | None) -> str:
    mime = (mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream").lower()
    ext = Path(filename).suffix.lower()

    if mime == "image/gif" or ext == ".gif":
        return "unsupported"

    if mime == "image/svg+xml" or ext == ".svg":
        return "file"

    if mime.startswith("image/"):
        return "image"

    if mime.startswith("video/"):
        return "video"

    return "file"


def serialize_message(message: Message) -> dict:
    return {
        "type": "message",
        "username": message.username,
        "text": message.text or "",
        "room": message.room,
        "timestamp": message.timestamp.isoformat(),
        "content_type": message.content_type or "text",
        "media_url": message.media_url,
        "file_name": message.file_name,
        "mime_type": message.mime_type,
        "file_size": message.file_size,
    }


def save_message(
    db: Session,
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
    db.commit()
    db.refresh(message)
    return message


@app.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=payload.username.strip(),
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@app.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username.strip()).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


@app.get("/rooms")
def list_rooms(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    rooms = db.query(Room).order_by(Room.created_at.desc()).all()
    result = []
    for room in rooms:
        result.append({
            "name": room.name,
            "created_by": room.created_by,
            "created_at": room.created_at.isoformat(),
            "online": len(room_members.get(room.name, set())),
        })
    return result


@app.post("/rooms")
def create_room(
    payload: CreateRoomRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
):
    room_name = payload.name.strip()

    existing = db.query(Room).filter(Room.name == room_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")

    room = Room(
        name=room_name,
        password_hash=hash_password(payload.password),
        created_by=username,
    )
    db.add(room)
    db.commit()

    return {"status": "created", "room": room_name}


@app.post("/rooms/join")
def join_room(
    payload: JoinRoomRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
):
    room_name = payload.room.strip()
    room = db.query(Room).filter(Room.name == room_name).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not verify_password(payload.password, room.password_hash):
        raise HTTPException(status_code=403, detail="Wrong room password")

    access_token = create_access_token({
        "sub": username,
        "room": room_name,
        "type": "room_access",
    })

    return {
        "status": "ok",
        "room": room_name,
        "room_token": access_token,
    }


@app.get("/messages/{room}")
def get_messages(
    room: str,
    room_token: str,
    db: Session = Depends(get_db),
):
    username = verify_room_token(room_token, room)
    if not username:
        raise HTTPException(status_code=403, detail="No access to this room")

    messages = (
        db.query(Message)
        .filter(Message.room == room)
        .order_by(Message.timestamp.desc())
        .limit(50)
        .all()
    )

    messages.reverse()
    return [serialize_message(message) for message in messages]


@app.post("/rooms/{room}/attachments")
async def upload_attachment(
    room: str,
    room_token: str = Form(...),
    text: str = Form(default=""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    username = verify_room_token(room_token, room)
    if not username or username != current_user:
        raise HTTPException(status_code=403, detail="No access to this room")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Attachment is missing a file name")

    caption = normalize_message_text(text, allow_empty=True)
    safe_filename = sanitize_filename(file.filename)
    mime_type = (file.content_type or mimetypes.guess_type(safe_filename)[0] or "application/octet-stream").lower()
    content_type = detect_message_content_type(safe_filename, mime_type)

    if content_type == "unsupported":
        raise HTTPException(status_code=400, detail="GIF uploads are disabled")

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
    stored_path.write_bytes(content)

    message = save_message(
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
    token = websocket.query_params.get("room_token")
    username = verify_room_token(token, room)

    if not username:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)
    room_members[room].add(username)

    await manager.broadcast_json({
        "type": "system",
        "text": f"{username} joined",
        "room": room,
        "timestamp": datetime.utcnow().isoformat(),
    }, room)

    try:
        while True:
            data = await websocket.receive_json()
            text = (data.get("text") or "").strip()

            if not text or len(text) > MAX_MESSAGE_LENGTH:
                continue

            db = SessionLocal()
            try:
                message = save_message(
                    db,
                    username=username,
                    room=room,
                    text=text,
                    content_type="text",
                )
            finally:
                db.close()

            await manager.broadcast_json(serialize_message(message), room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        if room in room_members and username in room_members[room]:
            room_members[room].remove(username)
            if not room_members[room]:
                del room_members[room]

        await manager.broadcast_json({
            "type": "system",
            "text": f"{username} left",
            "room": room,
            "timestamp": datetime.utcnow().isoformat(),
        }, room)


@app.get("/")
def get_index():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
