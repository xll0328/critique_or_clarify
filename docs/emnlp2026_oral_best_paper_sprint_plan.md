# EMNLP 2026 Oral / Best Paper Sprint Plan

Date: 2026-04-27

Target venue: EMNLP 2026 main conference, long paper.

Official timing anchor:

- ARR submission deadline for EMNLP 2026 long and short papers: 2026-05-25, 11:59PM UTC-12.
- Reviewer registration deadline for all authors: 2026-05-27.
- Author response and author-reviewer discussion: 2026-07-07 to 2026-07-13.
- Meta-review release: 2026-07-30.
- EMNLP commitment deadline: 2026-08-02.
- Notification: 2026-08-20.
- Camera-ready: 2026-09-20.
- Main conference: 2026-10-24 to 2026-10-29.

Source: https://2026.emnlp.org/calls/main_conference_papers/

## North Star

This project is aiming for the version that can plausibly receive oral-level enthusiasm:

> Assistants should not only answer well; they must first choose whether the user input should be answered, clarified, challenged, or set aside because the premise or evidence is defective.

The paper should not read as a mixed benchmark collection. It should read as a clean new evaluation setting: action selection under defective inputs.

## Oral / Best Paper Bar

The paper only has a serious oral/best-paper path if it satisfies all five standards below.

1. New problem framing:
   The paper reframes a broad class of LLM failures as a unified next-action decision problem, not as isolated hallucination, ambiguity, or retrieval-conflict cases.

2. Sharp empirical surprise:
   Strong open models should remain far from ceiling, and reasoning-style models should show a systematic failure mode rather than monotonically improving the benchmark.

3. Benchmark discipline:
   The action ontology, slice construction, utility metric, and human validation must be tight enough that reviewers cannot dismiss the task as subjective.

4. Intervention:
   The paper needs a simple, believable calibration lever, but it must be scoped honestly if it is not yet a complete method.

5. Paper execution:
   The Introduction, Figure 1, main table, failure analysis, and limitations must make the contribution obvious within the first two pages.

## Current Lock State

Submission-freeze candidate, not final external submission.

Closed gates:

- Action ontology is documented in `docs/action_ontology.md`.
- Reporting rules are documented in `docs/reporting_template.md`.
- Human validation for the active queue is complete: `human_validation_queue_ok completed=61/61`.
- DeepSeek-R1-Distill-Qwen-7B metrics are complete: dev action accuracy `0.3667`, dev utility `-0.4313`, quick+stale action accuracy `0.4500`, quick+stale utility `-0.4750`.
- Scale/reasoning comparisons, quick+stale comparisons, CI tables, LaTeX snippets, stale-pool pilot, and failure audits are generated.
- The paper draft compiles in ACL/ARR style at `paper/main.tex`; current output is `paper/main.pdf`.
- Related Work is present in `paper/sections/02_related_work.tex`, and citation-key consistency is covered by the local test suite.
- The anonymized review package is rebuilt at `_review_package/critique_or_clarify_emnlp2026_review.zip`.
- Oral readability is locked for the current internal freeze at `docs/emnlp2026_oral_readability_lock.md`.
- Final local clarity is locked for the current internal freeze at `docs/emnlp2026_final_local_clarity_pass.md`.
- Benchmark expansion coverage is represented in `experiments/day1/benchmark_expansion_coverage_audit.md` and `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md` (`560` paper-facing examples; action-balanced, target-exceeded).
- Ask/abstain candidates are generated at `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`, with manifest `data/candidates/emnlp2026_ask_abstain_seed_candidates_manifest.json`, coverage audit `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md`, validation queue `_assets/emnlp2026_expansion_candidate_validation_queue.csv`, and promotion tool `scripts/promote_validated_expansion_candidates.py`.
- Ask/abstain candidates are now promoted and paper-facing (`data/processed/emnlp2026_expanded_dev.jsonl` with manifest `data/processed/emnlp2026_expanded_dev_manifest.json`).
- Oral/best-paper quality audit is generated at `docs/emnlp2026_oral_best_paper_quality_audit.md` and currently marks the artifact `not oral-ready` because statistical depth and final human sign-off remain below target, even though coverage, action balance, API/frontier stress rows, automated full-PDF visual readiness, and the 35-entry bibliography threshold are now met.
- Slice-balanced 600 stress evidence now includes frontier/high/medium/low API rows: `gpt-5-chat-latest`, `qwen-plus-latest`, `gpt-4.1-mini`, and `qwen-turbo`; the frontier `gpt-5-chat-latest` row is stored at `outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_full_answer_topup_metrics.json` and appears in `experiments/day1/tables/day1_full_split_sensitivity.tex`.
- Full execution plan for the oral/best-paper sprint is locked at `docs/emnlp2026_oral_best_paper_sprint_execution_plan.md`.
- Final artifact lock passes `./scripts/run_submission_lock_checks.sh`, including asset sync, scale/reasoning checks, complete human validation, `129 passed`, PDF build, LaTeX log scan, anonymous review-package build, and package hygiene scan.

