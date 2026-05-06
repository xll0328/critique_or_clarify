from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


def test_promote_validated_expansion_candidates_writes_expanded_split(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "promote_validated_expansion_candidates.py"
    base_path = tmp_path / "base.jsonl"
    candidate_path = tmp_path / "candidates.jsonl"
    queue_path = tmp_path / "queue.csv"
    output_path = tmp_path / "expanded.jsonl"
    manifest_path = tmp_path / "manifest.json"
    write_jsonl(
        base_path,
        [
            row("base-answer", "answer", "answerable_control"),
            row("base-challenge", "challenge", "false_premise"),
        ],
    )
    write_jsonl(
        candidate_path,
        [
            row("ask-1", "ask", "ambiguous_intent"),
            row("abstain-1", "abstain", "insufficient_evidence"),
        ],
    )
    write_queue(
        queue_path,
        candidate_path,
        [
            ("ask-1", "ambiguous_intent", "ask", "accept"),
            ("abstain-1", "insufficient_evidence", "abstain", "accept"),
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--base-split",
            str(base_path),
            "--candidate-split",
            str(candidate_path),
            "--queue",
            str(queue_path),
            "--output",
            str(output_path),
            "--manifest-output",
            str(manifest_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = read_jsonl(output_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "accepted=2 total=4" in result.stdout
    assert [row["id"] for row in rows] == ["base-answer", "base-challenge", "ask-1", "abstain-1"]
    assert manifest["num_base_unique"] == 2
    assert manifest["num_promoted_candidates"] == 2
    assert manifest["by_action"] == {"abstain": 1, "answer": 1, "ask": 1, "challenge": 1}
    assert manifest["promoted_candidate_ids"] == ["ask-1", "abstain-1"]
    assert manifest["paper_facing"] is True


def test_promote_validated_expansion_candidates_requires_human_decisions(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "promote_validated_expansion_candidates.py"
    base_path = tmp_path / "base.jsonl"
    candidate_path = tmp_path / "candidates.jsonl"
    queue_path = tmp_path / "queue.csv"
    write_jsonl(base_path, [row("base-answer", "answer", "answerable_control")])
    write_jsonl(candidate_path, [row("ask-1", "ask", "ambiguous_intent")])
    write_queue(queue_path, candidate_path, [("ask-1", "ambiguous_intent", "ask", "")])

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--base-split",
            str(base_path),
            "--candidate-split",
            str(candidate_path),
            "--queue",
            str(queue_path),
            "--output",
            str(tmp_path / "expanded.jsonl"),
            "--manifest-output",
            str(tmp_path / "manifest.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "candidate ask-1 missing human_decision" in result.stderr
    assert "no accepted candidate rows to promote" in result.stderr


def test_promote_validated_expansion_candidates_blocks_duplicate_ids(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "promote_validated_expansion_candidates.py"
    base_path = tmp_path / "base.jsonl"
    candidate_path = tmp_path / "candidates.jsonl"
    queue_path = tmp_path / "queue.csv"
    write_jsonl(base_path, [row("dup-1", "answer", "answerable_control")])
    write_jsonl(candidate_path, [row("dup-1", "ask", "ambiguous_intent")])
    write_queue(queue_path, candidate_path, [("dup-1", "ambiguous_intent", "ask", "accept")])

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--base-split",
            str(base_path),
            "--candidate-split",
            str(candidate_path),
            "--queue",
            str(queue_path),
            "--output",
            str(tmp_path / "expanded.jsonl"),
            "--manifest-output",
            str(tmp_path / "manifest.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "candidate ids already exist in base splits: dup-1" in result.stderr


def row(row_id: str, action: str, slice_name: str) -> dict:
    return {
        "id": row_id,
        "source": "fixture",
        "prompt": "fixture prompt",
        "passages": [],
        "gold_action": action,
        "gold_response": "fixture response",
        "metadata": {"slice": slice_name},
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in rows:
            handle.write(json.dumps(item) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_queue(path: Path, source_artifact: Path, rows: list[tuple[str, str, str, str]]) -> None:
    fieldnames = [
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
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, (example_id, slice_name, gold_action, decision) in enumerate(rows, start=1):
            writer.writerow(
                {
                    "queue_id": f"HV-EX-{index:03d}",
                    "status": "completed" if decision else "pending",
                    "priority": "high",
                    "validation_type": "example_gold_label",
                    "source_artifact": str(source_artifact),
                    "example_id": example_id,
                    "slice": slice_name,
                    "gold_action": gold_action,
                    "check_question": "fixture",
                    "ai_prefill": "fixture",
                    "human_decision": decision,
                    "human_notes": "checked" if decision else "",
                }
            )
