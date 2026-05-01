import asyncio
import contextlib
from urllib.parse import urlparse

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from core.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT, MAX_MESSAGE_LENGTH
from core.rate_limit import check_duplicate_message_limit, check_websocket_rate_limit, enforce_websocket_rate_limit, get_client_ip_from_websocket
from database import SessionLocal
from models import Room, User
from services.messages import save_message, serialize_message
from services.parse import extract_mentions
from services.rooms import build_system_payload, room_members, verify_room_token
from utils.time import utc_now
from ws.manager import manager

router = APIRouter()


def websocket_origin_allowed(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host")

    if not origin or not host:
        return True

    parsed = urlparse(origin)
    return parsed.netloc.lower() == host.lower()


async def heartbeat(websocket: WebSocket):
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)

        last_seen = getattr(websocket.state, "last_seen", None)
        now = utc_now()

        if last_seen and (now - last_seen).total_seconds() > HEARTBEAT_TIMEOUT:
            await websocket.close(code=1001)
            return

        ok = await manager._send_safe(websocket, {
            "type": "ping",
            "timestamp": now.isoformat(),
        })

        if not ok:
            return


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    if not websocket_origin_allowed(websocket):
        await websocket.close(code=1008)
        return

    client_ip = get_client_ip_from_websocket(websocket)
    connect_retry_after = await check_websocket_rate_limit(
        "ws_connect",
        client_ip,
        25,
        60,
    )

    if connect_retry_after is not None:
        await websocket.close(code=1013)
        return

    token = websocket.query_params.get("room_token")
    username = verify_room_token(token, room)

    if not username:
        await websocket.close(code=1008)
        return

    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close(code=1008)
            return

        result = await db.execute(select(Room).where(Room.name == room))

        existing_room = result.scalar_one_or_none()

    if not existing_room:
        await websocket.close(code=1008)
        return

    is_admin = bool(user.is_admin)

    await manager.connect(websocket, room)
    websocket.state.username = username
    websocket.state.last_seen = utc_now()
    
    heartbeat_task = asyncio.create_task(heartbeat(websocket))

    was_offline = room_members[room][username] == 0
    room_members[room][username] += 1

    if was_offline:
        await manager.broadcast_json(
            build_system_payload(room, username, "joined"), room
        )

    try:
        while True:
            data = await websocket.receive_json()
            websocket.state.last_seen = utc_now()

            event_type = data.get("type")
            
            if event_type == "pong":
                continue

            if event_type == "typing":
                typing_retry_after = await check_websocket_rate_limit(
                    "ws_typing",
                    f"{room}:{username}:{client_ip}",
                    20,
                    10,
                )

                if not is_admin and typing_retry_after is not None:
                    continue

                await manager.broadcast_json(
                    {
                        "type": "typing",
                        "room": room,
                        "username": username,
                        "is_typing": bool(data.get("is_typing")),
                        "timestamp": utc_now().isoformat(),
                    },
                    room,
                    exclude=websocket,
                )
                continue

            text = (data.get("text") or "").strip()
            reply_to_id = data.get("reply_to_id")

            if reply_to_id is not None:
                try:
                    reply_to_id = int(reply_to_id)
                except (TypeError, ValueError):
                    reply_to_id = None

            if not text or len(text) > MAX_MESSAGE_LENGTH:
                continue

            message_bucket = f"{room}:{username}:{client_ip}"

            burst_retry_after = await check_websocket_rate_limit(
                "ws_message_burst",
                message_bucket,
                5,
                3,
            )

            if not is_admin and burst_retry_after is not None:
                await websocket.send_json(
                    {
                        "type": "system",
                        "text": "Too many messages too quickly",
                        "room": room,
                        "timestamp": utc_now().isoformat(),
                        "system_event": "rate_limited",
                        "system_actor": username,
                        "retry_after": burst_retry_after,
                    }
                )
                continue

            message_retry_after = await check_websocket_rate_limit(
                "ws_message",
                message_bucket,
                25,
                10,
            )

            if not is_admin and message_retry_after is not None:
                await websocket.send_json(
                    {
                        "type": "system",
                        "text": "Rate limit exceeded",
                        "room": room,
                        "timestamp": utc_now().isoformat(),
                        "system_event": "rate_limited",
                        "system_actor": username,
                        "retry_after": message_retry_after,
                    }
                )
                continue

            async with SessionLocal() as db:
                message = await save_message(
                    db,
                    username=username,
                    room=room,
                    text=text,
                    content_type="text",
                    reply_to_id=reply_to_id,
                )

            payload = serialize_message(message)
            await manager.broadcast_json(payload, room)

            mentions = extract_mentions(text)
            valid_mentions = [
                mentioned_user
                for mentioned_user in mentions
                if mentioned_user != username
                and mentioned_user in room_members.get(room, {})
            ]

            for mentioned_user in valid_mentions:
                await manager.send_personal_json(
                    {
                        "type": "mention",
                        "from": username,
                        "room": room,
                        "text": text,
                        "message": payload,
                        "timestamp": utc_now().isoformat(),
                    },
                    room,
                    mentioned_user,
                )

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print("WebSocket error:", repr(exc))
    finally:
        heartbeat_task.cancel()
        
        with contextlib.suppress(asyncio.CancelledError):
            await heartbeat_task
        
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
            await manager.broadcast_json(
                build_system_payload(room, username, "left"), room
            )
