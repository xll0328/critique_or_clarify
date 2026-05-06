from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert PCBench into the shared JSONL schema.")
    parser.add_argument(
        "--input",
        default="",
        help="Optional path to PCBench dataset.jsonl. If omitted, download from Hugging Face.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/pcbench_paired.jsonl",
        help="Output JSONL path in the shared schema.",
    )
    parser.add_argument(
        "--variant",
        choices=["paired", "challenge", "answer"],
        default="paired",
        help="Which converted view to export.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional cap for debugging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = resolve_input_path(args.input)
    output_path = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)

    converted: list[dict] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            converted.extend(convert_row(row, args.variant))
            if args.limit > 0 and len(converted) >= args.limit:
                converted = converted[: args.limit]
                break

    write_jsonl(output_path, converted)
    print(f"Wrote {len(converted)} PCBench examples to {output_path}")


def resolve_input_path(raw_input: str) -> Path:
    if raw_input:
        path = Path(raw_input)
        return path if path.is_absolute() else ROOT / path

    from huggingface_hub import hf_hub_download

    downloaded = hf_hub_download(
        repo_id="ALIENS232/PCBench",
        repo_type="dataset",
        filename="dataset.jsonl",
    )
    return Path(downloaded)


def convert_row(row: dict, variant: str) -> list[dict]:
    output_rows: list[dict] = []
    if variant in {"paired", "challenge"}:
        output_rows.append(convert_challenge_row(row))
    if variant in {"paired", "answer"}:
        output_rows.append(convert_answer_row(row))
    return output_rows


def convert_challenge_row(row: dict) -> dict:
    meta_info = dict(row.get("meta_info", {}))
    conflict = dict(row.get("conflict", {}))
    final_answer = normalize_text(meta_info.get("final_answer"))
    return {
        "id": f"pcbench-challenge-{row['pid']}",
        "source": "PCBench",
        "prompt": normalize_text(row.get("ill_query")) or "",
        "passages": [],
        "gold_action": "challenge",
        "gold_answer": final_answer,
        "gold_response": build_challenge_response(conflict, final_answer),
        "metadata": {
            "dataset": "PCBench",
            "slice": "false_premise",
            "paired_group_id": str(row["pid"]),
            "difficulty": normalize_text(row.get("difficulty")),
            "conflict_type": normalize_text(row.get("conflict_type")),
            "original_question": normalize_text(meta_info.get("original_question")),
            "reference_solution": normalize_text(meta_info.get("reference_solution")),
            "source_dataset": normalize_text(meta_info.get("source")),
            "source_pid": normalize_text(meta_info.get("source_pid")),
            "original_premise": normalize_text(conflict.get("original_premise")),
            "recomposed_premise": normalize_text(conflict.get("recomposed_premise")),
            "conflict_reason": normalize_text(conflict.get("conflict_reason")),
        },
    }


def convert_answer_row(row: dict) -> dict:
    meta_info = dict(row.get("meta_info", {}))
    return {
        "id": f"pcbench-answer-{row['pid']}",
        "source": "PCBench",
        "prompt": normalize_text(row.get("normal_query")) or "",
        "passages": [],
        "gold_action": "answer",
        "gold_answer": normalize_text(meta_info.get("final_answer")),
        "metadata": {
            "dataset": "PCBench",
            "slice": "answerable_control",
            "paired_group_id": str(row["pid"]),
            "difficulty": normalize_text(row.get("difficulty")),
            "conflict_type": normalize_text(row.get("conflict_type")),
            "original_question": normalize_text(meta_info.get("original_question")),
            "reference_solution": normalize_text(meta_info.get("reference_solution")),
            "source_dataset": normalize_text(meta_info.get("source")),
            "source_pid": normalize_text(meta_info.get("source_pid")),
        },
    }


def build_challenge_response(conflict: dict, final_answer: str | None) -> str:
    original_premise = normalize_text(conflict.get("original_premise"))
    recomposed_premise = normalize_text(conflict.get("recomposed_premise"))

    parts: list[str] = []
    if recomposed_premise:
        parts.append(f"The question contains an incorrect premise: {recomposed_premise}.")
    else:
        parts.append("The question contains an incorrect premise.")

    if original_premise:
        parts.append(f"The supported premise is: {original_premise}.")

    if final_answer:
        parts.append(f"If the premise is repaired, the correct answer is {final_answer}.")

    return " ".join(parts).strip()


def normalize_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


if __name__ == "__main__":
    main()
