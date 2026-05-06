from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import load_examples, read_jsonl
from coc.schema import Prediction

from compare_runs import action_precision, fmt, load_run


BUCKET_DEFINITIONS = [
    (
        "answerable_non_answer",
        "Answerable -> non-answer",
        lambda detail: detail["slice"] == "answerable_control" and detail["pred_action"] != "answer",
    ),
    (
        "answerable_wrong_answer",
        "Answerable -> wrong answer",
        lambda detail: detail["slice"] == "answerable_control"
        and detail["pred_action"] == "answer"
        and detail.get("answer_exact_match") is False,
    ),
    (
        "false_premise_answered",
        "False premise -> answered",
        lambda detail: detail["slice"] == "false_premise" and detail["pred_action"] == "answer",
    ),
    (
        "false_premise_retreat",
        "False premise -> abstain/ask",
        lambda detail: detail["slice"] == "false_premise" and detail["pred_action"] in {"abstain", "ask"},
    ),
    (
        "stale_premise_answered",
        "Stale premise -> answered",
        lambda detail: detail["slice"] == "stale_premise" and detail["pred_action"] == "answer",
    ),
    (
        "stale_premise_retreat",
        "Stale premise -> abstain/ask",
        lambda detail: detail["slice"] == "stale_premise" and detail["pred_action"] in {"abstain", "ask"},
    ),
    (
        "conflict_answer_miss",
        "Conflict -> answer miss",
        lambda detail: detail["slice"] == "conflicting_evidence"
        and detail["pred_action"] == "answer"
        and detail.get("answer_contains_match") is False,
    ),
]

