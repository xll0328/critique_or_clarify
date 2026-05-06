from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MEMO = REPO_ROOT / "docs" / "emnlp2026_reviewer_attack_memo.md"


def test_reviewer_attack_memo_reflects_closed_submission_gates() -> None:
    text = MEMO.read_text(encoding="utf-8")

    required_fragments = [
        "post-lock risk register",
        "`CRITICAL`: 0 open",
        "human_validation_queue_ok completed=61/61",
        "dev action accuracy `0.3667`",
        "dev utility `-0.4313`",
        "quick+stale action accuracy `0.4500`",
        "quick+stale utility `-0.4750`",
        "`129 passed`",
        "experiments/day1/benchmark_expansion_coverage_audit.md",
        "docs/emnlp2026_oral_best_paper_quality_audit.md",
        "_assets/emnlp2026_expansion_candidate_validation_queue.csv",
        "experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md",
        "scripts/promote_validated_expansion_candidates.py",
        "`submission_lock_checks_ok`",
        "Submission-freeze candidate for internal review.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_reviewer_attack_memo_no_longer_reports_old_blockers() -> None:
    text = MEMO.read_text(encoding="utf-8")

    stale_fragments = [
        "Not submission-ready yet",
        "0 / 61",
        "DeepSeek 7B metrics pending",
        "The 7B gate is closed and the project is on a plausible EMNLP-main path",
    ]

    present = [fragment for fragment in stale_fragments if fragment in text]
    assert present == []
