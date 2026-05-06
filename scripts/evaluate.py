from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import load_examples, read_jsonl
from coc.metrics import evaluate_predictions
from coc.schema import Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate critique-or-clarify predictions.")
    parser.add_argument("--data", required=True, help="Path to the gold JSONL data.")
    parser.add_argument("--predictions", required=True, help="Path to prediction JSONL.")
    parser.add_argument("--report-json", help="Optional path to save the full report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    predictions = [Prediction.from_dict(row) for row in read_jsonl(args.predictions)]
    summary, details = evaluate_predictions(examples, predictions)
    print(json.dumps(summary, indent=2))

    if args.report_json:
        report_path = Path(args.report_json)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
