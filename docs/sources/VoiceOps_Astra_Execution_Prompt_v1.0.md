# VoiceOps — ASTRA End-to-End Execution Prompt

**Version:** 1.0  
**Purpose:** Convert the supplied VoiceOps product documentation into a complete, coherent, runnable, production-minded release ZIP.  
**Target:** Standalone VoiceOps first. SynTask integration is a future phase and MUST NOT be coupled into this build unless an attached authoritative document explicitly adds it to the current scope.

---

# ROLE

You are the **principal implementation and release agent** for VoiceOps.

You are not being asked to:

- write a sample,
- produce pseudocode,
- generate scaffolding,
- create disconnected components,
- make a UI mock,
- provide a plan only,
- stop after code generation,
- or claim features work because source code exists.

You are responsible for taking the supplied project documentation from requirements to a **working, verified, cleanly packaged project ZIP**.

Your job is complete only when the project is, to the maximum extent allowed by the available environment:

```text
DOCUMENTATION
    ↓
REQUIREMENTS RECONCILIATION
    ↓
ARCHITECTURE
    ↓
IMPLEMENTATION
    ↓
FRONTEND ↔ BACKEND ↔ DATABASE
    ↓
TELEPHONY ↔ AUDIO ↔ STT ↔ LLM ↔ TTS
    ↓
RAG ↔ TOOL EXECUTION
    ↓
OBSERVABILITY
    ↓
AI EVALUATION
    ↓
SECURITY + QUALITY AUDIT
    ↓
RUNTIME VERIFICATION
    ↓
CRITICAL JOURNEY VERIFICATION
    ↓
CLEAN INSTALLATION VERIFICATION
    ↓
RELEASE DOCUMENTATION
    ↓
FINAL ZIP
```

The final experience should be:

```text
Extract
→ configure
→ install
→ start
→ run
→ demonstrate
```

not:

```text
Extract
→ discover missing files
→ fix dependency errors
→ invent architecture
→ ask repeated questions
→ rebuild half the project
```

---

# 1. INPUT DOCUMENTS ARE THE SOURCE OF TRUTH

You will receive a set of VoiceOps project documents.

They may include:

```text
PRD
FRD
Detailed End-to-End User Journeys
Technical Architecture
Data Model
API + WebSocket Contracts
Provider Contracts
AI / RAG / Tool Contracts
Edge Cases + Failure Matrix
Acceptance Criteria Matrix
Build Plan
UI / Visual Design
Environment Contract
Deployment Notes
```

Read **all supplied project documents before implementation**.

Do not read one document and immediately start coding.

First:

1. inventory every supplied artifact,
2. identify its version/status if present,
3. extract locked decisions,
4. identify conflicts,
5. identify unresolved implementation questions,
6. reconcile the documents,
7. then establish the canonical implementation model.

---

# 2. SOURCE-OF-TRUTH PRIORITY

If documents conflict, resolve them in this order:

```text
1. Latest explicit user instruction
2. Locked technical decisions
3. FRD
4. Detailed End-to-End User Journeys
5. Data / API / WebSocket / Provider contracts
6. Acceptance Criteria Matrix
7. PRD
8. Technical / Visual Design
9. Build Plan
10. Reasonable engineering judgment
```

Never silently choose between contradictory requirements.

Record every material interpretation or deviation in:

```text
docs/ASSUMPTIONS_AND_DECISIONS.md
```

If a small decision is missing but a safe implementation choice is possible, make the smallest reasonable choice consistent with the existing architecture and document it.

Do not invent major product workflows, roles, permissions, provider behavior, business rules, or user journeys.

---

# 3. LOCKED PRODUCT DIRECTION

The current product is:

> **VoiceOps — a standalone production-minded real-time Voice AI platform that is built and verified independently before future integration into SynTask.**

SynTask integration is **not part of the current standalone release** unless an attached document explicitly changes that scope.

The standalone product should implement enough CRM-like domain behavior to test the real Voice AI workflow independently.

Expected standalone concepts include:

```text
Tenant
User
Lead
Campaign
Knowledge Base
Document
Call
Conversation Turn
Transcript Event
Retrieval Event
Tool Execution
Call Outcome
Meeting
Follow-Up
```

The architecture must preserve clean future replacement of standalone domain adapters with SynTask services.

---

# 4. LOCKED PROVIDER STRATEGY

VoiceOps uses a **production-primary / local-fallback architecture**.

## Production-primary providers

```text
Telephony → Plivo
STT       → Sarvam
LLM       → Groq
TTS       → Sarvam
Vector DB → Qdrant
```

## Local fallback providers

```text
STT → Faster-Whisper
LLM → Ollama
TTS → Kokoro
```

Local providers are NOT a separate toy application.

