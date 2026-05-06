from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import load_examples, read_jsonl
from coc.schema import Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample representative prediction failures from a run.")
    parser.add_argument("--data", required=True, help="Gold JSONL path.")
    parser.add_argument("--predictions", required=True, help="Prediction JSONL path.")
    parser.add_argument("--per-slice", type=int, default=2, help="Examples to sample per slice.")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    examples = {example.id: example for example in load_examples(args.data)}
    predictions = {
        prediction.example_id: prediction
        for prediction in (Prediction.from_dict(row) for row in read_jsonl(args.predictions))
    }

    failures_by_slice: dict[str, list[dict[str, str]]] = defaultdict(list)
    for example_id, example in examples.items():
        prediction = predictions.get(example_id)
        if prediction is None:
            continue
        action_correct = prediction.action == example.gold_action
        answer_correct = (
            example.gold_action.value != "answer"
            or prediction.action.value != "answer"
            or normalize(prediction.response) == normalize(example.gold_answer or "")
        )
        if action_correct and answer_correct:
            continue

        failures_by_slice[str(example.metadata.get("slice", "unknown"))].append(
            {
                "id": example.id,
                "gold_action": example.gold_action.value,
                "pred_action": prediction.action.value,
                "parsed_as": str(prediction.metadata.get("parsed_as", "missing")),
                "prompt": example.prompt,
                "gold_answer": example.gold_answer or "",
                "prediction": prediction.response,
            }
        )

    for slice_name in sorted(failures_by_slice):
        bucket = failures_by_slice[slice_name]
        chosen = rng.sample(bucket, min(args.per_slice, len(bucket)))
        print(f"## {slice_name} ({len(bucket)} failures)")
        for item in chosen:
            print(json.dumps(item, ensure_ascii=False))


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


if __name__ == "__main__":
    main()
