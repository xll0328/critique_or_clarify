from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from compare_runs import fmt, infer_run_metadata


STOPWORDS = {
    "about",
    "after",
    "bard",
    "brand",
    "business",
    "called",
    "chatbot",
    "changed",
    "company",
    "country",
    "effective",
    "from",
    "known",
    "inc",
    "instead",
    "mlb",
    "name",
    "nfl",
    "now",
    "official",
    "productivity",
    "rice",
    "suite",
    "still",
    "that",
    "team",
    "the",
    "ticker",
    "under",
    "uses",
    "with",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit stale-premise predictions for cases where the model mentions the update but chooses the wrong action."
    )
    parser.add_argument("predictions", nargs="+", help="Prediction JSONL files to audit.")
    parser.add_argument(
        "--data",
        default="data/processed/day1_quick_plus_stale_pool.jsonl",
        help="Dataset JSONL containing stale-premise metadata.",
    )
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_expanded_stale_action_label_audit.md",
        help="Markdown output path.",
    )
    parser.add_argument(
        "--tex-output",
        default="",
        help="Optional LaTeX table output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = {row["id"]: row for row in read_jsonl(Path(args.data))}
    runs = [audit_predictions(Path(path), examples) for path in args.predictions]
    report = render_report(runs)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    if args.tex_output:
        tex_path = Path(args.tex_output)
        tex_path.parent.mkdir(parents=True, exist_ok=True)
        tex_path.write_text(render_latex_table(runs) + "\n", encoding="utf-8")
    print(f"Wrote {output_path} using {len(runs)} run(s).")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def audit_predictions(path: Path, examples: dict[str, dict[str, Any]]) -> dict[str, Any]:
    label = path.stem
    if label.endswith("_reparsed"):
        label = label.removesuffix("_reparsed")
    meta = infer_run_metadata(label)
    rows = read_jsonl(path)
    stale_items: list[dict[str, Any]] = []
    for prediction in rows:
        example = examples.get(prediction.get("example_id", ""))
        if not example:
            continue
        if example.get("metadata", {}).get("slice") != "stale_premise":
            continue
        pred_action = prediction.get("action", "")
        action_correct = pred_action == example.get("gold_action")
        update_mentioned, evidence = mentions_update(prediction, example)
        stale_items.append(
            {
                "id": example["id"],
                "pred_action": pred_action,
                "action_correct": action_correct,
                "update_mentioned": update_mentioned,
                "evidence": evidence,
                "response": prediction_text(prediction),
            }
        )

    wrong_items = [item for item in stale_items if not item["action_correct"]]
    wrong_with_update = [item for item in wrong_items if item["update_mentioned"]]
    answer_with_update = [
        item for item in wrong_with_update if item["pred_action"] == "answer"
    ]
    meta.update(
        {
            "label": label,
            "path": str(path),
            "stale_n": len(stale_items),
            "correct_n": sum(1 for item in stale_items if item["action_correct"]),
            "wrong_n": len(wrong_items),
            "wrong_update_n": len(wrong_with_update),
            "answer_update_n": len(answer_with_update),
            "pred_action_counts": Counter(item["pred_action"] for item in stale_items),
            "examples": wrong_with_update[:3],
        }
    )
    return meta


def mentions_update(prediction: dict[str, Any], example: dict[str, Any]) -> tuple[bool, str]:
    text = normalize(prediction_text(prediction))
    text_terms = set(re.findall(r"\w+", text))
    metadata = example.get("metadata", {})
    candidates = [metadata.get("entity", ""), metadata.get("corrected_fact", "")]

    for candidate in candidates:
        normalized_candidate = normalize(candidate)
        if normalized_candidate and len(normalized_candidate) >= 4 and normalized_candidate in text:
            return True, candidate

    entity_terms = content_terms(str(metadata.get("entity", "")))
    if entity_terms and all(term in text_terms for term in entity_terms):
        return True, " ".join(entity_terms)

    stale_terms = set(content_terms(str(metadata.get("stale_claim", ""))))
    corrected_delta_terms = [
        term
        for term in content_terms(str(metadata.get("corrected_fact", "")))
        if term not in stale_terms
    ]
    if corrected_delta_terms and all(term in text_terms for term in corrected_delta_terms):
        return True, " ".join(corrected_delta_terms)
    return False, ""


def content_terms(text: str) -> list[str]:
    raw_terms = re.findall(r"\w+", normalize(text))
    terms = []
    for term in raw_terms:
        if len(term) < 3:
            continue
        if term in STOPWORDS:
            continue
        if term not in terms:
            terms.append(term)
    return terms


def prediction_text(prediction: dict[str, Any]) -> str:
    return " ".join(
        str(prediction.get(field, "")) for field in ("response", "raw_output") if prediction.get(field)
    )


def normalize(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))


