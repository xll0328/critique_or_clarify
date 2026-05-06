from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
PAPER = REPO_ROOT / "paper"
AUDIT = DOCS / "emnlp2026_560_600_ci_scope_audit.md"


def test_560_600_ci_scope_audit_records_checked_surfaces() -> None:
    text = AUDIT.read_text(encoding="utf-8")

    required_fragments = [
        "Date: 2026-05-06",
        "canonical-vs-stress split language and confidence-interval scope",
        "No current main-paper wording does that",
        "Results: bootstrap interval paragraph",
        "Results: external API paragraph",
        "Results: slice-balance sensitivity paragraph",
        "Table `day1_full_split_sensitivity` caption",
        "Figure 6 caption",
        "Limitations",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_560_600_ci_scope_audit_locks_safe_phrases_in_paper() -> None:
    audit = AUDIT.read_text(encoding="utf-8")
    results = (PAPER / "sections" / "05_results.tex").read_text(encoding="utf-8")
    limitations = (PAPER / "sections" / "08_limitations.tex").read_text(encoding="utf-8")
    sensitivity_table = (PAPER / "tables" / "day1_full_split_sensitivity.tex").read_text(encoding="utf-8")

    required_fragments = [
        "600-example split as sensitivity evidence rather than as a replacement benchmark",
        "the headline remains the canonical 560-example split",
        "not a replacement headline benchmark",
        "uncertainty-qualified point estimates rather than as a fine-grained significance ranking",
        "local uncertainty checks over the current split samples",
        "not that every adjacent model difference is statistically separated",
    ]

    surface_text = "\n".join([audit, results, limitations, sensitivity_table])
    missing = [fragment for fragment in required_fragments if fragment not in surface_text]
    assert missing == []


def test_status_docs_point_to_560_600_ci_scope_audit() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_final_push_todo.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_560_600_ci_scope_audit.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
