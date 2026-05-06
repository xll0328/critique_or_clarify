from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_scale_reasoning_macros_emits_stable_latex_commands(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_scale_reasoning_macros.py"
    output_path = tmp_path / "day1_scale_reasoning_macros.tex"
    paths = [
        tmp_path / "qwen25_05b_day1_dev_metrics.json",
        tmp_path / "qwen25_15b_day1_dev_metrics.json",
        tmp_path / "deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json",
        tmp_path / "qwen25_coder_7b_day1_dev_metrics.json",
    ]

    paths[0].write_text(json.dumps({"summary": build_summary(-0.44, 0.35, 0.08, 0.07, 0.10)}), encoding="utf-8")
    paths[1].write_text(json.dumps({"summary": build_summary(-0.33, 0.46, 0.05, 0.76, 0.32)}), encoding="utf-8")
    paths[2].write_text(json.dumps({"summary": build_summary(-0.51, 0.38, 0.15, 0.01, 0.05)}), encoding="utf-8")
    paths[3].write_text(json.dumps({"summary": build_summary(-0.28, 0.60, 0.01, 0.94, 0.45)}), encoding="utf-8")

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
    assert r"\newcommand{\DayOneScaleReasoningFrontierModel}{Qwen2.5-Coder-7B-Instruct}" in text
    assert r"\newcommand{\DayOneScaleReasoningStrongestInstructStepStatus}{available}" in text
    assert r"\newcommand{\DayOneScaleReasoningStrongestInstructStepFrom}{Qwen2.5-1.5B-Instruct}" in text
    assert r"\newcommand{\DayOneScaleReasoningStrongestInstructStepTo}{Qwen2.5-Coder-7B-Instruct}" in text
    assert r"\newcommand{\DayOneScaleReasoningStrongestInstructStepDeltaActionAcc}{+0.14}" in text
    assert r"\newcommand{\DayOneScaleReasoningQwenOnePointFiveBFalsePremiseAcc}{0.32}" in text
    assert r"\newcommand{\DayOneScaleReasoningQwenCoderSevenBActionAcc}{0.6}" in text
    assert r"\newcommand{\DayOneScaleReasoningQwenCoderSevenBUtility}{-0.28}" in text
    assert r"\newcommand{\DayOneScaleReasoningQwenCoderSevenBFalsePremiseAcc}{0.45}" in text
    assert r"\newcommand{\DayOneScaleReasoningMatchedStatus}{available}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedSize}{1.5B}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedInstructModel}{Qwen2.5-1.5B-Instruct}" in text
    assert (
        r"\newcommand{\DayOneScaleReasoningLargestMatchedReasoningModel}{DeepSeek-R1-Distill-Qwen-1.5B}"
        in text
    )
    assert r"\newcommand{\DayOneScaleReasoningBestReasoningActionAcc}{0.38}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedReasoningActionAcc}{0.38}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedReasoningNumExamples}{12}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedReasoningPredAbstainCount}{3}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedReasoningFalsePremiseAcc}{0.05}" in text
    assert r"\newcommand{\DayOneScaleReasoningLargestMatchedDeltaUtility}{-0.18}" in text


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
