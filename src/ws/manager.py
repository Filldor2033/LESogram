import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass

from fastapi import WebSocket


@dataclass(slots=True, eq=False)
class ClientConnection:
    websocket: WebSocket
    room: str
    queue: asyncio.Queue[str | None]
    sender_task: asyncio.Task | None
    closed: bool = False


class ConnectionManager:
    def __init__(self, queue_size: int = 100):
        self.active_connections: dict[str, set[ClientConnection]] = defaultdict(set)
        self.queue_size = queue_size
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()

        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=self.queue_size)

        connection = ClientConnection(
            websocket=websocket, room=room, queue=queue, sender_task=None
        )

        sender_task = asyncio.create_task(self._sender_loop(connection))

        connection.sender_task = sender_task

        websocket.state.connection = connection

        async with self._lock:
            self.active_connections[room].add(connection)

    async def disconnect(self, websocket: WebSocket, code: int = 1000):
        connection: ClientConnection | None = getattr(
            websocket.state,
            "connection",
            None,
        )

        async with self._lock:
            if not connection or connection.closed:
                return

            connection.closed = True

            room_connections = self.active_connections.get(connection.room)

            if room_connections:
                room_connections.discard(connection)

                if not room_connections:
                    del self.active_connections[connection.room]

        current_task = asyncio.current_task()

        if connection.sender_task and connection.sender_task is not current_task:
            try:
                connection.queue.put_nowait(None)
            except asyncio.QueueFull:
                connection.sender_task.cancel()

            try:
                await connection.sender_task
            except asyncio.CancelledError:
                pass

        websocket.state.connection = None

        try:
            await asyncio.wait_for(
                websocket.close(code=code),
                timeout=2,
            )
        except Exception:
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
            await self.disconnect(websocket)

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
            await self.disconnect(websocket)

    def _enqueue(self, connection: ClientConnection, text: str) -> bool:
        if connection.closed:
            return False

        try:
            connection.queue.put_nowait(text)
            return True
        except asyncio.QueueFull:
            return False

    async def _sender_loop(
        self,
        connection: ClientConnection,
    ):
        try:
            while True:
                text = await connection.queue.get()

                if text is None:
                    break

                try:
                    await asyncio.wait_for(
                        connection.websocket.send_text(text),
                        timeout=5,
                    )
                except Exception:
                    await self.disconnect(connection.websocket)
                    break

        except asyncio.CancelledError:
            pass

    def _send_safe(
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

        await asyncio.gather(
            *(self.disconnect(c.websocket, code=code) for c in connections),
            return_exceptions=True,
        )


manager = ConnectionManager()
