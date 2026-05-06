from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_stale_action_label_audit import audit_predictions
from compare_runs import fmt, infer_run_metadata


DEFAULT_SPLIT = Path("data/processed/day1_quick_plus_stale_pool.jsonl")
DEFAULT_METRICS = [
    Path("outputs/day1/qwen25_05b_day1_quick_plus_stale_pool_metrics.json"),
    Path("outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json"),
    Path("outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json"),
]
DEFAULT_PREDICTIONS = [
    Path("outputs/day1/qwen25_05b_day1_quick_plus_stale_pool.jsonl"),
    Path("outputs/day1/qwen25_15b_day1_quick_plus_stale_pool.jsonl"),
    Path("outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed.jsonl"),
]
FIELDNAMES = [
    "queue_id",
    "status",
    "priority",
    "validation_type",
    "source_artifact",
    "example_id",
    "slice",
    "model",
    "gold_action",
    "pred_action",
    "check_question",
    "ai_prefill",
    "human_decision",
    "human_notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the active human-validation work queue for paper-facing day-1 evidence."
    )
    parser.add_argument("--split", default=str(DEFAULT_SPLIT), help="Dataset split to validate example labels for.")
    parser.add_argument(
        "--metric",
        action="append",
        dest="metrics",
        default=None,
        help="Metric JSON path used for manuscript-claim validation rows. Repeatable.",
    )
    parser.add_argument(
        "--prediction",
        action="append",
        dest="predictions",
        default=None,
        help="Prediction JSONL path used for action-label audit validation rows. Repeatable.",
    )
    parser.add_argument(
        "--skip-claims",
        action="store_true",
        help="Only emit example-label validation rows.",
    )
    parser.add_argument(
        "--output",
        default="_assets/human_validation_work_queue.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    split_path = Path(args.split)
    examples = read_jsonl(split_path)
    rows = build_example_rows(examples, split_path)
    if not args.skip_claims:
        metric_paths = [Path(path) for path in (args.metrics if args.metrics is not None else DEFAULT_METRICS)]
        prediction_paths = [
            Path(path) for path in (args.predictions if args.predictions is not None else DEFAULT_PREDICTIONS)
        ]
        rows.extend(build_claim_rows(examples, split_path, metric_paths, prediction_paths))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preserve_existing_decisions(output_path, rows)
    write_csv(output_path, rows)
    print(f"Wrote {len(rows)} queue rows to {output_path}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_example_rows(examples: list[dict[str, Any]], split_path: Path) -> list[dict[str, str]]:
    rows = []
    for index, example in enumerate(examples, start=1):
        metadata = example.get("metadata", {})
        slice_name = str(metadata.get("slice", "unknown"))
        rows.append(
            make_row(
                queue_id=f"HV-EX-{index:03d}",
                priority=example_priority(slice_name),
                validation_type="example_gold_label",
                source_artifact=str(split_path),
                example_id=str(example["id"]),
                slice_name=slice_name,
                gold_action=str(example.get("gold_action", "")),
                check_question=example_check_question(example),
                ai_prefill=example_prefill(example),
            )
        )
    return rows


def build_claim_rows(
    examples: list[dict[str, Any]],
    split_path: Path,
    metric_paths: list[Path],
    prediction_paths: list[Path],
) -> list[dict[str, str]]:
    runs = [load_metric(path) for path in metric_paths if path.exists()]
    rows: list[dict[str, str]] = []
    rows.append(
        make_row(
            queue_id="HV-CL-001",
            priority="high",
            validation_type="split_accounting_claim",
            source_artifact=str(split_path),
            check_question="Verify that the expanded stale-pool split counts and slice labels match the JSONL file.",
            ai_prefill=split_prefill(examples),
        )
    )

    run_by_model = {run["model"]: run for run in runs}
    for queue_id, model in [
        ("HV-CL-002", "Qwen2.5-0.5B-Instruct"),
        ("HV-CL-003", "Qwen2.5-1.5B-Instruct"),
        ("HV-CL-004", "DeepSeek-R1-Distill-Qwen-1.5B"),
    ]:
        run = run_by_model.get(model)
        if run is None:
            continue
        rows.append(
            make_row(
                queue_id=queue_id,
                priority="high",
                validation_type="metric_claim",
                source_artifact=run["path"],
                model=model,
                check_question=f"Verify the expanded stale-pool headline metrics for {model}.",
                ai_prefill=stale_metric_prefill(run),
            )
        )

    qwen_small = run_by_model.get("Qwen2.5-0.5B-Instruct")
    qwen_mid = run_by_model.get("Qwen2.5-1.5B-Instruct")
    deepseek_mid = run_by_model.get("DeepSeek-R1-Distill-Qwen-1.5B")
    if qwen_small is not None and qwen_mid is not None:
        rows.append(scale_claim_row("HV-CL-005", qwen_small, qwen_mid, overall=True))
        rows.append(scale_claim_row("HV-CL-006", qwen_small, qwen_mid, overall=False))
    if qwen_mid is not None and deepseek_mid is not None:
        rows.append(matched_claim_row("HV-CL-007", qwen_mid, deepseek_mid, overall=True))
        rows.append(matched_claim_row("HV-CL-008", qwen_mid, deepseek_mid, overall=False))

    examples_by_id = {row["id"]: row for row in examples}
    audits = {
        audit["model"]: audit
        for audit in (audit_predictions(path, examples_by_id) for path in prediction_paths if path.exists())
    }
    for queue_id, model in [
        ("HV-CL-009", "Qwen2.5-1.5B-Instruct"),
        ("HV-CL-010", "Qwen2.5-0.5B-Instruct"),
    ]:
        audit = audits.get(model)
        if audit is None:
            continue
        rows.append(
            make_row(
                queue_id=queue_id,
                priority="high",
                validation_type="action_label_failure_claim",
                source_artifact=audit["path"],
                model=model,
                check_question=f"Verify the wrong-action update-mention audit claim for {model}.",
                ai_prefill=(
                    f"stale_n={audit['stale_n']}; correct_challenge={audit['correct_n']}; "
                    f"wrong_action={audit['wrong_n']}; wrong_plus_update={audit['wrong_update_n']}; "
                    f"answer_plus_update={audit['answer_update_n']}"
                ),
            )
        )
    return rows


def load_metric(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    label = path.stem.removesuffix("_metrics")
    run = infer_run_metadata(label)
    run["path"] = str(path)
    run["summary"] = payload["summary"]
    return run


def example_check_question(example: dict[str, Any]) -> str:
    action = example.get("gold_action", "")
    if action == "answer":
        return "Does the prompt/evidence support answering, and is the gold answer acceptable?"
    if action == "challenge":
        return "Does the prompt contain a false or stale premise that should be challenged rather than answered?"
    if action == "ask":
        return "Is the prompt underspecified enough that a follow-up question is the best action?"
    return "Is abstention the best-supported action for this example?"


def example_priority(slice_name: str) -> str:
    if slice_name in {
        "false_premise",
        "stale_premise",
        "ambiguous_intent",
        "insufficient_evidence",
    }:
        return "high"
    return "medium"


def example_prefill(example: dict[str, Any]) -> str:
    metadata = example.get("metadata", {})
    fields = [
        f"gold_action={example.get('gold_action', '')}",
        f"source={example.get('source', '')}",
        f"slice={metadata.get('slice', 'unknown')}",
    ]
    if example.get("gold_answer"):
        fields.append(f"gold_answer={shorten(str(example['gold_answer']), 80)}")
    if example.get("gold_response"):
        fields.append(f"gold_response={shorten(str(example['gold_response']), 100)}")
    if metadata.get("source_url"):
        fields.append(f"source_url={metadata['source_url']}")
    fields.append(f"prompt={shorten(str(example.get('prompt', '')), 140)}")
    return "; ".join(fields)


def split_prefill(examples: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for example in examples:
        slice_name = str(example.get("metadata", {}).get("slice", "unknown"))
        counts[slice_name] = counts.get(slice_name, 0) + 1
    ordered = ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
    return f"total={len(examples)}; {ordered}"


def stale_metric_prefill(run: dict[str, Any]) -> str:
    summary = run["summary"]
    stale = summary["per_slice"]["stale_premise"]
    return (
        f"overall_action_accuracy={fmt(summary['action_accuracy'])}; "
        f"overall_avg_utility={fmt(summary['avg_utility'])}; "
        f"stale_action_accuracy={fmt(stale['action_accuracy'])}; "
        f"stale_avg_utility={fmt(stale['avg_utility'])}; "
        f"stale_over_answer_rate={fmt(stale['over_answer_rate'])}"
    )


def scale_claim_row(queue_id: str, source: dict[str, Any], target: dict[str, Any], *, overall: bool) -> dict[str, str]:
    if overall:
        source_stats = source["summary"]
        target_stats = target["summary"]
        check = "Verify the overall Qwen 0.5B -> 1.5B scale delta on the expanded stale-pool split."
        prefill = (
            f"action_accuracy_delta={delta(target_stats['action_accuracy'], source_stats['action_accuracy'])}; "
            f"avg_utility_delta={delta(target_stats['avg_utility'], source_stats['avg_utility'])}"
        )
    else:
        source_stats = source["summary"]["per_slice"]["stale_premise"]
        target_stats = target["summary"]["per_slice"]["stale_premise"]
        check = "Verify the stale-premise Qwen 0.5B -> 1.5B scale delta on the expanded split."
        prefill = (
            f"stale_action_accuracy_delta={delta(target_stats['action_accuracy'], source_stats['action_accuracy'])}; "
            f"stale_over_answer_delta={delta(target_stats['over_answer_rate'], source_stats['over_answer_rate'])}"
        )
    return make_row(
        queue_id=queue_id,
        priority="high",
        validation_type="scale_delta_claim",
        source_artifact=f"{source['path']} | {target['path']}",
        model=f"{source['model']} -> {target['model']}",
        check_question=check,
        ai_prefill=prefill,
    )


def matched_claim_row(queue_id: str, instruct: dict[str, Any], reasoning: dict[str, Any], *, overall: bool) -> dict[str, str]:
    if overall:
        source_stats = instruct["summary"]
        target_stats = reasoning["summary"]
        check = "Verify the overall matched 1.5B reasoning-vs-instruct delta on the expanded stale-pool split."
        prefill = (
            f"action_accuracy_delta={delta(target_stats['action_accuracy'], source_stats['action_accuracy'])}; "
            f"avg_utility_delta={delta(target_stats['avg_utility'], source_stats['avg_utility'])}"
        )
    else:
        source_stats = instruct["summary"]["per_slice"]["stale_premise"]
        target_stats = reasoning["summary"]["per_slice"]["stale_premise"]
        check = "Verify the stale-premise matched 1.5B reasoning-vs-instruct delta on the expanded split."
        prefill = (
            f"stale_action_accuracy_delta={delta(target_stats['action_accuracy'], source_stats['action_accuracy'])}; "
            f"stale_over_answer_delta={delta(target_stats['over_answer_rate'], source_stats['over_answer_rate'])}"
        )
    return make_row(
        queue_id=queue_id,
        priority="high",
        validation_type="matched_style_delta_claim",
        source_artifact=f"{instruct['path']} | {reasoning['path']}",
        model=f"{instruct['model']} vs {reasoning['model']}",
        check_question=check,
        ai_prefill=prefill,
    )


def make_row(
    *,
    queue_id: str,
    priority: str,
    validation_type: str,
    source_artifact: str,
    example_id: str = "",
    slice_name: str = "",
    model: str = "",
    gold_action: str = "",
    pred_action: str = "",
    check_question: str,
    ai_prefill: str,
) -> dict[str, str]:
    return {
        "queue_id": queue_id,
        "status": "pending",
        "priority": priority,
        "validation_type": validation_type,
        "source_artifact": source_artifact,
        "example_id": example_id,
        "slice": slice_name,
        "model": model,
        "gold_action": gold_action,
        "pred_action": pred_action,
        "check_question": check_question,
        "ai_prefill": ai_prefill,
        "human_decision": "",
        "human_notes": "",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def preserve_existing_decisions(path: Path, rows: list[dict[str, str]]) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", newline="") as handle:
        existing_by_id = {row.get("queue_id", ""): row for row in csv.DictReader(handle)}
    for row in rows:
        existing = existing_by_id.get(row["queue_id"])
        if existing is None:
            continue
        for field in ("human_decision", "human_notes"):
            value = existing.get(field, "")
            if value.strip():
                row[field] = value
        if row["human_decision"].strip():
            row["status"] = existing.get("status", "").strip() or "completed"


def delta(target: float, source: float) -> str:
    value = target - source
    if value > 0:
        return f"+{fmt(value)}"
    return fmt(value)


def shorten(text: str, limit: int) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


if __name__ == "__main__":
    main()
