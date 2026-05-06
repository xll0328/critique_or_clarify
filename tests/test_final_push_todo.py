from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
TODO = DOCS / "emnlp2026_final_push_todo.md"
WORKSHEET = DOCS / "emnlp2026_final_pdf_human_review_worksheet.md"


def test_final_push_todo_tracks_deadline_scope_and_stop_conditions() -> None:
    text = TODO.read_text(encoding="utf-8")

    required_fragments = [
        "Date: 2026-05-06",
        "2026-05-25, 11:59PM UTC-12",
        "https://2026.emnlp.org/calls/main_conference_papers/",
        "not yet oral-ready or best-paper-ready",
        "canonical paper-facing split is `560` examples",
        "slice-balanced `600` split is stress evidence only",
        "Keep confidence intervals as local uncertainty checks",
        "Do not start broad new model runs",
        "Stop Conditions",
        "a proposed paper claim would make the `600` split the de facto headline benchmark",
        "./scripts/run_submission_lock_checks.sh",
        "Opened `docs/emnlp2026_final_pdf_human_review_worksheet.md`",
        "Started the worksheet with a Codex-only PDF text preflight",
        "tightening the abstract around the line that answer quality is incomplete",
        "Synchronized the reviewer-response seed memo with the tightened abstract wording",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_final_push_todo_has_date_bounded_workstreams() -> None:
    text = TODO.read_text(encoding="utf-8")

    required_fragments = [
        "2026-05-06 to 2026-05-08",
        "2026-05-09 to 2026-05-11",
        "2026-05-12 to 2026-05-15",
        "2026-05-16 to 2026-05-20",
        "2026-05-21 to 2026-05-24",
        "2026-05-25",
        "Story And First Two Pages",
        "Evidence And Statistics",
        "Benchmark Validity",
        "Figures And Tables",
        "Reviewer Response And Rebuttal Prep",
        "Packaging, Forms, And Final Sign-Off",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_final_pdf_human_review_worksheet_does_not_auto_complete_signoff() -> None:
    text = WORKSHEET.read_text(encoding="utf-8")

    required_fragments = [
        "Status: opened for final human review. This worksheet is not completed human sign-off.",
        "Human reviewer name or initials",
        "Decision",
        "approve_for_submission",
        "approve_after_minor_fixes",
        "block_until_fixed",
        "Do not mark this worksheet as complete unless a human has inspected the compiled PDF",
        "Codex must not fill the human reviewer, decision, or final approval fields",
        "Status: automated preflight started. This is not human approval.",
        "PDF length: `13` pages.",
        "Pages 1-2 contain the first-story anchors",
        "Answer quality is an incomplete target",
        "right first move",
        "Pages 5-7 contain the main-result anchors",
        "Open human task: inspect the compiled PDF visually",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_final_push_artifacts() -> None:
    docs_to_check = [
        REPO_ROOT / "README.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
    ]

    missing_todo = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_final_push_todo.md"
        not in path.read_text(encoding="utf-8")
    ]
    missing_worksheet = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_final_pdf_human_review_worksheet.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing_todo == []
    assert missing_worksheet == []
