from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QWENPLUS_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_QWENPLUS_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_QWENPLUS_CANONICAL_GUARDED = (
    ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json"
)
DEFAULT_QWENPLUS_FULL_GUARDED = (
    ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_full_answer_topup_decision_first_guarded_metrics.json"
)
DEFAULT_GPT41_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_GPT41_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_gpt41mini_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_QWENTURBO_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_QWENTURBO_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenturbo_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_GPT5CHAT_CANONICAL_MAIN = (
    ROOT / "outputs" / "day1" / "aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json"
)
DEFAULT_GPT5CHAT_FULL_MAIN = (
    ROOT / "outputs" / "day1" / "aihubmix_gpt5chatlatest_day1_expanded_dev_with_full_answer_topup_metrics.json"
)
DEFAULT_OUTPUT = ROOT / "experiments" / "day1" / "tables" / "day1_full_split_sensitivity.tex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a compact canonical-vs-full split delta table for stress sensitivity."
    )
    parser.add_argument("--qwenplus-canonical-main", default=str(DEFAULT_QWENPLUS_CANONICAL_MAIN))
    parser.add_argument("--qwenplus-full-main", default=str(DEFAULT_QWENPLUS_FULL_MAIN))
    parser.add_argument("--qwenplus-canonical-guarded", default=str(DEFAULT_QWENPLUS_CANONICAL_GUARDED))
    parser.add_argument("--qwenplus-full-guarded", default=str(DEFAULT_QWENPLUS_FULL_GUARDED))
    parser.add_argument("--gpt41-canonical-main", default=str(DEFAULT_GPT41_CANONICAL_MAIN))
    parser.add_argument("--gpt41-full-main", default=str(DEFAULT_GPT41_FULL_MAIN))
    parser.add_argument("--qwenturbo-canonical-main", default=str(DEFAULT_QWENTURBO_CANONICAL_MAIN))
    parser.add_argument("--qwenturbo-full-main", default=str(DEFAULT_QWENTURBO_FULL_MAIN))
    parser.add_argument("--gpt5chat-canonical-main", default=str(DEFAULT_GPT5CHAT_CANONICAL_MAIN))
    parser.add_argument("--gpt5chat-full-main", default=str(DEFAULT_GPT5CHAT_FULL_MAIN))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--samples", type=int, default=2000, help="Bootstrap resamples for delta intervals.")
    parser.add_argument("--seed", type=int, default=0, help="Base random seed for deterministic intervals.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        (
            "qwen-plus-latest / decision-first",
            load_payload(Path(args.qwenplus_canonical_main)),
            load_payload(Path(args.qwenplus_full_main)),
        ),
        (
            "qwen-plus-latest / guarded",
            load_payload(Path(args.qwenplus_canonical_guarded)),
            load_payload(Path(args.qwenplus_full_guarded)),
        ),
        (
            "gpt-4.1-mini / decision-first",
            load_payload(Path(args.gpt41_canonical_main)),
            load_payload(Path(args.gpt41_full_main)),
        ),
        (
            "qwen-turbo / decision-first",
            load_payload(Path(args.qwenturbo_canonical_main)),
            load_payload(Path(args.qwenturbo_full_main)),
        ),
    ]
    gpt5chat_canonical = Path(args.gpt5chat_canonical_main)
    gpt5chat_full = Path(args.gpt5chat_full_main)
    if gpt5chat_canonical.exists() and gpt5chat_full.exists():
        rows.append(
            (
                "gpt-5-chat-latest / decision-first",
                load_payload(gpt5chat_canonical),
                load_payload(gpt5chat_full),
            )
        )

    table = render_table(rows, samples=args.samples, seed=args.seed)
    output_path.write_text(table, encoding="utf-8")
    print(f"Wrote {output_path}")


def load_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        raise ValueError(f"Malformed metrics payload: {path}")
    details = payload.get("details", [])
    if not isinstance(details, list):
        raise ValueError(f"Malformed metrics details: {path}")
    return {"summary": summary, "details": details}


def format_float(value: float) -> str:
    return f"{value:.4f}"


def delta(full: dict, canonical: dict, key: str) -> float:
    return float(full.get(key, 0.0)) - float(canonical.get(key, 0.0))


def metric_values(details: list[dict], key: str) -> list[float]:
    if key == "action_accuracy":
        return [1.0 if detail.get("action_correct") else 0.0 for detail in details]
    if key == "avg_utility":
        return [float(detail.get("utility", 0.0)) for detail in details]
    raise ValueError(f"Unsupported bootstrap metric: {key}")


def bootstrap_delta(
    *,
    full_values: list[float],
    canonical_values: list[float],
    samples: int,
    seed: int,
) -> dict[str, float]:
    if not full_values or not canonical_values:
        raise ValueError("Cannot bootstrap delta from empty values.")
    point = (sum(full_values) / len(full_values)) - (sum(canonical_values) / len(canonical_values))
    if samples <= 0:
        return {"point": point, "low": point, "high": point}

    rng = random.Random(seed)
    full_n = len(full_values)
    canonical_n = len(canonical_values)
    estimates: list[float] = []
    for _ in range(samples):
        full_total = 0.0
        canonical_total = 0.0
        for _ in range(full_n):
            full_total += full_values[rng.randrange(full_n)]
        for _ in range(canonical_n):
            canonical_total += canonical_values[rng.randrange(canonical_n)]
        estimates.append((full_total / full_n) - (canonical_total / canonical_n))
    estimates.sort()
    return {
        "point": point,
        "low": percentile(estimates, 0.025),
        "high": percentile(estimates, 0.975),
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("Cannot compute a percentile from an empty list.")
    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def format_interval(interval: dict[str, float]) -> str:
    return f"{format_float(interval['point'])} [{format_float(interval['low'])}, {format_float(interval['high'])}]"


def render_table(rows: list[tuple[str, dict, dict]], *, samples: int, seed: int) -> str:
    body: list[str] = []
    for row_index, (setting_name, canonical_payload, full_payload) in enumerate(rows):
        canonical = canonical_payload["summary"]
        full = full_payload["summary"]
        action_interval = bootstrap_delta(
            full_values=metric_values(full_payload["details"], "action_accuracy"),
            canonical_values=metric_values(canonical_payload["details"], "action_accuracy"),
            samples=samples,
            seed=seed + 1000 * row_index + 1,
        )
        action_interval["point"] = delta(full, canonical, "action_accuracy")
        utility_interval = bootstrap_delta(
            full_values=metric_values(full_payload["details"], "avg_utility"),
            canonical_values=metric_values(canonical_payload["details"], "avg_utility"),
            samples=samples,
            seed=seed + 1000 * row_index + 2,
        )
        utility_interval["point"] = delta(full, canonical, "avg_utility")
        body.append(
            " & ".join(
                [
                    setting_name.replace("_", r"\_"),
                    format_interval(action_interval),
                    format_interval(utility_interval),
                    format_float(delta(full, canonical, "over_answer_rate")),
                    format_float(delta(full, canonical, "json_parse_rate")),
                ]
            )
            + r" \\"
        )
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Setting & $\Delta$ Action Acc. (95\% CI) & $\Delta$ Utility (95\% CI) & $\Delta$ Over-answer & $\Delta$ JSON Parse \\",
        r"\midrule",
        *body,
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{Stress sensitivity from canonical 560 to slice-balanced 600, not a replacement headline benchmark, under fixed decoding settings (\texttt{max\_tokens}=64, temperature=0). Values are $\Delta$ (full minus canonical); action-accuracy and utility columns include bootstrap 95\% percentile intervals.}",
        r"\label{tab:day1-full-split-sensitivity}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
