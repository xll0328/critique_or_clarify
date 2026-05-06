from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from coc.io import read_jsonl


def test_prepare_answer_challenge_seed_candidates_outputs_targeted_pool(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_answer_challenge_seed_candidates.py"
    output_path = tmp_path / "answer_challenge_candidates.jsonl"
    manifest_path = tmp_path / "answer_challenge_candidates_manifest.json"

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

    assert len(rows) == 181
    assert manifest["by_action"] == {"answer": 48, "challenge": 133}
    assert manifest["by_slice"] == {
        "answerable_control": 24,
        "conflicting_evidence": 24,
        "false_premise": 68,
        "stale_premise": 65,
    }
    assert manifest["paper_facing"] is False
    assert {row["metadata"]["candidate_status"] for row in rows} == {"needs_human_validation"}


def test_prepare_answer_challenge_seed_candidates_encodes_slice_boundaries(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_answer_challenge_seed_candidates.py"
    output_path = tmp_path / "answer_challenge_candidates.jsonl"
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
    answer_rows = [row for row in rows if row["gold_action"] == "answer"]
    challenge_rows = [row for row in rows if row["gold_action"] == "challenge"]
    stale_rows = [row for row in rows if row["metadata"]["slice"] == "stale_premise"]

    assert all(row["metadata"]["slice"] in {"answerable_control", "conflicting_evidence"} for row in answer_rows)
    assert all(row["gold_answer"] for row in answer_rows)
    assert all(row["metadata"]["slice"] in {"false_premise", "stale_premise"} for row in challenge_rows)
    assert all("incorrect premise" in row["gold_response"] or "stale" in row["gold_response"] for row in challenge_rows)
    assert any(row["metadata"]["has_stale_signal"] is True for row in stale_rows)


def test_answer_challenge_candidates_can_be_wired_into_validation_queue(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    prepare_script = repo_root / "scripts" / "prepare_answer_challenge_seed_candidates.py"
    queue_script = repo_root / "scripts" / "build_human_validation_work_queue.py"
    candidate_path = tmp_path / "answer_challenge_candidates.jsonl"
    manifest_path = tmp_path / "manifest.json"
    queue_path = tmp_path / "answer_challenge_queue.csv"

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

    assert len(rows) == 181
    assert {row["validation_type"] for row in rows} == {"example_gold_label"}
    assert {row["status"] for row in rows} == {"pending"}
    assert {row["priority"] for row in rows} == {"high", "medium"}
    assert any("support answering" in row["check_question"] for row in rows)
    assert any("false or stale premise" in row["check_question"] for row in rows)
