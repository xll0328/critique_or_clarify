# EMNLP 2026 Final Push TODO

Date: 2026-05-06

Status: active final-push dashboard from 2026-05-06 through the EMNLP 2026 ARR submission deadline on 2026-05-25, 11:59PM UTC-12.

Source for timing: https://2026.emnlp.org/calls/main_conference_papers/

This document is the operational TODO board for turning the current submission-freeze candidate into the strongest defensible EMNLP submission. It does not replace final human scientific judgment, final PDF sign-off, author metadata review, conflicts review, reviewer registration, venue-form transfer, or the submit click.

## Current Position

- The paper is submission-close: the final lock gate passes, the PDF builds to 13 pages, the review package builds, and `main` is synchronized to GitHub.
- The paper is not yet oral-ready or best-paper-ready: `docs/emnlp2026_oral_best_paper_quality_audit.md` marks the artifact as a credible submission-freeze candidate, not an oral/best-paper-grade evidence package.
- The canonical paper-facing split is `560` examples with `answer=200`, `ask=80`, `challenge=200`, and `abstain=80`.
- The slice-balanced `600` split is stress evidence only. It must not replace the canonical `560` split in headline claims.
- Current major residual risks: statistical depth, final human PDF sign-off, slice-balance interpretation, and preserving the first-two-page action-selection story.

## Operating Principles

1. Preserve acceptance before chasing oral polish: no new claim may outrun a generated artifact, macro, metric JSON, citation audit, validation queue, or lock-gate result.
2. Keep the benchmark contribution ahead of the intervention contribution.
3. Treat `decision_first` as an exploratory calibration probe unless new cross-model evidence justifies stronger wording.
4. Keep confidence intervals as local uncertainty checks, not stable model-ranking proof.
5. Keep human-only work human-only: automated audits prepare sign-off but never become sign-off.
6. Do not start broad new model runs, large downloads, or GPU sweeps unless they directly address a fatal reviewer objection.

## Calendar Plan

| Window | Goal | Exit Criteria |
| --- | --- | --- |
| 2026-05-06 to 2026-05-08 | Board setup and reviewer-facing risk closure | This TODO board is live, response seeds cover statistics/CI overclaim, final PDF human-review worksheet is opened, and status docs point to both. |
| 2026-05-09 to 2026-05-11 | First-two-page and PDF-scale review | A human-scale PDF review worksheet is filled by a person or explicitly marked blocked; any Codex-only preflight remains labeled as preflight. |
| 2026-05-12 to 2026-05-15 | Results, statistics, and appendix hardening | Results prose, captions, limitation wording, and reviewer-response seeds all agree on canonical-vs-stress scope and CI interpretation. |
| 2026-05-16 to 2026-05-20 | Internal review and submission hardening | Review package, responsible-NLP packet, reproducibility packet, anonymity scan, and obvious reviewer-response materials are synchronized. |
| 2026-05-21 to 2026-05-24 | Freeze and dry run | No non-fatal experiments. Text, figures, tables, references, and review package are frozen after a clean lock gate. |
| 2026-05-25 | Submission day | Human authors complete venue metadata, reviewer registration, conflicts, forms, final PDF inspection, and submit before AOE deadline. |

## Workstream TODOs

### A. Story And First Two Pages

| Status | Task | Artifact |
| --- | --- | --- |
| closed | Keep next-action selection as the paper's central object. | `docs/emnlp2026_first_two_page_oral_readiness_audit.md` |
| closed | Keep Figure 1 as the first-two-page action-before-generation schematic. | `docs/emnlp2026_oral_readability_lock.md` |
| pending | Human-scale reread of pages 1-2 for density, breathlessness, and first-read memorability. | `docs/emnlp2026_final_pdf_human_review_worksheet.md` |
| pending | If a human reread flags density, tighten abstract or page-2 transition without moving Figure 1 later. | `paper/sections/00_abstract.tex`, `paper/sections/01_introduction.tex` |

### B. Evidence And Statistics