PROMPT_BOILERPLATE_MARKERS = [
    "i am a beginner in mathematics",
    "i will provide you with",
    "please answer the questions in english",
]
RESPONSE_THINKING_MARKERS = [
    "okay,",
    "okay so",
    "i need to",
    "i should",
    "let me think",
    "首先，",
    "好的，",
    "我需要",
    "我现在需要",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a paper-facing qualitative error-bucket audit for the current day-1 comparison."
    )
    parser.add_argument("metric_paths", nargs="+", help="Metric JSON files in the current comparison.")
    parser.add_argument("--data", default="data/processed/day1_dev.jsonl", help="Gold data JSONL.")
    parser.add_argument(
        "--title",
        default="Day-1 Error Bucket Audit",
        help="Markdown title for the emitted audit.",
    )
    parser.add_argument(
        "--intro",
        default="This audit condenses the current dev-scale comparison into a few failure buckets that are directly useful for the paper narrative.",
        help="Introductory sentence shown under the title.",
    )
    parser.add_argument(
        "--output",
        default="experiments/day1/day1_error_bucket_audit.md",
        help="Markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = [build_run_payload(Path(raw_path), Path(args.data)) for raw_path in args.metric_paths]
    report = render_report(runs, title=args.title, intro=args.intro)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")
    print(report)


def build_run_payload(metric_path: Path, data_path: Path) -> dict[str, Any]:
    run = load_run(metric_path)
    payload = json.loads(metric_path.read_text(encoding="utf-8"))
    details = payload["details"]
    detail_by_id = {detail["id"]: detail for detail in details}
    prediction_path = infer_prediction_path(metric_path)
    predictions = {
        prediction.example_id: prediction
        for prediction in (Prediction.from_dict(row) for row in read_jsonl(prediction_path))
    }
    examples = {example.id: example for example in load_examples(data_path)}
    run["metric_path"] = str(metric_path)
    run["prediction_path"] = str(prediction_path)
    run["details"] = details
    run["detail_by_id"] = detail_by_id
    run["predictions"] = predictions
    run["examples"] = examples
    run["bucket_counts"] = bucket_counts(details)
    run["bucket_examples"] = bucket_examples(run)
    return run


def infer_prediction_path(metric_path: Path) -> Path:
    if not metric_path.name.endswith("_metrics.json"):
        raise ValueError(f"Unexpected metric filename: {metric_path}")
    prediction_path = metric_path.with_name(metric_path.name.replace("_metrics.json", ".jsonl"))
    if not prediction_path.exists():
        raise FileNotFoundError(f"Missing prediction file for {metric_path}: {prediction_path}")
    return prediction_path


def bucket_counts(details: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for bucket_key, _, predicate in BUCKET_DEFINITIONS:
        counts[bucket_key] = sum(1 for detail in details if predicate(detail))
    return counts


def bucket_examples(run: dict[str, Any]) -> dict[str, dict[str, Any] | None]:
    picked: dict[str, dict[str, Any] | None] = {}
    for bucket_key, _, predicate in BUCKET_DEFINITIONS:
        candidates = [detail for detail in run["details"] if predicate(detail)]
        match = max(
            candidates,
            key=lambda detail: (example_score(run, detail), str(detail["id"])),
            default=None,
        )
        if match is None:
            picked[bucket_key] = None
            continue
        example = run["examples"][match["id"]]
        prediction = run["predictions"][match["id"]]
        picked[bucket_key] = {
            "id": match["id"],
            "source": match["source"],
            "slice": match["slice"],
            "gold_action": match["gold_action"],
            "pred_action": match["pred_action"],
            "parsed_as": match["parsed_as"],
            "prompt": compact_text(example.prompt, 180),
            "response": compact_text(prediction.response or prediction.raw_output, 220),
        }
    return picked


def example_score(run: dict[str, Any], detail: dict[str, Any]) -> float:
    example = run["examples"][detail["id"]]
    prediction = run["predictions"][detail["id"]]
    prompt = normalize_text(example.prompt)
    response = normalize_text(prediction.response or prediction.raw_output)
    prompt_lower = prompt.lower()
    response_lower = response.lower()
    prompt_overflow = max(0, len(prompt) - 180)
    response_overflow = max(0, len(response) - 220)
    boilerplate_hits = sum(marker in prompt_lower for marker in PROMPT_BOILERPLATE_MARKERS)
    thinking_hits = sum(marker in response_lower for marker in RESPONSE_THINKING_MARKERS)
    structured_noise = prompt.count("\\") + response.count("\\") + response.count("{") + response.count("}")
    score = 0.0
    if detail["source"] != "pcbench":
        score += 1.0
    if prediction.metadata.get("parsed_as") != "fallback":
        score += 0.5
    score -= 2.5 * boilerplate_hits
    score -= 1.5 * thinking_hits
    score -= prompt_overflow / 40.0
    score -= response_overflow / 40.0
    score -= abs(len(prompt) - 90) / 200.0
    score -= abs(len(response) - 120) / 220.0
    score -= structured_noise / 10.0
    return score


def render_report(runs: list[dict[str, Any]], *, title: str, intro: str) -> str:
    lines = [
        f"# {title}",
        "",
        intro,
        "",
        "## Cross-Run Takeaways",
        "",
    ]
    lines.extend(render_cross_run_takeaways(runs))
    for run in runs:
        lines.extend(["", f"## {run['model']}", ""])
        lines.extend(render_run_section(run))
    return "\n".join(lines).rstrip()


def render_cross_run_takeaways(runs: list[dict[str, Any]]) -> list[str]:
    strongest = max(runs, key=lambda run: run["summary"]["action_accuracy"])
    lowest_overanswer = min(runs, key=lambda run: run["summary"]["over_answer_rate"])
    lowest_parse = min(runs, key=lambda run: run["summary"].get("json_parse_rate", 0.0))
    lines = [
        f"- The strongest current snapshot model is `{strongest['model']}`: `action_accuracy={fmt(strongest['summary']['action_accuracy'])}`, `avg_utility={fmt(strongest['summary']['avg_utility'])}`.",
        f"- The safest current snapshot model by over-answer rate is `{lowest_overanswer['model']}`: `over_answer_rate={fmt(lowest_overanswer['summary']['over_answer_rate'])}`.",
        f"- The largest formatting bottleneck is still `{lowest_parse['model']}`: `json_parse_rate={fmt(lowest_parse['summary'].get('json_parse_rate', 0.0))}`.",
    ]
    return lines


def render_run_section(run: dict[str, Any]) -> list[str]:
    summary = run["summary"]
    fallback_count = sum(
        1 for prediction in run["predictions"].values() if prediction.metadata.get("parsed_as") == "fallback"
    )
    total_predictions = len(run["predictions"])
    lines = [
        f"- Snapshot: `action_accuracy={fmt(summary['action_accuracy'])}`, `avg_utility={fmt(summary['avg_utility'])}`, `over_answer_rate={fmt(summary['over_answer_rate'])}`, `challenge_precision={fmt(action_precision(summary, 'challenge'))}`.",
        f"- Format path: `fallback={fallback_count}/{total_predictions}`, `json_parse_rate={fmt(summary.get('json_parse_rate', 0.0))}`.",
        "- Dominant buckets:",
    ]
    for bucket_key, label, _ in sorted(
        BUCKET_DEFINITIONS,
        key=lambda item: run["bucket_counts"][item[0]],
        reverse=True,
    ):
        count = run["bucket_counts"][bucket_key]
        if count == 0:
            continue
        example = run["bucket_examples"][bucket_key]
        example_suffix = ""
        if example is not None:
            example_suffix = (
                f" Example `{example['id']}`: prompt `{example['prompt']}`; response `{example['response']}`."
            )
        lines.append(f"  - `{label}`: `{count}`.{example_suffix}")
    return lines


def compact_text(text: str, max_chars: int) -> str:
    squashed = normalize_text(text)
    if len(squashed) <= max_chars:
        return squashed
    return squashed[: max_chars - 3] + "..."


def normalize_text(text: str) -> str:
    return " ".join(text.split())


if __name__ == "__main__":
    main()
