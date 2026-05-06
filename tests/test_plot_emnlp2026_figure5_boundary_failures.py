from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_plot_emnlp2026_figure5_boundary_failures_outputs_assets(tmp_path: Path) -> None:
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "plot_emnlp2026_figure5_boundary_failures.py"
    )
    output_prefix = tmp_path / "figure5"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--output-prefix",
            str(output_prefix),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    png_path = output_prefix.with_suffix(".png")
    pdf_path = output_prefix.with_suffix(".pdf")
    csv_path = output_prefix.with_suffix(".csv")
    caption_path = output_prefix.with_name(output_prefix.name + "_caption.md")

    assert png_path.exists()
    assert png_path.stat().st_size > 1000
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000
    assert csv_path.exists()
    assert caption_path.exists()

    caption = caption_path.read_text(encoding="utf-8")
    assert "Boundary failure profile" in caption
    assert "caution does not translate into better first-move calibration" in caption

    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    assert len(rows) == 6
    by_model = {row["model"] for row in rows}
    assert by_model == {"Qwen2.5-1.5B-Instruct", "DeepSeek-R1-Distill-Qwen-7B"}
    assert {row["slice"] for row in rows} == {
        "answerable_control",
        "false_premise",
        "conflicting_evidence",
    }
