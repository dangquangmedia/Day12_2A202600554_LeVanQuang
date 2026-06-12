# 06-lab-complete Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `06-lab-complete` runnable, Docker-buildable, rubric-aligned, and submission-ready without deleting or rewriting unrelated workspace data.

**Architecture:** Execute in three safe phases. First, fix self-contained runtime/build issues so the lab can start cleanly from its own folder. Second, move quota and conversation state into Redis-backed components and align request models and defaults with the grading rubric. Third, synchronize docs and submission artifacts so local run, deployment, and grading evidence all match the real implementation.

**Tech Stack:** FastAPI, Python `unittest`, Docker, Docker Compose, Redis, Railway/Render YAML/TOML

---

## File Map

- `06-lab-complete/app/main.py` — current app entry point with in-memory auth/rate/cost logic
- `06-lab-complete/app/config.py` — environment-driven settings
- `06-lab-complete/Dockerfile` — currently copies a missing local `utils/` directory
- `06-lab-complete/docker-compose.yml` — currently points to `.env.local`
- `06-lab-complete/README.md` — local/deploy instructions
- `06-lab-complete/check_production_ready.py` — keyword/file checker
- `05-scaling-reliability/production/app.py` — reliability/reference patterns
- `04-api-gateway/production/{app.py,rate_limiter.py,cost_guard.py}` — security/reference patterns
- `utils/mock_llm.py` — shared mock response implementation to mirror into the final lab package

## Task 1: Make the lab self-contained and importable

**Files:**
- Create: `06-lab-complete/tests/test_runtime_basics.py`
- Create: `06-lab-complete/utils/__init__.py`
- Create: `06-lab-complete/utils/mock_llm.py`
- Modify: `06-lab-complete/Dockerfile`

- [ ] **Step 1: Write failing import/layout tests**
- [ ] **Step 2: Run the tests and confirm they fail because `utils.mock_llm` is missing**
- [ ] **Step 3: Add a local `utils/` package and keep Docker copy paths consistent**
- [ ] **Step 4: Re-run the focused tests and a direct `python -c "import app.main"` smoke check**

## Task 2: Align runtime behavior with rubric-critical requirements

**Files:**
- Create: `06-lab-complete/app/rate_limiter.py`
- Create: `06-lab-complete/app/cost_guard.py`
- Create: `06-lab-complete/app/history_store.py`
- Modify: `06-lab-complete/app/config.py`
- Modify: `06-lab-complete/app/main.py`
- Create: `06-lab-complete/tests/test_api_behavior.py`

- [ ] **Step 1: Write failing tests for `user_id`, conversation continuity, and rubric defaults**
- [ ] **Step 2: Write failing tests for Redis-backed quota/budget behavior behind clean interfaces**
- [ ] **Step 3: Extract in-memory logic from `main.py` into focused modules**
- [ ] **Step 4: Implement Redis-backed state and make `/ask` use `user_id` history**
- [ ] **Step 5: Re-run focused tests, then run the full local test suite**

## Task 3: Make local run, compose, and readiness wiring truthful

**Files:**
- Modify: `06-lab-complete/docker-compose.yml`
- Modify: `06-lab-complete/.env.example`
- Modify: `06-lab-complete/README.md`
- Create: `06-lab-complete/tests/test_docs_and_config.py`

- [ ] **Step 1: Write failing tests that assert README/env/compose agree on the env filename and service assumptions**
- [ ] **Step 2: Change compose and docs to one consistent local workflow**
- [ ] **Step 3: Re-run the focused docs/config tests**

## Task 4: Refresh submission artifacts after the app is real

**Files:**
- Create: `MISSION_ANSWERS.md`
- Create: `DEPLOYMENT.md`
- Create: `screenshots/.gitkeep`
- Modify: `06-lab-complete/README.md`

- [ ] **Step 1: Fill in mission answers from the actual implementation and commands used**
- [ ] **Step 2: Draft deployment instructions and placeholders for the final public URL/screenshots**
- [ ] **Step 3: Run validator and final smoke tests before claiming submission-ready status**

## Verification Gates

- `cd 06-lab-complete && python -m unittest discover -s tests -q`
- `cd 06-lab-complete && python -c "import app.main; print('import ok')"`
- `cd 06-lab-complete && python check_production_ready.py`
- `cd 06-lab-complete && docker compose config`

## Self-Review

- Spec coverage: this plan covers the exact safe sequence approved by the user: runtime/build first, Redis/stateless second, submission/docs third.
- Placeholder scan: no implementation step depends on undefined files without being created in an earlier task.
- Type consistency: the plan consistently uses `user_id`, `Redis`, `X-API-Key`, `/health`, and `/ready`, matching the grading guide and current code.
