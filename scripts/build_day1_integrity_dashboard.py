from __future__ import annotations

import argparse
import csv
from pathlib import Path

from check_scale_reasoning_status import MODEL_ROWS, METRIC_ROWS, REPORT_ROWS, metric_status, model_status, report_status
from summarize_human_validation_work_queue import VALID_DECISIONS


PAPER_ASSETS = [
    ("Scale/reasoning comparison", Path("experiments/day1/day1_scale_reasoning_comparison.md")),
    ("Scale/reasoning CI report", Path("experiments/day1/day1_scale_reasoning_ci.md")),
    ("Expanded stale-pool pilot", Path("experiments/day1/day1_expanded_stale_pool_pilot.md")),
    ("Expanded stale-pool LaTeX table", Path("experiments/day1/tables/day1_expanded_stale_pool_pilot_main.tex")),
    ("Action-label audit", Path("experiments/day1/day1_expanded_stale_action_label_audit.md")),
    (
        "Action-label audit LaTeX table",
        Path("experiments/day1/tables/day1_expanded_stale_action_label_audit_main.tex"),
    ),
    ("Human-validation queue", Path("_assets/human_validation_work_queue.csv")),
    ("Human-validation packet index", Path("_assets/human_validation_packets/index.md")),
    ("Codex expert validation review", Path("_assets/codex_expert_validation_review.md")),
    ("Codex multi-pass validation review", Path("_assets/codex_multipass_validation_review/summary.md")),
    ("Human-validation protocol", Path("docs/human_validation_protocol.md")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a day-1 integrity dashboard from model status, paper assets, and validation progress."
    )
    parser.add_argument(
        "--queue",
        default="_assets/human_validation_work_queue.csv",
        help="Human-validation queue CSV path.",
    )
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_integrity_dashboard.md",
        help="Markdown dashboard output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dashboard = render_dashboard(queue_path=Path(args.queue))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dashboard + "\n", encoding="utf-8")
    print(dashboard)


def render_dashboard(*, queue_path: Path) -> str:
    validation = validation_summary(queue_path)
    codex_review = codex_review_summary(Path("_assets/codex_expert_validation_review.csv"))
    multipass_review = multipass_review_summary(Path("_assets/codex_multipass_validation_review/consensus_review.csv"))
    lines = [
        "# Day-1 Integrity Dashboard",
        "",
        "This dashboard tracks whether the current day-1 evidence is ready to support paper-facing claims.",
        "",
        "## Blocking Gates",
        "",
        "| Gate | State | Detail |",
        "| --- | --- | --- |",
    ]
    gate_row(
        "Human validation",
        validation["completed"] == validation["total"] and validation["total"] > 0,
        f"{validation['completed']} / {validation['total']} rows completed",
        lines,
    )
    gate_row(
        "Human decision labels",
        validation["invalid_decisions"] == 0,
        f"{validation['invalid_decisions']} invalid non-empty labels",
        lines,
    )
    gate_row(
        "DeepSeek-R1-Distill-Qwen-7B metrics",
        deepseek7b_metrics_ready(),
        "dev and quick+stale metrics required for final scale/reasoning comparison",
        lines,
    )
    lines.extend(
        [
            "",
            "## Model And Report Status",
            "",
            "| Artifact | State | Progress | Detail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for label, final_path, partial_path, expected_bytes in MODEL_ROWS:
        state, progress, detail = model_status(final_path, partial_path, expected_bytes)
        lines.append(f"| {label} | {state} | {progress} | {detail} |")
    for label, path in METRIC_ROWS:
        state, progress, detail = metric_status(path)
        lines.append(f"| {label} | {state} | {progress} | {detail} |")
    for label, path in REPORT_ROWS:
        state, progress, detail = report_status(path)
        lines.append(f"| {label} | {state} | {progress} | {detail} |")

    lines.extend(
        [
            "",
            "## Paper-Facing Assets",
            "",
            "| Asset | State | Path |",
            "| --- | --- | --- |",
        ]
    )
    for label, path in PAPER_ASSETS:
        state = "ready" if path.exists() else "missing"
        lines.append(f"| {label} | {state} | `{path}` |")

    lines.extend(
        [
            "",
            "## Human Validation",
            "",
            f"- Active work queue: `{validation['completed']} / {validation['total']}` rows completed.",
            f"- Pending rows: `{validation['pending']}`.",
            f"- Invalid non-empty `human_decision` labels: `{validation['invalid_decisions']}`.",
            f"- Codex expert review: `{codex_review['accepted']} / {codex_review['total']}` rows accepted in `_assets/codex_expert_validation_review.csv`.",
            f"- Codex multi-pass review: `{multipass_review['accepted']} / {multipass_review['total']}` rows consensus-accepted across six passes.",
        ]
    )
    if validation["completed"] == validation["total"] and validation["total"] > 0:
        lines.append("- Human-validation is complete for the active queue; all rows have recorded human decisions.")
    else:
        lines.append(
            "- Human-validation remains incomplete until the queue rows have real human decisions; AI prefill is not a substitute."
        )
    return "\n".join(lines).rstrip()


def validation_summary(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"total": 0, "completed": 0, "pending": 0, "invalid_decisions": 0}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    completed = sum(1 for row in rows if row.get("human_decision", "").strip())
    invalid = sum(
        1
        for row in rows
        if row.get("human_decision", "").strip()
        and row.get("human_decision", "").strip() not in VALID_DECISIONS
    )
    return {
        "total": len(rows),
        "completed": completed,
        "pending": len(rows) - completed,
        "invalid_decisions": invalid,
    }


def codex_review_summary(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"total": 0, "accepted": 0}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        "total": len(rows),
        "accepted": sum(1 for row in rows if row.get("codex_expert_decision", "") == "accept"),
    }


def multipass_review_summary(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"total": 0, "accepted": 0}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        "total": len(rows),
        "accepted": sum(1 for row in rows if row.get("multipass_consensus_decision", "") == "accept"),
    }


def gate_row(label: str, passed: bool, detail: str, lines: list[str]) -> None:
    state = "pass" if passed else "blocked"
    lines.append(f"| {label} | {state} | {detail} |")


def deepseek7b_metrics_ready() -> bool:
    required = [
        Path("outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json"),
        Path("outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json"),
    ]
    return all(path.exists() for path in required)


if __name__ == "__main__":
    main()
