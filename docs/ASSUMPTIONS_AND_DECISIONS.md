# Implementation decisions

Latest build authorization releases the FRD documentation-only gate. PRD automatic failover deferral is superseded by that authorization and FRD FD-09. Standalone scope through V7 remains required; SynTask is excluded. FRD proposed functional choices are preserved as the current implementation baseline, without representing the draft as separately approved.

## Technical choices
- Python 3.12, FastAPI, synchronous SQLAlchemy/PostgreSQL transactions, one Uvicorn process initially; bounded asynchronous provider operations.
- Same-origin browser client with opaque HTTP-only sessions; ADMIN and OPERATOR. Explicit CLI bootstrap; no public signup.
- Internal mono PCM signed 16-bit little-endian, 16 kHz; browser 20 ms frames. Plivo mu-law 8 kHz converted at media boundary.
- Server VAD endpoints at 700 ms silence; speech maximum 30 seconds; one silence prompt after 15 seconds and end after another 15; maximum call 10 minutes.
- Complete validated assistant decision precedes speech. At most one tool per decision; maximum three per turn. Confirmation is server-held, expires after 120 seconds, and needs an audible readback followed by a new affirmative turn.
- Provider operation deadline 30 seconds including one primary retry and one local fallback. Fallback is sticky per family until call end. Configuration/auth/schema/programming failures never switch. TTS retries only before first emitted audio.
- Ollama nomic-embed-text embeddings, 768 dimensions, separate versioned Qdrant collection. 1200-character chunks with 200 overlap. Only approved tenant documents are eligible; PostgreSQL permission recheck after retrieval.
- UTF-8 TXT/MD and text PDF only, maximum 5 MiB/200k extracted characters. No URL fetch or OCR. No raw audio retention. Transcript retention default 30 days.
- Local models installed explicitly. Faster-Whisper and Kokoro support utterance processing, not fabricated native streaming capabilities.
- Unknown usage/pricing yields unavailable estimated cost, never zero billed cost.

## Recovery and evidence
On 2026-10-04 workspace maintenance removed the unsaved implementation. Source documents were recovered; reconstruction is required. Earlier source-only checks do not verify reconstructed code. Saved checkpoints are development artifacts, not production release certification.

## Continuation authorization reconciliation
The 2026-10-04 audit and continuation directive supersede the packaged draft on two points: V1 requires outbound only; outbound concurrency is bounded/configurable (OUTBOUND_CONCURRENCY, default 1, range 1–10). The original FRD remains unchanged as historical source. A separately frozen FRD was not found; no approval is fabricated. This reconciliation is authoritative for this candidate, not a replacement approved FRD.
STT now uses a stage-specific 65-second budget (up to 30 seconds live input plus 35 seconds recovery); other stages retain their bounded deadline. This still requires live latency qualification.
