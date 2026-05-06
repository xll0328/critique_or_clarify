from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
DOCS_DIR = REPO_ROOT / "docs"


def _section(name: str) -> str:
    return (PAPER_DIR / "sections" / name).read_text(encoding="utf-8")


def test_first_two_page_oral_thesis_is_locked_in_source() -> None:
    abstract = _section("00_abstract.tex")
    introduction = _section("01_introduction.tex")
    related_work = _section("02_related_work.tex")

    required_fragments = [
        "do not guarantee the right first move",
        "selecting \\texttt{answer} when \\texttt{challenge} is required",
        "not another defect category, but the action decision that precedes generation",
        "the assistant must decide whether answering is the right next action at all",
    ]
    combined = "\n".join([abstract, introduction, related_work])

    missing = [fragment for fragment in required_fragments if fragment not in combined]
    assert missing == []


def test_first_two_page_oral_readiness_audit_records_pdf_level_findings() -> None:
    audit = (DOCS_DIR / "emnlp2026_first_two_page_oral_readiness_audit.md").read_text(encoding="utf-8")

    required_fragments = [
        "PDF text extraction from `paper/main.pdf` pages 1-2 using `pypdf`",
        "`CRITICAL`: 0",
        "`MAJOR`: 0",
        "Figure 1 appears at the top of page 2 and is self-contained.",
        "Results preview and contributions appear before Related Work.",
        "wrong first move: selecting `answer` when `challenge` is required",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in audit]
    assert missing == []


def test_gap_and_readiness_docs_point_to_first_two_page_audit() -> None:
    gap_list = (DOCS_DIR / "emnlp2026_manuscript_gap_list.md").read_text(encoding="utf-8")
    checklist = (DOCS_DIR / "emnlp2026_submission_readiness_checklist.md").read_text(encoding="utf-8")
    reviewer_memo = (DOCS_DIR / "emnlp2026_reviewer_attack_memo.md").read_text(encoding="utf-8")

    assert "oral-readiness PDF audits closed" in gap_list
    assert "tests/test_first_two_page_oral_readiness.py" in checklist
    assert "PDF-level first-two-page oral-readiness audit is current" in reviewer_memo
