import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass

from fastapi import WebSocket


@dataclass(eq=False)
class ClientConnection:
    websocket: WebSocket
    queue: asyncio.Queue[str]
    sender_task: asyncio.Task


class ConnectionManager:
    def __init__(self, queue_size: int = 100):
        self.active_connections: dict[str, set[ClientConnection]] = defaultdict(set)
        self.queue_size = queue_size
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self.queue_size)
        sender_task = asyncio.create_task(self._sender_loop(websocket, queue))
        
        connection = ClientConnection(
            websocket=websocket,
            queue=queue,
            sender_task=sender_task
        )
        
        websocket.state.connection = connection
        
        async with self._lock:
            self.active_connections[room].add(connection)

    async def disconnect(self, websocket: WebSocket, room: str):
        connection: ClientConnection | None = getattr(
            websocket.state,
            "connection",
            None,
        )

        if not connection:
            return

        async with self._lock:
            if room in self.active_connections:
                self.active_connections[room].discard(connection)

                if not self.active_connections[room]:
                    del self.active_connections[room]

        connection.sender_task.cancel()

        try:
            await connection.sender_task
        except asyncio.CancelledError:
            pass

    async def broadcast_json(
        self,
        data: dict,
        room: str,
        exclude: WebSocket | None = None,
    ):
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

        async with self._lock:
            connections = list(self.active_connections.get(room, set()))

        dead: list[WebSocket] = []

        for connection in connections:
            if connection.websocket is exclude:
                continue

            ok = self._enqueue(connection, text)

            if not ok:
                dead.append(connection.websocket)

        for websocket in dead:
            await self.disconnect(websocket, room)

    async def send_personal_json(
        self,
        data: dict,
        room: str,
        username: str,
    ):
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

        async with self._lock:
            connections = list(self.active_connections.get(room, set()))

        dead: list[WebSocket] = []

        for connection in connections:
            if getattr(connection.websocket.state, "username", None) != username:
                continue

            ok = self._enqueue(connection, text)

            if not ok:
                dead.append(connection.websocket)

        for websocket in dead:
            await self.disconnect(websocket, room)
            
    def _enqueue(self, connection: ClientConnection, text: str) -> bool:
        try:
            connection.queue.put_nowait(text)
            return True
        except asyncio.QueueFull:
            return False
        
    async def _sender_loop(
        self,
        websocket: WebSocket,
        queue: asyncio.Queue[str],
    ):
        while True:
            text = await queue.get()

            try:
                await asyncio.wait_for(websocket.send_text(text), timeout=1.5)
            except Exception:
                break

    async def _send_safe(
        self,
        websocket: WebSocket,
        data: dict,
    ) -> bool:
        connection: ClientConnection | None = getattr(
            websocket.state,
            "connection",
            None,
        )

        if not connection:
            return False

        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return self._enqueue(connection, text)

    async def close_room(self, room: str, code: int = 1008):
        async with self._lock:
            connections = list(self.active_connections.get(room, set()))

        for connection in connections:
            try:
                await connection.websocket.close(code=code)
            except Exception:
                pass

            await self.disconnect(connection.websocket, room)


manager = ConnectionManager()