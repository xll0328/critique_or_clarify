from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Callable

from compare_runs import SLICE_DISPLAY_NAMES, fmt, infer_run_metadata, ordered_slice_names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export bootstrap confidence-interval tables for the current day-1 scale/reasoning comparison."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files that include per-example details.")
    parser.add_argument(
        "--output-md",
        help="Optional markdown report path.",
    )
    parser.add_argument(
        "--output-dir",
        default="experiments/day1/tables",
        help="Directory used for emitted LaTeX snippets.",
    )
    parser.add_argument(
        "--prefix",
        default="day1_scale_reasoning_ci",
        help="Filename prefix for emitted LaTeX snippets.",
    )
    parser.add_argument(
        "--title",
        default="Day-1 Bootstrap Confidence Intervals",
        help="Markdown heading for the optional report.",
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
        default=0,
        help="Base random seed for deterministic interval generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.paths]
    summarize_runs(runs, samples=args.samples, seed=args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    main_tex_path = output_dir / f"{args.prefix}_main.tex"
    slice_tex_path = output_dir / f"{args.prefix}_per_slice.tex"
    main_tex_path.write_text(render_main_table_tex(runs) + "\n", encoding="utf-8")
    slice_tex_path.write_text(render_slice_table_tex(runs) + "\n", encoding="utf-8")

    if args.output_md:
        output_path = Path(args.output_md)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_markdown_report(args.title, runs, args.samples) + "\n", encoding="utf-8")


def load_run(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "details" not in payload:
        raise ValueError(f"Metric file does not include per-example details: {path}")
    label = path.stem.replace("_metrics", "")
    meta = infer_run_metadata(label)
    meta["label"] = label
    meta["summary"] = payload["summary"]
    meta["details"] = payload["details"]
    return meta


def summarize_runs(runs: list[dict], *, samples: int, seed: int) -> None:
    for run_index, run in enumerate(runs):
        details = run["details"]
        run["bootstrap"] = {
            "avg_utility": bootstrap_mean(
                [float(detail["utility"]) for detail in details],
                samples=samples,
                seed=seed + 1000 * run_index + 1,
            ),
            "action_accuracy": bootstrap_mean(
                [1.0 if detail["action_correct"] else 0.0 for detail in details],
                samples=samples,
                seed=seed + 1000 * run_index + 2,
            ),
            "over_answer_rate": bootstrap_mean(
                [1.0 if is_over_answer(detail) else 0.0 for detail in details],
                samples=samples,
                seed=seed + 1000 * run_index + 3,
            ),
            "per_slice": {},
        }

        for slice_index, slice_name in enumerate(run["summary"].get("per_slice", {})):
            slice_details = [detail for detail in details if detail.get("slice") == slice_name]
            if not slice_details:
                continue
            run["bootstrap"]["per_slice"][slice_name] = bootstrap_mean(
                [1.0 if detail["action_correct"] else 0.0 for detail in slice_details],
                samples=samples,
                seed=seed + 1000 * run_index + 100 + slice_index,
            )


def is_over_answer(detail: dict) -> bool:
    return detail.get("pred_action") == "answer" and detail.get("gold_action") != "answer"


def bootstrap_mean(values: list[float], *, samples: int, seed: int) -> dict[str, float | int]:
    if not values:
        raise ValueError("Cannot bootstrap an empty value list.")
    point = sum(values) / len(values)
    if samples <= 0:
        return {"count": len(values), "point": point, "low": point, "high": point}

    rng = random.Random(seed)
    n = len(values)
    estimates: list[float] = []
    for _ in range(samples):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        estimates.append(total / n)
    estimates.sort()
    return {
        "count": n,
        "point": point,
        "low": percentile(estimates, 0.025),
        "high": percentile(estimates, 0.975),
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("Cannot compute a percentile from an empty list.")
    if q <= 0:
        return values[0]
    if q >= 1:
        return values[-1]
    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def render_markdown_report(title: str, runs: list[dict], samples: int) -> str:
    lines = [
        f"# {title}",
        "",
        f"Bootstrap 95% percentile intervals computed from per-example outcomes with `{samples}` resamples per run.",
        "",
        "## Main Table",
        "",
    ]
    lines.extend(render_main_table_md(runs))
    lines.extend(["", "## Per-Slice Action Accuracy", ""])
    lines.extend(render_slice_table_md(runs))
    return "\n".join(lines).rstrip()


def render_main_table_md(runs: list[dict]) -> list[str]:
    lines = [
        "| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | n |",
        "| --- | --- | --- | --- | --- |",
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
                    str(intervals["action_accuracy"]["count"]),
                ]
            )
            + " |"
        )
    return lines


def render_slice_table_md(runs: list[dict]) -> list[str]:
    slice_names = ordered_slice_names(runs)
    header = ["Model"] + [display_slice_name(slice_name) for slice_name in slice_names]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for run in runs:
        cells = [run["model"]]
        for slice_name in slice_names:
            interval = run["bootstrap"]["per_slice"].get(slice_name)
            cells.append(render_interval(interval) if interval else "-")
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def render_main_table_tex(runs: list[dict]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4.0pt}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Model & Utility (95\% CI) & Action Acc. (95\% CI) & Over-Answer (95\% CI) & $n$ \\",
        r"\midrule",
    ]
    for run in runs:
        intervals = run["bootstrap"]
        cells = [
            latex_escape(run["model"]),
            latex_escape(render_interval(intervals["avg_utility"])),
            latex_escape(render_interval(intervals["action_accuracy"])),
            latex_escape(render_interval(intervals["over_answer_rate"])),
            str(intervals["action_accuracy"]["count"]),
        ]
        lines.append(" & ".join(cells) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Bootstrap 95\% percentile intervals for the current day-1 scale/reasoning comparison.}",
            r"\label{tab:day1-scale-reasoning-ci-main}",
            r"\end{table*}",
        ]
    )
    return "\n".join(lines)


def render_slice_table_tex(runs: list[dict]) -> str:
    slice_names = ordered_slice_names(runs)
    alignment = "l" + "c" * len(slice_names)
    header = " & ".join(["Model"] + [latex_escape(display_slice_name(name)) for name in slice_names]) + r" \\"
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{3.8pt}",
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        header,
        r"\midrule",
    ]
    for run in runs:
        cells = [latex_escape(run["model"])]
        for slice_name in slice_names:
            interval = run["bootstrap"]["per_slice"].get(slice_name)
            cells.append(latex_escape(render_interval(interval)) if interval else r"--")
        lines.append(" & ".join(cells) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Per-slice bootstrap 95\% percentile intervals for action accuracy on day-1 development.}",
            r"\label{tab:day1-scale-reasoning-ci-slices}",
            r"\end{table*}",
        ]
    )
    return "\n".join(lines)


def render_interval(interval: dict[str, float | int] | None) -> str:
    if interval is None:
        return "-"
    return f"{fmt(float(interval['point']))} [{fmt(float(interval['low']))}, {fmt(float(interval['high']))}]"


def display_slice_name(slice_name: str) -> str:
    return SLICE_DISPLAY_NAMES.get(slice_name, slice_name.replace("_", " ").title())


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


if __name__ == "__main__":
    main()
