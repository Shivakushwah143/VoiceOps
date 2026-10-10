# Architecture

Same-origin static browser → FastAPI HTTP/WebSocket routes → domain and shared VoiceEngine → provider interfaces/adapters. PostgreSQL stores durable records; Redis provides transient leases; Qdrant retrieval filters tenant/KB/document and rechecks approval in PostgreSQL. Tools bind to call tenant, lead and initiating authority, validate schemas, require confirmation where specified and persist idempotent actions.

Provider manager: bounded primary retry, eligible fallback, sticky per-call provider family. Credential, authorization, request and schema failures do not switch. TTS does not retry after output begins. Plivo is never replaced by local AI. Local/browser media shares the engine.

Single API process currently hosts background work. Configurable outbound tenant admission is 1–10. Deployment scaling beyond one process requires qualification of coordination failure/recovery cases.
