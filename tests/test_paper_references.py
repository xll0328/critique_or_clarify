from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


def _citation_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]+)\}", tex):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def _bib_keys(bib: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))


def test_paper_citations_are_defined() -> None:
    tex = "\n".join(path.read_text(encoding="utf-8") for path in PAPER_DIR.rglob("*.tex"))
    bib = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")

    missing = sorted(_citation_keys(tex) - _bib_keys(bib))

    assert missing == []


def test_paper_bibliography_entries_are_used() -> None:
    tex = "\n".join(path.read_text(encoding="utf-8") for path in PAPER_DIR.rglob("*.tex"))
    bib = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")

    unused = sorted(_bib_keys(bib) - _citation_keys(tex))

    assert unused == []
