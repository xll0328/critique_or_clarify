from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_full_split_sensitivity_table_includes_ci_and_frontier_row(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_full_split_sensitivity_table.py"
    output_tex = tmp_path / "full_split_sensitivity.tex"

    subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--samples",
            "25",
            "--output",
            str(output_tex),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = output_tex.read_text(encoding="utf-8")
    assert r"$\Delta$ Action Acc. (95\% CI)" in text
    assert r"$\Delta$ Utility (95\% CI)" in text
    assert "gpt-5-chat-latest / decision-first" in text
    assert "[-" in text or "[0" in text
