from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_compare_runs_renders_markdown_report(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    first = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    second = tmp_path / "qwen25_coder_7b_day1_dev_metrics.json"
    output_path = tmp_path / "comparison.md"

    first.write_text(json.dumps({"summary": build_summary(avg_utility=-0.4)}), encoding="utf-8")
    second.write_text(
        json.dumps(
            {
                "summary": build_summary(
                    avg_utility=-0.2,
                    per_slice={
                        "answerable_control": {"avg_utility": -0.3, "action_accuracy": 0.4},
                        "false_premise": {"avg_utility": 0.1, "action_accuracy": 0.6},
                        "conflicting_evidence": {"avg_utility": -0.5, "action_accuracy": 1.0},
                    },
                    pred_action_counts={"answer": 6, "challenge": 2, "abstain": 4},
                    confusion={
                        "answer": {"answer": 5, "abstain": 3},
                        "challenge": {"challenge": 2, "answer": 1, "abstain": 1},
                    },
                )
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(first),
            str(second),
            "--title",
            "Day-1 Baseline Comparison",
            "--output",
            str(output_path),
            "--confusion-for",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    assert "# Day-1 Baseline Comparison" in stdout
    assert "## Main Table" in stdout
    assert "## Per-Slice Table" in stdout
    assert "Answerable" in stdout
    assert "False Premise" in stdout
    assert "Conflicting Evidence" in stdout
    assert "## Confusion Tables" in stdout
    assert "| Gold \\\\ Pred | answer | ask | challenge | abstain |" in stdout
    assert output_path.read_text(encoding="utf-8").startswith("# Day-1 Baseline Comparison")


def test_compare_runs_recognizes_qwen_15b_label(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    metrics_path = tmp_path / "qwen25_15b_day1_dev_metrics.json"
    metrics_path.write_text(json.dumps({"summary": build_summary(avg_utility=-0.3)}), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(script_path), str(metrics_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Qwen2.5-1.5B-Instruct" in completed.stdout


def test_compare_runs_recognizes_deepseek_7b_label(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    metrics_path = tmp_path / "deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json"
    metrics_path.write_text(json.dumps({"summary": build_summary(avg_utility=-0.3)}), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(script_path), str(metrics_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "DeepSeek-R1-Distill-Qwen-7B" in completed.stdout


def build_summary(
    *,
    avg_utility: float,
    per_slice: dict[str, dict[str, float]] | None = None,
    pred_action_counts: dict[str, int] | None = None,
    confusion: dict[str, dict[str, int]] | None = None,
) -> dict:
    return {
        "num_examples": 12,
        "action_accuracy": 0.5,
        "answer_em": 0.25,
        "answer_contains_rate": 0.5,
        "avg_utility": avg_utility,
        "over_answer_rate": 0.0833,
        "json_parse_rate": 0.9,
        "pred_action_counts": pred_action_counts or {"answer": 5, "ask": 2, "abstain": 5},
        "confusion": confusion
        or {
            "answer": {"answer": 4, "ask": 1, "abstain": 3},
            "challenge": {"ask": 1, "abstain": 3},
        },
        "per_slice": per_slice
        or {
            "answerable_control": {"avg_utility": -0.4, "action_accuracy": 0.5},
            "false_premise": {"avg_utility": -0.3, "action_accuracy": 0.2},
        },
    }
