from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from compare_runs import action_precision, fmt, load_run, ordered_slice_names
from day1_reporting_config import format_markdown_model_list, pending_scale_reasoning_models


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a paper-facing snapshot takeaway note from the current day-1 comparison."
    )
    parser.add_argument("metric_paths", nargs="+", help="Metric JSON files in the current comparison.")
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_snapshot_takeaways.md",
        help="Markdown output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [build_run(Path(raw_path)) for raw_path in args.metric_paths]
    report = render_report(runs)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    print(report)


def build_run(metric_path: Path) -> dict[str, Any]:
    run = load_run(metric_path)
    payload = json.loads(metric_path.read_text(encoding="utf-8"))
    run["details"] = payload.get("details", payload["summary"].get("details", []))
    return run


def render_report(runs: list[dict[str, Any]]) -> str:
    best_overall = max(runs, key=lambda run: (run["summary"]["avg_utility"], run["summary"]["action_accuracy"]))
    best_instruct = max(
        (run for run in runs if run["style"] == "instruct"),
        key=lambda run: run["summary"]["avg_utility"],
        default=None,
    )
    best_reasoning = max(
        (run for run in runs if run["style"] == "reasoning"),
        key=lambda run: run["summary"]["avg_utility"],
        default=None,
    )
    average_slice_acc = aggregate_slice_accuracy(runs)
    hardest_slice, hardest_slice_acc = min(average_slice_acc.items(), key=lambda item: item[1])
    strongest_slice, strongest_slice_acc = max(average_slice_acc.items(), key=lambda item: item[1])
    weakest_slice_for_best, weakest_slice_acc_for_best = min(
        (
            (slice_name, stats["action_accuracy"])
            for slice_name, stats in best_overall["summary"]["per_slice"].items()
        ),
        key=lambda item: item[1],
    )
    pending_models = pending_scale_reasoning_models(runs)
    lines = [
        "# Day-1 Snapshot Takeaways",
        "",
        "This note compresses the current day-1 snapshot into the few claims that are already stable enough to guide the paper narrative.",
        "",
        "## Claims We Can Already Defend",
        "",
        f"- The current frontier open baseline is `{best_overall['model']}` with `action_accuracy={fmt(best_overall['summary']['action_accuracy'])}`, `avg_utility={fmt(best_overall['summary']['avg_utility'])}`, and `challenge_precision={fmt(action_precision(best_overall['summary'], 'challenge'))}`.",
        f"- The hardest slice in the current snapshot is `{hardest_slice}` with mean action accuracy `{fmt(hardest_slice_acc)}` across the available runs; the easiest is `{strongest_slice}` at `{fmt(strongest_slice_acc)}`.",
    ]
    if best_instruct is not None and best_reasoning is not None:
        lines.append(
            f"- The best current reasoning baseline (`{best_reasoning['model']}`) is still worse than the best current instruct baseline (`{best_instruct['model']}`) on both utility (`{fmt(best_reasoning['summary']['avg_utility'])}` vs. `{fmt(best_instruct['summary']['avg_utility'])}`) and over-answer rate (`{fmt(best_reasoning['summary']['over_answer_rate'])}` vs. `{fmt(best_instruct['summary']['over_answer_rate'])}`)."
        )
        lines.append(
            f"- Reasoning has not solved formatting here: the best reasoning checkpoint's `json_parse_rate={fmt(best_reasoning['summary'].get('json_parse_rate', 0.0))}`, compared with `{fmt(best_instruct['summary'].get('json_parse_rate', 0.0))}` for the best current instruct baseline."
        )
    lines.extend(
        [
            "",
            "## Current Blockers",
            "",
            f"- Even the strongest current model is still weakest on `{weakest_slice_for_best}` (`action_accuracy={fmt(weakest_slice_acc_for_best)}`), so the benchmark is not close to saturation.",
            f"- The weakest current model by formatting is `{min(runs, key=lambda run: run['summary'].get('json_parse_rate', 0.0))['model']}`, which means part of the story is still instruction compliance rather than pure action policy.",
        ]
    )
    if pending_models:
        lines.append(
            f"- The current snapshot is still missing {format_markdown_model_list(pending_models)}, so the final scale/reasoning comparison should stay scoped until those rows land."
        )
    else:
        lines.append(
            "- All planned day-1 scale/reasoning checkpoints are present, so remaining blockers are about robustness, slice coverage, and statistical support rather than missing rows."
        )
    lines.extend(
        [
            "",
            "## Immediate Writing Use",
            "",
            "- Use this note to anchor the first paragraph of the Results section and the final sentence of the Introduction's experimental-preview paragraph.",
        ]
    )
    if pending_models:
        lines.append(
            "- Keep the claim scope narrow: calibration and slice difficulty are already supported; broad reasoning-over-instruct claims are not yet settled until the pending scale-matched runs land."
        )
    else:
        lines.append(
            "- The comparison can now be written as a completed day-1 snapshot, while avoiding broader claims until robustness runs and larger stale-premise coverage are complete."
        )
    return "\n".join(lines).rstrip()


def aggregate_slice_accuracy(runs: list[dict[str, Any]]) -> dict[str, float]:
    slice_names = ordered_slice_names(runs)
    averages: dict[str, float] = {}
    for slice_name in slice_names:
        values = [
            run["summary"]["per_slice"][slice_name]["action_accuracy"]
            for run in runs
            if slice_name in run["summary"]["per_slice"]
        ]
        averages[slice_name] = sum(values) / len(values)
    return averages


if __name__ == "__main__":
    main()
