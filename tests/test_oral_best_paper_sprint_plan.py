from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN = REPO_ROOT / "docs" / "emnlp2026_oral_best_paper_sprint_plan.md"


def test_oral_best_paper_plan_reflects_submission_freeze_lock() -> None:
    text = PLAN.read_text(encoding="utf-8")

    required_fragments = [
        "Date: 2026-05-06",
        "Submission-freeze candidate, not final external submission.",
        "human_validation_queue_ok completed=61/61",
        "DeepSeek-R1-Distill-Qwen-7B metrics are complete",
        "dev action accuracy `0.3667`",
        "quick+stale action accuracy `0.4500`",
        "Final artifact lock passes `./scripts/run_submission_lock_checks.sh`",
        "the full pytest suite",
        "experiments/day1/benchmark_expansion_coverage_audit.md",
        "docs/emnlp2026_oral_best_paper_quality_audit.md",
        "data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl",
        "_assets/emnlp2026_expansion_candidate_validation_queue.csv",
        "experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md",
        "scripts/promote_validated_expansion_candidates.py",
        "docs/emnlp2026_oral_best_paper_sprint_execution_plan.md",
        "docs/emnlp2026_oral_readability_lock.md",
        "submission_lock_checks_ok",
        "The benchmark/evaluation contribution is the lead claim.",
        "The decision-first intervention is promising and scoped to quick+stale behavior",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_oral_best_paper_plan_no_longer_tracks_closed_blockers() -> None:
    text = PLAN.read_text(encoding="utf-8")

    stale_fragments = [
        "`129 passed`",
        "`132 passed`",
        "while the 7B run finishes",
        "Active watcher for the DeepSeek-R1-Distill-Qwen-7B pipeline",
        "7B download/run fails",
        "Related Work and citation verification are still missing",
        "Next: convert these findings into the main Results prose and Figure 2.",
        "tail -f logs/day1/scale_reasoning_watch.log",
        "Ensure no paper claim depends on pending 7B artifacts unless those artifacts have landed.",
    ]

    present = [fragment for fragment in stale_fragments if fragment in text]
    assert present == []


def test_oral_best_paper_plan_uses_final_lock_gate_as_the_required_command() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "## Immediate Next Commands" in text
    assert "./scripts/run_submission_lock_checks.sh" in text
    assert "python scripts/validate_human_validation_queue.py \\" not in text
    assert "./scripts/make_day1_integrity_bundle.sh" not in text
