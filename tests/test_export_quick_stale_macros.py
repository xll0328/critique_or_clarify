from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_quick_stale_macros_emits_paper_numbers(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_quick_stale_macros.py"
    output_path = tmp_path / "day1_quick_stale_macros.tex"
    paths = [
        tmp_path / "qwen25_15b_day1_quick_plus_stale_grounded_metrics.json",
        tmp_path / "qwen25_coder_7b_day1_quick_plus_stale_grounded_metrics.json",
        tmp_path / "deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json",
    ]

    paths[0].write_text(json.dumps({"summary": build_summary(0.775, -0.2188, 0.05, 0.75, 0.25)}), encoding="utf-8")
    paths[1].write_text(json.dumps({"summary": build_summary(0.625, -0.2437, 0.025, 1.0, 0.0)}), encoding="utf-8")
    paths[2].write_text(json.dumps({"summary": build_summary(0.45, -0.475, 0.15, 0.25, 0.75)}), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            *[str(path) for path in paths],
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert r"\newcommand{\DayOneQuickStaleDeepSeekSevenBActionAcc}{0.45}" in text
    assert r"\newcommand{\DayOneQuickStaleDeepSeekSevenBUtility}{-0.475}" in text
    assert r"\newcommand{\DayOneQuickStaleDeepSeekSevenBStalePremiseAcc}{0.25}" in text
    assert r"\newcommand{\DayOneQuickStaleDeepSeekSevenBStalePremiseOverAnswer}{0.75}" in text
    assert r"\newcommand{\DayOneQuickStaleQwenOnePointFiveBUtility}{-0.2188}" in text
    assert r"\newcommand{\DayOneQuickStaleBestInstructModel}{Qwen2.5-1.5B-Instruct}" in text
    assert r"\newcommand{\DayOneQuickStaleDeepSeekSevenBDeltaVsQwenOnePointFiveBUtility}{-0.2562}" in text


def build_summary(
    action_accuracy: float,
    avg_utility: float,
    over_answer_rate: float,
    stale_action_accuracy: float,
    stale_over_answer_rate: float,
) -> dict:
    return {
        "num_examples": 40,
        "action_accuracy": action_accuracy,
        "answer_em": 0.0,
        "answer_contains_rate": 0.0,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "json_parse_rate": 0.5,
        "pred_action_counts": {"answer": 10, "ask": 0, "challenge": 10, "abstain": 20},
        "confusion": {
            "answer": {"answer": 10},
            "ask": {},
            "challenge": {"challenge": 10},
            "abstain": {},
        },
        "per_slice": {
            "answerable_control": {"action_accuracy": 0.5, "over_answer_rate": 0.0},
            "false_premise": {"action_accuracy": 0.5, "over_answer_rate": 0.25},
            "stale_premise": {
                "action_accuracy": stale_action_accuracy,
                "over_answer_rate": stale_over_answer_rate,
            },
            "conflicting_evidence": {"action_accuracy": 1.0, "over_answer_rate": 0.0},
        },
    }
