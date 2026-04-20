from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Message, User
from schemas import RegisterRequest, LoginRequest, TokenResponse
from auth import hash_password, verify_password, create_access_token, verify_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Realtime Chat", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================
# DB DEPENDENCY
# =============================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================
# CONNECTION MANAGER
# =============================

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
        dead_connections = []

        for connection in self.active_connections.get(room, []):
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection, room)


manager = ConnectionManager()


# =============================
# AUTH ROUTES
# =============================

@app.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password)
    )

    db.add(user)
    db.commit()

    token = create_access_token({"sub": payload.username})
    return TokenResponse(access_token=token)


@app.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": payload.username})
    return TokenResponse(access_token=token)


# =============================
# GET MESSAGES
# =============================

@app.get("/messages/{room}")
def get_messages(room: str, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(Message.room == room)
        .order_by(Message.timestamp.desc())
        .limit(50)
        .all()
    )

    messages = list(reversed(messages))

    return [
        {
            "username": m.username,
            "text": m.text,
            "room": m.room,
            "timestamp": m.timestamp.isoformat()
        }
        for m in messages
    ]


# =============================
# WEBSOCKET
# =============================

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    token = websocket.query_params.get("token")
    username = websocket.query_params.get("username")

    if not token or not username:
        await websocket.close(code=1008)
        return

    token_user = verify_token(token)
    if token_user != username:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)

    await manager.broadcast_json({
        "type": "system",
        "text": f"{username} joined",
        "room": room,
        "timestamp": datetime.utcnow().isoformat()
    }, room)

    try:
        while True:
            data = await websocket.receive_json()
            text = (data.get("text") or "").strip()

            if not text:
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
                "timestamp": msg.timestamp.isoformat()
            }, room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast_json({
            "type": "system",
            "text": f"{username} left",
            "room": room,
            "timestamp": datetime.utcnow().isoformat()
        }, room)


# =============================
# FRONTEND
# =============================

@app.get("/")
def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())