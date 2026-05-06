from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.backends import GenerationConfig, HeuristicBackend, TransformersBackend
from coc.io import load_examples, save_predictions
from coc.metrics import evaluate_predictions
from coc.prompts import build_messages, render_messages_plaintext


@dataclass(frozen=True)
class Job:
    data: Path
    output: Path
    eval_json: Path | None
    dump_prompts_dir: Path | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one loaded baseline backend across multiple data/output jobs."
    )
    parser.add_argument("--backend", choices=["heuristic", "transformers"], default="heuristic")
    parser.add_argument(
        "--job",
        action="append",
        default=[],
        metavar="DATA=OUTPUT=EVAL_JSON",
        help=(
            "Batch job triple. Use '-' for EVAL_JSON to skip metrics. Repeat for each split. "
            "The separator is '=' because project paths do not use it."
        ),
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit examples per job for quick debugging.")
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Print progress every N examples per job. Set to 0 to disable.",
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
        help="Prompt template variant.",
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
    parser.add_argument(
        "--dump-prompts-root",
        help="Optional root directory for plaintext prompts. Each job writes into a numbered subdirectory.",
    )
    args = parser.parse_args()
    args.assistant_prefix = _decode_escaped_text(args.assistant_prefix)
    if not args.job:
        raise SystemExit("At least one --job DATA=OUTPUT=EVAL_JSON is required.")
    return args


def _decode_escaped_text(text: str) -> str:
    if not text:
        return ""
    return bytes(text, "utf-8").decode("unicode_escape")


def main() -> None:
    args = parse_args()
    jobs = parse_jobs(args.job, args.dump_prompts_root)
    backend = build_backend(args)
    for index, job in enumerate(jobs, start=1):
        run_job(args, backend, job, index=index, total_jobs=len(jobs))


def parse_jobs(raw_jobs: list[str], dump_prompts_root: str | None) -> list[Job]:
    jobs = []
    for index, raw_job in enumerate(raw_jobs, start=1):
        parts = raw_job.split("=")
        if len(parts) != 3:
            raise ValueError(f"--job must use DATA=OUTPUT=EVAL_JSON, got: {raw_job}")
        data, output, eval_json = parts
        dump_dir = None
        if dump_prompts_root:
            dump_dir = Path(dump_prompts_root) / f"job_{index:02d}_{Path(output).stem}"
        jobs.append(
            Job(
                data=Path(data),
                output=Path(output),
                eval_json=None if eval_json == "-" else Path(eval_json),
                dump_prompts_dir=dump_dir,
            )
        )
    return jobs


def build_backend(args: argparse.Namespace):
    if args.backend == "heuristic":
        return HeuristicBackend()
    if not args.model:
        raise ValueError("--model is required when --backend transformers")
    return TransformersBackend(
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


def run_job(args: argparse.Namespace, backend, job: Job, *, index: int, total_jobs: int) -> None:
    examples = load_examples(job.data)
    if args.limit > 0:
        examples = examples[: args.limit]
    if job.dump_prompts_dir is not None:
        job.dump_prompts_dir.mkdir(parents=True, exist_ok=True)

    predictions = []
    total = len(examples)
    print(f"Starting job {index}/{total_jobs}: data={job.data} examples={total}", flush=True)
    for example_index, example in enumerate(examples, start=1):
        if job.dump_prompts_dir is not None:
            prompt_text = render_messages_plaintext(
                build_messages(
                    example,
                    style=args.prompt_style,
                    include_system_prompt=not args.omit_system_prompt,
                )
            )
            if args.assistant_prefix:
                prompt_text += f"\n\nASSISTANT PREFILL:\n{args.assistant_prefix}"
            (job.dump_prompts_dir / f"{example.id}.txt").write_text(prompt_text, encoding="utf-8")
        predictions.append(backend.predict(example))
        if args.progress_every > 0 and (example_index % args.progress_every == 0 or example_index == total):
            print(f"Job {index}/{total_jobs}: processed {example_index}/{total} examples", flush=True)

    save_predictions(job.output, predictions)
    print(f"Wrote {len(predictions)} predictions to {job.output}", flush=True)

    if job.eval_json is None:
        return
    summary, details = evaluate_predictions(examples, predictions)
    job.eval_json.parent.mkdir(parents=True, exist_ok=True)
    job.eval_json.write_text(
        json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
