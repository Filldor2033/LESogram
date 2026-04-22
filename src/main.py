from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Message, User, Room
from schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    CreateRoomRequest,
    JoinRoomRequest,
)
from auth import hash_password, verify_password, create_access_token, verify_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Realtime Chat", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


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

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' ws: wss:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    return response

@app.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=payload.username.strip(),
        hashed_password=hash_password(payload.password)
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
            "online": len(room_members.get(room.name, set()))
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


def verify_room_token(token: str | None, room: str) -> str | None:
    if not token:
        return None
    try:
        from jose import jwt
        from auth import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "room_access":
            return None
        if payload.get("room") != room:
            return None
        return payload.get("sub")
    except Exception:
        return None


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

    return [
        {
            "username": m.username,
            "text": m.text,
            "room": m.room,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in messages
    ]


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

            if not text:
                continue

            if len(text) > 1000:
                continue

            db = SessionLocal()
            try:
                msg = Message(username=username, room=room, text=text)
                db.add(msg)
                db.commit()
                db.refresh(msg)
            finally:
                db.close()

            await manager.broadcast_json({
                "type": "message",
                "username": username,
                "text": text,
                "room": room,
                "timestamp": msg.timestamp.isoformat(),
            }, room)

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
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())