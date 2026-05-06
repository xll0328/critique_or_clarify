from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
PLAN = DOCS / "emnlp2026_virtual_prereview_revision_plan.md"


def test_virtual_prereview_revision_plan_tracks_major_risks() -> None:
    text = PLAN.read_text(encoding="utf-8")

    required_fragments = [
        "borderline-findings signal",
        "Benchmark reads preliminary or internally named",
        "Dataset construction is underdescribed",
        "Ontology reliability is not IAA",
        "Parsing confounds model comparison",
        "Utility weights look ad hoc",
        "Figure/caption instability hurts trust",
        "Related work may be incomplete or hallucinated",
        "API baselines feel under-integrated",
        "Responsible-use discussion is too generic",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_virtual_prereview_revision_plan_has_experiment_queue_and_stop_conditions() -> None:
    text = PLAN.read_text(encoding="utf-8")

    required_fragments = [
        "Parse sensitivity audit",
        "Utility weight sensitivity",
        "Completed for the current local matrix",
        "API slice breakdown",
        "experiments/day1/day1_api_slice_breakdown.md",
        "all weakest API slices fall on `false_premise` or `conflicting_evidence`",
        "Human boundary packet",
        "Figure/source stability audit",
        "Stop if raw outputs are missing",
        "Stop if a suggested paper cannot be verified",
        "human agreement study",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_final_push_todo_points_to_virtual_prereview_plan() -> None:
    text = (DOCS / "emnlp2026_final_push_todo.md").read_text(encoding="utf-8")

    assert "docs/emnlp2026_virtual_prereview_revision_plan.md" in text
    assert "Virtual Prereview Major Revision" in text
