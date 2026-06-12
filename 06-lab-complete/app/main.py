"""
Production AI Agent — final Day 12 lab.
"""
from __future__ import annotations

import json
import logging
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from openai import OpenAI
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import build_api_key_verifier
from app.config import Settings, settings
from app.cost_guard import InMemoryCostGuard, RedisCostGuard
from app.history_store import InMemoryHistoryStore, RedisHistoryStore
from app.rate_limiter import InMemoryRateLimiter, RedisRateLimiter
from utils.mock_llm import ask as bundled_llm_ask


logging.basicConfig(level=logging.INFO, format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    model: str
    timestamp: str


def create_app(
    settings_obj: Settings | None = None,
    history_store=None,
    rate_limiter=None,
    cost_guard=None,
    llm_func=None,
) -> FastAPI:
    cfg = settings_obj or settings
    history = history_store or _build_history_store(cfg)
    limiter = rate_limiter or _build_rate_limiter(cfg)
    budget = cost_guard or _build_cost_guard(cfg)
    ask_llm = llm_func or (lambda question, history: _default_llm(question, history, cfg))
    verify_api_key = build_api_key_verifier(cfg.agent_api_key)
    state = {"ready": False, "start_time": time.time(), "request_count": 0, "error_count": 0}

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        logger.info(json.dumps({"event": "startup", "app": cfg.app_name, "environment": cfg.environment}))
        state["ready"] = _dependencies_ready(cfg, history, limiter, budget)
        yield
        state["ready"] = False
        logger.info(json.dumps({"event": "shutdown"}))

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        lifespan=lifespan,
        docs_url="/docs" if cfg.environment != "production" else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    )

    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        start = time.time()
        state["request_count"] += 1
        try:
            response: Response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            if "server" in response.headers:
                del response.headers["server"]
            logger.info(
                json.dumps(
                    {
                        "event": "request",
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "ms": round((time.time() - start) * 1000, 1),
                    }
                )
            )
            return response
        except Exception:
            state["error_count"] += 1
            raise

    @app.get("/")
    def root():
        return {
            "app": cfg.app_name,
            "version": cfg.app_version,
            "environment": cfg.environment,
            "endpoints": {
                "ask": "POST /ask (requires X-API-Key)",
                "health": "GET /health",
                "ready": "GET /ready",
            },
        }

    @app.post("/ask", response_model=AskResponse)
    async def ask_agent(body: AskRequest, request: Request, _key: str = Depends(verify_api_key)):
        limiter.check(body.user_id)
        budget.check_budget(body.user_id)

        prior_history = history.get_history(body.user_id)
        answer = ask_llm(body.question, prior_history)

        history.append_message(body.user_id, "user", body.question)
        history.append_message(body.user_id, "assistant", answer)

        input_tokens = len(body.question.split()) * 2
        output_tokens = len(answer.split()) * 2
        usage = budget.record_usage(body.user_id, input_tokens, output_tokens)

        logger.info(
            json.dumps(
                {
                    "event": "agent_call",
                    "user_id": body.user_id,
                    "q_len": len(body.question),
                    "client": str(request.client.host) if request.client else "unknown",
                    "budget_remaining_usd": usage["budget_remaining_usd"],
                }
            )
        )

        return AskResponse(
            user_id=body.user_id,
            question=body.question,
            answer=answer,
            model=cfg.llm_model,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok" if _dependencies_ready(cfg, history, limiter, budget) else "degraded",
            "version": cfg.app_version,
            "environment": cfg.environment,
            "uptime_seconds": round(time.time() - state["start_time"], 1),
            "total_requests": state["request_count"],
            "checks": {
                "llm": "mock" if not cfg.openai_api_key else "openai",
                "state_store": getattr(history, "backend_name", "unknown"),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.get("/ready")
    def ready():
        if not _dependencies_ready(cfg, history, limiter, budget):
            raise HTTPException(503, "Not ready")
        return {"ready": True}

    @app.get("/metrics")
    def metrics(_key: str = Depends(verify_api_key)):
        return {
            "uptime_seconds": round(time.time() - state["start_time"], 1),
            "total_requests": state["request_count"],
            "error_count": state["error_count"],
            "rate_limit_per_minute": cfg.rate_limit_per_minute,
            "monthly_budget_usd": cfg.monthly_budget_usd,
        }

    return app


def _default_llm(question: str, history: list[dict], cfg: Settings) -> str:
    lowered = question.lower()
    if "what is my name" in lowered:
        for message in reversed(history):
            if message["role"] != "user":
                continue
            marker = "my name is "
            if marker in message["content"].lower():
                name = message["content"].lower().split(marker, 1)[1].strip(" .!?")
                return f"Your name is {name.title()}."
    if cfg.openai_api_key:
        return _call_openai_response(question, history, cfg)
    return bundled_llm_ask(question)


def _call_openai_response(question: str, history: list[dict], cfg: Settings) -> str:
    client = OpenAI(api_key=cfg.openai_api_key)
    history_lines = [f"{item['role']}: {item['content']}" for item in history[-10:]]
    prompt_parts = [
        "You are a concise helpful assistant for the Day 12 deployment lab.",
        f"Conversation history:\n" + ("\n".join(history_lines) if history_lines else "(empty)"),
        f"User question: {question}",
    ]
    response = client.responses.create(
        model=cfg.llm_model,
        input="\n\n".join(prompt_parts),
    )
    return response.output_text.strip()


def _dependencies_ready(cfg: Settings, history, limiter, budget) -> bool:
    if not cfg.redis_url:
        return False
    return all(component.is_available() for component in (history, limiter, budget))


def _build_history_store(cfg: Settings):
    if not cfg.redis_url:
        return InMemoryHistoryStore()
    try:
        return RedisHistoryStore(cfg.redis_url)
    except Exception as exc:
        logger.warning("Falling back to in-memory history store: %s", exc)
        return InMemoryHistoryStore()


def _build_rate_limiter(cfg: Settings):
    if not cfg.redis_url:
        return InMemoryRateLimiter(max_requests=cfg.rate_limit_per_minute)
    try:
        return RedisRateLimiter(cfg.redis_url, max_requests=cfg.rate_limit_per_minute)
    except Exception as exc:
        logger.warning("Falling back to in-memory rate limiter: %s", exc)
        return InMemoryRateLimiter(max_requests=cfg.rate_limit_per_minute)


def _build_cost_guard(cfg: Settings):
    if not cfg.redis_url:
        return InMemoryCostGuard(monthly_budget_usd=cfg.monthly_budget_usd)
    try:
        return RedisCostGuard(cfg.redis_url, monthly_budget_usd=cfg.monthly_budget_usd)
    except Exception as exc:
        logger.warning("Falling back to in-memory cost guard: %s", exc)
        return InMemoryCostGuard(monthly_budget_usd=cfg.monthly_budget_usd)


def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))


signal.signal(signal.SIGTERM, _handle_signal)

app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug, timeout_graceful_shutdown=30)
