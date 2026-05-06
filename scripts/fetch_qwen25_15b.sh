#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_URL=https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct/resolve/main/model.safetensors
EXPECTED_BYTES=3087467144
MODEL_DIR=/data/sony/model_cache/Qwen2.5-1.5B-Instruct
FINAL_PATH=${MODEL_DIR}/model.safetensors
INCOMPLETE_PATH=${FINAL_PATH}.incomplete

mkdir -p "$MODEL_DIR"

for filename in .gitattributes LICENSE README.md config.json generation_config.json merges.txt tokenizer.json tokenizer_config.json vocab.json; do
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
    "https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct/resolve/main/$filename" \
    -o "$target"
done

scripts/resume_download.sh "$MODEL_URL" "$INCOMPLETE_PATH" "$EXPECTED_BYTES" 3

current_size=$(stat -c '%s' "$INCOMPLETE_PATH")
if [[ "$current_size" -ne "$EXPECTED_BYTES" ]]; then
  echo "download_size_mismatch size=$current_size expected=$EXPECTED_BYTES" >&2
  exit 1
fi

mv "$INCOMPLETE_PATH" "$FINAL_PATH"
stat -c 'model_ready size=%s path=%n' "$FINAL_PATH"
