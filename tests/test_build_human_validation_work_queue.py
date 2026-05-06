from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


def test_build_human_validation_work_queue_emits_pending_example_rows(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_human_validation_work_queue.py"
    split_path = tmp_path / "split.jsonl"
    output_path = tmp_path / "queue.csv"
    write_jsonl(
        split_path,
        [
            {
                "id": "example-answer",
                "source": "unit",
                "prompt": "Who wrote the answer?",
                "gold_action": "answer",
                "gold_answer": "Ada",
                "metadata": {"slice": "answerable_control"},
            },
            {
                "id": "example-stale",
                "source": "unit",
                "prompt": "Why is the old name still used?",
                "gold_action": "challenge",
                "gold_response": "The premise is outdated.",
                "metadata": {"slice": "stale_premise", "source_url": "https://example.test/source"},
            },
        ],
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--split",
            str(split_path),
            "--skip-claims",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = list(csv.DictReader(output_path.open(encoding="utf-8")))
    assert [row["queue_id"] for row in rows] == ["HV-EX-001", "HV-EX-002"]
    assert {row["status"] for row in rows} == {"pending"}
    assert rows[0]["validation_type"] == "example_gold_label"
    assert rows[1]["priority"] == "high"
    assert rows[1]["human_decision"] == ""
    assert "source_url=https://example.test/source" in rows[1]["ai_prefill"]


def test_build_human_validation_work_queue_preserves_existing_decisions(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_human_validation_work_queue.py"
    split_path = tmp_path / "split.jsonl"
    output_path = tmp_path / "queue.csv"
    write_jsonl(
        split_path,
        [
            {
                "id": "example-answer",
                "source": "unit",
                "prompt": "Who wrote the answer?",
                "gold_action": "answer",
                "gold_answer": "Ada",
                "metadata": {"slice": "answerable_control"},
            },
        ],
    )
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "queue_id",
                "status",
                "priority",
                "validation_type",
                "source_artifact",
                "example_id",
                "slice",
                "model",
                "gold_action",
                "pred_action",
                "check_question",
                "ai_prefill",
                "human_decision",
                "human_notes",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "queue_id": "HV-EX-001",
                "status": "reviewed",
                "human_decision": "accept",
                "human_notes": "Checked by reviewer A.",
            }
        )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--split",
            str(split_path),
            "--skip-claims",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = list(csv.DictReader(output_path.open(encoding="utf-8")))
    assert rows[0]["status"] == "reviewed"
    assert rows[0]["human_decision"] == "accept"
    assert rows[0]["human_notes"] == "Checked by reviewer A."


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
