from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_COVERAGE_PATH = Path(__file__).resolve().parents[1] / "experiments" / "emnlp2026" / "expanded_dev_with_answer_topup_coverage_audit.json"
DEFAULT_OUTPUT_PREFIX = Path(__file__).resolve().parents[1] / "experiments" / "day1" / "figures" / "emnlp2026_figure4_coverage_overview"


SLICE_ORDER = [
    "answerable_control",
    "false_premise",
    "stale_premise",
    "conflicting_evidence",
    "ambiguous_intent",
    "insufficient_evidence",
]
ACTIONS = ["answer", "ask", "challenge", "abstain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Figure 4: expanded dataset coverage overview for the paper-facing split."
    )
    parser.add_argument(
        "--coverage-path",
        default=str(DEFAULT_COVERAGE_PATH),
        help="Path to an expanded coverage audit JSON.",
    )
    parser.add_argument(
        "--output-prefix",
        default=str(DEFAULT_OUTPUT_PREFIX),
        help="Output prefix for PDF and PNG outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    coverage_path = Path(args.coverage_path)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    payload = json.loads(coverage_path.read_text(encoding="utf-8"))
    combined = payload["combined_unique"]
    by_slice = combined["by_slice"]
    by_action = combined["by_action"]
    total = combined["unique_examples"]

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=220, gridspec_kw={"width_ratios": [1.2, 1.0]})

    plot_slice_distribution(axes[0], by_slice, total)
    plot_action_distribution(axes[1], by_action, total)

    fig.suptitle("Expanded Evidence Bundle Balance for Paper-Facing Paper Draft", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))

    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), bbox_inches="tight")
    plt.close(fig)

    print(f"Wrote {output_prefix.with_suffix('.pdf')}")
    print(f"Wrote {output_prefix.with_suffix('.png')}")


def display_slice_name(name: str) -> str:
    return name.replace("_", " ").replace("control", "control").title()


def plot_slice_distribution(ax: plt.Axes, counts: dict[str, int], total: int) -> None:
    slice_counts = [counts.get(name, 0) for name in SLICE_ORDER]
    x_positions = list(range(len(SLICE_ORDER)))
    colors = ["#1B9E77", "#E69F00", "#56B4E9", "#009E73", "#CC79A7", "#F0E442"]

    bars = ax.bar(x_positions, slice_counts, color=colors)
    ax.set_title("A. Target Split by Slice", fontsize=10, fontweight="bold", loc="left")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([display_slice_name(name) for name in SLICE_ORDER], rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Examples", fontsize=9)
    ax.set_ylim(0, max(slice_counts) * 1.2 + 5)
    ax.grid(axis="y", alpha=0.25, linewidth=0.7, linestyle="--")
    ax.tick_params(axis="y", labelsize=8)

    for bar, count in zip(bars, slice_counts):
        if count == 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            str(count),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.text(
        0.03,
        0.98,
        f"Target paper-facing size = {total}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8.5,
        color="#333333",
    )


def plot_action_distribution(ax: plt.Axes, counts: dict[str, int], total: int) -> None:
    action_counts = [counts.get(action, 0) for action in ACTIONS]
    x_positions = list(range(len(ACTIONS)))
    colors = ["#A6761D", "#7570B3", "#D95F02", "#666666"]

    bars = ax.bar(x_positions, action_counts, color=colors)
    ax.set_title("B. Target Split by Gold Action", fontsize=10, fontweight="bold", loc="left")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([action.title() for action in ACTIONS], fontsize=9)
    ax.set_ylabel("Examples", fontsize=9)
    ax.set_ylim(0, max(action_counts) * 1.2 + 5)
    ax.grid(axis="y", alpha=0.25, linewidth=0.7, linestyle="--")
    ax.tick_params(axis="y", labelsize=8)

    for bar, count in zip(bars, action_counts):
        if count == 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            str(count),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    for idx, action in enumerate(ACTIONS):
        rate = action_counts[idx] / total if total else 0.0
        ax.text(
            idx,
            -0.14,
            f"{rate:.0%}",
            ha="center",
            va="top",
            fontsize=8,
            color="#444444",
            transform=ax.get_xaxis_transform(),
            clip_on=False,
        )


if __name__ == "__main__":
    main()
