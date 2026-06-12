"""Redis-backed budget tracking for the final Day 12 lab."""
from __future__ import annotations

from datetime import datetime, timezone

try:
    import redis
except ModuleNotFoundError:  # pragma: no cover - depends on environment
    redis = None
from fastapi import HTTPException


PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


class InMemoryCostGuard:
    backend_name = "memory"

    def __init__(self, monthly_budget_usd: float = 10.0):
        self.monthly_budget_usd = monthly_budget_usd
        self._usage: dict[str, dict] = {}

    def is_available(self) -> bool:
        return True

    def check_budget(self, user_id: str) -> None:
        if self.get_usage(user_id)["cost_usd"] >= self.monthly_budget_usd:
            raise HTTPException(status_code=402, detail="Monthly budget exceeded")

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> dict:
        usage = self._usage.setdefault(
            user_id,
            {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0},
        )
        usage["requests"] += 1
        usage["input_tokens"] += input_tokens
        usage["output_tokens"] += output_tokens
        usage["cost_usd"] = round(
            usage["cost_usd"] + self._cost_for_tokens(input_tokens, output_tokens),
            6,
        )
        return self.get_usage(user_id)

    def get_usage(self, user_id: str) -> dict:
        usage = self._usage.get(
            user_id,
            {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0},
        )
        return {
            "user_id": user_id,
            "month": datetime.now(timezone.utc).strftime("%Y-%m"),
            "requests": usage["requests"],
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "cost_usd": usage["cost_usd"],
            "budget_usd": self.monthly_budget_usd,
            "budget_remaining_usd": max(0.0, self.monthly_budget_usd - usage["cost_usd"]),
        }

    @staticmethod
    def _cost_for_tokens(input_tokens: int, output_tokens: int) -> float:
        return round(
            (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
            + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS,
            6,
        )


class RedisCostGuard:
    backend_name = "redis"

    def __init__(self, redis_url: str, monthly_budget_usd: float = 10.0):
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self._client = redis.from_url(redis_url, decode_responses=True)
        self.monthly_budget_usd = monthly_budget_usd

    def is_available(self) -> bool:
        if redis is None:
            return False
        try:
            self._client.ping()
            return True
        except redis.RedisError:
            return False

    def check_budget(self, user_id: str) -> None:
        usage = self.get_usage(user_id)
        if usage["cost_usd"] >= self.monthly_budget_usd:
            raise HTTPException(status_code=402, detail="Monthly budget exceeded")

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> dict:
        key = self._key(user_id)
        cost = self._cost_for_tokens(input_tokens, output_tokens)
        payload = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "request_count": 1,
            "cost_usd": cost,
        }
        self._client.hincrbyfloat(key, "cost_usd", payload["cost_usd"])
        self._client.hincrby(key, "input_tokens", payload["input_tokens"])
        self._client.hincrby(key, "output_tokens", payload["output_tokens"])
        self._client.hincrby(key, "request_count", payload["request_count"])
        return self.get_usage(user_id)

    def get_usage(self, user_id: str) -> dict:
        key = self._key(user_id)
        raw = self._client.hgetall(key)
        cost = float(raw.get("cost_usd", 0.0))
        return {
            "user_id": user_id,
            "month": datetime.now(timezone.utc).strftime("%Y-%m"),
            "requests": int(raw.get("request_count", 0)),
            "input_tokens": int(raw.get("input_tokens", 0)),
            "output_tokens": int(raw.get("output_tokens", 0)),
            "cost_usd": cost,
            "budget_usd": self.monthly_budget_usd,
            "budget_remaining_usd": max(0.0, self.monthly_budget_usd - cost),
        }

    def _key(self, user_id: str) -> str:
        return f"budget:{datetime.now(timezone.utc).strftime('%Y-%m')}:{user_id}"

    @staticmethod
    def _cost_for_tokens(input_tokens: int, output_tokens: int) -> float:
        return round(
            (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
            + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS,
            6,
        )
