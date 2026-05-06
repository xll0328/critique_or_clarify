from __future__ import annotations

import argparse
from pathlib import Path

from safetensors import safe_open


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Link a downloaded safetensors blob into a Hugging Face snapshot and verify it can be opened."
    )
    parser.add_argument("--snapshot-dir", required=True, help="Snapshot directory that should expose the final file.")
    parser.add_argument("--blob-path", required=True, help="Path to the downloaded blob or .incomplete file.")
    parser.add_argument("--filename", default="model.safetensors", help="Filename to create inside the snapshot.")
    return parser.parse_args()


def verify_safetensors(path: Path) -> int:
    with safe_open(path, framework="pt") as handle:
        return len(handle.keys())


def main() -> None:
    args = parse_args()
    snapshot_dir = Path(args.snapshot_dir)
    blob_path = Path(args.blob_path)
    target_path = snapshot_dir / args.filename

    if not snapshot_dir.is_dir():
        raise SystemExit(f"Snapshot directory does not exist: {snapshot_dir}")
    if not blob_path.is_file():
        raise SystemExit(f"Blob path does not exist: {blob_path}")

    num_tensors = verify_safetensors(blob_path)
    target_path.unlink(missing_ok=True)
    target_path.hardlink_to(blob_path)

    print(f"linked={target_path}")
    print(f"blob={blob_path}")
    print(f"num_tensors={num_tensors}")
    print(f"size_bytes={blob_path.stat().st_size}")


if __name__ == "__main__":
    main()
