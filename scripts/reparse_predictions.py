from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.backends import parse_prediction
from coc.io import read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reparse saved prediction JSONL files from raw model output.")
    parser.add_argument("--input", required=True, help="Existing prediction JSONL with raw_output fields.")
    parser.add_argument(
        "--output",
        help="Where to write reparsed predictions. Defaults to '<input>_reparsed.jsonl' or the input directory.",
    )
    return parser.parse_args()


def iter_input_paths(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(
            path
            for path in input_path.iterdir()
            if path.suffix == ".jsonl" and not path.name.endswith("_reparsed.jsonl")
        )
    raise FileNotFoundError(f"Input path does not exist: {input_path}")


def resolve_output_path(input_path: Path, source_path: Path, output_arg: str | None) -> Path:
    if input_path.is_file():
        if output_arg:
            return Path(output_arg)
        return source_path.with_name(f"{source_path.stem}_reparsed{source_path.suffix}")

    output_dir = Path(output_arg) if output_arg else input_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{source_path.stem}_reparsed{source_path.suffix}"


def reparse_file(input_path: Path, output_path: Path) -> int:
    rows = read_jsonl(input_path)
    reparsed_rows: list[dict] = []
    for row in rows:
        prediction = parse_prediction(str(row.get("raw_output", "")), str(row["example_id"]))
        merged_metadata = dict(row.get("metadata", {}))
        merged_metadata.update(prediction.metadata)
        reparsed_rows.append(
            {
                "example_id": prediction.example_id,
                "action": prediction.action.value,
                "response": prediction.response,
                "confidence": prediction.confidence,
                "raw_output": prediction.raw_output,
                "metadata": merged_metadata,
            }
        )
    write_jsonl(output_path, reparsed_rows)
    print(f"Reparsed {len(reparsed_rows)} rows into {output_path}")
    return len(reparsed_rows)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    total_rows = 0
    input_paths = iter_input_paths(input_path)
    for source_path in input_paths:
        output_path = resolve_output_path(input_path, source_path, args.output)
        total_rows += reparse_file(source_path, output_path)
    if len(input_paths) > 1:
        print(f"Processed {len(input_paths)} files and {total_rows} rows total.")


if __name__ == "__main__":
    main()
