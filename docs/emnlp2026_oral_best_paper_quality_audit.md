# EMNLP 2026 Oral / Best Paper Quality Audit

Date: 2026-04-29

Status: not oral-ready. The current artifact is a credible submission-freeze candidate, but it is not yet an oral/best-paper-grade evidence package.

## Scorecard

- Paper-facing unique examples: `560` / `500`
- Slice-balanced stress split: `600`
- Candidate-augmented unique examples: `560`
- Paper-facing actions: `abstain=80, answer=200, ask=80, challenge=200`
- Stress split actions: `abstain=80, answer=240, ask=80, challenge=200`
- Candidate-augmented actions: `abstain=80, answer=200, ask=80, challenge=200`
- Candidate status: `accepted`, paper-facing: `True`
- Main model rows: `10` (local `5`, API `5`)
- Paper-facing figures: `6`
- Bibliography entries: `35`
- Citation commands: `33`
- Qwen-plus-latest (main) 600-vs-560 delta: `Δaction=+0.0096`, `Δutility=+0.0212`
- Qwen-plus-latest (guarded) 600-vs-560 delta: `Δaction=+0.0079`, `Δutility=-0.0372`
- GPT-4.1-mini (decision-first) 600-vs-560 delta: `Δaction=+0.0076`, `Δutility=-0.0371`
- Qwen-turbo (decision-first) 600-vs-560 delta: `Δaction=+0.0107`, `Δutility=-0.0357`
- GPT-5-chat-latest (decision-first) 600-vs-560 delta: `Δaction=+0.0047`, `Δutility=-0.0363`

## Findings

| Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- |
| `MINOR` | `slice_balance_scope_canonical_only` | Canonical split still has unresolved slice gaps (answerable_control gap=14, conflicting_evidence gap=26), but a slice-balanced 600-example stress split is available and evaluated (qwen-plus-latest main Δaction=+0.0096, guarded Δaction=+0.0079). Additional stress rows: gpt-4.1-mini decision-first Δaction=+0.0076, qwen-turbo decision-first Δaction=+0.0107, gpt-5-chat-latest decision-first Δaction=+0.0047. | Keep headline claims scoped to the canonical split and report full-split sensitivity as stress evidence, not as a replacement benchmark. |

## Top Actions

1. Use the completed GPT-5-chat-latest row as the strong API/frontier control; do not broaden the model matrix further unless it answers a specific reviewer objection.
2. Keep the 600-example split framed as stress evidence: frontier/high/medium/low API rows now triangulate slice-balance sensitivity, but the canonical 560 remains the headline benchmark.
3. Bibliography breadth now meets the 35-entry oral threshold; only add more citations if they support a concrete claim not already covered.
4. Keep the full-split sensitivity claims CI-aware: the delta intervals overlap zero, so report the 600-example split as stress evidence rather than a stronger replacement benchmark.
