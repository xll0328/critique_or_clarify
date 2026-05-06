from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import read_jsonl


SLICE_ORDER = ["answerable_control", "false_premise", "conflicting_evidence"]
ACTION_ORDER = ["answer", "ask", "challenge", "abstain"]
ACTION_COLORS = {
    "answer": "#1B9E77",
    "ask": "#7570B3",
    "challenge": "#D95F02",
    "abstain": "#666666",
}
SLICE_DISPLAY = {
    "answerable_control": "Answerable",
    "false_premise": "False Premise",
    "conflicting_evidence": "Conflicting Evidence",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build EMNLP Figure 5: boundary-failure profile on Day-1 development split."
    )
    parser.add_argument(
        "--split",
        default="data/processed/day1_dev.jsonl",
        help="Gold split JSONL path.",
    )
    parser.add_argument(
        "--qwen-predictions",
        default="outputs/day1/qwen25_15b_day1_dev.jsonl",
        help="Prediction JSONL for Qwen2.5-1.5B-Instruct.",
    )
    parser.add_argument(
        "--deepseek-predictions",
        default="outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed.jsonl",
        help="Prediction JSONL for DeepSeek-R1-Distill-Qwen-7B.",
    )
    parser.add_argument(
        "--output-prefix",
        default="experiments/day1/figures/emnlp2026_figure5_boundary_failures",
        help="Output prefix for .png, .pdf, .csv, and caption .md.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    split_rows = {row["id"]: row for row in read_jsonl(args.split)}
    qwen_rows = index_predictions(args.qwen_predictions)
    deepseek_rows = index_predictions(args.deepseek_predictions)

    qwen_stats = compute_slice_stats(split_rows, qwen_rows)
    deepseek_stats = compute_slice_stats(split_rows, deepseek_rows)

    write_csv(output_prefix.with_suffix(".csv"), qwen_stats, deepseek_stats)
    render_figure(
        qwen_stats=qwen_stats,
        deepseek_stats=deepseek_stats,
        png_path=output_prefix.with_suffix(".png"),
        pdf_path=output_prefix.with_suffix(".pdf"),
    )
    caption_path = output_prefix.with_name(output_prefix.name + "_caption.md")
    caption_path.write_text(render_caption() + "\n", encoding="utf-8")

    print(f"Wrote {output_prefix.with_suffix('.png')}")
    print(f"Wrote {output_prefix.with_suffix('.pdf')}")
    print(f"Wrote {output_prefix.with_suffix('.csv')}")
    print(f"Wrote {caption_path}")


def index_predictions(path: str | Path) -> dict[str, dict[str, Any]]:
    return {row["example_id"]: row for row in read_jsonl(path)}


def compute_slice_stats(
    split_rows: dict[str, dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for slice_name in SLICE_ORDER:
        selected = [
            (gold, predictions[gold["id"]])
            for gold in split_rows.values()
            if gold.get("metadata", {}).get("slice") == slice_name and gold["id"] in predictions
        ]
        total = len(selected)
        if total == 0:
            stats[slice_name] = {f"pred_{action}_rate": 0.0 for action in ACTION_ORDER}
            stats[slice_name]["accuracy"] = 0.0
            continue
        by_pred = {action: 0 for action in ACTION_ORDER}
        correct = 0
        for gold, pred in selected:
            pred_action = str(pred.get("action", "abstain"))
            if pred_action not in by_pred:
                pred_action = "abstain"
            by_pred[pred_action] += 1
            if pred_action == gold.get("gold_action"):
                correct += 1
        row = {f"pred_{action}_rate": by_pred[action] / total for action in ACTION_ORDER}
        row["accuracy"] = correct / total
        stats[slice_name] = row
    return stats


def write_csv(path: Path, qwen_stats: dict[str, dict[str, float]], deepseek_stats: dict[str, dict[str, float]]) -> None:
    rows: list[dict[str, Any]] = []
    for model, stats in [
        ("Qwen2.5-1.5B-Instruct", qwen_stats),
        ("DeepSeek-R1-Distill-Qwen-7B", deepseek_stats),
    ]:
        for slice_name in SLICE_ORDER:
            row = {
                "model": model,
                "slice": slice_name,
                "accuracy": stats[slice_name]["accuracy"],
            }
            for action in ACTION_ORDER:
                row[f"pred_{action}_rate"] = stats[slice_name][f"pred_{action}_rate"]
            rows.append(row)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_figure(
    *,
    qwen_stats: dict[str, dict[str, float]],
    deepseek_stats: dict[str, dict[str, float]],
    png_path: Path,
    pdf_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15.6, 4.9), dpi=220, gridspec_kw={"width_ratios": [1.1, 1.1, 1.0]})
    plot_stacked_panel(axes[0], qwen_stats, "A. Qwen2.5-1.5B: per-slice predicted-action mix")
    plot_stacked_panel(axes[1], deepseek_stats, "B. DeepSeek-R1-7B: per-slice predicted-action mix")
    plot_delta_panel(axes[2], qwen_stats, deepseek_stats)

    handles = [plt.Rectangle((0, 0), 1, 1, color=ACTION_COLORS[action]) for action in ACTION_ORDER]
    fig.legend(
        handles=handles,
        labels=[action.title() for action in ACTION_ORDER],
        ncol=4,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.01),
        frameon=False,
        fontsize=8,
        title="Predicted action",
        title_fontsize=8,
    )

    fig.text(0.015, 0.965, "Figure 5", fontsize=13, fontweight="bold", ha="left", va="top")
    fig.text(
        0.12,
        0.965,
        "Boundary failure profile: reasoning shifts toward abstain without fixing false-premise interruption",
        fontsize=12,
        ha="left",
        va="top",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.9), w_pad=1.4)
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def plot_stacked_panel(ax: plt.Axes, stats: dict[str, dict[str, float]], title: str) -> None:
    x = np.arange(len(SLICE_ORDER))
    bottom = np.zeros(len(SLICE_ORDER))
    for action in ACTION_ORDER:
        heights = np.array([stats[slice_name][f"pred_{action}_rate"] for slice_name in SLICE_ORDER])
        ax.bar(x, heights, bottom=bottom, color=ACTION_COLORS[action], edgecolor="white", linewidth=0.6)
        bottom += heights

    ax.set_xticks(x)
    ax.set_xticklabels([SLICE_DISPLAY[name] for name in SLICE_ORDER], rotation=15, ha="right", fontsize=8.5)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Prediction share", fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)


