from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize one or more evaluation JSON files as a markdown table.")
    parser.add_argument("paths", nargs="+", help="Metric JSON files produced by scripts/run_baseline.py")
    return parser.parse_args()


def format_action_counts(summary: dict) -> str:
    counts = summary.get("pred_action_counts", {})
    if not counts:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def main() -> None:
    args = parse_args()
    print("| Run | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse | Pred Actions |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for raw_path in args.paths:
        path = Path(raw_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        summary = payload["summary"]
        label = path.stem.replace("_metrics", "")
        print(
            "| "
            + " | ".join(
                [
                    label,
                    str(summary["num_examples"]),
                    str(summary["avg_utility"]),
                    str(summary["action_accuracy"]),
                    str(summary["answer_em"]),
                    str(summary.get("answer_contains_rate", 0.0)),
                    str(summary["over_answer_rate"]),
                    str(summary.get("json_parse_rate", 0.0)),
                    format_action_counts(summary),
                ]
            )
            + " |"
        )


if __name__ == "__main__":
    main()
