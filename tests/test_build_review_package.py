from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "critique_or_clarify_emnlp2026_review"
FORBIDDEN_SUBSTRINGS = (
    "/data/sony",
    "sony",
    "model_cache",
    "outputs/day1",
    "experiments/day1",
    "_assets/",
)


def test_build_review_package_copies_only_anonymous_paper_sources(tmp_path: Path) -> None:
    script_path = REPO_ROOT / "scripts" / "build_review_package.sh"

    subprocess.run(
        [str(script_path), "--output-dir", str(tmp_path), "--no-build"],
        check=True,
        capture_output=True,
        text=True,
    )

    package_dir = tmp_path / PACKAGE_NAME
    paper_dir = package_dir / "paper"
    expected_paths = [
        paper_dir / "main.tex",
        paper_dir / "main.pdf",
        paper_dir / "references.bib",
        paper_dir / "build.sh",
        paper_dir / "README.md",
        paper_dir / "sections" / "01_introduction.tex",
        paper_dir / "tables" / "day1_scale_reasoning_main.tex",
        paper_dir / "figures" / "figure2_action_calibration.pdf",
        paper_dir / "styles" / "acl.sty",
    ]
    assert all(path.exists() for path in expected_paths)

    packaged_files = [path for path in package_dir.rglob("*") if path.is_file()]
    assert not any(path.suffix in {".aux", ".log", ".out", ".blg", ".bbl"} for path in packaged_files)

    leaks: list[str] = []
    for path in packaged_files:
        if path.suffix.lower() == ".pdf":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in FORBIDDEN_SUBSTRINGS:
            if needle in text:
                leaks.append(f"{path.relative_to(package_dir)} contains {needle}")

    assert leaks == []
