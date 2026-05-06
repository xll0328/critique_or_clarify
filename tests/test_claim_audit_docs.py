from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"


def test_numeric_claim_audit_uses_final_lock_gate() -> None:
    text = (DOCS / "emnlp2026_numeric_claim_audit.md").read_text(encoding="utf-8")

    required_fragments = [
        "current submission-freeze audit",
        "paper/tables/day1_scale_reasoning_macros.tex",
        "paper/tables/day1_quick_stale_macros.tex",
        "paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex",
        "Full test suite `129 passed`",
        "data/candidates/emnlp2026_ask_abstain_seed_candidates_manifest.json",
        "experiments/emnlp2026/ask_abstain_candidate_coverage_audit.json",
        "scripts/promote_validated_expansion_candidates.py",
        "docs/emnlp2026_oral_best_paper_quality_audit.json",
        "scripts/audit_oral_best_paper_readiness.py",
        "./scripts/run_submission_lock_checks.sh",
        "submission_lock_checks_ok",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_numeric_claim_audit_no_longer_lists_manual_final_gate_sequence() -> None:
    text = (DOCS / "emnlp2026_numeric_claim_audit.md").read_text(encoding="utf-8")

    stale_fragments = [
        "./scripts/make_day1_scale_reasoning_comparison.sh\n./scripts/sync_paper_assets.sh",
        "python scripts/validate_human_validation_queue.py \\\n  --queue _assets/human_validation_work_queue.csv",
    ]

    present = [fragment for fragment in stale_fragments if fragment in text]
    assert present == []


def test_claim_ledger_scopes_decision_first_to_quick_stale() -> None:
    text = (DOCS / "emnlp2026_claim_ledger.md").read_text(encoding="utf-8")

    required_fragments = [
        "current submission-freeze state",
        "A lightweight decision-first intervention can reduce over-answering while preserving answer-supported behavior on quick+stale.",
        "promising, scoped",
        "Do not claim broad assistant helpfulness.",
        "On the Qwen2.5-1.5B quick+stale split",
        "dev-scale evidence is directionally useful but too small for a broad method claim",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_claim_ledger_records_final_lock_wording() -> None:
    text = (DOCS / "emnlp2026_claim_ledger.md").read_text(encoding="utf-8")

    assert "The current artifact freeze passes `./scripts/run_submission_lock_checks.sh`" in text
    assert "anonymous review-package build" in text
    assert "package hygiene scan" in text
    assert "preserving overall utility on the Qwen2.5-1.5B day-1 dev split" not in text


def test_claim_ledger_keeps_600_split_as_stress_evidence() -> None:
    text = (DOCS / "emnlp2026_claim_ledger.md").read_text(encoding="utf-8")

    assert "The slice-balanced 600-example split is useful as stress evidence but is not the canonical benchmark." in text
    assert "The 600-example split changes answer counts and is currently stress evidence for slice-balance sensitivity." in text
    assert "the canonical 560-example split remains the headline benchmark" in text
