# VoiceOps — Functional Requirements Document

**Version:** 1.0  
**Date:** 2 October 2026  
**Status:** DRAFT FOR USER REVIEW — NOT APPROVED OR FROZEN  
**Phase:** Documentation + Architecture Freeze  
**Artifact:** 2 of 12 in the user-defined documentation sequence  
**Product:** Standalone production-minded real-time Voice AI platform  
**Next artifact after approval:** Detailed End-to-End User Journeys

## 1. Purpose and authority

This FRD defines what the standalone VoiceOps application must do, who may do it, which state changes are valid, and what callers and operators observe when a workflow succeeds or fails. It translates the PRD into functional behavior without implementing the application or prematurely specifying SDK methods, database tables, HTTP routes, or media payloads.

The governing principle is that speech is an interaction channel; application state remains authoritative. An LLM saying “your demo is scheduled” is not evidence of a Meeting. A successful database commit is evidence of the action; confirmed playback is evidence that the caller was told about it. These must be tracked separately.

### 1.1 Sources read in full

| Reference | Source | Version/status in source | Authority here |
| --- | --- | --- | --- |
| U | Latest user project instructions, including the documentation-only phase | Current explicit instructions | Highest; locks scope, stack, independence, sequence, and controlled fallback |
| P | VoiceOps_PRD_v1.0.md | v1.0; Draft for Architecture Lock / Ready for review | Product requirements and source requirement IDs |
| M | END-TO-END-VERIFIED-PROJECT-ZIP — MASTER BUILD DIRECTIVE | No explicit version | Engineering, evidence, audit, and future release standards |
| E | VoiceOps_Astra_Execution_Prompt_v1.0.md | v1.0 | Future implementation obligations, including runtime modes and automatic failover |

No unseen previous chat is treated as a source of additional locked behavior. The attached sources and explicit instructions are sufficient for this draft. No SynTask implementation detail has been imported as a VoiceOps requirement.

### 1.2 Requirement and decision labels

- **LOCKED:** Explicit in U or an existing authoritative source, with any conflict resolved below.
- **PROPOSED:** A new functional choice made visible in this FRD for user review. It becomes binding only when approved.
- **OPEN:** An unresolved choice with a named downstream document and a freeze condition. The implementation agent may not fill it silently.
- **Implementation detail:** How a requirement will be realized; deliberately assigned to the relevant later contract or architecture document.

The `FRD-*` IDs identify requirements in this document. “Shall” describes the intended requirement after approval. It does not imply that a newly proposed choice is already approved, implemented, or verified. All elaborations beyond source requirements are proposals under the decision register in §3.

### 1.3 Conflict reconciliation

| ID | Source tension | Resolution and reason |
| --- | --- | --- |
| CR-01 | P FR-P-009 permits manual fallback and leaves automatic failover for later; E §7 requires automatic failover | U explicitly requires controlled failure classification and local fallback. Manual selection and controlled automatic failover are required for the completed standalone scope. |
| CR-02 | M assumes definition is complete; E ends with “Now execute”; U prohibits coding and requires sequential document review | U prevails. Those execution commands remain dormant until the documentation gate and later implementation authorization. This turn produces only the FRD. |
| CR-03 | P §7 uses V1–V7 capability phases; E describes the completed standalone release | Preserve those phases as milestones. This FRD covers the completed standalone capability set through productionization, not a claim that every capability belongs in the first voice slice. V8 integration stays excluded. |
| CR-04 | M has generic examples and a generic document order; U provides VoiceOps-specific stack and 12-document order | Generic examples do not add providers or infrastructure. U's order and stack apply. |
| CR-05 | P describes an eventual SynTask capability while U emphasizes a standalone platform | VoiceOps uses its own identity, domain, storage, and operations. Future integration is a boundary design constraint, not current connectivity or shared data. |
| CR-06 | Developer is an initial persona; neither source defines a Developer authorization role | A persona is not a permission grant. Proposed roles are Administrator and Operator; a developer uses explicitly assigned permissions. |

The original files are unchanged. These interpretations must later be carried into `docs/ASSUMPTIONS_AND_DECISIONS.md`; that separate document is not generated in this turn.

## 2. Locked product model and scope

### 2.1 Locked stack and boundaries

| Concern | Primary | Controlled local alternative | Rule |
| --- | --- | --- | --- |
| Telephony | Plivo | Browser/local audio adapter is a different transport | Local AI cannot replace the telephone network |
| STT | Sarvam streaming STT | Faster-Whisper | Common STT contract; capability differences must be explicit |
| LLM | Groq | Ollama | Common structured-decision contract |
| TTS | Sarvam streaming TTS | Kokoro | Common synthesis contract; compatible voice/language profile required |
| Embeddings | OPEN model behind EmbeddingProvider | OPEN | No embedding provider or model is silently chosen here |
| Retrieval | Qdrant | Local Qdrant | Tenant and permission scope remain mandatory |
| Durable domain data | PostgreSQL | Local PostgreSQL | Authoritative business records |
| Transient state/coordination | Redis | Local Redis | Not durable business truth |
| Backend/media | FastAPI, WebSockets | Same engine | Python/async orchestration as in P |
| Observability | Prometheus, Grafana, structured logs | Same stack | Measured operational evidence |

The Voice Engine depends on TelephonyProvider, STTProvider, LLMProvider, TTSProvider, EmbeddingProvider, and Tool Gateway contracts. Business/domain code does not import provider SDKs. Qdrant access is confined to the retrieval boundary. API routing, persistence, provider adapters, UI, and orchestration remain separate responsibilities.

### 2.2 Runtime modes

| Mode | Media | AI stages | Functional expectation |
| --- | --- | --- | --- |
| Production-like | Plivo | Sarvam STT → Groq → Sarvam TTS | A real authorized/test phone path; requires credentials and secure ingress |
| Fully local AI | Browser/local audio | Faster-Whisper → Ollama → Kokoro | Uses the same engine, domain records, retrieval rules, tools, and inspection UI; cloud AI keys are not required |
| Hybrid failover | Plivo or permitted local adapter | Primary stages with eligible local fallback per stage | One failed stage switches under policy; successful stages are not rerun unnecessarily |

Manual provider selection is explicit configuration, not a reaction that conceals a failing cloud configuration. Calls record their mode and effective provider per operation. Model assets and sufficient hardware are prerequisites for local operation; “zero cloud AI cost” is not a claim of zero compute cost or a fully offline installation.

### 2.3 Milestones versus finished scope

| PRD phase | Required capability | Completion boundary |
| --- | --- | --- |
| V1 | Core streaming voice | Connected media, recognized speech, relevant response, audible playback, at least two turns, persisted events |
| V2 | Conversational reliability | Endpointing, silence, cancellation, barge-in, bounded recovery |
| V3 | RAG | Real ingestion through scoped retrieval and observable answers |
| V4 | Tools | Controlled business writes with authorization, confirmation, idempotency, and audit |
| V5 | Campaign product | Leads, queue, monitoring, outcomes, meetings, follow-ups |
| V6 | Observability/evaluation | Measured timing, errors, usage, AI evaluation evidence |
| V7 | Productionization | Repeatable configuration/startup, secure ingress, durable recovery, documented release checks |
| V8 | SynTask integration | Future, excluded |

Authentication, tenant isolation, consent gates, cancellation safety, and honest evidence apply from the first slice that uses them; they are not deferred merely because full UI/evaluation arrives later.

Excluded from this standalone scope: SynTask imports/APIs, enterprise SSO, billing, Kubernetes, unnecessary microservices, arbitrary model code execution, raw database tools, calendar/email/WhatsApp integrations, automatic meeting invitations, autonomous commercial mass dialing, live human transfer, and a general CRM workflow builder. None is added by this FRD.

## 3. Visible functional decisions proposed for approval

These are the principal new choices. Detailed rules in later sections implement these proposals rather than implying prior approval.

