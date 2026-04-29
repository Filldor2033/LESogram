import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState


class ConnectionManager:
    def __init__(self, concurrent_threshold: int = 10):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.concurrent_threshold = concurrent_threshold

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if (
            room in self.active_connections
            and websocket in self.active_connections[room]
        ):
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_json(
        self,
        data: dict,
        room: str,
        exclude: WebSocket | None = None,
    ):
        connections = [
            conn
            for conn in self.active_connections.get(room, [])
            if conn.client_state == WebSocketState.CONNECTED and conn is not exclude
        ]

        if not connections:
            return

        if len(connections) < self.concurrent_threshold:
            dead = await self._broadcast_sequential(data, room, connections)
        else:
            dead = await self._broadcast_concurrent(data, room, connections)

        for conn in dead:
            self.disconnect(conn, room)
            
    async def send_personal_json(
        self,
        data: dict,
        room: str,
        username: str,
    ):
        connections = self.active_connections.get(room, [])

        for conn in connections:
            if getattr(conn.state, "username", None) != username:
                continue

            await self._send_safe(conn, data)

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
        dead: list[WebSocket] = []

        async with asyncio.TaskGroup() as tg:
            for conn in connections:
                tg.create_task(self._send_and_track(conn, data, dead))

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
