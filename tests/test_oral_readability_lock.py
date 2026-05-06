from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
LOCK = DOCS / "emnlp2026_oral_readability_lock.md"


def test_oral_readability_lock_covers_90_second_story() -> None:
    text = LOCK.read_text(encoding="utf-8")

    required_fragments = [
        "90-Second Reviewer Takeaway",
        "answer, ask, challenge, or abstain",
        "wrong-first-move",
        "Figure 1 is the oral schematic",
        "caution is not monotonic safety",
        "Oral Readability Lock is closed",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_oral_readability_lock_preserves_main_evidence_and_scope() -> None:
    text = LOCK.read_text(encoding="utf-8")

    required_fragments = [
        "DeepSeek-R1-Distill-Qwen-7B reaches `0.3667` action accuracy and `-0.4313` utility",
        "quick+stale utility from `-0.2188` to `-0.1375`",
        "action accuracy from `0.775` to `0.85`",
        "over-answer rate from `0.05` to `0`",
        "current prompt/parsing protocol",
        "not a complete method",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_oral_readability_lock() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_oral_best_paper_sprint_plan.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_oral_readability_lock.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
