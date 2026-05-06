# EMNLP 2026 Citation Coverage Audit

Date: 2026-04-27

Status: first freeze-pass citation and related-work coverage audit for the current manuscript.

## Summary

- `CRITICAL`: 0 open
- `MAJOR`: 0 open for the current claim scope
- `MINOR`: 2 residual checks after any prose expansion

This audit is not an exhaustive literature survey. It records whether the current paper claims are backed by the cited clusters that appear in the manuscript, and whether the paper avoids overclaiming novelty beyond those citations.

## Mechanical Citation Gate

Current test coverage:

- `tests/test_paper_references.py` verifies that every `\cite` key in the paper resolves in `paper/references.bib`.
- The same test verifies that every bibliography entry is used in the paper.
- The final artifact lock runs the reference test through `./scripts/run_submission_lock_checks.sh`.

Current cited keys:

- `kwiatkowski-etal-2019-natural`
- `rajpurkar-etal-2018-know`
- `aliannejadi-etal-2019-asking`
- `min-etal-2020-ambigqa`
- `stelmakh-etal-2022-asqa`
- `yu-etal-2023-crepe`
- `lin-etal-2022-truthfulqa`
- `kasai-etal-2023-realtimeqa`
- `vu-etal-2023-freshllms`
- `kamath-etal-2020-selective`
- `shaier-etal-2024-adaptive`
- `liu-etal-2025-open`
- `kadavath-etal-2022-language`

## Coverage Map

| Manuscript claim | Citation cluster | Current support | Residual risk |
| --- | --- | --- | --- |
| Standard QA evaluates answer generation, not necessarily first action choice. | Natural Questions and SQuAD-style QA: `kwiatkowski-etal-2019-natural`, `rajpurkar-etal-2018-know`. | Sufficient for the contrast with answer-production benchmarks. | Do not imply these benchmarks are flawed; say they optimize a different object. |
| Ambiguous or underspecified queries motivate `ask`. | Clarification and ambiguous QA: `aliannejadi-etal-2019-asking`, `min-etal-2020-ambigqa`, `stelmakh-etal-2022-asqa`. | Sufficient for motivating `ask` as one action in the ontology. | Current empirical evidence is not a complete ask evaluation. Keep that limitation visible. |
| False-premise and truthfulness work motivates `challenge`. | False presupposition and truthfulness: `yu-etal-2023-crepe`, `lin-etal-2022-truthfulqa`. | Sufficient for the defective-premise slice motivation. | Avoid saying the paper is the first to study false premises. The contribution is the shared action-selection framing. |
| Stale-premise examples are related to temporal QA and freshness. | Time-sensitive QA and fresh knowledge: `kasai-etal-2023-realtimeqa`, `vu-etal-2023-freshllms`. | Sufficient for motivating stale fact failures. | Keep stale coverage scoped to the current quick+stale examples. |
| Abstention and uncertainty motivate `abstain`, but do not replace challenge or ask. | Unanswerable/selective QA and calibration: `rajpurkar-etal-2018-know`, `kamath-etal-2020-selective`, `kadavath-etal-2022-language`. | Sufficient for positioning abstain as one action rather than the whole task. | Do not claim a complete evaluation of hard abstain behavior. |
| Retrieval conflict is a distinct evidence condition inside the same action space. | Retrieval conflict and adaptive QA: `shaier-etal-2024-adaptive`, `liu-etal-2025-open`. | Sufficient for motivating evidence-conflict examples and answer-vs-abstain boundaries. | Keep the boundary rule: conflict alone does not force abstain when support remains. |
| The paper's contribution is unifying these conditions as next-action selection under defective inputs. | Related Work synthesis across all above clusters. | Supported as a framing contribution, not as a first/only claim. | Do not use wording like "no prior work" or "first benchmark for defective inputs" without a new external search. |

## Reviewer-Facing Positioning

The safest related-work sentence is:

The cited tasks study important pieces of defective-input handling, including clarification, false-premise correction, temporal robustness, abstention, calibration, and retrieval conflict; this paper evaluates these behaviors as one next-action selection problem before response generation.

Avoid these claims:

- "No prior work studies defective inputs."
- "This is the first benchmark for hallucination safety."
- "The citation set exhaustively covers assistant calibration."
- "The benchmark fully evaluates ask and abstain."

## Residual Checks

1. Re-run this audit after any new novelty claim, related-work paragraph, or benchmark-scope sentence.
2. If the submission version adds a stronger "first" or "only" claim, perform a fresh literature search before freezing that wording.
3. Keep `docs/emnlp2026_reviewer_response_seed_memo.md` aligned with this audit so rebuttal seeds cite the same scope.
