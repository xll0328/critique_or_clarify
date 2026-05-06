from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_build_day1_error_bucket_audit_emits_markdown(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_error_bucket_audit.py"
    data_path = tmp_path / "day1_dev.jsonl"
    prediction_path = tmp_path / "qwen25_05b_day1_dev.jsonl"
    metric_path = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    output_path = tmp_path / "audit.md"

    data_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "a1",
                        "prompt": "What is 2+2?",
                        "passages": [],
                        "gold_action": "answer",
                        "gold_answer": "4",
                        "source": "toy",
                        "metadata": {"slice": "answerable_control"},
                    }
                ),
                json.dumps(
                    {
                        "id": "b1",
                        "prompt": "Why is the false solution correct?",
                        "passages": [],
                        "gold_action": "challenge",
                        "gold_answer": "",
                        "source": "toy",
                        "metadata": {"slice": "false_premise"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    prediction_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "example_id": "a1",
                        "action": "abstain",
                        "response": "I cannot answer.",
                        "raw_output": "I cannot answer.",
                        "metadata": {"parsed_as": "fallback"},
                    }
                ),
                json.dumps(
                    {
                        "example_id": "b1",
                        "action": "answer",
                        "response": "It is correct.",
                        "raw_output": "It is correct.",
                        "metadata": {"parsed_as": "fallback"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    metric_path.write_text(
        json.dumps(
            {
                "summary": {
                    "num_examples": 2,
                    "action_accuracy": 0.0,
                    "answer_em": 0.0,
                    "answer_contains_rate": 0.0,
                    "avg_utility": -0.5,
                    "over_answer_rate": 0.5,
                    "json_parse_rate": 0.0,
                    "pred_action_counts": {"answer": 1, "abstain": 1},
                    "confusion": {"answer": {"abstain": 1}, "challenge": {"answer": 1}},
                    "per_slice": {
                        "answerable_control": {"avg_utility": -0.5, "action_accuracy": 0.0},
                        "false_premise": {"avg_utility": -0.5, "action_accuracy": 0.0},
                    },
                },
                "details": [
                    {
                        "id": "a1",
                        "source": "toy",
                        "slice": "answerable_control",
                        "gold_action": "answer",
                        "pred_action": "abstain",
                        "parsed_as": "fallback",
                        "action_correct": False,
                        "answer_exact_match": None,
                        "answer_contains_match": None,
                        "utility": -0.5,
                    },
                    {
                        "id": "b1",
                        "source": "toy",
                        "slice": "false_premise",
                        "gold_action": "challenge",
                        "pred_action": "answer",
                        "parsed_as": "fallback",
                        "action_correct": False,
                        "answer_exact_match": None,
                        "answer_contains_match": None,
                        "utility": -0.5,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(metric_path),
            "--data",
            str(data_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    audit = output_path.read_text(encoding="utf-8")
    assert "# Day-1 Error Bucket Audit" in audit
    assert "Answerable -> non-answer" in audit
    assert "False premise -> answered" in audit
    assert "fallback=2/2" in audit


def test_build_day1_error_bucket_audit_prefers_more_readable_example(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_error_bucket_audit.py"
    data_path = tmp_path / "day1_dev.jsonl"
    prediction_path = tmp_path / "qwen25_05b_day1_dev.jsonl"
    metric_path = tmp_path / "qwen25_05b_day1_dev_metrics.json"
    output_path = tmp_path / "audit.md"

    data_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "a0",
                        "prompt": (
                            "I am a beginner in mathematics. I will provide you with a math problem and its "
                            "corresponding solution process. Please answer the questions in English."
                        ),
                        "passages": [],
                        "gold_action": "answer",
                        "gold_answer": "4",
                        "source": "pcbench",
                        "metadata": {"slice": "answerable_control"},
                    }
                ),
                json.dumps(
                    {
                        "id": "z9",
                        "prompt": "What is 2+2?",
                        "passages": [],
                        "gold_action": "answer",
                        "gold_answer": "4",
                        "source": "toy",
                        "metadata": {"slice": "answerable_control"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    prediction_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "example_id": "a0",
                        "action": "ask",
                        "response": "Okay, I need to understand which part of the provided solution you want me to explain.",
                        "raw_output": "Okay, I need to understand which part of the provided solution you want me to explain.",
                        "metadata": {"parsed_as": "fallback"},
                    }
                ),
                json.dumps(
                    {
                        "example_id": "z9",
                        "action": "ask",
                        "response": "Could you clarify which step you want explained?",
                        "raw_output": "Could you clarify which step you want explained?",
                        "metadata": {"parsed_as": "fallback"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    metric_path.write_text(
        json.dumps(
            {
                "summary": {
                    "num_examples": 2,
                    "action_accuracy": 0.0,
                    "answer_em": 0.0,
                    "answer_contains_rate": 0.0,
                    "avg_utility": -0.5,
                    "over_answer_rate": 0.0,
                    "json_parse_rate": 0.0,
                    "pred_action_counts": {"ask": 2},
                    "confusion": {"answer": {"ask": 2}},
                    "per_slice": {
                        "answerable_control": {"avg_utility": -0.5, "action_accuracy": 0.0},
                    },
                },
                "details": [
                    {
                        "id": "a0",
                        "source": "pcbench",
                        "slice": "answerable_control",
                        "gold_action": "answer",
                        "pred_action": "ask",
                        "parsed_as": "fallback",
                        "action_correct": False,
                        "answer_exact_match": None,
                        "answer_contains_match": None,
                        "utility": -0.5,
                    },
                    {
                        "id": "z9",
                        "source": "toy",
                        "slice": "answerable_control",
                        "gold_action": "answer",
                        "pred_action": "ask",
                        "parsed_as": "fallback",
                        "action_correct": False,
                        "answer_exact_match": None,
                        "answer_contains_match": None,
                        "utility": -0.5,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(metric_path),
            "--data",
            str(data_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    audit = output_path.read_text(encoding="utf-8")
    assert "Example `z9`" in audit
    assert "Example `a0`" not in audit


def test_build_day1_error_bucket_audit_includes_stale_buckets(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_error_bucket_audit.py"
    data_path = tmp_path / "day1_quick_plus_stale.jsonl"
    prediction_path = tmp_path / "qwen25_15b_day1_quick_plus_stale_grounded.jsonl"
    metric_path = tmp_path / "qwen25_15b_day1_quick_plus_stale_grounded_metrics.json"
    output_path = tmp_path / "audit.md"

    data_path.write_text(
        json.dumps(
            {
                "id": "s1",
                "prompt": "Who is the current president of Atlantis?",
                "passages": [],
                "gold_action": "challenge",
                "gold_answer": "",
                "source": "toy",
                "metadata": {"slice": "stale_premise"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    prediction_path.write_text(
        json.dumps(
            {
                "example_id": "s1",
                "action": "answer",
                "response": "The current president is Alice.",
                "raw_output": "The current president is Alice.",
                "metadata": {"parsed_as": "json"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    metric_path.write_text(
        json.dumps(
            {
                "summary": {
                    "num_examples": 1,
                    "action_accuracy": 0.0,
                    "answer_em": 0.0,
                    "answer_contains_rate": 0.0,
                    "avg_utility": -0.5,
                    "over_answer_rate": 1.0,
                    "json_parse_rate": 1.0,
                    "pred_action_counts": {"answer": 1},
                    "confusion": {"challenge": {"answer": 1}},
                    "per_slice": {
                        "stale_premise": {"avg_utility": -0.5, "action_accuracy": 0.0},
                    },
                },
                "details": [
                    {
                        "id": "s1",
                        "source": "toy",
                        "slice": "stale_premise",
                        "gold_action": "challenge",
                        "pred_action": "answer",
                        "parsed_as": "json",
                        "action_correct": False,
                        "answer_exact_match": None,
                        "answer_contains_match": None,
                        "utility": -0.5,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(metric_path),
            "--data",
            str(data_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    audit = output_path.read_text(encoding="utf-8")
    assert "Stale premise -> answered" in audit
    assert "Example `s1`" in audit
