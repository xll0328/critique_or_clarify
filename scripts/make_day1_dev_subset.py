from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a stratified day-1 development subset.")
    parser.add_argument(
        "--qacc",
        default="data/processed/qacc_dev.jsonl",
        help="Path to processed QACC JSONL.",
    )
    parser.add_argument(
        "--pcbench-paired",
        default="data/processed/pcbench_paired.jsonl",
        help="Path to processed PCBench paired JSONL.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/day1_dev.jsonl",
        help="Output combined JSONL.",
    )
    parser.add_argument(
        "--manifest",
        default="data/processed/day1_dev_manifest.json",
        help="Output manifest JSON.",
    )
    parser.add_argument("--qacc-size", type=int, default=40)
    parser.add_argument("--pcbench-pairs", type=int, default=40)
    parser.add_argument(
        "--stale",
        default="data/processed/stale_fact_seed.jsonl",
        help="Optional processed stale-premise JSONL.",
    )
    parser.add_argument(
        "--stale-size",
        type=int,
        default=0,
        help="How many stale-premise seed examples to include. Defaults to 0 to preserve the original day1 split.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    qacc_rows = read_jsonl(resolve_path(args.qacc))
    pcbench_rows = read_jsonl(resolve_path(args.pcbench_paired))
    stale_rows = read_jsonl(resolve_path(args.stale)) if args.stale_size > 0 else []

    qacc_sample = sample_qacc(qacc_rows, args.qacc_size, rng)
    pcbench_sample = sample_pcbench_pairs(pcbench_rows, args.pcbench_pairs, rng)
    stale_sample = sample_stale(stale_rows, args.stale_size, rng)

    combined = qacc_sample + pcbench_sample + stale_sample
    rng.shuffle(combined)

    output_path = resolve_path(args.output)
    manifest_path = resolve_path(args.manifest)
    write_jsonl(output_path, combined)

    manifest = build_manifest(combined, args.seed)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(combined)} examples to {output_path}")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else ROOT / path


def sample_qacc(rows: list[dict], sample_size: int, rng: random.Random) -> list[dict]:
    filtered = []
    for row in rows:
        if row.get("gold_action") != "answer":
            continue
        copied = dict(row)
        metadata = dict(copied.get("metadata", {}))
        metadata.setdefault("slice", "conflicting_evidence")
        copied["metadata"] = metadata
        filtered.append(copied)
    return rng.sample(filtered, min(sample_size, len(filtered)))


def sample_pcbench_pairs(rows: list[dict], pair_count: int, rng: random.Random) -> list[dict]:
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        metadata = row.get("metadata", {})
        pair_id = str(metadata.get("paired_group_id", row.get("id", "")))
        grouped[pair_id][row.get("gold_action", "")] = row

    strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    for pair_id, pair_rows in grouped.items():
        challenge_row = pair_rows.get("challenge")
        answer_row = pair_rows.get("answer")
        if not challenge_row or not answer_row:
            continue
        metadata = challenge_row.get("metadata", {})
        key = (
            str(metadata.get("difficulty", "unknown")),
            str(metadata.get("conflict_type", "unknown")),
        )
        strata[key].append(pair_id)

    selected_pair_ids = stratified_pair_sample(strata, pair_count, rng)

    selected_rows: list[dict] = []
    for pair_id in selected_pair_ids:
        pair_rows = grouped[pair_id]
        selected_rows.append(pair_rows["answer"])
        selected_rows.append(pair_rows["challenge"])
    return selected_rows


def sample_stale(rows: list[dict], sample_size: int, rng: random.Random) -> list[dict]:
    if sample_size <= 0:
        return []

    normalized: list[dict] = []
    for row in rows:
        copied = dict(row)
        metadata = dict(copied.get("metadata", {}))
        metadata.setdefault("slice", "stale_premise")
        metadata.setdefault("has_stale_premise", True)
        copied["metadata"] = metadata
        normalized.append(copied)
    return rng.sample(normalized, min(sample_size, len(normalized)))


def stratified_pair_sample(
    strata: dict[tuple[str, str], list[str]],
    pair_count: int,
    rng: random.Random,
) -> list[str]:
    all_pairs = sum(len(pair_ids) for pair_ids in strata.values())
    if pair_count >= all_pairs:
        return [pair_id for pair_ids in strata.values() for pair_id in pair_ids]

    shuffled = {key: rng.sample(pair_ids, len(pair_ids)) for key, pair_ids in strata.items()}
    selected: list[str] = []
    ordered_keys = sorted(shuffled.keys())

    while len(selected) < pair_count:
        progress = False
        for key in ordered_keys:
            bucket = shuffled[key]
            if not bucket:
                continue
            selected.append(bucket.pop())
            progress = True
            if len(selected) >= pair_count:
                break
        if not progress:
            break
    return selected


def build_manifest(rows: list[dict], seed: int) -> dict:
    by_source: dict[str, int] = defaultdict(int)
    by_slice: dict[str, int] = defaultdict(int)
    by_action: dict[str, int] = defaultdict(int)
    by_difficulty: dict[str, int] = defaultdict(int)
    by_conflict: dict[str, int] = defaultdict(int)

    for row in rows:
        metadata = row.get("metadata", {})
        by_source[str(row.get("source", "unknown"))] += 1
        by_slice[str(metadata.get("slice", "unknown"))] += 1
        by_action[str(row.get("gold_action", "unknown"))] += 1
        difficulty = metadata.get("difficulty")
        conflict = metadata.get("conflict_type")
        if difficulty:
            by_difficulty[str(difficulty)] += 1
        if conflict:
            by_conflict[str(conflict)] += 1

    return {
        "seed": seed,
        "num_examples": len(rows),
        "by_source": dict(by_source),
        "by_slice": dict(by_slice),
        "by_action": dict(by_action),
        "by_difficulty": dict(by_difficulty),
        "by_conflict_type": dict(by_conflict),
    }


if __name__ == "__main__":
    main()
