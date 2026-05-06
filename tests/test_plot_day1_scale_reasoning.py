from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_plot_day1_scale_reasoning_emits_png_and_csvs(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "plot_day1_scale_reasoning.py"
    first = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    second = tmp_path / "deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json"
    output_prefix = tmp_path / "figures" / "day1_scale_reasoning"

    first.write_text(
        json.dumps({"summary": build_summary(avg_utility=-0.4, action_accuracy=0.35)}),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"summary": build_summary(avg_utility=-0.5, action_accuracy=0.38)}),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(first),
            str(second),
            "--title",
            "Day-1 Scale And Reasoning Snapshot",
            "--output-prefix",
            str(output_prefix),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    overall_csv = output_prefix.with_name(output_prefix.name + "_overall.csv")
    slice_csv = output_prefix.with_name(output_prefix.name + "_per_slice.csv")
    figure_path = output_prefix.with_suffix(".png")

    assert overall_csv.exists()
    assert slice_csv.exists()
    assert figure_path.exists()
    assert figure_path.stat().st_size > 0
    assert "Qwen2.5-0.5B-Instruct" in overall_csv.read_text(encoding="utf-8")
    assert "DeepSeek-R1-Distill-Qwen-1.5B" in overall_csv.read_text(encoding="utf-8")
    assert "False Premise" in slice_csv.read_text(encoding="utf-8")


def build_summary(*, avg_utility: float, action_accuracy: float) -> dict:
    return {
        "num_examples": 12,
        "action_accuracy": action_accuracy,
        "answer_em": 0.25,
        "answer_contains_rate": 0.5,
        "avg_utility": avg_utility,
        "over_answer_rate": 0.0833,
        "json_parse_rate": 0.9,
        "pred_action_counts": {"answer": 5, "ask": 2, "abstain": 5},
        "confusion": {
            "answer": {"answer": 4, "ask": 1, "abstain": 3},
            "challenge": {"ask": 1, "abstain": 3},
        },
        "per_slice": {
            "answerable_control": {"avg_utility": -0.4, "action_accuracy": 0.5},
            "false_premise": {"avg_utility": -0.3, "action_accuracy": 0.2},
            "conflicting_evidence": {"avg_utility": -0.1, "action_accuracy": 0.7},
        },
    }
