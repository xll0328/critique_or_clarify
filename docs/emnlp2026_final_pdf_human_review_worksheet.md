# EMNLP 2026 Final PDF Human Review Worksheet

Date opened: 2026-05-06

Status: opened for final human review. This worksheet is not completed human sign-off.

Purpose: prepare the final human PDF read required before external submission. Automated audits can populate context, but a person must complete the reviewer, date, decision, and notes fields.

## Inputs

- Current manuscript PDF: `paper/main.pdf`
- Full-PDF automated visual audit: `docs/emnlp2026_full_pdf_visual_readiness_audit.md`
- First-two-page oral-readiness audit: `docs/emnlp2026_first_two_page_oral_readiness_audit.md`
- Oral readability lock: `docs/emnlp2026_oral_readability_lock.md`
- Final local clarity pass: `docs/emnlp2026_final_local_clarity_pass.md`
- Final-push TODO dashboard: `docs/emnlp2026_final_push_todo.md`

## Human Completion Fields

| Field | Value |
| --- | --- |
| Human reviewer name or initials |  |
| Review date |  |
| PDF version or commit hash |  |
| Decision |  |
| Required fixes before submission |  |
| Optional fixes if time permits |  |

Allowed decisions:

- `approve_for_submission`
- `approve_after_minor_fixes`
- `block_until_fixed`

Do not mark this worksheet as complete unless a human has inspected the compiled PDF at actual submission scale.

## Review Checklist

| Status | Item | Notes |
| --- | --- | --- |
| pending | Page 1 makes the wrong-first-move problem memorable without relying on appendix material. |  |
| pending | Page 2 preserves Figure 1 and the contribution list before Related Work becomes too dense. |  |
| pending | The abstract is dense but still readable in one pass. |  |
| pending | Figure 1 is readable at paper scale and still communicates action-before-generation. |  |
| pending | Figure 2 and other dense visual elements are readable without zooming beyond normal review scale. |  |
| pending | Main tables are not visually overwhelming and captions explain the action-selection interpretation. |  |
| pending | Results do not over-read bootstrap intervals or API point estimates as fine-grained rankings. |  |
| pending | The canonical `560` split and the `600` stress split are not confused. |  |
| pending | `decision_first` remains an exploratory calibration probe, not a deployed controller. |  |
| pending | Ask/challenge/abstain boundary cases are understandable from paper text alone. |  |
| pending | No automated audit is described as final human sign-off. |  |
| pending | No local paths, internal identities, or non-anonymous support files appear in the submission package. |  |
| pending | Responsible-NLP and reproducibility answers are ready for manual transfer into the venue form. |  |

## Codex Preflight

Date: 2026-05-06

Status: automated preflight started. This is not human approval.

Observed from `paper/main.pdf` using PDF text extraction:

- PDF length: `13` pages.
- Pages 1-2 contain the first-story anchors: `next-action`, `wrong first move`, `answer`, `ask`, `challenge`, `abstain`, `Figure 1`, and `defective`.
- Pages 5-7 contain the main-result anchors: `DeepSeek`, `decision_first`, `confidence`, `bootstrap`, `over-answer`, `utility`, `action accuracy`, `Figure 2`, and `Table`.
- Commit used for this preflight: `cbbf88a`.

Open human task: inspect the compiled PDF visually at actual review scale and fill the Human Completion Fields above.

## Automation Boundary

Codex may help by running tests, building the PDF, scanning for paths, checking references, and preparing this worksheet. Codex must not fill the human reviewer, decision, or final approval fields unless a human explicitly provides the completed values.
