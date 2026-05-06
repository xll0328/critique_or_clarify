from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_audit_benchmark_expansion_coverage_uses_dynamic_interpretation(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "audit_benchmark_expansion_coverage.py"
    split_path = tmp_path / "split.jsonl"
    output_md = tmp_path / "audit.md"
    output_json = tmp_path / "audit.json"

    rows = [
        row("fixture-answer-1", "answer", "answerable_control"),
        row("fixture-answer-2", "answer", "answerable_control"),
    ]
    with split_path.open("w", encoding="utf-8") as handle:
        for item in rows:
            handle.write(json.dumps(item) + "\n")

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--split",
            str(split_path),
            "--output-md",
            str(output_md),
            "--output-json",
            str(output_json),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    markdown = output_md.read_text(encoding="utf-8")

    assert "current candidate-augmented bundle is still `498` examples short" in markdown
    assert "largest remaining action deficit is `challenge` with a gap of `200` examples" in markdown
    assert "largest scientific deficit is action coverage for `ask` and `abstain`" not in markdown


def row(row_id: str, action: str, slice_name: str) -> dict:
    return {
        "id": row_id,
        "source": "fixture",
        "prompt": "fixture prompt",
        "passages": [],
        "gold_action": action,
        "gold_answer": "fixture answer" if action == "answer" else None,
        "gold_response": "fixture response" if action != "answer" else None,
        "metadata": {"slice": slice_name},
    }
