from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_baseline_batch_runs_two_heuristic_jobs(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_baseline_batch.py"
    first_data = tmp_path / "first.jsonl"
    second_data = tmp_path / "second.jsonl"
    first_output = tmp_path / "first_predictions.jsonl"
    second_output = tmp_path / "second_predictions.jsonl"
    first_metrics = tmp_path / "first_metrics.json"
    second_metrics = tmp_path / "second_metrics.json"

    first_data.write_text(json.dumps(build_example("first", "answer")) + "\n", encoding="utf-8")
    second_data.write_text(json.dumps(build_example("second", "challenge", has_false_premise=True)) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--backend",
            "heuristic",
            "--job",
            f"{first_data}={first_output}={first_metrics}",
            "--job",
            f"{second_data}={second_output}={second_metrics}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Starting job 1/2" in completed.stdout
    assert "Starting job 2/2" in completed.stdout
    assert json.loads(first_output.read_text(encoding="utf-8").splitlines()[0])["action"] == "answer"
    assert json.loads(second_output.read_text(encoding="utf-8").splitlines()[0])["action"] == "challenge"
    assert json.loads(first_metrics.read_text(encoding="utf-8"))["summary"]["action_accuracy"] == 1.0
    assert json.loads(second_metrics.read_text(encoding="utf-8"))["summary"]["action_accuracy"] == 1.0


def build_example(example_id: str, action: str, *, has_false_premise: bool = False) -> dict:
    return {
        "id": example_id,
        "source": "unit",
        "prompt": "Prompt",
        "passages": [],
        "gold_action": action,
        "gold_answer": "Answer" if action == "answer" else "",
        "gold_response": "Challenge" if action == "challenge" else "",
        "metadata": {
            "slice": "false_premise" if has_false_premise else "answerable_control",
            "has_false_premise": has_false_premise,
        },
    }
