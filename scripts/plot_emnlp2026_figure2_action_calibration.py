from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from compare_runs import SLICE_DISPLAY_NAMES, fmt, load_run


DEV_METRICS = [
    Path("outputs/day1/qwen25_05b_day1_dev_metrics.json"),
    Path("outputs/day1/qwen25_15b_day1_dev_metrics.json"),
    Path("outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json"),
    Path("outputs/day1/qwen25_coder_7b_day1_dev_metrics.json"),
    Path("outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json"),
]
QUICK_STALE_METRICS = [
    Path("outputs/day1/qwen25_05b_day1_quick_plus_stale_grounded_metrics.json"),
    Path("outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json"),
    Path("outputs/day1/qwen25_coder_7b_day1_quick_plus_stale_grounded_metrics.json"),
    Path("outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json"),
    Path("outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json"),
]

MODEL_ORDER = [
    "Qwen2.5-0.5B-Instruct",
    "Qwen2.5-1.5B-Instruct",
    "Qwen2.5-Coder-7B-Instruct",
    "DeepSeek-R1-Distill-Qwen-1.5B",
    "DeepSeek-R1-Distill-Qwen-7B",
]
MODEL_COLORS = {
    "Qwen2.5-0.5B-Instruct": "#8C6D31",
    "Qwen2.5-1.5B-Instruct": "#1B9E77",
    "Qwen2.5-Coder-7B-Instruct": "#7570B3",
    "DeepSeek-R1-Distill-Qwen-1.5B": "#D95F02",
    "DeepSeek-R1-Distill-Qwen-7B": "#E7298A",
}
STYLE_MARKERS = {
    "instruct": "o",
    "reasoning": "D",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build EMNLP Figure 2: action-calibration results from metric JSON artifacts."
    )
    parser.add_argument(
        "--output-prefix",
        default="experiments/day1/figures/emnlp2026_figure2_action_calibration",
        help="Output prefix for .png, .pdf, .csv, and caption .md.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    dev_runs = load_existing_runs(DEV_METRICS)
    quick_stale_runs = load_existing_runs(QUICK_STALE_METRICS)
    write_csv(output_prefix.with_suffix(".csv"), build_csv_rows(dev_runs, quick_stale_runs))
    render_figure(
        dev_runs=dev_runs,
        quick_stale_runs=quick_stale_runs,
        png_path=output_prefix.with_suffix(".png"),
        pdf_path=output_prefix.with_suffix(".pdf"),
    )
    output_prefix.with_name(output_prefix.name + "_caption.md").write_text(
        render_caption() + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_prefix.with_suffix('.png')}")
    print(f"Wrote {output_prefix.with_suffix('.pdf')}")
    print(f"Wrote {output_prefix.with_suffix('.csv')}")
    print(f"Wrote {output_prefix.with_name(output_prefix.name + '_caption.md')}")


def load_existing_runs(paths: list[Path]) -> list[dict[str, Any]]:
    runs = [load_run(path) for path in paths if path.exists()]
    return sorted(runs, key=lambda run: MODEL_ORDER.index(run["model"]) if run["model"] in MODEL_ORDER else 999)


def build_csv_rows(dev_runs: list[dict[str, Any]], quick_stale_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    quick_by_model = {run["model"]: run for run in quick_stale_runs}
    for run in dev_runs:
        summary = run["summary"]
        quick = quick_by_model.get(run["model"], {})
        quick_summary = quick.get("summary", {})
        rows.append(
            {
                "model": run["model"],
                "style": run["style"],
                "dev_action_accuracy": summary["action_accuracy"],
                "dev_avg_utility": summary["avg_utility"],
                "dev_json_parse_rate": summary.get("json_parse_rate", 0.0),
                "dev_answerable_accuracy": slice_metric(summary, "answerable_control", "action_accuracy"),
                "dev_false_premise_accuracy": slice_metric(summary, "false_premise", "action_accuracy"),
                "dev_conflicting_evidence_accuracy": slice_metric(summary, "conflicting_evidence", "action_accuracy"),
                "quick_stale_false_over_answer": slice_metric(quick_summary, "false_premise", "over_answer_rate"),
                "quick_stale_stale_over_answer": slice_metric(quick_summary, "stale_premise", "over_answer_rate"),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_figure(*, dev_runs: list[dict[str, Any]], quick_stale_runs: list[dict[str, Any]], png_path: Path, pdf_path: Path) -> None:
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15.2, 5.15),
        dpi=220,
        gridspec_kw={"width_ratios": [1.0, 1.4, 1.1]},
    )
    plot_overall_panel(axes[0], dev_runs)
    plot_dev_slice_panel(axes[1], dev_runs)
    plot_defect_overanswer_panel(axes[2], dev_runs, quick_stale_runs)
    add_model_legend(fig, dev_runs)
    fig.text(
        0.015,
        0.965,
        "Figure 2",
        fontsize=13,
        fontweight="bold",
        ha="left",
        va="top",
    )
    fig.text(
        0.12,
        0.965,
        "Reasoning traces do not automatically yield calibrated next-action decisions",
        fontsize=12,
        ha="left",
        va="top",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.91), w_pad=2.0)
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def add_model_legend(fig: plt.Figure, dev_runs: list[dict[str, Any]]) -> None:
    handles = [
        Patch(
            facecolor=MODEL_COLORS.get(run["model"], "#666666"),
            edgecolor="white",
            label=short_label(run["model"]),
        )
        for run in dev_runs
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.005),
        ncol=len(handles),
        frameon=False,
        fontsize=8,
        title="Shared model-color legend for panels B and C",
        title_fontsize=8,
        columnspacing=1.5,
        handlelength=1.4,
    )


