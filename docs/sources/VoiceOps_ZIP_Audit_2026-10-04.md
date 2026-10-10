# VoiceOps ZIP Audit — 2026-10-04

**Artifact audited:** `VoiceOps-source-checkpoint(1).zip`  
**Audit target:** VoiceOps PRD / FRD / Master Build Directive / Astra Execution Prompt  
**Overall verdict:** **NOT RELEASE-READY**  
**Release classification:** Source checkpoint / implementation work in progress  
**Production-ready ZIP gate:** **FAIL**

---

## 1. Executive verdict

The ZIP is internally honest: its own `README.md` and `docs/CHECKPOINT_STATUS.md` say that it is an incomplete source checkpoint and explicitly state that no production-readiness claim is being made.

That assessment is correct.

The archive contains a meaningful backend foundation, but it is not yet a runnable end-to-end VoiceOps product and does not satisfy the requested final release standard.

### Current score

| Area | Score | Verdict |
|---|---:|---|
| Architecture direction | 7/10 | Strong foundation |
| Backend/domain implementation | 6/10 | Significant work exists |
| Voice orchestration | 6/10 | Good concepts, important correctness gaps |
| Provider abstraction/failover | 7/10 | Good pattern, needs fixes and verification |
| RAG | 6/10 | Real ingestion/retrieval path exists |
| Tool safety | 7/10 | Strong boundary, some failure handling is wrong |
| Security baseline | 6/10 | Several good controls, incomplete audit |
| Observability | 3/10 | Event base exists; real metrics/trace coverage is incomplete |
| Frontend/product UX | 0/10 | Missing |
| Deployment/bootstrap | 1/10 | Missing |
| Runtime verification | 1/10 | Syntax compile only |
| AI evaluations | 0/10 | Runner/results absent |
| Final production readiness | **1/10** | **FAIL** |

---

## 2. What is genuinely good

The source is not empty scaffolding. The following are meaningful implementation strengths:

- Provider interfaces exist for STT, LLM, TTS, embeddings and telephony.
- A `ProviderManager` implements bounded retry, fallback eligibility and sticky fallback behavior.
- Tenant ownership is enforced in many persistence paths through `owned(...)`.
- Qdrant retrieval applies tenant, knowledge-base and approved-document filtering.
- Tool execution is kept behind backend validation rather than giving the LLM raw database/shell access.
- Opt-out persists suppression across duplicate leads sharing the same number.
- Barge-in/cancellation logic exists and attempts to cancel generation and clear playback.
- Plivo bidirectional streaming, audio conversion, checkpoints and playback are represented.
- Sarvam realtime STT uses the correct modern realtime endpoint shape.
- Call, turn, event, retrieval/tool-related records and meeting/follow-up domain records exist.
- No obvious real API keys, `.env` secrets, private keys or model weights were packaged.
- Python syntax compilation succeeds for the packaged backend.

This is a useful engineering checkpoint.

---

## 3. Immediate release blockers

### P0-01 — The packaged application cannot start

`backend/app/main.py` mounts a frontend directory at import time:

```python
frontend = Path(__file__).resolve().parents[2] / 'frontend'
app.mount('/assets', StaticFiles(directory=frontend), name='assets')
```

The ZIP contains no `frontend/` directory.

FastAPI/Starlette `StaticFiles` validates the directory during construction, so this is an application-startup blocker.

**Required fix:** implement the frontend or change startup behavior while the frontend is absent. The final release must include the real frontend required by the product.

---

### P0-02 — No database/bootstrap path

The repository contains SQLAlchemy models but no:

- Alembic migration set,
- deterministic schema initialization,
- bootstrap CLI,
- initial Tenant/Admin provisioning command.

The implementation decisions explicitly state that bootstrap is required, but no executable bootstrap exists.

A fresh user therefore cannot initialize the product, create the first tenant/admin, or log in.

**Required fix:** provide migrations/schema initialization plus an explicit first-admin bootstrap path and document it in `START_HERE.md`.

---

### P0-03 — Deployment/runtime package is missing

The final release requires reproducible startup, but this ZIP lacks:

- `docker-compose.yml`
- backend Dockerfile
- frontend build files
- `.env.example`
- infrastructure configuration
- production/local startup scripts
- `START_HERE.md`

