from __future__ import annotations

import argparse
from pathlib import Path

from build_day1_pairwise_deltas import (
    consecutive_pairs,
    enrich_run,
    format_delta,
    matched_style_pairs,
    pair_delta,
    size_label,
    slice_drop_text,
    slice_gain_text,
)
from build_day1_snapshot_takeaways import aggregate_slice_accuracy
from compare_runs import SLICE_DISPLAY_NAMES, fmt
from export_scale_reasoning_tables import latex_escape


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export stable LaTeX macros for the current day-1 scale/reasoning snapshot."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files to export.")
    parser.add_argument(
        "--output",
        default="experiments/day1/tables/day1_scale_reasoning_macros.tex",
        help="Output path for emitted LaTeX macros.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [enrich_run(Path(raw_path)) for raw_path in args.paths]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_macros(runs) + "\n", encoding="utf-8")


def render_macros(runs: list[dict]) -> str:
    best_overall = max(runs, key=lambda run: (run["summary"]["avg_utility"], run["summary"]["action_accuracy"]))
    average_slice_acc = aggregate_slice_accuracy(runs)
    hardest_slice, hardest_slice_acc = min(average_slice_acc.items(), key=lambda item: item[1])
    easiest_slice, easiest_slice_acc = max(average_slice_acc.items(), key=lambda item: item[1])
    best_instruct = max(
        (run for run in runs if run["style"] == "instruct"),
        key=lambda run: (run["summary"]["avg_utility"], run["summary"]["action_accuracy"]),
        default=None,
    )
    best_reasoning = max(
        (run for run in runs if run["style"] == "reasoning"),
        key=lambda run: (run["summary"]["avg_utility"], run["summary"]["action_accuracy"]),
        default=None,
    )

    instruct_runs = sorted(
        (run for run in runs if run["style"] == "instruct" and run["size_b"] is not None),
        key=lambda run: (run["size_b"], run["model"]),
    )
    instruct_pairs = consecutive_pairs(instruct_runs)
    best_instruct_step = (
        max(instruct_pairs, key=lambda pair: pair_delta(pair[0], pair[1])["action_accuracy"])
        if instruct_pairs
        else None
    )

    matched_pairs = matched_style_pairs(
        instruct_runs,
        sorted(
            (run for run in runs if run["style"] == "reasoning" and run["size_b"] is not None),
            key=lambda run: (run["size_b"], run["model"]),
        ),
    )
    largest_matched_pair = max(
        matched_pairs,
        key=lambda pair: (pair[0]["size_b"], pair[0]["summary"]["avg_utility"]),
        default=None,
    )

    macros = [
        macro("DayOneScaleReasoningFrontierModel", best_overall["model"]),
        macro("DayOneScaleReasoningFrontierActionAcc", fmt(best_overall["summary"]["action_accuracy"])),
        macro("DayOneScaleReasoningFrontierUtility", fmt(best_overall["summary"]["avg_utility"])),
        macro("DayOneScaleReasoningHardestSlice", display_slice_name(hardest_slice)),
        macro("DayOneScaleReasoningHardestSliceMeanAcc", fmt(hardest_slice_acc)),
        macro("DayOneScaleReasoningEasiestSlice", display_slice_name(easiest_slice)),
        macro("DayOneScaleReasoningEasiestSliceMeanAcc", fmt(easiest_slice_acc)),
        macro(
            "DayOneScaleReasoningBestInstructModel",
            best_instruct["model"] if best_instruct is not None else "NA",
        ),
        macro(
            "DayOneScaleReasoningBestReasoningModel",
            best_reasoning["model"] if best_reasoning is not None else "NA",
        ),
        macro(
            "DayOneScaleReasoningBestReasoningActionAcc",
            fmt(best_reasoning["summary"]["action_accuracy"]) if best_reasoning is not None else "NA",
        ),
        macro(
            "DayOneScaleReasoningBestReasoningUtility",
            fmt(best_reasoning["summary"]["avg_utility"]) if best_reasoning is not None else "NA",
        ),
        macro(
            "DayOneScaleReasoningBestReasoningJsonParse",
            fmt(best_reasoning["summary"]["json_parse_rate"]) if best_reasoning is not None else "NA",
        ),
        macro(
            "DayOneScaleReasoningStrongestInstructStepStatus",
            "available" if best_instruct_step is not None else "pending",
        ),
    ]
    macros.extend(render_named_model_macros(runs, "Qwen2.5-1.5B-Instruct", "DayOneScaleReasoningQwenOnePointFiveB"))
    macros.extend(render_named_model_macros(runs, "Qwen2.5-Coder-7B-Instruct", "DayOneScaleReasoningQwenCoderSevenB"))
    macros.extend(render_instruct_step_macros(best_instruct_step))
    macros.extend(render_matched_pair_macros(largest_matched_pair))
    return "\n".join(macros)


def render_named_model_macros(runs: list[dict], model: str, prefix: str) -> list[str]:
    run = next((candidate for candidate in runs if candidate["model"] == model), None)
    if run is None:
        return [
            macro(f"{prefix}Model", model),
            macro(f"{prefix}ActionAcc", "NA"),
            macro(f"{prefix}Utility", "NA"),
            macro(f"{prefix}FalsePremiseAcc", "NA"),
            macro(f"{prefix}AnswerableAcc", "NA"),
            macro(f"{prefix}OverAnswer", "NA"),
        ]

    return [
        macro(f"{prefix}Model", model),
        macro(f"{prefix}ActionAcc", fmt(run["summary"]["action_accuracy"])),
        macro(f"{prefix}Utility", fmt(run["summary"]["avg_utility"])),
        macro(f"{prefix}FalsePremiseAcc", fmt(slice_action_accuracy(run, "false_premise"))),
        macro(f"{prefix}AnswerableAcc", fmt(slice_action_accuracy(run, "answerable_control"))),
        macro(f"{prefix}OverAnswer", fmt(run["summary"]["over_answer_rate"])),
    ]


def render_instruct_step_macros(pair: tuple[dict, dict] | None) -> list[str]:
    if pair is None:
        return [
            macro("DayOneScaleReasoningStrongestInstructStepFrom", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepTo", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepDeltaActionAcc", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepDeltaUtility", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepDeltaJsonParse", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepBiggestGain", "NA"),
            macro("DayOneScaleReasoningStrongestInstructStepBiggestDrop", "NA"),
        ]
    source, target = pair
    delta = pair_delta(source, target)
    return [
        macro("DayOneScaleReasoningStrongestInstructStepFrom", source["model"]),
        macro("DayOneScaleReasoningStrongestInstructStepTo", target["model"]),
        macro("DayOneScaleReasoningStrongestInstructStepDeltaActionAcc", format_delta(delta["action_accuracy"])),
        macro("DayOneScaleReasoningStrongestInstructStepDeltaUtility", format_delta(delta["avg_utility"])),
        macro("DayOneScaleReasoningStrongestInstructStepDeltaJsonParse", format_delta(delta["json_parse_rate"])),
        macro("DayOneScaleReasoningStrongestInstructStepBiggestGain", slice_gain_text(delta["largest_gain"])),
        macro("DayOneScaleReasoningStrongestInstructStepBiggestDrop", slice_drop_text(delta["largest_drop"])),
    ]


def render_matched_pair_macros(pair: tuple[dict, dict] | None) -> list[str]:
    if pair is None:
        return [
            macro("DayOneScaleReasoningMatchedStatus", "pending"),
            macro("DayOneScaleReasoningLargestMatchedSize", "NA"),
            macro("DayOneScaleReasoningLargestMatchedInstructModel", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningModel", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningActionAcc", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningUtility", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningJsonParse", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningNumExamples", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningPredAnswerCount", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningPredAskCount", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningPredChallengeCount", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningPredAbstainCount", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningFalsePremiseAcc", "NA"),
            macro("DayOneScaleReasoningLargestMatchedReasoningAnswerableAcc", "NA"),
            macro("DayOneScaleReasoningLargestMatchedDeltaActionAcc", "NA"),
            macro("DayOneScaleReasoningLargestMatchedDeltaUtility", "NA"),
            macro("DayOneScaleReasoningLargestMatchedDeltaOverAnswer", "NA"),
            macro("DayOneScaleReasoningLargestMatchedDeltaJsonParse", "NA"),
        ]
    instruct_run, reasoning_run = pair
    delta = pair_delta(instruct_run, reasoning_run)
    return [
        macro("DayOneScaleReasoningMatchedStatus", "available"),
        macro("DayOneScaleReasoningLargestMatchedSize", size_label(instruct_run["size_b"])),
        macro("DayOneScaleReasoningLargestMatchedInstructModel", instruct_run["model"]),
        macro("DayOneScaleReasoningLargestMatchedReasoningModel", reasoning_run["model"]),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningActionAcc",
            fmt(reasoning_run["summary"]["action_accuracy"]),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningUtility",
            fmt(reasoning_run["summary"]["avg_utility"]),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningJsonParse",
            fmt(reasoning_run["summary"]["json_parse_rate"]),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningNumExamples",
            str(int(reasoning_run["summary"]["num_examples"])),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningPredAnswerCount",
            str(pred_action_count(reasoning_run, "answer")),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningPredAskCount",
            str(pred_action_count(reasoning_run, "ask")),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningPredChallengeCount",
            str(pred_action_count(reasoning_run, "challenge")),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningPredAbstainCount",
            str(pred_action_count(reasoning_run, "abstain")),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningFalsePremiseAcc",
            fmt(slice_action_accuracy(reasoning_run, "false_premise")),
        ),
        macro(
            "DayOneScaleReasoningLargestMatchedReasoningAnswerableAcc",
            fmt(slice_action_accuracy(reasoning_run, "answerable_control")),
        ),
        macro("DayOneScaleReasoningLargestMatchedDeltaActionAcc", format_delta(delta["action_accuracy"])),
        macro("DayOneScaleReasoningLargestMatchedDeltaUtility", format_delta(delta["avg_utility"])),
        macro("DayOneScaleReasoningLargestMatchedDeltaOverAnswer", format_delta(delta["over_answer_rate"])),
        macro("DayOneScaleReasoningLargestMatchedDeltaJsonParse", format_delta(delta["json_parse_rate"])),
    ]


def display_slice_name(slice_name: str) -> str:
    return SLICE_DISPLAY_NAMES.get(slice_name, slice_name.replace("_", " ").title())


def slice_action_accuracy(run: dict, slice_name: str) -> float:
    return float(run["summary"]["per_slice"][slice_name]["action_accuracy"])


def pred_action_count(run: dict, action: str) -> int:
    return int(run["summary"].get("pred_action_counts", {}).get(action, 0))


def macro(name: str, value: str) -> str:
    return rf"\newcommand{{\{name}}}{{{latex_escape(value)}}}"


if __name__ == "__main__":
    main()
