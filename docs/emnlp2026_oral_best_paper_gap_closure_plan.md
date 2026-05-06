# EMNLP 2026 Oral / Best Paper Gap Closure Plan

Date: 2026-05-06

Status: active gap-closure plan launched after the final-push dashboard and abstract first-move framing updates.

Official timing anchor: EMNLP 2026 long and short papers use the ARR submission deadline of 2026-05-25, 11:59PM UTC-12. Reviewer registration for all authors is due 2026-05-27. Source checked on 2026-05-06: `https://2026.emnlp.org/calls/main_conference_papers/`.

## Hard Answer

We are close to a defensible EMNLP submission, but not close enough to honestly call the current artifact oral-ready or best-paper-ready.

Operational distance:

| Target | Current Distance | Why |
| --- | --- | --- |
| Clean EMNLP submission | close | The lock gate passes, the PDF builds to 13 pages, the review package builds, and the canonical evidence is human-validated. Final human PDF/form/sign-off work remains. |
| Oral-level paper | medium-far | The first-move framing is strong and the evidence package is credible, but statistical depth, final PDF readability, and canonical-vs-stress claim discipline still need hardening. |
| Best-paper-level paper | far | Best-paper requires more than being correct: the paper must feel field-shaping, difficult to dismiss as benchmark mixture, visually memorable, and statistically over-prepared. We do not have that guarantee. |

Current readiness estimate from project audits: `3.1 / 5` overall, below the practical oral threshold. Treat this as an internal operational score, not a prediction of reviewer outcome.

## What Is Already Strong

- The central object is sharp: next-action selection under defective inputs.
- The abstract now leads with the first-move frame: answer quality is incomplete if the assistant chooses the wrong action before generating.
- Canonical paper-facing split: `560` examples with `answer=200`, `ask=80`, `challenge=200`, and `abstain=80`.
- Human validation is complete for the active paper-facing queue: `61/61`.
- Current main model rows: `10`; current paper-facing figures: `6`; bibliography entries: `35`.
- The slice-balanced `600` split has frontier/high/medium/low API stress rows, but remains stress evidence only.
- `./scripts/run_submission_lock_checks.sh` passes for the current freeze.

## Remaining Oral / Best Paper Gaps

| Gap | Severity | Closure Standard | Owner Surface |
| --- | --- | --- | --- |
| Final human PDF read is not complete | critical for submission | A human fills `docs/emnlp2026_final_pdf_human_review_worksheet.md`; Codex preflight remains labeled preflight. | PDF worksheet, official submission system |
| Statistical depth is not oral-grade | major for oral | Results, limitations, response seeds, and numeric audit all describe CIs as local uncertainty checks and avoid fine-grained model ranking. | Results, limitations, numeric claim audit, response seeds |
| Best-paper narrative is not yet field-shaping enough | major for best paper | First two pages make reviewers remember the wrong-first-move problem before they see dense tables. | Abstract, Introduction, Figure 1, oral readability lock |
| 600-vs-560 split could be misread | major for reviewer trust | Every headline claim remains on canonical `560`; `600` stays sensitivity/stress evidence. | Results, limitations, claim ledger |
| Intervention could overtake benchmark contribution | major for reviewer trust | `decision_first` stays an exploratory calibration probe; negative variants remain visible. | Abstract, Introduction, Intervention, response seeds |
| EMNLP integrity risk | major for desk-risk perception | Claims, citations, and AI-assisted artifacts remain traceable; no hallucinated citation or thin-sliced contribution language. | Citation audit, claim ledger, final package |
| Final forms and metadata are human-only | critical for submission | Authors complete author list, affiliations, conflicts, reviewer registration, responsible-NLP transfer, and submit click. | Official venue system |

## Detailed TODO Board

### Track A: Acceptance-Safe Freeze

| Status | Task | Exit Criteria |
| --- | --- | --- |
| active | Keep `main` synchronized to GitHub after each coherent sprint chunk. | `git status -sb` is clean and `main...origin/main` is aligned. |
| active | Keep the final lock gate green after any paper-facing edit. | `./scripts/run_submission_lock_checks.sh` returns `submission_lock_checks_ok`. |
| pending-human | Complete final PDF human review. | Human reviewer, decision, date, and notes are filled by a person, not Codex. |
| pending-human | Complete author metadata, conflicts, reviewer registration, and venue-form transfer. | Official submission system is filled by human authors. |

