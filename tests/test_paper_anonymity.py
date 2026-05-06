from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


MANUSCRIPT_PATTERNS = ("main.tex", "sections/*.tex", "tables/*.tex", "references.bib", "build.sh", "README.md")
FORBIDDEN_SUBSTRINGS = (
    "/data/sony",
    "sony",
    "model_cache",
    "outputs/day1",
    "experiments/day1",
    "_assets/",
)


def test_manuscript_sources_do_not_expose_local_paths() -> None:
    files: list[Path] = []
    for pattern in MANUSCRIPT_PATTERNS:
        files.extend(PAPER_DIR.glob(pattern))

    leaks: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_SUBSTRINGS:
            if needle in text:
                leaks.append(f"{path.relative_to(REPO_ROOT)} contains {needle}")

    assert leaks == []
