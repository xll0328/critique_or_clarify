#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import load_examples, read_jsonl
from coc.metrics import exact_match
from coc.schema import Action, Example, Prediction


DEFAULT_RUNS = [
    "Qwen2.5-0.5B-Instruct:instruct:outputs/day1/qwen25_05b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "Qwen2.5-1.5B-Instruct:instruct:outputs/day1/qwen25_15b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "DeepSeek-R1-Distill-Qwen-1.5B:reasoning:outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed.jsonl:data/processed/day1_dev.jsonl",
    "Qwen2.5-Coder-7B-Instruct:instruct:outputs/day1/qwen25_coder_7b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "DeepSeek-R1-Distill-Qwen-7B:reasoning:outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed.jsonl:data/processed/day1_dev.jsonl",
]

SCHEMES: dict[str, dict[str, float]] = {
    "paper_default": {
        "answer_correct": 1.0,
        "answer_wrong": -0.5,
        "ask_on_answer": -0.25,
        "abstain_on_answer": -0.5,
        "challenge_on_answer": -0.75,
        "nonanswer_correct": 0.5,
        "overanswer": -1.0,
        "other_nonanswer": -0.25,
    },
    "overanswer_heavy": {
        "answer_correct": 1.0,
        "answer_wrong": -0.5,
        "ask_on_answer": -0.2,
        "abstain_on_answer": -0.5,
        "challenge_on_answer": -0.75,
        "nonanswer_correct": 0.5,
        "overanswer": -1.5,
        "other_nonanswer": -0.1,
    },
    "caution_heavy": {
        "answer_correct": 1.0,
        "answer_wrong": -0.5,
        "ask_on_answer": -0.5,
        "abstain_on_answer": -0.75,
        "challenge_on_answer": -1.0,
        "nonanswer_correct": 0.5,
        "overanswer": -1.0,
        "other_nonanswer": -0.25,
    },
    "flat_action": {
        "answer_correct": 1.0,
        "answer_wrong": -1.0,
        "ask_on_answer": -1.0,
        "abstain_on_answer": -1.0,
        "challenge_on_answer": -1.0,
        "nonanswer_correct": 1.0,
        "overanswer": -1.0,
        "other_nonanswer": -1.0,
    },
}


@dataclass(frozen=True)
class RunSpec:
    label: str
    family: str
    predictions_path: Path
    data_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether utility conclusions depend on one weight scheme.")
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Run spec as LABEL:FAMILY:PREDICTIONS_JSONL:DATA_JSONL. Repeatable.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/day1_utility_weight_sensitivity_audit.md",
        help="Markdown report output.",
    )
    parser.add_argument(
        "--output-json",
        default="experiments/day1/day1_utility_weight_sensitivity_audit.json",
        help="Machine-readable JSON report output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    specs = [parse_run_spec(raw) for raw in (args.run or DEFAULT_RUNS)]
    runs = [load_run(spec) for spec in specs]
    scheme_rows = [audit_scheme(name, weights, runs) for name, weights in SCHEMES.items()]

    payload = {
        "audit": "utility_weight_sensitivity",
        "interpretation": (
            "This audit probes whether ranking and reasoning-vs-instruct conclusions depend on the default "
            "asymmetric utility weights. It is a sensitivity check, not a replacement metric."
        ),
        "schemes": scheme_rows,
    }

    output_json = resolve_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    output_md = resolve_path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload) + "\n", encoding="utf-8")

    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def parse_run_spec(raw: str) -> RunSpec:
    pieces = raw.split(":")
    if len(pieces) != 4:
        raise SystemExit(f"Invalid --run spec, expected LABEL:FAMILY:PREDICTIONS_JSONL:DATA_JSONL: {raw}")
    label, family, predictions_path, data_path = pieces
    return RunSpec(
        label=label,
        family=family,
        predictions_path=resolve_path(predictions_path),
        data_path=resolve_path(data_path),
    )


def load_run(spec: RunSpec) -> dict[str, Any]:
    examples = load_examples(spec.data_path)
    predictions = [Prediction.from_dict(row) for row in read_jsonl(spec.predictions_path)]
    prediction_map = {prediction.example_id: prediction for prediction in predictions}
    pairs = [(example, prediction_map[example.id]) for example in examples if example.id in prediction_map]
    if len(pairs) != len(examples):
        missing = sorted(example.id for example in examples if example.id not in prediction_map)
        raise SystemExit(f"{spec.label} missing predictions for {len(missing)} examples: {missing[:5]}")
    return {
        "label": spec.label,
        "family": spec.family,
        "predictions": display_path(spec.predictions_path),
        "data": display_path(spec.data_path),
        "pairs": pairs,
    }


