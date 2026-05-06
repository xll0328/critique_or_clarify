from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
MEMO = DOCS / "emnlp2026_reviewer_triage_revision_memo.md"


def test_reviewer_triage_revision_memo_covers_required_personas_and_buckets() -> None:
    text = MEMO.read_text(encoding="utf-8")

    required_fragments = [
        "Date: 2026-05-06",
        "2026-05-25",
        "Reviewer 1: novelty and positioning",
        "Reviewer 2: benchmark validity",
        "Reviewer 3: experiments and statistics",
        "Devil's Advocate",
        "Must-Fix Before Submission",
        "Should-Fix Before Submission",
        "Appendix-Only Or Defer",
        "Safe Next Editing Order",
        "First pass closed in `paper/sections/05_results.tex` and `paper/sections/08_limitations.tex`",
        "not fine-grained model rankings",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_reviewer_triage_revision_memo_enforces_claim_scope() -> None:
    text = MEMO.read_text(encoding="utf-8")

    required_fragments = [
        "canonical 560-example claims separate from 600-example stress evidence",
        "The canonical split remains `560`",
        "slice-balanced `600` split is sensitivity or stress evidence only",
        "Utility must be described as an asymmetric harm-ordering diagnostic",
        "`decision_first` stays an exploratory calibration lever",
        "Scope DeepSeek reasoning results to completed Day-1 local checkpoints",
        "Automated audits do not replace final human PDF read",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_reviewer_triage_revision_memo_blocks_overclaim_language() -> None:
    text = MEMO.read_text(encoding="utf-8")

    forbidden_as_claims = [
        ' "oral-ready"',
        ' "best-paper-ready"',
        ' "the 600-example split replaces the canonical benchmark"',
        ' "utility captures real user costs"',
        ' "decision_first is a robust controller"',
        ' "reasoning models fail at defective inputs"',
        ' "automated audit is final human sign-off"',
    ]

    assert "## Do Not Say" in text
    missing_do_not_say_entries = [
        fragment.strip()
        for fragment in forbidden_as_claims
        if fragment.strip() not in text
    ]
    assert missing_do_not_say_entries == []


def test_status_docs_point_to_reviewer_triage_revision_memo() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_reviewer_attack_memo.md",
        DOCS / "emnlp2026_oral_best_paper_sprint_plan.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_reviewer_triage_revision_memo.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
