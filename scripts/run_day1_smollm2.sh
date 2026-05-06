#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

python scripts/prefetch_model.py \
  --repo-id HuggingFaceTB/SmolLM2-135M-Instruct

CUDA_VISIBLE_DEVICES=7 python scripts/run_baseline.py \
  --backend transformers \
  --model HuggingFaceTB/SmolLM2-135M-Instruct \
  --local-files-only \
  --data data/processed/day1_dev.jsonl \
  --output outputs/day1/smollm2_135m_day1_dev.jsonl \
  --eval-json outputs/day1/smollm2_135m_day1_dev_metrics.json \
  --max-new-tokens 120 \
  --temperature 0.0
