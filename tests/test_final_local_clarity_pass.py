from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
PAPER = REPO_ROOT / "paper"
LOCK = DOCS / "emnlp2026_final_local_clarity_pass.md"


def test_final_local_clarity_pass_records_closed_gates_and_scope() -> None:
    text = LOCK.read_text(encoding="utf-8")

    required_fragments = [
        "Human validation is complete at `61/61`",
        "DeepSeek-R1-Distill-Qwen-7B has both development and quick+stale metrics",
        "next-action selection under defective inputs",
        "not present the intervention as a complete method",
        "Final Local Clarity Pass is closed",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_manuscript_keeps_page_neutral_intervention_float_placement() -> None:
    main = (PAPER / "main.tex").read_text(encoding="utf-8")
    generated_table = (
        REPO_ROOT
        / "experiments"
        / "day1"
        / "tables"
        / "qwen25_15b_quick_plus_stale_intervention_main.tex"
    ).read_text(encoding="utf-8")
    paper_table = (
        PAPER / "tables" / "qwen25_15b_quick_plus_stale_intervention_main.tex"
    ).read_text(encoding="utf-8")

    assert "\\usepackage{dblfloatfix}" in main
    assert "\\begin{table*}[!b]" in generated_table
    assert "\\begin{table*}[!b]" in paper_table


def test_status_docs_point_to_final_local_clarity_pass() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_oral_best_paper_sprint_plan.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_final_local_clarity_pass.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
