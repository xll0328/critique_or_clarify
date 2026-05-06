from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from compare_runs import SLICE_DISPLAY_NAMES, fmt, load_run, ordered_slice_names
from day1_reporting_config import format_markdown_model_list, pending_scale_reasoning_models


SIZE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)B")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a paper-facing pairwise delta note for the current day-1 scale/reasoning comparison."
    )
    parser.add_argument("metric_paths", nargs="+", help="Metric JSON files in the current comparison.")
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_pairwise_deltas.md",
        help="Markdown output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [enrich_run(Path(raw_path)) for raw_path in args.metric_paths]
    report = render_report(runs)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")


def enrich_run(metric_path: Path) -> dict[str, Any]:
    run = load_run(metric_path)
    run["size_b"] = infer_size_b(run["model"])
    return run


def infer_size_b(model_name: str) -> float | None:
    match = SIZE_PATTERN.search(model_name)
    if match is None:
        return None
    return float(match.group(1))


def render_report(runs: list[dict[str, Any]]) -> str:
    instruct_runs = sorted(
        (run for run in runs if run["style"] == "instruct" and run["size_b"] is not None),
        key=lambda run: (run["size_b"], run["model"]),
    )
    reasoning_runs = sorted(
        (run for run in runs if run["style"] == "reasoning" and run["size_b"] is not None),
        key=lambda run: (run["size_b"], run["model"]),
    )
    instruct_pairs = consecutive_pairs(instruct_runs)
    reasoning_pairs = consecutive_pairs(reasoning_runs)
    matched_pairs = matched_style_pairs(instruct_runs, reasoning_runs)

    lines = [
        "# Day-1 Pairwise Deltas",
        "",
        "This note turns the current scale/reasoning snapshot into pairwise deltas that are easier to cite in the paper than raw tables alone.",
        "",
        "## Frontier Steps",
        "",
        "### Instruct Frontier",
        "",
    ]
    lines.extend(render_frontier_section(instruct_pairs, "instruct"))
    lines.extend(["", "### Reasoning Frontier", ""])
    lines.extend(render_frontier_section(reasoning_pairs, "reasoning"))
    lines.extend(["", "## Scale-Matched Style Contrasts", ""])
    lines.extend(render_matched_section(matched_pairs, runs))
    lines.extend(["", "## Immediate Writing Use", ""])
    lines.extend(render_writing_use(instruct_pairs, matched_pairs))
    return "\n".join(lines).rstrip()


