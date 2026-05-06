from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from coc.io import read_jsonl


def test_prepare_answer_topup_seed_candidates_outputs_expected_pool(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_answer_topup_seed_candidates.py"
    output_path = tmp_path / "answer_topup_candidates.jsonl"
    manifest_path = tmp_path / "answer_topup_candidates_manifest.json"

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

    assert len(rows) == 60
    assert manifest["by_action"] == {"answer": 60}
    assert manifest["by_slice"] == {"answerable_control": 30, "conflicting_evidence": 30}
    assert manifest["paper_facing"] is False
    assert {row["metadata"]["candidate_status"] for row in rows} == {"needs_human_validation"}


def test_prepare_answer_topup_seed_candidates_supports_custom_counts_and_id_prefix(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_answer_topup_seed_candidates.py"
    output_path = tmp_path / "answer_topup_custom.jsonl"
    manifest_path = tmp_path / "answer_topup_custom_manifest.json"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--output",
            str(output_path),
            "--manifest-output",
            str(manifest_path),
            "--answerable-control-count",
            "14",
            "--conflicting-evidence-count",
            "26",
            "--answerable-start-index",
            "31",
            "--conflicting-start-index",
            "31",
            "--id-prefix",
            "answer-topup-v2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = read_jsonl(output_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(rows) == 40
    assert {row["metadata"]["slice"] for row in rows} == {
        "answerable_control",
        "conflicting_evidence",
    }
    assert manifest["by_slice"] == {"answerable_control": 14, "conflicting_evidence": 26}
    assert rows[0]["id"] == "answer-topup-v2-control-031"
    assert rows[-1]["id"] == "answer-topup-v2-conflict-056"


def test_prepare_answer_topup_seed_candidates_uses_answer_metadata(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_answer_topup_seed_candidates.py"
    output_path = tmp_path / "answer_topup_candidates.jsonl"
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
    assert all(row["gold_action"] == "answer" for row in rows)
    assert all(row["gold_answer"] for row in rows)
    assert all(row["passages"] for row in rows)
    assert all(
        row["metadata"]["slice"] in {"answerable_control", "conflicting_evidence"} for row in rows
    )
    assert all("not paper-facing until validation" in row["metadata"]["construction_note"] for row in rows)


def test_answer_topup_candidates_can_be_wired_into_validation_queue(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    prepare_script = repo_root / "scripts" / "prepare_answer_topup_seed_candidates.py"
    queue_script = repo_root / "scripts" / "build_human_validation_work_queue.py"
    candidate_path = tmp_path / "answer_topup_candidates.jsonl"
    manifest_path = tmp_path / "manifest.json"
    queue_path = tmp_path / "answer_topup_queue.csv"

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

    assert len(rows) == 60
    assert {row["validation_type"] for row in rows} == {"example_gold_label"}
    assert {row["status"] for row in rows} == {"pending"}
    assert {row["priority"] for row in rows} == {"medium"}
    assert all("support answering" in row["check_question"] for row in rows)
