from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import read_jsonl, write_jsonl


DEFAULT_BASE_SPLITS = [
    ROOT / "data" / "processed" / "day1_dev.jsonl",
    ROOT / "data" / "processed" / "day1_quick_plus_stale_pool.jsonl",
    ROOT / "data" / "processed" / "stale_fact_pool.jsonl",
]
DEFAULT_CANDIDATE_SPLIT = ROOT / "data" / "candidates" / "emnlp2026_ask_abstain_seed_candidates.jsonl"
DEFAULT_QUEUE = ROOT / "_assets" / "emnlp2026_expansion_candidate_validation_queue.csv"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "emnlp2026_expanded_dev.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "processed" / "emnlp2026_expanded_dev_manifest.json"
VALID_DECISIONS = {"accept", "fix", "reject", "needs_second_pass"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote accepted expansion candidates into an expanded validated split."
    )
    parser.add_argument(
        "--base-split",
        action="append",
        dest="base_splits",
        default=None,
        help="Base JSONL split to include before promoted candidates. Repeatable.",
    )
    parser.add_argument(
        "--candidate-split",
        default=str(DEFAULT_CANDIDATE_SPLIT),
        help="Candidate JSONL file to promote from.",
    )
    parser.add_argument(
        "--queue",
        default=str(DEFAULT_QUEUE),
        help="Human-validation queue CSV containing decisions for the candidate split.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Expanded JSONL output path.")
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST), help="Manifest JSON output path.")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow pending candidate decisions and promote only accepted rows.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_splits = [resolve_path(path) for path in (args.base_splits or DEFAULT_BASE_SPLITS)]
    candidate_split = resolve_path(args.candidate_split)
    queue_path = resolve_path(args.queue)
    output_path = resolve_path(args.output)
    manifest_path = resolve_path(args.manifest_output)

    base_rows, base_duplicate_ids = load_unique_base_rows(base_splits)
    candidate_rows = read_jsonl(candidate_split)
    queue_rows = read_csv(queue_path)
    promotion = select_promoted_candidates(
        candidate_rows,
        queue_rows,
        candidate_split,
        require_complete=not args.allow_incomplete,
    )

    errors = list(promotion["errors"])
    candidate_by_id = {str(row["id"]): row for row in candidate_rows}
    duplicate_promoted_ids = sorted(set(candidate_by_id) & {str(row["id"]) for row in base_rows})
    if duplicate_promoted_ids:
        errors.append(f"candidate ids already exist in base splits: {', '.join(duplicate_promoted_ids)}")
    if not promotion["accepted_ids"]:
        errors.append("no accepted candidate rows to promote")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    promoted_rows = [candidate_by_id[example_id] for example_id in promotion["accepted_ids"]]
    expanded_rows = base_rows + promoted_rows
    write_jsonl(output_path, expanded_rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            build_manifest(
                base_splits=base_splits,
                candidate_split=candidate_split,
                queue_path=queue_path,
                output_path=output_path,
                rows=expanded_rows,
                base_rows=base_rows,
                base_duplicate_ids=base_duplicate_ids,
                promotion=promotion,
            ),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "promoted_expansion_candidates "
        f"accepted={len(promoted_rows)} total={len(expanded_rows)} output={relative_display(output_path)}"
    )


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def relative_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_unique_base_rows(paths: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    for path in paths:
        for row in read_jsonl(path):
            example_id = str(row["id"])
            if example_id in seen:
                duplicates.append(example_id)
                continue
            seen.add(example_id)
            rows.append(row)
    return rows, sorted(set(duplicates))


def select_promoted_candidates(
    candidate_rows: list[dict[str, Any]],
    queue_rows: list[dict[str, str]],
    candidate_split: Path,
    *,
    require_complete: bool,
) -> dict[str, Any]:
    candidate_ids = [str(row["id"]) for row in candidate_rows]
    queue_by_example = {
        row.get("example_id", "").strip(): row
        for row in queue_rows
        if row.get("validation_type", "").strip() == "example_gold_label"
        and same_artifact(row.get("source_artifact", ""), candidate_split)
    }

    accepted_ids: list[str] = []
    skipped_by_decision: Counter[str] = Counter()
    errors: list[str] = []
    for example_id in candidate_ids:
        row = queue_by_example.get(example_id)
        if row is None:
            errors.append(f"candidate {example_id} missing validation queue row")
            continue
        decision = row.get("human_decision", "").strip()
        if not decision:
            if require_complete:
                errors.append(f"candidate {example_id} missing human_decision")
            skipped_by_decision["pending"] += 1
            continue
        if decision not in VALID_DECISIONS:
            errors.append(f"candidate {example_id} invalid human_decision={decision}")
            continue
        if decision == "accept":
            accepted_ids.append(example_id)
        else:
            skipped_by_decision[decision] += 1

    return {
        "accepted_ids": accepted_ids,
        "skipped_by_decision": dict(sorted(skipped_by_decision.items())),
        "errors": errors,
    }


def same_artifact(source_artifact: str, expected_path: Path) -> bool:
    if not source_artifact:
        return False
    source_path = resolve_path(source_artifact)
    return source_path.resolve() == expected_path.resolve()


def build_manifest(
    *,
    base_splits: list[Path],
    candidate_split: Path,
    queue_path: Path,
    output_path: Path,
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    base_duplicate_ids: list[str],
    promotion: dict[str, Any],
) -> dict[str, Any]:
    return {
        "output": relative_display(output_path),
        "base_splits": [relative_display(path) for path in base_splits],
        "candidate_split": relative_display(candidate_split),
        "validation_queue": relative_display(queue_path),
        "num_base_unique": len(base_rows),
        "base_duplicate_ids": base_duplicate_ids,
        "num_promoted_candidates": len(promotion["accepted_ids"]),
        "num_examples": len(rows),
        "by_action": dict(sorted(Counter(str(row.get("gold_action", "unknown")) for row in rows).items())),
        "by_slice": dict(
            sorted(Counter(str(row.get("metadata", {}).get("slice", "unknown")) for row in rows).items())
        ),
        "promoted_candidate_ids": promotion["accepted_ids"],
        "skipped_candidates_by_decision": promotion["skipped_by_decision"],
        "paper_facing": True,
        "promotion_rule": "Only candidate rows with human_decision=accept are promoted.",
    }


if __name__ == "__main__":
    main()