def consecutive_pairs(runs: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return list(zip(runs, runs[1:]))


def matched_style_pairs(
    instruct_runs: list[dict[str, Any]], reasoning_runs: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    instruct_by_size = best_run_by_size(instruct_runs)
    reasoning_by_size = best_run_by_size(reasoning_runs)
    shared_sizes = sorted(set(instruct_by_size) & set(reasoning_by_size))
    return [(instruct_by_size[size_b], reasoning_by_size[size_b]) for size_b in shared_sizes]


def best_run_by_size(runs: list[dict[str, Any]]) -> dict[float, dict[str, Any]]:
    picked: dict[float, dict[str, Any]] = {}
    for run in runs:
        size_b = run["size_b"]
        if size_b is None:
            continue
        current = picked.get(size_b)
        if current is None or run["summary"]["avg_utility"] > current["summary"]["avg_utility"]:
            picked[size_b] = run
    return picked


def render_frontier_section(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]], style: str
) -> list[str]:
    if not pairs:
        return [f"- No within-style {style} scale step is available yet."]
    lines = [
        "| From | To | Delta Utility | Delta Action Acc. | Delta Over-Answer | Delta JSON Parse | Biggest Slice Gain | Biggest Slice Drop |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for source, target in pairs:
        delta = pair_delta(source, target)
        lines.append(
            "| "
            + " | ".join(
                [
                    source["model"],
                    target["model"],
                    format_delta(delta["avg_utility"]),
                    format_delta(delta["action_accuracy"]),
                    format_delta(delta["over_answer_rate"]),
                    format_delta(delta["json_parse_rate"]),
                    slice_gain_text(delta["largest_gain"]),
                    slice_drop_text(delta["largest_drop"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "Interpretation:"])
    for source, target in pairs:
        delta = pair_delta(source, target)
        lines.append(
            f"- From `{source['model']}` to `{target['model']}`, action accuracy changes by `{format_delta(delta['action_accuracy'])}`, utility by `{format_delta(delta['avg_utility'])}`, and JSON parse by `{format_delta(delta['json_parse_rate'])}`."
        )
    return lines


def render_matched_section(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]], runs: list[dict[str, Any]]
) -> list[str]:
    if not pairs:
        pending_models = pending_scale_reasoning_models(runs)
        pending_text = format_markdown_model_list(pending_models) if pending_models else "the missing matched counterpart"
        return [
            "- No exact size-matched instruct-vs-reasoning pair is available yet.",
            f"- Pending checkpoints still matter here: {pending_text}.",
        ]
    lines = [
        "| Size | Instruct | Reasoning | Reasoning Minus Instruct Utility | Action Acc. | Over-Answer | JSON Parse | Biggest Slice Gain For Reasoning | Biggest Slice Drop For Reasoning |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for instruct_run, reasoning_run in pairs:
        delta = pair_delta(instruct_run, reasoning_run)
        lines.append(
            "| "
            + " | ".join(
                [
                    size_label(instruct_run["size_b"]),
                    instruct_run["model"],
                    reasoning_run["model"],
                    format_delta(delta["avg_utility"]),
                    format_delta(delta["action_accuracy"]),
                    format_delta(delta["over_answer_rate"]),
                    format_delta(delta["json_parse_rate"]),
                    slice_gain_text(delta["largest_gain"]),
                    slice_drop_text(delta["largest_drop"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "Interpretation:"])
    for instruct_run, reasoning_run in pairs:
        delta = pair_delta(instruct_run, reasoning_run)
        lines.append(
            f"- At `{size_label(instruct_run['size_b'])}`, `{reasoning_run['model']}` changes utility by `{format_delta(delta['avg_utility'])}`, action accuracy by `{format_delta(delta['action_accuracy'])}`, and over-answer by `{format_delta(delta['over_answer_rate'])}` relative to `{instruct_run['model']}`."
        )
    return lines


def render_writing_use(
    instruct_pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    matched_pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> list[str]:
    lines = [
        "- Use the frontier-step lines when describing scale effects; they are direct deltas, not eyeballed differences from the markdown table.",
    ]
    if matched_pairs:
        lines.append(
            "- Use the size-matched contrast lines for instruct-vs-reasoning claims, because they isolate style at the same approximate parameter scale."
        )
    else:
        lines.append(
            "- Hold broad instruct-vs-reasoning claims until at least one exact size-matched pair exists in this note."
        )
    if instruct_pairs:
        best_step = max(instruct_pairs, key=lambda pair: pair_delta(pair[0], pair[1])["action_accuracy"])
        lines.append(
            f"- The current strongest available instruct step is `{best_step[0]['model']} -> {best_step[1]['model']}` by action accuracy, so that is the cleanest scale sentence to foreground."
        )
    return lines


def pair_delta(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    source_summary = source["summary"]
    target_summary = target["summary"]
    slice_deltas = build_slice_deltas(source, target)
    return {
        "avg_utility": target_summary["avg_utility"] - source_summary["avg_utility"],
        "action_accuracy": target_summary["action_accuracy"] - source_summary["action_accuracy"],
        "over_answer_rate": target_summary["over_answer_rate"] - source_summary["over_answer_rate"],
        "json_parse_rate": target_summary.get("json_parse_rate", 0.0)
        - source_summary.get("json_parse_rate", 0.0),
        "largest_gain": max(slice_deltas, key=lambda item: item[1]) if slice_deltas else None,
        "largest_drop": min(slice_deltas, key=lambda item: item[1]) if slice_deltas else None,
    }


def build_slice_deltas(
    source: dict[str, Any], target: dict[str, Any]
) -> list[tuple[str, float]]:
    slice_names = ordered_slice_names([source, target])
    deltas: list[tuple[str, float]] = []
    for slice_name in slice_names:
        if slice_name not in source["summary"]["per_slice"] or slice_name not in target["summary"]["per_slice"]:
            continue
        deltas.append(
            (
                slice_name,
                target["summary"]["per_slice"][slice_name]["action_accuracy"]
                - source["summary"]["per_slice"][slice_name]["action_accuracy"],
            )
        )
    return deltas


def size_label(size_b: float | None) -> str:
    if size_b is None:
        return "unknown"
    return f"{fmt(size_b)}B"


def slice_delta_text(item: tuple[str, float] | None) -> str:
    if item is None:
        return "-"
    slice_name, delta = item
    label = SLICE_DISPLAY_NAMES.get(slice_name, slice_name.replace("_", " ").title())
    if abs(delta) < 1e-12:
        return f"{label} 0"
    return f"{label} {format_delta(delta)}"


def slice_gain_text(item: tuple[str, float] | None) -> str:
    if item is None:
        return "-"
    if item[1] <= 1e-12:
        return "No gain"
    return slice_delta_text(item)


def slice_drop_text(item: tuple[str, float] | None) -> str:
    if item is None:
        return "-"
    if item[1] >= -1e-12:
        return "No regression"
    return slice_delta_text(item)


def format_delta(value: float) -> str:
    rendered = fmt(abs(value))
    if rendered == "0":
        return "0"
    return f"+{rendered}" if value > 0 else f"-{rendered}"


if __name__ == "__main__":
    main()
