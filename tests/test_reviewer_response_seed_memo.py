from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
MEMO = DOCS / "emnlp2026_reviewer_response_seed_memo.md"


def test_reviewer_response_seed_memo_covers_major_attack_paths() -> None:
    text = MEMO.read_text(encoding="utf-8")

    required_fragments = [
        "Benchmark Soup / Dataset Mixture",
        "Utility Weights Are Arbitrary",
        "Reasoning-Model Overclaim",
        "Intervention Overclaim",
        "Ask And Hard Abstain Coverage",
        "Statistical Confidence And CI Overclaim",
        "benchmark-soup",
        "utility-weight",
        "reasoning-overclaim",
        "intervention-overclaim",
        "statistics-overclaim",
        "Answer quality is an incomplete target",
        "right first move",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_reviewer_response_seed_memo_enforces_scope_constraints() -> None:
    text = MEMO.read_text(encoding="utf-8")

    required_fragments = [
        "not a universal user-cost model",
        "completed Day-1 local checkpoints",
        "exploratory calibration probe",
        "do not claim broad assistant helpfulness",
        "not yet balanced evidence for all possible clarification or abstention settings",
        "local uncertainty checks over the current split samples",
        "avoid fine-grained model-ranking claims",
        "the 600-example split is sensitivity evidence rather than a replacement benchmark",
        "not broad assistant helpfulness or final-answer quality alone",
        "answer quality is incomplete if the model chooses the wrong action first",
        "Do not say:",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_reviewer_response_seed_memo() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_reviewer_attack_memo.md",
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_reviewer_response_seed_memo.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
