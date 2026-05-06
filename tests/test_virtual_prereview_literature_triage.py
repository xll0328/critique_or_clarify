from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
TRIAGE = DOCS / "emnlp2026_virtual_prereview_literature_triage.md"


def test_virtual_prereview_literature_triage_separates_verified_from_unverified() -> None:
    text = TRIAGE.read_text(encoding="utf-8")

    required_fragments = [
        "Do not add unverified entries to `paper/references.bib`",
        "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions",
        "10.48550/arxiv.2506.09038",
        "Judge Before Answer: Can MLLM Discern the False Premise in Question?",
        "10.48550/arxiv.2510.10965",
        "Premise Order Matters in Reasoning with Large Language Models",
        "10.48550/arxiv.2402.08939",
        "title-mismatch",
        "Not Yet Verified",
        "No bibliography edit in this chunk",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_virtual_prereview_literature_triage() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_final_push_todo.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_virtual_prereview_literature_triage.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []

