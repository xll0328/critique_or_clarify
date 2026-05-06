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

from coc.backends import extract_first_json_object
from coc.io import load_examples, read_jsonl
from coc.metrics import evaluate_predictions
from coc.schema import Action, Prediction


DEFAULT_RUNS = [
    "Qwen2.5-0.5B-Instruct:outputs/day1/qwen25_05b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "Qwen2.5-1.5B-Instruct:outputs/day1/qwen25_15b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "DeepSeek-R1-Distill-Qwen-1.5B:outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed.jsonl:data/processed/day1_dev.jsonl",
    "Qwen2.5-Coder-7B-Instruct:outputs/day1/qwen25_coder_7b_day1_dev.jsonl:data/processed/day1_dev.jsonl",
    "DeepSeek-R1-Distill-Qwen-7B:outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed.jsonl:data/processed/day1_dev.jsonl",
]


@dataclass(frozen=True)
class RunSpec:
    label: str
    predictions_path: Path
    data_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit how strict JSON parsing versus deterministic fallback changes action metrics."
    )
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Run spec as LABEL:PREDICTIONS_JSONL:DATA_JSONL. Repeatable.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/day1_parse_sensitivity_audit.md",
        help="Markdown report output.",
    )
    parser.add_argument(
        "--output-json",
        default="experiments/day1/day1_parse_sensitivity_audit.json",
        help="Machine-readable JSON report output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    specs = [parse_run_spec(raw) for raw in (args.run or DEFAULT_RUNS)]
    report_rows = [audit_run(spec) for spec in specs]

    payload = {
        "audit": "parse_sensitivity",
        "interpretation": (
            "This audit quantifies protocol sensitivity. It does not turn low-format-adherence "
            "runs into model-intrinsic action-selection claims."
        ),
        "runs": report_rows,
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
    if len(pieces) != 3:
        raise SystemExit(f"Invalid --run spec, expected LABEL:PREDICTIONS_JSONL:DATA_JSONL: {raw}")
    label, predictions_path, data_path = pieces
    return RunSpec(label=label, predictions_path=resolve_path(predictions_path), data_path=resolve_path(data_path))


def audit_run(spec: RunSpec) -> dict[str, Any]:
    examples = load_examples(spec.data_path)
    raw_rows = read_jsonl(spec.predictions_path)
    current_predictions = [Prediction.from_dict(row) for row in raw_rows]
    strict_predictions = [strict_json_or_abstain(row) for row in raw_rows]

    current_summary, current_details = evaluate_predictions(examples, current_predictions)
    strict_summary, strict_details = evaluate_predictions(examples, strict_predictions)
    current_by_id = {detail["id"]: detail for detail in current_details}
    strict_by_id = {detail["id"]: detail for detail in strict_details}

    fallback_ids = [
        prediction.example_id
        for prediction in current_predictions
        if prediction.metadata.get("parsed_as") != "json"
    ]
    json_ids = [
        prediction.example_id
        for prediction in current_predictions
        if prediction.metadata.get("parsed_as") == "json"
    ]

    action_changes = sum(
        1
        for current, strict in zip(current_predictions, strict_predictions, strict=True)
        if current.action != strict.action
    )

    return {
        "label": spec.label,
        "predictions": display_path(spec.predictions_path),
        "data": display_path(spec.data_path),
        "num_examples": current_summary["num_examples"],
        "json_parse_rate": current_summary["json_parse_rate"],
        "current_action_accuracy": current_summary["action_accuracy"],
        "strict_json_or_abstain_action_accuracy": strict_summary["action_accuracy"],
        "delta_current_minus_strict_action_accuracy": round(
            current_summary["action_accuracy"] - strict_summary["action_accuracy"], 4
        ),
        "current_avg_utility": current_summary["avg_utility"],
        "strict_json_or_abstain_avg_utility": strict_summary["avg_utility"],
        "delta_current_minus_strict_avg_utility": round(
            current_summary["avg_utility"] - strict_summary["avg_utility"], 4
        ),
        "current_over_answer_rate": current_summary["over_answer_rate"],
        "strict_json_or_abstain_over_answer_rate": strict_summary["over_answer_rate"],
        "fallback_rows": len(fallback_ids),
        "fallback_action_accuracy_current_parser": subset_accuracy(current_by_id, fallback_ids),
        "json_rows": len(json_ids),
        "json_action_accuracy_current_parser": subset_accuracy(current_by_id, json_ids),
        "action_changes_from_strict_to_current": action_changes,
        "strict_pred_action_counts": strict_summary["pred_action_counts"],
        "current_pred_action_counts": current_summary["pred_action_counts"],
        "strict_confusion": strict_summary["confusion"],
        "current_confusion": current_summary["confusion"],
    }


def strict_json_or_abstain(row: dict[str, Any]) -> Prediction:
    payload = extract_first_json_object(str(row.get("raw_output", "")))
    if isinstance(payload, dict):
        action_text = str(payload.get("action", "")).strip().lower()
        if action_text in {action.value for action in Action}:
            confidence = payload.get("confidence")
            return Prediction(
                example_id=str(row["example_id"]),
                action=Action(action_text),
                response=str(payload.get("response", "")).strip(),
                confidence=float(confidence) if isinstance(confidence, int | float) else None,
                raw_output=str(row.get("raw_output", "")),
                metadata={"parsed_as": "strict_json"},
            )

    return Prediction(
        example_id=str(row["example_id"]),
        action=Action.ABSTAIN,
        response="",
        confidence=None,
        raw_output=str(row.get("raw_output", "")),
        metadata={"parsed_as": "strict_missing"},
    )


def subset_accuracy(details_by_id: dict[str, dict[str, Any]], example_ids: list[str]) -> float | None:
    if not example_ids:
        return None
    correct = sum(1 for example_id in example_ids if details_by_id[example_id]["action_correct"])
    return round(correct / len(example_ids), 4)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Parse Sensitivity Audit",
        "",
        "Status: generated parse/protocol sensitivity audit from saved raw prediction JSONL files.",
        "",
        "Interpretation: this audit quantifies how much the current deterministic fallback parser changes metrics relative to a strict JSON-or-abstain rule. It does not remove protocol confounding or justify broader model-family claims.",
        "",
        "| Run | N | JSON Parse | Current Acc. | Strict JSON-or-Abstain Acc. | Delta Acc. | Current Utility | Strict Utility | Delta Utility | Fallback Rows | Fallback Acc. | Action Changes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["runs"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["label"],
                    str(row["num_examples"]),
                    fmt(row["json_parse_rate"]),
                    fmt(row["current_action_accuracy"]),
                    fmt(row["strict_json_or_abstain_action_accuracy"]),
                    fmt_signed(row["delta_current_minus_strict_action_accuracy"]),
                    fmt(row["current_avg_utility"]),
                    fmt(row["strict_json_or_abstain_avg_utility"]),
                    fmt_signed(row["delta_current_minus_strict_avg_utility"]),
                    str(row["fallback_rows"]),
                    fmt_optional(row["fallback_action_accuracy_current_parser"]),
                    str(row["action_changes_from_strict_to_current"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Reading Guide",
            "",
            "- `Current Acc.` is the metric used by the current deterministic parser.",
            "- `Strict JSON-or-Abstain Acc.` treats any non-JSON or malformed-action output as `abstain`.",
            "- `Fallback Acc.` reports action accuracy only on rows that were not strict JSON under the current parser.",
            "- Large deltas mean the row is protocol-sensitive and should not support broad model-intrinsic claims.",
            "",
            "## Artifact Paths",
            "",
        ]
    )
    for row in payload["runs"]:
        lines.append(f"- `{row['label']}`: `{row['predictions']}` on `{row['data']}`")
    return "\n".join(lines)


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def fmt_signed(value: float) -> str:
    return f"{value:+.4f}".rstrip("0").rstrip(".")


def fmt_optional(value: float | None) -> str:
    if value is None:
        return "NA"
    return fmt(value)


if __name__ == "__main__":
    main()

