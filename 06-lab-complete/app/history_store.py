"""Conversation history storage for the final Day 12 lab."""
from __future__ import annotations

import json
from datetime import datetime, timezone

try:
    import redis
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    redis = None


class InMemoryHistoryStore:
    backend_name = "memory"

    def __init__(self):
        self._data: dict[str, list[dict]] = {}

    def is_available(self) -> bool:
        return True

    def get_history(self, user_id: str) -> list[dict]:
        return list(self._data.get(user_id, []))

    def append_message(self, user_id: str, role: str, content: str) -> list[dict]:
        history = self._data.setdefault(user_id, [])
        history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._data[user_id] = history[-20:]
        return self._data[user_id]


class RedisHistoryStore:
    backend_name = "redis"

    def __init__(self, redis_url: str, ttl_seconds: int = 86400):
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self._client = redis.from_url(redis_url, decode_responses=True)
        self._ttl_seconds = ttl_seconds

    def is_available(self) -> bool:
        if redis is None:
            return False
        try:
            self._client.ping()
            return True
        except redis.RedisError:
            return False

    def get_history(self, user_id: str) -> list[dict]:
        data = self._client.get(self._key(user_id))
        return json.loads(data) if data else []

    def append_message(self, user_id: str, role: str, content: str) -> list[dict]:
        history = self.get_history(user_id)
        history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        history = history[-20:]
        self._client.set(self._key(user_id), json.dumps(history), ex=self._ttl_seconds)
        return history

    @staticmethod
    def _key(user_id: str) -> str:
        return f"history:{user_id}"
