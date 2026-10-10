# VoiceOps continuation candidate

Standalone FastAPI voice-to-workflow platform. Production adapters: Plivo, Sarvam STT/TTS and Groq. Local adapters: Faster-Whisper, Ollama and Kokoro, using the same engine. PostgreSQL stores tenant/domain truth; Redis coordinates runtime work; Qdrant stores scoped document vectors.

Begin with **START_HERE.md**.

This candidate continues the existing source; it is not a rewrite. Added: connected operator UI, microphone/audio playback client, Docker infrastructure, schema initialization/admin bootstrap, provider corrections, media ownership/turn correlation fixes, metrics and executable verification/evaluation scripts.

**Release gate remains BLOCKED.** Backend startup and basic HTTP responses were exercised. Full-stack database, tools, RAG, voice playback, local models, phone calling and deployment were not verified. Several product surfaces and release controls remain incomplete; see docs/IMPLEMENTATION_REPORT.md. Do not treat this ZIP as production-ready.