This prevents clean-install verification.

---

### P0-04 — The packaged FRD is stale and not the approved/frozen version

The ZIP contains:

```text
Status: DRAFT FOR USER REVIEW — NOT APPROVED OR FROZEN
```

It also still contains the earlier proposals:

- inbound calling in FD-01,
- fixed one-call-per-tenant behavior in FD-03.

Those were later changed in the approved direction:

- outbound is the required V1 telephony scope,
- concurrency should be bounded/configurable with development default = 1, not architecturally hardcoded to one forever.

The code currently implements the old single-active-call-per-tenant assumption in `jobs.py`.

**Required fix:** replace the stale FRD with the approved/frozen artifact and reconcile code against it before further implementation.

---

### P0-05 — The default Groq model is already decommissioned

`backend/app/config.py` defaults to:

```python
GROQ_MODEL=llama-3.3-70b-versatile
```

That model was shut down for Groq free/developer-tier usage in August 2026.

The primary LLM path will therefore fail by default.

**Required fix:** use a currently supported configured model (for example the approved GPT-OSS model selected in provider contracts) and keep it configurable.

---

### P0-06 — Sarvam TTS configuration is inconsistent with the current WebSocket contract

The code sends:

```python
{
  "type": "config",
  "data": {
    "speaker": ...,
    "target_language_code": "en-IN",
    ...
  }
}
```

The current Sarvam streaming TTS WebSocket contract uses `language_code` in the config message.

The production TTS adapter therefore needs correction and live verification before it can be claimed as working.

---

### P0-07 — No production-provider runtime verification

The checkpoint explicitly states that none of the following were exercised:

- backend startup,
- PostgreSQL initialization,
- Redis,
- Qdrant,
- browser voice journey,
- local model inference,
- Sarvam,
- Groq,
- Plivo,
- real phone call,
- provider fallback,
- AI evaluations.

Therefore none of these may be classified as VERIFIED.

---

## 4. Critical voice/runtime correctness defects

### P1-01 — STT timeout budget includes the user's speaking time

`ProviderManager.run()` wraps the entire STT operation in one ~30-second deadline.

The STT operation itself consumes the live utterance stream. VoiceOps also allows an utterance up to ~30 seconds.

A legitimate long utterance can therefore consume almost the complete retry/fallback budget before STT finalization happens.

**Required design:** separate live-input streaming duration from finalization/recovery deadlines, or use stage-specific budgets.

---

### P1-02 — Media lease ownership is unsafe

`run_media()` acquires:

```text
media:<call_id> = "active"
```

and later renews it with plain `EXPIRE`.

There is no unique owner token.

If a lease expires and another worker acquires it, the old worker can still renew the new worker's lease and continue processing, allowing duplicate media ownership.

The jobs worker uses a safer compare-and-expire token pattern; media ownership should do the same.

---

### P1-03 — Plivo clear confirmation is not actually acknowledged

The current Plivo implementation sends `clearAudio` and immediately marks playback completion locally.

Plivo's protocol provides a real `clearedAudio` confirmation event, but the code does not process it.

This means the system cannot reliably distinguish:

```text
clear requested
```

from:

```text
clear confirmed
```

That weakens barge-in evidence and creates potential races around interrupted speech.

---

### P1-04 — Turn correlation is wrong for STT events

A `Turn` record is created only after final STT text is received.

`self.turn_id` remains set to the previous turn while the next utterance is being transcribed.

Therefore:

- partial transcript events,
- STT provider events,
- STT failure/retry events

can be linked to the previous conversational turn, while the first utterance may have no turn ID at all.

This breaks the stated observability requirement that each call/turn be traceable.

**Required fix:** create an utterance/turn identity before STT begins or maintain a distinct input-turn/utterance correlation ID.

---

### P1-05 — Malformed tool arguments can terminate the entire call

The LLM decision schema validates `tool.args` only as a generic dictionary.

Tool-specific validation happens later:

```python
TOOL_SCHEMAS[request.name].model_validate(request.args)
```

If the LLM omits a required scheduling field or returns an invalid datetime/timezone, Pydantic/`ZoneInfo`/`ValueError` can escape the controlled `DomainError` path and fall into the generic turn exception handler.