### Readiness Diagnosis (hard view)

Answer to your direct question: **not Oral-ready, and not Best-Paper-ready** in the current state.

- Current position against top-level venue criteria:
  - Novel problem framing: **partially met** (core framing exists, but needs sharper paper-wide anchoring)
  - Experimental strength: **not yet at oral level** (model frontier, confidence intervals, and negative controls are still thin relative to oral-level expectations)
  - Reproducibility / benchmark discipline: **good** (strong human-validated baseline, but not yet broadened)
  - Visual communication: **insufficient for oral review** (results focus is there, but lacks intuitive/diagnostic views)
  - Citation coverage: **below oral expectation** in manuscript body (enough in raw count but uneven claim support)
  - Writing clarity and first-two-page narrative: **currently acceptable but fragile** (locked, but sensitive to any new evidence insertion)

Concrete score (0-5):

- Framing clarity: 3.8
- Claim defensibility: 4.0 (within locked evidence)
- Experimental breadth: 2.8
- Visual quality: 2.9
- Methodological depth: 3.2
- Citation quality (claim-to-quote alignment): 2.9

Estimated overall readiness: **3.1 / 5**, below the practical oral threshold.

Current claim posture:

- The benchmark/evaluation contribution is the lead claim.
- The 7B reasoning result supports a scoped reasoning-risk story, including weak action calibration and format-following issues.
- The decision-first intervention is promising and scoped to quick+stale behavior; do not present it as a broad assistant helpfulness result.
- No paper-facing claim should depend on stale local notes, unverified ad hoc numbers, or internal-only work packets.

Remaining review work:

- Human PDF-level read for logic, figure readability, and anonymous-submission polish.
- Final check that the first two pages make the action-selection problem legible without the appendix.
- Final check that intervention language stays scoped and does not overtake the benchmark contribution.
- External submission metadata, author list, reviewer registration, and form-level responsible-NLP answers.

## Sprint Principle

Every task must move at least one of these gates:

1. Evidence: verify a result used in a paper claim.
2. Story: make the contribution easier for reviewers to understand.
3. Robustness: eliminate a reviewer objection before submission.
4. Writing: convert validated evidence into manuscript-ready text, tables, or figures.
5. Packaging: preserve the clean review package and one-command lock gate.

If a task does not move one of those gates, it is not part of the EMNLP sprint.

## Immediate 72-Hour Top-Level Push (2026-04-28 -> 2026-05-01)

Goal: move from “not oral-ready” to “oral-risks audited and reduced.”

Phase 1: Narrative integrity (today, 4-6 hours)

1. Lock the core story around 4 actions, not the intervention.
2. Rewrite the first 2 pages to make: problem gap -> action ontology -> empirical surprise -> why this is a new setting.
3. Add a one-paragraph "why this is not mixed-benchmark soup" statement in Introduction.
4. Add/update 3 explicit claim-to-evidence anchors in the manuscript for any claim about utility/calibration/format behavior.

Phase 2: Visualization hardening (today/tomorrow)

1. Add a compact 4-view figure set before any new tables:
   - Panel A: action accuracy by split and model family.
   - Panel B: utility vs decision coverage (answer/ask/challenge/abstain) with confidence intervals.
   - Panel C: failure-type distribution (clarity taxonomy) per model family.
   - Panel D: cost-utility Pareto for local API models and paid counterparts.
2. Reformat at least one existing dense table into a ratio/stacked view to improve digestibility.
3. Keep Figure 1 readable at 1-column width on first-pass PDF.

Phase 3: Evidence densification without scope explosion (next 2-3 days)

1. Prioritize API quick-baseline confirmation and the expanded-dev model matrix because these directly target the reviewer “coverage” objections.
   - Command (now ready): run Day-1/quick+stale model pipelines on `data/processed/emnlp2026_expanded_dev.jsonl` and regenerate tables/figures from the same artifacts.
2. Run only experiments that close a specific reviewer objection:
   - action coverage for non-answer actions with external API models,
   - 1-2 robustness slices for known weak spots,
   - utility stability under prompt-constraint perturbations.
3. Add at least one negative control slice where the method does not help, to demonstrate honesty.

Phase 4: Citation discipline (ongoing, parallel to above)

1. Add 8–12 high-signal citations where claims are currently unsupported in body text (intro/methods/results/limitations).
2. Ensure every major claim is backed by either:
   - generated metrics,
   - audit artifact,
   - or directly relevant cited literature.
3. Remove any language implying this is the first/only method in the space unless supported by a direct comparative map.

Definition of exit for this phase:

- No obvious “major oral rejector” objection remains in the first two pages.
- The paper-facing artifact includes at least one visualization that explains model behavior across all 4 action types.
- External API baseline section includes quantified comparison and no ungrounded method promises.
- Oral best-paper claim remains explicitly conditional: "new benchmark framing + calibrated intervention evidence."

## Timeline

There are 28 calendar days from 2026-04-27 to the ARR submission deadline on 2026-05-25.

### Sprint 0: 2026-04-26 to 2026-04-27

Status: completed.

Locked deliverables:

- Oral/best-paper target and sprint plan.
- Paper claim ledger.
- Paper skeleton and compileable manuscript.
- Human validation marked complete.
- DeepSeek-R1-Distill-Qwen-7B pipeline completed.
- Numeric and claim-scope audits current for the submission freeze.
- Final lock gate passing with `submission_lock_checks_ok`.

### Sprint 1: 2026-04-28 to 2026-05-03

Goal: convert the locked artifact into a reviewer-readable paper, not a pile of evidence.

Required deliverables:

- PDF-level read of pages 1-2: problem, task, surprise, and contribution must be clear before the appendix.
- Figure/table readability pass, especially Figure 2 and the main comparison tables.
- One final qualitative-example pass: examples must support the action-selection story, not just show model mistakes.
- Results prose pass: 7B reasoning-risk language must be explicit, scoped, and tied to generated metrics.
- Intervention prose pass: decision-first is a calibration lever, not the central method claim.
- Final local clarity pass: page-neutral wide-table placement, scoped claims, and human-only final checks are guarded by `docs/emnlp2026_final_local_clarity_pass.md`.
- Run `./scripts/run_submission_lock_checks.sh` after edits.

Decision gate:

- If the paper still reads like "benchmark soup" after pages 1-2, rewrite the Introduction and Figure 1 before adding new experiments.
- If the intervention language sounds stronger than the evidence, demote it in the framing and keep the benchmark as the lead.

### Sprint 2: 2026-05-04 to 2026-05-09

Goal: harden against the most likely reviewer objections.

Required deliverables:

- Reviewer-1 pass: novelty and positioning against clarification, abstention, false-premise, temporal robustness, and retrieval-conflict work.
- Reviewer-2 pass: benchmark validity, label subjectivity, and boundary cases.
- Reviewer-3 pass: experimental design, metrics, confidence intervals, and model coverage.
- Devil's Advocate pass: "why is this a unified scientific setting rather than a mixed benchmark?"
- A revision memo with must-fix, should-fix, and appendix-only buckets.

Experiment policy:

- Do not start broad new experiments by default.
- Only run a new experiment if it directly answers a fatal reviewer concern.
- Any new result must enter the claim ledger and pass the final lock gate before it can appear in the paper.

### Sprint 3: 2026-05-10 to 2026-05-15

Goal: produce the submission candidate draft.

Required deliverables:

- Complete manuscript prose pass.
- Verified citations and bibliography fit.
- Final task/benchmark section with boundary rules.
- Final results section with macro-backed numbers only.
- Final limitations and responsible-NLP text.
- Paper PDF checked at actual page scale, not only source-level.

Draft standard:

- The first two pages must make the problem, task, empirical surprise, and contribution legible without reading the appendix.
- Every numerical claim must point to a generated artifact, macro file, metric JSON, or lock-gate check.
- Every citation must be relevant, present in the bibliography, and placed where it supports the claim.

### Sprint 4: 2026-05-16 to 2026-05-20

Goal: internal review and submission hardening.

Required deliverables:

- Fresh review pass from the compiled PDF.
- Anonymous review-package inspection.
- Responsible-NLP and reproducibility checklist reconciliation.
- Final response plan for obvious reviewer attacks.
- Full lock gate after each paper-facing change.

Decision gate:

- If the paper cannot answer "why is this a new scientific setting?" in one paragraph, rewrite the Introduction before touching anything else.

### Sprint 5: 2026-05-21 to 2026-05-24

Goal: submission lock.

Required deliverables:

- Final manuscript in ACL/ARR format.
- Final tables and figures regenerated from current artifacts.
- Final integrity report.
- Anonymous supplemental or review package, if submitted.
- Reproducibility checklist.
- Responsible NLP checklist.
- Submission dry run.

Submission rule:

- Freeze experiments by 2026-05-22 unless a result directly fixes a fatal reviewer concern.
- Freeze text by 2026-05-24.
- Submit before 2026-05-25 AOE.

## Workstreams

### A. Evidence And Experiments

Owner: Codex execution, human scientific judgment.

Immediate tasks:

- Keep existing results locked through `./scripts/run_submission_lock_checks.sh`.
- Use `python scripts/audit_benchmark_expansion_coverage.py` as the first gate for benchmark expansion.
- Inspect 7B failures only to support qualitative explanation, not to invent new broad claims.
- Keep all paper-facing numbers macro-backed or generated from metric JSON.

