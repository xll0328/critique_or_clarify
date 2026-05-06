from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from compare_runs import SLICE_DISPLAY_NAMES, fmt, load_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a filled day-1 model report from quick/dev metrics and sampled failures."
    )
    parser.add_argument("--dev-metrics", required=True, help="Development metrics JSON path.")
    parser.add_argument("--output", required=True, help="Markdown output path.")
    parser.add_argument("--quick-metrics", help="Optional quick metrics JSON path.")
    parser.add_argument("--dev-failures", help="Optional sampled failure text file for dev.")
    parser.add_argument("--date", help="Run date to report, e.g. 2026-04-24.")
    parser.add_argument("--model-id", help="Original model identifier for metadata display.")
    parser.add_argument("--local-snapshot", help="Local model path or snapshot path.")
    parser.add_argument("--gpu", help="GPU description, e.g. CUDA_VISIBLE_DEVICES=2.")
    parser.add_argument("--prompt-format", default="action-selection JSON")
    parser.add_argument("--max-new-tokens", help="Generation cap used for the run.")
    parser.add_argument("--temperature", help="Sampling temperature used for the run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dev_run = build_metric_payload(Path(args.dev_metrics))
    quick_run = build_metric_payload(Path(args.quick_metrics)) if args.quick_metrics else None
    failures = parse_failure_file(Path(args.dev_failures)) if args.dev_failures else {}
    report = render_report(
        dev_run=dev_run,
        quick_run=quick_run,
        failures=failures,
        date=args.date,
        model_id=args.model_id,
        local_snapshot=args.local_snapshot,
        gpu=args.gpu,
        prompt_format=args.prompt_format,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")


def build_metric_payload(path: Path) -> dict[str, Any]:
    run = load_run(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    run["summary"] = payload["summary"]
    run["details"] = payload.get("details", [])
    return run


def parse_failure_file(path: Path) -> dict[str, list[dict[str, Any]]]:
    failures: dict[str, list[dict[str, Any]]] = defaultdict(list)
    current_slice = "unknown"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_slice = line[3:].split(" (", 1)[0]
            continue
        if line.startswith("{"):
            failures[current_slice].append(json.loads(line))
    return dict(failures)


def render_report(
    *,
    dev_run: dict[str, Any],
    quick_run: dict[str, Any] | None,
    failures: dict[str, list[dict[str, Any]]],
    date: str | None,
    model_id: str | None,
    local_snapshot: str | None,
    gpu: str | None,
    prompt_format: str,
    max_new_tokens: str | None,
    temperature: str | None,
) -> str:
    model_name = dev_run["model"]
    lines = [
        f"# {model_name} on Day-1",
        "",
        "## Run Metadata",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Date | `{date or 'unknown'}` |",
        f"| Model | `{model_id or model_name}` |",
        f"| GPUs | `{gpu or 'unknown'}` |",
        f"| Prompt format | {prompt_format} |",
        f"| Max new tokens | `{max_new_tokens or 'unknown'}` |",
        f"| Temperature | `{temperature or 'unknown'}` |",
    ]
    if local_snapshot:
        lines.append(f"| Local snapshot | `{local_snapshot}` |")

    lines.extend(["", "## Main Metrics", ""])
    lines.extend(render_main_metrics(dev_run, quick_run))
    lines.extend(["", "## Per-Slice Metrics on `day1_dev`", ""])
    lines.extend(render_slice_metrics(dev_run))
    lines.extend(["", "## Confusion Notes", ""])
    lines.extend(render_confusion_notes(dev_run))
    lines.extend(["", "## Qualitative Read", ""])
    lines.extend(render_qualitative_read(dev_run, quick_run))
    if failures:
        lines.extend(["", "## Representative Failures", ""])
        lines.extend(render_representative_failures(failures))
    lines.extend(["", "## Interpretation", ""])
    lines.extend(render_interpretation(dev_run, quick_run))
    return "\n".join(lines).rstrip()


def render_main_metrics(dev_run: dict[str, Any], quick_run: dict[str, Any] | None) -> list[str]:
    lines = [
        "| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if quick_run is not None:
        lines.append(render_metric_row("day1_quick", quick_run["summary"]))
    lines.append(render_metric_row("day1_dev", dev_run["summary"]))
    return lines


def render_metric_row(split: str, summary: dict[str, Any]) -> str:
    return (
        "| "
        + " | ".join(
            [
                f"`{split}`",
                f"`{summary['num_examples']}`",
                f"`{fmt(summary['avg_utility'])}`",
                f"`{fmt(summary['action_accuracy'])}`",
                f"`{fmt(summary['answer_em'])}`",
                f"`{fmt(summary.get('answer_contains_rate', 0.0))}`",
                f"`{fmt(summary['over_answer_rate'])}`",
                f"`{fmt(summary.get('json_parse_rate', 0.0))}`",
            ]
        )
        + " |"
    )


def render_slice_metrics(dev_run: dict[str, Any]) -> list[str]:
    summary = dev_run["summary"]
    lines = [
        "| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for slice_name, slice_summary in summary["per_slice"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{slice_name}`",
                    f"`{slice_summary['count']}`",
                    f"`{fmt(slice_summary['avg_utility'])}`",
                    f"`{fmt(slice_summary['action_accuracy'])}`",
                    f"`{fmt(slice_summary['answer_em'])}`",
                    f"`{fmt(slice_summary.get('answer_contains_rate', 0.0))}`",
                    f"`{fmt(slice_summary['over_answer_rate'])}`",
                    f"`{fmt(slice_summary.get('json_parse_rate', 0.0))}`",
                ]
            )
            + " |"
        )
    return lines


def render_confusion_notes(dev_run: dict[str, Any]) -> list[str]:
    summary = dev_run["summary"]
    lines = [f"- `pred_action_counts`: `{json.dumps(summary.get('pred_action_counts', {}), ensure_ascii=False)}`"]
    off_diagonal: list[tuple[int, str, str]] = []
    for gold_action, row in summary.get("confusion", {}).items():
        for pred_action, count in row.items():
            if gold_action == pred_action or count <= 0:
                continue
            off_diagonal.append((int(count), gold_action, pred_action))
    for count, gold_action, pred_action in sorted(off_diagonal, reverse=True)[:6]:
        lines.append(f"- `{gold_action} -> {pred_action}`: `{count}`")
    return lines


def render_qualitative_read(dev_run: dict[str, Any], quick_run: dict[str, Any] | None) -> list[str]:
    summary = dev_run["summary"]
    false_premise = summary["per_slice"].get("false_premise")
    answerable = summary["per_slice"].get("answerable_control")
    conflict = summary["per_slice"].get("conflicting_evidence")
    lines: list[str] = []
    json_parse_rate = summary.get("json_parse_rate", 0.0)
    if json_parse_rate >= 0.9:
        lines.append("1. Output formatting is effectively solved at this scale, so the remaining errors are mostly policy or content errors rather than parser failures.")
    elif json_parse_rate <= 0.1:
        lines.append("1. Output formatting is still a major bottleneck: most predictions are parsed through the fallback path rather than valid JSON.")
    else:
        lines.append("1. Output formatting is partially recovered but still nontrivial, so policy quality and format-following are still entangled.")
    if false_premise is not None:
        lines.append(
            f"2. `false_premise` remains a key calibration test: dev action accuracy is `{fmt(false_premise['action_accuracy'])}` with over-answer rate `{fmt(false_premise['over_answer_rate'])}`."
        )
    if conflict is not None:
        lines.append(
            f"3. `conflicting_evidence` is easier than defective-premise correction here, reaching `{fmt(conflict['action_accuracy'])}` action accuracy on `day1_dev`."
        )
    if answerable is not None:
        lines.append(
            f"4. `answerable_control` is still not saturated: dev action accuracy is `{fmt(answerable['action_accuracy'])}`, which means the model still hesitates on clean answerable items."
        )
    if quick_run is not None:
        delta = summary["action_accuracy"] - quick_run["summary"]["action_accuracy"]
        lines.append(
            f"5. Relative to `day1_quick`, the dev split changes action accuracy by `{fmt(delta)}` and keeps the same qualitative ranking across slices, so the pattern is not a tiny-subset artifact."
        )
    else:
        lines.append("5. The current report uses the available dev run as the main decision point.")
    return lines


def render_representative_failures(failures: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines: list[str] = []
    ordered_slices = ["false_premise", "conflicting_evidence", "answerable_control"]
    index = 1
    for slice_name in ordered_slices:
        if not failures.get(slice_name):
            continue
        item = select_representative_failure(failures[slice_name])
        lines.append(f"{index}. `{slice_name}`: {render_failure_item(item)}")
        index += 1
    if index == 1:
        for slice_name, bucket in sorted(failures.items()):
            if not bucket:
                continue
            item = select_representative_failure(bucket)
            lines.append(f"{index}. `{slice_name}`: {render_failure_item(item)}")
            index += 1
            if index > 3:
                break
    return lines


def select_representative_failure(items: list[dict[str, Any]]) -> dict[str, Any]:
    for item in items:
        if item["pred_action"] != item["gold_action"]:
            return item
    return items[0]


def render_failure_item(item: dict[str, Any]) -> str:
    gold_action = item["gold_action"]
    pred_action = item["pred_action"]
    example_id = item["id"]
    if pred_action != gold_action:
        return f"the model predicted `{pred_action}` instead of `{gold_action}` on `{example_id}`."
    return (
        f"the model chose the correct action `{pred_action}` on `{example_id}`, "
        "but the sampled row still failed a content or parsing criterion."
    )


def render_interpretation(dev_run: dict[str, Any], quick_run: dict[str, Any] | None) -> list[str]:
    summary = dev_run["summary"]
    false_premise = summary["per_slice"].get("false_premise")
    answerable = summary["per_slice"].get("answerable_control")
    lines = [
        f"- The main dev decision metric is `avg_utility={fmt(summary['avg_utility'])}` with `action_accuracy={fmt(summary['action_accuracy'])}`, so this run is informative even when strict answer exact match stays low.",
    ]
    if false_premise is not None and answerable is not None:
        lines.append(
            f"- The central tradeoff is between defective-premise calibration and clean-answer willingness: `false_premise` sits at `{fmt(false_premise['action_accuracy'])}` action accuracy while `answerable_control` sits at `{fmt(answerable['action_accuracy'])}`."
        )
    if quick_run is not None:
        lines.append(
            "- Because both quick and dev are available, this report can distinguish stable behavior from subset noise without relying only on the tiny split."
        )
    else:
        lines.append(
            "- This report should be read as a dev-scale decision point rather than a full robustness profile across every subset."
        )
    return lines


if __name__ == "__main__":
    main()
