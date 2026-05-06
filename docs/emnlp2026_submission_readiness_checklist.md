# EMNLP 2026 Submission Readiness Checklist

Date: 2026-04-27

Status: first submission-facing checklist for Critique-or-Clarify.

## Closed Gates

| Gate | Status | Command / Evidence |
| --- | --- | --- |
| Human validation complete | closed | `python scripts/validate_human_validation_queue.py --queue _assets/human_validation_work_queue.csv --require-complete` |
| DeepSeek-R1-Distill-Qwen-7B metrics | closed | `python scripts/check_scale_reasoning_status.py` |
| Paper PDF builds | closed | `./paper/build.sh` |
| Citation keys and bibliography usage resolve | closed | `pytest -q tests/test_paper_references.py` |
| Citation coverage audit | first freeze pass closed | `docs/emnlp2026_citation_coverage_audit.md` |
| Main figures and tables present | closed for first draft | `./scripts/sync_paper_assets.sh` and `./paper/build.sh` |
| Oral readability lock | closed for current internal freeze | `docs/emnlp2026_oral_readability_lock.md` |
| Full PDF visual readiness audit | closed for current internal freeze | `docs/emnlp2026_full_pdf_visual_readiness_audit.md` |
| Final local clarity pass | closed for current internal freeze | `docs/emnlp2026_final_local_clarity_pass.md` |
| Benchmark expansion coverage audit | closed | `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md` |
| Ask/abstain candidate validation queue | closed | `_assets/emnlp2026_expansion_candidate_validation_queue.csv` |
| Validated candidate promotion tool | closed | `scripts/promote_validated_expansion_candidates.py` |
| Oral/best-paper quality audit | opened for oral sprint | `docs/emnlp2026_oral_best_paper_quality_audit.md` |
| Paper asset references resolve | closed | `pytest -q tests/test_paper_assets.py` |
| Manuscript local-path anonymity | closed for first draft | `pytest -q tests/test_paper_anonymity.py` |
| Paper claim-scope guardrails | closed for first draft | `pytest -q tests/test_paper_claim_scope.py` |
| Reviewer-attack response seeds | first pass closed | `docs/emnlp2026_reviewer_response_seed_memo.md` |
| Venue-form transfer packet | form-ready internal draft closed | `docs/emnlp2026_venue_form_transfer_packet.md` |
| Final submission lock gate | closed for current freeze | `./scripts/run_submission_lock_checks.sh` |
| Core result numbers macro-backed | closed for scale/reasoning, quick+stale, and intervention claims | `paper/tables/day1_scale_reasoning_macros.tex`; `paper/tables/day1_quick_stale_macros.tex`; `paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex` |

## Open Submission Work