That currently ends the voice call as:

```text
FAILED / voice_pipeline_failure
```

instead of producing a bounded repair/clarification.

This is a major production behavior bug.

**Required fix:** use typed/discriminated tool schemas or catch tool-validation/timezone failures and convert them to structured rejection/clarification behavior.

---

### P1-06 — Invalid user input can become HTTP 500

Examples such as `valid_phone()` and `valid_time()` raise ordinary `ValueError`.

Several API/domain paths do not convert those errors to a controlled 4xx `DomainError`.

Invalid phone/time input can therefore become a server error instead of a validation response.

---

### P1-07 — Worker exceptions are silently swallowed

`jobs.py` contains several broad:

```python
except Exception:
    pass
```

paths.

This can hide:

- ingestion failures,
- worker ownership failures,
- dispatch failures,
- summary failures,
- persistent infrastructure defects.

A production system must surface these through structured logs/events/metrics and transition affected work into explicit failure/reconciliation states.

---

### P1-08 — Hardcoded single-call dispatch contradicts the updated product direction

The dispatcher currently blocks when any active outbound phone call exists for the tenant.

Development default concurrency = 1 is fine, but the architecture should use a configurable admission limit rather than a permanent boolean assumption.

---

## 5. Observability and evidence gaps

The event model is a useful start, but the release does not yet satisfy VoiceOps observability requirements.

Current `/metrics` returns only DB counts for calls and events. It does not provide the required production metrics for:

- STT latency
- LLM TTFT
- TTS first-audio
- end-to-end turn latency
- retrieval latency
- tool latency
- failover count/success
- provider failures
- interruption/cancellation
- call duration
- usage/cost
- active calls
- queue depth

There is no Grafana configuration.

The code records some timing events in the database, but no complete end-to-end latency calculation exists and true delivery/proxy timing is not consistently distinguished.

---

## 6. Cost accounting is incomplete

Some LLM usage is stored as events, but the required cost/usage ledger is absent.

Missing or incomplete:

- STT billed audio duration,
- TTS character/audio usage,
- telephony billed duration/cost,
- retry/fallback cost,
- pricing version/date,
- per-call estimate,
- per-connected-minute estimate,
- explicit separation between estimated and provider-billed values.

---

## 7. AI evaluation gap

There is no evaluation runner.

`GET /api/evaluations` only reads an `evaluations.json` file if one happens to exist.

The required scenarios have not been executed, including:

- grounded RAG answer,
- no-result RAG,
- tenant leakage,
- correct tool choice,
- invalid tool rejection,
- duplicate protection,
- scheduling clarification,
- opt-out,
- interruption,
- silence,
- eligible fallback,
- ineligible fallback,
- primary + fallback failure,
- summary correctness.

No AI quality claims can currently be made.

---

## 8. Frontend/product workflow gap

No frontend exists in the ZIP.

Therefore none of the required operator journeys are available:

- login/setup
- dashboard
- leads
- lead detail
- campaigns
- campaign detail
- local voice session
- calls
- call detail
- knowledge base/documents
- meetings/follow-ups
- settings/provider health
- evaluations

The API also lacks some complete operator workflows noted by the checkpoint itself, such as campaign editing and richer meeting/follow-up management.

---

## 9. Security findings

Positive controls already present:

- HTTP-only session cookie.
- SameSite strict.
- PBKDF2 password hashing.
- Server-side tenant scoping.
- Admin guard on privileged routes.
- provider secrets are not returned directly.
- tool gateway does not expose arbitrary SQL/shell/filesystem/HTTP.
- callback signature verification is attempted.
- test-number allowlist and consent gates exist.
- opt-out suppression is persisted.

Remaining concerns:

- full authorization matrix has not been runtime tested,
- API rate limits are largely absent outside login,
- payload/field bounds are incomplete across all routes,
- security logging/audit coverage is incomplete,
- worker/media race conditions can violate state consistency,
- tenant isolation has not been adversarially evaluated,
- no final prompt-injection/RAG security evaluation exists,
- no production CORS/proxy/ingress audit exists.

---

## 10. Current external provider contract check

The following current public-provider facts were checked during audit:

### Groq

