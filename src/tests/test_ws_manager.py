from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.websockets import WebSocketState

from ws.manager import ConnectionManager


@pytest.mark.asyncio
async def test_connection_manager_broadcast_with_dead_connections():
    manager = ConnectionManager()

    ws_good = Mock()
    ws_good.client_state = WebSocketState.CONNECTED
    ws_good.send_text = AsyncMock()

    ws_dead = Mock()
    ws_dead.client_state = WebSocketState.CONNECTED
    ws_dead.send_text = AsyncMock(side_effect=RuntimeError("dead"))

    room = "test_room"
    manager.active_connections[room] = {ws_good, ws_dead}

    await manager.broadcast_json({"type": "test"}, room)

    ws_good.send_text.assert_called_once()
    assert ws_dead not in manager.active_connections.get(room, [])


@pytest.mark.asyncio
async def test_connection_manager_close_room():
    manager = ConnectionManager()

    ws = Mock()
    ws.close = AsyncMock()

    manager.active_connections["temp_room"] = {ws}

    await manager.close_room("temp_room", code=1001)

    ws.close.assert_called_once_with(code=1001)
    assert "temp_room" not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_dead():
    manager = ConnectionManager()

    ws_alive = Mock()
    ws_alive.client_state = WebSocketState.CONNECTED
    ws_alive.send_text = AsyncMock()

    ws_dead = Mock()
    ws_dead.client_state = WebSocketState.CONNECTED
    ws_dead.send_text = AsyncMock(side_effect=RuntimeError("Connection lost"))

    room = "test"
    manager.active_connections[room] = {ws_alive, ws_dead}

    await manager.broadcast_json({"type": "ping"}, room)

    ws_alive.send_text.assert_called_once()

    sent_text = ws_alive.send_text.call_args.args[0]
    assert '"type":"ping"' in sent_text

    assert ws_dead not in manager.active_connections.get(room, [])
    assert ws_alive in manager.active_connections.get(room, [])