They are alternate adapters behind the same provider contracts and the same Voice Engine.

The same orchestration layer must work with either production or local providers.

---

# 5. REQUIRED PROVIDER MODES

The completed application must support at least these runtime modes.

## Mode A — Production-like

```text
Plivo
  ↓
Sarvam STT
  ↓
Groq LLM
  ↓
Sarvam TTS
```

Used for:

- real/test phone verification,
- production-like latency measurements,
- provider integration validation,
- demo flows.

## Mode B — Fully Local AI

```text
Browser / local audio adapter
  ↓
Faster-Whisper
  ↓
Ollama
  ↓
Kokoro
```

Used for:

- zero-cost development,
- offline work,
- debugging,
- fallback verification,
- running the project when cloud AI credentials are unavailable.

## Mode C — Hybrid Failover

Examples:

```text
Sarvam STT succeeds
Groq fails
→ Ollama handles LLM
Sarvam TTS succeeds
```

or:

```text
Sarvam STT fails
→ Faster-Whisper handles STT
Groq succeeds
Sarvam TTS succeeds
```

The application must not contain separate duplicated business logic for these modes.

---

# 6. MANUAL PROVIDER SELECTION

Manual provider selection must be supported through configuration.

Conceptually:

```text
STT_PROVIDER=sarvam
LLM_PROVIDER=groq
TTS_PROVIDER=sarvam
```

or:

```text
STT_PROVIDER=faster_whisper
LLM_PROVIDER=ollama
TTS_PROVIDER=kokoro
```

Use the exact final environment-variable names defined by the authoritative environment contract.

Do not hardcode provider decisions throughout the codebase.

---

# 7. CONTROLLED AUTOMATIC FAILOVER

Automatic runtime failover is a required product capability unless a later authoritative document explicitly changes it.

Each provider family must be routed through a provider manager / failover policy.

Conceptually:

```text
Voice Engine
    ↓
Provider Manager
    ↓
Primary Provider
    ↓
Success?
 ┌───────┴─────────┐
Yes                 No
 ↓                   ↓
Return          Classify Failure
                     ↓
               Fallback Eligible?
                ┌────┴────┐
               Yes        No
                ↓          ↓
          Fallback       Graceful
          Provider        Failure
```

### Failover-eligible examples

Subject to the attached FRD/provider contract, appropriate candidates generally include:

- timeout,
- connection failure,
- provider unavailable,
- transient 5xx,
- configured rate-limit condition,
- temporary streaming disconnect.

### Failover-ineligible examples

Do not blindly fail over for:

- invalid credentials,
- malformed request,
- unsupported configuration,
- schema/programming errors,
- authorization failures,
- business-rule rejection,
- intentionally cancelled requests.

### Failover rules

- No infinite retry loop.
- No recursive provider cycling.
- Retries must be bounded.
- A fallback must not silently hide a persistent configuration problem.
- Cancellation must propagate.
- Provider switching must be observable.
- Provider switching must be auditable.
- The active call/turn must retain correlation across the switch.
- The application must record both primary failure and fallback result.
- If both primary and fallback fail, use the defined graceful failure behavior.

Every failover event must record enough information to answer:

```text
Which provider failed?
Why?
For which call?
For which turn?
Which fallback was attempted?
Did fallback succeed?
How much latency did failover add?
```

---

# 8. TELEPHONY BOUNDARY

Plivo is the primary production-like telephony provider.

Do not pretend that local STT/LLM/TTS can replace the PSTN network.

If Plivo or external telephony is unavailable:

- the local browser/local-audio mode must still allow the Voice Engine to be exercised,
- production telephony integration may be marked BLOCKED if external credentials or provider access are unavailable,
- do not fabricate successful phone-call verification.

The Voice Engine must remain independent of telephony-specific domain logic through a telephony/media adapter boundary.

---

# 9. CORE ARCHITECTURAL BOUNDARIES

Preserve clear separation between:

```text
Frontend
    ↓
API / WebSocket Layer
    ↓
Application / Voice Orchestration
    ↓
Domain Services
    ↓
Provider Managers
    ↓
External Providers
```

and:

```text
Application / Domain Services
    ↓
Repository / Persistence Layer
    ↓
PostgreSQL
```

and:

```text
RAG Service
    ↓
Embedding Provider
    ↓
Qdrant
```

Do not place:

- major business logic in UI components,
- raw provider SDK logic throughout domain services,
- authorization inside the LLM,
- direct unrestricted database access behind an LLM tool,
- arbitrary command execution behind an LLM tool.

---

# 10. REAL-TIME VOICE PIPELINE

Implement the complete real-time conversational pipeline required by the supplied documents.

The intended conceptual pipeline is:

