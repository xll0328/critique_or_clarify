from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


COLORS = {
    "input": "#f7f7f7",
    "decision": "#fff2cc",
    "answer": "#0072B2",
    "ask": "#CC79A7",
    "challenge": "#D55E00",
    "abstain": "#666666",
    "edge": "#444444",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Draw Figure 1 task schematic for the EMNLP sprint.")
    parser.add_argument(
        "--output-prefix",
        default="experiments/day1/figures/emnlp2026_figure1_task_schematic",
        help="Output prefix without extension.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(13.5, 7.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    draw_title(ax)
    draw_input_cards(ax)
    draw_decision_node(ax)
    draw_action_boxes(ax)
    draw_arrows(ax)

    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=220, bbox_inches="tight")
    print(f"Wrote {output_prefix.with_suffix('.pdf')}")
    print(f"Wrote {output_prefix.with_suffix('.png')}")


def draw_title(ax) -> None:
    ax.text(
        0.5,
        0.965,
        "Next-Action Selection Under Defective Inputs",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.925,
        "The assistant first decides what kind of repair, if any, is needed before generating a response.",
        ha="center",
        va="top",
        fontsize=10.5,
        color="#333333",
    )


def draw_input_cards(ax) -> None:
    cards = [
        (
            0.045,
            0.68,
            "Answerable control",
            "What county is Old Forge, New York in?",
            "Supported answer exists",
            COLORS["answer"],
        ),
        (
            0.045,
            0.48,
            "False premise",
            "Why did Marie Curie win the Nobel Prize in Literature?",
            "Premise should be corrected",
            COLORS["challenge"],
        ),
        (
            0.045,
            0.28,
            "Stale premise",
            "Why is Facebook still trading under FB?",
            "Outdated premise",
            COLORS["challenge"],
        ),
        (
            0.045,
            0.08,
            "Conflicting evidence",
            "Passage A says 1890; Passage B says 1902.",
            "Support may be irreconcilable",
            COLORS["abstain"],
        ),
    ]
    for x, y, title, prompt, tag, color in cards:
        draw_box(ax, x, y, 0.29, 0.145, facecolor=COLORS["input"], edgecolor=color, linewidth=1.5)
        ax.text(x + 0.014, y + 0.118, title, ha="left", va="center", fontsize=10, fontweight="bold", color=color)
        ax.text(x + 0.014, y + 0.078, wrap(prompt, 36), ha="left", va="center", fontsize=9.3, color="#111111")
        ax.text(x + 0.014, y + 0.025, tag, ha="left", va="center", fontsize=8.6, color="#555555")

    ax.text(0.19, 0.86, "User input + optional evidence", ha="center", va="center", fontsize=11.5, fontweight="bold")


def draw_decision_node(ax) -> None:
    draw_box(ax, 0.405, 0.37, 0.22, 0.22, facecolor=COLORS["decision"], edgecolor="#B08D00", linewidth=1.6)
    ax.text(0.515, 0.535, "Choose the\nhighest-utility\nnext action", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.text(0.515, 0.405, "action before generation", ha="center", va="center", fontsize=9.5, color="#555555")


def draw_action_boxes(ax) -> None:
    actions = [
        (0.71, 0.68, "answer", "Provide the supported answer directly.", COLORS["answer"]),
        (0.71, 0.48, "ask", "Ask the minimum useful follow-up question.", COLORS["ask"]),
        (0.71, 0.28, "challenge", "Correct the false or stale premise first.", COLORS["challenge"]),
        (0.71, 0.08, "abstain", "Explain why support is insufficient or conflicting.", COLORS["abstain"]),
    ]
    for x, y, action, description, color in actions:
        draw_box(ax, x, y, 0.245, 0.145, facecolor="#ffffff", edgecolor=color, linewidth=1.7)
        ax.text(
            x + 0.018,
            y + 0.103,
            action,
            ha="left",
            va="center",
            fontsize=11.5,
            fontweight="bold",
            fontfamily="monospace",
            color=color,
        )
        ax.text(x + 0.018, y + 0.052, wrap(description, 34), ha="left", va="center", fontsize=9.3, color="#222222")

    ax.text(0.83, 0.86, "Response behavior", ha="center", va="center", fontsize=11.5, fontweight="bold")


def draw_arrows(ax) -> None:
    for y in [0.752, 0.552, 0.352, 0.152]:
        arrow(ax, (0.34, y), (0.405, 0.48))
    for y in [0.752, 0.552, 0.352, 0.152]:
        arrow(ax, (0.625, 0.48), (0.71, y))
    ax.text(0.515, 0.315, "Answer generation is downstream of action choice.", ha="center", va="center", fontsize=9.5, color="#333333")


def draw_box(ax, x: float, y: float, width: float, height: float, *, facecolor: str, edgecolor: str, linewidth: float) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
    )
    ax.add_patch(patch)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        color=COLORS["edge"],
        linewidth=1.1,
        mutation_scale=12,
        shrinkA=4,
        shrinkB=4,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(patch)


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


if __name__ == "__main__":
    main()
