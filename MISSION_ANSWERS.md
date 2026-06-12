# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded configuration and secret defaults make deployment unsafe and brittle.
2. Running without `PORT` from env breaks compatibility with Railway/Render style platforms.
3. Missing health and readiness endpoints prevents orchestrators from probing the app correctly.
4. In-memory state breaks horizontal scaling because each instance sees a different session snapshot.
5. Weak logging makes cloud debugging and cost/security investigation much harder.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcoded defaults or manual terminal export | `.env` and environment variables | Lets one codebase run across local, Docker, and cloud without code edits |
| Secrets | Easy to leak in code | Read from env only | Keeps credentials out of source control and commit history |
| Health | Often missing | `/health` and `/ready` | Enables orchestration, health probing, and safer rollout behavior |
| Logging | Ad hoc prints | Structured JSON logs | Easier to search, alert on, and debug in production |
| State | In memory | Redis-backed | Required for stateless scaling and multi-turn consistency |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim`
2. Working directory: `/app`
3. `COPY requirements.txt` first to preserve Docker layer caching when app code changes.
4. `CMD` supplies the default runtime command and can be overridden more easily than `ENTRYPOINT`.

### Exercise 2.3: Image size comparison
- Final lab production image: `06-lab-complete-agent:latest` built successfully at `354MB`
- This is below the `< 500 MB` requirement from the delivery checklist
- Multi-stage build keeps runtime image smaller by excluding builder-only packages from the final layer

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: pending live deployment
- Screenshot: pending `screenshots/` capture after deployment

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Verified by local automated tests in `06-lab-complete/tests/test_api_behavior.py`
- Verified by real Docker stack checks inside the running `agent` container
- `POST /ask` without valid `X-API-Key` returned `401 Unauthorized`
- `POST /ask` with valid API key and payload `{"user_id":"demo","question":"What is deployment?"}` returned `200`
- Conversation follow-up with `{"user_id":"demo","question":"What is my name?"}` returned `Your name is Alice.`

### Exercise 4.4: Cost guard implementation
The final lab uses a Redis-backed monthly budget tracker keyed by `budget:<YYYY-MM>:<user_id>`. Before a response is generated, the app checks the current user's spend; after the response, it records token-estimated cost so future requests can be blocked with `402` when the monthly ceiling is reached. The configured target budget is `$10/month per user`, aligned with the final project rubric.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- `/health` reports service status, model backend type, and state store type.
- `/ready` is tied to dependency readiness rather than only process liveness.
- SIGTERM is handled explicitly so orchestrators can shut the service down cleanly.
- Conversation history, quota, and budget state were moved out of in-process globals and into Redis-backed modules.
- Real Docker Compose stack verification:
  - Redis service was `healthy`
  - Agent service reported `running restart=0 health=healthy`
  - Internal `/health` returned `"state_store": "redis"` and `"llm": "openai"`
- One local-machine caveat remains outside the app itself: another host process is already bound to `localhost:8000`, so direct host-browser testing should either use a free port mapping or stop that unrelated process with approval.
