from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from coc.io import read_jsonl


def test_prepare_ask_abstain_seed_candidates_outputs_balanced_candidate_pool(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_ask_abstain_seed_candidates.py"
    output_path = tmp_path / "ask_abstain_candidates.jsonl"
    manifest_path = tmp_path / "ask_abstain_candidates_manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
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

    assert len(rows) == 160
    assert manifest["by_action"] == {"abstain": 80, "ask": 80}
    assert manifest["by_slice"] == {"ambiguous_intent": 80, "insufficient_evidence": 80}
    assert manifest["paper_facing"] is False
    assert {row["metadata"]["candidate_status"] for row in rows} == {"needs_human_validation"}


def test_prepare_ask_abstain_seed_candidates_uses_action_boundary_metadata(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_ask_abstain_seed_candidates.py"
    output_path = tmp_path / "ask_abstain_candidates.jsonl"
    manifest_path = tmp_path / "manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
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
    ask_rows = [row for row in rows if row["gold_action"] == "ask"]
    abstain_rows = [row for row in rows if row["gold_action"] == "abstain"]

    assert all(row["metadata"]["requires_clarification"] is True for row in ask_rows)
    assert all(row["metadata"]["missing_slots"] for row in ask_rows)
    assert any(row["metadata"]["has_irreconcilable_evidence"] is True for row in abstain_rows)
    assert all("not paper-facing until validation" in row["metadata"]["construction_note"] for row in rows)


def test_candidate_rows_can_be_wired_into_validation_queue(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    prepare_script = repo_root / "scripts" / "prepare_ask_abstain_seed_candidates.py"
    queue_script = repo_root / "scripts" / "build_human_validation_work_queue.py"
    candidate_path = tmp_path / "ask_abstain_candidates.jsonl"
    manifest_path = tmp_path / "manifest.json"
    queue_path = tmp_path / "candidate_queue.csv"

    subprocess.run(
        [
            sys.executable,
            str(prepare_script),
            "--output",
            str(candidate_path),
            "--manifest-output",
            str(manifest_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(queue_script),
            "--split",
            str(candidate_path),
            "--skip-claims",
            "--output",
            str(queue_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = list(csv.DictReader(queue_path.open(encoding="utf-8")))

    assert len(rows) == 160
    assert {row["validation_type"] for row in rows} == {"example_gold_label"}
    assert {row["status"] for row in rows} == {"pending"}
    assert {row["priority"] for row in rows} == {"high"}
    assert any("follow-up question is the best action" in row["check_question"] for row in rows)
    assert any("abstention the best-supported action" in row["check_question"] for row in rows)
