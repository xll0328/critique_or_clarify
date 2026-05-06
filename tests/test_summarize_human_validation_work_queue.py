from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_summarize_human_validation_work_queue_reports_progress(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "summarize_human_validation_work_queue.py"
    queue_path = tmp_path / "queue.csv"
    output_path = tmp_path / "summary.md"
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
                "human_decision": "accept",
            }
        )
        writer.writerow(
            {
                "queue_id": "HV-CL-001",
                "status": "pending",
                "priority": "medium",
                "validation_type": "metric_claim",
                "human_decision": "",
            }
        )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--queue",
            str(queue_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "Active work queue: `1 / 2` rows completed." in text
    assert "| example_gold_label | 1 |" in text
    assert "Invalid non-empty `human_decision` labels: `0`." in text
