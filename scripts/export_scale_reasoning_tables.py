from __future__ import annotations

import argparse
from pathlib import Path

from compare_runs import (
    SLICE_DISPLAY_NAMES,
    action_precision,
    fmt,
    load_run,
    ordered_slice_names,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export the current day-1 scale/reasoning comparison as paper-ready LaTeX tables."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files to export.")
    parser.add_argument(
        "--output-dir",
        default="experiments/day1/tables",
        help="Directory used for emitted .tex snippets.",
    )
    parser.add_argument(
        "--prefix",
        default="day1_scale_reasoning",
        help="Filename prefix for the emitted table snippets.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.paths]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    main_path = output_dir / f"{args.prefix}_main.tex"
    slice_path = output_dir / f"{args.prefix}_per_slice.tex"
    main_path.write_text(render_main_table_tex(runs) + "\n", encoding="utf-8")
    slice_path.write_text(render_slice_table_tex(runs) + "\n", encoding="utf-8")


def render_main_table_tex(runs: list[dict]) -> str:
    best = best_main_values(runs)
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4.5pt}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lllrrrrrr}",
        r"\toprule",
        r"Model & Family & Style & Utility & Action Acc. & Answer Contains & Over-Answer & Challenge Prec. & JSON Parse \\",
        r"\midrule",
    ]
    for run in runs:
        summary = run["summary"]
        cells = [
            latex_escape(run["model"]),
            latex_escape(run["family"]),
            latex_escape(run["style"]),
            highlight_if_best(fmt(summary["avg_utility"]), summary["avg_utility"], best["avg_utility"]),
            highlight_if_best(fmt(summary["action_accuracy"]), summary["action_accuracy"], best["action_accuracy"]),
            highlight_if_best(
                fmt(summary.get("answer_contains_rate", 0.0)),
                summary.get("answer_contains_rate", 0.0),
                best["answer_contains_rate"],
            ),
            highlight_if_best(
                fmt(summary["over_answer_rate"]),
                summary["over_answer_rate"],
                best["over_answer_rate"],
            ),
            highlight_if_best(
                fmt(action_precision(summary, "challenge")),
                action_precision(summary, "challenge"),
                best["challenge_precision"],
            ),
            highlight_if_best(
                fmt(summary.get("json_parse_rate", 0.0)),
                summary.get("json_parse_rate", 0.0),
                best["json_parse_rate"],
            ),
        ]
        lines.append(" & ".join(cells) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            r"\caption{Day-1 development comparison for the completed local model matrix. The main decision metrics are utility, action accuracy, and over-answer rate; answer containment and JSON parse rate diagnose content and protocol adherence. Higher is better except over-answer rate.}",
            r"\label{tab:day1-scale-reasoning-main}",
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
        r"\setlength{\tabcolsep}{4.0pt}",
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        header,
        r"\midrule",
    ]
    for run in runs:
        summary = run["summary"]
        cells = [latex_escape(run["model"])]
        for slice_name in slice_names:
            slice_summary = summary["per_slice"].get(slice_name)
            if slice_summary is None:
                cells.append(r"--")
                continue
            cells.append(
                latex_escape(
                    f"{fmt(slice_summary['avg_utility'])} / {fmt(slice_summary['action_accuracy'])}"
                )
            )
        lines.append(" & ".join(cells) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Per-slice utility / action-accuracy pairs on Day-1 development. The slice table shows that model errors are structured by input defect type rather than explained by a single pooled score.}",
            r"\label{tab:day1-scale-reasoning-slices}",
            r"\end{table*}",
        ]
    )
    return "\n".join(lines)


def best_main_values(runs: list[dict]) -> dict[str, tuple[float, bool]]:
    challenge_precisions = [action_precision(run["summary"], "challenge") for run in runs]
    return {
        "avg_utility": best_value_with_variation([run["summary"]["avg_utility"] for run in runs], higher_is_better=True),
        "action_accuracy": best_value_with_variation(
            [run["summary"]["action_accuracy"] for run in runs], higher_is_better=True
        ),
        "answer_em": best_value_with_variation([run["summary"]["answer_em"] for run in runs], higher_is_better=True),
        "answer_contains_rate": best_value_with_variation(
            [run["summary"].get("answer_contains_rate", 0.0) for run in runs],
            higher_is_better=True,
        ),
        "over_answer_rate": best_value_with_variation(
            [run["summary"]["over_answer_rate"] for run in runs], higher_is_better=False
        ),
        "challenge_precision": best_value_with_variation(challenge_precisions, higher_is_better=True),
        "json_parse_rate": best_value_with_variation(
            [run["summary"].get("json_parse_rate", 0.0) for run in runs],
            higher_is_better=True,
        ),
    }


def best_value_with_variation(values: list[float], *, higher_is_better: bool) -> tuple[float, bool]:
    best_value = max(values) if higher_is_better else min(values)
    has_variation = any(abs(value - best_value) > 1e-12 for value in values)
    return best_value, has_variation


def highlight_if_best(rendered: str, value: float, best_info: tuple[float, bool]) -> str:
    best_value, has_variation = best_info
    if has_variation and abs(value - best_value) < 1e-12:
        return rf"\textbf{{{rendered}}}"
    return rendered


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
