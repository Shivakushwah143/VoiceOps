# VoiceOps — Product Requirements Document (PRD)

**Document Version:** 1.0  
**Status:** Draft for Architecture Lock  
**Product Type:** Standalone Real-Time Voice AI Platform  
**Primary Goal:** Build and verify a production-minded Voice AI system independently, then later integrate the proven engine into SynTask.  
**Initial Environment:** Local-first runtime with real/testable external AI and telephony services where free tiers or trial credits permit.  
**Future Integration:** SynTask CRM / Sales / Meetings / Tasks / Knowledge Base

---

## 1. Product Vision

VoiceOps is a standalone, production-minded real-time Voice AI platform that can place or receive testable phone calls, understand a human speaker in real time, reason using an LLM, retrieve tenant-scoped business knowledge, execute approved business actions through controlled tools, synthesize speech, and maintain an auditable record of the entire interaction.

The initial product must prove the complete real-world voice-agent loop before any SynTask integration:

```text
Phone
  ↓
Telephony
  ↓
Streaming Audio
  ↓
Speech-to-Text
  ↓
Turn Management
  ↓
Context + RAG
  ↓
LLM Reasoning
  ↓
Tool Execution
  ↓
Text-to-Speech
  ↓
Streaming Audio
  ↓
Phone
```

VoiceOps is not intended to remain a separate commercial product forever. It is the isolated engineering and validation layer from which a future **SynTask Voice Agent** capability can be integrated safely.

---

## 2. Problem Statement

Building a voice AI feature directly inside SynTask would combine too many unknowns at once:

- telephony
- bidirectional streaming
- audio codecs
- speech recognition
- turn detection
- interruption handling
- LLM orchestration
- retrieval
- tool calling
- CRM state changes
- latency
- observability
- provider failures
- multi-tenancy
- cost tracking
- production deployment

This creates a high risk of architecture drift, hidden coupling, unreliable behavior, and difficult debugging.

The product therefore needs a standalone environment where the complete voice workflow can be built, measured, verified, and productionized independently.

---

## 3. Product Objective

Build a standalone Voice AI platform that can complete a real or testable phone conversation using production-style external services while keeping the core application runnable locally.

The first meaningful product milestone is:

> A verified phone receives or participates in a real test call. The user speaks naturally. The system streams audio to STT, produces a transcript, generates a context-aware LLM response, converts the response to speech, plays it back over the same call, and records latency and call events for the complete turn.

The platform must later support:

- tenant-scoped RAG
- controlled business tools
- campaigns
- lead context
- call outcomes
- summaries
- follow-up actions
- observability
- AI evaluations
- local provider fallback
- future SynTask integration

---

## 4. Product Principles

### 4.1 Real workflow before UI polish

The primary voice loop must work end to end before building a large dashboard.

### 4.2 Production-style services first, local fallbacks second

The preferred initial runtime is:

```text
Telephony → Plivo
STT       → Sarvam
LLM       → Groq
TTS       → Sarvam
```

The product must also support local fallback providers:

```text
STT → Faster-Whisper
LLM → Ollama
TTS → Kokoro
```

Local providers are fallback and development adapters, not a separate application architecture.

### 4.3 Provider independence

Business logic must not depend directly on a specific STT, LLM, TTS, telephony, or vector database SDK.

Every external provider must be accessed through an explicit provider interface.

### 4.4 Deterministic security boundaries

The LLM may request a tool action but may not directly authorize or execute protected state changes.

Backend application logic remains authoritative.

### 4.5 Measured claims only

Latency, cost, quality, call completion, retrieval accuracy, and other metrics must be based on executed runs.

No performance number may be presented as verified unless it was actually measured.

### 4.6 Build for eventual SynTask integration

The standalone domain should resemble the future SynTask use case without importing or depending on the SynTask codebase.

The Voice Engine must remain reusable behind a future SynTask adapter.

---

## 5. Target Users

### 5.1 Developer / AI Engineer

Primary initial user.

Needs to:

