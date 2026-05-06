#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

BASE_URL=https://hf-mirror.com/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B/resolve/main
MODEL_DIR=/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B

mkdir -p "$MODEL_DIR"

for filename in .gitattributes LICENSE README.md config.json generation_config.json tokenizer.json tokenizer_config.json model.safetensors.index.json; do
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

scripts/resume_download.sh \
  "$BASE_URL/model-00001-of-000002.safetensors" \
  "$MODEL_DIR/model-00001-of-000002.safetensors" \
  8606596466 \
  3 &
pid_shard1=$!

scripts/resume_download.sh \
  "$BASE_URL/model-00002-of-000002.safetensors" \
  "$MODEL_DIR/model-00002-of-000002.safetensors" \
  6624675384 \
  3 &
pid_shard2=$!

wait "$pid_shard1"
wait "$pid_shard2"

for filename in model-00001-of-000002.safetensors model-00002-of-000002.safetensors; do
  stat -c 'model_ready size=%s path=%n' "$MODEL_DIR/$filename"
done