def plot_delta_panel(ax: plt.Axes, qwen_stats: dict[str, dict[str, float]], deepseek_stats: dict[str, dict[str, float]]) -> None:
    x = np.arange(len(SLICE_ORDER))
    qwen_acc = np.array([qwen_stats[slice_name]["accuracy"] for slice_name in SLICE_ORDER])
    deepseek_acc = np.array([deepseek_stats[slice_name]["accuracy"] for slice_name in SLICE_ORDER])
    delta = deepseek_acc - qwen_acc

    bars = ax.bar(x, delta, color=["#2C7FB8" if value >= 0 else "#D7301F" for value in delta], alpha=0.9)
    ax.axhline(0.0, color="#555555", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels([SLICE_DISPLAY[name] for name in SLICE_ORDER], rotation=15, ha="right", fontsize=8.5)
    ax.set_ylabel("Accuracy delta (DeepSeek - Qwen)", fontsize=9)
    ax.set_title("C. Accuracy shift by slice", fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, delta):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + (0.015 if value >= 0 else -0.02),
            f"{value:+.2f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=8,
        )


def render_caption() -> str:
    return (
        "Boundary failure profile on the Day-1 development split. Panels A and B show per-slice predicted-action "
        "mixtures for Qwen2.5-1.5B-Instruct and DeepSeek-R1-Distill-Qwen-7B. Panel C reports per-slice action-accuracy "
        "deltas (DeepSeek minus Qwen). The key pattern is asymmetric: reasoning shifts toward abstain on answerable controls "
        "without recovering false-premise interruption, so caution does not translate into better first-move calibration."
    )


if __name__ == "__main__":
    main()
