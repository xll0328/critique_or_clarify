#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

if [[ -z "${AIHUBMIX_API_KEY:-}" ]]; then
  echo "Missing AIHUBMIX_API_KEY. Export it before running." >&2
  exit 1
fi

run_with_retry() {
  local model="$1"
  local prompt_style="$2"
  local output_path="$3"
  local eval_path="$4"
  local attempt=1

  while true; do
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] run ${model} style=${prompt_style} attempt=${attempt}"
    if python scripts/run_aihubmix_baseline.py \
      --model "${model}" \
      --data data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl \
      --output "${output_path}" \
      --eval-json "${eval_path}" \
      --prompt-style "${prompt_style}" \
      --max-tokens 64 \
      --temperature 0.0 \
      --request-timeout 45 \
      --retry 1 \
      --save-every 5 \
      --progress-every 5 \
      --resume; then
      break
    fi

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] run failed; retry in 6s"
    attempt=$((attempt + 1))
    sleep 6
  done
}

run_with_retry \
  "qwen-plus-latest" \
  "decision_first_guarded" \
  "outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded.jsonl" \
  "outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json"

run_with_retry \
  "qwen-plus-latest" \
  "critique_first" \
  "outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first.jsonl" \
  "outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first_metrics.json"

python scripts/compare_runs.py \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first_metrics.json \
  --title "Qwen-Plus-Latest Prompt-Style Controls (Expanded 560)" \
  --confusion-for 1 --confusion-for 2 --confusion-for 3 \
  --output experiments/day1/day1_qwenplus_prompt_controls_comparison.md

python scripts/export_scale_reasoning_bootstrap.py \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first_metrics.json \
  --title "Qwen-Plus-Latest Prompt Controls Bootstrap CIs" \
  --output-md experiments/day1/day1_qwenplus_prompt_controls_ci.md \
  --output-dir experiments/day1/tables \
  --prefix day1_qwenplus_prompt_controls_ci

python scripts/plot_emnlp2026_figure6_api_baseline_comparison.py \
  --metric-paths \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first_metrics.json \
  --output-prefix experiments/day1/figures/day1_qwenplus_prompt_controls

bash scripts/sync_paper_assets.sh

python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path

note = Path("experiments/day1/notes.md")
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
entry = (
    f"| {ts} | AIHubMix API (`qwen-plus-latest`) | "
    "`emnlp2026_expanded_dev_with_answer_topup` (560) | "
    "`decision_first_guarded + critique_first` refresh and control comparison generated | "
    "Artifacts: "
    "`outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json`, "
    "`outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first_metrics.json`, "
    "`experiments/day1/day1_qwenplus_prompt_controls_comparison.md`, "
    "`experiments/day1/day1_qwenplus_prompt_controls_ci.md`, "
    "`experiments/day1/figures/day1_qwenplus_prompt_controls.{png,pdf}`. |"
)

lines = note.read_text(encoding="utf-8").splitlines()
if entry not in lines:
    insert_idx = None
    for idx, line in enumerate(lines):
        if line.startswith("| 202"):
            insert_idx = idx
            break
    if insert_idx is None:
        lines.append(entry)
    else:
        lines.insert(insert_idx, entry)
    note.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] prompt-controls refresh complete"