- configure providers
- launch the local application
- start test calls
- observe streaming events
- inspect transcripts
- view latency
- debug provider failures
- test local fallbacks
- run AI evaluations

### 5.2 Sales Operator

Later product user.

Needs to:

- create a campaign
- select leads
- select a knowledge base
- define a call objective
- start calls
- monitor calls
- inspect outcomes
- review summaries
- inspect scheduled follow-ups

### 5.3 Administrator

Needs to:

- configure tenant-level settings
- manage provider credentials
- control available tools
- inspect audit logs
- manage knowledge sources
- inspect usage and cost

---

## 6. Primary Use Case

The initial business use case is an **AI Sales Calling Agent**.

Example:

```text
Lead
Name: Rahul
Company: ABC Manufacturing
Interest: HRMS
Previous note: Asked about biometric attendance

AI calls Rahul
        ↓
Rahul asks:
"Does your system support biometric attendance?"
        ↓
VoiceOps retrieves approved knowledge
        ↓
AI answers using retrieved context
        ↓
Rahul says:
"Schedule a demo tomorrow."
        ↓
LLM requests schedule_demo tool
        ↓
Backend validates the request
        ↓
Meeting is created
        ↓
Call finishes
        ↓
Summary + outcome + follow-up are stored
```

The standalone project will implement its own minimal business entities so that this full workflow can be tested without SynTask.

---

## 7. Scope

### 7.1 V1 — Real-Time Voice Core

V1 must provide:

- real or testable telephony connection
- bidirectional audio streaming
- WebSocket-based media gateway
- streaming speech-to-text
- conversational turn management
- LLM response generation
- streaming or low-latency text-to-speech
- playback to caller
- conversation history
- per-turn event tracking
- latency tracking
- call lifecycle tracking
- provider abstraction
- configuration through environment variables
- local development environment

### 7.2 V2 — Conversational Reliability

V2 must add:

- voice activity detection
- endpointing
- silence handling
- barge-in
- interruption cancellation
- partial transcripts
- reconnect/error behavior
- timeout handling
- malformed provider response handling
- bounded retry behavior

### 7.3 V3 — RAG

V3 must add:

- knowledge-base creation
- document ingestion
- text extraction
- chunking
- embeddings
- Qdrant storage
- tenant-scoped retrieval
- permission-aware retrieval where applicable
- retrieved-context assembly
- retrieval trace storage
- no-result behavior

### 7.4 V4 — Tool-Calling Agent

V4 must add controlled tools such as:

- `update_lead`
- `add_call_note`
- `schedule_demo`
- `create_followup`
- `set_call_outcome`
- `opt_out_contact`

Every tool must have:

- purpose
- schema
- authorization rules
- validation
- failure behavior
- audit record

### 7.5 V5 — Voice Campaign Product

V5 must add:

- leads
- campaigns
- campaign objectives
- knowledge-base selection
- call queue
- call attempt records
- call statuses
- live monitoring
- transcripts
- call summaries
- objections
- disposition/outcome
- follow-up status

### 7.6 V6 — Observability and AI Evaluation

V6 must add:

- structured logs
- request/call correlation IDs
- STT latency
- LLM time-to-first-token
- TTS time-to-first-audio
- end-to-end turn latency
- provider error counts
- call duration
- token usage
- estimated cost
- interruption events
- tool-call events
- retrieval events
- Prometheus metrics
- Grafana dashboards
- evaluation datasets
- evaluation reports

### 7.7 V7 — Productionization

V7 must add:

- Dockerized services
- production configuration
- health/readiness endpoints
- safe secret management
- durable database configuration
- worker/background processing where required
- deployment documentation
- public secure WebSocket endpoint
- provider credential configuration
- production observability
- clean release packaging

### 7.8 V8 — SynTask Integration

SynTask integration is explicitly out of scope for the standalone build.

After VoiceOps is verified, a future integration will replace standalone business-domain adapters with SynTask services/APIs.

Expected future mappings:

