#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

INTERVAL_SECONDS=${INTERVAL_SECONDS:-120}
MAX_SECONDS=${MAX_SECONDS:-21600}
START_SECONDS=$(date +%s)

complete() {
  [[ -f outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json ]] &&
    [[ -f outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json ]]
}

while true; do
  echo "watch_tick ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  ./scripts/ensure_scale_reasoning_progress.sh

  if complete; then
    echo "scale_reasoning_complete ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    break
  fi

  now_seconds=$(date +%s)
  elapsed_seconds=$((now_seconds - START_SECONDS))
  if [[ "$elapsed_seconds" -ge "$MAX_SECONDS" ]]; then
    echo "watch_timeout elapsed_seconds=$elapsed_seconds max_seconds=$MAX_SECONDS" >&2
    exit 124
  fi

  sleep "$INTERVAL_SECONDS"
done
