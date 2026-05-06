from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from coc.schema import Example, Prediction


def read_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_examples(path: str | Path) -> list[Example]:
    return [Example.from_dict(row) for row in read_jsonl(path)]


def save_predictions(path: str | Path, predictions: Iterable[Prediction]) -> None:
    write_jsonl(path, (prediction.to_dict() for prediction in predictions))
