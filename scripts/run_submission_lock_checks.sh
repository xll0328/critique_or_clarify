#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
REVIEW_PACKAGE_DIR="$REPO_ROOT/_review_package/critique_or_clarify_emnlp2026_review"

cd "$REPO_ROOT"

echo "[1/9] Syncing paper assets"
./scripts/sync_paper_assets.sh

echo "[2/9] Checking scale/reasoning artifacts"
python scripts/check_scale_reasoning_status.py

echo "[3/9] Checking human validation queue"
python scripts/validate_human_validation_queue.py \
  --queue _assets/human_validation_work_queue.csv \
  --require-complete

echo "[4/9] Running test suite"
pytest -q

echo "[5/9] Building paper PDF"
./paper/build.sh

echo "[6/9] Auditing full PDF visual readiness"
python scripts/audit_full_pdf_visual_readiness.py

echo "[7/9] Scanning paper LaTeX logs"
if grep -nE "Overfull|undefined|Undefined|Fatal|Emergency|Error" paper/main.log paper/main.blg; then
  echo "paper_log_scan_failed" >&2
  exit 1
fi

echo "[8/9] Building anonymous review package"
./scripts/build_review_package.sh

echo "[9/9] Scanning review package"
if find "$REVIEW_PACKAGE_DIR" -type f \( \
  -name '*.aux' -o \
  -name '*.log' -o \
  -name '*.out' -o \
  -name '*.bbl' -o \
  -name '*.blg' \
\) -print -quit | grep -q .; then
  echo "review_package_latex_aux_files_found" >&2
  exit 1
fi

if grep -R -nE '/data/sony|sony|model_cache|outputs/day1|experiments/day1|_assets/' "$REVIEW_PACKAGE_DIR"; then
  echo "review_package_internal_path_found" >&2
  exit 1
fi

echo "submission_lock_checks_ok"