| ID | Proposed choice | Why it is needed | Related sections |
| --- | --- | --- | --- |
| FD-01 | Outbound authorized test call is the first phone milestone. The completed scope also supports controlled inbound test calls using registered tenant routes and known eligible contacts. | Resolves first-demo direction and unknown inbound caller behavior | 6 |
| FD-02 | Two tenant roles: Administrator and Operator; no public self-registration, hidden developer bypass, or global cross-tenant administrator UI | Defines minimal identity and permissions without enterprise scope | 4 |
| FD-03 | Campaigns launch explicitly, with one outbound call at a time per tenant in the initial standalone release; no automatic redial, timed campaign scheduling, or automatic repeat lead enrollment | Makes queue and concurrency behavior bounded | 5, 10 |
| FD-04 | Phone eligibility requires recorded permission, development/test number allowlisting, and no tenant-scoped normalized-number suppression. Opt-out is not cleared by normal lead edits or a voice request. | Gives consent/opt-out a deterministic gate | 5, 9 |
| FD-05 | Lead status enum NEW, CONTACTED, QUALIFIED, NOT_INTERESTED, CLOSED; call disposition is separate from lead status and transport status | Avoids importing SynTask sales stages and conflating outcomes | 5, 11 |
| FD-06 | Knowledge ingestion initially supports text-based PDF, UTF-8 TXT, and Markdown uploads; registration may use an already managed file, not arbitrary remote URLs. Explicit admin approval controls retrieval publication. | Defines a complete narrow ingestion workflow | 8 |
| FD-07 | Meetings and follow-ups are standalone database records. Scheduling requires explicit date, time, timezone, duration, assigned operator, and caller confirmation. No claim of external-calendar availability or invitation delivery. | Prevents overpromising integration and ambiguous scheduling | 9, 11 |
| FD-08 | Schema-validated complete assistant decision before speaking; one tool request per decision, up to three business tool operations per user turn; no autonomous unbounded tool loop | Bounds actions and prevents speaking unvalidated structured output | 7, 9 |
| FD-09 | At most one primary retry and one local fallback attempt per provider operation; active calls stay on successful fallback for that provider family until call end; no mid-call automatic failback | Limits delay and provider oscillation | 12 |
| FD-10 | One clarification after empty/unintelligible finalized speech; one silence reprompt before graceful end. Exact timer values are frozen in later contracts. | Specifies behavior without inventing unresearched timeouts | 7, 16 |
| FD-11 | English is the proposed baseline validation language. Hindi and Hindi-English support remains OPEN pending compatible primary/local profiles and explicit scope approval. | Does not infer end-to-end language support from provider branding | 7, 16 |
| FD-12 | No durable raw call recording by default. Transcripts and redacted events are retained under an explicit retention policy; short-lived bounded audio is permitted for STT replay and is discarded. | Separates conversational evidence from recording policy | 7, 14, 16 |
| FD-13 | Connected caller hang-up is COMPLETED unless an established failure caused termination; business and summary status remain independent. Summary processing never starts tools. | Separates lifecycle from task success | 6, 11 |

Approval of the FRD locks approved functional choices. It does not lock OPEN implementation selections or waive the remaining documentation sequence.

## 4. Identity, tenant boundaries, and access

**Source:** P §§5, 10.3–10.5, 12; M §13; E §§14, 24. **New choices:** FD-02.

### FRD-ID-001 — Provisioning and authentication

The application shall support authenticated tenant users. Initial tenant/administrator provisioning shall be an explicit setup operation; an empty database shall show setup guidance, not create users on an unauthenticated request. Administrators may provision/deactivate operators within their tenant. Public signup, password recovery email, SSO, and tenant switching are not required in this release.

Login, logout, session expiry, invalid login, deactivated user, and revoked session behavior shall exist. Invalid login shall not reveal whether an account exists. Deactivation/revocation prevents new protected operations and new monitoring subscriptions. An active conversation whose initiating authority is revoked shall stop new protected writes and end safely. Exact credential storage, session mechanism, lifetimes, and bootstrap commands are OPEN for Architecture and API contracts.

**Observable acceptance:** An Operator cannot access Administrator actions by directly invoking the backend. A deactivated account cannot start a new call or view a transcript through an existing connection.

### FRD-ID-002 — Effective permissions

| Capability | Administrator | Operator | Voice session |
| --- | --- | --- | --- |
| Manage tenant users/settings/tool policy | Yes | No | No |
| Inspect provider configuration health | Yes | Sanitized availability needed to operate | No credentials |
| Create/edit/archive leads, append notes | Yes | Yes, same tenant | Only allowed tools on bound lead |
| Record consent evidence | Yes | Yes, explicit operator action | Cannot grant its own dialing consent |
| Clear opt-out | Excluded in this release | No | No |
| Create/edit/start/pause campaign | Yes | Yes, same tenant | No campaign administration |
| Create KB, upload documents | Yes | Yes | No |
| Approve/withdraw documents | Yes | No | No |
| Inspect calls, retrieval, tools, summaries | Yes | Yes, same tenant | Only bounded current-session context |
| Create/manage meetings and follow-ups | Yes | Yes, same tenant | Restricted tools with confirmation |
| View security audit and trigger evaluations | Yes | No | No |

All tenant operators may use approved knowledge bases in their tenant in the proposed initial permission model. Private per-user KB sharing is excluded; future permission scopes must be enforced in retrieval if added. Backend denial remains authoritative even if a UI control is visible.

### FRD-ID-003 — Tenant/session binding

Tenant identity comes from authenticated identity or a verified registered telephony route. Caller-supplied identifiers, model output, document text, and client query parameters cannot confer tenant membership. Every referenced domain object must be revalidated within that scope.

A voice session has a narrowly scoped principal bound to its tenant, call, lead where applicable, campaign objective, approved knowledge base, tool policy, and initiating authority. A phone caller is not an authenticated tenant operator. Phone number matching provides context, not permission to access arbitrary records.

Cross-tenant object access shall fail without exposing the other tenant's data. Isolation covers lists, detail views, files, WebSockets, retrieval, tools, metrics views, meetings, and follow-ups.

**Observable acceptance:** A malicious tool request or retrieval query that supplies another tenant's ID cannot read or mutate that tenant's records.

## 5. Leads, consent, and call eligibility

**Source:** P §§6, 12, 17, 20; E §15. **New choices:** FD-04, FD-05.

### FRD-LEAD-001 — Minimal lead management

Users shall create, list, inspect, edit, and archive leads. Functional data comprises display name, normalized phone number where calling is intended, company, interest, controlled status, append-only notes, consent evidence, opt-out state, ownership tenant, and timestamps. Exact physical fields and validation lengths belong to Data Model/API contracts.

A lead without a valid phone number may exist as a draft or local-demo subject but cannot be phone-dialed. Identity-critical edits, especially a phone change, invalidate the old number's consent applicability and require new evidence for the new destination. Archiving prevents new enrollment/calls while preserving historical references. Required lead records cannot be hard-deleted through normal UI.

Proposed lead status values are NEW, CONTACTED, QUALIFIED, NOT_INTERESTED, CLOSED. CLOSED and NOT_INTERESTED are excluded from new automated campaign calls by default. A connected call may move NEW to CONTACTED; further changes require an explicit allowed tool or operator action with supporting context. Status changes do not grant consent.

### FRD-LEAD-002 — Consent and suppression

Outbound eligibility shall be checked at enrollment and again immediately before dialing. All conditions must hold:

1. Tenant and initiating user remain active and authorized.
2. Lead is active, destination is valid, and campaign context is valid if supplied.
3. Permission to call is recorded as GRANTED with source and timestamp; UNKNOWN or DENIED is ineligible.
4. Development/test destination is explicitly allowlisted; allowlisting alone does not imply consent.
5. No active opt-out/suppression exists for that normalized destination in the tenant.
6. No other outbound attempt for that destination is in progress in the tenant.
7. Required persistence, media path, provider profile, and coordination gates are ready.

Normal CRUD, CSV-like inputs if ever added, campaign creation, and the LLM cannot infer consent. Demonstration fixtures must use intentionally configured authorized test destinations rather than arbitrary realistic phone numbers.

Suppression applies to the tenant and normalized destination, so creating a duplicate Lead does not evade opt-out. This does not create cross-tenant contact lookup or a global do-not-call database.

### FRD-LEAD-003 — Priority opt-out