Do not do by default:

- Do not launch another large model run unless it fixes a fatal review risk.
- Do not promote the intervention beyond the quick+stale evidence.

### B. Benchmark Validity

Owner: human final judgment, Codex artifacts.

Immediate state:

- Active human validation completed for 61 rows.
- Action ontology, boundary rules, and adjudication protocol exist.
- Reviewer-facing boundary-case material is drafted.
- Current unique audited coverage is `560` paper-facing examples with all four actions represented (`answer=200`, `ask=80`, `challenge=200`, `abstain=80`).
- `ask` / `abstain` candidate intake is complete and promoted; remaining slice-level expansion work targets `answerable_control` and `conflicting_evidence` balance.

Next tasks:

- Ensure the Data Quality / Human Validation prose in the manuscript matches the completed queue and does not expose internal packets.
- Keep the `ask` vs `challenge` vs `abstain` boundaries visible in the paper.
- Validate additional slices only when opened; broaden the model matrix only after robustness runs close the current oral-level gaps.
- Use the human-validation result as evidence of agreement and protocol discipline, not as proof that the ontology is uniquely correct.

### C. Paper Story

Owner: Codex drafts, human approval.

Core story:

1. NLP systems are evaluated as answer generators.
2. Real assistants first need a repair action when the input is defective.
3. We formalize four actions: answer, ask, challenge, abstain.
4. Current models show slice-specific calibration failures.
5. Reasoning does not automatically solve this and may rationalize bad premises or fail the format.
6. A lightweight decision-first controller can improve utility on quick+stale if it preserves answerability.

Immediate tasks:

- Preserve the first-two-page action-selection arc.
- Keep the benchmark contribution ahead of the intervention contribution.
- Make limitations precise rather than defensive.

### D. Figures And Tables

Minimum paper-facing set:

- Figure 1: task schematic with four actions and three defect families.
- Figure 2: over-answer rate by slice and model family.
- Table 1: benchmark slices, sources, sizes, gold action distribution.
- Table 2: main model comparison with utility, action accuracy, over-answer rate, answerability.
- Table 3: intervention comparison.
- Appendix: confusion matrices, bootstrap CIs, validation packets summary if appropriate and anonymous.

Immediate tasks:

- Check all figure text at final PDF scale.
- Ensure table captions state the action-selection interpretation, not just metric names.
- Avoid duplicating numbers in prose if a macro or table already carries them.

### E. Integrity And Submission

Owner: Codex checks, human final sign-off.

Required command:

```bash
./scripts/run_submission_lock_checks.sh
```

This gate syncs paper assets, checks scale/reasoning artifacts, requires complete human validation, runs the full test suite, builds the PDF, scans LaTeX logs, builds the anonymous review package, and scans the package for aux/log files or internal paths.

## Risk Register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Reviewers see benchmark soup | High | Lead with formal action-selection problem and ontology; make slices instances of one decision problem. |
| Labels look subjective | High | Use human validation, boundary rules, adjudication protocol, and examples. |
| Intervention is overclaimed | High | Keep decision-first as promising and scoped; lead with the benchmark/evaluation contribution. |
| Evidence bundle still lacks oral-level depth | High | Follow `docs/emnlp2026_oral_best_paper_sprint_execution_plan.md`; strengthen frontier model evidence, confidence intervals, and action-boundary diagnostics rather than size-only expansion. |
| Figure or table is not legible at PDF scale | Medium | Do a final compiled-PDF read and revise captions, sizing, or appendix placement. |
| Citation or positioning issue | High | Verify citation relevance, not only BibTeX key presence. |
| Anonymous package leaks internal paths | High | Use the final lock gate package hygiene scan after every packaging change. |

## Best-Paper Stretch Goals

These are not required for a strong submission, but they are the path from solid paper to memorable paper.

1. A crisp theorem-like task definition:
   "Given user input and optional evidence, choose the next assistant action maximizing expected user utility."

2. A memorable failure example:
   One example where a reasoning model gives a fluent rationale for an outdated or false premise.

3. A simple intervention with a clean mechanism:
   "Decide the action first, then generate."

4. A figure that reviewers can explain from memory:
   Four actions, three defect types, and the over-answer failure mode.

5. A reviewer-proof limitations section:
   Narrow, honest, and clear about text-only scope and dataset construction.

## Immediate Next Commands

Run the final lock gate after any paper-facing edit:

```bash
python scripts/audit_benchmark_expansion_coverage.py
./scripts/run_submission_lock_checks.sh
```

Run the sprint-plan regression check after updating project plans:

```bash
pytest -q tests/test_oral_best_paper_sprint_plan.py
```
