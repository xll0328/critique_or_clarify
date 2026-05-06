from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_oral_best_paper_readiness_audit_records_current_hard_gaps(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "audit_oral_best_paper_readiness.py"
    output_md = tmp_path / "audit.md"
    output_json = tmp_path / "audit.json"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
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
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert payload["status"] == "not_oral_ready"
    assert payload["metrics"]["paper_facing_unique_examples"] == 560
    assert payload["metrics"]["candidate_augmented_unique_examples"] == 560
    assert payload["metrics"]["paper_facing_action_counts"]["answer"] == 200
    assert payload["metrics"]["paper_facing_action_counts"]["challenge"] == 200
    assert payload["metrics"]["paper_facing_action_counts"]["ask"] == 80
    assert payload["metrics"]["paper_facing_action_counts"]["abstain"] == 80
    assert payload["metrics"]["bib_entries"] >= 13
    assert payload["metrics"]["figure_count"] >= 3
    if payload["metrics"]["model_rows"] < 8:
        assert "model_matrix_too_narrow" in markdown
    else:
        assert "model_matrix_too_narrow" not in markdown
    if payload["metrics"]["bib_entries"] < 25:
        assert "related_work_too_thin" in markdown
    else:
        assert "related_work_too_thin" not in markdown
    assert "missing_validated_actions" not in markdown


def test_legacy_oral_bench_readiness_audit_points_to_canonical_dashboard() -> None:
    legacy = Path(__file__).resolve().parents[1] / "experiments" / "emnlp2026" / "oral_bench_readiness_audit.md"
    text = legacy.read_text(encoding="utf-8")

    required_fragments = [
        "superseded legacy pointer",
        "docs/emnlp2026_oral_best_paper_quality_audit.md",
        "docs/emnlp2026_oral_best_paper_quality_audit.json",
        "Paper-facing unique examples: `560` / `500`.",
        "Main model rows: `10`",
        "Bibliography entries: `35`.",
        "600-example slice-balanced split as stress evidence",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []

    stale_fragments = [
        "Date: 2026-04-28",
        "Main model rows: `8`",
        "Bibliography entries: `26`",
        "Add one more distinct robustness control",
    ]
    present = [fragment for fragment in stale_fragments if fragment in text]
    assert present == []
