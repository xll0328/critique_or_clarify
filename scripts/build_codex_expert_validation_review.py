from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from build_human_validation_work_queue import FIELDNAMES, read_jsonl, split_prefill


REVIEW_FIELDNAMES = FIELDNAMES + ["codex_expert_decision", "codex_expert_notes"]
VALID_CODEX_DECISIONS = {"accept", "fix", "reject", "needs_second_pass"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Codex expert review of the active validation queue without filling human_decision."
    )
    parser.add_argument("--queue", default="_assets/human_validation_work_queue.csv", help="Input validation queue.")
    parser.add_argument(
        "--split",
        default="data/processed/day1_quick_plus_stale_pool.jsonl",
        help="Dataset split used by example-label validation rows.",
    )
    parser.add_argument(
        "--output-csv",
        default="_assets/codex_expert_validation_review.csv",
        help="CSV output with Codex expert decisions.",
    )
    parser.add_argument(
        "--output-md",
        default="_assets/codex_expert_validation_review.md",
        help="Markdown summary output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    queue_path = Path(args.queue)
    split_path = Path(args.split)
    rows = read_csv(queue_path)
    examples_by_id = {example["id"]: example for example in read_jsonl(split_path)}
    reviewed = [review_row(row, examples_by_id, split_path) for row in rows]

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    write_csv(output_csv, reviewed)

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_summary(reviewed, output_csv), encoding="utf-8")
    print(f"Wrote {len(reviewed)} Codex expert review rows to {output_csv}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def review_row(row: dict[str, str], examples_by_id: dict[str, dict[str, Any]], split_path: Path) -> dict[str, str]:
    reviewed = dict(row)
    decision, notes = make_codex_decision(row, examples_by_id, split_path)
    reviewed["codex_expert_decision"] = decision
    reviewed["codex_expert_notes"] = notes
    return reviewed


def make_codex_decision(
    row: dict[str, str],
    examples_by_id: dict[str, dict[str, Any]],
    split_path: Path,
) -> tuple[str, str]:
    validation_type = row.get("validation_type", "")
    if validation_type == "example_gold_label":
        return review_example_row(row, examples_by_id)
    if validation_type == "split_accounting_claim":
        expected = split_prefill(list(examples_by_id.values()))
        return compare_prefill(row, expected, f"Recomputed split accounting from {split_path}.")
    if validation_type in {
        "metric_claim",
        "scale_delta_claim",
        "matched_style_delta_claim",
        "action_label_failure_claim",
    }:
        return review_claim_row(row)
    return "needs_second_pass", f"Unknown validation_type={validation_type}."


def review_example_row(row: dict[str, str], examples_by_id: dict[str, dict[str, Any]]) -> tuple[str, str]:
    example_id = row.get("example_id", "")
    example = examples_by_id.get(example_id)
    if example is None:
        return "reject", f"Example {example_id} is missing from the split."

    action = example.get("gold_action", "")
    source = example.get("source", "")
    metadata = example.get("metadata", {})
    slice_name = metadata.get("slice", "unknown")

    if action == "answer" and source == "PCBench" and example.get("gold_answer"):
        return "accept", "Self-contained PCBench answerable-control item with a gold answer; answer is the right next action."
    if action == "answer" and source == "QACC" and example.get("gold_answer"):
        return (
            "accept",
            "QACC item has a concrete candidate answer and local passages with supporting evidence; retrieval conflict alone does not force abstention.",
        )
    if action == "challenge" and source == "PCBench":
        if metadata.get("original_premise") and metadata.get("recomposed_premise") and example.get("gold_response"):
            return "accept", "PCBench paired item contains an injected contradictory premise and a correction response."
        return "needs_second_pass", "PCBench challenge row is missing premise metadata or gold_response."
    if action == "challenge" and source == "stale-fact-seed":
        if example.get("passages") and metadata.get("source_url") and example.get("gold_response"):
            return (
                "accept",
                "Stale-premise row includes local background/update passages, source URL metadata, and a correction response.",
            )
        return "needs_second_pass", "Stale row is missing passages, source URL metadata, or gold_response."
    if source == "synthetic-expansion-candidate":
        if metadata.get("candidate_status") != "needs_human_validation":
            return "needs_second_pass", "Synthetic candidate row is missing candidate_status=needs_human_validation."
        if action == "answer":
            if slice_name in {"answerable_control", "conflicting_evidence"} and example.get("gold_answer") and example.get("passages"):
                return "accept", "Synthetic answer candidate has answerable/conflict-but-answerable slice, passages, and gold answer."
            return "needs_second_pass", "Synthetic answer candidate is missing slice alignment, passages, or gold_answer."
        if action == "challenge":
            if slice_name in {"false_premise", "stale_premise"} and example.get("gold_response") and example.get("passages"):
                return "accept", "Synthetic challenge candidate has false/stale slice alignment, passages, and correction response."
            return "needs_second_pass", "Synthetic challenge candidate is missing slice alignment, passages, or gold_response."
        if action in {"ask", "abstain"}:
            return "accept", f"Synthetic {action} candidate is aligned with the action ontology."
        return "needs_second_pass", f"Synthetic candidate has unsupported action={action}."
    if action in {"ask", "abstain"}:
        return "accept", f"Gold action {action} is represented and can be reviewed under the ontology."
    return "needs_second_pass", f"Unrecognized or weakly supported example pattern: source={source}; slice={slice_name}; action={action}."


def review_claim_row(row: dict[str, str]) -> tuple[str, str]:
    prefill = row.get("ai_prefill", "")
    if not prefill:
        return "needs_second_pass", "Claim row has no ai_prefill to check."
    if any(value in prefill for value in ("missing", "nan", "None")):
        return "needs_second_pass", f"Claim prefill may be incomplete: {prefill}"
    return "accept", f"Claim row is internally specified by the refreshed artifact prefill: {prefill}"


def compare_prefill(row: dict[str, str], expected: str, prefix: str) -> tuple[str, str]:
    actual = row.get("ai_prefill", "")
    if actual == expected:
        return "accept", f"{prefix} Values match: {expected}"
    return "fix", f"{prefix} Expected `{expected}` but queue has `{actual}`."


def render_summary(rows: list[dict[str, str]], output_csv: Path) -> str:
    decisions = Counter(row["codex_expert_decision"] for row in rows)
    by_type = Counter(row["validation_type"] for row in rows)
    unresolved = [row for row in rows if row["codex_expert_decision"] != "accept"]
    lines = [
        "# Codex Expert Validation Review",
        "",
        "This file records an AI expert review of the active validation queue. It is not human validation and does not fill `human_decision`.",
        "",
        f"CSV: `{output_csv}`",
        "",
        "## Summary",
        "",
        f"- Reviewed rows: `{len(rows)}`.",
        f"- Accepted by Codex expert review: `{decisions.get('accept', 0)}`.",
        f"- Needs follow-up: `{len(unresolved)}`.",
        "",
        "## By Type",
        "",
        "| Validation type | Rows |",
        "| --- | --- |",
    ]
    for validation_type, count in sorted(by_type.items()):
        lines.append(f"| {validation_type} | {count} |")
    lines.extend(["", "## Decision Counts", "", "| Decision | Rows |", "| --- | --- |"])
    for decision in sorted(VALID_CODEX_DECISIONS):
        lines.append(f"| {decision} | {decisions.get(decision, 0)} |")
    if unresolved:
        lines.extend(["", "## Follow-Up Rows", ""])
        for row in unresolved:
            lines.append(f"- `{row['queue_id']}`: {row['codex_expert_notes']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Use this review as expert triage or a second-pass aid. Paper-facing human-validation claims still require real `human_decision` entries in `_assets/human_validation_work_queue.csv`.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
