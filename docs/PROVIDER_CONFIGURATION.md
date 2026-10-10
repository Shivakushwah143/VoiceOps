# Provider configuration

See .env.example and START_HERE.md. Secrets remain server-side. Manual STT_PROVIDER: sarvam/faster_whisper; LLM_PROVIDER: groq/ollama; TTS_PROVIDER: sarvam/kokoro. Blank uses VOICE_MODE defaults. Hybrid enables eligible local fallback; local selects local adapters explicitly.

Official references checked during continuation:
- https://console.groq.com/docs/models — openai/gpt-oss-120b configurable default.
- https://docs.sarvam.ai/api-reference/text-to-speech/stream — config language_code.
- https://docs.sarvam.ai/api/api-guides-tutorials/speech-to-text/realtime-streaming — realtime STT contract.
- https://docs.plivo.com/docs/voice-agents/audio-streaming/concepts/audio-streaming-reference — clearAudio/clearedAudio and playback events.

Document checks are not live-provider verification. Provider availability, model compatibility, account permissions and voice/audio outputs remain unverified.
