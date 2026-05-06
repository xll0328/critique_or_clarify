from __future__ import annotations

import argparse
import http.client
import json
import os
import ssl
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.backends import parse_prediction
from coc.io import load_examples, read_jsonl, save_predictions
from coc.metrics import evaluate_predictions
from coc.prompts import build_messages
from coc.schema import Prediction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an OpenAI-compatible baseline through AIHubMix and evaluate with the existing pipeline."
    )
    parser.add_argument("--model", required=True, help="Remote model id, e.g. gpt-4o-mini.")
    parser.add_argument("--data", required=True, help="Gold JSONL split path.")
    parser.add_argument("--output", required=True, help="Prediction JSONL path.")
    parser.add_argument("--eval-json", required=True, help="Evaluation JSON path.")
    parser.add_argument("--api-key-env", default="AIHUBMIX_API_KEY", help="Environment variable for API key.")
    parser.add_argument("--base-url", default="https://aihubmix.com", help="AIHubMix base URL.")
    parser.add_argument(
        "--prompt-style",
        choices=[
            "main",
            "compact",
            "self_contained",
            "verify_first",
            "decision_first",
            "decision_first_balanced",
            "decision_first_guarded",
            "critique_first",
        ],
        default="main",
    )
    parser.add_argument("--omit-system-prompt", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--retry", type=int, default=3, help="Retries per example for transient network/server errors.")
    parser.add_argument("--sleep-seconds", type=float, default=0.0, help="Optional sleep after each request.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing output JSONL if present.",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=20,
        help="Checkpoint predictions to disk every N newly processed examples.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_key = os.getenv(args.api_key_env, "").strip()
    if not api_key:
        raise SystemExit(f"Missing API key: set {args.api_key_env} in your environment.")

    examples = load_examples(args.data)
    if args.limit > 0:
        examples = examples[: args.limit]

    output_path = Path(args.output)
    allowed_ids = {example.id for example in examples}
    predictions: list[Prediction] = []
    existing_ids: set[str] = set()
    if args.resume and output_path.exists():
        rows = read_jsonl(output_path)
        for row in rows:
            try:
                prediction = Prediction.from_dict(row)
            except Exception:
                continue
            if prediction.example_id not in allowed_ids:
                continue
            if prediction.example_id in existing_ids:
                continue
            existing_ids.add(prediction.example_id)
            predictions.append(prediction)

    if existing_ids:
        examples = [example for example in examples if example.id not in existing_ids]

    resumed = len(existing_ids)
    total = len(examples)
    full_total = resumed + total
    if resumed > 0:
        print(f"Resumed with {resumed}/{full_total} existing predictions", flush=True)

    for idx, example in enumerate(examples, start=1):
        messages = build_messages(
            example,
            style=args.prompt_style,
            include_system_prompt=not args.omit_system_prompt,
        )
        raw_output = chat_completion(
            base_url=args.base_url,
            api_key=api_key,
            model=args.model,
            messages=messages,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
            request_timeout=args.request_timeout,
            retry=args.retry,
        )
        prediction = parse_prediction(raw_output, example.id)
        prediction.metadata["backend"] = "aihubmix_openai_compatible"
        prediction.metadata["model_name"] = args.model
        prediction.metadata["prompt_style"] = args.prompt_style
        predictions.append(prediction)

        processed_total = resumed + idx
        if args.save_every > 0 and (idx % args.save_every == 0 or processed_total == full_total):
            save_predictions(args.output, predictions)
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)
        if args.progress_every > 0 and (processed_total % args.progress_every == 0 or processed_total == full_total):
            print(f"Processed {processed_total}/{full_total} examples", flush=True)

    save_predictions(args.output, predictions)
    eval_examples = load_examples(args.data)
    if args.limit > 0:
        eval_examples = eval_examples[: args.limit]
    summary, details = evaluate_predictions(eval_examples, predictions)
    Path(args.eval_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.eval_json).write_text(
        json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(predictions)} predictions to {args.output}")
    print(json.dumps(summary, indent=2))


def chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    top_p: float,
    max_tokens: int,
    request_timeout: int,
    retry: int,
) -> str:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    context = ssl.create_default_context()

    attempts = max(1, retry + 1)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url=url, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, context=context, timeout=request_timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return extract_content(data)
        except HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            transient = exc.code in {408, 409, 425, 429, 500, 502, 503, 504}
            if transient and attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
            raise SystemExit(f"HTTP {exc.code} from AIHubMix: {body_text[:500]}") from exc
        except URLError as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
        except TimeoutError as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
        except (http.client.RemoteDisconnected, OSError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)
                continue

    raise SystemExit(f"Network error from AIHubMix after retries: {last_error}")


def extract_content(payload: dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        raise SystemExit(f"Malformed chat completion payload: missing choices. keys={sorted(payload.keys())}")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "\n".join(part for part in parts if part).strip()
    return str(content)


if __name__ == "__main__":
    main()
