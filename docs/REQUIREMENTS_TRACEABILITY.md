# Traceability

| Requirement group | Implementation | Status |
|---|---|---|
| Identity and tenant scope | security.py, db.py, models.py | IMPLEMENTED; runtime UNVERIFIED |
| Leads, consent, suppression | domain.py, main.py | IMPLEMENTED; runtime UNVERIFIED |
| Voice, turns, transport | engine.py, audio.py, media.py | IMPLEMENTED; runtime BLOCKED |
| Primary/local provider contracts | providers/* | IMPLEMENTED; live runtime BLOCKED |
| Failover eligibility | providers/base.py, verify_policy.py | fixture policies VERIFIED; live fallback BLOCKED |
| RAG ingestion/retrieval | rag.py | IMPLEMENTED; runtime BLOCKED |
| Tool gateway | domain.py, policy.py | IMPLEMENTED; durable actions UNVERIFIED |
| Campaigns and outcomes | jobs.py, main.py | IMPLEMENTED; runtime UNVERIFIED |
| Frontend | frontend/* | assets VERIFIED; interactions UNVERIFIED |
| Observability | observability.py, infra/* | partial IMPLEMENTED; full requirement UNVERIFIED |
| Costs | usage events only | UNVERIFIED; ledger incomplete |
| AI evaluations | scripts/evaluate.py | runner IMPLEMENTED; execution BLOCKED |
| Startup | Dockerfile, compose, cli.py | HTTP startup VERIFIED; full-stack startup BLOCKED |
