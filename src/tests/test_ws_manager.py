import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from ws.manager import ConnectionManager


def make_ws():
    ws = Mock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.close = AsyncMock()

    state = Mock()
    ws.state = state

    return ws


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    manager = ConnectionManager()

    ws = make_ws()
    room = "test_room"

    await manager.connect(ws, room)
    await manager.broadcast_json({"type": "test"}, room)

    await asyncio.sleep(0.01)

    ws.send_text.assert_called_once()

    sent_text = ws.send_text.call_args.args[0]
    assert '"type":"test"' in sent_text

    await manager.disconnect(ws, room)


@pytest.mark.asyncio
async def test_connection_manager_broadcast_with_dead_connections():
    manager = ConnectionManager()

    ws_good = make_ws()

    ws_dead = make_ws()
    ws_dead.send_text = AsyncMock(side_effect=RuntimeError("dead"))

    room = "test_room"

    await manager.connect(ws_good, room)
    await manager.connect(ws_dead, room)

    await manager.broadcast_json({"type": "test"}, room)

    await asyncio.sleep(0.05)

    ws_good.send_text.assert_called_once()
    ws_dead.send_text.assert_called_once()

    await manager.disconnect(ws_good, room)
    await manager.disconnect(ws_dead, room)


@pytest.mark.asyncio
async def test_connection_manager_close_room():
    manager = ConnectionManager()

    ws = make_ws()
    room = "temp_room"

    await manager.connect(ws, room)

    await manager.close_room(room, code=1001)

    ws.close.assert_called_once_with(code=1001)
    assert room not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_full_queue():
    manager = ConnectionManager(queue_size=1)

    ws = make_ws()
    room = "test"

    await manager.connect(ws, room)

    connection = ws.state.connection

    connection.queue.put_nowait("blocked")

    await manager.broadcast_json({"type": "ping"}, room)

    assert room not in manager.active_connections

    await manager.disconnect(ws, room)
