import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv('DATABASE_URL', 'postgresql+psycopg://voiceops:voiceops@postgres/voiceops')
    redis_url: str = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    qdrant_url: str = os.getenv('QDRANT_URL', 'http://qdrant:6333')
    ollama_url: str = os.getenv('OLLAMA_URL', 'http://ollama:11434')
    public_url: str = os.getenv('PUBLIC_URL', 'http://localhost:8000').rstrip('/')
    secure_cookie: bool = os.getenv('SECURE_COOKIE', 'false').lower() == 'true'
    data_dir: str = os.getenv('DATA_DIR', '/data')
    mode: str = os.getenv('VOICE_MODE', 'local')
    stt: str = os.getenv('STT_PROVIDER', '')
    llm: str = os.getenv('LLM_PROVIDER', '')
    tts: str = os.getenv('TTS_PROVIDER', '')
    sarvam_key: str = os.getenv('SARVAM_API_KEY', '')
    groq_key: str = os.getenv('GROQ_API_KEY', '')
    groq_model: str = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')
    embedding_model: str = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
    sarvam_stt_model: str = os.getenv('SARVAM_STT_MODEL', 'saaras:v3-realtime')
    sarvam_tts_model: str = os.getenv('SARVAM_TTS_MODEL', 'bulbul:v3')
    sarvam_voice: str = os.getenv('SARVAM_VOICE', 'shubh')
    whisper_dir: str = os.getenv('WHISPER_MODEL_DIR', '/models/whisper')
    kokoro_dir: str = os.getenv('KOKORO_MODEL_DIR', '/models/kokoro')
    plivo_id: str = os.getenv('PLIVO_AUTH_ID', '')
    plivo_token: str = os.getenv('PLIVO_AUTH_TOKEN', '')
    plivo_from: str = os.getenv('PLIVO_FROM_NUMBER', '')
    allowlist: tuple = tuple(x.strip() for x in os.getenv('TEST_PHONE_ALLOWLIST', '').split(',') if x.strip())
    metrics_token: str = os.getenv('METRICS_TOKEN', '')
    rate_fallback: bool = os.getenv('RATE_LIMIT_FALLBACK', 'false').lower() == 'true'
    outbound_concurrency: int = max(1,min(10,int(os.getenv('OUTBOUND_CONCURRENCY','1'))))
    retention_days: int = int(os.getenv('TRANSCRIPT_RETENTION_DAYS', '30'))

settings = Settings()
