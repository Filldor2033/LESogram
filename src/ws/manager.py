import asyncio
import json
from collections import defaultdict

from fastapi import WebSocket
from fastapi.websockets import WebSocketState


class ConnectionManager:
    def __init__(self, concurrent_threshold: int = 10):
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.concurrent_threshold = concurrent_threshold

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections[room].add(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)

            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_json(
        self,
        data: dict,
        room: str,
        exclude: WebSocket | None = None,
    ):
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

        connections = [
            conn
            for conn in list(self.active_connections.get(room, set()))
            if conn.client_state == WebSocketState.CONNECTED and conn is not exclude
        ]

        if not connections:
            return

        if len(connections) < self.concurrent_threshold:
            dead = await self._broadcast_text_sequential(text, connections)
        else:
            dead = await self._broadcast_text_concurrent(text, connections)

        for conn in dead:
            self.disconnect(conn, room)

    async def send_personal_json(
        self,
        data: dict,
        room: str,
        username: str,
    ):
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        connections = list(self.active_connections.get(room, []))
        dead = []

        for conn in connections:
            if getattr(conn.state, "username", None) != username:
                continue

            ok = await self._send_text_safe(conn, text)

            if not ok:
                dead.append(conn)

        for conn in dead:
            self.disconnect(conn, room)

    async def _broadcast_text_sequential(
        self,
        text: str,
        connections: list[WebSocket],
    ) -> list[WebSocket]:
        dead = []

        for conn in connections:
            ok = await self._send_text_safe(conn, text)

            if not ok:
                dead.append(conn)

        return dead

    async def _broadcast_text_concurrent(
        self,
        text: str,
        connections: list[WebSocket],
    ) -> list[WebSocket]:
        results = await asyncio.gather(
            *(self._send_text_safe(conn, text) for conn in connections),
            return_exceptions=True,
        )

        return [
            conn
            for conn, result in zip(connections, results)
            if result is not True
        ]

    async def _send_text_safe(
        self,
        websocket: WebSocket,
        text: str,
    ) -> bool:
        try:
            await asyncio.wait_for(websocket.send_text(text), timeout=3.0)
            return True
        except Exception:
            return False

    async def _send_safe(
        self,
        websocket: WebSocket,
        data: dict,
    ) -> bool:
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return await self._send_text_safe(websocket, text)

    async def close_room(self, room: str, code: int = 1008):
        connections = list(self.active_connections.get(room, []))

        for connection in connections:
            try:
                await connection.close(code=code)
            except Exception:
                pass

        self.active_connections.pop(room, None)


manager = ConnectionManager()