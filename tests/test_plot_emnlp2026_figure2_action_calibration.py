from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_plot_emnlp2026_figure2_action_calibration_outputs_assets(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "plot_emnlp2026_figure2_action_calibration.py"
    output_prefix = tmp_path / "figure2"

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
    assert caption_path.exists()
    caption = caption_path.read_text(encoding="utf-8")
    assert "Reasoning traces do not automatically" in caption
    assert "shared model-color legend" in caption
    assert "caution is not monotonic safety" in caption

    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    assert len(rows) >= 5
    deepseek7b = next(row for row in rows if row["model"] == "DeepSeek-R1-Distill-Qwen-7B")
    assert deepseek7b["style"] == "reasoning"
    assert float(deepseek7b["dev_action_accuracy"]) == 0.3667
    assert float(deepseek7b["quick_stale_stale_over_answer"]) == 0.75


def test_plot_emnlp2026_figure2_script_keeps_shared_model_legend() -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "plot_emnlp2026_figure2_action_calibration.py"
    script = script_path.read_text(encoding="utf-8")

    assert "add_model_legend" in script
    assert "Shared model-color legend for panels B and C" in script
    assert "colors use shared legend" in script
