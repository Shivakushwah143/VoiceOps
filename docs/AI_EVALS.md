# Evaluations

scripts/verify_policy.py executes deterministic fault-injection fixtures, opt-out phrase matching and invalid-input rejection. Results are policy verification, not AI-quality scores.

scripts/evaluate.py runs actual configured LLM calls for grounded answer, missing knowledge, scheduling clarification, opt-out and prompt injection. It validates structured outputs and saves raw outputs for human review; it does not infer groundedness from schema validity. Current five cases BLOCKED. Remaining requested end-to-end audio/tool/isolation/summary scenarios are open release work.
