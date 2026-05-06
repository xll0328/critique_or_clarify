from __future__ import annotations

import argparse
import http.client
import json
import os
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ModelRow(dict):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List low-cost AIHubMix models using the model management API."
    )
    parser.add_argument("--api-key-env", default="AIHUBMIX_API_KEY", help="Environment variable for API key.")
    parser.add_argument("--base-url", default="https://aihubmix.com", help="AIHubMix base URL.")
    parser.add_argument("--type", default="llm", help="Model type filter, e.g. llm.")
    parser.add_argument(
        "--feature",
        action="append",
        default=[],
        help="Optional feature filter, repeatable. Example: --feature structured_outputs",
    )
    parser.add_argument("--top-k", type=int, default=12, help="Number of rows to keep after sorting by blended price.")
    parser.add_argument("--retry", type=int, default=4, help="Retries for transient network errors.")
    parser.add_argument(
        "--output-json",
        default="experiments/day1/aihubmix_budget_models.json",
        help="Path to save ranked model rows as JSON.",
    )
    parser.add_argument(
        "--output-md",
        default="experiments/day1/aihubmix_budget_models.md",
        help="Path to save ranked model rows as markdown.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    key = os.getenv(args.api_key_env, "").strip()
    payload = fetch_models(
        base_url=args.base_url,
        api_key=key,
        model_type=args.type,
        features=args.feature,
        retry=args.retry,
    )
    rows = rank_rows(payload, top_k=args.top_k)

    output_json = resolve_path(args.output_json)
    output_md = resolve_path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(
            rows,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    output_md.write_text(render_markdown(rows, args.type, args.feature), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {display(output_json)}")
    print(f"Wrote markdown report to {display(output_md)}")


def fetch_models(*, base_url: str, api_key: str, model_type: str, features: list[str], retry: int) -> dict:
    query: dict[str, str] = {}
    if model_type:
        query["type"] = model_type
    if features:
        query["feature"] = ",".join(features)

    suffix = "/api/v1/models"
    if query:
        suffix = f"{suffix}?{urlencode(query)}"
    url = f"{base_url.rstrip('/')}{suffix}"

    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = Request(url=url, headers=headers, method="GET")
    context = ssl.create_default_context()
    attempts = max(1, retry + 1)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, context=context, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            transient = exc.code in {408, 409, 425, 429, 500, 502, 503, 504}
            if transient and attempt < attempts:
                continue
            raise SystemExit(f"HTTP {exc.code} while fetching models: {body[:300]}") from exc
        except (URLError, TimeoutError, http.client.RemoteDisconnected, OSError) as exc:
            last_error = exc
            if attempt < attempts:
                continue
    raise SystemExit(f"Network error while fetching models after retries: {last_error}")


def rank_rows(payload: dict, *, top_k: int) -> list[ModelRow]:
    models = payload.get("data", [])
    rows: list[ModelRow] = []
    for model in models:
        pricing = model.get("pricing", {})
        input_price = as_float(pricing.get("input"))
        output_price = as_float(pricing.get("output"))
        if input_price is None or output_price is None:
            continue
        rows.append(
            ModelRow(
                model_id=str(model.get("model_id", "")),
                types=str(model.get("types", "")),
                input_price=input_price,
                output_price=output_price,
                blended_price=(input_price + output_price) / 2.0,
                features=str(model.get("features", "")),
                context_length=as_int(model.get("context_length")),
                max_output=as_int(model.get("max_output")),
            )
        )
    rows.sort(
        key=lambda row: (
            float(row["blended_price"]),
            float(row["input_price"]),
            float(row["output_price"]),
            str(row["model_id"]),
        )
    )
    return rows[: max(1, top_k)]


def render_markdown(rows: list[ModelRow], model_type: str, features: list[str]) -> str:
    feature_text = ",".join(features) if features else "none"
    lines = [
        "# AIHubMix Budget Model Ranking",
        "",
        f"- type filter: `{model_type or 'all'}`",
        f"- feature filter: `{feature_text}`",
        "",
        "| Rank | Model | Input Price | Output Price | Blended | Features | Context | Max Output |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | `{row['model_id']}` | `{float(row['input_price']):.6g}` | `{float(row['output_price']):.6g}` | "
            f"`{float(row['blended_price']):.6g}` | `{row.get('features') or '-'}` | `{int(row['context_length'])}` | `{int(row['max_output'])}` |"
        )
    lines.append("")
    return "\n".join(lines)


def as_float(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return ROOT / path


def display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
