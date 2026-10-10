# Audit remediation

| Audit | Root cause / change | Files | Evidence / status |
|---|---|---|---|
| P0-01 | Missing UI directory; added connected static client | frontend/* | HTTP assets 200; startup VERIFIED, UI interactions UNVERIFIED |
| P0-02 | Missing provisioning; schema v1 and bootstrap CLI | cli.py | IMPLEMENTED; DB execution BLOCKED |
| P0-03 | Missing install path; Compose/Docker/env/start guide | root, scripts/configure.py | IMPLEMENTED; Docker run BLOCKED |
| P0-04 | Old FRD conflicts; recorded latest scope overrides | ASSUMPTIONS_AND_DECISIONS | frozen artifact BLOCKED |
| P0-05 | Obsolete default; configurable GPT-OSS | config.py | official docs checked; runtime BLOCKED |
| P0-06 | Wrong TTS field; language_code | cloud.py | IMPLEMENTED; runtime BLOCKED |
| P0-07 | No live environment evidence | VERIFICATION_REPORT | basic HTTP VERIFIED; provider paths BLOCKED |
| P1-01 | STT consumes speech budget; separate larger stage budget | engine.py,base.py | IMPLEMENTED; live timing UNVERIFIED |
| P1-02 | Static owner; random token compare-renew/delete | media.py | IMPLEMENTED; Redis race UNVERIFIED |
| P1-03 | Clear prematurely considered done; gate output on ack | media.py | IMPLEMENTED; Plivo runtime BLOCKED |
| P1-04 | Turn created after STT; create at speech start | engine.py | IMPLEMENTED; runtime UNVERIFIED |
| P1-05 | Tool argument exceptions; controlled clarification | engine.py | IMPLEMENTED; audio runtime BLOCKED |
| P1-06 | ValueError HTTP 500; controlled 422 | main.py | IMPLEMENTED; input journeys UNVERIFIED |
| P1-07 | Silent worker errors; structured failure logs and reconnect | jobs.py | absent-Redis log VERIFIED; job recovery UNVERIFIED |
| P1-08 | Fixed single call; bounded admission setting | config.py,jobs.py | IMPLEMENTED; concurrency UNVERIFIED |

Audit sections 5–9 remain partially remediated: metrics, cost, evaluation coverage, full operator workflows and security qualification are open. No claim that all release blockers are closed.
