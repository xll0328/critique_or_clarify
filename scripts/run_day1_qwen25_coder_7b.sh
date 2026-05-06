#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_DIR=/data/sony/.cache/modelscope/hub/models/Qwen/Qwen2___5-Coder-7B-Instruct
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$MODEL_DIR" \
  --local-files-only \
  --data data/processed/day1_quick.jsonl \
  --output outputs/day1/qwen25_coder_7b_day1_quick.jsonl \
  --eval-json outputs/day1/qwen25_coder_7b_day1_quick_metrics.json \
  --max-new-tokens 140 \
  --temperature 0.0

python scripts/sample_failures.py \
  --data data/processed/day1_quick.jsonl \
  --predictions outputs/day1/qwen25_coder_7b_day1_quick.jsonl \
  --per-slice 2 > experiments/day1/qwen25_coder_7b_day1_quick_failures.txt

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$MODEL_DIR" \
  --local-files-only \
  --data data/processed/day1_dev.jsonl \
  --output outputs/day1/qwen25_coder_7b_day1_dev.jsonl \
  --eval-json outputs/day1/qwen25_coder_7b_day1_dev_metrics.json \
  --max-new-tokens 140 \
  --temperature 0.0

python scripts/sample_failures.py \
  --data data/processed/day1_dev.jsonl \
  --predictions outputs/day1/qwen25_coder_7b_day1_dev.jsonl \
  --per-slice 2 > experiments/day1/qwen25_coder_7b_day1_dev_failures.txt

python scripts/summarize_metrics.py \
  outputs/day1/qwen25_coder_7b_day1_quick_metrics.json \
  outputs/day1/qwen25_coder_7b_day1_dev_metrics.json
