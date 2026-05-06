from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_plot_emnlp2026_figure6_uses_bootstrap_ci_artifact(tmp_path: Path) -> None:
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "plot_emnlp2026_figure6_api_baseline_comparison.py"
    )
    metric_path = tmp_path / "aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json"
    ci_path = tmp_path / "day1_scale_reasoning_api_ci.md"
    output_prefix = tmp_path / "figure6_api_baseline_comparison"

    metric_path.write_text(json.dumps(build_metric_payload()), encoding="utf-8")
    ci_path.write_text(
        "\n".join(
            [
                "# Day-1 Bootstrap Confidence Intervals",
                "",
                "## Main Table",
                "",
                "| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | n |",
                "| --- | --- | --- | --- | --- |",
                "| qwen-turbo | 0.1 [0.05, 0.14] | 0.75 [0.65, 0.85] | 0.25 [0.15, 0.35] | 4 |",
                "",
                "## Per-Slice Action Accuracy",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--metric-paths",
            str(metric_path),
            "--ci-md",
            str(ci_path),
            "--output-prefix",
            str(output_prefix),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output_prefix.with_suffix(".png").exists()
    assert output_prefix.with_suffix(".png").stat().st_size > 1000
    assert output_prefix.with_suffix(".pdf").exists()
    assert output_prefix.with_suffix(".pdf").stat().st_size > 1000

    module = load_module(script_path)
    intervals = module.load_ci_intervals(ci_path)
    assert intervals["qwen-turbo"]["action_accuracy"] == (0.75, 0.65, 0.85)
    over_answer_errors = module.errorbar_arrays(
        {"qwen-turbo": {"ci": intervals["qwen-turbo"]}},
        ["qwen-turbo"],
        "over_answer",
    )
    assert over_answer_errors[0] == pytest.approx([0.1])
    assert over_answer_errors[1] == pytest.approx([0.1])


def load_module(script_path: Path):
    spec = importlib.util.spec_from_file_location("figure6_api_baseline", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_metric_payload() -> dict:
    return {
        "summary": {
            "num_examples": 4,
            "action_accuracy": 0.75,
            "answer_em": 0.0,
            "answer_contains_rate": 0.5,
            "avg_utility": 0.1,
            "over_answer_rate": 0.25,
            "json_parse_rate": 0.8,
            "pred_action_counts": {
                "answer": 2,
                "ask": 1,
                "challenge": 1,
                "abstain": 0,
            },
        }
    }
