import asyncio

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db, get_current_user_model
from auth import create_access_token, hash_password, verify_password
from core.rate_limit import enforce_http_rate_limit, enforce_http_rate_limit_for_user
from schemas import CreateRoomRequest, JoinRoomRequest
from services.rooms import build_system_payload, require_room_access, room_members
from models import Message, Room, User
from services.uploads import remove_room_uploads
from ws.manager import manager

router = APIRouter()


@router.get("/rooms")
async def list_rooms(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(get_current_user),
):
    del username
    enforce_http_rate_limit(request, "list_rooms", 120, 60)

    result = await db.execute(select(Room).order_by(Room.created_at.desc()))
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


@router.post("/rooms")
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

    result = await db.execute(select(Room).where(Room.name == room_name))
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


@router.post("/rooms/join")
async def join_room(
    payload: JoinRoomRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    enforce_http_rate_limit_for_user(request, "join_room", 30, 300, current_user)

    room_name = payload.room.strip()

    result = await db.execute(select(Room).where(Room.name == room_name))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not current_user.is_admin:
        if not verify_password(payload.password, room.password_hash):
            raise HTTPException(status_code=403, detail="Wrong room password")

    access_token = create_access_token(
        {
            "sub": current_user.username,
            "room": room_name,
            "type": "room_access",
        }
    )

    return {
        "status": "ok",
        "room": room_name,
        "room_token": access_token,
    }


@router.get("/rooms/{room}/users")
async def list_room_users(
    room: str,
    room_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    enforce_http_rate_limit(request, "list_room_users", 120, 60)

    username = await require_room_access(room, room_token, db)
    del username

    result = await db.execute(select(Room).where(Room.name == room))
    existing_room = result.scalar_one_or_none()

    if not existing_room:
        raise HTTPException(status_code=404, detail="Room not found")

    usernames = sorted(room_members.get(room, {}).keys(), key=str.lower)

    admin_map = {}

    if usernames:
        result = await db.execute(
            select(User.username, User.is_admin).where(User.username.in_(usernames))
        )
        rows = result.all()

        admin_map = {row.username: bool(row.is_admin) for row in rows}

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


@router.delete("/rooms/{room_name}")
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

    result = await db.execute(select(Room).where(Room.name == room_name))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.created_by != current_user.username and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only the creator or admin can delete this room",
        )

    room_result = await db.execute(select(Message).where(Message.room == room_name))
    messages = list(room_result.scalars().all())

    remove_room_uploads(messages)

    await db.execute(delete(Message).where(Message.room == room_name))

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
