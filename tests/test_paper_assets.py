from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


def _paper_tex() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in PAPER_DIR.rglob("*.tex"))


def test_paper_input_files_exist() -> None:
    tex = _paper_tex()
    inputs = re.findall(r"\\input\{([^}]+)\}", tex)

    missing = [
        target
        for target in inputs
        if not (PAPER_DIR / f"{target}.tex").exists() and not (PAPER_DIR / target).exists()
    ]

    assert missing == []


def test_paper_graphics_files_exist() -> None:
    tex = _paper_tex()
    graphics = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)

    missing = [target for target in graphics if not (PAPER_DIR / target).exists()]

    assert missing == []