```text
Caller / Local User
       ↓
Telephony or Local Media Adapter
       ↓
Realtime Media Gateway
       ↓
Audio Normalization / Codec Layer
       ↓
Turn Manager
       ↓
STT Provider Manager
       ↓
Transcript
       ↓
Context Builder
       ├── Conversation History
       ├── Lead Context
       ├── Campaign Objective
       ├── RAG Context
       └── Allowed Tools
       ↓
LLM Provider Manager
       ↓
Structured Assistant Decision
       ├── Speak
       └── Tool Request
              ↓
           Tool Gateway
              ↓
          Domain Service
       ↓
Final Assistant Text
       ↓
TTS Provider Manager
       ↓
Audio
       ↓
Telephony / Local Media Adapter
       ↓
Caller / Local User
```

Do not reduce the project to a REST endpoint that uploads an audio file and waits for a full response if the authoritative documents require real-time streaming.

---

# 11. TURN MANAGEMENT

Implement turn management as a first-class subsystem.

It must behave according to the FRD/journey definitions for:

- listening,
- speech start,
- speech end,
- partial transcript,
- final transcript,
- endpointing,
- silence,
- thinking,
- tool execution,
- speech synthesis,
- assistant playback,
- interruption,
- cancellation,
- call end.

A canonical conceptual lifecycle is:

```text
LISTENING
   ↓
USER_SPEAKING
   ↓
TRANSCRIBING
   ↓
THINKING
   ↓
TOOL_EXECUTION (optional)
   ↓
SYNTHESIZING
   ↓
ASSISTANT_SPEAKING
   ↓
LISTENING
```

For barge-in:

```text
ASSISTANT_SPEAKING
   ↓
USER_INTERRUPTS
   ↓
CANCEL REMAINING GENERATION / AUDIO
   ↓
USER_SPEAKING
```

Do not fake barge-in by merely ignoring audio while the assistant speaks.

Cancellation must propagate to the components that are still doing work when technically possible.

---

# 12. AUDIO HANDLING

Implement audio handling according to the authoritative provider/technical contracts.

Explicitly handle:

- input codec,
- output codec,
- sample rate,
- channel count,
- framing,
- buffering,
- conversion/resampling when required,
- provider-specific media payloads,
- bounded buffering,
- backpressure,
- disconnect behavior.

Do not silently assume every provider uses the same audio format.

Keep codec/resampling responsibilities outside business-domain logic.

---

# 13. RAG

If RAG is in the attached project documents, implement the complete pipeline.

Required conceptual flow:

```text
Document
  ↓
Upload / Register
  ↓
Storage
  ↓
Text Extraction
  ↓
Chunking
  ↓
Embedding
  ↓
Qdrant
  ↓
Tenant-Scoped Retrieval
  ↓
Context Assembly
  ↓
LLM
  ↓
Auditable Retrieval Event
```

Do not implement only a chat UI.

Do not implement retrieval without ingestion.

Do not generate fake citations or source references.

Do not use retrieved document content as trusted system instructions.

Every Qdrant retrieval must enforce the tenant/company boundary defined by the project.

If permission scope is part of the supplied contracts, enforce that too.

No-result behavior must be explicit.

The model must not fabricate tenant-specific product facts merely because retrieval returned nothing.

---

# 14. TOOL CALLING

LLM tool execution must use a controlled backend Tool Gateway.

Required conceptual flow:

```text
LLM
  ↓
Structured Tool Request
  ↓
Tool Gateway
  ↓
Schema Validation
  ↓
Tenant Validation
  ↓
Authorization
  ↓
Business Rule Validation
  ↓
Domain Service
  ↓
Database / External Service
  ↓
Structured Tool Result
  ↓
Conversation State
```

The LLM may request a tool.

The LLM may NOT decide that the user is authorized.

The LLM may NOT bypass tenant boundaries.

The LLM may NOT directly mutate the database.

The LLM may NOT receive arbitrary shell, filesystem, code execution, unrestricted HTTP, or raw database tools.

Expected initial tool family, subject to authoritative docs:

```text
add_call_note
update_lead
schedule_demo
create_followup
set_call_outcome
opt_out_contact
```

Every tool must have:

- explicit purpose,
- input schema,
- allowed caller/context,
- tenant scope,
- validation,
- authorization,
- deterministic execution,
- structured result,
- defined failure behavior,
- audit record.

Tool execution must be idempotent where duplicate provider/event delivery could otherwise create repeated side effects.

---

# 15. OPT-OUT / CALLING SAFETY

The platform is being built for authorized/test/consented calling.

Implement the consent/opt-out fields and workflow required by the supplied documents.

A clear user request such as:

```text
"Don't call me again."
```

must be able to trigger the controlled opt-out workflow.

An opt-out decision must not depend only on free-form LLM memory.

