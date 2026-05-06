from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_build_stale_pool_pilot_report_emits_matched_contrast(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_stale_pool_pilot_report.py"
    qwen_path = tmp_path / "qwen25_15b_day1_quick_plus_stale_pool_metrics.json"
    qwen_small_path = tmp_path / "qwen25_05b_day1_quick_plus_stale_pool_metrics.json"
    deepseek_path = tmp_path / "deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json"
    output_path = tmp_path / "pilot.md"
    output_dir = tmp_path / "tables"

    qwen_small_path.write_text(
        json.dumps(
            {
                "summary": build_summary(-0.63, 0.31, 0.37, 0.02, 0.0, -0.85, 0.8),
                "details": build_details(stale_correct=False, stale_pred_action="answer"),
            }
        ),
        encoding="utf-8",
    )
    qwen_path.write_text(
        json.dumps(
            {
                "summary": build_summary(-0.18, 0.72, 0.11, 0.86, 0.73, 0.10, 0.27),
                "details": build_details(stale_correct=True, stale_pred_action="challenge"),
            }
        ),
        encoding="utf-8",
    )
    deepseek_path.write_text(
        json.dumps(
            {
                "summary": build_summary(-0.40, 0.22, 0.14, 0.0, 0.27, -0.30, 0.33),
                "details": build_details(stale_correct=False, stale_pred_action="ask"),
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(qwen_small_path),
            str(qwen_path),
            str(deepseek_path),
            "--output",
            str(output_path),
            "--output-dir",
            str(output_dir),
            "--samples",
            "10",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "# Expanded Stale-Premise Pool Pilot" in text
    assert "Qwen2.5-1.5B-Instruct" in text
    assert "DeepSeek-R1-Distill-Qwen-1.5B" in text
    assert "Qwen Scale Signal" in text
    assert "Bootstrap 95% CIs" in text
    assert "Matched 1.5B Contrast" in text
    assert "scale-sensitive diagnostic" in text
    assert "reasoning traces do not by themselves" in text
    tex = (output_dir / "day1_expanded_stale_pool_pilot_main.tex").read_text(encoding="utf-8")
    assert r"Stale Acc. (95\% CI)" in tex
    assert r"\label{tab:day1-expanded-stale-pool-pilot}" in tex


def build_summary(
    avg_utility: float,
    action_accuracy: float,
    over_answer_rate: float,
    json_parse_rate: float,
    stale_accuracy: float,
    stale_utility: float,
    stale_over_answer: float,
) -> dict:
    return {
        "num_examples": 51,
        "action_accuracy": action_accuracy,
        "answer_em": 0.0,
        "answer_contains_rate": 0.0,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "json_parse_rate": json_parse_rate,
        "pred_action_counts": {"answer": 1},
        "confusion": {},
        "per_slice": {
            "answerable_control": {"count": 12, "avg_utility": -0.5, "action_accuracy": 0.3},
            "false_premise": {"count": 12, "avg_utility": 0.1, "action_accuracy": 0.7},
            "stale_premise": {
                "count": 15,
                "avg_utility": stale_utility,
                "action_accuracy": stale_accuracy,
                "over_answer_rate": stale_over_answer,
            },
            "conflicting_evidence": {"count": 12, "avg_utility": -0.5, "action_accuracy": 1.0},
        },
        "details": [],
    }


def build_details(*, stale_correct: bool, stale_pred_action: str) -> list[dict]:
    return [
        {
            "id": "answerable-1",
            "slice": "answerable_control",
            "gold_action": "answer",
            "pred_action": "answer",
            "action_correct": True,
            "utility": -0.5,
        },
        {
            "id": "stale-1",
            "slice": "stale_premise",
            "gold_action": "challenge",
            "pred_action": stale_pred_action,
            "action_correct": stale_correct,
            "utility": 0.5 if stale_correct else -1.0,
        },
    ]
