from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_export_intervention_pilot_tables_emits_markdown_and_tex(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_intervention_pilot_tables.py"
    baseline = tmp_path / "baseline_metrics.json"
    decision_first = tmp_path / "decision_first_metrics.json"
    markdown_output = tmp_path / "intervention.md"
    tex_output = tmp_path / "intervention.tex"
    macros_output = tmp_path / "intervention_macros.tex"

    baseline.write_text(
        json.dumps(
            {
                "summary": build_summary(
                    avg_utility=-0.22,
                    action_accuracy=0.78,
                    over_answer_rate=0.05,
                    answerable_acc=0.42,
                    conflict_acc=1.0,
                    false_acc=0.92,
                    stale_acc=0.75,
                )
            }
        ),
        encoding="utf-8",
    )
    decision_first.write_text(
        json.dumps(
            {
                "summary": build_summary(
                    avg_utility=-0.14,
                    action_accuracy=0.85,
                    over_answer_rate=0.0,
                    answerable_acc=0.5,
                    conflict_acc=1.0,
                    false_acc=1.0,
                    stale_acc=1.0,
                )
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--run",
            f"baseline={baseline}",
            "--run",
            f"decision_first={decision_first}",
            "--markdown-output",
            str(markdown_output),
            "--tex-output",
            str(tex_output),
            "--macros-output",
            str(macros_output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    markdown = markdown_output.read_text(encoding="utf-8")
    tex = tex_output.read_text(encoding="utf-8")
    macros = macros_output.read_text(encoding="utf-8")

    assert "`decision_first`" in markdown
    assert "+0.08" in markdown
    assert "Defective-Premise Acc." in markdown
    assert r"\label{tab:qwen25-15b-intervention-pilot}" in tex
    assert r"\textbf{0}" in tex
    assert r"\newcommand{\QwenQuickStaleInterventionDecisionFirstUtility}{-0.14}" in macros
    assert r"\newcommand{\QwenQuickStaleInterventionDecisionFirstDeltaUtility}{+0.08}" in macros
    assert r"\newcommand{\QwenQuickStaleInterventionDecisionFirstOverAnswer}{0}" in macros


def build_summary(
    *,
    avg_utility: float,
    action_accuracy: float,
    over_answer_rate: float,
    answerable_acc: float,
    conflict_acc: float,
    false_acc: float,
    stale_acc: float,
) -> dict:
    return {
        "num_examples": 40,
        "action_accuracy": action_accuracy,
        "answer_em": 0.0,
        "answer_contains_rate": 0.45,
        "avg_utility": avg_utility,
        "over_answer_rate": over_answer_rate,
        "json_parse_rate": 0.85,
        "pred_action_counts": {"answer": 18, "challenge": 22},
        "confusion": {
            "answer": {"answer": 18, "challenge": 6},
            "challenge": {"challenge": 16},
        },
        "per_slice": {
            "answerable_control": {"count": 12, "action_accuracy": answerable_acc},
            "conflicting_evidence": {"count": 12, "action_accuracy": conflict_acc},
            "false_premise": {"count": 12, "action_accuracy": false_acc},
            "stale_premise": {"count": 4, "action_accuracy": stale_acc},
        },
    }
