from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_paper_figure2_caption_is_finding_first_and_self_contained() -> None:
    results = (REPO_ROOT / "paper" / "sections" / "05_results.tex").read_text(encoding="utf-8")

    required_fragments = [
        "Reasoning traces do not automatically yield calibrated next-action decisions.",
        "shared model-color legend below the panels",
        "caution is not monotonic safety",
        "weak on false/stale premise interruption",
        "abstaining heavily on clean answerable controls",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in results]
    assert missing == []


def test_figure2_audit_records_oral_readiness_closure() -> None:
    audit = (REPO_ROOT / "docs" / "emnlp2026_figure2_audit.md").read_text(encoding="utf-8")

    required_fragments = [
        "oral-readiness polish pass current",
        "`MAJOR`: 0",
        "Panel C no longer relies on Panel B for model colors.",
        "Caption states the oral-readiness takeaway: caution is not monotonic safety.",
        "Shared model-color legend is present below the panels.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in audit]
    assert missing == []