def audit_scheme(name: str, weights: dict[str, float], runs: list[dict[str, Any]]) -> dict[str, Any]:
    scored_runs = []
    for run in runs:
        values = [score_pair(example, prediction, weights) for example, prediction in run["pairs"]]
        scored_runs.append(
            {
                "label": run["label"],
                "family": run["family"],
                "avg_utility": round(sum(values) / max(len(values), 1), 4),
                "num_examples": len(values),
            }
        )
    ranked = sorted(scored_runs, key=lambda row: (row["avg_utility"], row["label"]), reverse=True)
    best_instruct = first_family(ranked, "instruct")
    best_reasoning = first_family(ranked, "reasoning")
    return {
        "scheme": name,
        "weights": weights,
        "ranking": ranked,
        "best_overall": ranked[0]["label"],
        "best_instruct": best_instruct["label"] if best_instruct else None,
        "best_reasoning": best_reasoning["label"] if best_reasoning else None,
        "best_instruct_utility": best_instruct["avg_utility"] if best_instruct else None,
        "best_reasoning_utility": best_reasoning["avg_utility"] if best_reasoning else None,
        "best_reasoning_minus_best_instruct": (
            round(best_reasoning["avg_utility"] - best_instruct["avg_utility"], 4)
            if best_instruct and best_reasoning
            else None
        ),
    }


def score_pair(example: Example, prediction: Prediction, weights: dict[str, float]) -> float:
    if example.gold_action == Action.ANSWER:
        if prediction.action == Action.ANSWER and exact_match(prediction.response, example.gold_answer or ""):
            return weights["answer_correct"]
        if prediction.action == Action.ANSWER:
            return weights["answer_wrong"]
        if prediction.action == Action.ASK:
            return weights["ask_on_answer"]
        if prediction.action == Action.ABSTAIN:
            return weights["abstain_on_answer"]
        return weights["challenge_on_answer"]

    if prediction.action == example.gold_action:
        return weights["nonanswer_correct"]
    if prediction.action == Action.ANSWER:
        return weights["overanswer"]
    return weights["other_nonanswer"]


def first_family(rows: list[dict[str, Any]], family: str) -> dict[str, Any] | None:
    for row in rows:
        if row["family"] == family:
            return row
    return None


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Utility Weight Sensitivity Audit",
        "",
        "Status: generated utility-weight sensitivity audit from saved prediction JSONL files.",
        "",
        "Interpretation: this audit checks whether the main model-comparison story depends on one utility weighting. It does not replace the paper's default metric.",
        "",
        "| Scheme | Best Overall | Best Instruct | Best Reasoning | Best Reasoning - Best Instruct |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for scheme in payload["schemes"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    scheme["scheme"],
                    scheme["best_overall"],
                    scheme["best_instruct"] or "NA",
                    scheme["best_reasoning"] or "NA",
                    fmt_optional(scheme["best_reasoning_minus_best_instruct"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Per-Scheme Rankings", ""])
    for scheme in payload["schemes"]:
        lines.extend(
            [
                f"### {scheme['scheme']}",
                "",
                "| Rank | Run | Family | Avg Utility |",
                "| ---: | --- | --- | ---: |",
            ]
        )
        for rank, row in enumerate(scheme["ranking"], start=1):
            lines.append(f"| {rank} | {row['label']} | {row['family']} | {fmt(row['avg_utility'])} |")
        lines.append("")

    lines.extend(
        [
            "## Reading Guide",
            "",
            "- `paper_default` matches the paper's current asymmetric utility scheme.",
            "- `overanswer_heavy` penalizes direct answers on non-answer gold examples more strongly.",
            "- `caution_heavy` penalizes unnecessary ask/abstain/challenge on answerable examples more strongly.",
            "- `flat_action` ignores graded harm and rewards only action correctness.",
            "- If the best reasoning row overtakes the best instruct row under a scheme, the reasoning-model claim needs to be weakened or reanalyzed.",
        ]
    )
    return "\n".join(lines)


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def fmt_optional(value: float | None) -> str:
    if value is None:
        return "NA"
    return fmt(value)


if __name__ == "__main__":
    main()

