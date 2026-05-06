from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert QACC into the shared JSONL schema.")
    parser.add_argument(
        "--input",
        default="data/raw/external/qa-with-conflicting-context/data/ConflictQA_Dataset.json",
        help="Path to the original QACC JSON file.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/qacc_dev.jsonl",
        help="Output JSONL path in the shared schema.",
    )
    parser.add_argument(
        "--split",
        default="dev",
        choices=["train", "dev", "test", "all"],
        help="Which split to export.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional cap for quick debugging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    output_path = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)

    with input_path.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    converted = []
    for row in rows:
        split = str(row.get("split", "")).lower()
        if args.split != "all" and split != args.split:
            continue
        converted.append(convert_row(row))
        if args.limit > 0 and len(converted) >= args.limit:
            break

    write_jsonl(output_path, converted)
    print(f"Wrote {len(converted)} QACC examples to {output_path}")


def convert_row(row: dict[str, Any]) -> dict[str, Any]:
    split = str(row.get("split", "unknown")).lower()
    annotation_id = row.get("annotation_task_id", "unknown")
    question = str(row["question"]).strip()
    contexts = [str(item).strip() for item in row.get("contexts", []) if str(item).strip()]
    sources = [str(item).strip() for item in row.get("sources", []) if str(item).strip()]
    correct_answer = str(row.get("correctAnswer", "")).strip()

    candidate_answers = []
    for key in ["firstAnswer", "secondAnswer", "thirdAnswer", "fourthAnswer"]:
        value = row.get(key)
        if _is_missing(value):
            continue
        text = str(value).strip()
        if text:
            candidate_answers.append(text)

    return {
        "id": f"qacc-{split}-{annotation_id}",
        "source": "QACC",
        "prompt": question,
        "passages": contexts,
        "gold_action": "answer",
        "gold_answer": correct_answer,
        "metadata": {
            "dataset": "QACC",
            "slice": "conflicting_evidence",
            "split": split,
            "has_conflicting_evidence": True,
            "candidate_answers": candidate_answers,
            "reason_codes": _safe_literal_list(row.get("reasons")),
            "explanation": _clean_optional_text(row.get("explanation")),
            "source_ids": sources,
        },
    }


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip().lower()
    return text in {"", "nan", "none"}


def _safe_literal_list(value: Any) -> list[str]:
    if _is_missing(value):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    text = str(value).strip()
    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return [text]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def _clean_optional_text(value: Any) -> str | None:
    if _is_missing(value):
        return None
    text = str(value).strip()
    return text or None


if __name__ == "__main__":
    main()
