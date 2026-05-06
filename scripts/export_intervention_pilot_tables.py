from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from compare_runs import fmt


DEFAULT_RUNS = [
    (
        "baseline",
        Path("outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json"),
    ),
    (
        "decision_first",
        Path("outputs/day1/interventions/qwen25_15b_day1_quick_plus_stale_decision_first_metrics.json"),
    ),
    (
        "critique_first",
        Path("outputs/day1/interventions/qwen25_15b_day1_quick_plus_stale_critique_first_metrics.json"),
    ),
    (
        "decision_first_guarded",
        Path("outputs/day1/interventions/qwen25_15b_day1_quick_plus_stale_decision_first_guarded_metrics.json"),
    ),
    (
        "decision_first_balanced",
        Path("outputs/day1/interventions/qwen25_15b_day1_quick_plus_stale_decision_first_balanced_metrics.json"),
    ),
]


@dataclass(frozen=True)
class Run:
    label: str
    path: Path
    summary: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Qwen2.5-1.5B quick+stale prompt-intervention pilot tables."
    )
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Metric JSON to include. Repeatable. Defaults to the current intervention pilot bundle.",
    )
    parser.add_argument(
        "--markdown-output",
        default="experiments/day1/interventions/qwen25_15b_quick_plus_stale_intervention_summary.md",
        help="Markdown table output path.",
    )
    parser.add_argument(
        "--tex-output",
        default="experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_main.tex",
        help="LaTeX table output path.",
    )
    parser.add_argument(
        "--macros-output",
        default="experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex",
        help="LaTeX macro output path for manuscript prose.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_specs = parse_run_specs(args.run) if args.run else DEFAULT_RUNS
    runs = [load_run(label, path) for label, path in run_specs if path.exists()]
    if len(runs) < 2:
        raise SystemExit("Need at least two existing metric JSON files to compare interventions.")

    baseline = runs[0]
    markdown = render_markdown(runs, baseline)
    tex = render_tex(runs, baseline)
    macros = render_macros(runs, baseline)

    markdown_path = Path(args.markdown_output)
    tex_path = Path(args.tex_output)
    macros_path = Path(args.macros_output)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    macros_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown + "\n", encoding="utf-8")
    tex_path.write_text(tex + "\n", encoding="utf-8")
    macros_path.write_text(macros + "\n", encoding="utf-8")
    print(f"Wrote {markdown_path}")
    print(f"Wrote {tex_path}")
    print(f"Wrote {macros_path}")


def parse_run_specs(raw_specs: list[str]) -> list[tuple[str, Path]]:
    specs = []
    for raw_spec in raw_specs:
        if "=" not in raw_spec:
            raise ValueError(f"--run must use LABEL=PATH, got: {raw_spec}")
        label, raw_path = raw_spec.split("=", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"--run label is empty: {raw_spec}")
        specs.append((label, Path(raw_path)))
    return specs


def load_run(label: str, path: Path) -> Run:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Run(label=label, path=path, summary=payload["summary"])


def render_markdown(runs: list[Run], baseline: Run) -> str:
    lines = [
        "# Qwen2.5-1.5B Quick+Stale Intervention Summary",
        "",
        "Generated from metric JSON artifacts. Deltas are relative to the first row.",
        "",
        "| Variant | Utility | Delta Utility | Action Acc. | Delta Acc. | Over-Answer | Answer-Supported Acc. | Defective-Premise Acc. | JSON Parse |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{run.label}`",
                    fmt(run.summary["avg_utility"]),
                    fmt_delta(run.summary["avg_utility"] - baseline.summary["avg_utility"]),
                    fmt(run.summary["action_accuracy"]),
                    fmt_delta(run.summary["action_accuracy"] - baseline.summary["action_accuracy"]),
                    fmt(run.summary["over_answer_rate"]),
                    fmt(weighted_slice_accuracy(run.summary, ["answerable_control", "conflicting_evidence"])),
                    fmt(weighted_slice_accuracy(run.summary, ["false_premise", "stale_premise"])),
                    fmt(run.summary.get("json_parse_rate", 0.0)),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Answer-supported accuracy pools `answerable_control` and `conflicting_evidence`; defective-premise accuracy pools `false_premise` and `stale_premise`.",
        ]
    )
    return "\n".join(lines)


def render_tex(runs: list[Run], baseline: Run) -> str:
    lines = [
        r"\begin{table*}[!b]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4.5pt}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"Variant & Utility & $\Delta$ Utility & Action Acc. & $\Delta$ Acc. & Over-Answer & Answer-Supported Acc. & Defective-Premise Acc. \\",
        r"\midrule",
    ]
    best_utility = best_usable_utility(runs, baseline)
    best_acc = max(run.summary["action_accuracy"] for run in runs)
    best_defective = max(weighted_slice_accuracy(run.summary, ["false_premise", "stale_premise"]) for run in runs)
    min_over_answer = min(run.summary["over_answer_rate"] for run in runs)

    for run in runs:
        utility = run.summary["avg_utility"]
        action_acc = run.summary["action_accuracy"]
        over_answer = run.summary["over_answer_rate"]
        defective_acc = weighted_slice_accuracy(run.summary, ["false_premise", "stale_premise"])
        cells = [
            latex_escape(run.label),
            highlight(fmt(utility), utility, best_utility, higher_is_better=True),
            fmt_delta(utility - baseline.summary["avg_utility"]),
            highlight(fmt(action_acc), action_acc, best_acc, higher_is_better=True),
            fmt_delta(action_acc - baseline.summary["action_accuracy"]),
            highlight(fmt(over_answer), over_answer, min_over_answer, higher_is_better=False),
            fmt(weighted_slice_accuracy(run.summary, ["answerable_control", "conflicting_evidence"])),
            highlight(fmt(defective_acc), defective_acc, best_defective, higher_is_better=True),
        ]
        lines.append(" & ".join(cells) + r" \\")

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            r"\caption{Prompt-intervention pilot on the Qwen2.5-1.5B quick+stale split. Deltas are relative to the baseline prompt. Answer-supported accuracy pools answerable controls and conflicting-evidence items; defective-premise accuracy pools false- and stale-premise items. Utility is highlighted only among variants that do not reduce overall or answer-supported action accuracy versus baseline.}",
            r"\label{tab:qwen25-15b-intervention-pilot}",
            r"\end{table*}",
        ]
    )
    return "\n".join(lines)


