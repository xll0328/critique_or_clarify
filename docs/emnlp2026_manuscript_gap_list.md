# EMNLP 2026 Manuscript Gap List

Date: 2026-04-27

Status: paper-facing gap list after the Day-1 validation, DeepSeek-R1-Distill-Qwen-7B, responsible-NLP preflight, and final lock gates closed.

## Current Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Human validation | closed | `61 / 61` rows completed; validator passes with `--require-complete`. |
| 7B reasoning checkpoint | closed | DeepSeek-R1-Distill-Qwen-7B dev and quick+stale metrics are present in the dashboard. |
| Main result tables | closed for Day-1 | Generated under `experiments/day1/tables/` and synced into `paper/tables/`. |
| Main figures | closed for first draft | Figure 1 and Figure 2 are generated and synced into `paper/figures/`. |
| Compileable draft | closed for scaffold | `paper/main.pdf` builds in ACL/ARR review style. |
| Related Work | coverage pass closed | Verified-citation draft is in `paper/sections/02_related_work.tex`; selective QA / abstention coverage has been added. |
| First-two-page story and visual balance | oral-readiness PDF audits closed | Abstract, Introduction, Figure 1 caption, and Related Work handoff now repeat the same wrong-first-move and shared action-decision-record framing; `docs/emnlp2026_first_two_page_oral_readiness_audit.md`, `docs/emnlp2026_first_two_page_visual_balance_audit.md`, `tests/test_paper_story_flow.py`, `tests/test_first_two_page_oral_readiness.py`, and `tests/test_first_two_page_visual_balance.py` guard this. |
| Oral readability lock | closed for current internal freeze | `docs/emnlp2026_oral_readability_lock.md` verifies the 90-second reviewer story across PDF pages 1-2 and the main result/figure/intervention pages. |
| Full PDF visual readiness audit | closed for current internal freeze | `docs/emnlp2026_full_pdf_visual_readiness_audit.md` renders all 13 pages and checks for blank pages, missing story anchors, and text-extraction integrity; this is automated preflight, not final human sign-off. |
| Final local clarity pass | closed for current internal freeze | `docs/emnlp2026_final_local_clarity_pass.md` verifies local prose scope, human-only final checks, and page-neutral wide-table placement between intervention and qualitative analysis. |
| Benchmark expansion coverage audit | opened for oral sprint | `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md` records `560` unique paper-facing examples with `answer=200`, `ask=80`, `challenge=200`, `abstain=80`; residual slice gaps are `answerable_control=14`, `conflicting_evidence=26`. |
| Ask/abstain candidate intake | validated and promoted | `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`, `data/candidates/emnlp2026_ask_abstain_seed_candidates_manifest.json`, and `_assets/emnlp2026_expansion_candidate_validation_queue.csv` now have `160` accepted rows promoted into `data/processed/emnlp2026_expanded_dev.jsonl`. |
| Results and qualitative story | first polish pass closed | Results now states that all rows share one action ontology; qualitative prose names the utility loss for stale/false/answerable/conflict boundaries. |
| Benchmark construction prose | first polish pass closed | Section 3 now states the source-to-schema normalization and the shared action-decision record. |
| Utility sensitivity note | first pass closed | Task Definition and Limitations now state that utility weights encode an asymmetric harm ordering and must be read with action accuracy, over-answer rate, and slice-level metrics. |
| Paper asset/citation/anonymity tests | closed for first draft | `tests/test_paper_assets.py`, `tests/test_paper_references.py`, and `tests/test_paper_anonymity.py` pass; bibliography entries must be cited. |
| Paper claim-scope tests | closed for first draft | `tests/test_paper_claim_scope.py` guards coverage scope, utility interpretation, reasoning-model scope, and intervention guardrails. |
| Citation coverage audit | first freeze pass closed | `docs/emnlp2026_citation_coverage_audit.md` maps the current related-work clusters to paper claims and records the no-first/only-claim boundary. |
| Numeric claim audit | current freeze closed | `docs/emnlp2026_numeric_claim_audit.md`; scale/reasoning, quick+stale, intervention, and final lock claims are macro- or gate-backed. |
| Reviewer-attack response seeds | first pass closed | `docs/emnlp2026_reviewer_response_seed_memo.md` prepares scoped responses for benchmark-soup, utility-weight, reasoning-overclaim, intervention-overclaim, ask/hard-abstain coverage, and statistics/CI overclaim objections. |
| Intervention claim | scoped first pass closed | Section 6 now reports the `decision_first` gain together with answer-supported and defective-premise guardrails; keep the claim exploratory unless a stronger controller lands. |
| Venue-form transfer packet | form-ready internal draft closed | `docs/emnlp2026_venue_form_transfer_packet.md` consolidates responsible-NLP, reproducibility, privacy, artifact, compute-disclosure, and human-only final-check answers. |
| Submission checklist | closed for current freeze | Responsible NLP and reproducibility preflights exist; paper-source anonymity and final lock tests cover support files and package hygiene. |

