from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_codex_multipass_validation_review.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("build_codex_multipass_validation_review", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_multipass_accepts_clean_answer_example() -> None:
    module = load_module()
    row = {
        "queue_id": "HV-EX-001",
        "status": "pending",
        "priority": "medium",
        "validation_type": "example_gold_label",
        "source_artifact": "split.jsonl",
        "example_id": "example-answer",
        "slice": "answerable_control",
        "model": "",
        "gold_action": "answer",
        "pred_action": "",
        "check_question": "Does the prompt/evidence support answering?",
        "ai_prefill": "gold_action=answer",
        "human_decision": "",
        "human_notes": "",
    }
    example = {
        "id": "example-answer",
        "source": "PCBench",
        "prompt": "What is 2+2?",
        "gold_action": "answer",
        "gold_answer": "4",
        "metadata": {"slice": "answerable_control"},
    }
    context = {
        "examples_by_id": {"example-answer": example},
        "expected_by_id": {"HV-EX-001": row},
        "audits": {},
        "metric_payloads": {},
    }

    pass_rows = module.run_passes([row], context)
    consensus = module.build_consensus([row], pass_rows)

    assert len(pass_rows) == 6
    assert {pass_row["pass_decision"] for pass_row in pass_rows} == {"accept"}
    assert consensus[0]["multipass_consensus_decision"] == "accept"
    assert consensus[0]["multipass_accept_count"] == "6"


def test_consensus_marks_non_accept_for_follow_up() -> None:
    module = load_module()
    row = {"queue_id": "HV-001", "human_decision": "", "human_notes": ""}
    pass_rows = [
        {
            "queue_id": "HV-001",
            "pass_id": "P1",
            "pass_name": "ontology_boundary",
            "pass_decision": "accept",
            "pass_notes": "ok",
        },
        {
            "queue_id": "HV-001",
            "pass_id": "P2",
            "pass_name": "artifact_and_source_presence",
            "pass_decision": "needs_second_pass",
            "pass_notes": "missing source",
        },
    ]

    consensus = module.build_consensus([row], pass_rows)

    assert consensus[0]["multipass_consensus_decision"] == "needs_second_pass"
    assert consensus[0]["multipass_accept_count"] == "1"
    assert consensus[0]["multipass_non_accept_count"] == "1"
