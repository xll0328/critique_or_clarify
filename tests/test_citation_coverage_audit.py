from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
AUDIT = DOCS / "emnlp2026_citation_coverage_audit.md"


def test_citation_coverage_audit_lists_all_current_bib_keys() -> None:
    text = AUDIT.read_text(encoding="utf-8")

    required_keys = [
        "kwiatkowski-etal-2019-natural",
        "rajpurkar-etal-2018-know",
        "aliannejadi-etal-2019-asking",
        "min-etal-2020-ambigqa",
        "stelmakh-etal-2022-asqa",
        "yu-etal-2023-crepe",
        "lin-etal-2022-truthfulqa",
        "kasai-etal-2023-realtimeqa",
        "vu-etal-2023-freshllms",
        "kamath-etal-2020-selective",
        "shaier-etal-2024-adaptive",
        "liu-etal-2025-open",
        "kadavath-etal-2022-language",
    ]

    missing = [key for key in required_keys if key not in text]
    assert missing == []


def test_citation_coverage_audit_preserves_scoped_positioning() -> None:
    text = AUDIT.read_text(encoding="utf-8")

    required_fragments = [
        "not an exhaustive literature survey",
        "next-action selection under defective inputs",
        "Supported as a framing contribution, not as a first/only claim.",
        "Do not imply these benchmarks are flawed",
        "Do not claim a complete evaluation of hard abstain behavior.",
        "The benchmark fully evaluates ask and abstain.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_citation_coverage_audit() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_reviewer_attack_memo.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_citation_coverage_audit.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
