import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app import main
from app.config import Settings


class InMemoryHistoryStore:
    backend_name = "redis"

    def __init__(self):
        self._data = {}

    def append_message(self, user_id, role, content):
        self._data.setdefault(user_id, []).append({"role": role, "content": content})

    def get_history(self, user_id):
        return list(self._data.get(user_id, []))

    def is_available(self):
        return True


class InMemoryRateLimiter:
    backend_name = "redis"

    def __init__(self, max_requests):
        self.max_requests = max_requests
        self.counts = {}

    def is_available(self):
        return True

    def check(self, user_id):
        used = self.counts.get(user_id, 0)
        if used >= self.max_requests:
            raise main.HTTPException(status_code=429, detail="Rate limit exceeded")
        self.counts[user_id] = used + 1
        return {"limit": self.max_requests, "remaining": self.max_requests - self.counts[user_id]}


class InMemoryCostGuard:
    backend_name = "redis"

    def __init__(self, budget_usd):
        self.budget_usd = budget_usd
        self.usage = {}

    def check_budget(self, user_id):
        if self.usage.get(user_id, 0.0) >= self.budget_usd:
            raise main.HTTPException(status_code=402, detail="Monthly budget exceeded")

    def record_usage(self, user_id, input_tokens, output_tokens):
        spent = self.usage.get(user_id, 0.0) + ((input_tokens + output_tokens) / 1000) * 1.0
        self.usage[user_id] = spent
        return {
            "user_id": user_id,
            "cost_usd": spent,
            "budget_usd": self.budget_usd,
            "budget_remaining_usd": max(0.0, self.budget_usd - spent),
        }

    def get_usage(self, user_id):
        spent = self.usage.get(user_id, 0.0)
        return {
            "user_id": user_id,
            "cost_usd": spent,
            "budget_usd": self.budget_usd,
            "budget_remaining_usd": max(0.0, self.budget_usd - spent),
        }

    def is_available(self):
        return True


def contextual_llm(question, history):
    lowered = question.lower()
    for message in reversed(history):
        content_lower = message["content"].lower()
        if message["role"] == "user" and "my name is " in content_lower:
            name = content_lower.split("my name is ", 1)[1].strip(" .!?")
            if "what is my name" in lowered:
                return f"Your name is {name.title()}."
    return f"Mock answer: {question}"


class ApiBehaviorTests(unittest.TestCase):
    def make_client(self):
        settings = Settings(
            environment="test",
            debug=False,
            agent_api_key="test-key",
            rate_limit_per_minute=10,
            monthly_budget_usd=10.0,
            redis_url="redis://test",
        )
        app = main.create_app(
            settings_obj=settings,
            history_store=InMemoryHistoryStore(),
            rate_limiter=InMemoryRateLimiter(max_requests=10),
            cost_guard=InMemoryCostGuard(budget_usd=10.0),
            llm_func=contextual_llm,
        )
        return TestClient(app)

    def test_ask_requires_user_id(self):
        client = self.make_client()

        response = client.post(
            "/ask",
            headers={"X-API-Key": "test-key"},
            json={"question": "Hello"},
        )

        self.assertEqual(response.status_code, 422)

    def test_follow_up_uses_conversation_history(self):
        client = self.make_client()

        first = client.post(
            "/ask",
            headers={"X-API-Key": "test-key"},
            json={"user_id": "alice", "question": "My name is Alice"},
        )
        self.assertEqual(first.status_code, 200)

        second = client.post(
            "/ask",
            headers={"X-API-Key": "test-key"},
            json={"user_id": "alice", "question": "What is my name?"},
        )

        self.assertEqual(second.status_code, 200)
        self.assertIn("Alice", second.json()["answer"])

    def test_health_reports_redis_backed_state(self):
        client = self.make_client()

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["state_store"], "redis")

    def test_default_llm_prefers_openai_when_api_key_present(self):
        with mock.patch("app.main._call_openai_response", return_value="openai answer") as call_openai:
            result = main._default_llm(
                "Explain deployment",
                [],
                Settings(openai_api_key="test-key", llm_model="gpt-5.4-mini"),
            )

        self.assertEqual(result, "openai answer")
        call_openai.assert_called_once()


class SettingsTests(unittest.TestCase):
    def test_default_model_is_gpt_5_4_mini(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            settings = Settings()
        self.assertEqual(settings.llm_model, "gpt-5.4-mini")


if __name__ == "__main__":
    unittest.main()
