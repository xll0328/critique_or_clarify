from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from compare_runs import fmt, load_run
from export_scale_reasoning_tables import latex_escape


MODEL_PREFIXES = {
    "Qwen2.5-0.5B-Instruct": "DayOneQuickStaleQwenZeroPointFiveB",
    "Qwen2.5-1.5B-Instruct": "DayOneQuickStaleQwenOnePointFiveB",
    "Qwen2.5-Coder-7B-Instruct": "DayOneQuickStaleQwenCoderSevenB",
    "DeepSeek-R1-Distill-Qwen-1.5B": "DayOneQuickStaleDeepSeekOnePointFiveB",
    "DeepSeek-R1-Distill-Qwen-7B": "DayOneQuickStaleDeepSeekSevenB",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export stable LaTeX macros for the Day-1 quick+stale snapshot."
    )
    parser.add_argument("paths", nargs="+", help="Quick+stale metric JSON files to export.")
    parser.add_argument(
        "--output",
        default="experiments/day1/tables/day1_quick_stale_macros.tex",
        help="Output path for emitted LaTeX macros.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.paths]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_macros(runs) + "\n", encoding="utf-8")


def render_macros(runs: list[dict[str, Any]]) -> str:
    runs_by_model = {run["model"]: run for run in runs}
    macros: list[str] = []

    for model, prefix in MODEL_PREFIXES.items():
        macros.extend(render_model_macros(prefix, model, runs_by_model.get(model)))

    best_instruct = max(
        (run for run in runs if run["style"] == "instruct"),
        key=lambda run: (run["summary"]["avg_utility"], run["summary"]["action_accuracy"]),
        default=None,
    )
    macros.extend(
        [
            macro("DayOneQuickStaleBestInstructModel", best_instruct["model"] if best_instruct else "NA"),
            macro(
                "DayOneQuickStaleBestInstructActionAcc",
                fmt(best_instruct["summary"]["action_accuracy"]) if best_instruct else "NA",
            ),
            macro(
                "DayOneQuickStaleBestInstructUtility",
                fmt(best_instruct["summary"]["avg_utility"]) if best_instruct else "NA",
            ),
        ]
    )

    deepseek = runs_by_model.get("DeepSeek-R1-Distill-Qwen-7B")
    qwen = runs_by_model.get("Qwen2.5-1.5B-Instruct")
    if deepseek is not None and qwen is not None:
        macros.extend(
            [
                macro(
                    "DayOneQuickStaleDeepSeekSevenBDeltaVsQwenOnePointFiveBActionAcc",
                    format_delta(deepseek["summary"]["action_accuracy"] - qwen["summary"]["action_accuracy"]),
                ),
                macro(
                    "DayOneQuickStaleDeepSeekSevenBDeltaVsQwenOnePointFiveBUtility",
                    format_delta(deepseek["summary"]["avg_utility"] - qwen["summary"]["avg_utility"]),
                ),
            ]
        )
    else:
        macros.extend(
            [
                macro("DayOneQuickStaleDeepSeekSevenBDeltaVsQwenOnePointFiveBActionAcc", "NA"),
                macro("DayOneQuickStaleDeepSeekSevenBDeltaVsQwenOnePointFiveBUtility", "NA"),
            ]
        )

    return "\n".join(macros)


def render_model_macros(prefix: str, model: str, run: dict[str, Any] | None) -> list[str]:
    if run is None:
        return [
            macro(f"{prefix}Model", model),
            macro(f"{prefix}ActionAcc", "NA"),
            macro(f"{prefix}Utility", "NA"),
            macro(f"{prefix}OverAnswer", "NA"),
            macro(f"{prefix}JsonParse", "NA"),
            macro(f"{prefix}AnswerableControlAcc", "NA"),
            macro(f"{prefix}FalsePremiseAcc", "NA"),
            macro(f"{prefix}FalsePremiseOverAnswer", "NA"),
            macro(f"{prefix}StalePremiseAcc", "NA"),
            macro(f"{prefix}StalePremiseOverAnswer", "NA"),
            macro(f"{prefix}ConflictingEvidenceAcc", "NA"),
        ]

    summary = run["summary"]
    return [
        macro(f"{prefix}Model", model),
        macro(f"{prefix}ActionAcc", fmt(summary["action_accuracy"])),
        macro(f"{prefix}Utility", fmt(summary["avg_utility"])),
        macro(f"{prefix}OverAnswer", fmt(summary["over_answer_rate"])),
        macro(f"{prefix}JsonParse", fmt(summary.get("json_parse_rate", 0.0))),
        macro(f"{prefix}AnswerableControlAcc", fmt(slice_metric(summary, "answerable_control", "action_accuracy"))),
        macro(f"{prefix}FalsePremiseAcc", fmt(slice_metric(summary, "false_premise", "action_accuracy"))),
        macro(f"{prefix}FalsePremiseOverAnswer", fmt(slice_metric(summary, "false_premise", "over_answer_rate"))),
        macro(f"{prefix}StalePremiseAcc", fmt(slice_metric(summary, "stale_premise", "action_accuracy"))),
        macro(f"{prefix}StalePremiseOverAnswer", fmt(slice_metric(summary, "stale_premise", "over_answer_rate"))),
        macro(f"{prefix}ConflictingEvidenceAcc", fmt(slice_metric(summary, "conflicting_evidence", "action_accuracy"))),
    ]


def slice_metric(summary: dict[str, Any], slice_name: str, metric_name: str) -> float:
    return float(summary["per_slice"].get(slice_name, {}).get(metric_name, 0.0))


def format_delta(value: float) -> str:
    return f"{value:+.4f}".rstrip("0").rstrip(".")


def macro(name: str, value: str) -> str:
    return rf"\newcommand{{\{name}}}{{{latex_escape(value)}}}"


if __name__ == "__main__":
    main()
