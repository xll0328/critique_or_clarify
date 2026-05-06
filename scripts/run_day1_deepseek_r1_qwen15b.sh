#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_DIR=/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-1.5B
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}

if [[ ! -f "$MODEL_DIR/model.safetensors" ]]; then
  echo "missing_model path=$MODEL_DIR/model.safetensors" >&2
  echo "Run scripts/fetch_deepseek_r1_qwen15b.sh first." >&2
  exit 1
fi

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$MODEL_DIR" \
  --local-files-only \
  --omit-system-prompt \
  --assistant-prefix '<think>\n' \
  --data data/processed/day1_quick.jsonl \
  --output outputs/day1/deepseek_r1_qwen15b_day1_quick.jsonl \
  --eval-json outputs/day1/deepseek_r1_qwen15b_day1_quick_metrics.json \
  --max-new-tokens 180 \
  --temperature 0.6 \
  --top-p 0.95 \
  --seed 42

python scripts/sample_failures.py \
  --data data/processed/day1_quick.jsonl \
  --predictions outputs/day1/deepseek_r1_qwen15b_day1_quick.jsonl \
  --per-slice 2 > experiments/day1/deepseek_r1_qwen15b_day1_quick_failures.txt

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$MODEL_DIR" \
  --local-files-only \
  --omit-system-prompt \
  --assistant-prefix '<think>\n' \
  --data data/processed/day1_dev.jsonl \
  --output outputs/day1/deepseek_r1_qwen15b_day1_dev.jsonl \
  --eval-json outputs/day1/deepseek_r1_qwen15b_day1_dev_metrics.json \
  --max-new-tokens 180 \
  --temperature 0.6 \
  --top-p 0.95 \
  --seed 42

python scripts/sample_failures.py \
  --data data/processed/day1_dev.jsonl \
  --predictions outputs/day1/deepseek_r1_qwen15b_day1_dev.jsonl \
  --per-slice 2 > experiments/day1/deepseek_r1_qwen15b_day1_dev_failures.txt

python scripts/summarize_metrics.py \
  outputs/day1/deepseek_r1_qwen15b_day1_quick_metrics.json \
  outputs/day1/deepseek_r1_qwen15b_day1_dev_metrics.json
