from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from compare_runs import SLICE_DISPLAY_NAMES, load_run, ordered_slice_names


MODEL_COLORS = {
    "Qwen2.5-0.5B-Instruct": "#D8A36A",
    "Qwen2.5-1.5B-Instruct": "#C46A33",
    "Qwen2.5-Coder-7B-Instruct": "#7F3B08",
    "DeepSeek-R1-Distill-Qwen-1.5B": "#4C8D9B",
    "DeepSeek-R1-Distill-Qwen-7B": "#0F5C73",
}
STYLE_MARKERS = {
    "instruct": "o",
    "reasoning": "D",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot the current day-1 scale/reasoning comparison from metrics JSON files."
    )
    parser.add_argument("paths", nargs="+", help="Metric JSON files to visualize.")
    parser.add_argument("--title", default="Day-1 Scale And Reasoning Snapshot")
    parser.add_argument(
        "--output-prefix",
        default="experiments/day1/figures/day1_scale_reasoning",
        help="Path prefix used for the PNG and CSV outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [load_run(Path(raw_path)) for raw_path in args.paths]
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    overall_rows = build_overall_rows(runs)
    slice_rows = build_slice_rows(runs)

    write_csv(output_prefix.with_name(output_prefix.name + "_overall.csv"), overall_rows)
    write_csv(output_prefix.with_name(output_prefix.name + "_per_slice.csv"), slice_rows)
    render_figure(
        runs=runs,
        title=args.title,
        output_prefix=output_prefix,
    )


def build_overall_rows(runs: list[dict]) -> list[dict[str, str | float]]:
    rows: list[dict[str, str | float]] = []
    for index, run in enumerate(runs, start=1):
        summary = run["summary"]
        rows.append(
            {
                "rank": index,
                "label": run["label"],
                "model": run["model"],
                "family": run["family"],
                "style": run["style"],
                "short_label": shorten_model_name(run["model"]),
                "action_accuracy": summary["action_accuracy"],
                "avg_utility": summary["avg_utility"],
                "answer_em": summary["answer_em"],
                "answer_contains_rate": summary.get("answer_contains_rate", 0.0),
                "over_answer_rate": summary["over_answer_rate"],
                "json_parse_rate": summary.get("json_parse_rate", 0.0),
            }
        )
    return rows


def build_slice_rows(runs: list[dict]) -> list[dict[str, str | float]]:
    rows: list[dict[str, str | float]] = []
    slice_names = ordered_slice_names(runs)
    for run in runs:
        summary = run["summary"]
        for slice_name in slice_names:
            slice_summary = summary["per_slice"].get(slice_name)
            if slice_summary is None:
                continue
            rows.append(
                {
                    "label": run["label"],
                    "model": run["model"],
                    "style": run["style"],
                    "slice_name": slice_name,
                    "slice_display_name": SLICE_DISPLAY_NAMES.get(
                        slice_name, slice_name.replace("_", " ").title()
                    ),
                    "action_accuracy": slice_summary["action_accuracy"],
                    "avg_utility": slice_summary["avg_utility"],
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str | float]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_figure(*, runs: list[dict], title: str, output_prefix: Path) -> None:
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12.6, 5.2),
        dpi=200,
        gridspec_kw={"width_ratios": [1.0, 1.3]},
    )
    plot_tradeoff_panel(axes[0], runs)
    plot_slice_panel(axes[1], runs)
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    fig.text(
        0.5,
        0.02,
        "Left: overall utility vs. action accuracy (horizontal error bars are 95% Wilson CI). "
        "Right: per-slice action accuracy with 95% Wilson CI.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(output_prefix.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_tradeoff_panel(ax: plt.Axes, runs: list[dict]) -> None:
    for run in runs:
        summary = run["summary"]
        model = run["model"]
        x_value = summary["action_accuracy"]
        y_value = summary["avg_utility"]
        low, high = wilson_interval(x_value, int(summary.get("num_examples", 0)))
        marker_size = 120 + 340 * summary.get("json_parse_rate", 0.0)
        ax.scatter(
            x_value,
            y_value,
            s=marker_size,
            marker=STYLE_MARKERS.get(run["style"], "o"),
            color=MODEL_COLORS.get(model, "#555555"),
            edgecolors="black",
            linewidths=0.8,
            alpha=0.9,
            zorder=3,
        )
        ax.errorbar(
            x_value,
            y_value,
            xerr=[[max(0.0, x_value - low)], [max(0.0, high - x_value)]],
            fmt="none",
            ecolor="#333333",
            elinewidth=0.8,
            capsize=2.5,
            zorder=2,
        )
        ax.annotate(
            shorten_model_name(model),
            (x_value, y_value),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("Overall Tradeoff", fontsize=12, fontweight="bold")
    ax.set_xlabel("Action Accuracy")
    ax.set_ylabel("Average Utility")
    ax.grid(alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_xlim(0.0, 1.0)
    ax.axvline(0.5, color="#bdbdbd", linewidth=1.0, linestyle=":")
    ax.axhline(0.0, color="#bdbdbd", linewidth=1.0, linestyle=":")
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker=STYLE_MARKERS["instruct"],
            linestyle="",
            color="w",
            markerfacecolor="#777777",
            markeredgecolor="black",
            label="Instruct",
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker=STYLE_MARKERS["reasoning"],
            linestyle="",
            color="w",
            markerfacecolor="#777777",
            markeredgecolor="black",
            label="Reasoning",
            markersize=8,
        ),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False, fontsize=9)


def plot_slice_panel(ax: plt.Axes, runs: list[dict]) -> None:
    slice_names = ordered_slice_names(runs)
    display_names = [SLICE_DISPLAY_NAMES.get(name, name.replace("_", " ").title()) for name in slice_names]
    bar_width = 0.78 / max(1, len(runs))
    x_positions = list(range(len(slice_names)))

    for index, run in enumerate(runs):
        summary = run["summary"]
        offsets = [x + (index - (len(runs) - 1) / 2) * bar_width for x in x_positions]
        heights = [
            summary["per_slice"].get(slice_name, {}).get("action_accuracy", 0.0)
            for slice_name in slice_names
        ]
        yerr = []
        for slice_name, height in zip(slice_names, heights):
            count = int(summary["per_slice"].get(slice_name, {}).get("count", 0))
            low, high = wilson_interval(float(height), count)
            yerr.append(max(float(height) - low, high - float(height)))
        ax.bar(
            offsets,
            heights,
            width=bar_width,
            color=MODEL_COLORS.get(run["model"], "#555555"),
            label=shorten_model_name(run["model"]),
            edgecolor="white",
            linewidth=0.7,
            alpha=0.95,
            yerr=yerr,
            ecolor="#333333",
            capsize=1.8,
            error_kw={"elinewidth": 0.8},
        )

    ax.set_title("Per-Slice Action Accuracy", fontsize=12, fontweight="bold")
    ax.set_ylabel("Accuracy")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(display_names, rotation=18, ha="right")
    ax.set_ylim(0.0, 1.0)
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=8)


def shorten_model_name(model_name: str) -> str:
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
