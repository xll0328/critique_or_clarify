from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from compare_runs import fmt, infer_run_metadata
from export_scale_reasoning_bootstrap import bootstrap_mean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a report for the expanded stale-premise pool pilot."
    )
    parser.add_argument("metrics", nargs="+", help="Metric JSON files from the expanded stale pool runs.")
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_expanded_stale_pool_pilot.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--split",
        default="data/processed/day1_quick_plus_stale_pool.jsonl",
        help="Expanded stale-pool split path to mention in the report.",
    )
    parser.add_argument(
        "--output-dir",
        default="experiments/day1/tables",
        help="Directory for emitted LaTeX snippets.",
    )
    parser.add_argument(
        "--prefix",
        default="day1_expanded_stale_pool_pilot",
        help="Filename prefix for emitted LaTeX snippets.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=2000,
        help="Number of bootstrap resamples per metric.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=17,
        help="Base random seed for deterministic bootstrap intervals.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.metrics]
    summarize_bootstrap(runs, samples=args.samples, seed=args.seed)
    report = render_report(runs, split_path=args.split)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tex_path = output_dir / f"{args.prefix}_main.tex"
    tex_path.write_text(render_latex_table(runs) + "\n", encoding="utf-8")
    print(f"Wrote {output_path} using {len(runs)} run(s).")


def load_run(metric_path: Path) -> dict[str, Any]:
    payload = json.loads(metric_path.read_text(encoding="utf-8"))
    label = metric_path.stem.replace("_metrics", "")
    run = infer_run_metadata(label)
    run["label"] = label
    run["path"] = str(metric_path)
    run["summary"] = payload["summary"]
    run["details"] = payload.get("details", [])
    return run


def summarize_bootstrap(runs: list[dict[str, Any]], *, samples: int, seed: int) -> None:
    for index, run in enumerate(runs):
        details = run.get("details", [])
        if not details:
            run["bootstrap"] = {}
            continue
        stale_details = [detail for detail in details if detail.get("slice") == "stale_premise"]
        run["bootstrap"] = {
            "action_accuracy": bootstrap_mean(
                [1.0 if detail["action_correct"] else 0.0 for detail in details],
                samples=samples,
                seed=seed + index * 1000 + 1,
            ),
            "avg_utility": bootstrap_mean(
                [float(detail["utility"]) for detail in details],
                samples=samples,
                seed=seed + index * 1000 + 2,
            ),
            "over_answer_rate": bootstrap_mean(
                [1.0 if is_over_answer(detail) else 0.0 for detail in details],
                samples=samples,
                seed=seed + index * 1000 + 3,
            ),
            "stale_action_accuracy": bootstrap_mean(
                [1.0 if detail["action_correct"] else 0.0 for detail in stale_details],
                samples=samples,
                seed=seed + index * 1000 + 4,
            ),
            "stale_avg_utility": bootstrap_mean(
                [float(detail["utility"]) for detail in stale_details],
                samples=samples,
                seed=seed + index * 1000 + 5,
            ),
            "stale_over_answer_rate": bootstrap_mean(
                [1.0 if is_over_answer(detail) else 0.0 for detail in stale_details],
                samples=samples,
                seed=seed + index * 1000 + 6,
            ),
        }


def is_over_answer(detail: dict[str, Any]) -> bool:
    return detail.get("pred_action") == "answer" and detail.get("gold_action") != "answer"


def render_report(runs: list[dict[str, Any]], *, split_path: str) -> str:
    lines = [
        "# Expanded Stale-Premise Pool Pilot",
        "",
        f"This pilot uses `{split_path}`. It is not part of the main day-1 comparison table until all reported models are rerun on this same expanded split.",
        "",
        "## Split",
        "",
        "| Split | N | Answerable | False Premise | Stale Premise | Conflicting Evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    split_summary = summarize_split(runs[0]["summary"])
    lines.append(
        "| "
        + " | ".join(
            [
                Path(split_path).name,
                str(split_summary["total"]),
                str(split_summary.get("answerable_control", 0)),
                str(split_summary.get("false_premise", 0)),
                str(split_summary.get("stale_premise", 0)),
                str(split_summary.get("conflicting_evidence", 0)),
            ]
        )
        + " |"
    )
    lines.extend(["", "## Results", ""])
    lines.extend(render_results_table(runs))
    if all(run.get("bootstrap") for run in runs):
        lines.extend(["", "## Bootstrap 95% CIs", ""])
        lines.extend(render_bootstrap_table(runs))
    lines.extend(["", "## Qwen Scale Signal", ""])
    lines.extend(render_qwen_scale_signal(runs))
    lines.extend(["", "## Matched 1.5B Contrast", ""])
    lines.extend(render_matched_contrast(runs))
    lines.extend(["", "## Failure Pattern", ""])
    lines.extend(render_failure_pattern(runs))
    return "\n".join(lines).rstrip()


def summarize_split(summary: dict[str, Any]) -> dict[str, int]:
    per_slice = summary["per_slice"]
    split_summary = {slice_name: int(stats["count"]) for slice_name, stats in per_slice.items()}
    split_summary["total"] = int(summary["num_examples"])
    return split_summary


def render_results_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Model | Style | N | Utility | Action Acc. | Over-Answer | JSON Parse | Stale Acc. | Stale Utility | Stale Over-Answer |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        summary = run["summary"]
        stale = summary["per_slice"].get("stale_premise", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    run["model"],
                    run["style"],
                    str(summary["num_examples"]),
                    fmt(summary["avg_utility"]),
                    fmt(summary["action_accuracy"]),
                    fmt(summary["over_answer_rate"]),
                    fmt(summary.get("json_parse_rate", 0.0)),
                    fmt(stale.get("action_accuracy", 0.0)),
                    fmt(stale.get("avg_utility", 0.0)),
                    fmt(stale.get("over_answer_rate", 0.0)),
                ]
            )
            + " |"
        )
    return lines


