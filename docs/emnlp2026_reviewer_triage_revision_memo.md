# EMNLP 2026 Reviewer Triage Revision Memo

Date: 2026-05-06

Status: Sprint-2 reviewer-risk triage for the current submission-freeze artifact.
This memo turns the reviewer attack notes into an edit order. It is not a
substitute for final human scientific judgment or the official submission form.

Timing anchor: the EMNLP 2026 main-track ARR deadline is 2026-05-25, 11:59PM
UTC-12. Source checked on 2026-05-06:
`https://2026.emnlp.org/calls/main_conference_papers/`.

## Triage Principle

With less than three weeks before the ARR deadline, do not start broad new
experiments by default. Prefer edits that make the current evidence harder to
misread:

1. preserve the unified action-selection framing;
2. keep canonical 560-example claims separate from 600-example stress evidence;
3. make uncertainty and utility guardrails visible;
4. keep `decision_first` an exploratory calibration probe;
5. keep human-only sign-off outside automated claims.

## Reviewer Personas

| Persona | Likely Concern | Current Evidence | Triage |
| --- | --- | --- | --- |
| Reviewer 1: novelty and positioning | The task may look like benchmark soup rather than a new setting. | Abstract, Introduction, Figure 1, Task Definition, Benchmark Construction, and Related Work all repeat "next-action selection under defective inputs"; `docs/emnlp2026_first_two_page_oral_readiness_audit.md` and `docs/emnlp2026_reviewer_response_seed_memo.md` guard the story. | Must-fix only if a paper edit weakens the first-two-page action-selection framing. |
| Reviewer 2: benchmark validity | Labels and utility may look subjective. | `docs/action_ontology.md`, `docs/human_validation_protocol.md`, `_assets/human_validation_work_queue.csv`, and `docs/emnlp2026_numeric_claim_audit.md` document the ontology, validation queue, and metric sources. | Must-fix: keep utility text paired with action accuracy, over-answer rate, slice metrics, and examples. |
| Reviewer 3: experiments and statistics | Model coverage and confidence may not be oral-strength. | `docs/emnlp2026_oral_best_paper_quality_audit.md` records `10` model rows, `6` figures, `35` bibliography entries, API stress rows, and remaining not-oral-ready status. | Must-fix: do not claim oral-ready; should-fix: improve confidence narration or appendix evidence if time permits. |
| Devil's Advocate | The 600-example split may look like moving the benchmark after seeing results. | `docs/emnlp2026_claim_ledger.md`, `paper/sections/05_results.tex`, and `paper/sections/08_limitations.tex` scope the 600-example split as stress evidence, not the canonical benchmark. | Must-fix: prevent any prose that says the 600-example split replaces the canonical 560-example split. |

## Must-Fix Before Submission

| Item | Owner Surface | Required Edit Or Check | Stop Condition |
| --- | --- | --- | --- |
| Canonical-vs-stress split scope | Results, Limitations, claim ledger | The canonical split remains `560`; the slice-balanced `600` split is sensitivity or stress evidence only. | Stop if a new result or table would make 600 the de facto headline benchmark without a new validated freeze. |
| Utility interpretation | Task Definition, Results, Intervention, Limitations | Utility must be described as an asymmetric harm-ordering diagnostic and read with disaggregated metrics. | Stop if a sentence uses utility alone to claim broad assistant helpfulness. |
| Intervention status | Intervention, Abstract, Introduction | `decision_first` stays an exploratory calibration lever; negative variants remain visible. | Stop if the method is described as a robust controller or deployment-ready policy. |
| Reasoning-model claim | Abstract, Introduction, Results | Scope DeepSeek reasoning results to completed Day-1 local checkpoints and the current prompt/parsing protocol. | Stop if wording generalizes to all reasoning models, chain-of-thought, or model families. |
| Final human sign-off | Submission checklist, venue packet | Automated audits do not replace final human PDF read, author metadata, conflicts, reviewer registration, or submit click. | Stop if an automated artifact is described as final human validation. |

## Should-Fix Before Submission

| Item | Best Target | Why It Matters |
| --- | --- | --- |
| Confidence narration | Results and Limitations | First pass closed in `paper/sections/05_results.tex` and `paper/sections/08_limitations.tex`: intervals are framed as local uncertainty checks that support coarse patterns, not fine-grained model rankings. |
| Reviewer-response synchronization | `docs/emnlp2026_reviewer_response_seed_memo.md` | Every major paper-facing claim should have a scoped response seed and evidence path. |
| Citation-to-claim alignment | Related Work and citation coverage audit | The bibliography count meets the threshold, but the final risk is claim placement rather than raw citation count. |
| First-two-page reread | `paper/main.pdf` pages 1-2 | Oral enthusiasm depends on whether the action-selection object is legible before reviewers reach tables. |
| Appendix routing | Reproducibility and coverage artifacts | Dense validation and coverage details should support the paper without making the main text read like process notes. |

## Appendix-Only Or Defer

| Candidate Work | Decision | Reason |
| --- | --- | --- |
| Broad new model matrix | Defer unless tied to a fatal reviewer objection. | New runs risk creating unfrozen claims and consume time that should go to paper polish and sign-off. |
| More API stress rows | Defer by default. | Frontier/high/medium/low stress evidence already exists; more rows are less valuable than claim discipline. |
| Recanonicalizing the 600-example split | Defer. | It changes answer counts and needs a new validation/freeze decision. |
| Large ontology rewrite | Defer. | The current ontology is already wired through tests, paper sections, figures, and validation docs. |
| New utility weights | Defer. | Changing weights would force table, macro, prose, audit, and reviewer-response updates. |

## Safe Next Editing Order

1. Read pages 1-2 of `paper/main.pdf` for action-selection clarity.
2. Read Results and Limitations for canonical-vs-stress split language.
3. Read Intervention for overclaim and answer-supported guardrail language.
4. Run targeted paper tests after prose edits.
5. Run `./scripts/run_submission_lock_checks.sh` before any artifact freeze.

## Do Not Say

- "oral-ready"
- "best-paper-ready"
- "the 600-example split replaces the canonical benchmark"
- "utility captures real user costs"
- "decision_first is a robust controller"
- "reasoning models fail at defective inputs"
- "automated audit is final human sign-off"
