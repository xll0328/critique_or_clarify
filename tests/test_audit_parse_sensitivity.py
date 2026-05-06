from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_audit_parse_sensitivity_quantifies_strict_json_delta(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "audit_parse_sensitivity.py"
    data = tmp_path / "data.jsonl"
    predictions = tmp_path / "predictions.jsonl"
    output_md = tmp_path / "audit.md"
    output_json = tmp_path / "audit.json"

    data.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "ex1",
                        "prompt": "Who won?",
                        "passages": [],
                        "gold_action": "answer",
                        "gold_answer": "Ada",
                        "source": "unit",
                        "metadata": {"slice": "answerable_control"},
                    }
                ),
                json.dumps(
                    {
                        "id": "ex2",
                        "prompt": "Confirm stale premise.",
                        "passages": [],
                        "gold_action": "challenge",
                        "gold_response": "The premise is stale.",
                        "source": "unit",
                        "metadata": {"slice": "stale_premise"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    predictions.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "example_id": "ex1",
                        "action": "answer",
                        "response": "Ada",
                        "confidence": None,
                        "raw_output": '{"action": "answer", "response": "Ada"}',
                        "metadata": {"parsed_as": "json"},
                    }
                ),
                json.dumps(
                    {
                        "example_id": "ex2",
                        "action": "challenge",
                        "response": "The premise is stale.",
                        "confidence": None,
                        "raw_output": "This premise is stale, so I should challenge it.",
                        "metadata": {"parsed_as": "fallback"},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--run",
            f"unit:{predictions}:{data}",
            "--output-md",
            str(output_md),
            "--output-json",
            str(output_json),
        ],
        check=True,
        cwd=repo_root,
    )

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    row = payload["runs"][0]

    assert row["current_action_accuracy"] == 1.0
    assert row["strict_json_or_abstain_action_accuracy"] == 0.5
    assert row["delta_current_minus_strict_action_accuracy"] == 0.5
    assert row["fallback_rows"] == 1
    assert row["fallback_action_accuracy_current_parser"] == 1.0
    assert "Strict JSON-or-Abstain" in output_md.read_text(encoding="utf-8")