def render_macros(runs: list[Run], baseline: Run) -> str:
    by_label = {run.label: run for run in runs}
    decision_first = by_label.get("decision_first")
    best_usable = max_usable_run(runs, baseline)
    lines = [
        macro("QwenQuickStaleInterventionBaselineLabel", baseline.label),
        macro("QwenQuickStaleInterventionBaselineUtility", fmt(baseline.summary["avg_utility"])),
        macro("QwenQuickStaleInterventionBaselineActionAcc", fmt(baseline.summary["action_accuracy"])),
        macro("QwenQuickStaleInterventionBaselineOverAnswer", fmt(baseline.summary["over_answer_rate"])),
        macro("QwenQuickStaleInterventionBaselineAnswerSupportedAcc", fmt(answer_supported_accuracy(baseline))),
        macro("QwenQuickStaleInterventionBaselineDefectivePremiseAcc", fmt(defective_premise_accuracy(baseline))),
        macro("QwenQuickStaleInterventionBestUsableLabel", best_usable.label),
        macro("QwenQuickStaleInterventionBestUsableUtility", fmt(best_usable.summary["avg_utility"])),
        macro("QwenQuickStaleInterventionBestUsableActionAcc", fmt(best_usable.summary["action_accuracy"])),
        macro("QwenQuickStaleInterventionBestUsableOverAnswer", fmt(best_usable.summary["over_answer_rate"])),
    ]
    if decision_first is not None:
        lines.extend(
            [
                macro("QwenQuickStaleInterventionDecisionFirstUtility", fmt(decision_first.summary["avg_utility"])),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstDeltaUtility",
                    fmt_delta(decision_first.summary["avg_utility"] - baseline.summary["avg_utility"]),
                ),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstActionAcc",
                    fmt(decision_first.summary["action_accuracy"]),
                ),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstDeltaActionAcc",
                    fmt_delta(decision_first.summary["action_accuracy"] - baseline.summary["action_accuracy"]),
                ),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstOverAnswer",
                    fmt(decision_first.summary["over_answer_rate"]),
                ),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstAnswerSupportedAcc",
                    fmt(answer_supported_accuracy(decision_first)),
                ),
                macro(
                    "QwenQuickStaleInterventionDecisionFirstDefectivePremiseAcc",
                    fmt(defective_premise_accuracy(decision_first)),
                ),
            ]
        )
    return "\n".join(lines)


def weighted_slice_accuracy(summary: dict[str, Any], slice_names: list[str]) -> float:
    total = 0
    weighted = 0.0
    for slice_name in slice_names:
        slice_summary = summary.get("per_slice", {}).get(slice_name)
        if not slice_summary:
            continue
        count = int(slice_summary.get("count", 0))
        total += count
        weighted += float(slice_summary.get("action_accuracy", 0.0)) * count
    if total == 0:
        return 0.0
    return round(weighted / total, 4)


def answer_supported_accuracy(run: Run) -> float:
    return weighted_slice_accuracy(run.summary, ["answerable_control", "conflicting_evidence"])


def defective_premise_accuracy(run: Run) -> float:
    return weighted_slice_accuracy(run.summary, ["false_premise", "stale_premise"])


def max_usable_run(runs: list[Run], baseline: Run) -> Run:
    best_utility = best_usable_utility(runs, baseline)
    return max(
        (run for run in runs if abs(run.summary["avg_utility"] - best_utility) < 1e-12),
        key=lambda run: (run.summary["action_accuracy"], -run.summary["over_answer_rate"]),
    )


def best_usable_utility(runs: list[Run], baseline: Run) -> float:
    baseline_answer_supported = weighted_slice_accuracy(
        baseline.summary,
        ["answerable_control", "conflicting_evidence"],
    )
    usable_runs = [
        run
        for run in runs
        if run.summary["action_accuracy"] >= baseline.summary["action_accuracy"]
        and weighted_slice_accuracy(run.summary, ["answerable_control", "conflicting_evidence"])
        >= baseline_answer_supported
    ]
    if not usable_runs:
        usable_runs = runs
    return max(run.summary["avg_utility"] for run in usable_runs)


def fmt_delta(value: float) -> str:
    rendered = fmt(value)
    if value > 0:
        return f"+{rendered}"
    return rendered


def highlight(rendered: str, value: float, best_value: float, *, higher_is_better: bool) -> str:
    _ = higher_is_better
    is_best = abs(value - best_value) < 1e-12
    if is_best:
        return rf"\textbf{{{rendered}}}"
    return rendered


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def macro(name: str, value: str) -> str:
    return rf"\newcommand{{\{name}}}{{{latex_escape(value)}}}"


if __name__ == "__main__":
    main()
