# Executed verification

2026-10-04:
- Installed all 45 resolved backend packages into a clean Python 3.12 virtual environment with uv.
- Imported FastAPI application successfully (34 routes at initial check).
- Started Uvicorn subprocess and issued actual HTTP requests: /livez 200, / 200, /assets/app.js 200, /openapi.json 200, /api/me 401, /readyz 503 with PostgreSQL unavailable. Evidence: evals/http-results.json.
- Python compileall succeeded; Node module syntax checks passed for app.js and voice.js.
- Executed deterministic provider fixtures for network, timeout, unavailable, credentials, authorization, schema, request and rate-limit failures. Eligible fallback and sticky selection assertions passed; ineligible cases did not fallback. This is not real-provider verification. Evidence: evals/policy-results.json.
- Attempted five real LLM evaluation cases; each BLOCKED because Ollama was unavailable. Evidence: evals/ai-results.json.
- Docker, PostgreSQL and Redis server executables were absent. No database bootstrap or full-stack clean installation was verified.
- Cloud provider credentials and local model assets unavailable. No phone or audible two-turn journey was verified.
- UI assets served successfully; interactive browser UI behavior was not exercised.
