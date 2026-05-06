from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_scale_reasoning_tables_emits_tex_snippets(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_scale_reasoning_tables.py"
    first = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    second = tmp_path / "qwen25_coder_7b_day1_dev_metrics.json"
    output_dir = tmp_path / "tables"

    first.write_text(
        json.dumps({"summary": build_summary(avg_utility=-0.4, action_accuracy=0.35, over_answer_rate=0.08)}),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"summary": build_summary(avg_utility=-0.2, action_accuracy=0.6, over_answer_rate=0.01)}),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(first),
            str(second),
            "--output-dir",
            str(output_dir),
            "--prefix",
            "day1_scale_reasoning",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    main_tex = (output_dir / "day1_scale_reasoning_main.tex").read_text(encoding="utf-8")
    slice_tex = (output_dir / "day1_scale_reasoning_per_slice.tex").read_text(encoding="utf-8")

    assert r"\begin{table*}[t]" in main_tex
    assert "Qwen2.5-Coder-7B-Instruct" in main_tex
    assert r"\textbf{0.6}" in main_tex
    assert r"\textbf{0.01}" in main_tex
    assert "False Premise" in slice_tex
    assert "utility / action-accuracy" in slice_tex


def build_summary(*, avg_utility: float, action_accuracy: float, over_answer_rate: float) -> dict:
    return {
        "num_examples": 12,
        "action_accuracy": action_accuracy,
        "answer_em": 0.25,
        "answer_contains_rate": 0.5,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "json_parse_rate": 0.9,
        "pred_action_counts": {"answer": 5, "ask": 2, "challenge": 2, "abstain": 3},
        "confusion": {
            "answer": {"answer": 4, "ask": 1},
            "ask": {"ask": 1},
            "challenge": {"challenge": 2},
            "abstain": {"abstain": 3},
        },
        "per_slice": {
            "answerable_control": {"avg_utility": -0.4, "action_accuracy": 0.5},
            "false_premise": {"avg_utility": -0.3, "action_accuracy": 0.2},
            "conflicting_evidence": {"avg_utility": -0.1, "action_accuracy": 0.7},
        },
    }