def render_report(runs: list[dict[str, Any]]) -> str:
    lines = [
        "# Expanded Stale-Premise Action-Label Audit",
        "",
        "This audit uses a conservative string heuristic over each stale example's corrected entity/fact metadata. It asks whether a wrong-action prediction still mentions the update, which indicates an action-label failure rather than a pure factual-retrieval failure.",
        "",
        "## Summary",
        "",
        "| Model | Style | Stale N | Correct Challenge | Wrong Action | Wrong + Update Mention | Answer + Update Mention | Pred Actions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for run in runs:
        wrong_n = run["wrong_n"]
        wrong_update = run["wrong_update_n"]
        lines.append(
            "| "
            + " | ".join(
                [
                    run["model"],
                    run["style"],
                    str(run["stale_n"]),
                    f"{run['correct_n']} ({rate(run['correct_n'], run['stale_n'])})",
                    str(wrong_n),
                    f"{wrong_update} ({rate(wrong_update, wrong_n)})",
                    str(run["answer_update_n"]),
                    format_counter(run["pred_action_counts"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Representative Wrong-Action Update Mentions", ""])
    for run in runs:
        lines.append(f"### {run['model']}")
        if not run["examples"]:
            lines.append("- No wrong-action stale predictions matched the corrected entity/fact heuristic.")
            continue
        for item in run["examples"]:
            lines.append(
                f"- `{item['id']}` predicted `{item['pred_action']}` while mentioning `{item['evidence']}`: {shorten(item['response'])}"
            )
    return "\n".join(lines).rstrip()


def render_latex_table(runs: list[dict[str, Any]]) -> str:
    rows = []
    for run in runs:
        rows.append(
            " & ".join(
                [
                    latex_escape(run["model"]),
                    latex_escape(run["style"]),
                    latex_escape(count_with_rate(run["correct_n"], run["stale_n"])),
                    latex_escape(count_with_rate(run["wrong_update_n"], run["wrong_n"])),
                    str(run["answer_update_n"]),
                    latex_escape(format_counter(run["pred_action_counts"])),
                ]
            )
            + r" \\"
        )
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{3.6pt}",
        r"\begin{tabular}{llcccl}",
        r"\toprule",
        r"Model & Style & Correct Challenge & Wrong+Update/Wrong & Answer+Update & Pred Actions \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Expanded stale-premise action-label audit. Wrong+Update counts wrong-action stale predictions that still mention the corrected entity or update, separating action-selection failures from pure update retrieval misses.}",
        r"\label{tab:day1-expanded-stale-action-label-audit}",
        r"\end{table*}",
    ]
    return "\n".join(lines)


def rate(count: int, total: int) -> str:
    if total <= 0:
        return "-"
    return fmt(count / total)


def count_with_rate(count: int, total: int) -> str:
    return f"{count}/{total} ({rate(count, total)})"


def format_counter(counter: Counter[str]) -> str:
    return ", ".join(f"{key}:{counter[key]}" for key in sorted(counter))


def latex_escape(text: str) -> str:
    return (
        str(text)
        .replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def shorten(text: str, limit: int = 180) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


if __name__ == "__main__":
    main()
