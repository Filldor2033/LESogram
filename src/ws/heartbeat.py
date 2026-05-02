import asyncio

from core.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT
from utils.time import utc_now


async def heartbeat(websocket, send_safe):
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)

        last_seen = getattr(websocket.state, "last_seen", None)
        now = utc_now()

        if last_seen and (now - last_seen).total_seconds() > HEARTBEAT_TIMEOUT:
            await websocket.close(code=1001)
            return

        ok = await send_safe(
            websocket,
            {
                "type": "ping",
                "timestamp": now.isoformat(),
            },
        )

        if not ok:
            return