## Must-Fix Before Internal Review

1. First-two-page story and visual-balance lock.
   The main object is now repeated across Abstract, Introduction, Figure 1 caption, Task Definition, and Related Work handoff. The current PDF-level story and visual-balance audits are closed; final review should preserve compression and visual balance, not re-open the core framing.

2. Scoped reasoning-model claim.
   The DeepSeek-R1-Distill-Qwen results support a local completed-checkpoint finding, not a universal claim about reasoning models. This wording is now guarded by `tests/test_paper_claim_scope.py`.

3. Intervention wording lock.
   The paper can lead with `decision_first` as an exploratory calibration probe because the answer-supported guardrail is now explicit. Do not upgrade it to a general method claim without follow-up controller evidence; keep negative variants visible.

## Should-Fix Before Submission

| Item | Target |
| --- | --- |
| Citation audit | Closed as a test gate and coverage audit: every `\cite` key resolves, every bibliography entry is used, and `docs/emnlp2026_citation_coverage_audit.md` maps citation clusters to paper claims. |
| Numeric audit | Every reported number traces to metric JSON, generated tables, or dashboard artifacts. |
| Utility sensitivity note | First pass closed in Task Definition and Limitations; re-check only if utility weights or intervention claims change. |
| Ethics and responsible NLP | Current submission-freeze preflight exists at `docs/emnlp2026_responsible_nlp_checklist.md`; form-ready transfer answers are consolidated in `docs/emnlp2026_venue_form_transfer_packet.md`. |
| Reproducibility appendix | Draft exists at `docs/emnlp2026_reproducibility_appendix.md`; form-ready artifact and lock-gate answers are consolidated in `docs/emnlp2026_venue_form_transfer_packet.md`. |
| Anonymization pass | Paper-source/support-file test is active; `scripts/build_review_package.sh` creates the clean paper package. |
| Oral readability lock | Closed for current internal freeze; preserve `docs/emnlp2026_oral_readability_lock.md` after any abstract, Figure 1, results, Figure 2, or intervention edit. |
| Full PDF visual readiness | Closed for current internal freeze at `docs/emnlp2026_full_pdf_visual_readiness_audit.md`; rerun after any build or layout edit, then still require a final human PDF read. |

## Current Best-Paper Risk Register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| The task looks like a loose dataset merge. | critical | First pass closed: action selection is now the repeated formal object in the title, abstract, intro, Figure 1 caption, task section, and Related Work. Keep this wording stable during later edits. |
| The method contribution is too small. | major | Frame intervention as a calibration probe unless a robust controller result lands. |
| Utility weights look arbitrary. | reduced | Task Definition now states the asymmetric harm-ordering interpretation; Limitations ties claims to agreement with action accuracy, over-answer rate, and slice-level metrics. |
| `ask` and hard `abstain` are under-covered in oral-balanced composition. | reduced | `ask` and `abstain` are paper-facing in the canonical split; remaining risk is slice balance (`answerable_control` and `conflicting_evidence`) and model frontier depth. |
| Evidence bundle is too small for oral/best-paper claims. | major | Sprint execution plan now targets an expanded evidence bundle: `docs/emnlp2026_oral_best_paper_sprint_execution_plan.md`; generated coverage audit tracks the concrete deficits. |
| Reasoning-model result is overclaimed. | major | Scope to local checkpoint matrix and include JSON adherence caveat. |
| Reviewer attacks are answered ad hoc. | reduced | `docs/emnlp2026_reviewer_response_seed_memo.md` now gives scoped response seeds and do-not-say constraints for the major objection paths, including confidence-interval overclaim risk. |
| Related Work misses close prior tasks. | reduced | Verified citation pass now covers ambiguity, false premises, stale facts, selective QA / abstention, retrieval conflict, and calibration; `docs/emnlp2026_citation_coverage_audit.md` records the current coverage map. |
| Oral-level story becomes diluted by late edits. | reduced | `docs/emnlp2026_oral_readability_lock.md` now records the 90-second reviewer takeaway and the page-level anchors that must survive edits. |

## Next Execution Order

1. Preserve the oral readability lock after any abstract, Figure 1, results, Figure 2, or intervention edit.
2. Preserve `docs/emnlp2026_final_local_clarity_pass.md` after any layout, float, or wide-table edit.
3. Expand model matrix on `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl` (API + local reruns where useful) before changing manuscript claims on action-balance behavior.
4. Copy the venue-form transfer packet into the official submission form when active, with human author sign-off.
5. Keep the citation coverage audit and reviewer response seed memo synchronized with any claim, table, or wording change.
