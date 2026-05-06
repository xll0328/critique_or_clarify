from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a blind adjudication TSV sheet.")
    parser.add_argument("--data", required=True, help="Input JSONL file.")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    parser.add_argument("--sample-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.data)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    rows = read_jsonl(input_path)
    if not rows:
        raise ValueError("Input dataset is empty.")

    rng = random.Random(args.seed)
    sample_size = min(args.sample_size, len(rows))
    sample = rng.sample(rows, sample_size)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "source",
        "prompt",
        "num_passages",
        "passage_preview",
        "annotator_a_action",
        "annotator_a_confidence",
        "annotator_a_decisive_issue",
        "annotator_a_notes",
        "annotator_b_action",
        "annotator_b_confidence",
        "annotator_b_decisive_issue",
        "annotator_b_notes",
        "adjudicated_action",
        "adjudication_status",
        "adjudicator_rationale",
        "rubric_issue",
        "final_confidence",
        "keep_for_benchmark",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in sample:
            passages = row.get("passages", [])
            preview = " || ".join(str(text).replace("\t", " ").strip() for text in passages[:2])
            writer.writerow(
                {
                    "id": row.get("id", ""),
                    "source": row.get("source", ""),
                    "prompt": str(row.get("prompt", "")).replace("\t", " ").strip(),
                    "num_passages": len(passages),
                    "passage_preview": preview[:400],
                    "annotator_a_action": "",
                    "annotator_a_confidence": "",
                    "annotator_a_decisive_issue": "",
                    "annotator_a_notes": "",
                    "annotator_b_action": "",
                    "annotator_b_confidence": "",
                    "annotator_b_decisive_issue": "",
                    "annotator_b_notes": "",
                    "adjudicated_action": "",
                    "adjudication_status": "",
                    "adjudicator_rationale": "",
                    "rubric_issue": "",
                    "final_confidence": "",
                    "keep_for_benchmark": "",
                }
            )

    print(f"Wrote {sample_size} adjudication rows to {output_path}")


if __name__ == "__main__":
    main()