A clear caller request to stop future contact shall cancel normal sales continuation and route to the controlled opt-out action. Deterministic explicit phrase rules and structured intent assessment shall be defined/evaluated in AI contracts. If meaning is ambiguous, ask a brief clarification; do not falsely declare an opt-out persisted. Missing or uncertain speech recognition shall never be interpreted as consent.

Once suppression commits, queued attempts for the destination are cancelled/skipped and pre-dial checks block further automated calling. The caller may receive a brief acknowledgment before end; no meeting/follow-up sales action is started afterward. Existing outbound-contact follow-ups are marked blocked by suppression; historical meetings are not silently deleted.

If opt-out persistence fails, immediately suppress further dialing in the running session, halt affected outbound dispatch, and show a durable-state failure/reconciliation requirement. Do not claim successful permanent opt-out. Reopening dispatch requires durable consent/suppression reconciliation; a restart does not authorize blind continuation of queued calls.

**Observable acceptance:** “Don't call me again” results in suppression and no second campaign dial, including through a duplicate Lead. An unavailable database produces a visible failure, not a false success acknowledgment.

## 6. Calls, transport, and lifecycle

**Source:** P FR-P-001/002/007/013, §§13, 19, 23; E §§8, 10–12. **New choices:** FD-01, FD-13.

### FRD-CALL-001 — Creation and preflight

Users shall start an authorized outbound call from a lead or queued campaign attempt. A request must durably create one Call before placing the provider operation. Repeated submission of the same start operation returns the same attempt/result rather than redialing. An intentional later redial is a new operator action with a new Call, subject to eligibility.

Each Call identifies tenant, lead/contact where applicable, campaign if any, direction, transport, runtime mode, application call ID, provider call ID when known, stable correlation ID, lifecycle timestamps, effective provider profile, and failure/end reason. Secrets are not copied into call records. One Conversation belongs to the Call; ConversationTurn, TranscriptEvent, RetrievalEvent, and ToolExecution describe its detailed activity.

Preflight failure blocks dialing with an understandable reason. If the telephony request may have reached the provider but its result is unknown, the application reconciles that same attempt and does not issue a fresh dial automatically.

### FRD-CALL-002 — Controlled inbound and local sessions

For proposed inbound test support, a verified registered destination route determines the tenant and permitted objective/KB/tool policy. A known eligible caller can be matched within that tenant. Unknown, ambiguous, unconsented test callers, unregistered destinations, and spoofed/unverified requests are rejected without exposing business context. No lead is automatically created from unknown inbound caller information. Opted-out callers are not used to restart sales conversations or clear suppression.

Inbound context uses Administrator-configured route authority with the same restricted session tool principal, never an unrestricted admin principal. Telephony verification mechanisms are OPEN in Provider/API contracts.

Local browser audio sessions require authenticated users and microphone permission, explicit start/stop controls, and the same domain/audit pipeline. They do not ring a telephone or obtain a fabricated provider call ID. No unsolicited browser reconnect creates a new Call. A local session may use a selected lead; without one, lead-mutating tools are unavailable.

### FRD-CALL-003 — Canonical call states

| State | Meaning | Permitted normal next states |
| --- | --- | --- |
| CREATED | Durable attempt/session exists | QUEUED, DIALING, CONNECTED for validated inbound/local, REJECTED, CANCELLED, FAILED |
| QUEUED | Waiting for explicit dispatch | DIALING, CANCELLED, REJECTED, FAILED |
| DIALING | Outbound connection requested | RINGING, CONNECTED, BUSY, NO_ANSWER, REJECTED, FAILED, CANCELLED |
| RINGING | Provider reports alerting | CONNECTED, BUSY, NO_ANSWER, REJECTED, FAILED, CANCELLED |
| CONNECTED | Human/media transport has connected | ACTIVE, ENDING |
| ACTIVE | Valid media and engine session running | ENDING |
| ENDING | Media/generation teardown or hang-up initiated | COMPLETED, FAILED, CANCELLED |
| COMPLETED | A connected call ended normally | Terminal |
| NO_ANSWER | Outbound attempt never connected within ring policy | Terminal |
| BUSY | Busy reported before connection | Terminal |
| FAILED | Technical failure prevented/ended workflow | Terminal |
| CANCELLED | Operator/system explicitly cancelled attempt/session | Terminal |
| REJECTED | Eligibility or verified provider rejection prevented connection | Terminal |

Provider callbacks may omit intermediate states; a validated transition can skip DIALING/RINGING observations to CONNECTED. Inbound/local sessions do not pretend to have rung. Callback order does not authorize regression from ACTIVE to RINGING or resurrection of a terminal call. Late authoritative metadata may enrich a record through an audited reconciliation without restarting conversation work.

Caller hang-up after connection normally yields COMPLETED; hang-up before answer yields an appropriate no-connection reason. COMPLETED is not equivalent to sales success. A provider technical failure yields FAILED. Operator cancellation yields CANCELLED. Exact provider-status mapping is OPEN for Provider Contracts.

### FRD-CALL-004 — Media admission and termination

An accepted media connection shall bind to exactly one verified active Call and session ownership. Unsupported codecs, invalid framing, excessive payloads, replayed/stale connections, and cross-call media are rejected. Audio is normalized outside domain services. Buffers and processing queues are bounded; unsupported input or sustained overload cannot accumulate indefinitely or silently fabricate recognized speech.

The caller shall receive live responses without waiting for a complete recording. Input, processing, and output may stream concurrently under turn policy. Local model processing may use bounded utterance windows; the UI must not claim provider-native partial streaming when it is not available.

On hang-up, cancellation, or an unrecoverable media disconnect, stop admitting new audio, invalidate outstanding generations, cancel providers where possible, stop/clear playback, and reject new tool actions. Already committed actions remain recorded. Pending transport release is reconciled; no redial is started.

**Observable acceptance:** Duplicate callbacks do not create duplicate sessions or tools. A terminal Call never starts playback from a late TTS result.

## 7. Turn management and assistant behavior

**Source:** P FR-P-003–007, §§14, 19; E §§10–12. **New choices:** FD-08, FD-10–12.

### FRD-TURN-001 — Canonical states and transcript finality

The canonical normal sequence is LISTENING → USER_SPEAKING → TRANSCRIBING → THINKING → optional TOOL_EXECUTION → SYNTHESIZING → ASSISTANT_SPEAKING → LISTENING. Streaming operations may overlap, but these labels describe the authoritative control phase, not a claim that microphone processing stops during playback.

Each user interaction has a stable turn ID. Transcript partials are revision events, not independent caller utterances. Only a finalized, accepted user utterance may trigger business tool execution. Duplicate finals do not start a second assistant response. Provider corrections after the turn has acted are retained as corrections rather than replaying actions automatically.

The Turn Manager uses speech activity, endpointing, provider finality, and configured time limits to accept an utterance. Noise and playback echo alone must not count as a confirmed user business instruction. Long speech is bounded; if the utterance limit is reached, explain/ask the caller to continue rather than pretending a truncated request is complete.

### FRD-TURN-002 — Context and structured decision

Context shall include security policy, approved call objective, bounded history, allowed lead context, selected approved knowledge, allowed tools, and already committed action results. Tenant/session scope and permission data come from the backend. Retrieved text and caller content are untrusted data and cannot change tool authority.

The model returns a structured assistant decision with approved spoken text and either no tool or one permitted tool request. Complete schema and policy validation precede TTS. Invalid JSON, extra unsupported fields, unknown tools, and invalid action parameters do not produce unchecked speech or business writes. One same-provider output repair is permitted only within the operation budget and only when no side effect has started; repeated invalid output uses a safe response or ends under failure policy. It is not a reason to blindly switch providers.

After a tool request, gateway results enter a bounded continuation. The assistant may confirm success only from a committed successful result. At most three normal business tool operations may execute per user turn, with one request per decision. An opt-out request preempts this flow and is never ignored because the normal tool budget is exhausted. No infinite agent/tool loop is permitted.

Streaming LLM text deltas may be measured internally, but raw deltas are not spoken before their decision is validated. This knowingly trades some latency for a clear action/security boundary. Sentence-level synthesis may stream approved text afterward.

### FRD-TURN-003 — Silence and recognition failure

