from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SPLITS = [
    Path("data/processed/day1_dev.jsonl"),
    Path("data/processed/day1_quick_plus_stale.jsonl"),
    Path("data/processed/day1_quick_plus_stale_pool.jsonl"),
    Path("data/processed/stale_fact_pool.jsonl"),
]

TARGETS = {
    "total_unique": 500,
    "by_slice": {
        "answerable_control": 120,
        "false_premise": 120,
        "stale_premise": 80,
        "conflicting_evidence": 120,
        "ambiguous_intent": 80,
        "insufficient_evidence": 80,
    },
    "by_action": {
        "answer": 200,
        "ask": 80,
        "challenge": 200,
        "abstain": 80,
    },
}

SLICE_ORDER = [
    "answerable_control",
    "false_premise",
    "stale_premise",
    "conflicting_evidence",
    "ambiguous_intent",
    "insufficient_evidence",
]
ACTION_ORDER = ["answer", "ask", "challenge", "abstain"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit current benchmark coverage against oral-level expansion targets."
    )
    parser.add_argument(
        "--split",
        action="append",
        default=[],
        help="JSONL split to audit. Repeatable. Defaults to current paper-facing Day-1 splits.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/benchmark_expansion_coverage_audit.md",
        help="Markdown audit output path.",
    )
    parser.add_argument(
        "--output-json",
        default="experiments/day1/benchmark_expansion_coverage_audit.json",
        help="Machine-readable audit output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    split_paths = [Path(path) for path in args.split] if args.split else DEFAULT_SPLITS
    split_summaries = [summarize_split(path) for path in split_paths]
    combined = summarize_combined(split_paths)
    gaps = build_gap_report(combined, TARGETS)

    payload = {
        "splits": split_summaries,
        "combined_unique": combined,
        "targets": TARGETS,
        "gaps": gaps,
        "priority_build_queue": priority_build_queue(gaps),
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize_split(path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    return {
        "path": str(path),
        "rows": len(rows),
        "unique_ids": len({str(row.get("id", "")) for row in rows}),
        "by_slice": ordered_counter(count_by(rows, "slice")),
        "by_action": ordered_counter(count_by(rows, "action")),
        "by_source": dict(sorted(count_by(rows, "source").items())),
    }


def summarize_combined(paths: list[Path]) -> dict[str, Any]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: Counter[str] = Counter()
    total_rows = 0
    for path in paths:
        for row in load_jsonl(path):
            total_rows += 1
            row_id = str(row.get("id", ""))
            if row_id in rows_by_id:
                duplicate_ids[row_id] += 1
                continue
            rows_by_id[row_id] = row

    rows = list(rows_by_id.values())
    return {
        "input_rows": total_rows,
        "unique_examples": len(rows),
        "duplicate_ids": sum(duplicate_ids.values()),
        "by_slice": ordered_counter(count_by(rows, "slice")),
        "by_action": ordered_counter(count_by(rows, "action")),
        "by_source": dict(sorted(count_by(rows, "source").items())),
    }


def count_by(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        if field == "slice":
            value = row.get("metadata", {}).get("slice", "unknown")
        elif field == "action":
            value = row.get("gold_action", "unknown")
        elif field == "source":
            value = row.get("source", "unknown")
        else:
            raise ValueError(f"Unsupported field: {field}")
        counter[str(value)] += 1
    return counter


def ordered_counter(counter: Counter[str]) -> dict[str, int]:
    preferred = SLICE_ORDER + ACTION_ORDER
    ordered: dict[str, int] = {}
    for key in preferred:
        if key in counter and key not in ordered:
            ordered[key] = counter[key]
    for key in sorted(counter):
        if key not in ordered:
            ordered[key] = counter[key]
    return ordered


def build_gap_report(summary: dict[str, Any], targets: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_unique": {
            "current": summary["unique_examples"],
            "target": targets["total_unique"],
            "gap": max(0, targets["total_unique"] - summary["unique_examples"]),
        },
        "by_slice": build_dimension_gaps(summary["by_slice"], targets["by_slice"]),
        "by_action": build_dimension_gaps(summary["by_action"], targets["by_action"]),
    }


def build_dimension_gaps(current: dict[str, int], target: dict[str, int]) -> dict[str, dict[str, int]]:
    gaps = {}
    for key, target_count in target.items():
        current_count = int(current.get(key, 0))
        gaps[key] = {
            "current": current_count,
            "target": target_count,
            "gap": max(0, target_count - current_count),
        }
    return gaps


def priority_build_queue(gaps: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for dimension in ["by_action", "by_slice"]:
        for name, values in gaps[dimension].items():
            if values["gap"] > 0:
                items.append(
                    {
                        "dimension": dimension.replace("by_", ""),
                        "name": name,
                        "current": values["current"],
                        "target": values["target"],
                        "gap": values["gap"],
                    }
                )
    return sorted(items, key=lambda item: (-item["gap"], item["dimension"], item["name"]))


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Benchmark Expansion Coverage Audit",
        "",
        "Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.",
        "",
        "## Current Split Coverage",
        "",
        "| Split | Rows | Unique IDs | Actions | Slices |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for summary in payload["splits"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{summary['path']}`",
                    str(summary["rows"]),
                    str(summary["unique_ids"]),
                    compact_counts(summary["by_action"]),
                    compact_counts(summary["by_slice"]),
                ]
            )
            + " |"
        )

    combined = payload["combined_unique"]
    lines.extend(
        [
            "",
            "## Combined Unique Coverage",
            "",
            f"- Input rows across audited splits: `{combined['input_rows']}`",
            f"- Unique example IDs: `{combined['unique_examples']}`",
            f"- Duplicate IDs across audited splits: `{combined['duplicate_ids']}`",
            f"- Action coverage: {compact_counts(combined['by_action'])}",
            f"- Slice coverage: {compact_counts(combined['by_slice'])}",
            "",
            "## Oral-Level Expansion Gaps",
            "",
            f"- Unique-example target: `{payload['targets']['total_unique']}`; current `{payload['gaps']['total_unique']['current']}`; gap `{payload['gaps']['total_unique']['gap']}`.",
            "",
            "### Action Gaps",
            "",
            "| Action | Current | Target | Gap |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for action in ACTION_ORDER:
        values = payload["gaps"]["by_action"][action]
        lines.append(f"| `{action}` | {values['current']} | {values['target']} | {values['gap']} |")

    lines.extend(
        [
            "",
            "### Slice Gaps",
            "",
            "| Slice | Current | Target | Gap |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for slice_name in SLICE_ORDER:
        values = payload["gaps"]["by_slice"][slice_name]
        lines.append(f"| `{slice_name}` | {values['current']} | {values['target']} | {values['gap']} |")

    lines.extend(
        [
            "",
            "## Priority Build Queue",
            "",
            "| Priority | Dimension | Name | Current | Target | Gap |",
            "| ---: | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for index, item in enumerate(payload["priority_build_queue"], start=1):
        lines.append(
            f"| {index} | {item['dimension']} | `{item['name']}` | {item['current']} | {item['target']} | {item['gap']} |"
        )

    lines.extend(["", "## Interpretation", ""])
    lines.extend(render_interpretation(payload))
    return "\n".join(lines)


def compact_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"`{key}`={value}" for key, value in counts.items()) or "-"


def render_interpretation(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    total_gap = int(payload["gaps"]["total_unique"]["gap"])
    action_queue = [
        item for item in payload["priority_build_queue"] if item["dimension"] == "action" and item["gap"] > 0
    ]
    slice_queue = [
        item for item in payload["priority_build_queue"] if item["dimension"] == "slice" and item["gap"] > 0
    ]

    if total_gap == 0:
        lines.append(
            "- Candidate-augmented scale reaches the current 500-example planning target, but remains non-paper-facing until human validation and promotion."
        )
    else:
        lines.append(
            f"- The current candidate-augmented bundle is still `{total_gap}` examples short of the 500-example planning target."
        )

    if action_queue:
        item = action_queue[0]
        lines.append(
            f"- The largest remaining action deficit is `{item['name']}` with a gap of `{item['gap']}` examples."
        )
    else:
        lines.append("- Action-level candidate targets are currently met across all four actions.")

    if slice_queue:
        item = slice_queue[0]
        lines.append(
            f"- The next expansion sprint should focus on `{item['name']}` (slice gap `{item['gap']}`), then continue down the priority queue."
        )
    else:
        lines.append("- Slice-level candidate targets are currently met across all tracked slices.")

    return lines


if __name__ == "__main__":
    main()