### Track B: Oral Evidence Hardening

| Status | Task | Exit Criteria |
| --- | --- | --- |
| active | Re-check every new result sentence added after 2026-05-06. | Each numeric/result claim maps to macro, metric JSON, audit, or lock-gate artifact. |
| active | Keep confidence narration coarse. | No sentence says CIs prove stable model ordering or adjacent model rank. |
| active | Keep `600` as stress evidence. | Headline benchmark claims remain on canonical `560`. |
| pending | Re-read Figure 2 and dense tables at PDF scale. | Human worksheet records readability or blocks with exact page/table issue. |

### Track C: Best-Paper Narrative Hardening

| Status | Task | Exit Criteria |
| --- | --- | --- |
| active | Preserve the first-move hook in the abstract and first two pages. | Page 1 retains the answer-quality-incomplete / right-first-move frame. |
| active | Keep Figure 1 on the first-two-page path. | No layout edit pushes Figure 1 later without an explicit stop decision. |
| pending | Run a human-scale first-two-page reread for density and memorability. | Human worksheet records whether the first read is memorable or too dense. |
| pending | Tighten page-2 transition only if human reread flags breathlessness. | Any edit preserves Figure 1 placement and reruns story tests. |

### Track D: Reviewer Attack Preemption

| Status | Task | Exit Criteria |
| --- | --- | --- |
| active | Keep response seeds synchronized with exact paper wording. | `docs/emnlp2026_reviewer_response_seed_memo.md` includes current first-move framing. |
| active | Keep benchmark-soup defense explicit. | Rebuttal prep says one action decision, not four unrelated tasks. |
| active | Keep utility humble. | Utility is described as asymmetric harm-ordering diagnostic, not real user cost. |
| active | Keep reasoning-model result scoped. | Claims are limited to completed Day-1 local checkpoints and prompt/parsing protocol. |
| pending | Add final author-response skeleton after actual reviews arrive. | Future rebuttal text acknowledges real reviewer wording before pointing to evidence. |

### Track E: Submission Operations

| Status | Task | Exit Criteria |
| --- | --- | --- |
| active | Maintain anonymous review package hygiene. | Review package builds and scan passes. |
| pending-human | Transfer responsible-NLP and reproducibility answers. | Official form matches `docs/emnlp2026_venue_form_transfer_packet.md`. |
| pending-human | Register all authors as reviewers by 2026-05-27. | All authors confirm completion externally. |
| pending-human | Submit before 2026-05-25 AOE. | Human author completes final submit click. |

## Date-Bounded Plan

| Window | Primary Goal | Must Finish |
| --- | --- | --- |
| 2026-05-06 to 2026-05-08 | Gap plan launch and reviewer-risk closure | This plan is wired into README/checklist/tests; response seeds and final-push TODO stay synchronized. |
| 2026-05-09 to 2026-05-11 | Human-scale PDF and first-two-page read | Worksheet is completed by a human or explicitly marked blocked. |
| 2026-05-12 to 2026-05-15 | Results/statistics hardening | Numeric claim audit, Results, Limitations, and response seeds agree on CI and 560-vs-600 scope. |
| 2026-05-16 to 2026-05-20 | Internal review package hardening | Review package, form transfer packet, anonymity scan, and reviewer response prep are synchronized. |
| 2026-05-21 to 2026-05-24 | Freeze and dry run | No non-fatal experiments; clean lock gate; human PDF/form checks queued or complete. |
| 2026-05-25 | ARR submission day | Human authors submit before 11:59PM UTC-12. |

## Started On 2026-05-06

- Launched this gap-closure plan to answer the direct distance question: submission-close, oral medium-far, best-paper far.
- Started the first implementation task: wire this plan into project status docs and tests so the sprint has a durable control surface.

## Stop Conditions

Stop and ask for a human decision if:

- a task would promote the `600` stress split into the headline benchmark;
- a task requires a new model run, paid API spend, large download, GPU allocation, or broad scope change;
- an automated audit would fill or imply final human sign-off;
- a claim requires new literature support not covered by the citation audit;
- a layout edit moves Figure 1 out of the first-two-page story;
- official venue metadata, conflicts, reviewer registration, or submit click is needed.
