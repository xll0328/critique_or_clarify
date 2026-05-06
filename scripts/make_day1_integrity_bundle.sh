#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

python scripts/build_human_validation_work_queue.py \
  --output _assets/human_validation_work_queue.csv

python scripts/validate_human_validation_queue.py \
  --queue _assets/human_validation_work_queue.csv > /dev/null

python scripts/summarize_human_validation_work_queue.py \
  --queue _assets/human_validation_work_queue.csv \
  --output _assets/human_validation_work_queue_summary.md > /dev/null

python scripts/export_human_validation_packets.py \
  --queue _assets/human_validation_work_queue.csv \
  --split data/processed/day1_quick_plus_stale_pool.jsonl \
  --output-dir _assets/human_validation_packets > /dev/null

python scripts/build_codex_expert_validation_review.py \
  --queue _assets/human_validation_work_queue.csv \
  --split data/processed/day1_quick_plus_stale_pool.jsonl \
  --output-csv _assets/codex_expert_validation_review.csv \
  --output-md _assets/codex_expert_validation_review.md > /dev/null

python scripts/build_codex_multipass_validation_review.py \
  --queue _assets/human_validation_work_queue.csv \
  --split data/processed/day1_quick_plus_stale_pool.jsonl \
  --output-dir _assets/codex_multipass_validation_review > /dev/null

python scripts/build_day1_integrity_dashboard.py \
  --queue _assets/human_validation_work_queue.csv \
  --output experiments/day1/day1_integrity_dashboard.md > /dev/null

echo "Wrote day-1 integrity bundle." >&2
