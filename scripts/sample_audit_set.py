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
    parser = argparse.ArgumentParser(description="Sample examples into a TSV audit sheet.")
    parser.add_argument("--data", required=True, help="Input JSONL file.")
    parser.add_argument("--output", required=True, help="Output TSV file.")
    parser.add_argument("--sample-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.data)
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
        "gold_action",
        "prompt",
        "num_passages",
        "passage_preview",
        "proposed_action",
        "final_action",
        "confidence",
        "disputed",
        "decisive_issue",
        "short_notes",
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
                    "gold_action": row.get("gold_action", ""),
                    "prompt": str(row.get("prompt", "")).replace("\t", " ").strip(),
                    "num_passages": len(passages),
                    "passage_preview": preview[:400],
                    "proposed_action": "",
                    "final_action": "",
                    "confidence": "",
                    "disputed": "",
                    "decisive_issue": "",
                    "short_notes": "",
                }
            )

    print(f"Wrote {sample_size} audit rows to {output_path}")


if __name__ == "__main__":
    main()
