from __future__ import annotations

import argparse
import csv
import json
from math import ceil
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export markdown packets that make the human-validation queue fast to review."
    )
    parser.add_argument(
        "--queue",
        default="_assets/human_validation_work_queue.csv",
        help="Human-validation queue CSV path.",
    )
    parser.add_argument(
        "--split",
        default="data/processed/day1_quick_plus_stale_pool.jsonl",
        help="Dataset JSONL used to expand example-label rows.",
    )
    parser.add_argument(
        "--output-dir",
        default="_assets/human_validation_packets",
        help="Directory for packet markdown files.",
    )
    parser.add_argument("--batch-size", type=int, default=15, help="Rows per packet.")
    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include rows that already have a human_decision.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    queue_path = Path(args.queue)
    split_path = Path(args.split)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_queue(queue_path)
    if not args.include_completed:
        rows = [row for row in rows if not row.get("human_decision", "").strip()]
    rows.sort(key=sort_key)
    examples = {row["id"]: row for row in read_jsonl(split_path)} if split_path.exists() else {}
    packet_paths = write_packets(
        rows,
        examples=examples,
        queue_path=queue_path,
        split_path=split_path,
        output_dir=output_dir,
        batch_size=args.batch_size,
    )
    write_index(
        rows,
        packet_paths=packet_paths,
        output_dir=output_dir,
        queue_path=queue_path,
        batch_size=args.batch_size,
    )
    print(f"Wrote {len(packet_paths)} packet(s) for {len(rows)} queue row(s) to {output_dir}")


def read_queue(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_packets(
    rows: list[dict[str, str]],
    *,
    examples: dict[str, dict[str, Any]],
    queue_path: Path,
    split_path: Path,
    output_dir: Path,
    batch_size: int,
) -> list[Path]:
    if batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    packet_paths: list[Path] = []
    total_batches = ceil(len(rows) / batch_size) if rows else 0
    for batch_index in range(total_batches):
        batch_rows = rows[batch_index * batch_size : (batch_index + 1) * batch_size]
        packet_path = output_dir / f"batch_{batch_index + 1:03d}.md"
        packet_path.write_text(
            render_packet(
                batch_rows,
                batch_number=batch_index + 1,
                total_batches=total_batches,
                examples=examples,
                queue_path=queue_path,
                split_path=split_path,
            )
            + "\n",
            encoding="utf-8",
        )
        packet_paths.append(packet_path)
    return packet_paths


def write_index(
    rows: list[dict[str, str]],
    *,
    packet_paths: list[Path],
    output_dir: Path,
    queue_path: Path,
    batch_size: int,
) -> None:
    by_type: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for row in rows:
        by_type[row.get("validation_type", "unknown")] = by_type.get(row.get("validation_type", "unknown"), 0) + 1
        by_priority[row.get("priority", "unknown")] = by_priority.get(row.get("priority", "unknown"), 0) + 1
    lines = [
        "# Human Validation Packets",
        "",
        f"Queue: `{queue_path}`",
        "",
        f"Pending rows exported: `{len(rows)}`.",
        "",
        "These packets are review aids. A row is not human-validated until `human_decision` is recorded in the CSV.",
        "",
        "## Packets",
        "",
        "| Packet | Rows |",
        "| --- | --- |",
    ]
    for packet_path in packet_paths:
        rel_path = packet_path.relative_to(output_dir.parent)
        lines.append(f"| `{rel_path}` | {packet_row_range(packet_path.name, len(rows), batch_size)} |")
    lines.extend(["", "## By Validation Type", "", "| Type | Rows |", "| --- | --- |"])
    for key in sorted(by_type):
        lines.append(f"| {key} | {by_type[key]} |")
    lines.extend(["", "## By Priority", "", "| Priority | Rows |", "| --- | --- |"])
    for key in sorted(by_priority):
        lines.append(f"| {key} | {by_priority[key]} |")
    (output_dir / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_packet(
    rows: list[dict[str, str]],
    *,
    batch_number: int,
    total_batches: int,
    examples: dict[str, dict[str, Any]],
    queue_path: Path,
    split_path: Path,
) -> str:
    lines = [
        f"# Human Validation Packet {batch_number:03d} / {total_batches:03d}",
        "",
        f"Queue: `{queue_path}`",
        f"Split: `{split_path}`",
        "",
        "Record final decisions in the CSV, not in this packet. Allowed decisions: `accept`, `fix`, `reject`, `needs_second_pass`.",
        "",
    ]
    for row in rows:
        lines.extend(render_row(row, examples))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_row(row: dict[str, str], examples: dict[str, dict[str, Any]]) -> list[str]:
    queue_id = row.get("queue_id", "")
    title = f"## {queue_id} | {row.get('validation_type', '')} | {row.get('priority', '')}"
    lines = [
        title,
        "",
        f"- Status: `{row.get('status', '')}`",
        f"- Source artifact: `{row.get('source_artifact', '')}`",
        f"- Check: {row.get('check_question', '')}",
        f"- AI prefill: {row.get('ai_prefill', '')}",
        "- Decision fields to fill in CSV: `human_decision`, `human_notes`",
    ]
    example_id = row.get("example_id", "")
    if example_id:
        example = examples.get(example_id)
        if example is None:
            lines.append(f"- Example `{example_id}` was not found in the split file.")
        else:
            lines.extend(render_example_context(example))
    return lines


def render_example_context(example: dict[str, Any]) -> list[str]:
    metadata = example.get("metadata", {})
    lines = [
        "",
        "### Example Context",
        "",
        f"- Example ID: `{example.get('id', '')}`",
        f"- Source: `{example.get('source', '')}`",
        f"- Slice: `{metadata.get('slice', 'unknown')}`",
        f"- Gold action: `{example.get('gold_action', '')}`",
    ]
    if example.get("gold_answer"):
        lines.append(f"- Gold answer: {example['gold_answer']}")
    if example.get("gold_response"):
        lines.append(f"- Gold response: {example['gold_response']}")
    if metadata.get("stale_claim"):
        lines.append(f"- Stale claim: {metadata['stale_claim']}")
    if metadata.get("corrected_fact"):
        lines.append(f"- Corrected fact: {metadata['corrected_fact']}")
    if metadata.get("source_url"):
        lines.append(f"- Source URL: {metadata['source_url']}")
    passages = example.get("passages", [])
    if passages:
        lines.extend(["", "### Passages", ""])
        for index, passage in enumerate(passages, start=1):
            lines.append(f"{index}. {passage}")
    lines.extend(["", "### Prompt", "", "```text", str(example.get("prompt", "")), "```"])
    return lines


def sort_key(row: dict[str, str]) -> tuple[int, int, str]:
    priority_rank = {"high": 0, "medium": 1, "low": 2}.get(row.get("priority", ""), 3)
    type_rank = 0 if row.get("validation_type") != "example_gold_label" else 1
    return (priority_rank, type_rank, row.get("queue_id", ""))


def packet_row_range(packet_name: str, total_rows: int, batch_size: int = 15) -> str:
    batch_number = int(packet_name.removeprefix("batch_").removesuffix(".md"))
    start = (batch_number - 1) * batch_size + 1
    end = min(batch_number * batch_size, total_rows)
    return f"{start}-{end}"


if __name__ == "__main__":
    main()
