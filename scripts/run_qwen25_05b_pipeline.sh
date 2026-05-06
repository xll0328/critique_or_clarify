#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_URL=https://hf-mirror.com/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors
EXPECTED_BYTES=988097824
EXPECTED_BLOB=fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe
BLOB_DIR=/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/blobs
FINAL_BLOB=${BLOB_DIR}/${EXPECTED_BLOB}
INCOMPLETE_BLOB=${FINAL_BLOB}.incomplete
SNAPSHOT_DIR=/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}

if [[ -f "$FINAL_BLOB" ]]; then
  echo "using_existing_blob path=$FINAL_BLOB"
else
  scripts/resume_download.sh "$MODEL_URL" "$INCOMPLETE_BLOB" "$EXPECTED_BYTES" 3

  if [[ ! -f "$INCOMPLETE_BLOB" ]]; then
    echo "download_missing path=$INCOMPLETE_BLOB" >&2
    exit 1
  fi

  current_size=$(stat -c '%s' "$INCOMPLETE_BLOB")
  if [[ "$current_size" -ne "$EXPECTED_BYTES" ]]; then
    echo "download_size_mismatch size=$current_size expected=$EXPECTED_BYTES" >&2
    exit 1
  fi

  mv "$INCOMPLETE_BLOB" "$FINAL_BLOB"
fi

stat -c 'blob_ready size=%s path=%n' "$FINAL_BLOB"

python scripts/finalize_snapshot_weight.py \
  --snapshot-dir "$SNAPSHOT_DIR" \
  --blob-path "$FINAL_BLOB"

python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer

path = "/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775"
tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, use_safetensors=True)
print("load_ok", tokenizer.vocab_size, model.__class__.__name__)
PY

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$SNAPSHOT_DIR" \
  --local-files-only \
  --data data/processed/day1_quick.jsonl \
  --output outputs/day1/qwen25_05b_day1_quick.jsonl \
  --eval-json outputs/day1/qwen25_05b_day1_quick_metrics.json \
  --max-new-tokens 140 \
  --temperature 0.0

python scripts/sample_failures.py \
  --data data/processed/day1_quick.jsonl \
  --predictions outputs/day1/qwen25_05b_day1_quick.jsonl \
  --per-slice 2 > experiments/day1/qwen25_05b_day1_quick_failures.txt

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$SNAPSHOT_DIR" \
  --local-files-only \
  --data data/processed/day1_dev.jsonl \
  --output outputs/day1/qwen25_05b_day1_dev.jsonl \
  --eval-json outputs/day1/qwen25_05b_day1_dev_metrics.json \
  --max-new-tokens 140 \
  --temperature 0.0

python scripts/sample_failures.py \
  --data data/processed/day1_dev.jsonl \
  --predictions outputs/day1/qwen25_05b_day1_dev.jsonl \
  --per-slice 2 > experiments/day1/qwen25_05b_day1_dev_failures.txt

python scripts/summarize_metrics.py \
  outputs/day1/qwen25_05b_day1_quick_metrics.json \
  outputs/day1/qwen25_05b_day1_dev_metrics.json