def render_bootstrap_table(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | Stale Acc. (95% CI) | Stale Over-Answer (95% CI) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        intervals = run["bootstrap"]
        lines.append(
            "| "
            + " | ".join(
                [
                    run["model"],
                    render_interval(intervals["avg_utility"]),
                    render_interval(intervals["action_accuracy"]),
                    render_interval(intervals["over_answer_rate"]),
                    render_interval(intervals["stale_action_accuracy"]),
                    render_interval(intervals["stale_over_answer_rate"]),
                ]
            )
            + " |"
        )
    return lines


def render_latex_table(runs: list[dict[str, Any]]) -> str:
    has_bootstrap = all(run.get("bootstrap") for run in runs)
    if has_bootstrap:
        header = (
            r"Model & Style & Utility (95\% CI) & Action Acc. (95\% CI) & "
            r"Stale Acc. (95\% CI) & Stale Over-Answer (95\% CI) \\"
        )
        rows = []
        for run in runs:
            intervals = run["bootstrap"]
            rows.append(
                " & ".join(
                    [
                        latex_escape(run["model"]),
                        latex_escape(run["style"]),
                        latex_escape(render_interval(intervals["avg_utility"])),
                        latex_escape(render_interval(intervals["action_accuracy"])),
                        latex_escape(render_interval(intervals["stale_action_accuracy"])),
                        latex_escape(render_interval(intervals["stale_over_answer_rate"])),
                    ]
                )
                + r" \\"
            )
        alignment = "llcccc"
    else:
        header = r"Model & Style & Utility & Action Acc. & Stale Acc. & Stale Over-Answer \\"
        rows = []
        for run in runs:
            summary = run["summary"]
            stale = summary["per_slice"]["stale_premise"]
            rows.append(
                " & ".join(
                    [
                        latex_escape(run["model"]),
                        latex_escape(run["style"]),
                        fmt(summary["avg_utility"]),
                        fmt(summary["action_accuracy"]),
                        fmt(stale["action_accuracy"]),
                        fmt(stale["over_answer_rate"]),
                    ]
                )
                + r" \\"
            )
        alignment = "llcccc"

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{3.6pt}",
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        header,
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Expanded stale-premise pool pilot. This table is separate from the main day-1 comparison until all reported models are rerun on the same expanded split.}",
        r"\label{tab:day1-expanded-stale-pool-pilot}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def render_matched_contrast(runs: list[dict[str, Any]]) -> list[str]:
    qwen = next((run for run in runs if run["model"] == "Qwen2.5-1.5B-Instruct"), None)
    deepseek = next((run for run in runs if run["model"] == "DeepSeek-R1-Distill-Qwen-1.5B"), None)
    if qwen is None or deepseek is None:
        return ["- The matched 1.5B instruct-vs-reasoning pilot is incomplete."]

    qwen_summary = qwen["summary"]
    deepseek_summary = deepseek["summary"]
    qwen_stale = qwen_summary["per_slice"]["stale_premise"]
    deepseek_stale = deepseek_summary["per_slice"]["stale_premise"]
    return [
        f"- Overall, DeepSeek-R1-Distill-Qwen-1.5B changes action accuracy by `{delta(deepseek_summary['action_accuracy'], qwen_summary['action_accuracy'])}` and utility by `{delta(deepseek_summary['avg_utility'], qwen_summary['avg_utility'])}` relative to Qwen2.5-1.5B-Instruct.",
        f"- On stale premises, DeepSeek-R1-Distill-Qwen-1.5B changes action accuracy by `{delta(deepseek_stale['action_accuracy'], qwen_stale['action_accuracy'])}` and over-answer rate by `{delta(deepseek_stale['over_answer_rate'], qwen_stale['over_answer_rate'])}`.",
        "- The expanded pool therefore strengthens the current caution: reasoning traces do not by themselves produce the desired `challenge` action under stale premises.",
    ]