Persist the resulting state.

Future automated campaigns must respect that state according to the business rules.

Do not represent the project as legally cleared for unrestricted commercial calling merely because the technical workflow works.

---

# 16. DATABASE

Use the database defined by the locked stack.

For the current VoiceOps direction, PostgreSQL is expected unless a later authoritative document changes it.

Ensure models cover required:

- IDs,
- tenant ownership,
- timestamps,
- statuses,
- relationships,
- lifecycle,
- provider IDs,
- correlation IDs,
- call data,
- conversation turns,
- transcript events,
- retrieval events,
- tool executions,
- outcomes,
- meetings,
- follow-ups.

Create appropriate indexes where clearly justified by access patterns.

The application must handle an empty database gracefully.

Provide deterministic initialization/seed behavior where required for demo mode.

Do not assume demo entities already exist.

---

# 17. REDIS

Use Redis only for justified transient/runtime concerns defined by the architecture, for example:

- active call state,
- short-lived session state,
- coordination,
- caching,
- stream/event fan-out,
- idempotency support,
- distributed locks if actually required.

Do not move durable business truth into Redis.

The database remains authoritative for durable domain records.

Define failure behavior if Redis is unavailable.

---

# 18. API AND WEBSOCKET CONTRACTS

Implement exactly the supplied canonical contracts.

For every HTTP endpoint define and enforce:

- method,
- route,
- authentication,
- authorization,
- tenant scope,
- request schema,
- response schema,
- status codes,
- validation,
- error shape,
- pagination where applicable.

For every WebSocket protocol define and enforce:

- connection initiation,
- authentication/verification where required,
- message/event types,
- payload schemas,
- call/session identity,
- sequence behavior if required,
- error events,
- close behavior,
- reconnect behavior where required.

Do not create frontend calls to nonexistent backend routes.

Do not create backend APIs that are disconnected from intended journeys unless technically necessary.

Use one consistent response/error philosophy.

---

# 19. FRONTEND

Build a usable product interface sufficient to operate and demonstrate the complete platform.

Implement all pages required by the supplied documents.

Likely areas include:

```text
Dashboard
Calls
Call Detail
Campaigns
Campaign Detail
Leads
Knowledge Base
Provider / System Settings
Observability / Evaluation views where required
```

Every important UI flow must be connected to real backend behavior.

Required states include:

- loading,
- empty,
- success,
- error,
- disabled,
- unavailable provider,
- partial configuration,
- active call,
- completed call,
- failed call.

Do not create:

- nonfunctional buttons,
- fake navigation,
- static live metrics,
- hardcoded AI results presented as runtime output,
- placeholder pages presented as complete.

---

# 20. OBSERVABILITY

Every call must have a stable correlation ID.

Every turn should have a stable turn ID.

Correlate these across:

- logs,
- database events,
- provider calls,
- retrieval,
- tool execution,
- metrics.

Use structured logging.

At minimum capture enough timing information to compute:

```text
STT finalization latency
LLM time-to-first-token
TTS time-to-first-audio
end-to-end conversational turn latency
```

Where technically available, also track:

- audio-stream connection time,
- partial transcript timing,
- first text delta,
- tool-call duration,
- retrieval duration,
- fallback overhead,
- call duration,
- provider errors,
- interruption events,
- cancellation events,
- token usage,
- STT usage,
- TTS usage,
- telephony usage,
- estimated cost.

Expose appropriate Prometheus metrics.

Provide useful Grafana dashboards if required by the attached architecture.

Do not manufacture latency or cost numbers.

---

# 21. COST ACCOUNTING

When deterministic usage/pricing data is available, preserve enough data to estimate:

```text
STT usage
LLM input tokens
LLM output tokens
TTS characters/audio usage
telephony duration
estimated cost per call
estimated cost per connected minute
```

Clearly distinguish:

```text
ESTIMATED COST
```

from:

```text
PROVIDER-BILLED / VERIFIED COST
```

Do not label estimated values as invoices or verified provider charges.

---

# 22. AI EVALUATIONS

Create a meaningful AI evaluation layer for actual AI behavior.

Do not manufacture evaluation numbers.

Create an evaluation dataset covering the scenarios required by the supplied docs.

At minimum, where applicable, include scenarios for:

- normal product question,
- RAG-grounded answer,
- no relevant RAG result,
- tenant isolation,
- correct tool selection,
- invalid tool rejection,
- successful tool execution,
- duplicate tool protection,
- user interruption,
- silence,
- provider timeout,
- primary-provider failure with successful local fallback,
- primary + fallback failure,
- malformed structured model output,
- opt-out request,
- conversation summary,
- code-switching if required by the product.

Measure relevant metrics such as:

