# EMNLP 2026 Oral / Best Paper Quality Audit

Date: 2026-04-28

Status: not oral-ready. The current artifact is a credible submission-freeze candidate, but it is not yet at oral/best-paper confidence.

## Scorecard

- Paper-facing unique examples: `560` / `500`
- Candidate-augmented unique examples: `560`
- Paper-facing actions: `answer=200, ask=80, challenge=200, abstain=80`
- Candidate-augmented actions: `answer=200, ask=80, challenge=200, abstain=80`
- Candidate status: `accepted`, paper-facing: `True`
- Main model rows: `8`
- Canonical API rows: `4` (`qwen-turbo`, `qwen-plus-latest`, `gpt-4o-mini`, `gpt-4.1-mini`)
- Paper-facing figures: `6`
- Bibliography entries: `26`
- Citation commands: `21`

## Findings

| Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- |
| `MAJOR` | `frontier_evidence_partial_closure` | Canonical 560-split API contrast is now present (qwen-turbo, qwen-plus-latest, gpt-4o-mini, gpt-4.1-mini), but frontier evidence is still concentrated in one prompt policy and one split family. | Add one more distinct robustness control (prompt-constrained or policy-constrained) and at least one additional strong frontier-style control before oral-strength claims. |
| `MINOR` | `statistical_depth_partial_closure` | Bootstrap CIs now exist for local and API headline tables, but uncertainty is not yet fully propagated into all figure-level delta narratives. | Add CI/error bars to the remaining headline delta figures and reference uncertainty directly in result prose. |
| `MAJOR` | `slice_balance_risk` | The canonical split is full in action coverage, but slice balance is not yet target-balanced (`answerable_control=106`, `conflicting_evidence=94`). | Close the remaining slice-target imbalance with human-validated additions before framing per-slice conclusions as universal. |

## Top Actions

1. Complete one additional robustness control on the canonical split (non-repairing prompt or strict policy-constrained prompt), then integrate it into the same table/figure protocol.
2. Extend CI-aware reporting to all headline delta figures, not only the main comparison tables.
3. Run a targeted slice-balance follow-up for `answerable_control` and `conflicting_evidence` additions, promote only after validation queue completion.
4. Expand references from 26 toward 35-40 with targeted citations in benchmark/protocol/results sections, not only related work.
