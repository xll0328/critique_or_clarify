# EMNLP 2026 Reviewer Attack Memo

Status: post-lock risk register after the Day-1 validation, DeepSeek-R1-Distill-Qwen-7B, and final submission-lock gates closed.

## Summary Counts

- `CRITICAL`: 0 open
- `MAJOR`: 4 open
- `MINOR`: 4 open

## Closed Or Reduced Findings

### CLOSED 1: The paper reads as a unified action-selection problem rather than a dataset mixture.

Original risk:
The strongest rejection path was "benchmark soup": ambiguity plus false premise plus stale facts plus conflict.

Current evidence:
The Abstract, Introduction, Figure 1 caption, Related Work ending, Task Definition, Benchmark Construction, and Results now repeat the same object: next-action selection under defective inputs. The paper frames all slices as input/evidence -> action decision -> constrained response, and the Results section states that rows are scored under one action ontology rather than as separate benchmark subtasks.

Current evidence:
The PDF-level first-two-page oral-readiness audit is current at `docs/emnlp2026_first_two_page_oral_readiness_audit.md`. It verifies that page 1 names the answer-generation gap, the Facebook example states the wrong-first-move failure, Figure 1 appears at the top of page 2 as a self-contained task schematic, and Related Work opens with the same "before judging answer text" boundary.

Current evidence:
The visual-balance audit is current at `docs/emnlp2026_first_two_page_visual_balance_audit.md`. It verifies that page 1 is dense but story-forward, Figure 1 is readable at paper scale, contributions appear before Related Work, and the first two pages preserve the intended visual path from title to task schematic to positioning.

Current evidence:
The full-PDF automated visual readiness audit is current at `docs/emnlp2026_full_pdf_visual_readiness_audit.md`. It renders all 13 pages, checks for blank pages and missing story anchors, and explicitly remains separate from final human PDF sign-off.

Residual action:
Re-read the full PDF after any layout change. Do not add new slice prose unless it reinforces the same action-selection object.

### CLOSED 2: Human validation is no longer pending.

Current evidence:
The active work queue is complete: `human_validation_queue_ok completed=61/61`. Section 3 describes this narrowly as sign-off for active labels and paper-facing arithmetic under the documented ontology, not as proof that the ontology is uniquely correct.

Residual action:
Keep the phrase "human-validated evidence bundle" scoped. Avoid broad claims such as "the benchmark is objectively human validated."

### CLOSED 3: The 7B reasoning checkpoint gate is no longer pending.

Current evidence:
DeepSeek-R1-Distill-Qwen-7B has completed dev and quick+stale metrics. The current expected gate outputs are dev action accuracy `0.3667`, dev utility `-0.4313`, quick+stale action accuracy `0.4500`, and quick+stale utility `-0.4750`.

Residual action:
Keep the conclusion local: in the completed Day-1 local matrix and prompt protocol, reasoning-style checkpoints do not automatically improve next-action calibration.

### CLOSED 4: Qualitative examples now target action-boundary errors.

Current evidence:
The qualitative table and prose cover stale premise, false premise, answerable-control over-caution, and conflict-but-answerable boundaries. The examples state why the utility loss is the wrong first action, not just wrong final wording.

Residual action:
Do not replace these with generic failure samples. The examples are serving a reviewer-facing task-definition role.

### CLOSED 5: Final artifact lock is scripted.

Current evidence:
`./scripts/run_submission_lock_checks.sh` syncs paper assets, checks scale/reasoning artifacts, requires complete human validation, runs the full pytest suite, builds the PDF, scans LaTeX logs, builds the anonymous review package, and scans the package. The current expected terminal state is a passing pytest suite and `submission_lock_checks_ok`.

Current oral-sprint coverage audit:
`experiments/day1/benchmark_expansion_coverage_audit.md` and `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md` record `560` paper-facing examples, with all four actions represented and a `0` example gap to the oral target size.

Current candidate intake:
`data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`, `_assets/emnlp2026_expansion_candidate_validation_queue.csv`, and `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md` include `160` accepted rows that are now promoted into the paper-facing split. `scripts/promote_validated_expansion_candidates.py` enforces `human_decision=accept` and writes `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl`.

Current oral/best-paper audit:
`docs/emnlp2026_oral_best_paper_quality_audit.md` marks the project not oral-ready. The largest reviewer-facing risks are now statistical depth and final human sign-off rather than missing visual preflight or frontier rows: split size, action coverage, the 35-entry bibliography threshold, automated full-PDF visual readiness, and frontier/high/medium/low 600-split API stress rows are met, but confidence estimation and final human PDF review remain below oral/best-paper bar.