| Status | Task | Artifact |
| --- | --- | --- |
| closed | Keep canonical split at `560` paper-facing examples. | `docs/emnlp2026_claim_ledger.md` |
| closed | Treat `600` rows as sensitivity or stress evidence only. | `paper/sections/05_results.tex`, `paper/sections/08_limitations.tex` |
| closed | Add response seed for statistics/CI overclaim. | `docs/emnlp2026_reviewer_response_seed_memo.md` |
| pending | Re-check that every new result sentence added after 2026-05-06 is macro-, metric-, audit-, or lock-backed. | `docs/emnlp2026_numeric_claim_audit.md` |
| pending | Keep delta intervals scoped when discussing full-minus-canonical comparisons. | `experiments/day1/tables/day1_full_split_sensitivity.tex` |

### C. Benchmark Validity

| Status | Task | Artifact |
| --- | --- | --- |
| closed | Action ontology and boundary rules exist. | `docs/action_ontology.md` |
| closed | Human validation is complete for the active queue: `61/61`. | `_assets/human_validation_work_queue.csv` |
| pending | Human final read checks whether `ask`, `challenge`, and `abstain` boundaries are understandable from the paper alone. | `docs/emnlp2026_final_pdf_human_review_worksheet.md` |
| pending | Do not promote additional candidate rows unless a new validation queue and freeze decision exist. | `docs/emnlp2026_submission_readiness_checklist.md` |

### D. Figures And Tables

| Status | Task | Artifact |
| --- | --- | --- |
| closed | Paper-facing figures are present and full-PDF visual audit passes. | `docs/emnlp2026_full_pdf_visual_readiness_audit.md` |
| pending | Human review verifies Figure 2 and dense tables remain readable at actual PDF scale. | `docs/emnlp2026_final_pdf_human_review_worksheet.md` |
| pending | Any caption edit must preserve action-selection interpretation and rerun story/asset tests. | `paper/figures`, `paper/tables` |

### E. Reviewer Response And Rebuttal Prep

| Status | Task | Artifact |
| --- | --- | --- |
| closed | Reviewer triage memo exists. | `docs/emnlp2026_reviewer_triage_revision_memo.md` |
| closed | Response seeds cover benchmark-soup, utility, reasoning, intervention, ask/abstain, and statistics/CI overclaim. | `docs/emnlp2026_reviewer_response_seed_memo.md` |
| pending | After any paper edit, keep response seeds synchronized with exact paper wording. | `docs/emnlp2026_reviewer_response_seed_memo.md` |
| pending | During author response, tailor wording to actual reviews; do not paste seeds mechanically. | future rebuttal draft |

### F. Packaging, Forms, And Final Sign-Off

| Status | Task | Artifact |
| --- | --- | --- |
| closed | One-command final lock gate passes. | `./scripts/run_submission_lock_checks.sh` |
| pending | Human author transfers responsible-NLP and reproducibility answers into the official venue form. | `docs/emnlp2026_venue_form_transfer_packet.md` |
| pending | Human author confirms author list, affiliations, reviewer registration, and conflicts. | official submission system |
| pending | Human author visually inspects final PDF and records decision. | `docs/emnlp2026_final_pdf_human_review_worksheet.md` |
| pending | Human author submits before 2026-05-25 AOE. | official submission system |

## Stop Conditions

Stop and ask for a human decision if:

- a proposed paper claim would make the `600` split the de facto headline benchmark;
- a task requires a new model run, large download, paid API spend, or GPU allocation;
- a human-validation or final-PDF sign-off field would otherwise be filled by automation;
- a claim needs new literature support beyond the current citation coverage audit;
- a layout edit changes first-two-page Figure 1 placement or pushes contributions later;
- the next step would materially change scope from submission hardening to a new study.

## Immediate Next Commands

Run after any paper-facing edit:

```bash
pytest -q tests/test_final_push_todo.py tests/test_reviewer_response_seed_memo.py tests/test_reviewer_triage_revision_memo.py tests/test_paper_claim_scope.py
./scripts/run_submission_lock_checks.sh
```

## Started On 2026-05-06

- Created this final-push TODO dashboard.
- Opened `docs/emnlp2026_final_pdf_human_review_worksheet.md` as the first human-facing final-signoff prep artifact.
- Started the worksheet with a Codex-only PDF text preflight: `paper/main.pdf` is `13` pages, pages 1-2 expose the first-story anchors, and pages 5-7 expose the main-result anchors.
- Started the first paper-facing final-push edit by tightening the abstract around the line that answer quality is incomplete without choosing the right first move.
- Added tests so status docs keep pointing to the current final-push plan rather than stale sprint notes.
