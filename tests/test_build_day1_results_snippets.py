from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_build_day1_results_snippets_handles_pending_and_matched_style_cases(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_results_snippets.py"
    output_path = tmp_path / "day1_results_snippets.md"
    pending_paths = [
        tmp_path / "qwen25_05b_day1_dev_metrics.json",
        tmp_path / "deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json",
        tmp_path / "qwen25_coder_7b_day1_dev_metrics.json",
    ]

    pending_paths[0].write_text(json.dumps({"summary": build_summary(-0.44, 0.35, 0.08, 0.07, 0.10)}), encoding="utf-8")
    pending_paths[1].write_text(json.dumps({"summary": build_summary(-0.51, 0.38, 0.15, 0.01, 0.05)}), encoding="utf-8")
    pending_paths[2].write_text(json.dumps({"summary": build_summary(-0.28, 0.60, 0.01, 0.94, 0.45)}), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            *[str(path) for path in pending_paths],
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    pending_text = output_path.read_text(encoding="utf-8")
    assert "# Day-1 Results Snippets" in pending_text
    assert "Results Lead" in pending_text
    assert "Scale Paragraph" in pending_text
    assert "Reasoning Paragraph" in pending_text
    assert "not scale-matched" in pending_text
    assert "Qwen2.5-1.5B-Instruct" in pending_text

    matched_path = tmp_path / "qwen25_15b_day1_dev_metrics.json"
    matched_path.write_text(json.dumps({"summary": build_summary(-0.33, 0.46, 0.05, 0.76, 0.32)}), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(pending_paths[0]),
            str(matched_path),
            str(pending_paths[1]),
            str(pending_paths[2]),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    matched_text = output_path.read_text(encoding="utf-8")
    assert "largest currently available size-matched contrast (`1.5B`)" in matched_text
    assert "DeepSeek-R1-Distill-Qwen-1.5B" in matched_text
    assert "Qwen2.5-1.5B-Instruct" in matched_text


def build_summary(
    avg_utility: float,
    action_accuracy: float,
    over_answer_rate: float,
    json_parse_rate: float,
    false_premise_accuracy: float,
) -> dict:
    return {
        "num_examples": 12,
        "action_accuracy": action_accuracy,
        "answer_em": 0.1,
        "answer_contains_rate": 0.2,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "json_parse_rate": json_parse_rate,
        "pred_action_counts": {"answer": 5, "ask": 2, "challenge": 2, "abstain": 3},
        "confusion": {
            "answer": {"answer": 4, "ask": 1},
            "ask": {"ask": 1},
            "challenge": {"challenge": 2},
            "abstain": {"abstain": 3},
        },
        "per_slice": {
            "answerable_control": {"avg_utility": -0.4, "action_accuracy": 0.35},
            "false_premise": {"avg_utility": -0.3, "action_accuracy": false_premise_accuracy},
            "conflicting_evidence": {"avg_utility": -0.1, "action_accuracy": 0.7},
        },
        "details": [],
    }
