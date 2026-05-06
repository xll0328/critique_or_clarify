#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

LOG_DIR=${LOG_DIR:-logs/day1}
QWEN_DIR=/data/sony/model_cache/Qwen2.5-1.5B-Instruct
DEEPSEEK_DIR=/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B
QWEN_BYTES=3087467144
DEEPSEEK_SHARD1_BYTES=8606596466
DEEPSEEK_SHARD2_BYTES=6624675384

mkdir -p "$LOG_DIR"

has_exact_size() {
  local path=$1
  local expected=$2
  [[ -f "$path" && "$(stat -c '%s' "$path")" -eq "$expected" ]]
}

is_running() {
  local pattern=$1
  pgrep -af "$pattern" | grep -v "ensure_scale_reasoning_progress" >/dev/null 2>&1
}

start_background() {
  local label=$1
  local log_path=$2
  shift 2
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "would_start label=$label log=$log_path cmd=$*"
    return
  fi
  setsid nohup "$@" >> "$log_path" 2>&1 < /dev/null &
  echo "started label=$label pid=$! log=$log_path"
}

missing_qwen_metrics() {
  [[ ! -f outputs/day1/qwen25_15b_day1_dev_metrics.json ]] ||
    [[ ! -f outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json ]]
}

missing_deepseek_metrics() {
  [[ ! -f outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json ]] ||
    [[ ! -f outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json ]]
}

qwen_ready() {
  has_exact_size "$QWEN_DIR/model.safetensors" "$QWEN_BYTES"
}

deepseek_ready() {
  has_exact_size "$DEEPSEEK_DIR/model-00001-of-000002.safetensors" "$DEEPSEEK_SHARD1_BYTES" &&
    has_exact_size "$DEEPSEEK_DIR/model-00002-of-000002.safetensors" "$DEEPSEEK_SHARD2_BYTES"
}

echo "== scale/reasoning status =="
python scripts/check_scale_reasoning_status.py

if ! qwen_ready; then
  if is_running "fetch_qwen25_15b.sh"; then
    echo "qwen_fetch=running"
  else
    start_background qwen25_15b_fetch "$LOG_DIR/qwen25_15b_fetch.log" ./scripts/fetch_qwen25_15b.sh
  fi
elif missing_qwen_metrics; then
  if is_running "run_day1_qwen25_15b.sh"; then
    echo "qwen_runner=running"
  else
    start_background qwen25_15b_runner "$LOG_DIR/qwen25_15b_runner.log" ./scripts/run_day1_qwen25_15b.sh
  fi
else
  echo "qwen25_15b=complete"
fi

if ! deepseek_ready; then
  if is_running "fetch_deepseek_r1_qwen7b.sh|resume_download.sh.*DeepSeek-R1-Distill-Qwen-7B"; then
    echo "deepseek7b_fetch=running"
  else
    start_background deepseek7b_fetch "$LOG_DIR/deepseek_r1_qwen7b_fetch.log" ./scripts/fetch_deepseek_r1_qwen7b.sh
  fi
elif missing_deepseek_metrics; then
  if is_running "run_day1_deepseek_r1_qwen7b.sh|run_baseline.py.*DeepSeek-R1-Distill-Qwen-7B"; then
    echo "deepseek7b_runner=running"
  else
    start_background deepseek7b_runner "$LOG_DIR/deepseek_r1_qwen7b_runner.log" ./scripts/run_day1_deepseek_r1_qwen7b.sh
  fi
else
  echo "deepseek7b=complete"
fi
