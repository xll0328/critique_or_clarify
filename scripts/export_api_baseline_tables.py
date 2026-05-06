#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_METRIC_PATHS = [
    "outputs/day1/aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json",
    "outputs/day1/aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup_metrics.json",
    "outputs/day1/aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json",
    "outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json",
    "outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json",
]

MODEL_ORDER = [
    "qwen-turbo",
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "qwen-plus-latest",
    "gpt-5-chat-latest",
]

MODEL_DISPLAY = {
    "qwen-turbo": "qwen-turbo",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "qwen-plus-latest": "qwen-plus-latest",
    "gpt-5-chat-latest": "gpt-5-chat-latest",
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
    "gpt-4o-mini": (0.1500, 0.6000),
    "gpt-4.1-mini": (0.1500, 0.6000),
    "qwen-plus-latest": (0.1100, 0.2750),
    "gpt-5-chat-latest": (1.2500, 10.0000),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export API baseline LaTeX table from metric JSON files.")
    parser.add_argument(
        "--metric-paths",
        nargs="+",
        default=DEFAULT_METRIC_PATHS,
        help="Metric JSON paths from scripts/run_aihubmix_baseline.py",
    )
    parser.add_argument(
        "--output-tex",
        default="experiments/day1/tables/day1_api_baseline_dev.tex",
        help="Output table path.",
    )
    return parser.parse_args()


def canonicalize_model_id(model_id: str) -> str:
    normalized = model_id.lower().replace("_", "").replace("-", "")
    for alias, canonical in NAME_ALIASES.items():
        if normalized.startswith(alias):
            return canonical
    # Fallback: preserve known names if already canonical.
    if model_id in MODEL_DISPLAY:
        return model_id
    return model_id


def parse_model_id_from_path(path: Path) -> str:
    stem = path.stem
    stem = stem.replace("_day1_expanded_dev_with_answer_topup_metrics", "")
    stem = stem.replace("aihubmix_", "")
    return canonicalize_model_id(stem)


def fmt_price(value: float) -> str:
    if value >= 0.1:
        return f"{value:.4f}"
    return f"{value:.3f}"


def fmt_metric(value: float) -> str:
    return f"{value:.4f}"


def main() -> None:
    args = parse_args()
    rows: dict[str, dict[str, float]] = {}

    for raw_path in args.metric_paths:
        metric_path = Path(raw_path)
        payload = json.loads(metric_path.read_text(encoding="utf-8"))
        summary = payload["summary"]
        model_id = parse_model_id_from_path(metric_path)
        rows[model_id] = {
            "action_accuracy": float(summary["action_accuracy"]),
            "avg_utility": float(summary["avg_utility"]),
            "json_parse_rate": float(summary["json_parse_rate"]),
            "over_answer_rate": float(summary["over_answer_rate"]),
            "answer_contains_rate": float(summary["answer_contains_rate"]),
        }

    ordered_models = [model for model in MODEL_ORDER if model in rows]
    extras = sorted(model for model in rows if model not in ordered_models)
    ordered_models.extend(extras)

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{5pt}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lllrrrrr}",
        r"\toprule",
        r"Model & Input (\$/M) & Output (\$/M) & Action Acc. & Avg Utility & JSON Parse & Over-answer & Answer Contains \\ ",
        r"\midrule",
    ]

    for model in ordered_models:
        metrics = rows[model]
        input_price, output_price = KNOWN_PRICES.get(model, (0.0, 0.0))
        lines.append(
            " & ".join(
                [
                    MODEL_DISPLAY.get(model, model),
                    f"\\${fmt_price(input_price)}",
                    f"\\${fmt_price(output_price)}",
                    fmt_metric(metrics["action_accuracy"]),
                    fmt_metric(metrics["avg_utility"]),
                    fmt_metric(metrics["json_parse_rate"]),
                    fmt_metric(metrics["over_answer_rate"]),
                    fmt_metric(metrics["answer_contains_rate"]),
                ]
            )
            + r" \\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            (
                r"\caption{External API baselines on the 560-example canonical split "
                r"(\texttt{emnlp2026\_expanded\_dev\_with\_answer\_topup}, decision-first, max\_tokens=64, "
                r"temperature=0.0). Metrics are measured on \texttt{avg\_utility}, \texttt{action\_accuracy}, "
                r"\texttt{json\_parse\_rate}, \texttt{over\_answer\_rate}, and \texttt{answer\_contains\_rate}.}"
            ),
            r"\label{tab:day1-api-baseline}",
            r"\end{table*}",
        ]
    )

    output_path = Path(args.output_tex)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