An empty/unintelligible finalized utterance causes one clarification; it does not call business tools, invent words, or add a fabricated user message. A repeated inability to understand ends gracefully with a reason after the configured limit.

While listening, silence causes one brief reprompt; continued silence ends gracefully. Silence timers distinguish waiting for the caller from time spent thinking, synthesizing, or playing speech. Provider timeouts do not count as caller silence. Silence/timer values and speech thresholds are OPEN for the later contracts, not runtime guesses.

The greeting identifies the represented organization and the assistant as automated, explains the purpose briefly, and invites the caller to continue. Caller refusal ends without continuing the pitch. A request for a human produces an honest limitation and, only with agreement, a supported callback follow-up; live transfer is out of scope.

### FRD-TURN-004 — Barge-in and cancellation

Confirmed caller speech during assistant work/playback starts interruption handling: stop admitting output from the interrupted generation, cancel remaining model/synthesis work where possible, request playback clearing, and accept the new caller utterance. Late results from a cancelled generation are ignored for playback and new actions. Monitoring records the interruption and whether output clearing was acknowledged.

Cancellation does not roll back a committed meeting or note. A tool not yet committed must recheck cancellation/authority at its commit boundary; an action with an uncertain commit result enters reconciliation rather than blind replay. Conversation context retains successful committed results even if their spoken acknowledgment was interrupted.

Generated text, synthesized audio, queued playback, and confirmed delivered audio are distinct events. Without playback acknowledgment, delivery is UNKNOWN/UNCONFIRMED rather than asserted as heard. History must preserve interruption/truncation metadata instead of treating the full generated response as delivered.

### FRD-TURN-005 — Language/profile capability

The session uses an explicit supported language/voice profile. The proposed baseline is English; Hindi/Hindi-English scope is OPEN. STT, LLM, TTS, and fallback profile compatibility must be checked before calling. Unsupported language/voice/model configurations are configuration failures, not eligible failover.

If speech is outside the supported profile, ask for a supported language when recognizably possible; otherwise use the same recognition-failure behavior. Never claim Kokoro/Faster-Whisper profile parity without validation. Model downloads must be explicit setup steps; no undocumented large download occurs during a live call.

**Observable acceptance:** An interrupted “meeting created” acknowledgment does not create a second meeting on the next turn. A partial “schedule…” transcript cannot execute scheduling.

## 8. Knowledge bases, documents, and retrieval

**Source:** P FR-P-010, §§7.3, 15, 18; E §13. **New choices:** FD-06.

### FRD-KB-001 — Source management and ingestion

Users shall create named tenant knowledge bases, inspect their documents, and upload supported sources. Proposed initial formats are text-based PDF, UTF-8 TXT, and Markdown. Image-only/scanned PDFs without supported extraction, encrypted unreadable PDFs, corrupt files, oversized content, and unsupported formats fail with actionable status. OCR and arbitrary remote URL fetching are out of scope.

Document registration points only to an already managed tenant file; it does not give the LLM or user an unrestricted filesystem path. File access is authenticated/tenant-scoped, storage paths are server-controlled, and document contents cannot execute code. File bytes, version identity, extraction/chunking configuration, embedding configuration, and ingestion results must remain traceable.

Document ingestion follows RECEIVED → VALIDATING → EXTRACTING → CHUNKING → EMBEDDING → INDEXING → READY_FOR_REVIEW → APPROVED. A failure becomes FAILED with the last completed stage and a sanitized reason. REJECTED/WITHDRAWN content is not available to retrieval. These are functional states, not finalized database enums.

Successful indexing is not approval. An Administrator explicitly approves a usable version. Re-ingestion is idempotent for the same source/version/configuration; retry does not duplicate active chunks. A changed source/configuration is a new version requiring review. Empty extracted text cannot count as a successful usable document.

### FRD-KB-002 — Publication, withdrawal, and deletion

Only approved, currently eligible document versions may supply new retrieval context. Withdrawal is effective for future retrieval immediately at the authoritative permission boundary, even if asynchronous vector cleanup is pending. Historical retrieval records retain source/version references subject to retention policy. A replacement version is activated coherently; incomplete mixed indexes are not presented as complete.

Calls record the selected KB and exact versions used per retrieval. New approved versions may be used on later turns; earlier answers remain traceable to their original version. Withdrawn content already in cached conversation context must not be reused as support for a new answer. Exact context invalidation and version mechanics belong to AI and Data contracts.

Archiving a KB blocks new campaign/call selection. If a selected KB becomes unavailable during a call, the next knowledge-dependent response follows no-knowledge behavior; it does not search another tenant or KB automatically.

### FRD-RAG-001 — Scoped and grounded retrieval

Business questions shall use the session's selected approved knowledge base. The backend supplies tenant, KB, active-version, and permission scope on every retrieval. Model-provided filters cannot remove those constraints. Results are validated against authoritative document publication state before entering context.

Each retrieval trace records call/turn, query or approved redacted representation, KB, source/version/chunk identities, relevance scores when available, timing, result count, filtering outcome, and failure/no-result reason. Spoken citations are optional; auditable real source references are required. Citations cannot point to chunks not actually retrieved.

No relevant result, insufficient support, conflicting source claims, timeout, and unavailable Qdrant are distinguishable. For any of these, the assistant states that it cannot confirm the business fact, asks a clarification if helpful, or offers an authorized follow-up. It does not invent features, prices, promises, or commitments. Existing conversation context may only support an answer if its sources remain approved and relevant.

General greetings/clarifications do not require retrieval. The criteria for domain-question routing, thresholds, chunking, embeddings, and context budget are OPEN in AI/RAG contracts. Embedding model/version incompatibility requires controlled reindexing, not mixing incompatible vectors or inventing similarity scores.

**Observable acceptance:** An unpublished source never supports an answer; a zero-result question produces a safe acknowledgment, and call detail shows the actual retrieval result or failure.

## 9. Tool Gateway and business actions

**Source:** P FR-P-011, §§16–17, 20; E §§14–15. **New choices:** FD-07, FD-08.

### FRD-TOOL-001 — Admission and result authority

All model-requested actions pass through the Tool Gateway: allowed tool → schema validation → call/turn validity → tenant/object binding → effective authorization → required caller confirmation → business rules → idempotency → domain service → durable result → audit.

The gateway derives tenant/call/lead from the verified session. It does not trust model-supplied ownership IDs. A caller cannot select another Lead by naming it. Arbitrary URLs, shell commands, SQL, file paths, or code are never tool inputs. Tools receive the minimum required data and return bounded structured outcomes.

Gateway result classes include SUCCEEDED, REJECTED, FAILED, CANCELLED, and UNKNOWN_COMMIT/RECONCILIATION_REQUIRED. Exact schemas/status strings are finalized in AI/Tool and API contracts. A failure response cannot be worded as success. Authorization rejection is not repaired by a different LLM provider.

### FRD-TOOL-002 — Initial allowed tool behavior

| Tool | Allowed functional input | Preconditions and confirmation | Durable effect | Failure behavior |
| --- | --- | --- | --- | --- |
| add_call_note | Bounded note text about this call | Active bound lead/call; append permission; facts traceable to conversation | Append note linked to call/turn/lead | Reject out-of-scope references; never overwrite old notes |
| update_lead | Allowlisted interest/company/status changes | Bound lead; allowed field/status; caller-supported correction or qualification, with explicit confirmation when changing company/interest | Update allowed fields with prior/new value audit | Reject identity, phone, tenant, owner, consent, suppression, or arbitrary fields |
| schedule_demo | Purpose, explicit start, timezone, duration, assigned tenant operator | Bound lead; future valid time; participant/operator resolvable; caller confirms date/time/timezone/duration and demo intent | Create standalone Meeting | Missing/ambiguous time asks clarification; conflicts are rejected with no invented alternative slot |
| create_followup | Bounded purpose, due date/time/timezone, assignee, contact intent | Bound lead; valid active assignee; caller agrees for callback/outreach; opt-out blocks contact intent | Create standalone FollowUp | Reject missing assignee/time or forbidden outreach; do not schedule an automatic call |
| set_call_outcome | Controlled disposition and supported rationale | Bound call; evidence supports value; no overwriting opt-out with positive sales outcome | Persist provisional business disposition; finalization preserves stronger safety result | Reject unknown/unsupported enum; no transport-status mutation |
| opt_out_contact | Current destination/lead binding and request evidence | Clear request or confirmed clarification; special safety permission independent of sales-tool policy | Persist tenant destination suppression, lead opt-out, timestamp/source; block queued outreach | On persistence failure halt dialing and require reconciliation; never claim durable success |

