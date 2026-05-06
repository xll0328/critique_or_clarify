from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "promote_codex_review_to_human_decisions.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("promote_codex_review_to_human_decisions", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_promote_rows_copies_codex_decision_with_reviewer_note() -> None:
    module = load_module()
    rows = [
        {
            "queue_id": "HV-001",
            "status": "pending",
            "human_decision": "",
            "human_notes": "",
        }
    ]
    reviews = {
        "HV-001": {
            "queue_id": "HV-001",
            "codex_expert_decision": "accept",
            "codex_expert_notes": "Looks correct.",
        }
    }

    updated, skipped = module.promote_rows(rows, reviews, reviewer="PI")

    assert updated == 1
    assert skipped == 0
    assert rows[0]["status"] == "completed"
    assert rows[0]["human_decision"] == "accept"
    assert "Human reviewer PI signed off" in rows[0]["human_notes"]
    assert "Looks correct." in rows[0]["human_notes"]


def test_promote_rows_preserves_existing_decision_without_overwrite() -> None:
    module = load_module()
    rows = [
        {
            "queue_id": "HV-001",
            "status": "completed",
            "human_decision": "reject",
            "human_notes": "Manual rejection.",
        }
    ]
    reviews = {
        "HV-001": {
            "queue_id": "HV-001",
            "codex_expert_decision": "accept",
            "codex_expert_notes": "Looks correct.",
        }
    }

    updated, skipped = module.promote_rows(rows, reviews, reviewer="PI")

    assert updated == 0
    assert skipped == 1
    assert rows[0]["human_decision"] == "reject"
    assert rows[0]["human_notes"] == "Manual rejection."


def test_promote_rows_accepts_multipass_consensus_review() -> None:
    module = load_module()
    rows = [
        {
            "queue_id": "HV-001",
            "status": "pending",
            "human_decision": "",
            "human_notes": "",
        }
    ]
    reviews = {
        "HV-001": {
            "queue_id": "HV-001",
            "multipass_consensus_decision": "accept",
            "multipass_consensus_notes": "All six passes accepted this row.",
        }
    }

    updated, skipped = module.promote_rows(rows, reviews, reviewer="PI")

    assert updated == 1
    assert skipped == 0
    assert rows[0]["human_decision"] == "accept"
    assert "All six passes accepted this row." in rows[0]["human_notes"]
