from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import hashlib

from database import SessionLocal, engine
from models import Base, Message, User

# =============================
# INIT
# =============================

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# =============================
# AUTH CONFIG
# =============================

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================
# UTILS
# =============================

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# =============================
# CONNECTION MANAGER
# =============================

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # room -> list

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)

    async def broadcast(self, message: str, room: str):
        for connection in self.active_connections.get(room, []):
            await connection.send_text(message)

manager = ConnectionManager()

# =============================
# AUTH ROUTES
# =============================

@app.post("/register")
def register(username: str, password: str):
    db: Session = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        return {"error": "User already exists"}

    user = User(
        username=username,
        hashed_password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.close()

    return {"status": "registered"}


@app.post("/login")
def login(username: str, password: str):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": username})
    db.close()

    return {"access_token": token}

# =============================
# GET MESSAGES
# =============================

@app.get("/messages/{room}")
def get_messages(room: str):
    db: Session = SessionLocal()

    messages = (
        db.query(Message)
        .filter(Message.room == room)
        .order_by(Message.timestamp.desc())
        .limit(50)
        .all()
    )

    db.close()

    return list(reversed([
        {"username": m.username, "text": m.text}
        for m in messages
    ]))

# =============================
# WEBSOCKET
# =============================

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    token = websocket.query_params.get("token")

    token_user = verify_token(token)
    if token_user != username:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room)
    await manager.broadcast(f"🔵 {username} joined", room)

    try:
        while True:
            data = await websocket.receive_text()

            db: Session = SessionLocal()
            msg = Message(username=username, room=room, text=data)
            db.add(msg)
            db.commit()
            db.close()

            await manager.broadcast(f"{username}: {data}", room)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"🔴 {username} left", room)

# =============================
# FRONTEND
# =============================

@app.get("/")
def get():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())