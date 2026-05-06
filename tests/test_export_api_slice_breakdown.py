from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_api_slice_breakdown.py"


def test_export_api_slice_breakdown_reports_boundary_hardest_slices(tmp_path: Path) -> None:
    metric_paths = [
        write_metric(
            tmp_path / "aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json",
            action_accuracy=0.70,
            avg_utility=0.05,
            false_acc=0.40,
            conflict_acc=0.90,
            false_over=0.50,
            pred_counts={"answer": 6, "challenge": 4},
        ),
        write_metric(
            tmp_path / "aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json",
            action_accuracy=0.90,
            avg_utility=0.08,
            false_acc=0.65,
            conflict_acc=0.80,
            false_over=0.25,
            pred_counts={"answer": 5, "challenge": 5},
        ),
    ]
    output_md = tmp_path / "api_slice.md"
    output_json = tmp_path / "api_slice.json"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--metric-paths",
            *[str(path) for path in metric_paths],
            "--output-md",
            str(output_md),
            "--output-json",
            str(output_json),
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    text = output_md.read_text(encoding="utf-8")
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert "Day-1 API Slice Breakdown" in text
    assert "No new API calls" in text
    assert "not a fine-grained model ranking" in text
    assert "`false_premise`" in text
    assert "Boundary-Slice Over-answer Rates" in text
    assert "over-answer" in text.lower()
    assert payload["aggregate"]["all_hardest_slices_are_boundary"] is True
    assert payload["aggregate"]["top_action_accuracy_model"] == "gpt-5-chat-latest"
    assert payload["aggregate"]["top_action_accuracy_hardest_slice"] == "false_premise"
    assert payload["runs"][0]["hardest_slice"] == "false_premise"
    assert payload["runs"][0]["boundary_over_answer_rate"] > 0.0


def write_metric(
    path: Path,
    *,
    action_accuracy: float,
    avg_utility: float,
    false_acc: float,
    conflict_acc: float,
    false_over: float,
    pred_counts: dict[str, int],
) -> Path:
    summary = {
        "num_examples": 10,
        "action_accuracy": action_accuracy,
        "avg_utility": avg_utility,
        "json_parse_rate": 1.0,
        "over_answer_rate": 0.1,
        "pred_action_counts": pred_counts,
        "per_slice": {
            "answerable_control": {
                "count": 2,
                "action_accuracy": 1.0,
                "over_answer_rate": 0.0,
                "json_parse_rate": 1.0,
            },
            "false_premise": {
                "count": 4,
                "action_accuracy": false_acc,
                "over_answer_rate": false_over,
                "json_parse_rate": 1.0,
            },
            "conflicting_evidence": {
                "count": 4,
                "action_accuracy": conflict_acc,
                "over_answer_rate": 0.0,
                "json_parse_rate": 1.0,
            },
        },
    }
    payload = {
        "summary": summary,
        "details": [
            {
                "id": f"fp-{index}",
                "slice": "false_premise",
                "gold_action": "challenge",
                "pred_action": "answer" if index == 0 else "challenge",
                "action_correct": index != 0,
                "parsed_as": "json",
            }
            for index in range(4)
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