```text
VoiceOps Lead        → SynTask Lead
VoiceOps Campaign    → SynTask Sales Campaign
VoiceOps Meeting     → SynTask Meeting
VoiceOps Follow-up   → SynTask Task / Activity
VoiceOps Knowledge   → SynTask Knowledge / Documents
VoiceOps User/Tenant → SynTask User / Company
```

The Voice Engine itself should not require major redesign.

---

## 8. Out of Scope for Initial V1

The following are not required for the first working vertical slice:

- SynTask codebase integration
- large-scale outbound campaign execution
- production billing
- enterprise SSO
- Kubernetes
- microservices
- complex workflow builders
- multi-region deployment
- advanced analytics
- custom model training
- fine-tuning
- arbitrary LLM-generated code execution
- unrestricted database access from the LLM
- unsupported phone-number automation
- real commercial calling without appropriate consent/compliance

---

## 9. Core Functional Requirements

### FR-P-001 — Call Session

The system shall create a unique call session for every voice call.

A call session must track:

- call ID
- provider call ID
- tenant
- lead/contact
- campaign if applicable
- start time
- end time
- status
- provider configuration
- conversation state

### FR-P-002 — Streaming Audio Input

The media gateway shall receive audio continuously from the configured telephony adapter.

The system must not require waiting for a complete call recording before processing speech.

### FR-P-003 — Speech Recognition

The configured STT provider shall process incoming audio and return transcript events.

The architecture must support partial and final transcripts where the provider supports them.

### FR-P-004 — Turn Management

The system shall determine when the user has completed a conversational turn.

Turn management must eventually support:

- speech start
- speech end
- endpoint detection
- silence timeout
- interruption
- cancellation

### FR-P-005 — LLM Orchestration

The system shall construct an LLM request from approved context including:

- system policy
- call objective
- conversation history
- lead/contact context
- retrieved knowledge
- permitted tools

### FR-P-006 — Speech Synthesis

The configured TTS provider shall convert approved assistant text into audio suitable for playback to the caller.

### FR-P-007 — Audio Playback

Generated audio shall be returned through the telephony connection.

### FR-P-008 — Provider Abstraction

The following provider types must use interfaces:

- TelephonyProvider
- STTProvider
- LLMProvider
- TTSProvider
- EmbeddingProvider

Switching providers must not require rewriting conversation-domain logic.

### FR-P-009 — Local Fallback

The application shall support local provider alternatives:

- Faster-Whisper STT
- Ollama LLM
- Kokoro TTS

A local fallback may be manually selected through configuration.

Automatic failover may be added later after explicit policy is defined.

### FR-P-010 — RAG

When the user asks a question that requires business/domain knowledge, the system shall retrieve relevant content from the configured tenant knowledge base.

Retrieval must always be tenant-scoped.

### FR-P-011 — Tool Calling

The LLM may request only tools explicitly available to the current session.

Requested tools shall pass through a backend Tool Gateway before execution.

### FR-P-012 — Call Summary

After a completed call, the system shall generate and persist a structured summary.

Potential fields:

- summary
- outcome
- interest level
- objections
- user commitments
- business commitments
- follow-up actions
- opt-out status

### FR-P-013 — Audit Trail

The platform shall record significant events including:

- call started
- call connected
- audio stream opened
- STT partial
- STT final
- LLM request
- LLM response
- retrieval
- tool requested
- tool accepted/rejected
- TTS requested
- TTS audio ready
- interruption
- call ended
- failure

Sensitive values must not be logged unnecessarily.

### FR-P-014 — Latency Measurement

The platform shall capture timestamps sufficient to compute at minimum:

```text
STT finalization latency
LLM time-to-first-token
TTS time-to-first-audio
end-to-end conversational turn latency
```

Measured values must be tied to an individual call and turn.

### FR-P-015 — Cost Accounting

Where provider usage data or deterministic pricing data is available, the application should record enough usage information to estimate:

- STT usage
- LLM input/output tokens
- TTS usage
- telephony duration
- cost per call
- cost per connected minute

Estimated and provider-billed cost must be labeled separately.

---

