from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SLICE_ORDER = [
    "answerable_control",
    "ask",
    "false_premise",
    "stale_premise",
    "conflicting_evidence",
]
SLICE_DISPLAY_NAMES = {
    "answerable_control": "Answerable",
    "ask": "Ambiguous",
    "false_premise": "False Premise",
    "stale_premise": "Stale Premise",
    "conflicting_evidence": "Conflicting Evidence",
}
ACTION_ORDER = ["answer", "ask", "challenge", "abstain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare one or more metrics JSON files using the project reporting template."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files produced by scripts/run_baseline.py")
    parser.add_argument("--title", default="Run Comparison", help="Markdown heading for the report.")
    parser.add_argument("--output", help="Optional markdown file to write.")
    parser.add_argument(
        "--confusion-for",
        action="append",
        default=[],
        help=(
            "Run label, model name, or 1-based position to emit a confusion table for. "
            "Repeatable. Defaults to the last run."
        ),
    )
    parser.add_argument(
        "--skip-confusion",
        action="store_true",
        help="Do not emit any confusion tables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.paths]
    report = render_report(
        title=args.title,
        runs=runs,
        confusion_runs=resolve_confusion_runs(runs, args.confusion_for, args.skip_confusion),
    )
    print(report)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report + "\n", encoding="utf-8")


def render_report(title: str, runs: list[dict[str, Any]], confusion_runs: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", "", "## Main Table", ""]
    lines.extend(render_main_table(runs))
    lines.extend(["", "## Per-Slice Table", ""])
    lines.extend(render_slice_table(runs))
    if confusion_runs:
        lines.extend(["", "## Confusion Tables", ""])
        lines.extend(render_confusion_tables(confusion_runs))
    return "\n".join(lines).rstrip()


def load_run(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    label = path.stem.replace("_metrics", "")
    meta = infer_run_metadata(label)
    meta["label"] = label
    meta["summary"] = summary
    return meta


def infer_run_metadata(label: str) -> dict[str, str]:
    lowered = label.lower()
    if "gpt5chatlatest" in lowered or "gpt-5-chat-latest" in lowered:
        return {
            "model": "gpt-5-chat-latest",
            "family": "OpenAI API",
            "style": "api",
        }
    if "gpt41mini" in lowered or "gpt-4.1-mini" in lowered:
        return {
            "model": "gpt-4.1-mini",
            "family": "OpenAI API",
            "style": "api",
        }
    if "gpt4omini" in lowered or "gpt-4o-mini" in lowered:
        return {
            "model": "gpt-4o-mini",
            "family": "OpenAI API",
            "style": "api",
        }
    if "qwenpluslatest" in lowered or "qwen-plus-latest" in lowered:
        return {
            "model": "qwen-plus-latest",
            "family": "Qwen API",
            "style": "api",
        }
    if "qwenturbo" in lowered or "qwen-turbo" in lowered:
        return {
            "model": "qwen-turbo",
            "family": "Qwen API",
            "style": "api",
        }
    if "ernie45_03b" in lowered or "ernie-4.5-0.3b" in lowered:
        return {
            "model": "ernie-4.5-0.3b",
            "family": "ERNIE API",
            "style": "api",
        }
    if ("deepseek" in lowered or "r1" in lowered) and ("7b" in lowered or "qwen7b" in lowered):
        return {
            "model": "DeepSeek-R1-Distill-Qwen-7B",
            "family": "DeepSeek/Qwen",
            "style": "reasoning",
        }
    if "deepseek" in lowered or "r1" in lowered:
        return {
            "model": "DeepSeek-R1-Distill-Qwen-1.5B",
            "family": "DeepSeek/Qwen",
            "style": "reasoning",
        }
    if "smollm2" in lowered:
        return {
            "model": "SmolLM2-135M-Instruct",
            "family": "SmolLM2",
            "style": "instruct",
        }
    if "15b" in lowered or "1_5b" in lowered or "1.5b" in lowered:
        return {
            "model": "Qwen2.5-1.5B-Instruct",
            "family": "Qwen2.5",
            "style": "instruct",
        }
    if "coder" in lowered:
        return {
            "model": "Qwen2.5-Coder-7B-Instruct",
            "family": "Qwen2.5-Coder",
            "style": "instruct",
        }
    if "05b" in lowered:
        return {
            "model": "Qwen2.5-0.5B-Instruct",
            "family": "Qwen2.5",
            "style": "instruct",
        }
    return {
        "model": label,
        "family": "unknown",
        "style": "unknown",
    }


def render_main_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        summary = run["summary"]
        lines.append(
            "| "
            + " | ".join(
                [
                    run["model"],
                    run["family"],
                    run["style"],
                    fmt(summary["avg_utility"]),
                    fmt(summary["action_accuracy"]),
                    fmt(summary["answer_em"]),
                    fmt(summary.get("answer_contains_rate", 0.0)),
                    fmt(summary["over_answer_rate"]),
                    fmt(action_precision(summary, "ask")),
                    fmt(action_precision(summary, "challenge")),
                    fmt(action_precision(summary, "abstain")),
                    fmt(summary.get("json_parse_rate", 0.0)),
                ]
            )
            + " |"
        )
    return lines


def render_slice_table(runs: list[dict[str, Any]]) -> list[str]:
    slice_names = ordered_slice_names(runs)
    header = ["Model"] + [display_slice_name(name) for name in slice_names]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for run in runs:
        summary = run["summary"]
        cells = [run["model"]]
        for slice_name in slice_names:
            slice_summary = summary["per_slice"].get(slice_name)
            if slice_summary is None:
                cells.append("-")
                continue
            cells.append(
                f"{fmt(slice_summary['avg_utility'])} / {fmt(slice_summary['action_accuracy'])}"
            )
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def render_confusion_tables(runs: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for index, run in enumerate(runs):
        summary = run["summary"]
        lines.append(f"### {run['model']} (`{run['label']}`)")
        lines.append("")
        lines.append("| Gold \\\\ Pred | answer | ask | challenge | abstain |")
        lines.append("| --- | --- | --- | --- | --- |")
        for gold_action in ACTION_ORDER:
            row = [gold_action]
            for pred_action in ACTION_ORDER:
                row.append(str(confusion_value(summary, gold_action, pred_action)))
            lines.append("| " + " | ".join(row) + " |")
        if index != len(runs) - 1:
            lines.append("")
    return lines


def ordered_slice_names(runs: list[dict[str, Any]]) -> list[str]:
    discovered: list[str] = []
    for run in runs:
        for slice_name in run["summary"]["per_slice"].keys():
            if slice_name not in discovered:
                discovered.append(slice_name)
    ordered = [name for name in DEFAULT_SLICE_ORDER if name in discovered]
    extras = sorted(name for name in discovered if name not in DEFAULT_SLICE_ORDER)
    return ordered + extras


def resolve_confusion_runs(
    runs: list[dict[str, Any]],
    requested_targets: list[str],
    skip_confusion: bool,
) -> list[dict[str, Any]]:
    if skip_confusion or not runs:
        return []
    targets = requested_targets or [str(len(runs))]
    resolved: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    for target in targets:
        run = find_run(runs, target)
        if run["label"] in seen_labels:
            continue
        seen_labels.add(run["label"])
        resolved.append(run)
    return resolved


def find_run(runs: list[dict[str, Any]], target: str) -> dict[str, Any]:
    if target.isdigit():
        index = int(target) - 1
        if 0 <= index < len(runs):
            return runs[index]
        raise ValueError(f"Confusion target index out of range: {target}")

    lowered = target.lower()
    exact_matches = [
        run
        for run in runs
        if lowered in {run["label"].lower(), run["model"].lower()}
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]

    partial_matches = [
        run
        for run in runs
        if lowered in run["label"].lower() or lowered in run["model"].lower()
    ]
    if len(partial_matches) == 1:
        return partial_matches[0]
    if exact_matches or partial_matches:
        raise ValueError(f"Confusion target is ambiguous: {target}")
    raise ValueError(f"Unknown confusion target: {target}")


def display_slice_name(slice_name: str) -> str:
    return SLICE_DISPLAY_NAMES.get(slice_name, slice_name.replace("_", " ").title())


def confusion_value(summary: dict[str, Any], gold_action: str, pred_action: str) -> int:
    return int(summary.get("confusion", {}).get(gold_action, {}).get(pred_action, 0))


def action_precision(summary: dict[str, Any], action: str) -> float:
    predicted_total = summary.get("pred_action_counts", {}).get(action, 0)
    if predicted_total == 0:
        return 0.0
    true_positive = confusion_value(summary, action, action)
    return round(true_positive / predicted_total, 4)


def fmt(value: float | int) -> str:
    return f"{float(value):.4f}".rstrip("0").rstrip(".")


if __name__ == "__main__":
    main()
