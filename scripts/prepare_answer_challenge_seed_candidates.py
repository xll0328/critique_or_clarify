from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


DEFAULT_OUTPUT = ROOT / "data" / "candidates" / "emnlp2026_answer_challenge_seed_candidates.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "candidates" / "emnlp2026_answer_challenge_seed_candidates_manifest.json"

ANSWER_SLICE_COUNTS = {
    "answerable_control": 24,
    "conflicting_evidence": 24,
}
CHALLENGE_COUNTS = {
    "false_premise": 68,
    "stale_premise": 65,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create seed candidate examples for answer/challenge benchmark expansion."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Candidate JSONL output path.")
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST), help="Manifest JSON output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = resolve_path(args.output)
    manifest_path = resolve_path(args.manifest_output)
    rows = build_rows()
    write_jsonl(output_path, rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(build_manifest(rows), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} answer/challenge candidate examples to {output_path}")
    print(f"Wrote manifest to {manifest_path}")


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def build_rows() -> list[dict]:
    rows: list[dict] = []
    rows.extend(build_answerable_rows())
    rows.extend(build_conflicting_answer_rows())
    rows.extend(build_false_challenge_rows())
    rows.extend(build_stale_challenge_rows())
    return rows


def build_answerable_rows() -> list[dict]:
    entities = [
        ("Astera Prize", "2018", "Nina Park"),
        ("Astera Prize", "2020", "Leo Martins"),
        ("Beacon Fellowship", "2019", "Iris Cole"),
        ("Beacon Fellowship", "2021", "Ravi Shah"),
        ("Harbor Cup", "2017", "Team Northwave"),
        ("Harbor Cup", "2022", "Team Crestline"),
        ("Lumen Medal", "2016", "Ada Romero"),
        ("Lumen Medal", "2023", "Evan Cho"),
        ("Novacore Grant", "2020", "Mina Patel"),
        ("Novacore Grant", "2024", "Samir Khan"),
        ("Orchid Award", "2015", "Jade Li"),
        ("Orchid Award", "2022", "Arun Bose"),
        ("Pioneer Grant", "2018", "Elena Cruz"),
        ("Pioneer Grant", "2021", "Noah Reed"),
        ("Quarry Prize", "2019", "Hana Kim"),
        ("Quarry Prize", "2023", "Owen Park"),
    ]
    rows: list[dict] = []
    for index in range(ANSWER_SLICE_COUNTS["answerable_control"]):
        event, year, winner = entities[index % len(entities)]
        prompt = f"According to the passage, who won the {year} {event}?"
        passages = [
            f"Archive note: The {year} {event} winner was {winner}.",
            f"Selection committee report: {winner} received the top score in the final round.",
        ]
        rows.append(
            answer_row(
                row_id=f"answer-control-seed-{index + 1:03d}",
                prompt=prompt,
                passages=passages,
                gold_answer=winner,
                slice_name="answerable_control",
                support_type="single_fact_with_redundant_support",
            )
        )
    return rows


def build_conflicting_answer_rows() -> list[dict]:
    entities = [
        "Orion Transit Line",
        "Summit Charter",
        "Helix Protocol",
        "Rivermark Bridge",
        "Northpoint Charter",
        "Crescent Accord",
        "Bluefield Campus",
        "Silverpine Charter",
        "Atlas Relay",
        "Harbor Registry",
    ]
    rows: list[dict] = []
    for index in range(ANSWER_SLICE_COUNTS["conflicting_evidence"]):
        entity = entities[index % len(entities)]
        year_a = 2012 + (index % 6)
        year_b = year_a + 2
        prompt = f"According to the passages, which opening year for {entity} is better supported?"
        passages = [
            f"Passage A: {entity} opened in {year_a} after a two-year construction period.",
            f"Passage B: Later corrections show {entity} opened in {year_b}, citing official permits.",
            f"Passage C: The historical registry marks {year_b} as the final corrected year for {entity}.",
        ]
        rows.append(
            answer_row(
                row_id=f"answer-conflict-seed-{index + 1:03d}",
                prompt=prompt,
                passages=passages,
                gold_answer=str(year_b),
                slice_name="conflicting_evidence",
                support_type="conflict_but_answerable_with_stronger_evidence",
            )
        )
    return rows


def build_false_challenge_rows() -> list[dict]:
    entities = [
        ("Southbridge Council", "12", "9"),
        ("Northbay Panel", "15", "11"),
        ("HelioWorks Board", "18", "13"),
        ("Cedar Policy Group", "14", "10"),
        ("Metro Transit Board", "16", "12"),
        ("Lakeview Council", "20", "17"),
        ("Summit Education Board", "11", "8"),
        ("Westline Review Panel", "13", "9"),
    ]
    rows: list[dict] = []
    for index in range(CHALLENGE_COUNTS["false_premise"]):
        body, wrong_count, true_count = entities[index % len(entities)]
        prompt = f"The passage says {body} has {wrong_count} voting members. What policy did all of them approve?"
        passages = [
            f"Reference sheet: {body} has {true_count} voting members.",
            f"Meeting record: The approval tally was {true_count}-0 in favor of Policy R.",
        ]
        response = (
            f"The prompt has an incorrect premise: {body} has {true_count} voting members, not {wrong_count}. "
            f"The corrected supported statement is that Policy R passed {true_count}-0."
        )
        rows.append(
            challenge_row(
                row_id=f"challenge-false-seed-{index + 1:03d}",
                prompt=prompt,
                passages=passages,
                gold_response=response,
                slice_name="false_premise",
                challenge_type="numeric_false_premise",
            )
        )
    return rows


def build_stale_challenge_rows() -> list[dict]:
    entities = [
        ("Orion Mobile", "Dana Wu", "Rafael Kim", "2024-03-12"),
        ("Aster Labs", "Ivy Chen", "Marta Doyle", "2023-11-01"),
        ("Northpoint Energy", "Lena Park", "Tomas Vega", "2025-01-20"),
        ("Silverline Transit", "Arun Das", "Mina Holt", "2024-07-04"),
        ("Cobalt Robotics", "Rina Shah", "Leo Pratt", "2023-09-15"),
        ("Helix Media", "Nora King", "Evan Ruiz", "2024-05-09"),
        ("Beacon Health", "Paul Yin", "Jade Soto", "2025-02-03"),
        ("Crescent Data", "Iris Nolan", "Noah Kerr", "2024-08-18"),
    ]
    rows: list[dict] = []
    for index in range(CHALLENGE_COUNTS["stale_premise"]):
        company, old_ceo, new_ceo, change_date = entities[index % len(entities)]
        prompt = f"Confirm that {old_ceo} is still the current CEO of {company}."
        passages = [
            f"Background profile (2019): {old_ceo} served as CEO of {company}.",
            f"Update ({change_date}): {company} announced {new_ceo} as the new CEO.",
        ]
        response = (
            f"The premise is stale. {old_ceo} was a past CEO, but the update shows {new_ceo} "
            f"became CEO on {change_date}."
        )
        rows.append(
            challenge_row(
                row_id=f"challenge-stale-seed-{index + 1:03d}",
                prompt=prompt,
                passages=passages,
                gold_response=response,
                slice_name="stale_premise",
                challenge_type="entity_update_staleness",
                stale_signal=True,
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
            "construction_note": "Seed candidate for answer-action expansion; not paper-facing until validation.",
        },
    }


def challenge_row(
    *,
    row_id: str,
    prompt: str,
    passages: list[str],
    gold_response: str,
    slice_name: str,
    challenge_type: str,
    stale_signal: bool = False,
) -> dict:
    return {
        "id": row_id,
        "source": "synthetic-expansion-candidate",
        "prompt": prompt,
        "passages": passages,
        "gold_action": "challenge",
        "gold_answer": None,
        "gold_response": gold_response,
        "metadata": {
            "slice": slice_name,
            "candidate_status": "needs_human_validation",
            "challenge_type": challenge_type,
            "has_stale_signal": stale_signal,
            "construction_note": "Seed candidate for challenge-action expansion; not paper-facing until validation.",
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