| Item | Priority | Current State | Next Action |
| --- | --- | --- | --- |
| Related Work coverage review | high | Selective QA / abstention coverage added with verified ACL citation; first freeze-pass coverage audit is closed at `docs/emnlp2026_citation_coverage_audit.md`. | Re-run citation coverage after any new claims are added. |
| Final numeric audit | high | Current submission-freeze audit exists at `docs/emnlp2026_numeric_claim_audit.md`; core main-text result prose, quick+stale claims, intervention claims, and final lock output are macro- or gate-backed. | Re-run after any experiment freeze or prose expansion. |
| Oral readability lock | high | Current internal freeze is closed at `docs/emnlp2026_oral_readability_lock.md`; it verifies the 90-second reviewer story across pages 1-2 and the main result/figure/intervention pages. | Re-run after any abstract, Figure 1, results, Figure 2, or intervention edit. |
| Full PDF visual readiness | high | Current automated full-manuscript render/readability preflight is closed at `docs/emnlp2026_full_pdf_visual_readiness_audit.md`; it renders all 13 pages and checks story anchors, blank pages, and text extraction. | Re-run after any PDF build or layout-affecting edit; this does not replace final human PDF sign-off. |
| Final local clarity pass | high | Current internal freeze is closed at `docs/emnlp2026_final_local_clarity_pass.md`; it verifies scoped local prose, page-neutral wide-table placement, and human-only final checks. | Re-run after any layout, float, wide-table, or final-signoff wording edit. |
| First-two-page story and visual balance | high | Oral-readiness PDF story and visual-balance audits closed: Abstract, Introduction, Figure 1 caption, and Related Work handoff emphasize the wrong-first-move framing and shared action-decision record, with Figure 1 readable at paper scale. | Keep `tests/test_paper_story_flow.py`, `tests/test_first_two_page_oral_readiness.py`, and `tests/test_first_two_page_visual_balance.py` passing; re-read after any layout change. |
| Results / qualitative story | high | First polish pass closed: shared action ontology and utility-loss examples are explicit in the manuscript. | Re-read after final PDF layout pass. |
| Utility sensitivity | high | First pass closed: Task Definition states that utility weights encode an asymmetric harm ordering, and Limitations says claims must agree with disaggregated metrics. | Re-check only if weights, tables, or intervention claims change. |
| Reviewer-response preparation | high | First pass closed: `docs/emnlp2026_reviewer_response_seed_memo.md` covers benchmark-soup, utility-weight, reasoning-overclaim, intervention-overclaim, and ask/hard-abstain coverage objections. | Keep synchronized with final paper wording and tailor final rebuttal text to actual reviews. |
| Oral/best-paper quality gap | high | `docs/emnlp2026_oral_best_paper_quality_audit.md` marks the current artifact not oral-ready: `560` paper-facing examples (`answer=200`, `ask=80`, `challenge=200`, `abstain=80`), `10` main model rows, `6` figures, and `35` bibliography entries. Automated full-PDF visual readiness is closed, but final human PDF sign-off is still required. | Treat this audit as the sprint dashboard until confidence estimates and final human review are strengthened. |
| Benchmark construction prose | high | First polish pass closed: source-to-schema normalization and shared action-decision record are explicit in Section 3. | Expand only if page budget allows an appendix. |
| Responsible NLP checklist | high | Current submission-freeze preflight exists at `docs/emnlp2026_responsible_nlp_checklist.md`; form-ready short answers are consolidated in `docs/emnlp2026_venue_form_transfer_packet.md`. | Transfer into the venue's exact checklist format when the submission form is active, with human sign-off. |
| Reproducibility appendix | high | Appendix-ready command block exists at `docs/emnlp2026_reproducibility_appendix.md`; form-ready artifact and lock-gate answers are consolidated in `docs/emnlp2026_venue_form_transfer_packet.md`. | Refresh after any new experiment run or artifact freeze. |
| Anonymization | high | Paper sources, paper README, and paper build script pass the local-path anonymity test; `scripts/build_review_package.sh` creates a clean paper package and is wrapped by the final lock gate. | Re-run `./scripts/run_submission_lock_checks.sh` after final artifact freeze. |
| Intervention strength | medium | `decision_first` is promising but scoped, and the answer-supported / defective-premise guardrail is explicit in Section 6. | Keep as an exploratory calibration probe unless follow-up controller results preserve answerability and improve slice coverage. |
| Benchmark expansion for oral target | medium | Canonical paper-facing coverage now uses `560` examples (`answer=200`, `ask=80`, `challenge=200`, `abstain=80`) and meets the expansion size target; remaining gaps are slice-level (`conflicting_evidence=94/120`, `answerable_control=106/120`) and challenge/action-depth balance. | Follow `docs/emnlp2026_oral_best_paper_sprint_execution_plan.md`; prioritize slice-level balance and robustness runs before broadening the model matrix further. |
| Ambiguous-intent / hard-abstain coverage | high | `ask` and `abstain` are now paper-facing in the canonical split; keep claim language aligned to canonical coverage and avoid implying balanced evidence density beyond documented slice counts. Candidate intake exists at `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl` and `_assets/emnlp2026_expansion_candidate_validation_queue.csv`. | Promote any newly sampled candidates with full validation before changing the claim footprint. |

## Final Lock Commands

Run before any submission package is created:

```bash
./scripts/run_submission_lock_checks.sh
```

This gate syncs paper assets, checks scale/reasoning artifacts, requires all human-validation rows, runs the full test suite, builds the paper PDF, scans LaTeX logs, builds the anonymous review package, and scans the package for aux/log files or internal paths.

## Review-Package Risks

- Working-repo paths such as `/data/sony/...` are acceptable in internal docs but must not appear in the anonymized submitted artifact; paper-support files are now covered by `tests/test_paper_anonymity.py`.
- Model-cache paths should be converted to model identifiers or documented separately in reproducibility notes.
- Long generated outputs should stay in artifacts or appendix material; the main paper should only show compact action-boundary evidence.
- Claims about reasoning models must stay scoped to the completed local checkpoint matrix and prompt protocol.
