from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


def _section(name: str) -> str:
    return (PAPER_DIR / "sections" / name).read_text(encoding="utf-8")


def test_abstract_presents_unified_action_decision_benchmark() -> None:
    abstract = _section("00_abstract.tex")

    required_fragments = [
        "Answer quality is an incomplete target",
        "evidence-conditioned first-move decision",
        "share one action-decision record",
        "action ontology",
        "completed human-validation queue",
        "completed Day-1 local model-and-prompt matrix",
        "The scoped claim is that next-action calibration is a distinct capability",
        "do not guarantee the right first move",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in abstract]
    assert missing == []


def test_introduction_running_example_names_wrong_first_move() -> None:
    introduction = _section("01_introduction.tex")

    assert "Facebook is still trading under the ticker \\texttt{FB}" in introduction
    assert "The failure is not merely a stale fact in the final answer" in introduction
    assert "choosing the wrong first move" in introduction
    assert "selecting \\texttt{answer} when \\texttt{challenge} is required" in introduction


def test_introduction_defuses_dataset_mixture_objection() -> None:
    introduction = _section("01_introduction.tex")

    assert "not another defect category, but the action decision that precedes generation" in introduction
    assert "shared action-decision record and action ontology" in introduction
    assert "the slice source is secondary to the first-move label being evaluated" in introduction


def test_related_work_handoff_names_one_policy_problem() -> None:
    related_work = _section("02_related_work.tex")

    assert "one assistant policy problem" in related_work
    assert "before it can safely generate the final text" in related_work
