#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


MODEL_MAP = {
    "aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup": "qwen-turbo",
    "aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup": "gpt-4o-mini",
    "aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup": "gpt-4.1-mini",
    "aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup": "qwen-plus-latest",
    "aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup": "gpt-5-chat-latest",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert bootstrap CI table into paper-facing API CI table.")
    parser.add_argument(
        "--input-tex",
        default="experiments/day1/tables/day1_scale_reasoning_api_ci_main.tex",
        help="Input bootstrap CI table path.",
    )
    parser.add_argument(
        "--output-tex",
        default="experiments/day1/tables/day1_api_baseline_ci_main.tex",
        help="Output paper-facing API CI table path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_tex)
    output_path = Path(args.output_tex)
    lines = input_path.read_text(encoding="utf-8").splitlines()

    output: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(r"\begin{tabular}"):
            output.append(r"\resizebox{\textwidth}{!}{%")
            output.append(line)
            continue
        if stripped.startswith(r"\end{tabular}"):
            output.append(line)
            output.append(r"}")
            continue
        if stripped.startswith(r"\caption{"):
            output.append(
                r"\caption{Bootstrap 95\% percentile intervals for external API baselines on the canonical split.}"
            )
            continue
        if stripped.startswith(r"\label{"):
            output.append(r"\label{tab:day1-api-baseline-ci}")
            continue
        if "&" in line and line.rstrip().endswith(r"\\") and not stripped.startswith("Model"):
            model = line.split("&", 1)[0].strip().replace(r"\_", "_")
            display = MODEL_MAP.get(model, model)
            output.append(line.replace(line.split("&", 1)[0], display, 1))
            continue
        output.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
