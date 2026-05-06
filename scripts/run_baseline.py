from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.backends import GenerationConfig, HeuristicBackend, TransformersBackend
from coc.io import load_examples, save_predictions
from coc.metrics import evaluate_predictions
from coc.prompts import build_messages, render_messages_plaintext


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a baseline for critique-or-clarify.")
    parser.add_argument("--backend", choices=["heuristic", "transformers"], default="heuristic")
    parser.add_argument("--data", required=True, help="Path to JSONL examples.")
    parser.add_argument("--output", required=True, help="Where to write JSONL predictions.")
    parser.add_argument("--eval-json", help="Optional path for a JSON metrics summary.")
    parser.add_argument("--dump-prompts-dir", help="Optional directory for plaintext prompts.")
    parser.add_argument("--limit", type=int, default=0, help="Limit examples for quick debugging.")
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Print progress every N examples. Set to 0 to disable.",
    )
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
        help="Prompt template variant. Keep `main` for benchmark runs; use `compact` for weak-model diagnostics.",
    )
    parser.add_argument("--model", help="Hugging Face model name for the transformers backend.")
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--allow-pytorch-bin", action="store_true")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible sampling baselines.")
    parser.add_argument(
        "--omit-system-prompt",
        action="store_true",
        help="Render only a user message. Useful for reasoning models that recommend avoiding system prompts.",
    )
    parser.add_argument(
        "--assistant-prefix",
        default="",
        help="Optional text appended right after the generation prompt, e.g. '<think>\\n' for reasoning models.",
    )
    args = parser.parse_args()
    args.assistant_prefix = _decode_escaped_text(args.assistant_prefix)
    return args


def _decode_escaped_text(text: str) -> str:
    if not text:
        return ""
    return bytes(text, "utf-8").decode("unicode_escape")


def main() -> None:
    args = parse_args()
    examples = load_examples(args.data)
    if args.limit > 0:
        examples = examples[: args.limit]

    if args.backend == "heuristic":
        backend = HeuristicBackend()
    else:
        if not args.model:
            raise ValueError("--model is required when --backend transformers")
        backend = TransformersBackend(
            GenerationConfig(
                model_name=args.model,
                prompt_style=args.prompt_style,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                device_map=args.device_map,
                dtype=args.dtype,
                trust_remote_code=args.trust_remote_code,
                use_safetensors=not args.allow_pytorch_bin,
                local_files_only=args.local_files_only,
                include_system_prompt=not args.omit_system_prompt,
                assistant_prefix=args.assistant_prefix,
                seed=args.seed,
            )
        )

    prompt_dir = Path(args.dump_prompts_dir) if args.dump_prompts_dir else None
    if prompt_dir is not None:
        prompt_dir.mkdir(parents=True, exist_ok=True)

    predictions = []
    total = len(examples)
    for index, example in enumerate(examples, start=1):
        if prompt_dir is not None:
            prompt_path = prompt_dir / f"{example.id}.txt"
            prompt_text = render_messages_plaintext(
                build_messages(
                    example,
                    style=args.prompt_style,
                    include_system_prompt=not args.omit_system_prompt,
                )
            )
            if args.assistant_prefix:
                prompt_text += f"\n\nASSISTANT PREFILL:\n{args.assistant_prefix}"
            prompt_path.write_text(prompt_text, encoding="utf-8")
        prediction = backend.predict(example)
        predictions.append(prediction)
        if args.progress_every > 0 and (index % args.progress_every == 0 or index == total):
            print(f"Processed {index}/{total} examples", flush=True)

    save_predictions(args.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {args.output}")

    if args.eval_json:
        summary, details = evaluate_predictions(examples, predictions)
        eval_path = Path(args.eval_json)
        eval_path.parent.mkdir(parents=True, exist_ok=True)
        eval_path.write_text(
            json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