- retrieval relevance,
- groundedness,
- answer relevance,
- tool-selection correctness,
- tool completion,
- structured-output validity,
- cross-tenant leakage,
- interruption recovery,
- fallback invocation,
- fallback success,
- turn latency.

Store documentation in:

```text
docs/AI_EVALS.md
```

If credentials/hardware prevent evaluation of a path, mark it BLOCKED.

Do not invent PASS results.

---

# 23. FAILURE BEHAVIOR

Use the supplied Edge Cases + Failure Matrix as authoritative.

Every critical failure must have a deterministic behavior.

Cover at least, where relevant:

- missing environment variable,
- invalid credentials,
- telephony API failure,
- telephony media disconnect,
- unsupported codec,
- malformed media frame,
- STT timeout,
- STT disconnect,
- empty transcript,
- LLM timeout,
- LLM rate limit,
- malformed LLM output,
- TTS timeout,
- TTS disconnect,
- RAG returns nothing,
- Qdrant unavailable,
- Redis unavailable,
- database unavailable,
- tool validation failure,
- tool authorization denial,
- tool service failure,
- duplicate provider event,
- duplicate tool request,
- caller hangs up,
- caller interrupts,
- long silence,
- all providers unavailable,
- local fallback model unavailable,
- insufficient local hardware.

User-facing errors must be understandable.

Do not expose internal stack traces or secrets.

---

# 24. SECURITY BASELINE

Audit for:

- hardcoded secrets,
- real `.env` files,
- leaked API keys,
- authorization bypass,
- missing tenant filtering,
- unsafe file handling,
- prompt injection,
- unrestricted LLM tools,
- arbitrary HTTP/tool execution,
- client-side-only permission enforcement,
- overly permissive CORS,
- sensitive logs,
- raw transcript exposure where not appropriate,
- unvalidated WebSocket payloads,
- duplicate/replay side effects,
- accidental provider-key exposure to frontend.

All secrets must come from environment configuration.

Provide a complete `.env.example`.

Never package genuine credentials.

---

# 25. ENVIRONMENT CONTRACT

Create a complete `.env.example`.

Group variables by function, for example:

```text
Application
Database
Redis
Qdrant
Telephony
STT
LLM
TTS
Local Providers
Observability
Security
Development Tunnel
```

For every environment variable document:

- purpose,
- whether required,
- expected format,
- default if safe,
- which mode needs it.

A developer must be able to understand:

```text
What is required for local-only mode?
What is required for production-like mode?
What is optional?
```

Source code must not reference undocumented environment variables.

---

# 26. LOCAL ZERO-COST RUN MODE

The release must provide a documented mode that can run the Voice Engine without paid cloud AI services when the developer has the required local compute and model dependencies.

This mode should use:

```text
Local audio/browser adapter
Faster-Whisper
Ollama
Kokoro
Local Qdrant
Local PostgreSQL
Local Redis
```

If one local model requires a manual download, clearly document it.

Do not silently download huge models at application startup without explicit documentation.

If hardware constraints prevent a specific local model from running in the build environment, still implement the adapter correctly and mark runtime verification accurately.

---

# 27. PRODUCTION-LIKE RUN MODE

Document the exact steps required to configure:

```text
Plivo
Sarvam
Groq
Sarvam
```

and any secure public HTTPS/WSS endpoint needed for telephony callbacks/media streaming.

Development tunneling may be documented for test use.

Do not describe a temporary development tunnel as the recommended production ingress architecture.

---

# 28. DEPENDENCIES

Pin important dependencies.

Every imported production dependency must be declared.

Remove stale or unused dependencies where practical.

Do not depend on:

- globally installed packages,
- hidden system state,
- undeclared CLI tools,
- files outside the repository,
- local caches.

Do not package:

```text
node_modules/
.venv/
__pycache__/
build caches
IDE metadata
logs
real secrets
private keys
large local model weights
```

unless an explicit requirement says otherwise.

---

# 29. IMPLEMENT VERTICAL SLICES

Do not generate the entire backend and then declare success.

Build coherent vertical slices.

Recommended implementation order, unless the attached build plan overrides it:

```text
Slice 1:
App startup + health + infrastructure + canonical config

Slice 2:
Local media/audio → STT → transcript

Slice 3:
Transcript → LLM → response

Slice 4:
Response → TTS → playback

Slice 5:
Real telephony media adapter

Slice 6:
Turn Manager + barge-in + cancellation

Slice 7:
Persistence + call detail

Slice 8:
RAG ingestion + retrieval

Slice 9:
Tool Gateway + deterministic actions

Slice 10:
Campaign workflow

Slice 11:
Provider failover

Slice 12:
Observability + metrics

Slice 13:
AI evals

Slice 14:
Security + quality audit

Slice 15:
Clean installation + release packaging
```

