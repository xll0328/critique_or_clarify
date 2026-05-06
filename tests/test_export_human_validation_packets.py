from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


def test_export_human_validation_packets_writes_index_and_example_context(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_human_validation_packets.py"
    queue_path = tmp_path / "queue.csv"
    split_path = tmp_path / "split.jsonl"
    output_dir = tmp_path / "packets"
    with queue_path.open("w", encoding="utf-8", newline="") as handle:
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
                "status": "pending",
                "priority": "high",
                "validation_type": "example_gold_label",
                "source_artifact": "split.jsonl",
                "example_id": "example-1",
                "slice": "stale_premise",
                "gold_action": "challenge",
                "check_question": "Check the label.",
                "ai_prefill": "gold_action=challenge",
                "human_decision": "",
                "human_notes": "",
            }
        )
        writer.writerow(
            {
                "queue_id": "HV-CL-001",
                "status": "pending",
                "priority": "medium",
                "validation_type": "metric_claim",
                "source_artifact": "metrics.json",
                "check_question": "Check the metric.",
                "ai_prefill": "action_accuracy=1",
                "human_decision": "accept",
                "human_notes": "",
            }
        )
    write_jsonl(
        split_path,
        [
            {
                "id": "example-1",
                "source": "unit",
                "prompt": "Why is the old name still used?",
                "passages": ["Update: the new name is active."],
                "gold_action": "challenge",
                "gold_response": "The premise is outdated.",
                "metadata": {
                    "slice": "stale_premise",
                    "stale_claim": "Old name is still used.",
                    "corrected_fact": "New name is active.",
                    "source_url": "https://example.test/source",
                },
            }
        ],
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--queue",
            str(queue_path),
            "--split",
            str(split_path),
            "--output-dir",
            str(output_dir),
            "--batch-size",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    index = (output_dir / "index.md").read_text(encoding="utf-8")
    packet = (output_dir / "batch_001.md").read_text(encoding="utf-8")
    assert "Pending rows exported: `1`." in index
    assert "HV-EX-001" in packet
    assert "Corrected fact: New name is active." in packet
    assert "Record final decisions in the CSV" in packet
    assert not (output_dir / "batch_002.md").exists()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