`llama-3.3-70b-versatile` is deprecated/decommissioned for the normal free/developer path. The configured default must change.

### Sarvam Realtime STT

The current realtime endpoint and the use of:

- `speech-to-text-realtime/ws`
- `audio_input`
- `speech_start`
- `speech_end`
- `transcript.partial`
- `transcript.final`

are directionally aligned with current Sarvam realtime STT documentation.

### Sarvam Streaming TTS

Current streaming configuration uses `language_code`; the implementation currently sends `target_language_code`, so the adapter requires correction and live contract verification.

### Plivo

The selected architecture is directionally aligned with current Plivo audio streaming:

- bidirectional `<Stream>`
- μ-law 8 kHz
- `playAudio`
- `checkpoint`
- `playedStream`
- `clearAudio`

However Plivo also emits `clearedAudio` acknowledgement, which the implementation currently ignores.

---

## 11. Required final-release artifacts still missing

The Astra release prompt required at minimum:

```text
START_HERE.md
README.md
.env.example
docker-compose.yml / equivalent startup infrastructure
frontend
backend runtime/deployment definition

docs/ASSUMPTIONS_AND_DECISIONS.md
docs/ARCHITECTURE.md
docs/PROVIDER_CONFIGURATION.md
docs/AI_EVALS.md
docs/VERIFICATION_REPORT.md
docs/REQUIREMENTS_TRACEABILITY.md
docs/IMPLEMENTATION_REPORT.md
```

Only `README.md` and `ASSUMPTIONS_AND_DECISIONS.md` are currently present from that release set.

---

## 12. Release-gate verdict

| Gate | Status |
|---|---|
| Source exists | PASS |
| Syntax compiles | PASS |
| No obvious packaged secrets | PASS |
| Frontend exists | FAIL |
| Backend starts | FAIL / cannot be claimed |
| DB initialization exists | FAIL |
| Bootstrap admin exists | FAIL |
| Local mode verified | FAIL |
| Production providers verified | FAIL |
| Plivo phone call verified | FAIL |
| RAG runtime verified | FAIL |
| Tool runtime verified | FAIL |
| Hybrid failover verified | FAIL |
| AI evaluations executed | FAIL |
| Prometheus/Grafana complete | FAIL |
| Clean install verified | FAIL |
| Requirements traceability complete | FAIL |
| Final ZIP production-ready | **FAIL** |

---

# Final conclusion

This archive should be treated as:

> **VoiceOps backend reconstruction checkpoint with meaningful architecture and domain work**

—not as:

> **VoiceOps v1 production-ready release**

The checkpoint is useful and worth continuing from. Rebuilding from scratch would waste good work.

The correct next action is to give Astra this ZIP plus this audit and instruct it to **continue/fix the existing implementation**, not start another rewrite.

---

# Remediation instruction for Astra

Use this audit as a release-blocking defect list.

Do NOT rebuild VoiceOps from scratch.

Preserve the useful backend architecture and correct it.

Priority order:

```text
1. Reconcile/replace stale authoritative FRD.
2. Make project bootable:
   database migrations/init
   bootstrap admin
   .env.example
   Docker/local infrastructure
   frontend
   START_HERE.
3. Replace deprecated Groq default.
4. Revalidate and fix current Sarvam/Plivo contracts.
5. Fix STT deadline allocation.
6. Fix media lease ownership.
7. Implement Plivo clear acknowledgement.
8. Fix per-turn/utterance correlation.
9. Make malformed tool arguments controlled clarification/rejection, not call failure.
10. Convert validation errors to proper 4xx/domain errors.
11. Remove silent background-worker exception swallowing.
12. Replace hardcoded one-call dispatch with bounded configurable admission.
13. Finish operator workflows/UI.
14. Implement real Prometheus metrics + Grafana.
15. Implement usage/cost ledger.
16. Implement and run AI evaluations.
17. Run local critical journey.
18. Run production-provider journey where credentials permit.
19. Run real Plivo two-turn phone journey where credentials permit.
20. Exercise hybrid failover.
21. Perform security/tenant audit.
22. Perform clean-install verification.
23. Generate truthful verification/traceability/implementation reports.
24. Only then package the final production-ready ZIP.
```

Do not mark any blocked external path VERIFIED.
