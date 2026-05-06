from __future__ import annotations

import argparse
from pathlib import Path

from build_day1_pairwise_deltas import consecutive_pairs, enrich_run, matched_style_pairs
from day1_reporting_config import format_latex_model_list, pending_scale_reasoning_models


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export manuscript-ready LaTeX prose snippets for the current day-1 scale/reasoning snapshot."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files to export.")
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_results_snippets.tex",
        help="Output path for the emitted LaTeX snippet.",
    )
    parser.add_argument(
        "--macros-path",
        default="experiments/day1/tables/day1_scale_reasoning_macros.tex",
        help="Path to the macro file that should be input before this snippet.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [enrich_run(Path(raw_path)) for raw_path in args.paths]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_snippet(runs, macros_path=args.macros_path) + "\n", encoding="utf-8")


def render_snippet(runs: list[dict], *, macros_path: str) -> str:
    instruct_runs = sorted(
        (run for run in runs if run["style"] == "instruct" and run["size_b"] is not None),
        key=lambda run: (run["size_b"], run["model"]),
    )
    strongest_instruct_step = list(consecutive_pairs(instruct_runs))
    strongest_instruct_step_available = bool(strongest_instruct_step)

    matched_pairs = matched_style_pairs(
        instruct_runs,
        sorted(
            (run for run in runs if run["style"] == "reasoning" and run["size_b"] is not None),
            key=lambda run: (run["size_b"], run["model"]),
        ),
    )
    matched_available = bool(matched_pairs)

    lines = [
        f"% Auto-generated from the current day-1 snapshot.",
        f"% Requires: \\input{{{macros_path}}}",
        r"\paragraph{Snapshot Results.}",
        (
            r"On the current day-1 development snapshot, \texttt{\DayOneScaleReasoningFrontierModel} "
            r"is the strongest open baseline, reaching action accuracy "
            r"\DayOneScaleReasoningFrontierActionAcc{} and average utility "
            r"\DayOneScaleReasoningFrontierUtility{}. The hardest slice remains "
            r"\DayOneScaleReasoningHardestSlice{} "
            r"(\DayOneScaleReasoningHardestSliceMeanAcc{} mean action accuracy), whereas "
            r"\DayOneScaleReasoningEasiestSlice{} is currently the easiest "
            r"(\DayOneScaleReasoningEasiestSliceMeanAcc{})."
        ),
        "",
        r"\paragraph{Scale Effects.}",
    ]
    if strongest_instruct_step_available:
        lines.append(
            r"The strongest currently available instruct scale step, "
            r"\texttt{\DayOneScaleReasoningStrongestInstructStepFrom} "
            r"to \texttt{\DayOneScaleReasoningStrongestInstructStepTo}, changes action accuracy by "
            r"\DayOneScaleReasoningStrongestInstructStepDeltaActionAcc{}, utility by "
            r"\DayOneScaleReasoningStrongestInstructStepDeltaUtility{}, and JSON parse rate by "
            r"\DayOneScaleReasoningStrongestInstructStepDeltaJsonParse{}. "
            r"The largest slice gain is \DayOneScaleReasoningStrongestInstructStepBiggestGain{}, "
            r"while the largest slice drop is \DayOneScaleReasoningStrongestInstructStepBiggestDrop{}."
        )
    else:
        lines.append(
            r"The current snapshot does not yet contain multiple instruct checkpoints, so no within-style scale statement is available."
        )
    lines.extend(["", r"\paragraph{Reasoning Contrast.}"])
    if matched_available:
        lines.append(
            r"At the largest currently available size-matched contrast, "
            r"\texttt{\DayOneScaleReasoningLargestMatchedInstructModel} versus "
            r"\texttt{\DayOneScaleReasoningLargestMatchedReasoningModel} at "
            r"\DayOneScaleReasoningLargestMatchedSize{}, the reasoning model changes action accuracy by "
            r"\DayOneScaleReasoningLargestMatchedDeltaActionAcc{}, utility by "
            r"\DayOneScaleReasoningLargestMatchedDeltaUtility{}, over-answer rate by "
            r"\DayOneScaleReasoningLargestMatchedDeltaOverAnswer{}, and JSON parse rate by "
            r"\DayOneScaleReasoningLargestMatchedDeltaJsonParse{} relative to the instruct baseline."
        )
    else:
        pending_models = pending_scale_reasoning_models(runs)
        if pending_models:
            pending_clause = rf"the pending checkpoints {format_latex_model_list(pending_models)} have not finished"
        else:
            pending_clause = r"the remaining matched counterpart has not finished"
        lines.append(
            rf"The instruct-vs-reasoning comparison is not yet size-matched, because {pending_clause}. "
            rf"The safe current takeaway is only that \texttt{{\DayOneScaleReasoningBestReasoningModel}} "
            rf"is not yet competitive with \texttt{{\DayOneScaleReasoningBestInstructModel}} on the present snapshot."
        )
    lines.extend(
        [
            "",
            r"\paragraph{Intro Preview.}",
            (
                r"Across completed open baselines, scale clearly improves action calibration, but "
                r"\DayOneScaleReasoningHardestSlice{} remains the key bottleneck and the final "
                r"instruct-versus-reasoning claim should wait for the missing size-matched checkpoints."
            ),
        ]
    )
    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    main()