Lead notes and outcome classification do not require a second caller confirmation for recording what the caller already said. Meeting creation and outreach follow-ups do. A configured tool whitelist cannot disable the safety path for an explicit opt-out.

### FRD-TOOL-003 — Relative time and scheduling safety

“Tomorrow” alone is insufficient for scheduling. Resolve it relative to the caller's explicitly established timezone and the conversation date; ask for missing time, duration, or timezone. Tenant timezone may be proposed but must be confirmed for the meeting. Ambiguous daylight-saving times require disambiguation. Past/nonexistent times fail. Persist normalized instant plus the business timezone and caller-confirmed representation.

An assigned operator is selected from tenant configuration or explicit operator choice; the model cannot invent attendees. The domain service checks overlap against VoiceOps Meetings for that assigned operator, including concurrent scheduling attempts. It does not claim to know the operator's external calendar. Confirm only “created in our system,” not “invitation sent” or “calendar reserved externally.”

No implicit follow-up is created merely because a summary recommends it. No meeting automatically creates a second follow-up unless an approved workflow explicitly requests both. Meeting cancellation/rescheduling is an operator workflow in this release, not an added voice tool.

### FRD-TOOL-004 — Idempotency and concurrent change

An action intent has a durable idempotency identity scoped to tenant/call/turn/action. Duplicate event delivery, provider switching, lost responses, and model restatement of the same confirmed intent return the existing result. Same identity with different payload is a conflict. An intentionally new action requires a new intent/confirmation; textual similarity alone is not an idempotency guarantee.

Before a write commits, revalidate caller confirmation, call cancellation, authority, and current domain state. Concurrent opt-out overrides queued outreach; conflicting lead edits fail visibly or use an audited merge rule frozen in Data contracts. A timeout after possible commit is reconciled against durable action state before any retry. Cancellation never undoes an already committed business action implicitly.

**Observable acceptance:** A Groq timeout after a Meeting has committed cannot cause Ollama to create the same Meeting again. A tool rejected for another tenant remains rejected regardless of provider.

## 10. Campaign and queue behavior

**Source:** P §§7.5, 12, 18; E §19. **New choices:** FD-03.

### FRD-CAMP-001 — Definition and readiness

Users shall create campaigns with name, bounded objective, selected active leads, an approved KB for knowledge-dependent selling, supported language/provider profile, and an allowed tool subset constrained by tenant policy. Campaign objective text is not privileged policy and cannot override security. Leads and KB must belong to the tenant.

Proposed states: DRAFT, READY, RUNNING, PAUSED, COMPLETED, CANCELLED. Validation promotes DRAFT to READY; explicit start promotes READY to RUNNING. Failed validation remains DRAFT with reasons. Campaigns without callable leads cannot start. COMPLETED/CANCELLED campaigns are not silently reopened; an operator creates or explicitly prepares a new run.

Changes to objective, KB, provider profile, or lead membership are permitted before running or while paused for future attempts. Active calls retain their initiating campaign/profile snapshot, subject to live security and document-withdrawal checks. A start action is idempotent and cannot enqueue a second identical run.

### FRD-CAMP-002 — Dispatch, pause, and completion

The proposed initial dispatcher admits one outbound active attempt per tenant, including ad hoc calls. Excess requests remain visibly queued; no unlimited concurrency is implied. A selected lead receives at most one attempt in a campaign run. Dispatch order is recorded and deterministic. Revalidate eligibility immediately before dialing.

Pause prevents dispatch of new calls; it does not hang up active calls. Cancel closes outstanding queued attempts; active calls may finish unless the operator separately cancels the call. No-answer, busy, failed, or rejected attempts are visible and do not auto-redial. Follow-up records do not trigger autonomous dialing. Automatic time-window scheduling is excluded; timezone-aware due times belong to follow-ups/meetings only.

COMPLETED means every member attempt is terminal or explicitly skipped. Connected/completed/failed/skipped totals must derive from records, not hardcoded progress. Paused or infrastructure-blocked runs show the reason and cannot claim completion merely because no worker is active.

### FRD-CAMP-003 — Restart and ownership safety

Queue state and attempt history are durable. After process loss, the system reconciles provider calls and ownership before resuming dispatch. It does not assume that an unseen call failed or redial a potentially active destination. If exclusive dispatch/media ownership cannot be established, pause/stop affected work rather than run two engines for one call.

**Observable acceptance:** Starting twice creates one run. Pausing during a connected call allows that call to finish but stops the next queued lead. Restarting during DIALING does not produce an unexamined second telephone call.

## 11. Outcomes, summaries, meetings, and follow-ups

**Source:** P FR-P-012, §§7.5, 12, 18; E §§16, 32. **New choices:** FD-05, FD-07, FD-13.

### FRD-RESULT-001 — Separate result dimensions

| Dimension | What it answers | Proposed values/meaning |
| --- | --- | --- |
| Call transport state | Did the call connect and how did it end? | Canonical states in §6 |
| Business disposition | What did the caller decide? | UNKNOWN, INTERESTED, NOT_INTERESTED, DEMO_SCHEDULED, FOLLOWUP_REQUESTED, OPTED_OUT |
| Tool result | Was a requested state change committed? | Success, rejection, failure, cancellation, uncertain commit |
| Summary status | Has a grounded summary been produced? | NOT_REQUIRED, PENDING, PROCESSING, READY, FAILED |
| Playback delivery | Was a response sent/confirmed delivered? | Separate generated, queued, acknowledged, interrupted, unconfirmed evidence |

DEMO_SCHEDULED requires a successfully persisted Meeting. FOLLOWUP_REQUESTED records caller intent; call detail separately distinguishes an existing FollowUp from a failed creation. OPTED_OUT takes precedence over positive sales dispositions. Multiple facts remain in structured summary even though one primary disposition is selected. An unanswered call has UNKNOWN business disposition and no fabricated conversation summary.

### FRD-RESULT-002 — Post-call processing

The call can reach its terminal state before summary processing completes. A connected call with usable accepted transcript shall generate a structured summary containing concise conversation summary, outcome, interest, objections, caller/business commitments, confirmed action references, requested-but-failed actions, suggested next steps, and opt-out status. Unknown values remain unknown.

Generation uses finalized transcripts, delivery/interruption metadata, and durable tool results. It does not execute tools, change consent, create meetings, or grant promises. It is idempotent per input version. Failure leaves summary FAILED with a retry option for an authorized operator; the transcript remains available. An approved replacement summary preserves prior provenance rather than rewriting facts silently.

### FRD-RESULT-003 — Meeting and follow-up management

Users shall inspect created Meetings/FollowUps from call detail and from their relevant management list. Meetings carry lead, call origin, purpose, confirmed time/timezone/duration, assigned operator, and SCHEDULED/COMPLETED/CANCELLED status. Operators may reschedule/cancel using the same validation/conflict rules; any external notification is out of scope.

FollowUps carry lead, call origin, purpose, due time/timezone, assignee, status, and contact intent. Proposed statuses are OPEN, DONE, CANCELLED, BLOCKED_BY_OPT_OUT. Users may explicitly mark done/cancel; overdue is derived from due time, not a model-generated claim. Creation does not send a message or place a phone call. Automated outreach is disabled by suppression even for an existing FollowUp.

**Observable acceptance:** Call detail can display COMPLETED with a failed scheduling tool and no Meeting. A summary cannot turn that failed request into DEMO_SCHEDULED.

## 12. Controlled provider selection and failover

**Source:** U locked strategy; P FR-P-008/009, §10.1; E §§5–8, 23. **New choices:** FD-09.

### FRD-PROV-001 — Effective profile and admission

