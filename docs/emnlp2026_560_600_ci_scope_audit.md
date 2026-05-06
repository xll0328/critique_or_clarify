# EMNLP 2026 560/600 And CI Scope Audit

Date: 2026-05-06

Status: current final-push audit for canonical-vs-stress split language and confidence-interval scope.

## Audit Question

Can a reviewer misread the paper as replacing the canonical 560-example benchmark with the 600-example stress split, or as using bootstrap intervals to prove stable fine-grained model rankings?

## Result

No current main-paper wording does that. The remaining risk is future drift after Results, Limitations, table, figure, abstract, or reviewer-response edits.

## Checked Surfaces

| Surface | Finding | Status |
| --- | --- | --- |
| Results: bootstrap interval paragraph | Says intervals separate coarse patterns from small rank differences and explicitly does not claim every adjacent model difference is separated. | pass |
| Results: external API paragraph | Describes API rows as uncertainty-qualified point estimates rather than a fine-grained significance ranking. | pass |
| Results: slice-balance sensitivity paragraph | Says the 600-example split is sensitivity evidence rather than a replacement benchmark and that the headline remains the canonical 560-example split. | pass |
| Table `day1_full_split_sensitivity` caption | Now labels the table as stress sensitivity from canonical 560 to slice-balanced 600, not a replacement headline benchmark. | pass |
| Figure 6 caption | States API baseline comparison is on the 560-example canonical split. | pass |
| Limitations | States the 600-example variant is a stress split, not the canonical benchmark, and that CIs are local uncertainty checks rather than proof of stable ordering. | pass |

## Locked Wording

These fragments should survive future edits:

- `600-example split as sensitivity evidence rather than as a replacement benchmark`
- `the headline remains the canonical 560-example split`
- `not a replacement headline benchmark`
- `uncertainty-qualified point estimates rather than as a fine-grained significance ranking`
- `local uncertainty checks over the current split samples`
- `not that every adjacent model difference is statistically separated`

## Next Trigger

Re-run this audit after any edit to:

- `paper/sections/05_results.tex`
- `paper/sections/08_limitations.tex`
- `scripts/export_full_split_sensitivity_table.py`
- `paper/tables/day1_full_split_sensitivity.tex`
- `paper/figures/figure6_api_baseline_comparison.pdf`
- reviewer-response or gap-closure docs that quote `560`, `600`, CI, bootstrap, ranking, or full-minus-canonical deltas.
