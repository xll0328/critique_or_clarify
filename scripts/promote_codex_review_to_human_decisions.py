from __future__ import annotations

import argparse
import csv
from pathlib import Path

from build_codex_expert_validation_review import VALID_CODEX_DECISIONS
from build_human_validation_work_queue import FIELDNAMES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a signed-off Codex expert review into human_decision fields."
    )
    parser.add_argument("--queue", default="_assets/human_validation_work_queue.csv", help="Queue CSV to update.")
    parser.add_argument(
        "--codex-review",
        default="_assets/codex_expert_validation_review.csv",
        help="Codex expert review CSV to promote after human sign-off.",
    )
    parser.add_argument(
        "--reviewer",
        required=True,
        help="Human reviewer name or initials recorded in human_notes.",
    )
    parser.add_argument(
        "--confirm-reviewed",
        action="store_true",
        help="Required confirmation that the human reviewer has reviewed and accepts the Codex review.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing non-empty human_decision values.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be promoted without modifying the queue.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.confirm_reviewed:
        raise SystemExit("--confirm-reviewed is required before writing human_decision values.")

    queue_path = Path(args.queue)
    codex_path = Path(args.codex_review)
    rows = read_csv(queue_path)
    review_by_id = {row["queue_id"]: row for row in read_csv(codex_path)}
    updated, skipped = promote_rows(
        rows,
        review_by_id,
        reviewer=args.reviewer,
        overwrite=args.overwrite,
    )
    print(f"promote_codex_review updated={updated} skipped_existing={skipped}")
    if args.dry_run:
        return
    write_csv(queue_path, rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def promote_rows(
    rows: list[dict[str, str]],
    review_by_id: dict[str, dict[str, str]],
    *,
    reviewer: str,
    overwrite: bool = False,
) -> tuple[int, int]:
    updated = 0
    skipped = 0
    for row in rows:
        queue_id = row.get("queue_id", "")
        review = review_by_id.get(queue_id)
        if review is None:
            raise ValueError(f"missing Codex review row for queue_id={queue_id}")
        decision = review_decision(review)
        if decision not in VALID_CODEX_DECISIONS:
            raise ValueError(f"queue_id={queue_id} invalid review decision={decision}")
        if row.get("human_decision", "").strip() and not overwrite:
            skipped += 1
            continue

        row["human_decision"] = decision
        row["human_notes"] = signed_note(
            reviewer=reviewer,
            decision=decision,
            existing_note=row.get("human_notes", ""),
            codex_note=review_notes(review),
        )
        row["status"] = "completed"
        updated += 1
    return updated, skipped


def review_decision(review: dict[str, str]) -> str:
    return (
        review.get("multipass_consensus_decision", "").strip()
        or review.get("codex_expert_decision", "").strip()
    )


def review_notes(review: dict[str, str]) -> str:
    return (
        review.get("multipass_consensus_notes", "").strip()
        or review.get("codex_expert_notes", "").strip()
    )


def signed_note(*, reviewer: str, decision: str, existing_note: str, codex_note: str) -> str:
    prefix = f"Human reviewer {reviewer} signed off on Codex expert review."
    parts = [prefix]
    if codex_note.strip():
        parts.append(f"Codex note: {codex_note.strip()}")
    if existing_note.strip():
        parts.append(f"Prior human note: {existing_note.strip()}")
    if decision != "accept" and not codex_note.strip() and not existing_note.strip():
        parts.append("Non-accept decision requires follow-up.")
    return " ".join(parts)


if __name__ == "__main__":
    main()
