from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_scale_reasoning_bootstrap_emits_md_and_tex(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_scale_reasoning_bootstrap.py"
    first = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    second = tmp_path / "qwen25_coder_7b_day1_dev_metrics.json"
    output_dir = tmp_path / "tables"
    markdown_path = tmp_path / "day1_scale_reasoning_ci.md"

    first.write_text(json.dumps(build_payload(offset=0)), encoding="utf-8")
    second.write_text(json.dumps(build_payload(offset=1)), encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(first),
            str(second),
            "--samples",
            "200",
            "--seed",
            "13",
            "--output-md",
            str(markdown_path),
            "--output-dir",
            str(output_dir),
            "--prefix",
            "day1_scale_reasoning_ci",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    markdown = markdown_path.read_text(encoding="utf-8")
    main_tex = (output_dir / "day1_scale_reasoning_ci_main.tex").read_text(encoding="utf-8")
    slice_tex = (output_dir / "day1_scale_reasoning_ci_per_slice.tex").read_text(encoding="utf-8")

    assert "Bootstrap 95% percentile intervals" in markdown
    assert "Qwen2.5-Coder-7B-Instruct" in markdown
    assert "0.5 [" in markdown
    assert "False Premise" in markdown
    assert r"Utility (95\% CI)" in main_tex
    assert "Qwen2.5-0.5B-Instruct" in main_tex
    assert r"Per-slice bootstrap 95\% percentile intervals" in slice_tex


def build_payload(*, offset: int) -> dict:
    details = []
    for index in range(4):
        details.append(
            {
                "id": f"answer-{offset}-{index}",
                "slice": "answerable_control",
                "gold_action": "answer",
                "pred_action": "answer",
                "action_correct": True,
                "utility": -0.1 * (offset + 1),
            }
        )
    for index in range(2):
        details.append(
            {
                "id": f"false-{offset}-{index}",
                "slice": "false_premise",
                "gold_action": "challenge",
                "pred_action": "challenge" if offset else "ask",
                "action_correct": bool(offset),
                "utility": 0.0 if offset else -0.25,
            }
        )
    for index in range(2):
        details.append(
            {
                "id": f"conflict-{offset}-{index}",
                "slice": "conflicting_evidence",
                "gold_action": "answer",
                "pred_action": "answer" if offset else "abstain",
                "action_correct": bool(offset),
                "utility": -0.2 if offset else -0.5,
            }
        )
    return {
        "summary": {
            "num_examples": len(details),
            "action_accuracy": 0.75 if offset else 0.5,
            "answer_em": 0.0,
            "answer_contains_rate": 0.0,
            "avg_utility": -0.1 if offset else -0.2375,
            "over_answer_rate": 0.0,
            "json_parse_rate": 1.0,
            "pred_action_counts": {"answer": 6, "ask": 2 if not offset else 0, "challenge": 2 if offset else 0, "abstain": 2 if not offset else 0},
            "confusion": {
                "answer": {"answer": 4, "abstain": 2 if not offset else 0},
                "challenge": {"ask": 2 if not offset else 0, "challenge": 2 if offset else 0},
            },
            "per_slice": {
                "answerable_control": {"avg_utility": -0.1 * (offset + 1), "action_accuracy": 1.0},
                "false_premise": {"avg_utility": 0.0 if offset else -0.25, "action_accuracy": 1.0 if offset else 0.0},
                "conflicting_evidence": {"avg_utility": -0.2 if offset else -0.5, "action_accuracy": 1.0 if offset else 0.0},
            },
        },
        "details": details,
    }