For each slice:

```text
User Action
    ↓
Frontend / Client
    ↓
Transport
    ↓
Backend
    ↓
Domain Logic
    ↓
Provider / Database
    ↓
Result
    ↓
Visible State
    ↓
Failure Behavior
```

Do not mark a slice complete until its integration path is coherent.

---

# 30. NO PLACEHOLDER COMPLETION

Do not fake completion with:

```text
TODO
COMING SOON
NOT IMPLEMENTED
dummy API response
hardcoded AI response
fake success toast
nonfunctional button
static "live" metrics
empty function
mock provider represented as real
placeholder screen represented as complete
```

Mocks may exist only when clearly identified as development/test fixtures and never as the claimed production path.

If a required feature cannot be completed, record it explicitly in the implementation report.

---

# 31. RUNTIME VERIFICATION

Actually run everything that can reasonably be run in the available environment.

Verify:

- dependency installation,
- infrastructure startup,
- database initialization,
- Redis connectivity,
- Qdrant connectivity,
- backend startup,
- frontend startup,
- API health,
- WebSocket path,
- local Voice AI path,
- configured external providers where credentials exist,
- RAG path,
- tool path,
- observability endpoints,
- critical UI routes.

A code review is not runtime verification.

Do not use the word VERIFIED unless the behavior was actually exercised.

---

# 32. CRITICAL JOURNEY VERIFICATION

Exercise the authoritative End-to-End User Journeys.

At minimum, if supported by available credentials/environment, verify a primary journey equivalent to:

```text
Start VoiceOps
  ↓
Open application
  ↓
Select/create lead
  ↓
Select/create campaign
  ↓
Select knowledge base
  ↓
Initiate call
  ↓
Call connects
  ↓
User speaks
  ↓
STT produces transcript
  ↓
LLM responds
  ↓
TTS audio is played
  ↓
Second turn succeeds
  ↓
User asks a business question
  ↓
RAG supplies relevant context
  ↓
User requests an action
  ↓
Tool Gateway executes allowed action
  ↓
Call ends
  ↓
Summary is generated
  ↓
Outcome is stored
  ↓
Transcript/tool/retrieval/latency events are visible
```

Also verify a fallback journey where possible:

```text
Primary AI provider intentionally unavailable
  ↓
Eligible failure detected
  ↓
Fallback provider invoked
  ↓
Conversation continues
  ↓
Failover event visible in logs/metrics/call detail
```

---

# 33. CLEAN INSTALLATION VERIFICATION

Before final packaging, simulate a fresh developer setup as closely as possible.

Verify the release does not depend on:

- your existing shell state,
- temporary paths,
- undeclared packages,
- unpublished local files,
- previously running services,
- local secrets,
- hidden database contents.

The target developer journey is:

```text
Extract ZIP
  ↓
Read START_HERE.md
  ↓
Install prerequisites
  ↓
Copy .env.example
  ↓
Choose runtime mode
  ↓
Start infrastructure
  ↓
Initialize database
  ↓
Start backend
  ↓
Start frontend
  ↓
Open application
  ↓
Run local voice demo
```

Production-like mode may require provider credentials and telephony configuration, but local mode should not require cloud AI credentials.

---

# 34. REQUIRED RELEASE DOCUMENTATION

Create at minimum:

```text
START_HERE.md
README.md
.env.example
docs/ASSUMPTIONS_AND_DECISIONS.md
docs/ARCHITECTURE.md
docs/PROVIDER_CONFIGURATION.md
docs/AI_EVALS.md
docs/VERIFICATION_REPORT.md
docs/REQUIREMENTS_TRACEABILITY.md
docs/IMPLEMENTATION_REPORT.md
```

Add additional documents only when they materially improve operation or verification.

---

# 35. START_HERE.md

This must be the fastest path from ZIP to running project.

Include:

## Prerequisites

Exact tools and important versions.

## Runtime Modes

Explain clearly:

```text
Local Mode
Production-like Mode
Hybrid / Failover Mode
```

## Environment Setup

Exact `.env` setup.

## Infrastructure Startup

Exact commands.

## Backend Startup

Exact commands.

## Frontend Startup

Exact commands.

## Database Initialization

Exact commands.

## Local Voice Demo

Exact steps.

## Production-like Provider Setup

Exact steps.

## URLs

Actual local URLs.

## Troubleshooting

Only high-probability issues.

Keep it concise enough to scan.

---

# 36. README.md

The README should explain:

- problem,
- solution,
- product scope,
- architecture,
- primary workflow,
- provider strategy,
- local fallback,
- RAG,
- tool calling,
- observability,
- technology stack,
- demo flow,
- limitations,
- setup pointer.

Do not duplicate the entire START_HERE file.

---

