from __future__ import annotations

import re
from collections import Counter
from typing import Any

from coc.schema import Action, Example, Prediction


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def exact_match(prediction: str, gold: str) -> bool:
    return normalize_text(prediction) == normalize_text(gold)


def contains_match(prediction: str, gold: str) -> bool:
    pred = normalize_text(prediction)
    target = normalize_text(gold)
    if not pred or not target:
        return False
    if pred == target:
        return True
    pred_tokens = pred.split()
    target_tokens = target.split()
    return _contains_token_subsequence(pred_tokens, target_tokens) or _contains_token_subsequence(
        target_tokens,
        pred_tokens,
    )


def evaluate_predictions(
    examples: list[Example],
    predictions: list[Prediction],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    prediction_map = {prediction.example_id: prediction for prediction in predictions}
    details: list[dict[str, Any]] = []

    action_correct = 0
    answer_total = 0
    answer_exact = 0
    answer_contains = 0
    utility_total = 0.0
    predicted_action_counts: Counter[str] = Counter()
    gold_action_counts: Counter[str] = Counter()
    parsed_as_counts: Counter[str] = Counter()
    confusion: dict[str, Counter[str]] = {
        action.value: Counter() for action in Action
    }
    slice_stats: dict[str, dict[str, float | int]] = {}
    over_answer_count = 0

    for example in examples:
        prediction = prediction_map.get(
            example.id,
            Prediction(example_id=example.id, action=Action.ABSTAIN, response="", raw_output=""),
        )
        slice_name = str(example.metadata.get("slice", "unknown"))
        parsed_as = str(prediction.metadata.get("parsed_as", "missing"))
        gold_action_counts[example.gold_action.value] += 1
        predicted_action_counts[prediction.action.value] += 1
        parsed_as_counts[parsed_as] += 1
        confusion[example.gold_action.value][prediction.action.value] += 1

        current_action_correct = prediction.action == example.gold_action
        action_correct += int(current_action_correct)
        if prediction.action == Action.ANSWER and example.gold_action != Action.ANSWER:
            over_answer_count += 1

        current_answer_exact = None
        current_answer_contains = None
        if example.gold_action == Action.ANSWER:
            answer_total += 1
            current_answer_exact = exact_match(prediction.response, example.gold_answer or "")
            current_answer_contains = contains_match(prediction.response, example.gold_answer or "")
            answer_exact += int(current_answer_exact and prediction.action == Action.ANSWER)
            answer_contains += int(current_answer_contains and prediction.action == Action.ANSWER)

        current_utility = utility_score(example, prediction, current_action_correct, current_answer_exact)
        utility_total += current_utility
        update_slice_stats(
            slice_stats,
            slice_name,
            example=example,
            prediction=prediction,
            parsed_as=parsed_as,
            action_correct=current_action_correct,
            answer_exact_match=current_answer_exact,
            answer_contains_match=current_answer_contains,
            utility=current_utility,
        )

        details.append(
            {
                "id": example.id,
                "source": example.source,
                "slice": slice_name,
                "gold_action": example.gold_action.value,
                "pred_action": prediction.action.value,
                "parsed_as": parsed_as,
                "action_correct": current_action_correct,
                "answer_exact_match": current_answer_exact,
                "answer_contains_match": current_answer_contains,
                "utility": current_utility,
            }
        )

    total = max(len(examples), 1)
    summary = {
        "num_examples": len(examples),
        "action_accuracy": round(action_correct / total, 4),
        "answer_em": round(answer_exact / max(answer_total, 1), 4),
        "answer_contains_rate": round(answer_contains / max(answer_total, 1), 4),
        "avg_utility": round(utility_total / total, 4),
        "over_answer_rate": round(over_answer_count / total, 4),
        "gold_action_counts": dict(gold_action_counts),
        "pred_action_counts": dict(predicted_action_counts),
        "parsed_as_counts": dict(parsed_as_counts),
        "json_parse_rate": round(parsed_as_counts.get("json", 0) / total, 4),
        "confusion": {gold: dict(row) for gold, row in confusion.items()},
        "per_slice": finalize_slice_stats(slice_stats),
    }
    return summary, details


def utility_score(
    example: Example,
    prediction: Prediction,
    action_correct: bool,
    answer_exact_match: bool | None,
) -> float:
    if example.gold_action == Action.ANSWER:
        if prediction.action == Action.ANSWER and answer_exact_match:
            return 1.0
        if prediction.action == Action.ANSWER:
            return -0.5
        if prediction.action == Action.ASK:
            return -0.25
        if prediction.action == Action.ABSTAIN:
            return -0.5
        return -0.75

    if action_correct:
        return 0.5
    if prediction.action == Action.ANSWER:
        return -1.0
    return -0.25


def update_slice_stats(
    stats: dict[str, dict[str, float | int]],
    slice_name: str,
    *,
    example: Example,
    prediction: Prediction,
    parsed_as: str,
    action_correct: bool,
    answer_exact_match: bool | None,
    answer_contains_match: bool | None,
    utility: float,
) -> None:
    bucket = stats.setdefault(
        slice_name,
        {
            "count": 0,
            "action_correct": 0,
            "utility_total": 0.0,
            "answer_total": 0,
            "answer_exact": 0,
            "answer_contains": 0,
            "over_answer": 0,
            "json_parsed": 0,
        },
    )
    bucket["count"] += 1
    bucket["action_correct"] += int(action_correct)
    bucket["utility_total"] += utility
    if example.gold_action == Action.ANSWER:
        bucket["answer_total"] += 1
        bucket["answer_exact"] += int(bool(answer_exact_match and prediction.action == Action.ANSWER))
        bucket["answer_contains"] += int(bool(answer_contains_match and prediction.action == Action.ANSWER))
    if prediction.action == Action.ANSWER and example.gold_action != Action.ANSWER:
        bucket["over_answer"] += 1
    bucket["json_parsed"] += int(parsed_as == "json")


def finalize_slice_stats(
    stats: dict[str, dict[str, float | int]]
) -> dict[str, dict[str, float | int]]:
    finalized: dict[str, dict[str, float | int]] = {}
    for slice_name, bucket in stats.items():
        count = int(bucket["count"])
        answer_total = int(bucket["answer_total"])
        finalized[slice_name] = {
            "count": count,
            "action_accuracy": round(int(bucket["action_correct"]) / max(count, 1), 4),
            "avg_utility": round(float(bucket["utility_total"]) / max(count, 1), 4),
            "answer_em": round(int(bucket["answer_exact"]) / max(answer_total, 1), 4),
            "answer_contains_rate": round(int(bucket["answer_contains"]) / max(answer_total, 1), 4),
            "over_answer_rate": round(int(bucket["over_answer"]) / max(count, 1), 4),
            "json_parse_rate": round(int(bucket["json_parsed"]) / max(count, 1), 4),
        }
    return finalized


def _contains_token_subsequence(container: list[str], query: list[str]) -> bool:
    if not query or len(query) > len(container):
        return False
    width = len(query)
    for index in range(len(container) - width + 1):
        if container[index : index + width] == query:
            return True
    return False