## 10. Non-Functional Requirements

### 10.1 Reliability

A failure in one provider must not crash the entire application process.

The caller must receive a safe fallback response or the call must terminate gracefully according to policy.

### 10.2 Low Latency

The architecture must prioritize streaming behavior.

The system shall measure actual latency rather than rely on a fixed claimed target during early development.

Optimization decisions must be based on measured bottlenecks.

### 10.3 Security

The system must:

- load secrets from environment configuration
- never expose provider keys to the frontend
- enforce tenant boundaries on the backend
- validate tool inputs
- restrict tool availability
- avoid arbitrary command execution
- treat retrieved document content as untrusted
- prevent RAG content from replacing system security instructions

### 10.4 Multi-Tenancy

Every tenant-owned entity must include a tenant/company boundary.

This includes at minimum:

- lead
- campaign
- knowledge base
- document
- call
- transcript
- tool action

Cross-tenant retrieval or state mutation is forbidden.

### 10.5 Observability

Every call must have a correlation identifier shared across:

- logs
- metrics
- call record
- transcript
- tool events
- retrieval events

### 10.6 Maintainability

Voice-domain orchestration must remain separate from:

- provider SDK code
- persistence code
- API routing
- frontend components

### 10.7 Portability

The core application should be runnable locally through documented setup.

The production deployment should not rely on hidden local files or undeclared global dependencies.

---

## 11. Proposed Technology Stack

### Backend

- Python
- FastAPI
- asyncio
- WebSockets
- Pydantic

### Telephony

Primary:

- Plivo

Future adapters may include other SIP/PSTN providers.

### STT

Primary:

- Sarvam streaming STT

Fallback:

- Faster-Whisper

### LLM

Primary:

- Groq-hosted model through a provider abstraction

Fallback:

- Ollama local model

The exact production model identifier must remain configuration rather than business logic.

### TTS

Primary:

- Sarvam streaming/low-latency TTS

Fallback:

- Kokoro

### Vector Database

- Qdrant

### Persistence

- PostgreSQL

### State / Cache

- Redis

### Observability

- structured application logs
- Prometheus
- Grafana

### Local Exposure During Telephony Development

- secure development tunnel or equivalent temporary HTTPS/WSS endpoint

This is development infrastructure only and must not be treated as the production deployment architecture.

---

## 12. Core Domain Entities

### Tenant

Represents an isolated organization.

### User

Represents an operator or administrator.

### Lead

Represents a person/contact the agent may call.

Expected concepts:

- identity
- phone number
- company
- interest
- stage/status
- notes
- consent/opt-out state

### Campaign

Defines a calling objective and set of leads.

### KnowledgeBase

Tenant-owned collection of approved business knowledge.

### Document

Source material ingested into a knowledge base.

### Call

Represents one call attempt/session.

### ConversationTurn

Represents one user/assistant interaction cycle.

### TranscriptEvent

Stores speech-recognition output and timing.

### RetrievalEvent

Stores what knowledge was retrieved for a turn.

### ToolExecution

Stores a requested and executed/rejected tool action.

### CallOutcome

Represents the final structured result of the conversation.

### Meeting

Standalone equivalent of a future SynTask meeting.

### FollowUp

Standalone equivalent of a future SynTask task/activity.

---

## 13. Call Lifecycle

Canonical high-level call states:

```text
CREATED
  ↓
QUEUED
  ↓
DIALING
  ↓
RINGING
  ↓
CONNECTED
  ↓
ACTIVE
  ↓
ENDING
  ↓
COMPLETED
```

Failure branches may include:

```text
NO_ANSWER
BUSY
FAILED
CANCELLED
REJECTED
```

Provider-specific statuses must be mapped into this canonical application state model.

---

## 14. Conversation Turn Lifecycle

Canonical turn states:

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

Interruption must allow:

```text
ASSISTANT_SPEAKING
   ↓
USER_INTERRUPTS
   ↓
CANCEL_REMAINING_AUDIO
   ↓
USER_SPEAKING
```

---

