from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


def test_validation_summary_counts_completed_and_invalid_decisions(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_integrity_dashboard.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("build_day1_integrity_dashboard", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    queue_path = tmp_path / "queue.csv"
    with queue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["queue_id", "human_decision"])
        writer.writeheader()
        writer.writerow({"queue_id": "HV-001", "human_decision": "accept"})
        writer.writerow({"queue_id": "HV-002", "human_decision": "bad_label"})
        writer.writerow({"queue_id": "HV-003", "human_decision": ""})

    assert module.validation_summary(queue_path) == {
        "total": 3,
        "completed": 2,
        "pending": 1,
        "invalid_decisions": 1,
    }


def test_codex_review_summary_counts_accepts(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_integrity_dashboard.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("build_day1_integrity_dashboard", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    review_path = tmp_path / "codex_review.csv"
    with review_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["queue_id", "codex_expert_decision"])
        writer.writeheader()
        writer.writerow({"queue_id": "HV-001", "codex_expert_decision": "accept"})
        writer.writerow({"queue_id": "HV-002", "codex_expert_decision": "needs_second_pass"})

    assert module.codex_review_summary(review_path) == {"total": 2, "accepted": 1}


def test_multipass_review_summary_counts_consensus_accepts(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_day1_integrity_dashboard.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("build_day1_integrity_dashboard", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    review_path = tmp_path / "multipass.csv"
    with review_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["queue_id", "multipass_consensus_decision"])
        writer.writeheader()
        writer.writerow({"queue_id": "HV-001", "multipass_consensus_decision": "accept"})
        writer.writerow({"queue_id": "HV-002", "multipass_consensus_decision": "needs_second_pass"})

    assert module.multipass_review_summary(review_path) == {"total": 2, "accepted": 1}
