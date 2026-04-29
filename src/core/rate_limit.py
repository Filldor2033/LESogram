import time
import asyncio

from collections import defaultdict, deque
from threading import Lock
from typing import Optional
from fastapi import HTTPException, Request, WebSocket

from models import User


class SlidingWindowRateLimiter:
    def __init__(self, cleanup_interval: int = 60, fallback_window: int = 300):
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.key_windows: dict[str, int] = {}
        self.lock = Lock()
        self.cleanup_interval = cleanup_interval
        self.fallback_window = fallback_window
        self._cleanup_task: Optional[asyncio.Task] = None

    def hit(
        self, bucket: str, identifier: str, limit: int, window_seconds: int
    ) -> int | None:
        now = time.monotonic()
        key = f"{bucket}:{identifier}"

        with self.lock:
            self.key_windows[key] = window_seconds
            entries = self.events[key]

            while entries and now - entries[0] > window_seconds:
                entries.popleft()

            if len(entries) >= limit:
                retry_after = max(1, int(window_seconds - (now - entries[0])) + 1)
                return retry_after

            entries.append(now)

        return None

    async def _cleanup_loop(self):
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
            except asyncio.CancelledError:
                break

    def _cleanup_expired(self):
        now = time.monotonic()
        with self.lock:
            keys_to_remove = []
            for key, entries in self.events.items():
                window = self.key_windows.get(key, self.fallback_window)
                while entries and now - entries[0] > window:
                    entries.popleft()
                if not entries:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.events[key]
                self.key_windows.pop(key, None)

    def start_cleanup(self):
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup(self):
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None


rate_limiter = SlidingWindowRateLimiter(cleanup_interval=120)


def get_client_ip_from_request(request: Request) -> str:
    return request.client.host if request.client and request.client.host else "unknown"


def get_client_ip_from_websocket(websocket: WebSocket) -> str:
    return (
        websocket.client.host
        if websocket.client and websocket.client.host
        else "unknown"
    )


def enforce_http_rate_limit(
    request: Request, bucket: str, limit: int, window_seconds: int
):
    retry_after = rate_limiter.hit(
        bucket, get_client_ip_from_request(request), limit, window_seconds
    )
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Retry in {retry_after} seconds",
        )


def enforce_http_rate_limit_for_user(
    request: Request,
    bucket: str,
    limit: int,
    window_seconds: int,
    user: User,
):
    if user.is_admin:
        return

    enforce_http_rate_limit(request, bucket, limit, window_seconds)


def enforce_websocket_rate_limit(
    websocket: WebSocket, bucket: str, identifier: str, limit: int, window_seconds: int
) -> bool:
    retry_after = rate_limiter.hit(bucket, identifier, limit, window_seconds)
    return retry_after is None
