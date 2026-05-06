#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_DIR=/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}
SHARD1_BYTES=8606596466
SHARD2_BYTES=6624675384

if [[ ! -f "$MODEL_DIR/model-00001-of-000002.safetensors" ]]; then
  echo "missing_model path=$MODEL_DIR/model-00001-of-000002.safetensors" >&2
  echo "Run scripts/fetch_deepseek_r1_qwen7b.sh first." >&2
  exit 1
fi

if [[ ! -f "$MODEL_DIR/model-00002-of-000002.safetensors" ]]; then
  echo "missing_model path=$MODEL_DIR/model-00002-of-000002.safetensors" >&2
  echo "Run scripts/fetch_deepseek_r1_qwen7b.sh first." >&2
  exit 1
fi

if [[ "$(stat -c '%s' "$MODEL_DIR/model-00001-of-000002.safetensors")" -ne "$SHARD1_BYTES" ]]; then
  echo "incomplete_model path=$MODEL_DIR/model-00001-of-000002.safetensors expected=$SHARD1_BYTES" >&2
  exit 1
fi

if [[ "$(stat -c '%s' "$MODEL_DIR/model-00002-of-000002.safetensors")" -ne "$SHARD2_BYTES" ]]; then
  echo "incomplete_model path=$MODEL_DIR/model-00002-of-000002.safetensors expected=$SHARD2_BYTES" >&2
  exit 1
fi

run_split() {
  local output_stem=$1
  local data_path=$2
  local fail_per_slice=$3
  local base=outputs/day1/${output_stem}

  CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
    --backend transformers \
    --model "$MODEL_DIR" \
    --local-files-only \
    --omit-system-prompt \
    --assistant-prefix '<think>\n' \
    --data "$data_path" \
    --output "${base}.jsonl" \
    --eval-json "${base}_metrics.json" \
    --max-new-tokens 180 \
    --temperature 0.6 \
    --top-p 0.95 \
    --seed 42

  python scripts/sample_failures.py \
    --data "$data_path" \
    --predictions "${base}.jsonl" \
    --per-slice "$fail_per_slice" > "experiments/day1/$(basename "${base}")_failures.txt"

  python scripts/reparse_predictions.py \
    --input "${base}.jsonl" \
    --output "${base}_reparsed.jsonl"

  python scripts/evaluate.py \
    --data "$data_path" \
    --predictions "${base}_reparsed.jsonl" \
    --report-json "${base}_reparsed_metrics.json"
}

run_split "deepseek_r1_qwen7b_day1_quick_useronlyfixed" "data/processed/day1_quick.jsonl" 2
run_split "deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed" "data/processed/day1_quick_plus_stale.jsonl" 2
run_split "deepseek_r1_qwen7b_day1_dev_useronlyfixed" "data/processed/day1_dev.jsonl" 2

python scripts/summarize_metrics.py \
  outputs/day1/deepseek_r1_qwen7b_day1_quick_useronlyfixed_reparsed_metrics.json \
  outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json \
  outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json

python scripts/build_day1_model_report.py \
  --quick-metrics outputs/day1/deepseek_r1_qwen7b_day1_quick_useronlyfixed_reparsed_metrics.json \
  --dev-metrics outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json \
  --dev-failures experiments/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_failures.txt \
  --output experiments/day1/deepseek_r1_qwen7b_day1_report.md \
  --model-id DeepSeek-R1-Distill-Qwen-7B \
  --local-snapshot "$MODEL_DIR" \
  --gpu "CUDA_VISIBLE_DEVICES=$GPU_ID" \
  --prompt-format "corrected user-only action-selection JSON" \
  --max-new-tokens 180 \
  --temperature 0.6

./scripts/make_day1_quick_plus_stale_comparison.sh
./scripts/make_day1_scale_reasoning_comparison.sh
