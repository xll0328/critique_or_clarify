#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

SNAPSHOT_DIR=/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775
EXPECTED_BYTES=988097824
FINAL_BLOB=/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/blobs/fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe
INCOMPLETE_BLOB=${FINAL_BLOB}.incomplete
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}

if [[ ! -f "$FINAL_BLOB" ]]; then
  if [[ ! -f "$INCOMPLETE_BLOB" ]]; then
    echo "missing_blob path=$FINAL_BLOB" >&2
    exit 1
  fi

  current_size=$(stat -c '%s' "$INCOMPLETE_BLOB")
  if [[ "$current_size" -ne "$EXPECTED_BYTES" ]]; then
    echo "download_size_mismatch size=$current_size expected=$EXPECTED_BYTES" >&2
    exit 1
  fi

  mv "$INCOMPLETE_BLOB" "$FINAL_BLOB"
fi

python scripts/finalize_snapshot_weight.py \
  --snapshot-dir "$SNAPSHOT_DIR" \
  --blob-path "$FINAL_BLOB"

CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
  --backend transformers \
  --model "$SNAPSHOT_DIR" \
  --local-files-only \
  --data data/processed/day1_dev.jsonl \
  --output outputs/day1/qwen25_05b_day1_dev.jsonl \
  --eval-json outputs/day1/qwen25_05b_day1_dev_metrics.json \
  --max-new-tokens 140 \
  --temperature 0.0