def render_qwen_scale_signal(runs: list[dict[str, Any]]) -> list[str]:
    small = next((run for run in runs if run["model"] == "Qwen2.5-0.5B-Instruct"), None)
    larger = next((run for run in runs if run["model"] == "Qwen2.5-1.5B-Instruct"), None)
    if small is None or larger is None:
        return ["- The expanded-pool Qwen scale pilot is incomplete."]

    small_summary = small["summary"]
    larger_summary = larger["summary"]
    small_stale = small_summary["per_slice"]["stale_premise"]
    larger_stale = larger_summary["per_slice"]["stale_premise"]
    return [
        f"- From Qwen2.5-0.5B to Qwen2.5-1.5B, overall action accuracy changes by `{delta(larger_summary['action_accuracy'], small_summary['action_accuracy'])}` and utility by `{delta(larger_summary['avg_utility'], small_summary['avg_utility'])}`.",
        f"- On stale premises, action accuracy changes by `{delta(larger_stale['action_accuracy'], small_stale['action_accuracy'])}` and over-answer rate changes by `{delta(larger_stale['over_answer_rate'], small_stale['over_answer_rate'])}`.",
        "- This makes the expanded stale pool useful as a scale-sensitive diagnostic rather than a saturated hand-written probe.",
    ]


def render_failure_pattern(runs: list[dict[str, Any]]) -> list[str]:
    lines = [
        "- The expanded stale pool remains diagnostic: failures persist even when the update passage states the corrected fact directly.",
        "- Qwen2.5-0.5B mostly fails stale premises by direct over-answering, which is the low-capability anchor for the scale story.",
        "- Qwen2.5-1.5B often knows the corrected fact but labels the response as `answer` rather than `challenge`, which isolates action selection from factual retrieval.",
    ]
    if any(run["style"] == "reasoning" for run in runs):
        lines.append(
            "- DeepSeek-R1-Distill-Qwen-1.5B mostly fails through fallback-format reasoning, `ask`, or `abstain`, so its weakness is both instruction compliance and action policy."
        )
    return lines


def delta(target: float, source: float) -> str:
    value = target - source
    if value > 0:
        return f"+{fmt(value)}"
    return fmt(value)


def render_interval(interval: dict[str, float | int]) -> str:
    return f"{fmt(float(interval['point']))} [{fmt(float(interval['low']))}, {fmt(float(interval['high']))}]"


def latex_escape(text: str) -> str:
    return (
        str(text)
        .replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


if __name__ == "__main__":
    main()
