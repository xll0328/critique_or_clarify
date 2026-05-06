from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prefetch a Hugging Face model snapshot and verify weight files exist.")
    parser.add_argument("--repo-id", required=True, help="Model repo id, e.g. HuggingFaceTB/SmolLM2-135M-Instruct")
    parser.add_argument(
        "--allow-pattern",
        action="append",
        default=[],
        help="Additional allow pattern. Can be passed multiple times.",
    )
    parser.add_argument("--repo-type", default="model", choices=["model", "dataset", "space"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    patterns = args.allow_pattern or [
        "*.json",
        "*.txt",
        "*.model",
        "*.py",
        "*.md",
        "*.safetensors",
        "*.bin",
        "*.tokenizer",
        "*.tiktoken",
        "*.sentencepiece",
    ]

    path = snapshot_download(
        repo_id=args.repo_id,
        repo_type=args.repo_type,
        allow_patterns=patterns,
    )
    snapshot_path = Path(path)
    weight_files = sorted(snapshot_path.rglob("*.safetensors")) + sorted(snapshot_path.rglob("*.bin"))

    print(f"snapshot_path={snapshot_path}")
    print(f"num_weight_files={len(weight_files)}")
    for weight_file in weight_files[:20]:
        print(weight_file)

    if not weight_files:
        raise SystemExit("No model weight files were found in the downloaded snapshot.")


if __name__ == "__main__":
    main()
