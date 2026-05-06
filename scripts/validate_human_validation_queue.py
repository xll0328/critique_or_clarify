from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


VALID_DECISIONS = {"accept", "fix", "reject", "needs_second_pass"}
DECISIONS_REQUIRING_NOTES = {"fix", "reject", "needs_second_pass"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate label hygiene for the human-validation work queue."
    )
    parser.add_argument(
        "--queue",
        default="_assets/human_validation_work_queue.csv",
        help="Human-validation queue CSV path.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Fail if any row is missing human_decision.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(Path(args.queue))
    errors = validate_rows(rows, require_complete=args.require_complete)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)
    completed = sum(1 for row in rows if row.get("human_decision", "").strip())
    print(f"human_validation_queue_ok completed={completed}/{len(rows)}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_rows(rows: list[dict[str, str]], *, require_complete: bool = False) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        queue_id = row.get("queue_id", "").strip()
        if not queue_id:
            errors.append(f"row={row_number} missing queue_id")
            continue
        if queue_id in seen_ids:
            errors.append(f"row={row_number} queue_id={queue_id} duplicate queue_id")
        seen_ids.add(queue_id)

        decision = row.get("human_decision", "").strip()
        notes = row.get("human_notes", "").strip()
        if require_complete and not decision:
            errors.append(f"row={row_number} queue_id={queue_id} missing human_decision")
            continue
        if not decision:
            continue
        if decision not in VALID_DECISIONS:
            errors.append(f"row={row_number} queue_id={queue_id} invalid human_decision={decision}")
            continue
        if decision in DECISIONS_REQUIRING_NOTES and not notes:
            errors.append(f"row={row_number} queue_id={queue_id} decision={decision} requires human_notes")
    return errors


if __name__ == "__main__":
    main()
