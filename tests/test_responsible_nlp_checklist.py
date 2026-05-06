from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = REPO_ROOT / "docs" / "emnlp2026_responsible_nlp_checklist.md"


def test_responsible_nlp_checklist_covers_submission_risk_areas() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")

    required_fragments = [
        "current submission-freeze responsible-NLP preflight",
        "not a deployment policy",
        "not from private user logs",
        "human_validation_queue_ok completed=61/61",
        "does not prove that the ontology is uniquely correct",
        "AI-generated review aids and Codex multipass outputs are treated as triage material",
        "scans the review package for local paths",
        "Over-answering can reinforce false or stale assumptions",
        "Over-challenging or over-abstaining can make assistants obstructive",
        "utility encodes an asymmetric harm ordering",
        "completed local checkpoint matrix and prompt protocol",
        "./scripts/run_submission_lock_checks.sh",
        "`129 passed`",
        "scripts/promote_validated_expansion_candidates.py",
        "submission_lock_checks_ok",
        "environmental or compute disclosure if requested by the form",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_responsible_nlp_checklist_does_not_overclaim_scope() -> None:
    text = CHECKLIST.read_text(encoding="utf-8").lower()

    forbidden_fragments = [
        "solves hallucination",
        "is deployment-ready",
        "objective benchmark",
        "proves the ontology",
        "uses private user logs",
    ]

    present = [fragment for fragment in forbidden_fragments if fragment in text]
    assert present == []
