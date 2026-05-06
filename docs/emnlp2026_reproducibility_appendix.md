# EMNLP 2026 Reproducibility Appendix Draft

Date: 2026-04-29

Status: command block for the current Day-1 artifact freeze. Update after any new experiment run or artifact-freeze change.

Venue-form transfer answers for reproducibility, artifacts, anonymization, and compute-disclosure fields are consolidated in `docs/emnlp2026_venue_form_transfer_packet.md`.

## Environment Assumptions

- Repository root: `/data/sony/emnlp2026_critique_or_clarify`
- Local model cache paths are internal and should be replaced with model identifiers in the anonymized package.
- Current paper build uses ACL review style under `paper/styles/`.

## Regenerate Reports, Tables, And Figures

```bash
cd /data/sony/emnlp2026_critique_or_clarify

./scripts/make_day1_scale_reasoning_comparison.sh
./scripts/make_day1_quick_plus_stale_comparison.sh
python scripts/export_intervention_pilot_tables.py
python scripts/plot_emnlp2026_figure2_action_calibration.py
./scripts/sync_paper_assets.sh
```

## Run Final Lock Gate

```bash
cd /data/sony/emnlp2026_critique_or_clarify

./scripts/run_submission_lock_checks.sh
```

The final lock gate syncs paper assets, checks scale/reasoning artifacts, requires
complete human validation, runs the full test suite, builds the paper PDF, scans
LaTeX logs, builds the anonymous review package, and scans the package for
LaTeX aux/log files or internal repository paths.

## Current Expected Gate Outputs

- Human validation: `human_validation_queue_ok completed=61/61`
- DeepSeek-R1-Distill-Qwen-7B dev metrics: action accuracy `0.3667`, utility `-0.4313`
- DeepSeek-R1-Distill-Qwen-7B quick+stale metrics: action accuracy `0.4500`, utility `-0.4750`
- Benchmark expansion audit: `experiments/day1/benchmark_expansion_coverage_audit.md`
- Ask/abstain candidate audit: `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md`; accepted rows have been validated and promoted into the paper-facing expanded split.
- Validated candidate promotion tool: `scripts/promote_validated_expansion_candidates.py`
- Oral/best-paper quality audit: `docs/emnlp2026_oral_best_paper_quality_audit.md`
- Full test suite: `129 passed`
- Paper build: `paper/main.pdf`, 13 pages, no overfull or undefined/fatal/error log findings in the final scan
- Review package: `_review_package/critique_or_clarify_emnlp2026_review.zip`, with source, figures, tables, styles, and `main.pdf` but no LaTeX aux/log/bbl files
- Venue-form packet: `docs/emnlp2026_venue_form_transfer_packet.md`
- Final lock gate: `submission_lock_checks_ok`
