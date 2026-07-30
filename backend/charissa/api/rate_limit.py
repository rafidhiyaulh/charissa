import threading
import time
from typing import Callable

from fastapi import Header, HTTPException, Request, status

Clock = Callable[[], float]


class RateLimiter:
    """Fixed-window rate limiter: at most `max_requests` per `window_seconds`, per key."""

    def __init__(self, max_requests: int, window_seconds: float, clock: Clock = time.monotonic):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._windows: dict[str, tuple[float, int]] = {}

    def allow(self, key: str) -> bool:
        now = self._clock()
        with self._lock:
            window_start, count = self._windows.get(key, (now, 0))
            if now - window_start >= self._window_seconds:
                window_start, count = now, 0
            count += 1
            self._windows[key] = (window_start, count)
            return count <= self._max_requests


def rate_limit_dependency(limiter: RateLimiter):
    """Builds a FastAPI dependency that rate-limits by API key (or client IP as a fallback)."""

    def _dependency(request: Request, x_api_key: str | None = Header(default=None)):
        key = x_api_key or (request.client.host if request.client else "unknown")
        if not limiter.allow(key):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")

    return _dependency
