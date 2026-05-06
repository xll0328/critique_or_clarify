#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

BASE_URL=https://hf-mirror.com/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B/resolve/main
MODEL_DIR=/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-1.5B
MODEL_PATH=$MODEL_DIR/model.safetensors
INCOMPLETE_PATH=${MODEL_PATH}.incomplete
EXPECTED_BYTES=3554214621

mkdir -p "$MODEL_DIR"

for filename in .gitattributes LICENSE README.md config.json generation_config.json tokenizer.json tokenizer_config.json; do
  target=$MODEL_DIR/$filename
  if [[ -f "$target" ]]; then
    continue
  fi
  curl \
    -fL \
    --retry 5 \
    --retry-delay 2 \
    --retry-all-errors \
    --connect-timeout 30 \
    "$BASE_URL/$filename" \
    -o "$target"
done

if [[ ! -f "$MODEL_PATH" ]]; then
  scripts/resume_download.sh "$BASE_URL/model.safetensors" "$INCOMPLETE_PATH" "$EXPECTED_BYTES" 3
  current_size=$(stat -c '%s' "$INCOMPLETE_PATH")
  if [[ "$current_size" -ne "$EXPECTED_BYTES" ]]; then
    echo "download_size_mismatch size=$current_size expected=$EXPECTED_BYTES" >&2
    exit 1
  fi
  mv "$INCOMPLETE_PATH" "$MODEL_PATH"
fi

stat -c 'model_ready size=%s path=%n' "$MODEL_PATH"
