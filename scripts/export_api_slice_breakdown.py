#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from export_api_baseline_tables import (
    DEFAULT_METRIC_PATHS,
    MODEL_DISPLAY,
    MODEL_ORDER,
    parse_model_id_from_path,
)


SLICE_ORDER = [
    "answerable_control",
    "false_premise",
    "stale_premise",
    "conflicting_evidence",
    "ambiguous_intent",
    "insufficient_evidence",
]

BOUNDARY_SLICES = {"false_premise", "stale_premise", "conflicting_evidence"}
ACTION_ORDER = ["answer", "ask", "challenge", "abstain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export slice-level API audit from saved metric JSON files."
    )
    parser.add_argument(
        "--metric-paths",
        nargs="+",
        default=DEFAULT_METRIC_PATHS,
        help="Metric JSON paths from scripts/run_aihubmix_baseline.py.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/day1_api_slice_breakdown.md",
        help="Markdown audit output path.",
    )
    parser.add_argument(
        "--output-json",
        default="experiments/day1/day1_api_slice_breakdown.json",
        help="Machine-readable audit output path.",
    )
    return parser.parse_args()


def fmt(value: float | int | None) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.4f}"


def pct(value: float | int | None) -> str:
    if value is None:
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def action_mix(pred_counts: dict[str, int]) -> str:
    pieces = []
    for action in ACTION_ORDER:
        count = int(pred_counts.get(action, 0))
        pieces.append(f"{action}={count}")
    extras = sorted(action for action in pred_counts if action not in ACTION_ORDER)
    pieces.extend(f"{action}={int(pred_counts[action])}" for action in extras)
    return ", ".join(pieces)


