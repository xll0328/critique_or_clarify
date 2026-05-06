from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_build_day1_model_report_emits_filled_markdown(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_model_report.py"
    quick_path = tmp_path / "qwen25_15b_day1_quick_metrics.json"
    dev_path = tmp_path / "qwen25_15b_day1_dev_metrics.json"
    failures_path = tmp_path / "qwen25_15b_day1_dev_failures.txt"
    output_path = tmp_path / "qwen25_15b_day1_report.md"

    quick_path.write_text(json.dumps({"summary": build_summary(36, -0.31, 0.44, 0.03, 0.72, 0.20, 0.75)}), encoding="utf-8")
    dev_path.write_text(json.dumps({"summary": build_summary(120, -0.29, 0.51, 0.04, 0.61, 0.12, 0.84)}), encoding="utf-8")
    failures_path.write_text(
        "\n".join(
            [
                "## false_premise (3 failures)",
                json.dumps({"id": "fp-1", "gold_action": "challenge", "pred_action": "answer"}),
                "## conflicting_evidence (2 failures)",
                json.dumps({"id": "ce-1", "gold_action": "answer", "pred_action": "answer"}),
                json.dumps({"id": "ce-2", "gold_action": "answer", "pred_action": "abstain"}),
                "## answerable_control (4 failures)",
                json.dumps({"id": "ac-1", "gold_action": "answer", "pred_action": "abstain"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--quick-metrics",
            str(quick_path),
            "--dev-metrics",
            str(dev_path),
            "--dev-failures",
            str(failures_path),
            "--output",
            str(output_path),
            "--date",
            "2026-04-24",
            "--model-id",
            "Qwen/Qwen2.5-1.5B-Instruct",
            "--local-snapshot",
            "/tmp/model",
            "--gpu",
            "CUDA_VISIBLE_DEVICES=2",
            "--max-new-tokens",
            "140",
            "--temperature",
            "0.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "# Qwen2.5-1.5B-Instruct on Day-1" in text
    assert "## Run Metadata" in text
    assert "`day1_quick`" in text
    assert "`day1_dev`" in text
    assert "## Per-Slice Metrics on `day1_dev`" in text
    assert "## Representative Failures" in text
    assert "`false_premise`" in text
    assert "`fp-1`" in text
    assert "predicted `answer` instead of `answer`" not in text
    assert "`ce-2`" in text


def build_summary(
    num_examples: int,
    avg_utility: float,
    action_accuracy: float,
    answer_em: float,
    answer_contains_rate: float,
    over_answer_rate: float,
    json_parse_rate: float,
) -> dict:
    return {
        "num_examples": num_examples,
        "action_accuracy": action_accuracy,
        "answer_em": answer_em,
        "answer_contains_rate": answer_contains_rate,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "gold_action_counts": {"answer": num_examples // 2, "challenge": num_examples // 2},
        "pred_action_counts": {"answer": num_examples // 2, "abstain": num_examples // 2},
        "parsed_as_counts": {"json": int(num_examples * json_parse_rate), "fallback": num_examples},
        "json_parse_rate": json_parse_rate,
        "confusion": {
            "answer": {"answer": num_examples // 3, "abstain": num_examples // 6},
            "challenge": {"answer": num_examples // 6, "challenge": num_examples // 3},
        },
        "per_slice": {
            "false_premise": {
                "count": num_examples // 3,
                "action_accuracy": 0.3,
                "avg_utility": -0.2,
                "answer_em": 0.0,
                "answer_contains_rate": 0.0,
                "over_answer_rate": 0.25,
                "json_parse_rate": json_parse_rate,
            },
            "conflicting_evidence": {
                "count": num_examples // 3,
                "action_accuracy": 0.7,
                "avg_utility": -0.1,
                "answer_em": 0.0,
                "answer_contains_rate": 0.6,
                "over_answer_rate": 0.0,
                "json_parse_rate": json_parse_rate,
            },
            "answerable_control": {
                "count": num_examples // 3,
                "action_accuracy": 0.4,
                "avg_utility": -0.3,
                "answer_em": answer_em,
                "answer_contains_rate": answer_contains_rate,
                "over_answer_rate": 0.0,
                "json_parse_rate": json_parse_rate,
            },
        },
        "details": [],
    }
