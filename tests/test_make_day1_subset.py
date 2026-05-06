from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from coc.io import read_jsonl


def test_make_day1_subset_can_include_stale_seed_without_changing_defaults(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "make_day1_dev_subset.py"

    qacc_path = tmp_path / "qacc.jsonl"
    pcbench_path = tmp_path / "pcbench.jsonl"
    stale_path = tmp_path / "stale.jsonl"
    output_path = tmp_path / "subset.jsonl"
    manifest_path = tmp_path / "subset_manifest.json"

    write_jsonl(
        qacc_path,
        [
            example(
                "qacc-1",
                source="QACC",
                gold_action="answer",
                metadata={"slice": "conflicting_evidence"},
            )
        ],
    )
    write_jsonl(
        pcbench_path,
        [
                example(
                    "pair-1-answer",
                    source="PCBench",
                    gold_action="answer",
                    metadata={
                        "paired_group_id": "pair-1",
                        "slice": "answerable_control",
                        "difficulty": "normal",
                        "conflict_type": "contra_premise_insert",
                    },
                ),
                example(
                    "pair-1-challenge",
                    source="PCBench",
                    gold_action="challenge",
                    metadata={
                        "paired_group_id": "pair-1",
                        "slice": "false_premise",
                        "difficulty": "normal",
                        "conflict_type": "contra_premise_insert",
                    },
                ),
            ],
        )
    write_jsonl(
        stale_path,
        [
            example(
                "stale-1",
                source="stale-fact-seed",
                gold_action="challenge",
                metadata={"slice": "stale_premise", "valid_as_of": "2026-04-23"},
            )
        ],
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--qacc",
            str(qacc_path),
            "--pcbench-paired",
            str(pcbench_path),
            "--stale",
            str(stale_path),
            "--qacc-size",
            "1",
            "--pcbench-pairs",
            "1",
            "--stale-size",
            "1",
            "--output",
            str(output_path),
            "--manifest",
            str(manifest_path),
            "--seed",
            "7",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = read_jsonl(output_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(rows) == 4
    assert manifest["num_examples"] == 4
    assert manifest["by_slice"]["conflicting_evidence"] == 1
    assert manifest["by_slice"]["answerable_control"] == 1
    assert manifest["by_slice"]["false_premise"] == 1
    assert manifest["by_slice"]["stale_premise"] == 1

    stale_row = next(row for row in rows if row["id"] == "stale-1")
    assert stale_row["metadata"]["has_stale_premise"] is True


def example(
    example_id: str,
    *,
    source: str,
    gold_action: str,
    metadata: dict,
) -> dict:
    return {
        "id": example_id,
        "source": source,
        "prompt": f"Prompt for {example_id}",
        "passages": [],
        "gold_action": gold_action,
        "gold_answer": "answer" if gold_action == "answer" else None,
        "gold_response": "response" if gold_action != "answer" else None,
        "metadata": metadata,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