## 15. RAG Product Rules

RAG exists to answer domain-specific questions using approved tenant knowledge.

The complete product behavior must include:

```text
Document
  ↓
Upload / Registration
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
```

Rules:

1. Retrieval must include tenant filtering.
2. Retrieved content is untrusted input.
3. Retrieved text may not override system security instructions.
4. Empty retrieval must have an explicit safe behavior.
5. Retrieval events must be observable.
6. Generated answers must not fabricate company-specific facts when knowledge is unavailable.
7. Source information should be stored for audit even when source citations are not spoken aloud during the phone call.

---

## 16. Tool-Calling Product Rules

The LLM may suggest an action but the backend decides whether it can execute.

Canonical flow:

```text
LLM
  ↓
Tool Request
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
Service Layer
  ↓
Database / External Service
  ↓
Structured Tool Result
  ↓
LLM / Call State
```

The LLM must never receive unrestricted:

- shell access
- raw database access
- filesystem access
- arbitrary HTTP access
- arbitrary code execution

---

## 17. Initial Tool Set

### `add_call_note`

Stores a note associated with the lead and call.

### `update_lead`

Updates only explicitly allowed lead fields.

### `schedule_demo`

Creates a demo/meeting request with validated time and participant data.

### `create_followup`

Creates a follow-up action after the call.

### `set_call_outcome`

Stores a valid outcome from a controlled enum.

### `opt_out_contact`

Marks the contact as not eligible for future automated calling.

This tool must take precedence over campaign continuation.

---

## 18. UI Requirements

The initial UI should remain focused.

### Dashboard

Show:

- active calls
- recent calls
- success/failure status
- latency summary
- provider status

### Calls

Show:

- lead/contact
- campaign
- duration
- call status
- transcript
- call summary
- tool actions
- retrieved knowledge events
- timing events
- errors

### Campaigns

Support:

- create campaign
- define objective
- select leads
- choose knowledge base
- start/pause campaign
- inspect progress

### Leads

Support basic standalone lead management sufficient for testing voice workflows.

### Knowledge Base

Support document registration/upload and ingestion status.

### Settings

Support provider configuration state without exposing secrets back to the browser.

---

## 19. Error and Failure Expectations

The product must define behavior for at least:

- invalid provider credentials
- telephony connection failure
- WebSocket disconnect
- unsupported audio
- STT unavailable
- STT timeout
- empty transcript
- LLM unavailable
- LLM timeout
- malformed LLM structured output
- TTS unavailable
- TTS timeout
- retrieval returns nothing
- Qdrant unavailable
- Redis unavailable
- database unavailable
- tool validation failure
- tool authorization rejection
- meeting creation failure
- caller interruption
- long silence
- caller hangs up
- duplicate provider event
- duplicate tool request
- opt-out request

Detailed exact behavior belongs in the FRD and Failure Matrix.

---

## 20. Compliance and Safety Requirements

The development environment may use only authorized/test/consented numbers.

The application must be designed to support:

- consent status
- consent source
- consent timestamp
- do-not-call / opt-out state
- opt-out timestamp
- campaign purpose
- call audit information

If a user clearly requests not to receive future calls, the product must allow that state to be recorded immediately.

Production commercial calling must not be treated as permitted merely because the technical call workflow functions.

---

## 21. AI Evaluation Requirements

VoiceOps must eventually maintain a small evaluation dataset covering realistic scenarios.

Minimum evaluation categories:

- correct response using RAG
- no-answer RAG behavior
- tenant isolation
- correct tool selection
- invalid tool request rejection
- tool execution success
- interruption recovery
- silence handling
- provider timeout
- malformed output recovery
- opt-out handling
- code-switching where applicable
- conversation summary correctness

Potential metrics:

- tool-selection accuracy
- tool-completion rate
- retrieval relevance
- groundedness
- structured-output validity
- cross-tenant leakage count
- interruption recovery rate
- turn latency p50
- turn latency p95
- STT latency
- LLM TTFT
- TTS TTFB

Evaluation results must be generated from actual executions.

