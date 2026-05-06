from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_audit_utility_weight_sensitivity_reports_best_family_gap(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "audit_utility_weight_sensitivity.py"
    data = tmp_path / "data.jsonl"
    instruct_predictions = tmp_path / "instruct.jsonl"
    reasoning_predictions = tmp_path / "reasoning.jsonl"
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

    instruct_predictions.write_text(
        "\n".join(
            [
                prediction("ex1", "answer", "Ada"),
                prediction("ex2", "challenge", "The premise is stale."),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    reasoning_predictions.write_text(
        "\n".join(
            [
                prediction("ex1", "abstain", ""),
                prediction("ex2", "answer", "It is still true."),
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
            f"instruct:instruct:{instruct_predictions}:{data}",
            "--run",
            f"reasoning:reasoning:{reasoning_predictions}:{data}",
            "--output-md",
            str(output_md),
            "--output-json",
            str(output_json),
        ],
        check=True,
        cwd=repo_root,
    )

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    paper_default = next(scheme for scheme in payload["schemes"] if scheme["scheme"] == "paper_default")

    assert paper_default["best_overall"] == "instruct"
    assert paper_default["best_reasoning_minus_best_instruct"] < 0
    assert "overanswer_heavy" in output_md.read_text(encoding="utf-8")


def prediction(example_id: str, action: str, response: str) -> str:
    return json.dumps(
        {
            "example_id": example_id,
            "action": action,
            "response": response,
            "confidence": None,
            "raw_output": response,
            "metadata": {"parsed_as": "json"},
        }
    )