def plot_overall_panel(ax: plt.Axes, dev_runs: list[dict[str, Any]]) -> None:
    y_positions = list(reversed(range(len(dev_runs))))
    for y_position, run in zip(y_positions, dev_runs):
        summary = run["summary"]
        model = run["model"]
        ax.scatter(
            summary["action_accuracy"],
            y_position,
            s=115 + 320 * summary.get("json_parse_rate", 0.0),
            marker=STYLE_MARKERS.get(run["style"], "o"),
            color=MODEL_COLORS.get(model, "#666666"),
            edgecolor="black",
            linewidth=0.8,
            zorder=3,
        )
        low, high = wilson_interval(summary["action_accuracy"], int(summary.get("num_examples", 0)))
        ax.errorbar(
            summary["action_accuracy"],
            y_position,
            xerr=[[max(0.0, summary["action_accuracy"] - low)], [max(0.0, high - summary["action_accuracy"])]],
            fmt="none",
            ecolor="#333333",
            elinewidth=0.8,
            capsize=2.5,
            zorder=2,
        )
        ax.text(
            min(summary["action_accuracy"] + 0.035, 0.95),
            y_position,
            f"U={fmt(summary['avg_utility'])}",
            va="center",
            fontsize=8,
        )
    ax.set_yticks(y_positions)
    ax.set_yticklabels([short_label(run["model"]) for run in dev_runs], fontsize=8)
    ax.set_xlim(0.0, 1.0)
    ax.set_xlabel("Dev Action Accuracy")
    ax.set_title("A. Overall Decision Quality\n(marker size = JSON parse rate)", fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.axvline(0.5, color="#9E9E9E", linestyle=":", linewidth=1.0)
    ax.set_axisbelow(True)


def plot_dev_slice_panel(ax: plt.Axes, dev_runs: list[dict[str, Any]]) -> None:
    slices = ["answerable_control", "false_premise", "conflicting_evidence"]
    x_positions = list(range(len(slices)))
    bar_width = 0.78 / max(1, len(dev_runs))
    for run_index, run in enumerate(dev_runs):
        offsets = [x + (run_index - (len(dev_runs) - 1) / 2) * bar_width for x in x_positions]
        heights = [slice_metric(run["summary"], slice_name, "action_accuracy") for slice_name in slices]
        yerr = []
        for slice_name, height in zip(slices, heights):
            count = int(run["summary"].get("per_slice", {}).get(slice_name, {}).get("count", 0))
            low, high = wilson_interval(height, count)
            yerr.append(max(height - low, high - height))
        ax.bar(
            offsets,
            heights,
            width=bar_width,
            color=MODEL_COLORS.get(run["model"], "#666666"),
            edgecolor="white",
            linewidth=0.5,
            label=short_label(run["model"]),
            yerr=yerr,
            ecolor="#333333",
            capsize=1.8,
            error_kw={"elinewidth": 0.8},
        )
    ax.set_xticks(x_positions)
    ax.set_xticklabels([SLICE_DISPLAY_NAMES.get(name, name.replace("_", " ").title()) for name in slices], rotation=15, ha="right")
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Action Accuracy")
    ax.set_title("B. Slice-Specific Calibration", fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)


def plot_defect_overanswer_panel(
    ax: plt.Axes,
    dev_runs: list[dict[str, Any]],
    quick_stale_runs: list[dict[str, Any]],
) -> None:
    quick_by_model = {run["model"]: run for run in quick_stale_runs}
    defect_slices = ["false_premise", "stale_premise"]
    x_positions = list(range(len(defect_slices)))
    bar_width = 0.78 / max(1, len(dev_runs))
    for run_index, run in enumerate(dev_runs):
        quick = quick_by_model.get(run["model"])
        summary = quick["summary"] if quick else {}
        offsets = [x + (run_index - (len(dev_runs) - 1) / 2) * bar_width for x in x_positions]
        heights = [slice_metric(summary, slice_name, "over_answer_rate") for slice_name in defect_slices]
        yerr = []
        for slice_name, height in zip(defect_slices, heights):
            count = int(summary.get("per_slice", {}).get(slice_name, {}).get("count", 0))
            low, high = wilson_interval(height, count)
            yerr.append(max(height - low, high - height))
        ax.bar(
            offsets,
            heights,
            width=bar_width,
            color=MODEL_COLORS.get(run["model"], "#666666"),
            edgecolor="white",
            linewidth=0.5,
            yerr=yerr,
            ecolor="#333333",
            capsize=1.8,
            error_kw={"elinewidth": 0.8},
        )
    ax.set_xticks(x_positions)
    ax.set_xticklabels(["False Premise", "Stale Premise"], rotation=12, ha="right")
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Over-Answer Rate")
    ax.set_title("C. Defective-Premise Risk", fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.text(
        0.98,
        0.92,
        "quick+stale split",
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=8,
        color="#4D4D4D",
    )
    ax.text(
        0.02,
        0.92,
        "colors use shared legend",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=8,
        color="#4D4D4D",
    )


def render_caption() -> str:
    return (
        "# Figure 2 Caption Draft\n\n"
        "Figure 2: Reasoning traces do not automatically yield calibrated next-action decisions. "
        "Panel A shows `day1_dev` action accuracy for the completed model matrix, with marker size proportional to JSON parse rate and text labels giving average utility; horizontal error bars show 95% Wilson intervals. "
        "Panel B breaks action accuracy down by answerable controls, false-premise prompts, and conflicting-evidence questions with 95% Wilson intervals. "
        "Panel C shows over-answer rates on false- and stale-premise items in the quick+stale split, also with 95% Wilson intervals, using the shared model-color legend below the panels. "
        "The central pattern is that caution is not monotonic safety: the DeepSeek-R1-Distill-Qwen reasoning checkpoints remain weak on false/stale premise interruption and, for the 7B checkpoint, also abstain heavily on clean answerable controls."
    )


def slice_metric(summary: dict[str, Any], slice_name: str, key: str) -> float:
    return float(summary.get("per_slice", {}).get(slice_name, {}).get(key, 0.0))


def short_label(model_name: str) -> str:
    return (
        model_name.replace("-Instruct", "")
        .replace("Qwen2.5-Coder-", "Coder-")
        .replace("Qwen2.5-", "Qwen-")
        .replace("DeepSeek-R1-Distill-Qwen-", "DeepSeek-")
    )


def wilson_interval(rate: float, count: int, z: float = 1.96) -> tuple[float, float]:
    if count <= 0:
        return 0.0, 0.0
    rate = min(1.0, max(0.0, float(rate)))
    denom = 1.0 + (z * z) / count
    center = (rate + (z * z) / (2.0 * count)) / denom
    margin = (
        z
        * math.sqrt((rate * (1.0 - rate) / count) + ((z * z) / (4.0 * count * count)))
        / denom
    )
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    return low, high


if __name__ == "__main__":
    main()
