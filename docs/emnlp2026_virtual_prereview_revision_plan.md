# EMNLP 2026 Virtual Prereview Revision Plan

Date: 2026-05-06

Status: active major-revision control board derived from the virtual prereview. This is a planning and execution artifact, not a human reviewer report.

## Current Read

The virtual prereview is not a desk-reject signal. It is a borderline-findings signal: the paper is structurally complete and on-topic, but reviewers may reject if they decide the benchmark is too preliminary, the ontology is under-validated, or the parsing protocol confounds decision quality.

The highest-leverage move is not broad polish. It is to close validity objections in a defensible order while keeping claims narrower than the current evidence.

## Priority Order

1. Stabilize paper presentation and internal-language leakage.
2. Downgrade over-broad benchmark and practical-relevance claims.
3. Add dataset-construction transparency from existing scripts and manifests.
4. Separate action-selection behavior from JSON/protocol adherence as far as existing artifacts allow.
5. Prepare human-only ontology reliability material without calling automation human agreement.
6. Add utility-weight sensitivity analysis from saved predictions.
7. Verify new related work before changing the bibliography.
8. Add API slice/confusion breakdown if it fits without layout damage.
9. Refresh response seeds, claim ledgers, and lock gates after each paper-facing edit.

## Must-Fix Items

| ID | Prereview Risk | Concrete Tasks | Artifact Targets | Stop Condition |
| --- | --- | --- | --- | --- |
| M1 | Benchmark reads preliminary or internally named. | Replace main-paper phrases such as "paper-facing Day-1 split" with reader-facing split names; call the resource an initial benchmark unless evidence is expanded. | `paper/sections/00_abstract.tex`, `paper/sections/01_introduction.tex`, `paper/sections/03_benchmark.tex`, `paper/sections/08_limitations.tex` | Stop if a stronger "final benchmark" claim is needed. |
| M2 | Dataset construction is underdescribed. | Add a compact construction paragraph explaining source normalization, template/source-conditioned synthetic candidates, human validation before promotion, duplicate-ID checks, and manifest-backed split accounting. | `paper/sections/03_benchmark.tex`, `docs/emnlp2026_reviewer_response_seed_memo.md` | Stop if the paper would imply all synthetic rows received independent IAA. |
| M3 | Ontology reliability is not IAA. | Keep current validation wording narrow; create a human-only boundary reliability packet for `ask`/`challenge`/`abstain` disputes. | `docs/action_ontology.md`, future reliability packet, final PDF worksheet | Stop if automation would fill human labels or agreement. |
| M4 | Parsing confounds model comparison. | Run an artifact-level parse sensitivity audit using saved raw outputs: strict JSON, current deterministic fallback, and relaxed explicit-action extraction where feasible. Report as protocol-sensitivity evidence, not a new headline table unless robust. | `experiments/day1/day1_parse_sensitivity_audit.md`, `scripts/audit_parse_sensitivity.py` | Closed for the current local matrix; re-run after any parsing or saved-output change. |
| M5 | Utility weights look ad hoc. | Recompute utility under conservative alternate weight schemes and test whether headline qualitative claims survive without depending on a single score. | `experiments/day1/day1_utility_weight_sensitivity_audit.md`, `scripts/audit_utility_weight_sensitivity.py` | Closed for the current local matrix; re-run after any metric, prediction, or utility-scheme change. |
| M6 | Figure/caption instability hurts trust. | Remove typo risk (`ISON`), make split names reader-facing, verify figure references/labels from source, and rerun PDF visual audit. | `paper/tables`, `paper/sections/05_results.tex`, tests | Stop if layout changes push the PDF over page budget. |
| M7 | Related work may be incomplete or hallucinated. | Verify each suggested new citation through literature tools before adding it; add only real, relevant, citable work. | `docs/emnlp2026_virtual_prereview_literature_triage.md`, `paper/references.bib`, `paper/sections/02_related_work.tex` | Stop if a suggested paper cannot be verified. |
| M8 | API baselines feel under-integrated. | Export slice-level API summaries and confusion/action-mix notes from existing metric JSON; decide whether to add a short prose sentence or appendix table. | `outputs/day1/*expanded_dev_with_answer_topup_metrics.json`, `paper/sections/05_results.tex` | Stop if the main paper cannot absorb the table without crowding. |
| M9 | Responsible-use discussion is too generic. | Strengthen over-challenge/over-abstain user impact language, especially non-native, underspecified, or low-confidence users. | `paper/sections/08_limitations.tex`, `docs/emnlp2026_responsible_nlp_checklist.md` | Stop if claims drift into deployment guidance not evaluated here. |

## Experiment Queue

| ID | Experiment | Minimal Command Shape | Success Criterion | Paper Use |
| --- | --- | --- | --- | --- |
| E1 | Parse sensitivity audit | `python scripts/audit_parse_sensitivity.py` | Completed for the current local matrix; low-adherence runs remain protocol-sensitive. | Limitation and response seed. |
| E2 | Utility weight sensitivity | `python scripts/audit_utility_weight_sensitivity.py` | Completed for the current local matrix; the best instruct row remains above the best reasoning row under tested schemes. | Limitation and response seed. |
| E3 | API slice breakdown | `python scripts/export_api_slice_breakdown.py ...` | Shows frontier APIs still have identifiable boundary-slice errors. | One Results paragraph or compact table. |
| E4 | Human boundary packet | `python scripts/build_boundary_reliability_packet.py ...` | Produces a packet for human adjudication without filling labels. | Submission or rebuttal support only after humans complete it. |
| E5 | Figure/source stability audit | `python scripts/audit_full_pdf_visual_readiness.py` plus source tests | No duplicated labels, no missing captions, no `ISON`. | Trust and presentation cleanup. |

No automated artifact should be described as a human agreement study. If we add agreement evidence, humans must supply the labels and adjudication notes first.
Stop if raw outputs are missing for any row needed by a parsing, utility, or response-seed claim.

## Related-Work Triage

Initial literature-tool check found verified candidates for:

- `AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions` (`10.48550/arxiv.2506.09038`).
- `Judge Before Answer: Can MLLM Discern the False Premise in Question?` (`10.48550/arxiv.2510.10965`).
- `Premise Order Matters in Reasoning with Large Language Models` (`10.48550/arxiv.2402.08939`).
- `Metacognitive Prompting Improves Understanding in Large Language Models` (`10.48550/arxiv.2308.05342`), noting that the prereview title/year were not exact.

Suggested items not yet verified should not be added to `paper/references.bib` until a source is found and the paper is read enough to support the local claim.

## First Execution Chunk

Started immediately:

- Main-paper claim downgrade and internal-language cleanup.
- Dataset construction transparency paragraph.
- Table caption split-name cleanup.
- Tests that lock the revised wording and prevent `ISON`/stale internal split names in the main table caption.
- Parse-sensitivity audit from saved raw outputs.
- Utility-weight sensitivity audit from saved predictions.
