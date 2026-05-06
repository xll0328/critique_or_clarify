from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    ANSWER = "answer"
    ASK = "ask"
    CHALLENGE = "challenge"
    ABSTAIN = "abstain"


@dataclass(slots=True)
class Example:
    id: str
    prompt: str
    passages: list[str]
    gold_action: Action
    gold_answer: str | None = None
    gold_response: str | None = None
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Example":
        return cls(
            id=str(data["id"]),
            prompt=str(data["prompt"]),
            passages=[str(item) for item in data.get("passages", [])],
            gold_action=Action(str(data["gold_action"]).lower()),
            gold_answer=_optional_str(data.get("gold_answer")),
            gold_response=_optional_str(data.get("gold_response")),
            source=str(data.get("source", "unknown")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["gold_action"] = self.gold_action.value
        return payload


@dataclass(slots=True)
class Prediction:
    example_id: str
    action: Action
    response: str = ""
    confidence: float | None = None
    raw_output: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Prediction":
        confidence = data.get("confidence")
        return cls(
            example_id=str(data["example_id"]),
            action=Action(str(data["action"]).lower()),
            response=str(data.get("response", "")),
            confidence=float(confidence) if confidence is not None else None,
            raw_output=str(data.get("raw_output", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action"] = self.action.value
        return payload


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
