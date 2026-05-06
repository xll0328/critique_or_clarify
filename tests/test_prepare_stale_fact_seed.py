from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from coc.io import read_jsonl


def test_prepare_stale_fact_seed_emits_grounding_passages() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_stale_fact_seed.py"
    output_path = repo_root / "data" / "processed" / "stale_fact_seed.jsonl"

    subprocess.run([sys.executable, str(script_path)], check=True, capture_output=True, text=True)

    rows = read_jsonl(output_path)

    assert len(rows) == 7
    assert all(row["gold_action"] == "challenge" for row in rows)
    assert all(row["metadata"]["slice"] == "stale_premise" for row in rows)
    assert all(row["metadata"]["has_stale_premise"] is True for row in rows)
    assert all(len(row["passages"]) >= 2 for row in rows)


def test_prepare_stale_fact_seed_can_emit_expanded_pool(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "prepare_stale_fact_seed.py"
    output_path = tmp_path / "stale_fact_pool.jsonl"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--include-expansion",
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = read_jsonl(output_path)

    assert len(rows) == 15
    assert rows[-1]["id"] == "stale-seed-015"
    assert all(row["gold_action"] == "challenge" for row in rows)
    assert all(row["metadata"]["source_url"].startswith("https://") for row in rows)
