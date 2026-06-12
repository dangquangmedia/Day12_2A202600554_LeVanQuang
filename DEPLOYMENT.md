# Deployment Information

## Public URL
Pending live deployment

## Platform
Railway or Render

## Test Commands

### Health Check
```bash
curl https://your-agent-domain/health
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent-domain/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LLM_MODEL=gpt-5.4-mini
- MONTHLY_BUDGET_USD
- RATE_LIMIT_PER_MINUTE

## Screenshots
- `screenshots/dashboard.png` — pending live deployment capture
- `screenshots/running.png` — pending live deployment capture
- `screenshots/test.png` — pending live deployment capture

## Notes
- Local code and regression tests are in place.
- Local Docker stack was verified with internal container probes for `/health`, `/ready`, `401` auth enforcement, and successful authenticated `POST /ask`.
- This file still needs the real public URL and screenshot evidence after deployment from your machine/account.
