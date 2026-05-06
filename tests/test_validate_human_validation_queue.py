from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "validate_human_validation_queue.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("validate_human_validation_queue", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validate_rows_accepts_pending_rows_without_require_complete() -> None:
    module = load_module()
    rows = [{"queue_id": "HV-001", "human_decision": "", "human_notes": ""}]

    assert module.validate_rows(rows) == []


def test_validate_rows_flags_bad_decisions_and_missing_notes() -> None:
    module = load_module()
    rows = [
        {"queue_id": "HV-001", "human_decision": "bad", "human_notes": ""},
        {"queue_id": "HV-002", "human_decision": "fix", "human_notes": ""},
        {"queue_id": "HV-002", "human_decision": "accept", "human_notes": ""},
        {"queue_id": "HV-004", "human_decision": "", "human_notes": ""},
    ]

    errors = module.validate_rows(rows, require_complete=True)
    assert "queue_id=HV-001 invalid human_decision=bad" in errors[0]
    assert any("queue_id=HV-002 decision=fix requires human_notes" in error for error in errors)
    assert any("queue_id=HV-002 duplicate queue_id" in error for error in errors)
    assert any("queue_id=HV-004 missing human_decision" in error for error in errors)
