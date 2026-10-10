# Start here

This continuation candidate has a working HTTP startup path, but full-stack voice behavior remains unverified. Read `docs/IMPLEMENTATION_REPORT.md` before deployment.

Prerequisites: Docker Engine/Desktop with Compose v2; Python 3.12 for configuration generation; local AI requires model downloads, several GB disk/RAM and adequate CPU/GPU.

From the extracted `voiceops` directory:

```sh
python scripts/configure.py
# Edit .env: choose VOICE_MODE, model/provider configuration.
docker compose up -d postgres redis qdrant ollama
docker compose build app
docker compose run --rm app python -m app.cli init-db
docker compose run --rm app python -m app.cli bootstrap
docker compose up -d app prometheus grafana
```

Open http://localhost:8000 and log in with the administrator you created. Grafana: http://localhost:3000, username admin, password from .env. No default app password. Frontend is served by FastAPI; no separate npm build.

## Local AI

Set LOCAL_AI=true before building. Explicitly install Faster-Whisper converted model files under `models/whisper`; Kokoro `config.json`, `kokoro-v1_0.pth`, and `af_heart.pt` under `models/kokoro`. The English spaCy model required by Kokoro must also be installed in the image; this model provisioning path remains a release limitation. Nothing downloads at app startup.

```sh
docker compose exec ollama ollama pull qwen2.5:3b
docker compose exec ollama ollama pull nomic-embed-text
```

Create a KB, upload a text PDF/TXT/MD, wait for ingestion, approve as administrator. Open Voice Studio, choose context, start microphone and use a headset. No phone is dialed in browser mode.

## Production-like / hybrid

Set VOICE_MODE=production or hybrid; configure SARVAM_API_KEY, GROQ_API_KEY, PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN, PLIVO_FROM_NUMBER. PUBLIC_URL must match your public HTTPS reverse proxy exactly; enable WebSocket upgrade and SECURE_COOKIE=true. Terminate TLS at a production reverse proxy; restrict backend port access. No production ingress config is bundled yet.

Create leads with E.164 phones, recorded consent source/timestamp and TEST_PHONE_ALLOWLIST membership. Create and explicitly start a campaign. Plivo outbound API receives answer/status callback URLs from PUBLIC_URL. No inbound route is included in V1.

## Checks

```sh
docker compose logs app
docker compose run --rm app python -m app.cli init-db
python scripts/verify_policy.py
```

For actual AI evaluations, run `scripts/evaluate.py` from a configured Python environment with backend dependencies and DATA_DIR set to a writable location. It records raw outputs and schema validity; semantic quality requires review.

Readiness requires PostgreSQL schema and Redis. Local models, Qdrant, telephony and cloud credential health must be checked separately. A healthy `/livez` is not proof of a voice journey.