Administrators/operators choose from configured permitted profiles; exact environment names are OPEN for Architecture/Provider Contracts. Secret values are configured server-side through environment/secret references. UI shows sanitized configured/not-configured/available/degraded/failed/unknown state, capabilities, and last-check time. A cached health check is not proof of the next call's success.

Manual local selection can run without cloud keys and is clearly labeled local. Production-like selection with missing/invalid credentials fails preflight for that profile; it does not quietly become a local call. Hybrid mode requires compatible local models already available, sufficient resources, and a bounded policy. No live call starts an undocumented model download.

The effective call profile snapshots primary and fallback choices and policy version; each operation records which provider actually served it. Security/configuration revocation may end a call, but normal profile edits take effect for new calls. Telephony has no automatic PSTN fallback; a local session is a separately initiated journey.

### FRD-PROV-002 — Failure classification

| Failure class | Automatic local fallback | Retry rule |
| --- | --- | --- |
| Timeout, network/connectivity failure, transient unavailability/5xx | Eligible only with safe replay, compatible ready fallback, and remaining deadline | At most one safe primary retry within budget; then at most one fallback |
| Temporary AI stream disconnect | Conditional on stage/output/replay rules | Never restart a conversation or replay a committed action |
| Rate limit | Eligible only if the profile explicitly enables it and provider-specific classification confirms it | Respect retry-after only if it fits the operation budget; do not wait indefinitely |
| Invalid credentials, authorization failure | No | Surface configuration/security failure; no provider cycling |
| Malformed request, unsupported codec/model/language/profile | No | Fix configuration/input; no blind retry |
| Programming/schema adapter error, invalid structured model output | No blind switch | Bounded output repair only as in §7; programming errors require correction |
| Tool validation/business-rule/tenant rejection | No | Explain rejection/clarify; another model cannot authorize the write |
| Intentional cancellation/caller hang-up | No | Propagate cancellation; discard late output |
| Unknown/unclassified error | No by default | Fail safely and audit classification gap |

Provider error codes are mapped in Provider Contracts using official source verification during that phase. This FRD does not assert undocumented vendor endpoint/codec behavior.

### FRD-PROV-003 — Bounded switching and recovery

For each STT/LLM/TTS operation, the proposed maximum is one primary retry and one fallback attempt. All attempts, backoff, output repair, and local readiness must fit one operation deadline and the remaining turn/call budget. Managers do not recursively call each other, rotate through arbitrary providers, or reset budgets after a switch.

A successful local fallback becomes the active provider for that family for the remainder of the call. Other stages retain their successful providers. No automatic mid-call failback is attempted. New calls may return to a validated primary when health/policy permits; exact admission cooldown is OPEN. Failed fallback has no further provider cycle.

Audit includes tenant/call/turn/operation, failed provider, normalized failure category, eligibility decision, attempted retry/switch, target provider, timestamps, added delay, result, and sanitized reason. Success never erases the original failure.

### FRD-PROV-004 — Safe replay by stage

| Stage | Safe continuation rule | When continuation is not safe |
| --- | --- | --- |
| STT | Replay only a complete retained bounded utterance; treat primary partials as superseded; accept one final utterance | Missing/overflowed audio cannot be reconstructed; ask caller to repeat once or end |
| LLM | Regenerate a decision from the same scoped context when no validated decision has been committed; include existing durable tool results in later continuation | Never replay tool execution or invent a clean state after unknown commit |
| TTS before output | Synthesize the same approved text with compatible fallback and one new output generation | Unsupported profile is ineligible; cancelled text cannot be revived |
| TTS after partial output | Clear remaining playback and invalidate old generation; use one explicit recovery message/restart only if output boundary and clear acknowledgment are known | Unknown delivered boundary or unacknowledged clear must not splice streams/replay whole speech blindly; end safely |
| Telephony/media | Reconcile/terminate the existing call under its media contract | Do not redial or substitute browser audio inside a PSTN call |

If no speech channel remains, use the termination primitive and record the failure; an audible apology cannot be guaranteed. If a compatible channel remains, give a brief approved failure/recovery response within budget. Preapproved text is not evidence of synthesized/delivered audio.

**Observable acceptance:** Invalid Sarvam credentials produce a configuration error without Faster-Whisper fallback. An eligible Groq timeout can switch only the LLM stage and leaves a correlated failure/switch/result trail.

## 13. Dependency and failure behavior

**Source:** P §§10, 19; E §§17, 23. This is the FRD behavior summary; the full Failure Matrix is still a separate future document.

| Condition | Required functional behavior | Operator/caller result |
| --- | --- | --- |
| PostgreSQL unavailable before call/write | Reject new durable operations; halt dispatch | Unavailable reason; no call/tool success claim |
| PostgreSQL lost during active call | Stop protected writes; attempt bounded teardown; do not continue unrecorded business actions | Explain inability if audio available; show reconciliation need after recovery |
| Redis unavailable before call | Fail coordination preflight; do not start new calls/dispatch | Paused/unavailable; CRUD may continue if safe PostgreSQL-backed |
| Redis lost during call | No new dispatch; continue only briefly where exclusive ownership is still proven, otherwise terminate | Visible degradation; exact grace bound frozen later |
| Qdrant unavailable | Ingestion cannot reach usable success; retrieval reports unavailable | Safe no-knowledge response; no cross-KB/provider invention |
| STT empty/timeout | Eligible provider recovery only under policy; otherwise clarification/end | No fabricated transcript/tool request |
| LLM unavailable/malformed | Bounded recovery/repair; no unauthorized decision | Brief safe response/end with failed turn recorded |
| TTS unavailable/disconnected | Respect output-generation/clear rules; terminate when speech delivery cannot be recovered | Failure retained even if caller hears no explanation |
| Malformed/unsupported media | Reject frame/connection, bounded error handling, no arbitrary decoder assumptions | Sanitized error/end reason |
| Tool validation/authorization denied | No mutation; persist rejection audit where possible | Explain/clarify; never switch to bypass denial |
| Meeting persistence conflict/failure | No scheduling success; uncertain commit requires reconciliation | Caller receives supported result, not invented reservation |
| Duplicate event/request | Deduplicate against operation/action identity | Existing result; no duplicate side effect |
| Media disconnect/process crash | Stop generation; reconcile one call; no silent resume/redial | Terminal/reconciliation status and incomplete evidence markers |
| Monitoring browser disconnect | Reconnect only monitoring, with state snapshot/history | Does not end an independent Plivo call or replay commands |
| Local media browser disconnect | End the local media session under contract | New session requires explicit user action |
| Expired/revoked UI authority | Deny protected operations/subscriptions; terminate voice authority safely if bound to it | Login/permission message without internal stack trace |
| Local model/hardware missing | Mark local/fallback profile unavailable; do not claim success | BLOCKED BY HARDWARE/required dependency where applicable |
| Maximum call duration or budget reached | Safe end, cancel work, record reason | No unbounded idle or generation loop |

Operational logs cannot replace a durable audit record; if persistence prevents recording a requested action, fail closed rather than promise an audit that does not exist. After crash, terminal reconciliation distinguishes observed events from inference. Process liveness, infrastructure readiness, and selected voice-profile availability are separate indicators.

## 14. UI, observation, privacy, and evaluations

**Source:** P FR-P-013–015, §§18, 21; M §§10, 17, 24–27; E §§19–22, 31–39.

### FRD-UI-001 — Required operator surfaces

| Surface | Required behavior |
| --- | --- |
| Login/setup guidance | Login/logout, expiry/denial, explicit bootstrap guidance when uninitialized |
| Dashboard | Active/recent calls, actual status counts, measured latency sample summary, sanitized provider/dependency state |
| Leads/detail | Create/edit/archive, consent evidence, opt-out/suppression, notes, related calls/meetings/follow-ups, gated test call |
| Campaigns/detail | Objective/lead/KB/profile configuration, readiness reasons, explicit start/pause/cancel, queue and actual progress |
| Local voice session | Microphone permission, start/stop, mode/profile, live state/transcript, playback/interrupt evidence |
| Calls/detail | Lifecycle, finalized/partial transcript distinction, generated/delivered response evidence, summary status, outcome, tool/retrieval/failover/timing/error timeline |
| Knowledge bases/documents | Upload/register, extraction/index/review status, retry failure, admin approval/withdrawal, source/version visibility |
| Meetings/follow-ups | Inspect and manage standalone records; due/status/conflict/suppression feedback |
| Settings/users | Sanitized profile/configuration health, tenant policy, user administration with role restrictions; no key reveal |
| Evaluation report | Administrator can inspect actual run cases/results/configuration/block reasons; run execution is bounded and clearly separate from live calling |