---

## 22. Product Success Criteria

The standalone VoiceOps project is considered successful when the following are demonstrably true:

### Core Voice

- a real/testable call can connect
- inbound caller audio reaches the backend
- speech is transcribed
- LLM generates a relevant response
- TTS audio is generated
- caller hears the response
- multiple conversational turns can complete

### Conversational Behavior

- silence is handled predictably
- caller interruption can stop current assistant playback
- call state remains consistent
- errors do not crash the application

### RAG

- tenant documents can be ingested
- tenant-scoped retrieval works
- retrieved context influences the answer
- missing knowledge is handled without fabricated business facts

### Tools

- approved tools can execute
- invalid tool calls are rejected
- every execution is auditable

### Observability

- every call has correlated logs/events
- stage-level latency can be calculated
- provider failures are visible
- actual measured results can be reported

### Portability

- another developer can configure and launch the project from documentation
- no secrets are required in source control
- required services and environment variables are documented

---

## 23. First Release Definition of Done

The first release is **not** complete because UI screens exist.

The first release is complete only when the primary runtime journey is actually exercised:

```text
Developer starts local VoiceOps
        ↓
Local infrastructure becomes healthy
        ↓
Telephony endpoint is reachable
        ↓
Developer initiates test call
        ↓
Verified phone rings
        ↓
Caller answers
        ↓
Caller speaks
        ↓
Backend receives streaming audio
        ↓
STT generates transcript
        ↓
LLM generates response
        ↓
TTS generates audio
        ↓
Caller hears AI response
        ↓
At least one additional turn succeeds
        ↓
Caller hangs up
        ↓
Call status becomes completed
        ↓
Transcript is persisted
        ↓
Timing events are persisted
        ↓
Call can be inspected in UI/API
```

The exact detailed version of this flow belongs in the End-to-End User Journey document.

---

## 24. Future SynTask Integration Contract

VoiceOps must expose or encapsulate reusable boundaries so that SynTask can later provide:

- tenant/company identity
- authenticated user identity
- lead context
- campaign context
- document/knowledge context
- meeting actions
- task/follow-up actions
- lead-state mutation
- call activity storage

Expected future architecture:

```text
SynTask
   ↓
Voice Agent Application Layer
   ↓
VoiceOps Engine
   ↓
Telephony / STT / LLM / TTS / RAG
```

SynTask remains authoritative for:

- authentication
- authorization
- company boundaries
- CRM business rules
- protected state changes

The Voice AI layer must never become the authority for those decisions.

---

## 25. Open Decisions for FRD Lock

The PRD intentionally does not finalize the following implementation-level decisions. They must be resolved in the FRD or technical design:

- exact Plivo call direction used for the first verified demo
- exact audio codec and sample-rate strategy
- exact Sarvam STT endpoint/configuration
- exact Sarvam TTS voice/configuration
- exact Groq model
- exact embedding model
- exact chunking strategy
- exact call queue design
- exact VAD/endpointing thresholds
- exact retry policies
- exact timeout values
- exact database schema
- exact event schema
- exact WebSocket message schema
- exact provider failover policy
- exact structured LLM response schema
- exact campaign scheduling rules
- exact consent workflow
- exact observability metric names

These decisions must not be silently invented during implementation.

---

## 26. Documentation Sequence

After this PRD is approved, the project documentation should continue in this order:

```text
PRD
 ↓
FRD
 ↓
Detailed End-to-End User Journeys
 ↓
Technical Architecture
 ↓
Data Model
 ↓
API + WebSocket Contracts
 ↓
Provider Contracts
 ↓
AI / RAG / Tool Contracts
 ↓
Failure Matrix
 ↓
Acceptance Criteria Matrix
 ↓
Build Plan
 ↓
Astra Implementation Prompt
```

The implementation should begin only after the important product and system decisions are explicit enough that Astra does not need to invent missing workflows.

---

# PRD Status

**Current state:** Ready for review.

**Next required artifact:** `VoiceOps_FRD_v1.0.md`