Residual action:
Run the lock gate after every paper-facing change. Treat a fresh lock run as the only valid artifact-freeze signal.

### REDUCED 6: Reviewer response seeds now exist for the four major attack paths.

Current evidence:
`docs/emnlp2026_reviewer_response_seed_memo.md` gives paper-side defenses, response seeds, do-not-say constraints, and evidence links for benchmark-soup, utility-weight, reasoning-overclaim, intervention-overclaim, plus ask and hard abstain coverage.

Current triage:
`docs/emnlp2026_reviewer_triage_revision_memo.md` converts these risks into must-fix, should-fix, appendix-only, and defer buckets for the final 2026-05-25 ARR push.

Residual action:
Use the memo when editing paper or writing a rebuttal. Keep the final author response tailored to actual reviewer text.

### REDUCED 7: Citation coverage is mapped to the current related-work claims.

Current evidence:
`docs/emnlp2026_citation_coverage_audit.md` maps the cited clusters for standard QA, clarification, ambiguous QA, false premises, truthfulness, temporal QA, selective QA, calibration, and retrieval conflict to the exact manuscript claims they support.

Residual action:
Re-run the coverage audit after any new novelty, related-work, or benchmark-scope claim. Do not introduce first/only claims without a fresh literature search.

## Open Major Findings

### MAJOR 1: The reasoning-vs-instruct claim must stay scoped.

Risk:
Reviewers will push back if the paper implies that reasoning models are generally worse. The evidence supports a local checkpoint-and-prompt finding, not a universal statement.

Required wording:
In the completed Day-1 local matrix, the DeepSeek reasoning checkpoints do not improve next-action calibration over the strongest instruction baselines under the current prompt and parsing protocol. Format adherence is part of the measured behavior because the task requires an explicit action decision.

### MAJOR 2: The intervention result is promising, not a full method.

Risk:
`decision_first_balanced` has high raw utility but damages action accuracy and answer-supported behavior. A reviewer could argue that utility can be gamed by becoming too cautious.

Required wording:
Lead with `decision_first`, not the highest raw utility row. Phrase the intervention as an exploratory calibration lever, report answer-supported and defective-premise guardrails, and keep negative prompt variants visible.

### MAJOR 3: Utility weights require constant context.

Risk:
Reviewers may object that the main score encodes arbitrary preferences.

Required wording:
Utility is a diagnostic summary that encodes an asymmetric harm ordering, not a universal user-cost model. It must be read with action accuracy, over-answer rate, answer-supported accuracy, per-slice metrics, and qualitative examples.

### MAJOR 4: `ask` and hard `abstain` coverage remains less central than answer-vs-challenge coverage.

Risk:
The four-action ontology can look overclaimed if active results mostly exercise answer/challenge decisions.

Required wording:
The Day-1 empirical matrix most strongly supports answer-vs-challenge and evidence-conflict calibration claims. `ask` and hard `abstain` are ontology-defined and present in the canonical paper-facing split; do not over-generalize these claims without slice-level and robustness context.

## Minor Findings

### MINOR 1: Keep language restrained.

Avoid unsupported phrases such as "solves", "general safety", "universal", "breakthrough", and "objective benchmark." The paper should sound precise, not inflated.

### MINOR 2: Use consistent names.

Use one task name throughout: "next-action selection under defective inputs." Avoid alternating among "repair action", "defect handling", and "calibration" without definition.

### MINOR 3: Figure captions need to carry the story.

Figure 1 should say that the benchmark scores the action before response content. Figure 2 should say which failure mode it visualizes. Table 3 should state that intervention gains are guarded by answer-supported accuracy.

### MINOR 4: Do not hide negative ablations.

The negative prompt variants are useful: they show that simply adding more caution or critique language can damage answerable/control behavior. Keep them in the intervention table or appendix.

## Top Three Next Checks

1. Keep `docs/emnlp2026_reviewer_response_seed_memo.md` and `docs/emnlp2026_reviewer_triage_revision_memo.md` synchronized with any paper-facing claim change.
2. Keep `docs/emnlp2026_citation_coverage_audit.md` synchronized with any related-work or novelty-claim change.
3. Re-read the final PDF first two pages for flow after every layout change.

## Submission Recommendation

Submission-freeze candidate for internal review. The evidence gates are closed and the one-command lock gate passes, so the project is no longer blocked by missing 7B metrics or human validation. For an EMNLP oral/best-paper push, the remaining work is not more broad experimentation by default; it is preserving the unified action-selection story, keeping claims scoped to the completed evidence, and doing final human PDF-level review before external submission.