These may be routes, tabs, or panels in a small UI; the frontend framework and precise route structure are OPEN. Every control corresponds to real backend behavior. Lists support bounded pagination/filtering; local filtering is not a security boundary. All relevant forms/actions have loading, empty, invalid, disabled, success, failure, and unavailable states.

Live monitoring displays event sequence/state from the backend. Reconnect requests a current snapshot and missed observable events where retained; it never restarts an interrupted command. Stale data is labeled. Zero samples display “No measurements,” not zero latency. Credentials, internal stack traces, and unrestricted transcript access do not appear in unauthenticated screens.

### FRD-OBS-001 — Event identity and audit

Calls have stable correlation IDs, turns have stable turn IDs, and individual operations/actions have deduplication identity. Significant events include lifecycle, media admission, transcript partial/final/correction, accepted utterance, retrieval, model request/decision/validation, tool requested/allowed/denied/committed/uncertain, synthesis, playback, interruption/cancellation, provider retry/failover, summary result, and reconciliation.

Event metadata includes source, time, call/turn/operation linkage, normalized result/reason, and evidence status. Logs are structured and redacted. Audits include actor/session authority and relevant action references; tool and opt-out evidence is durable. Sequence and provider timestamps cannot alone authorize execution. Exact schemas and audit retention are OPEN.

Call identifiers are carried in traces/events and metric exemplars or equivalent correlation; unbounded per-call/tenant labels must not overwhelm Prometheus. Dashboard aggregates do not expose tenant transcripts. Prometheus/Grafana are protected operational surfaces, not open public tenant-data endpoints.

### FRD-OBS-002 — Timing semantics

| Measurement | Functional definition | Evidence limitation |
| --- | --- | --- |
| STT finalization | Accepted final-transcript time minus estimated end of caller speech at the normalized media boundary | Identify endpointing source; missing speech-end time means unavailable |
| LLM TTFT | First text delta minus model operation start | Buffered/non-streaming output is not a measured first-token event |
| LLM decision completion | Validated complete decision minus model operation start | Includes schema validation/repair as separately recorded work |
| TTS first audio | First usable audio frame minus synthesis request start | Not equivalent to caller hearing it |
| End-to-end turn latency | First response playback acknowledgment minus caller speech-end boundary | If no playback acknowledgment, report gateway-send proxy separately and leave true delivery latency unknown |
| Retrieval/tool duration | Operation end minus start | Success and failed/cancelled samples remain distinguishable |
| Failover overhead | Switch-path elapsed time from primary failure detection through fallback usable result | Additional delay is measured, not advertised savings |
| Connected call duration | End time minus connected time | Attempt/ringing duration remains separate |

Elapsed time uses a monotonic timing basis within a runtime where appropriate; UTC wall times support audit. Cross-system estimates are labeled. p50/p95 specify sample count, mode, time window, successful/failed/cancelled inclusion rules, and whether delivery or proxy timing was used. No target latency/concurrency number is presented as achieved before execution.

### FRD-COST-001 — Usage and cost truth

Persist provider-reported STT/TTS/audio units, telephony duration, and LLM token counts when available, by operation including retry/fallback work. Missing units are UNKNOWN, not zero. Estimates cite configured pricing version/date/currency and units; trial credits/local execution are labeled rather than described as provider invoices. Provider-billed values are separate verified imports if ever supported, not inferred from an estimate. Exact current prices are not selected in this FRD.

### FRD-PRIV-001 — Sensitive data and retention

Secrets originate in server-side environment/secret configuration and never return to the browser or model. Transcript/document/phone/commitment information is tenant-scoped sensitive data. Diagnostic logs minimize content, while authorized call-detail views show the retained evidence needed for review. Redaction must not transform a failed action into a success.

Default durable call audio recording is excluded by FD-12. Bounded temporary audio may support STT replay and must be discarded after its permitted window/call termination. Any later recording feature requires explicit scope, permission, storage, access, and deletion decisions. Transcript/document/event/audit retention and deletion windows are OPEN and block productionization freeze until defined. Archiving is not equivalent to privacy erasure.

### FRD-EVAL-001 — Evaluation and runtime evidence

The eventual dataset covers grounded/no-result/conflicting-source answers, tenant isolation, tool selection/validation/authorization/idempotency, meeting time clarification, opt-out priority, interruption, silence, timeout, eligible failover, ineligible failure, both providers failing, malformed output, summary correctness, and approved language profiles. Cases identify expected permitted actions, forbidden actions, fixtures, provider/mode configuration, and scoring method.

Run results include actual outputs/actions, source references, timings, configuration versions, sample counts, pass/failure/reviewer rationale, and block reasons. Model-based judgments, if used, are labeled with judge configuration and supported by deterministic security/action checks. Evaluation runs use isolated tenant fixtures and never dial external phones by default; real-call verification is an explicit authorized journey.

No conventional test framework is mandated. Follow M's preference for AI evaluations and actual runtime/critical-journey/clean-install verification. A local model run cannot prove Sarvam/Plivo worked; a mock failure injection cannot prove a real provider outage was exercised. Verification language remains IMPLEMENTED, VERIFIED, AI-EVALUATED, UNVERIFIED, or BLOCKED with precise evidence.

## 15. PRD traceability and observable completion

This mapping is the FRD-level trace, not the later standalone Acceptance Criteria Matrix or implementation traceability report.

| PRD requirement | FRD requirements | Completion evidence required later |
| --- | --- | --- |
| FR-P-001 Call Session | CALL-001–003; OBS-001 | One durable correlated attempt, lifecycle and identities visible |
| FR-P-002 Streaming Audio Input | CALL-004; TURN-001 | Live accepted audio before call recording completion |
| FR-P-003 Speech Recognition | TURN-001/003/005; PROV-004 | Real transcript events with finality and supported profile |
| FR-P-004 Turn Management | TURN-001/003/004 | Endpointing, bounded silence, interruption/cancellation exercised |
| FR-P-005 LLM Orchestration | TURN-002; RAG-001; TOOL-001 | Scoped context and validated decisions from actual model runs |
| FR-P-006 Speech Synthesis | TURN-002/004/005; PROV-004 | Actual compatible audio generated; failed/cancelled work distinguished |
| FR-P-007 Audio Playback | CALL-004; TURN-004; OBS-002 | Actual playback evidence, delivery limitation labeled |
| FR-P-008 Provider Abstraction | §2; PROV-001–004 | Adapter-independent engine verified across selected modes |
| FR-P-009 Local Fallback | PROV-001–004; CR-01 | Manual selection and eligible/ineligible automatic switch evidence |
| FR-P-010 RAG | KB-001/002; RAG-001 | Real ingestion/publication/retrieval/source trace; tenant isolation |
| FR-P-011 Tool Calling | TOOL-001–004; LEAD-003 | Allowed committed actions and rejected/duplicate/opt-out cases |
| FR-P-012 Call Summary | RESULT-001/002 | Grounded structured summary tied to real transcript/tool results |
| FR-P-013 Audit Trail | OBS-001; ID-003; PROV-003 | Correlated lifecycle/retrieval/tool/failure/switch events |
| FR-P-014 Latency Measurement | OBS-002 | Defined stage timings, sample counts, delivery/proxy distinction |
| FR-P-015 Cost Accounting | COST-001 | Actual units/unknowns and labeled pricing-based estimate |
| P §7.5 / §18 Campaign/UI | CAMP-001–003; UI-001 | Connected CRUD/start/pause/queue/detail workflows |
| P §10 Security/multi-tenancy | ID-001–003; TOOL-001; RAG-001; PRIV-001 | Backend-enforced scope and rejected bypasses |
| P §19 Failure expectations | §13; TURN-003/004; PROV-002–004 | Deterministic failure journeys and recorded outcomes |
| P §20 Consent/opt-out | LEAD-002/003; TOOL-002 | Eligibility preflight and persisted suppression |
| P §21 / E §22 AI evals | EVAL-001 | Executed cases/results; no invented metrics |
| P §§22–23 Success/first call | CALL/TURN; OBS; §17 | Actual two-turn phone journey, transcript and timing inspection |
| P §§10.7, 7.7 / M release standard | §17 | Clean startup/deployment/release checks after implementation |
| P §24 Future integration | §2; ID-003; TOOL-001 | Clean reusable boundaries without SynTask dependency |