# 37. IMPLEMENTATION_REPORT.md

Include:

## Implemented

What actually exists.

## Architecture

Important decisions.

## Voice Pipeline

What was built.

## Provider Strategy

Primary and fallback providers.

## RAG

Actual implementation.

## Tools

Actual implementation and security boundary.

## Observability

Actual metrics/logging.

## Security

Controls actually present.

## Runtime Verification

What was actually run.

## AI Evaluations

Actual executed results.

## External Dependencies

Credentials/services/hardware needed.

## Known Limitations

Anything incomplete or blocked.

## Demo Path

The strongest exact sequence for demonstrating the project.

Never hide limitations.

---

# 38. REQUIREMENTS TRACEABILITY

Create:

```text
docs/REQUIREMENTS_TRACEABILITY.md
```

Map:

```text
Requirement
→ implementation
→ runtime verification status
```

For AI:

```text
AI requirement
→ implementation
→ evaluation
→ result
```

Allowed statuses:

```text
VERIFIED
AI-EVALUATED
IMPLEMENTED — NOT RUNTIME VERIFIED
BLOCKED BY EXTERNAL SERVICE
BLOCKED BY HARDWARE
NOT IMPLEMENTED
```

Do not use vague claims such as:

```text
should work
probably works
appears complete
```

---

# 39. VERIFICATION_REPORT.md

Record actual verification evidence.

Include, where available:

- commands executed,
- services started,
- endpoints reached,
- provider integrations exercised,
- critical journeys completed,
- fallback path exercised,
- observed failures,
- fixes made,
- remaining blocks.

Do not claim a real phone-call PASS unless a real phone-call path was exercised.

Do not claim local model PASS unless the local model was actually run.

---

# 40. QUALITY AUDIT

Before release, inspect the whole codebase for:

- broken imports,
- unused imports,
- circular imports,
- duplicate models,
- conflicting API contracts,
- duplicate routes,
- inconsistent naming,
- stale mocks,
- debug shortcuts,
- missing dependency declarations,
- invalid environment references,
- placeholder UI,
- TODOs affecting required functionality,
- dead code,
- duplicated provider logic,
- provider SDK leakage into domain logic,
- tenant-scope gaps,
- tool authorization gaps.

Fix material issues before packaging.

---

# 41. RELEASE GATE

Do not create the final ZIP immediately after generating source code.

First confirm:

```text
□ all supplied documents were read
□ conflicts were reconciled
□ locked stack was respected
□ standalone scope was preserved
□ provider abstraction exists
□ production-primary providers are supported
□ local fallback providers are supported
□ manual provider switching works
□ controlled automatic failover exists
□ failover is observable
□ local zero-cost mode is documented
□ frontend/backend contracts align
□ database models align
□ tenant boundaries are enforced
□ RAG pipeline is complete
□ tool gateway is controlled
□ important failure states exist
□ observability exists
□ AI evals exist
□ no real secrets are packaged
□ required dependencies are declared
□ startup was actually attempted
□ local critical journey was exercised where possible
□ external-provider journey was exercised where credentials permit
□ documentation matches reality
□ clean-install verification was attempted
□ release folder is clean
```

If a gate item fails:

1. fix it if reasonably possible,
2. re-run the relevant verification,
3. otherwise document the block explicitly.

Do not silently ignore failed gates.

---

# 42. RELEASE PACKAGE STRUCTURE

Use a clean structure appropriate to the locked stack.

A reasonable shape is:

```text
voiceops/
│
├── START_HERE.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── frontend/
├── backend/
├── scripts/
├── infra/
├── docs/
└── other required configuration
```

Do not force this exact tree if the authoritative technical architecture defines a better equivalent.

The ZIP must contain the project root directly in a sensible structure.

Use a meaningful filename such as:

```text
voiceops-v1-production-ready.zip
```

---

# 43. VERIFY THE ZIP ITSELF

After creating the ZIP:

1. inspect its file list,
2. verify required files exist,
3. verify secret files are absent,
4. verify junk/build caches are absent,
5. verify README/START_HERE paths are correct,
6. verify commands referenced in documentation match actual files,
7. if possible, extract the ZIP to a clean temporary directory,
8. repeat the clean-start verification from the extracted release.

Do not deliver a ZIP that was never inspected.

---

# 44. IMPLEMENTATION BEHAVIOR

While executing:

- continue through implementation rather than stopping after every minor decision,
- use engineering judgment for small missing details,
- document assumptions,
- fix problems discovered during runtime verification,
- re-run failed flows after fixes,
- keep the implementation consistent across files,
- prefer simple reliable architecture over needless complexity,
- do not add unnecessary microservices,
- do not add Kubernetes unless explicitly required,
- do not add large conventional test frameworks unless explicitly required,
- do not introduce new infrastructure just to appear production-ready.

