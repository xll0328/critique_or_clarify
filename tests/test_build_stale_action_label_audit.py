from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def test_build_stale_action_label_audit_detects_wrong_action_update_mentions(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_stale_action_label_audit.py"
    data_path = tmp_path / "data.jsonl"
    predictions_path = tmp_path / "qwen25_15b_day1_quick_plus_stale_pool.jsonl"
    output_path = tmp_path / "audit.md"
    tex_output_path = tmp_path / "audit.tex"

    write_jsonl(
        data_path,
        [
            {
                "id": "stale-seed-014",
                "gold_action": "challenge",
                "metadata": {
                    "slice": "stale_premise",
                    "entity": "Gemini",
                    "corrected_fact": "Bard is now known as Gemini.",
                },
            },
            {
                "id": "stale-seed-015",
                "gold_action": "challenge",
                "metadata": {
                    "slice": "stale_premise",
                    "entity": "Las Vegas Raiders",
                    "corrected_fact": "The NFL team is the Las Vegas Raiders.",
                },
            },
        ],
    )
    write_jsonl(
        predictions_path,
        [
            {
                "example_id": "stale-seed-014",
                "action": "answer",
                "response": "Bard has been renamed to Gemini.",
                "raw_output": "",
            },
            {
                "example_id": "stale-seed-015",
                "action": "challenge",
                "response": "The premise is outdated.",
                "raw_output": "",
            },
        ],
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(predictions_path),
            "--data",
            str(data_path),
            "--output",
            str(output_path),
            "--tex-output",
            str(tex_output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "# Expanded Stale-Premise Action-Label Audit" in text
    assert "Qwen2.5-1.5B-Instruct" in text
    assert "1 (1)" in text
    assert "stale-seed-014" in text
    assert "Gemini" in text
    tex = tex_output_path.read_text(encoding="utf-8")
    assert r"\label{tab:day1-expanded-stale-action-label-audit}" in tex
    assert "1/1 (1)" in tex


def test_update_mention_heuristic_ignores_generic_stale_terms() -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_stale_action_label_audit.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("build_stale_action_label_audit", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    example = {
        "id": "stale-seed-012",
        "gold_action": "challenge",
        "metadata": {
            "slice": "stale_premise",
            "entity": "Ben's Original",
            "stale_claim": "The rice brand is still called Uncle Ben's.",
            "corrected_fact": "The brand is Ben's Original.",
        },
    }
    prediction = {
        "example_id": "stale-seed-012",
        "action": "answer",
        "response": "The brand name Ben's was later changed to Beverly Ben's.",
        "raw_output": "",
    }

    assert module.mentions_update(prediction, example) == (False, "")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
