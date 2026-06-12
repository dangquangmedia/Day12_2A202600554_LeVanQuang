"""Redis-backed rate limiting for the final Day 12 lab."""
from __future__ import annotations

import time
import uuid

try:
    import redis
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    redis = None
from fastapi import HTTPException


class InMemoryRateLimiter:
    backend_name = "memory"

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_available(self) -> bool:
        return True

    def check(self, user_id: str) -> dict:
        now = time.time()
        window = [stamp for stamp in self._requests.get(user_id, []) if stamp >= now - self.window_seconds]
        if len(window) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        window.append(now)
        self._requests[user_id] = window
        return {"limit": self.max_requests, "remaining": max(0, self.max_requests - len(window))}


class RedisRateLimiter:
    backend_name = "redis"

    def __init__(self, redis_url: str, max_requests: int = 10, window_seconds: int = 60):
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self._client = redis.from_url(redis_url, decode_responses=True)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_available(self) -> bool:
        if redis is None:
            return False
        try:
            self._client.ping()
            return True
        except redis.RedisError:
            return False

    def check(self, user_id: str) -> dict:
        now = time.time()
        window_start = now - self.window_seconds
        key = self._key(user_id)

        self._client.zremrangebyscore(key, 0, window_start)
        current = self._client.zcard(key)
        if current >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        member = f"{now}:{uuid.uuid4().hex}"
        self._client.zadd(key, {member: now})
        self._client.expire(key, self.window_seconds)

        return {
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - current - 1),
            "window_seconds": self.window_seconds,
        }

    @staticmethod
    def _key(user_id: str) -> str:
        return f"rate:{user_id}"
