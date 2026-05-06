from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"


def test_first_two_page_visual_balance_audit_records_rendered_pdf_review() -> None:
    audit = (DOCS_DIR / "emnlp2026_first_two_page_visual_balance_audit.md").read_text(encoding="utf-8")

    required_fragments = [
        "Rendered `paper/main.pdf` pages 1-2 to PNG at 2x scale with PyMuPDF.",
        "`CRITICAL`: 0",
        "`MAJOR`: 0",
        "Page 1 is dense but readable and story-forward.",
        "Figure 1 is readable at paper scale.",
        "Contributions and Related Work both appear on page 2.",
        "first two pages are visually acceptable for an internal oral-readiness pass",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in audit]
    assert missing == []


def test_first_two_page_visual_balance_preserves_regression_rules() -> None:
    audit = (DOCS_DIR / "emnlp2026_first_two_page_visual_balance_audit.md").read_text(encoding="utf-8")

    required_fragments = [
        "Abstract ends with the right-first-move thesis.",
        "The Facebook `FB` example appears on page 1.",
        "Figure 1 appears on page 2 and remains legible at paper scale.",
        "Contributions appear before Related Work.",
        "Related Work begins with the \"before judging answer text\" boundary.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in audit]
    assert missing == []


def test_project_status_docs_point_to_visual_balance_audit() -> None:
    gap_list = (DOCS_DIR / "emnlp2026_manuscript_gap_list.md").read_text(encoding="utf-8")
    checklist = (DOCS_DIR / "emnlp2026_submission_readiness_checklist.md").read_text(encoding="utf-8")
    reviewer_memo = (DOCS_DIR / "emnlp2026_reviewer_attack_memo.md").read_text(encoding="utf-8")

    assert "First-two-page story and visual balance" in gap_list
    assert "tests/test_first_two_page_visual_balance.py" in checklist
    assert "visual-balance audit is current" in reviewer_memo
