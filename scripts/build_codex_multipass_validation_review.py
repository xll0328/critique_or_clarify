from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from build_human_validation_work_queue import (
    DEFAULT_METRICS,
    DEFAULT_PREDICTIONS,
    FIELDNAMES,
    build_claim_rows,
    build_example_rows,
    read_jsonl,
)
from build_stale_action_label_audit import audit_predictions


PASS_FIELDNAMES = FIELDNAMES + ["pass_id", "pass_name", "pass_decision", "pass_notes"]
CONSENSUS_FIELDNAMES = FIELDNAMES + [
    "multipass_consensus_decision",
    "multipass_accept_count",
    "multipass_non_accept_count",
    "multipass_consensus_notes",
]
PASS_SPECS: list[tuple[str, str]] = [
    ("P1", "ontology_boundary"),
    ("P2", "artifact_and_source_presence"),
    ("P3", "gold_answer_or_response_quality"),
    ("P4", "claim_arithmetic_recompute"),
    ("P5", "failure_audit_specificity"),
    ("P6", "consensus_stress_pass"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run six Codex expert-review passes over the active validation queue."
    )
    parser.add_argument("--queue", default="_assets/human_validation_work_queue.csv", help="Input queue CSV.")
    parser.add_argument(
        "--split",
        default="data/processed/day1_quick_plus_stale_pool.jsonl",
        help="Dataset split used by example-label rows.",
    )
    parser.add_argument(
        "--output-dir",
        default="_assets/codex_multipass_validation_review",
        help="Directory for pass-level and consensus outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    queue_path = Path(args.queue)
    split_path = Path(args.split)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(queue_path)
    examples = read_jsonl(split_path)
    context = build_context(examples, split_path)
    pass_rows = run_passes(rows, context)
    consensus_rows = build_consensus(rows, pass_rows)

    pass_csv = output_dir / "pass_level_review.csv"
    consensus_csv = output_dir / "consensus_review.csv"
    summary_md = output_dir / "summary.md"
    write_csv(pass_csv, pass_rows, PASS_FIELDNAMES)
    write_csv(consensus_csv, consensus_rows, CONSENSUS_FIELDNAMES)
    summary_md.write_text(render_summary(pass_rows, consensus_rows, pass_csv, consensus_csv), encoding="utf-8")
    print(f"Wrote {len(pass_rows)} pass rows and {len(consensus_rows)} consensus rows to {output_dir}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_context(examples: list[dict[str, Any]], split_path: Path) -> dict[str, Any]:
    expected_rows = build_example_rows(examples, split_path) + build_claim_rows(
        examples,
        split_path,
        DEFAULT_METRICS,
        DEFAULT_PREDICTIONS,
    )
    examples_by_id = {example["id"]: example for example in examples}
    expected_by_id = {row["queue_id"]: row for row in expected_rows}
    audits = {}
    for prediction_path in DEFAULT_PREDICTIONS:
        if prediction_path.exists():
            audit = audit_predictions(prediction_path, examples_by_id)
            audits[audit["model"]] = audit
    metric_payloads = {
        str(path): json.loads(path.read_text(encoding="utf-8"))
        for path in DEFAULT_METRICS
        if path.exists()
    }
    return {
        "examples_by_id": examples_by_id,
        "expected_by_id": expected_by_id,
        "audits": audits,
        "metric_payloads": metric_payloads,
    }


def run_passes(rows: list[dict[str, str]], context: dict[str, Any]) -> list[dict[str, str]]:
    pass_functions: list[Callable[[dict[str, str], dict[str, Any]], tuple[str, str]]] = [
        ontology_boundary_pass,
        artifact_and_source_presence_pass,
        gold_answer_or_response_quality_pass,
        claim_arithmetic_recompute_pass,
        failure_audit_specificity_pass,
        consensus_stress_pass,
    ]
    pass_rows: list[dict[str, str]] = []
    for pass_index, (pass_id, pass_name) in enumerate(PASS_SPECS):
        pass_fn = pass_functions[pass_index]
        for row in rows:
            decision, notes = pass_fn(row, context)
            pass_rows.append(
                {
                    **row,
                    "pass_id": pass_id,
                    "pass_name": pass_name,
                    "pass_decision": decision,
                    "pass_notes": notes,
                }
            )
    return pass_rows


def ontology_boundary_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    if row["validation_type"] != "example_gold_label":
        return "accept", "Claim row uses a recognized validation type and is outside action-label ontology."
    example = context["examples_by_id"].get(row["example_id"])
    if example is None:
        return "reject", "Example is missing from split."
    action = example.get("gold_action", "")
    source = example.get("source", "")
    slice_name = example.get("metadata", {}).get("slice", "")
    if action == "answer" and slice_name in {"answerable_control", "conflicting_evidence"}:
        return "accept", "Answer action matches an answerable/control or conflict-but-answerable row."
    if action == "challenge" and slice_name in {"false_premise", "stale_premise"}:
        return "accept", "Challenge action matches a false or stale premise row."
    if action == "ask" and slice_name == "ambiguous_intent":
        return "accept", "Ask action matches an ambiguous-intent row that requires clarification."
    if action == "abstain" and slice_name == "insufficient_evidence":
        return "accept", "Abstain action matches an insufficient-evidence row."
    return "needs_second_pass", f"Unexpected action/slice/source combination: action={action}; slice={slice_name}; source={source}."


def artifact_and_source_presence_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    if row["validation_type"] == "example_gold_label":
        example = context["examples_by_id"].get(row["example_id"])
        if example is None:
            return "reject", "Example is missing from split."
        source = example.get("source", "")
        metadata = example.get("metadata", {})
        if source == "QACC" and example.get("passages"):
            return "accept", "QACC row has local retrieved passages."
        if source == "PCBench":
            return "accept", "PCBench row is self-contained in the prompt."
        if source == "stale-fact-seed" and example.get("passages") and metadata.get("source_url"):
            return "accept", "Stale row has local passages plus source URL metadata."
        if source == "synthetic-expansion-candidate" and metadata.get("candidate_status") == "needs_human_validation":
            action = example.get("gold_action", "")
            if action in {"answer", "challenge"} and example.get("passages"):
                return "accept", "Synthetic answer/challenge candidate has local passages and pending-validation metadata."
            if action == "ask" and metadata.get("requires_clarification") and metadata.get("missing_slots"):
                return "accept", "Synthetic ask candidate includes missing-slot metadata for clarification."
            if action == "abstain" and metadata.get("abstain_type"):
                return "accept", "Synthetic abstain candidate includes abstain-type metadata."
        return "needs_second_pass", f"Missing source support for source={source}."
    missing = [path for path in source_paths(row["source_artifact"]) if not path.exists()]
    if missing:
        return "needs_second_pass", "Missing source artifact(s): " + ", ".join(str(path) for path in missing)
    return "accept", "All referenced source artifacts exist locally."


def gold_answer_or_response_quality_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    if row["validation_type"] != "example_gold_label":
        return "accept", "Claim row has no gold answer/response label to adjudicate in this pass."
    example = context["examples_by_id"].get(row["example_id"])
    if example is None:
        return "reject", "Example is missing from split."
    action = example.get("gold_action", "")
    if action == "answer":
        if example.get("gold_answer"):
            return "accept", "Answer row has a non-empty gold answer."
        return "reject", "Answer row is missing gold_answer."
    if action == "challenge":
        response = str(example.get("gold_response", ""))
        if not response:
            return "reject", "Challenge row is missing gold_response."
        if (
            "outdated" in response
            or "stale" in response
            or "incorrect premise" in response
            or "supported premise" in response
        ):
            return "accept", "Challenge response explicitly names the stale or incorrect premise and gives the correction."
        return "needs_second_pass", "Challenge response exists but does not clearly state outdated/incorrect premise."
    return "accept", f"Gold action {action} has no answer/response-specific issue in this split."


def claim_arithmetic_recompute_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    expected = context["expected_by_id"].get(row["queue_id"])
    if expected is None:
        return "reject", "Could not regenerate this queue row from current artifacts."
    mismatches = [
        field
        for field in ("source_artifact", "example_id", "slice", "model", "gold_action", "check_question", "ai_prefill")
        if row.get(field, "") != expected.get(field, "")
    ]
    if mismatches:
        return "fix", "Regenerated queue row differs in: " + ", ".join(mismatches)
    return "accept", "Queue row regenerates exactly from current split, metric, and prediction artifacts."


def failure_audit_specificity_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    validation_type = row["validation_type"]
    if validation_type == "action_label_failure_claim":
        expected = context["expected_by_id"].get(row["queue_id"], {})
        if row.get("ai_prefill") == expected.get("ai_prefill"):
            return "accept", "Action-label failure claim matches regenerated stale update-mention audit."
        return "fix", "Action-label failure claim differs from regenerated audit prefill."
    if validation_type == "metric_claim":
        payload = context["metric_payloads"].get(row["source_artifact"])
        if payload is None:
            return "needs_second_pass", "Metric JSON not loaded."
        summary = payload.get("summary", {})
        stale = summary.get("per_slice", {}).get("stale_premise", {})
        values = [
            summary.get("action_accuracy"),
            summary.get("avg_utility"),
            stale.get("action_accuracy"),
            stale.get("avg_utility"),
            stale.get("over_answer_rate"),
        ]
        if all(isinstance(value, (int, float)) and math.isfinite(value) for value in values):
            return "accept", "Metric JSON contains finite overall and stale-premise headline values."
        return "needs_second_pass", "Metric JSON contains missing or non-finite headline values."
    if validation_type == "example_gold_label":
        example = context["examples_by_id"].get(row["example_id"])
        if example is None:
            return "reject", "Example is missing from split."
        metadata = example.get("metadata", {})
        source = example.get("source", "")
        if source == "stale-fact-seed" and metadata.get("entity") and metadata.get("source_url"):
            return "accept", "Stale row includes corrected entity and source URL metadata for spot-checking."
        if source == "PCBench" and example.get("gold_action") == "challenge":
            original = metadata.get("original_premise", "")
            recomposed = metadata.get("recomposed_premise", "")
            if original and recomposed and original != recomposed:
                return "accept", "PCBench challenge row has distinct original and recomposed premises."
            return "needs_second_pass", "PCBench challenge row lacks distinct premise metadata."
        return "accept", "No failure-audit-specific issue for this example row."
    return "accept", "No failure-audit-specific issue for this claim type."


def consensus_stress_pass(row: dict[str, str], context: dict[str, Any]) -> tuple[str, str]:
    checks = [
        ontology_boundary_pass(row, context),
        artifact_and_source_presence_pass(row, context),
        gold_answer_or_response_quality_pass(row, context),
        claim_arithmetic_recompute_pass(row, context),
        failure_audit_specificity_pass(row, context),
    ]
    non_accept = [f"{decision}: {notes}" for decision, notes in checks if decision != "accept"]
    if non_accept:
        return "needs_second_pass", "Stress pass found non-accept signals: " + " | ".join(non_accept)
    return "accept", "Stress pass found no disagreement across the first five review lenses."


def build_consensus(rows: list[dict[str, str]], pass_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for pass_row in pass_rows:
        by_id[pass_row["queue_id"]].append(pass_row)
    consensus_rows: list[dict[str, str]] = []
    for row in rows:
        row_passes = by_id[row["queue_id"]]
        accept_count = sum(1 for pass_row in row_passes if pass_row["pass_decision"] == "accept")
        non_accept = [pass_row for pass_row in row_passes if pass_row["pass_decision"] != "accept"]
        if not non_accept:
            decision = "accept"
            notes = "All six Codex review passes accepted this row."
        elif any(pass_row["pass_decision"] == "reject" for pass_row in non_accept):
            decision = "reject"
            notes = summarize_non_accept(non_accept)
        elif any(pass_row["pass_decision"] == "fix" for pass_row in non_accept):
            decision = "fix"
            notes = summarize_non_accept(non_accept)
        else:
            decision = "needs_second_pass"
            notes = summarize_non_accept(non_accept)
        consensus_rows.append(
            {
                **row,
                "multipass_consensus_decision": decision,
                "multipass_accept_count": str(accept_count),
                "multipass_non_accept_count": str(len(non_accept)),
                "multipass_consensus_notes": notes,
            }
        )
    return consensus_rows


def summarize_non_accept(non_accept: list[dict[str, str]]) -> str:
    return " | ".join(
        f"{row['pass_id']} {row['pass_name']} -> {row['pass_decision']}: {row['pass_notes']}"
        for row in non_accept
    )


def source_paths(source_artifact: str) -> list[Path]:
    return [Path(part.strip()) for part in source_artifact.split("|") if part.strip()]


def render_summary(
    pass_rows: list[dict[str, str]],
    consensus_rows: list[dict[str, str]],
    pass_csv: Path,
    consensus_csv: Path,
) -> str:
    consensus_counts = Counter(row["multipass_consensus_decision"] for row in consensus_rows)
    pass_counts = Counter((row["pass_name"], row["pass_decision"]) for row in pass_rows)
    unresolved = [row for row in consensus_rows if row["multipass_consensus_decision"] != "accept"]
    lines = [
        "# Codex Multi-Pass Validation Review",
        "",
        "This is a six-pass Codex expert pre-review of the active validation queue. It does not fill `human_decision`; it is intended for the human reviewer to inspect and sign off.",
        "",
        f"Pass-level CSV: `{pass_csv}`",
        f"Consensus CSV: `{consensus_csv}`",
        "",
        "## Consensus",
        "",
        f"- Reviewed rows: `{len(consensus_rows)}`.",
        f"- Consensus accepted: `{consensus_counts.get('accept', 0)}`.",
        f"- Consensus follow-up rows: `{len(unresolved)}`.",
        "",
        "| Consensus decision | Rows |",
        "| --- | --- |",
    ]
    for decision in ("accept", "fix", "needs_second_pass", "reject"):
        lines.append(f"| {decision} | {consensus_counts.get(decision, 0)} |")
    lines.extend(["", "## Pass Counts", "", "| Pass | Accept | Fix | Needs second pass | Reject |", "| --- | --- | --- | --- | --- |"])
    for _, pass_name in PASS_SPECS:
        lines.append(
            f"| {pass_name} | {pass_counts.get((pass_name, 'accept'), 0)} | "
            f"{pass_counts.get((pass_name, 'fix'), 0)} | "
            f"{pass_counts.get((pass_name, 'needs_second_pass'), 0)} | "
            f"{pass_counts.get((pass_name, 'reject'), 0)} |"
        )
    if unresolved:
        lines.extend(["", "## Rows Requiring Follow-Up", ""])
        for row in unresolved:
            lines.append(f"- `{row['queue_id']}`: {row['multipass_consensus_notes']}")
    lines.extend(
        [
            "",
            "## Review Lenses",
            "",
            "1. `ontology_boundary`: action label versus slice and action ontology.",
            "2. `artifact_and_source_presence`: local artifacts, passages, and source metadata.",
            "3. `gold_answer_or_response_quality`: non-empty answers and explicit correction responses.",
            "4. `claim_arithmetic_recompute`: regenerated queue rows versus current artifacts.",
            "5. `failure_audit_specificity`: stale/failure audit and metric-specific checks.",
            "6. `consensus_stress_pass`: combined disagreement check over the first five lenses.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
