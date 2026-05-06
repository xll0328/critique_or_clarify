# Critique-or-Clarify Automation Notes

Use OMX for sustained work in this repo, especially `ralplan` before larger changes and `ralph` for bounded refresh/validation loops.

## Project North Star

This project studies action selection under defective inputs: `answer`, `ask`, `challenge`, and `abstain` under ambiguity, false premises, stale premises, and conflicting evidence.

## Safe Automation Targets

- Refresh integrity/readiness artifacts from existing scripts.
- Advance human-validation queue preparation and packet consistency checks.
- Summarize completed model metrics and update paper-facing snippets.
- Audit stale-premise and action-label failures against existing outputs.

## Guardrails

- Human validation is currently a blocker unless real human decisions are present in the active queue.
- Do not call AI prefill, Codex review, or multi-pass consensus "human validated".
- Do not claim a finalized benchmark until validation and required pending model rows are complete.
- Do not launch large model downloads or GPU inference sweeps without explicit approval.
- Keep the framing as unified action selection, not a loose mixture of unrelated benchmarks.

## Preferred Stop Conditions

Stop when a task requires a human decision, a new model run, a large download, or a paper claim stronger than the current integrity dashboard permits.
