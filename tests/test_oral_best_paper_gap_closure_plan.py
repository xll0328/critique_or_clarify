from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
PLAN = DOCS / "emnlp2026_oral_best_paper_gap_closure_plan.md"


def test_gap_closure_plan_answers_distance_question_and_tracks_deadline() -> None:
    text = PLAN.read_text(encoding="utf-8")

    required_fragments = [
        "Date: 2026-05-06",
        "2026-05-25, 11:59PM UTC-12",
        "https://2026.emnlp.org/calls/main_conference_papers/",
        "Clean EMNLP submission",
        "Oral-level paper",
        "Best-paper-level paper",
        "submission-close, oral medium-far, best-paper far",
        "Current readiness estimate from project audits: `3.1 / 5`",
        "`560` examples",
        "`61/61`",
        "`./scripts/run_submission_lock_checks.sh` passes",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_gap_closure_plan_has_tracks_and_human_only_stop_conditions() -> None:
    text = PLAN.read_text(encoding="utf-8")

    required_fragments = [
        "Track A: Acceptance-Safe Freeze",
        "Track B: Oral Evidence Hardening",
        "Track C: Best-Paper Narrative Hardening",
        "Track D: Reviewer Attack Preemption",
        "Track E: Submission Operations",
        "Final human PDF read is not complete",
        "Statistical depth is not oral-grade",
        "`600` as stress evidence",
        "pending-human",
        "automated audit would fill or imply final human sign-off",
        "official venue metadata, conflicts, reviewer registration, or submit click is needed",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_gap_closure_plan() -> None:
    docs_to_check = [
        REPO_ROOT / "README.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_final_push_todo.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_oral_best_paper_gap_closure_plan.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
