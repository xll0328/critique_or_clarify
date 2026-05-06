from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


VALID_DECISIONS = {"accept", "fix", "reject", "needs_second_pass"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize progress and label hygiene for the human-validation work queue."
    )
    parser.add_argument(
        "--queue",
        default="_assets/human_validation_work_queue.csv",
        help="Human-validation queue CSV path.",
    )
    parser.add_argument(
        "--output",
        default="_assets/human_validation_work_queue_summary.md",
        help="Markdown summary output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(Path(args.queue))
    report = render_summary(rows, queue_path=args.queue)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    print(report)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def render_summary(rows: list[dict[str, str]], *, queue_path: str) -> str:
    total = len(rows)
    completed = sum(1 for row in rows if row.get("human_decision", "").strip())
    invalid_decisions = [
        row
        for row in rows
        if row.get("human_decision", "").strip()
        and row.get("human_decision", "").strip() not in VALID_DECISIONS
    ]
    type_counts = Counter(row.get("validation_type", "unknown") for row in rows)
    priority_counts = Counter(row.get("priority", "unknown") for row in rows)
    lines = [
        "# Human Validation Work Queue Summary",
        "",
        f"Queue: `{queue_path}`",
        "",
        f"Active work queue: `{completed} / {total}` rows completed.",
        "",
        "This summary tracks real human decisions only. AI prefill remains triage and is not a substitute for completed human validation.",
        "",
        "## By Validation Type",
        "",
        "| Validation Type | Rows |",
        "| --- | --- |",
    ]
    for key in sorted(type_counts):
        lines.append(f"| {key} | {type_counts[key]} |")
    lines.extend(
        [
            "",
            "## By Priority",
            "",
            "| Priority | Rows |",
            "| --- | --- |",
        ]
    )
    for key in sorted(priority_counts):
        lines.append(f"| {key} | {priority_counts[key]} |")
    lines.extend(
        [
            "",
            "## Label Hygiene",
            "",
            f"- Invalid non-empty `human_decision` labels: `{len(invalid_decisions)}`.",
            f"- Allowed labels: `{', '.join(sorted(VALID_DECISIONS))}`.",
        ]
    )
    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    main()
