from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_SCRIPT = REPO_ROOT / "scripts" / "run_submission_lock_checks.sh"


def test_submission_lock_script_contains_all_blocking_gates() -> None:
    text = LOCK_SCRIPT.read_text(encoding="utf-8")

    required_fragments = [
        "./scripts/sync_paper_assets.sh",
        "python scripts/check_scale_reasoning_status.py",
        "python scripts/validate_human_validation_queue.py",
        "--require-complete",
        "pytest -q",
        "./paper/build.sh",
        "python scripts/audit_full_pdf_visual_readiness.py",
        "Overfull|undefined|Undefined|Fatal|Emergency|Error",
        "./scripts/build_review_package.sh",
        "find \"$REVIEW_PACKAGE_DIR\"",
        "/data/sony|sony|model_cache|outputs/day1|experiments/day1|_assets/",
        "submission_lock_checks_ok",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_submission_lock_script_is_portable_and_executable() -> None:
    text = LOCK_SCRIPT.read_text(encoding="utf-8")

    assert os.access(LOCK_SCRIPT, os.X_OK)
    assert "${BASH_SOURCE[0]}" in text
    assert "/data/sony/emnlp2026_critique_or_clarify" not in text