def load_run(metric_path: Path) -> dict[str, Any]:
    payload = json.loads(metric_path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    details = payload.get("details", [])
    model_id = parse_model_id_from_path(metric_path)
    per_slice = summary.get("per_slice", {})

    slice_rows: dict[str, dict[str, Any]] = {}
    for slice_name in sorted(per_slice):
        stats = dict(per_slice[slice_name])
        slice_details = [detail for detail in details if detail.get("slice") == slice_name]
        pred_counts = Counter(str(detail.get("pred_action", "missing")) for detail in slice_details)
        gold_counts = Counter(str(detail.get("gold_action", "missing")) for detail in slice_details)
        wrong_counts = Counter(
            str(detail.get("pred_action", "missing"))
            for detail in slice_details
            if not bool(detail.get("action_correct", False))
        )
        stats["pred_action_counts"] = dict(pred_counts)
        stats["gold_action_counts"] = dict(gold_counts)
        stats["wrong_pred_action_counts"] = dict(wrong_counts)
        slice_rows[slice_name] = stats

    hardest_slice = min(
        slice_rows,
        key=lambda slice_name: (
            float(slice_rows[slice_name].get("action_accuracy", 0.0)),
            -int(slice_rows[slice_name].get("count", 0)),
            slice_name,
        ),
    )

    boundary_counts = [
        int(slice_rows[slice_name].get("count", 0))
        for slice_name in BOUNDARY_SLICES
        if slice_name in slice_rows
    ]
    boundary_over_answer = [
        float(slice_rows[slice_name].get("over_answer_rate", 0.0))
        * int(slice_rows[slice_name].get("count", 0))
        for slice_name in BOUNDARY_SLICES
        if slice_name in slice_rows
    ]
    boundary_total = sum(boundary_counts)

    return {
        "model": model_id,
        "display_model": MODEL_DISPLAY.get(model_id, model_id),
        "metric_path": str(metric_path),
        "num_examples": int(summary["num_examples"]),
        "action_accuracy": float(summary["action_accuracy"]),
        "avg_utility": float(summary["avg_utility"]),
        "json_parse_rate": float(summary.get("json_parse_rate", 0.0)),
        "over_answer_rate": float(summary["over_answer_rate"]),
        "pred_action_counts": {
            str(action): int(count)
            for action, count in summary.get("pred_action_counts", {}).items()
        },
        "hardest_slice": hardest_slice,
        "hardest_slice_action_accuracy": float(
            slice_rows[hardest_slice].get("action_accuracy", 0.0)
        ),
        "hardest_slice_over_answer_rate": float(
            slice_rows[hardest_slice].get("over_answer_rate", 0.0)
        ),
        "boundary_over_answer_rate": (
            round(sum(boundary_over_answer) / max(boundary_total, 1), 4)
            if boundary_total
            else 0.0
        ),
        "per_slice": slice_rows,
    }


def ordered_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model = {run["model"]: run for run in runs}
    ordered = [by_model[model] for model in MODEL_ORDER if model in by_model]
    extras = sorted(
        (run for run in runs if run["model"] not in MODEL_ORDER),
        key=lambda r: r["model"],
    )
    ordered.extend(extras)
    return ordered


def build_aggregate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    hardest_counts = Counter(run["hardest_slice"] for run in runs)
    top_accuracy = max(runs, key=lambda run: (run["action_accuracy"], run["avg_utility"]))
    top_utility = max(runs, key=lambda run: (run["avg_utility"], run["action_accuracy"]))
    return {
        "num_runs": len(runs),
        "hardest_slice_counts": dict(sorted(hardest_counts.items())),
        "all_hardest_slices_are_boundary": all(
            run["hardest_slice"] in BOUNDARY_SLICES for run in runs
        ),
        "top_action_accuracy_model": top_accuracy["model"],
        "top_action_accuracy": top_accuracy["action_accuracy"],
        "top_action_accuracy_hardest_slice": top_accuracy["hardest_slice"],
        "top_action_accuracy_hardest_slice_action_accuracy": top_accuracy[
            "hardest_slice_action_accuracy"
        ],
        "top_utility_model": top_utility["model"],
        "top_utility": top_utility["avg_utility"],
        "top_utility_hardest_slice": top_utility["hardest_slice"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    runs = report["runs"]
    aggregate = report["aggregate"]
    lines = [
        "# Day-1 API Slice Breakdown",
        "",
        f"Date: {report['date']}",
        "",
        (
            "Status: generated from saved metric JSON artifacts only. "
            "No new API calls, model runs, or human-validation fields are used."
        ),
        "",
        "## Takeaways",
        "",
        (
            "- This audit supports API-section integration, not a fine-grained model ranking. "
            "The paper-facing use is the coarse pattern that high pooled accuracy can still "
            "hide premise/evidence-boundary errors."
        ),
        (
            "- All API rows have their weakest slice on a boundary slice "
            f"(`all_hardest_slices_are_boundary={aggregate['all_hardest_slices_are_boundary']}`): "
            f"`{json.dumps(aggregate['hardest_slice_counts'], sort_keys=True)}`."
        ),
        (
            f"- The top pooled-accuracy row is `{aggregate['top_action_accuracy_model']}` "
            f"(`action_accuracy={fmt(aggregate['top_action_accuracy'])}`), but its weakest slice is "
            f"`{aggregate['top_action_accuracy_hardest_slice']}` "
            f"(`action_accuracy={fmt(aggregate['top_action_accuracy_hardest_slice_action_accuracy'])}`)."
        ),
        "",
        "## Overall Rows",
        "",
        (
            "| Model | N | Action Acc. | Avg Utility | JSON Parse | Over-answer | "
            "Boundary Over-answer | Hardest Slice | Hardest Acc. | Hardest Over-answer | Predicted Actions |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]

    for run in runs:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{run['display_model']}`",
                    str(run["num_examples"]),
                    fmt(run["action_accuracy"]),
                    fmt(run["avg_utility"]),
                    fmt(run["json_parse_rate"]),
                    fmt(run["over_answer_rate"]),
                    fmt(run["boundary_over_answer_rate"]),
                    f"`{run['hardest_slice']}`",
                    fmt(run["hardest_slice_action_accuracy"]),
                    fmt(run["hardest_slice_over_answer_rate"]),
                    f"`{action_mix(run['pred_action_counts'])}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Per-Slice Action Accuracy",
            "",
            "| Model | "
            + " | ".join(f"`{slice_name}`" for slice_name in SLICE_ORDER)
            + " |",
            "| --- | " + " | ".join("---:" for _ in SLICE_ORDER) + " |",
        ]
    )
    for run in runs:
        cells = [f"`{run['display_model']}`"]
        for slice_name in SLICE_ORDER:
            stats = run["per_slice"].get(slice_name, {})
            cells.append(fmt(stats.get("action_accuracy")))
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Boundary-Slice Over-answer Rates",
            "",
            "| Model | `false_premise` | `stale_premise` | `conflicting_evidence` |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for run in runs:
        cells = [f"`{run['display_model']}`"]
        for slice_name in ["false_premise", "stale_premise", "conflicting_evidence"]:
            stats = run["per_slice"].get(slice_name, {})
            cells.append(pct(stats.get("over_answer_rate")))
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for path in report["metric_paths"]:
        lines.append(f"- `{path}`")

    return "\n".join(lines) + "\n"


def build_report(metric_paths: list[Path]) -> dict[str, Any]:
    runs = ordered_runs([load_run(path) for path in metric_paths])
    return {
        "date": date.today().isoformat(),
        "metric_paths": [str(path) for path in metric_paths],
        "aggregate": build_aggregate(runs),
        "runs": runs,
    }


def main() -> None:
    args = parse_args()
    metric_paths = [Path(path) for path in args.metric_paths]
    report = build_report(metric_paths)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")


if __name__ == "__main__":
    main()
