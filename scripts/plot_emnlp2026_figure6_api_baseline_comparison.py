#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


MODEL_DATA = {
    "qwen-turbo": {
        "action_accuracy": 0.6583,
        "avg_utility": -0.4396,
        "json_parse": 0.6,
        "over_answer": 0.1333,
        "pred_actions": {"answer": 83, "ask": 3, "challenge": 13, "abstain": 21},
        "input_price": 0.046,
        "output_price": 0.092,
    },
    "ernie-4.5-0.3b": {
        "action_accuracy": 0.4917,
        "avg_utility": -0.5813,
        "json_parse": 0.3167,
        "over_answer": 0.2667,
        "pred_actions": {"answer": 91, "ask": 23, "challenge": 0, "abstain": 6},
        "input_price": 0.0136,
        "output_price": 0.0544,
    },
}

NAME_ALIASES = {
    "qwenturbo": "qwen-turbo",
    "gpt4omini": "gpt-4o-mini",
    "gpt41mini": "gpt-4.1-mini",
    "qwenpluslatest": "qwen-plus-latest",
    "gpt5chatlatest": "gpt-5-chat-latest",
}

KNOWN_PRICES = {
    "qwen-turbo": (0.046, 0.092),
    "ernie-4.5-0.3b": (0.0136, 0.0544),
    "gpt-4.1-mini": (0.15, 0.6),
    "gpt-4o-mini": (0.15, 0.6),
    "qwen-plus-latest": (0.11, 0.275),
    "gpt-5-chat-latest": (1.25, 10.0),
}
ACTIONS = ["answer", "ask", "challenge", "abstain"]
ACTION_COLORS = {
    "answer": "#1B9E77",
    "ask": "#7570B3",
    "challenge": "#D95F02",
    "abstain": "#666666",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build API baseline comparison figure with utility + quality + action mix."
    )
    parser.add_argument(
        "--output-prefix",
        default="paper/figures/figure6_api_baseline_comparison",
        help="Output prefix for .pdf and .png files.",
    )
    parser.add_argument(
        "--metric-paths",
        nargs="*",
        default=[],
        help="Optional metric JSON files from scripts/run_aihubmix_baseline.py.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    if args.metric_paths:
        model_data = load_metric_data(args.metric_paths)
    else:
        model_data = MODEL_DATA

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(14.8, 4.2),
        dpi=240,
        gridspec_kw={"width_ratios": [1.15, 0.95, 1.1]},
    )

    plot_utility_panel(axes[0], model_data)
    plot_rate_panel(axes[1], model_data)
    plot_action_mix_panel(axes[2], model_data)

    fig.text(
        0.015,
        0.98,
        "Figure 6",
        fontsize=12,
        fontweight="bold",
        ha="left",
        va="top",
    )
    fig.text(
        0.12,
        0.98,
        (
            "External API baseline behavior: accuracy/utility tradeoff, quality rates, "
            "and predicted-action mix."
        ),
        fontsize=10,
        ha="left",
        va="top",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.93))

    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_metric_data(paths: list[str]) -> dict[str, dict[str, float]]:
    data: dict[str, dict[str, float]] = {}
    for raw_path in paths:
        metric_path = Path(raw_path)
        payload = json.loads(metric_path.read_text(encoding="utf-8"))
        summary = payload["summary"]
        model_id = metric_path.stem.replace("_day1_expanded_dev_with_answer_topup_metrics", "").replace(
            "_day1_dev_metrics",
            "",
        )
        model_id = model_id.replace("aihubmix_", "")
        for alias, canonical in NAME_ALIASES.items():
            if model_id.startswith(alias):
                model_id = model_id.replace(alias, canonical, 1)
                break
        model_id = canonicalize_model_id(model_id)
        input_price, output_price = KNOWN_PRICES.get(model_id, (0.0, 0.0))
        data[model_id] = {
            "action_accuracy": float(summary["action_accuracy"]),
            "avg_utility": float(summary["avg_utility"]),
            "json_parse": float(summary.get("json_parse_rate", 0.0)),
            "over_answer": float(summary["over_answer_rate"]),
            "pred_actions": {key: int(value) for key, value in summary["pred_action_counts"].items()},
            "input_price": input_price,
            "output_price": output_price,
        }
    return data


