from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SLICE_DISPLAY = {
    "answerable_control": "Answerable control",
    "false_premise": "False premise",
    "stale_premise": "Stale premise",
    "conflicting_evidence": "Conflicting evidence",
    "ambiguous_intent": "Ambiguous intent",
    "insufficient_evidence": "Insufficient evidence",
}
SLICE_ORDER = [
    "answerable_control",
    "false_premise",
    "stale_premise",
    "conflicting_evidence",
    "ambiguous_intent",
    "insufficient_evidence",
]
ACTION_ORDER = ["answer", "ask", "challenge", "abstain"]
SPLIT_DISPLAY = {
    "emnlp2026_expanded_dev_with_answer_topup": "expanded_canonical_560",
    "day1_dev": "day1_dev_120",
    "day1_quick_plus_stale_pool": "quick_stale_pool_51",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build paper-facing dataset/slice summary tables.")
    parser.add_argument(
        "--split",
        action="append",
        default=[],
        help="JSONL split to summarize. Repeatable.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/day1_dataset_slice_summary.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--output-tex",
        default="experiments/day1/tables/day1_dataset_slice_summary.tex",
        help="LaTeX table output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    splits = args.split or [
        "data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl",
        "data/processed/day1_dev.jsonl",
        "data/processed/day1_quick_plus_stale_pool.jsonl",
    ]
    summaries = [summarize_split(Path(path)) for path in splits]

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(summaries) + "\n", encoding="utf-8")

    output_tex = Path(args.output_tex)
    output_tex.parent.mkdir(parents=True, exist_ok=True)
    output_tex.write_text(render_latex(summaries) + "\n", encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_tex}")


def summarize_split(path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    slice_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()
    action_by_slice: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        slice_name = str(row.get("metadata", {}).get("slice", "unknown"))
        action = str(row.get("gold_action", "unknown"))
        source = str(row.get("source", "unknown"))
        slice_counter[slice_name] += 1
        source_counter[source] += 1
        action_by_slice[slice_name][action] += 1
    return {
        "path": path,
        "total": len(rows),
        "slice_counter": slice_counter,
        "source_counter": source_counter,
        "action_by_slice": action_by_slice,
    }


def render_markdown(summaries: list[dict[str, Any]]) -> str:
    lines = [
        "# Day-1 Dataset Slice Summary",
        "",
        "This table summarizes the active Day-1 splits used by the EMNLP sprint.",
        "",
        "| Split | Total | Slice | Count | Gold Actions | Sources |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    for summary in summaries:
        for slice_name in ordered_slices(summary["slice_counter"]):
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{summary['path'].name}`",
                        str(summary["total"]),
                        display_slice(slice_name),
                        str(summary["slice_counter"][slice_name]),
                        action_summary(summary["action_by_slice"][slice_name]),
                        source_summary_for_slice(summary["path"], slice_name),
                    ]
                )
                + " |"
            )
    return "\n".join(lines)


def render_latex(summaries: list[dict[str, Any]]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{5pt}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llrll}",
        r"\toprule",
        r"Split & Slice & Count & Gold actions & Source \\",
        r"\midrule",
    ]
    for summary in summaries:
        split_name = split_display_name(summary["path"])
        for slice_name in ordered_slices(summary["slice_counter"]):
            lines.append(
                " & ".join(
                    [
                        split_name,
                        latex_escape(display_slice(slice_name)),
                        str(summary["slice_counter"][slice_name]),
                        latex_escape(action_summary(summary["action_by_slice"][slice_name])),
                        latex_escape(source_summary_for_slice(summary["path"], slice_name)),
                    ]
                )
                + r" \\"
            )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            r"\caption{Benchmark split composition by slice, gold action, and source. The canonical paper-facing split is \texttt{emnlp2026\_expanded\_dev\_with\_answer\_topup}; compact splits are retained for diagnostic ablations.}",
            r"\label{tab:day1-dataset-slice-summary}",
            r"\end{table*}",
        ]
    )
    return "\n".join(lines)


def ordered_slices(counter: Counter[str]) -> list[str]:
    ordered = [name for name in SLICE_ORDER if name in counter]
    extras = sorted(name for name in counter if name not in SLICE_ORDER)
    return ordered + extras


def display_slice(slice_name: str) -> str:
    return SLICE_DISPLAY.get(slice_name, slice_name.replace("_", " ").title())


def split_display_name(path: Path) -> str:
    stem = path.name.replace(".jsonl", "")
    display = SPLIT_DISPLAY.get(stem, stem)
    return latex_escape(display)


def action_summary(counter: Counter[str]) -> str:
    pieces = [f"{action}={counter[action]}" for action in ACTION_ORDER if counter[action]]
    extras = [f"{action}={counter[action]}" for action in sorted(counter) if action not in ACTION_ORDER]
    return ", ".join(pieces + extras)


def source_summary_for_slice(path: Path, slice_name: str) -> str:
    counter: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if str(row.get("metadata", {}).get("slice", "unknown")) == slice_name:
            counter[str(row.get("source", "unknown"))] += 1
    return ", ".join(f"{source}={count}" for source, count in sorted(counter.items()))


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


if __name__ == "__main__":
    main()