The first business demo must visibly connect: eligible Lead → Campaign/objective → approved KB → real voice turns → grounded response → caller-confirmed demo request → committed Meeting → Call end → grounded summary/outcome → inspectable retrieval/tool/failover/timing evidence. Optional FollowUp must be explicitly requested/confirmed under the applicable rules.

## 16. Open decision register and freeze ownership

OPEN does not mean “use engineering judgment while coding.” Each decision must be resolved in the named artifact and cross-checked against this FRD before implementation of the dependent capability.

| ID | Decision still required | Owner document | Freeze condition |
| --- | --- | --- | --- |
| OD-01 | Approve/modify FD-01–13, especially inbound scope, roles, lead/disposition enums, concurrency, language, recording | FRD review | Functional approval recorded |
| OD-02 | Exact authentication/session approach, lifetimes, revocation, bootstrap, credential protection | Technical Architecture; API Contracts | Protected HTTP/WS/local-media journeys fully specified |
| OD-03 | Frontend technology/routes, deployment topology, worker/process ownership, transient-state boundaries | Technical Architecture; User Journeys | Locked stack extended only by explicit justified decisions |
| OD-04 | Plivo verified callbacks/media handshake, directions, canonical status mapping, public secure ingress | Provider Contracts; API + WebSocket Contracts | Official current provider capability references and connection/teardown journeys |
| OD-05 | Input/output codec, sample rate/channels/frame limits, resampling, playback acknowledgment/clear behavior | Provider Contracts; Architecture; WebSocket Contracts | End-to-end compatible media and cancellation contract |
| OD-06 | Exact Sarvam STT/TTS endpoints/models/voice/language limits; Groq/Ollama model; local model assets/hardware | Provider Contracts | Current primary-source verification, configuration/capability matrix |
| OD-07 | Embedding provider/model/version/dimension, extraction/chunking, retrieval thresholds, token/context budgets | AI/RAG Contracts; Data Model | Reproducible ingestion/query and reindexing policy |
| OD-08 | Exact entity IDs/schema, constraints, action ledger/idempotency keys, durable queue and uncertainty reconciliation | Data Model; Architecture | Concurrent writes/duplicate delivery/restart cannot create duplicate effects |
| OD-09 | Exact HTTP routes, request/response/errors/status codes, pagination, WS event sequencing/reconnect | API + WebSocket Contracts | Every user action has a canonical secure contract |
| OD-10 | Exact assistant/summary/tool schemas, caller-confirmation evidence, opt-out detection/ambiguity policy | AI/RAG/Tool Contracts | Validity/security boundaries and evaluation cases defined |
| OD-11 | Lead validation lengths, files/size/format bounds, notes/output limits, timezone/duration defaults | Data/API/Tool Contracts | No unconstrained or implicit input behavior |
| OD-12 | VAD/endpointing thresholds; utterance/ringing/silence/call limits; STT/LLM/TTS/RAG/tool/summary timeouts; total turn deadlines; backoff/cooldown; Redis grace; reconciliation limits | Provider/AI Contracts; Failure Matrix | Finite numeric values, precedence, budget consumption, and end behavior recorded |
| OD-13 | Retention/deletion/redaction windows for files, transcripts, temporary audio, audits, events, evaluations | Data Model; Architecture; Failure Matrix | Productionization gate includes actionable access/deletion policy |
| OD-14 | Whether Hindi/Hindi-English are required, optional, or excluded; supported fallback profile for each | FRD review; Provider/AI Contracts | No unsupported language silently degrades into inaccurate promises |
| OD-15 | Metrics names/labels/exemplars, dashboard visibility, exact health/readiness rules | Architecture; Acceptance Matrix | Operational truth separated from tenant-sensitive data and profile readiness |
| OD-16 | Pricing version sources/usage units, unavailable-usage semantics, estimation implementation | Provider Contracts | Estimates are reproducible and distinct from billing |
| OD-17 | Exact evaluation case count/scoring thresholds, deterministic checks, reviewer/judge rules, evidence format | AI Contracts; Acceptance Matrix | Security-critical requirements and accepted quality gates explicit |
| OD-18 | Pinned dependencies, environment names/defaults, local model setup, Windows/Linux commands, deployment ingress and packaging plan | Architecture; Provider Contracts; Build Plan | Fresh setup has no hidden credentials/assets/global dependencies |

P §25 decisions are accounted for: first call direction and campaign scheduling/consent behavior are proposed in this FRD; codec/provider/model/embedding/chunking/VAD/retries/timeouts/schema/event/WS/failover details are assigned above. Failover eligibility and bounded functional behavior are defined in §12; numeric deadlines and vendor classifications still require contracts.

## 17. Documentation gate and future engineering obligations

This FRD does not authorize implementation. The remaining sequence stays:

1. Detailed End-to-End User Journeys.
2. Technical Architecture.
3. Data Model.
4. API + WebSocket Contracts.
5. Provider Contracts.
6. AI / RAG / Tool Contracts.
7. Edge Cases + Failure Matrix.
8. Acceptance Criteria Matrix.
9. Build Plan.
10. Reconcile the existing Astra Execution Prompt against the approved complete set.

The PRD and existing Execution Prompt remain inputs; neither is silently rewritten. Each later document must preserve approved decisions or explicitly surface a proposed change. Implementation begins only after the user releases the documentation gate and the relevant decisions are resolved.

Future work must respect M/E: declared/pinned dependencies, safe complete environment placeholders, coherent vertical slices, real ingestion/tools/provider paths, authenticated tenant boundaries, AI evaluations, security/quality audit, runtime and critical-journey verification, clean installation, accurate traceability/reports, and clean ZIP inspection. No conventional testing framework is added unless explicitly required. No real secrets, private keys, caches, or unlicensed/large model weights are bundled blindly.

A code path can be IMPLEMENTED without being VERIFIED. The first real telephone journey requires actual Plivo/media/cloud-provider execution and at least two audible conversational turns. Local operation verifies its own path only. Blocked credentials/hardware are recorded precisely. No latency, cost, tool success, fallback success, phone connection, or evaluation score is fabricated. The final release ZIP remains prohibited during this documentation phase.

## 18. Review checklist

- Does the standalone scope through V7 match the intended finished product while preserving the first V1 milestone?
- Are FD-01–13 acceptable, particularly inbound restrictions, the two roles, serialized campaigns, supported languages, and recording default?
- Are the consent/suppression rules and caller-confirmation requirements correct?
- Are standalone Meeting/FollowUp semantics sufficient without external calendar/invitation integration?
- Are eligible failover, safe replay, bounded switching, and no blind configuration fallback correctly specified?
- Are all OPEN items assigned to later documents rather than delegated to implementation guesses?

**Document completion:** Draft authored and checked for source coverage and internal consistency.  
**Approval:** Pending user review.  
**Implementation/runtime/evaluation status:** Not started; no runtime or AI quality claims.  
**Stop point:** FRD only. No User Journey document, project implementation, or release ZIP has been created.

### Appendix A — Source snapshot

SHA-256 identifies the exact attached bytes read for this draft; it is not runtime verification.

| Source | SHA-256 |
| --- | --- |
| VoiceOps_PRD_v1.0.md | f63db0a271b639684090c541333e750a6705633cb25232d81ce64db8b81fe5de |
| Master Build Directive | 19f7b28bb3953457e3c28e978b37929417728c8ed85f6e32ca2e3e75b193f1ed |
| VoiceOps_Astra_Execution_Prompt_v1.0.md | ba8cc23a7b803966137d4f0ce435b836a55d60138784bebdfd3d8f1472f4c3d4 |