def canonicalize_model_id(model_id: str) -> str:
    replacements = {
        "qwenturbo": "qwen-turbo",
        "qwenpluslatest": "qwen-plus-latest",
        "gpt4omini": "gpt-4o-mini",
        "gpt41mini": "gpt-4.1-mini",
        "gpt5chatlatest": "gpt-5-chat-latest",
    }
    for old, new in replacements.items():
        model_id = model_id.replace(old, new)
    return model_id


def plot_utility_panel(ax: plt.Axes, data: dict[str, dict[str, float]]) -> None:
    models = list(data.keys())
    x = [data[m]["action_accuracy"] for m in models]
    y = [data[m]["avg_utility"] for m in models]
    sizes = [700 + 6000 * data[m]["json_parse"] for m in models]
    ax.scatter(x, y, s=sizes, color="#1f78b4", edgecolor="black", linewidth=0.8, zorder=3)

    for model, xx, yy in zip(models, x, y):
        blended = (data[model]["input_price"] + data[model]["output_price"]) / 2
        ax.text(
            xx + 0.005,
            yy + 0.02,
            f"{model}\\nU={yy:+.3f}\\n${blended:.3f}/M",
            ha="left",
            va="bottom",
            fontsize=7.5,
        )

    x_low = max(0.0, min(x) - 0.08)
    x_high = min(1.0, max(x) + 0.08)
    y_low = min(-0.7, min(y) - 0.1)
    y_high = max(0.05, max(y) + 0.1)
    ax.set_xlim(x_low, x_high)
    ax.set_ylim(y_low, y_high)
    ax.set_xlabel("Action accuracy")
    ax.set_ylabel("Average utility")
    ax.set_title("A. Accuracy-utility profile", fontsize=10, fontweight="bold", loc="left")
    ax.grid(alpha=0.25, linestyle="--", linewidth=0.7)
    ax.axhline(0.0, color="#888888", linewidth=1.0, linestyle=":")


def plot_rate_panel(ax: plt.Axes, data: dict[str, dict[str, float]]) -> None:
    models = list(data.keys())
    parse_rates = [data[m]["json_parse"] for m in models]
    over_answer = [data[m]["over_answer"] for m in models]

    x = list(range(len(models)))
    width = 0.38
    ax.bar([i - width / 2 for i in x], parse_rates, width=width, label="JSON parse", color="#56B4E9")
    ax.bar([i + width / 2 for i in x], over_answer, width=width, label="Over-answer", color="#E69F00")

    ax.set_xticks(list(x))
    ax.set_xticklabels(models, fontsize=8)
    ax.set_title("B. Format and safety rates", fontsize=10, fontweight="bold", loc="left")
    ax.set_ylabel("Rate")
    rate_max = max(parse_rates + over_answer) if parse_rates or over_answer else 1.0
    ax.set_ylim(0, min(1.05, rate_max + 0.12))
    ax.legend(loc="upper center", frameon=False, fontsize=8, ncol=2)
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)

    for i, model in enumerate(models):
        ax.text(i - width / 2, parse_rates[i] + 0.015, f"{parse_rates[i]:.2f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + width / 2, over_answer[i] + 0.015, f"{over_answer[i]:.2f}", ha="center", va="bottom", fontsize=8)


def plot_action_mix_panel(ax: plt.Axes, data: dict[str, dict[str, float]]) -> None:
    models = list(data.keys())
    x = list(range(len(models)))
    bottom = [0.0] * len(models)

    for action in ACTIONS:
        values = []
        for model in models:
            total = sum(data[model]["pred_actions"].values())
            values.append((data[model]["pred_actions"].get(action, 0) / total) if total else 0.0)
        ax.bar(x, values, width=0.55, bottom=bottom, label=action.title(), color=ACTION_COLORS[action])
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(models, fontsize=8)
    ax.set_title("C. Predicted action mix", fontsize=10, fontweight="bold", loc="left")
    ax.set_ylabel("Share")
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=0.7)

    handles = [plt.Rectangle((0, 0), 1, 1, color=ACTION_COLORS[action]) for action in ACTIONS]
    ax.legend(
        handles,
        [action.title() for action in ACTIONS],
        title="Predicted action",
        title_fontsize=8,
        fontsize=8,
        ncol=2,
        loc="upper right",
        frameon=False,
        handlelength=1.2,
    )


if __name__ == "__main__":
    main()
