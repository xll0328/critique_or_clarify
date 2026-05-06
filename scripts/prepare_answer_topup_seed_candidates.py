from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


DEFAULT_OUTPUT = ROOT / "data" / "candidates" / "emnlp2026_answer_topup_seed_candidates.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "candidates" / "emnlp2026_answer_topup_seed_candidates_manifest.json"

COUNTS = {
    "answerable_control": 30,
    "conflicting_evidence": 30,
}
DEFAULT_ID_PREFIX = "answer-topup"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create top-up seed candidates for answer-action coverage expansion."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Candidate JSONL output path.")
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST), help="Manifest JSON output path.")
    parser.add_argument(
        "--answerable-control-count",
        type=int,
        default=COUNTS["answerable_control"],
        help="Number of answerable_control candidates to emit.",
    )
    parser.add_argument(
        "--conflicting-evidence-count",
        type=int,
        default=COUNTS["conflicting_evidence"],
        help="Number of conflicting_evidence candidates to emit.",
    )
    parser.add_argument(
        "--answerable-start-index",
        type=int,
        default=1,
        help="1-based index start for answerable_control row ids.",
    )
    parser.add_argument(
        "--conflicting-start-index",
        type=int,
        default=1,
        help="1-based index start for conflicting_evidence row ids.",
    )
    parser.add_argument(
        "--id-prefix",
        default=DEFAULT_ID_PREFIX,
        help="Row id prefix for generated candidates.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = resolve_path(args.output)
    manifest_path = resolve_path(args.manifest_output)
    validate_args(args)
    rows = build_rows(
        answerable_control_count=args.answerable_control_count,
        conflicting_evidence_count=args.conflicting_evidence_count,
        answerable_start_index=args.answerable_start_index,
        conflicting_start_index=args.conflicting_start_index,
        id_prefix=args.id_prefix,
    )
    write_jsonl(output_path, rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(build_manifest(rows), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} answer top-up candidate examples to {output_path}")
    print(f"Wrote manifest to {manifest_path}")


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def validate_args(args: argparse.Namespace) -> None:
    if args.answerable_control_count < 0:
        raise SystemExit("--answerable-control-count must be >= 0")
    if args.conflicting_evidence_count < 0:
        raise SystemExit("--conflicting-evidence-count must be >= 0")
    if args.answerable_start_index < 1:
        raise SystemExit("--answerable-start-index must be >= 1")
    if args.conflicting_start_index < 1:
        raise SystemExit("--conflicting-start-index must be >= 1")


def build_rows(
    *,
    answerable_control_count: int,
    conflicting_evidence_count: int,
    answerable_start_index: int,
    conflicting_start_index: int,
    id_prefix: str,
) -> list[dict]:
    return build_answerable_rows(
        count=answerable_control_count,
        start_index=answerable_start_index,
        id_prefix=id_prefix,
    ) + build_conflicting_rows(
        count=conflicting_evidence_count,
        start_index=conflicting_start_index,
        id_prefix=id_prefix,
    )


def build_answerable_rows(*, count: int, start_index: int, id_prefix: str) -> list[dict]:
    entities = [
        ("Meridian Prize", "2018", "Lina Zhao"),
        ("Meridian Prize", "2021", "Omar Nabil"),
        ("Coastal Fellowship", "2019", "Priya Iyer"),
        ("Coastal Fellowship", "2022", "Ethan Wu"),
        ("Aurora Award", "2017", "Marta Lin"),
        ("Aurora Award", "2024", "Kenji Sato"),
        ("Northlight Grant", "2020", "Rae Morgan"),
        ("Northlight Grant", "2023", "Diego Park"),
        ("Summit Medal", "2016", "Hyejin Choi"),
        ("Summit Medal", "2025", "Noel Rivera"),
    ]
    rows: list[dict] = []
    for offset in range(count):
        index = start_index - 1 + offset
        event, year, winner = entities[index % len(entities)]
        rows.append(
            answer_row(
                row_id=f"{id_prefix}-control-{index + 1:03d}",
                prompt=f"According to the passage, who won the {year} {event}?",
                passages=[
                    f"Official bulletin: {winner} won the {year} {event}.",
                    f"Committee minutes: The winner for {year} {event} was {winner}.",
                ],
                gold_answer=winner,
                slice_name="answerable_control",
                support_type="single_fact_redundant_confirmation",
            )
        )
    return rows


def build_conflicting_rows(*, count: int, start_index: int, id_prefix: str) -> list[dict]:
    entities = [
        "Cedar Transit Plan",
        "Harbor Safety Code",
        "Nova Charter",
        "Delta Bridge Project",
        "Riverton Policy Draft",
        "Lumen Rail Program",
        "Northport Bylaw",
        "Silverfield Contract",
        "Atlas Deployment",
        "Helix Registry",
    ]
    rows: list[dict] = []
    for offset in range(count):
        index = start_index - 1 + offset
        entity = entities[index % len(entities)]
        weak_year = 2011 + (index % 7)
        strong_year = weak_year + 3
        rows.append(
            answer_row(
                row_id=f"{id_prefix}-conflict-{index + 1:03d}",
                prompt=f"According to the passages, what year for {entity} is better supported?",
                passages=[
                    f"Early draft: {entity} was listed under year {weak_year}.",
                    f"Corrected notice: {entity} was finalized in {strong_year}.",
                    f"Registry errata: the corrected year for {entity} is {strong_year}.",
                ],
                gold_answer=str(strong_year),
                slice_name="conflicting_evidence",
                support_type="conflict_with_corrected_preferred_evidence",
            )
        )
    return rows


def answer_row(
    *,
    row_id: str,
    prompt: str,
    passages: list[str],
    gold_answer: str,
    slice_name: str,
    support_type: str,
) -> dict:
    return {
        "id": row_id,
        "source": "synthetic-expansion-candidate",
        "prompt": prompt,
        "passages": passages,
        "gold_action": "answer",
        "gold_answer": gold_answer,
        "gold_response": None,
        "metadata": {
            "slice": slice_name,
            "candidate_status": "needs_human_validation",
            "support_type": support_type,
            "construction_note": "Seed candidate for answer top-up expansion; not paper-facing until validation.",
        },
    }


def build_manifest(rows: list[dict]) -> dict:
    return {
        "num_examples": len(rows),
        "candidate_status": "needs_human_validation",
        "by_action": dict(sorted(Counter(row["gold_action"] for row in rows).items())),
        "by_slice": dict(sorted(Counter(row["metadata"]["slice"] for row in rows).items())),
        "by_source": dict(sorted(Counter(row["source"] for row in rows).items())),
        "paper_facing": False,
        "next_step": "Review candidates and promote accepted rows into an expanded validated split.",
    }


if __name__ == "__main__":
    main()