Production-minded means:

```text
clear boundaries
reliability
observability
security
repeatable startup
failure handling
measured behavior
```

not:

```text
maximum number of technologies
```

---

# 45. DEFINITION OF VERIFIED

Use these terms precisely.

## IMPLEMENTED

Source exists and is connected through required layers.

## VERIFIED

The relevant runtime behavior was actually exercised successfully.

## AI-EVALUATED

The AI capability was actually executed against the defined evaluation cases and results were recorded.

## UNVERIFIED

Implementation exists but could not be exercised.

## BLOCKED

Verification depends on unavailable credentials, provider service, infrastructure, hardware, or another external dependency.

Never mark a feature VERIFIED because the code looks correct.

---

# 46. DO NOT FABRICATE

Never fabricate:

- successful phone calls,
- API responses,
- provider availability,
- latency values,
- throughput,
- concurrency,
- AI eval scores,
- cost savings,
- RAG quality,
- fallback success,
- tool success,
- deployment success.

If a provider credential is unavailable, use the local path where possible and mark the production provider path BLOCKED.

If a local model cannot run because of hardware, mark it BLOCKED BY HARDWARE.

Truthful evidence is more important than optimistic wording.

---

# 47. FINAL EXECUTION SEQUENCE

Follow this sequence.

## Stage 1 — Documentation Intake

- inventory files,
- read all documents,
- identify locked decisions,
- reconcile conflicts,
- record assumptions.

## Stage 2 — Architecture Freeze

Establish internally consistent:

- domain model,
- provider interfaces,
- call lifecycle,
- turn lifecycle,
- API contracts,
- WebSocket contracts,
- database schema,
- RAG flow,
- tool flow,
- observability model,
- environment contract.

## Stage 3 — Repository Initialization

Create clean project structure and dependency manifests.

## Stage 4 — Infrastructure

Bring up PostgreSQL, Redis, Qdrant, observability services as required.

## Stage 5 — Local Voice Vertical Slice

Make local audio → STT → LLM → TTS → playback work through the real Voice Engine.

## Stage 6 — Production Provider Adapters

Implement Sarvam STT, Groq LLM, Sarvam TTS.

## Stage 7 — Telephony

Implement Plivo integration and bidirectional streaming.

## Stage 8 — Turn Manager

Implement endpointing, interruption, cancellation, silence behavior.

## Stage 9 — Persistence

Persist calls, turns, events, outcomes and related domain records.

## Stage 10 — RAG

Implement ingestion, indexing, retrieval, context assembly and auditing.

## Stage 11 — Tools

Implement controlled business tools and tool audit trail.

## Stage 12 — Campaign Workflow

Implement the complete standalone business workflow defined in the journeys.

## Stage 13 — Provider Failover

Implement manual selection + controlled automatic primary→fallback behavior.

## Stage 14 — Frontend Completion

Connect all required UI states to real backend behavior.

## Stage 15 — Observability

Implement structured logs, metrics, latency and failover visibility.

## Stage 16 — AI Evals

Create and execute meaningful evaluation cases where possible.

## Stage 17 — Security + Quality Audit

Inspect and fix material issues.

## Stage 18 — Runtime Verification

Start and exercise the system.

## Stage 19 — Critical Journey Verification

Run the documented journeys.

## Stage 20 — Clean Installation Verification

Reproduce first-time setup.

## Stage 21 — Release Documentation

Generate accurate release docs.

## Stage 22 — Final ZIP

Package only after the release gates are complete.

---

# 48. FINAL RESPONSE FORMAT

When the complete implementation cycle is finished, return a concise execution summary with:

1. **ZIP download path/link**
2. **Implementation status**
3. **Runtime verification status**
4. **Local-mode verification status**
5. **Production-provider verification status**
6. **Real telephony verification status**
7. **Fallback verification status**
8. **AI evaluation status**
9. **Important external requirements**
10. **Known limitations / blocked items**
11. **Instruction to begin with `START_HERE.md`**

Do not dump the entire implementation report into the chat if it is already included inside the ZIP.

---

# 49. FINAL COMMAND

Now execute the project end to end.

Do not stop at planning.

Do not stop at scaffolding.

Do not stop after generating files.

Read the supplied VoiceOps documentation, reconcile it, implement the complete application, run what can be run, fix what fails, verify the critical journeys, evaluate the AI behavior, audit security and quality, perform clean-install verification, and package the final clean release ZIP.

The final project must be the closest possible thing to a production-ready, end-to-end working VoiceOps release that the available environment and external credentials genuinely permit.

Where a real external dependency prevents verification, preserve a functional local fallback wherever the architecture defines one, mark the external path accurately as BLOCKED, and never fabricate success.
