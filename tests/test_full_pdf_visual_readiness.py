from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
SCRIPT = REPO_ROOT / "scripts" / "audit_full_pdf_visual_readiness.py"
AUDIT_MD = DOCS / "emnlp2026_full_pdf_visual_readiness_audit.md"
AUDIT_JSON = DOCS / "emnlp2026_full_pdf_visual_readiness_audit.json"


def test_full_pdf_visual_readiness_audit_records_rendered_full_manuscript() -> None:
    text = AUDIT_MD.read_text(encoding="utf-8")
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    required_fragments = [
        "automated full-manuscript PDF render/readability preflight",
        "This is not final human sign-off.",
        "Rendered `paper/main.pdf` to PNG pages",
        "Page count: `13`.",
        "`CRITICAL`: 0",
        "`MAJOR`: 0",
        "The compiled PDF text contains the title/task anchor",
        "do not treat this automated audit as final human submission approval",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []
    assert payload["page_count"] == 13
    assert payload["severity_counts"]["CRITICAL"] == 0
    assert payload["severity_counts"]["MAJOR"] == 0
    assert len(payload["pages"]) == payload["page_count"]
    assert not payload["missing_anchors"]


def test_full_pdf_visual_readiness_is_integrated_into_status_docs_and_lock_gate() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_reviewer_attack_memo.md",
    ]

    missing_docs = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_full_pdf_visual_readiness_audit.md"
        not in path.read_text(encoding="utf-8")
    ]
    assert missing_docs == []

    lock_script = (REPO_ROOT / "scripts" / "run_submission_lock_checks.sh").read_text(encoding="utf-8")
    assert "python scripts/audit_full_pdf_visual_readiness.py" in lock_script
    assert SCRIPT.exists()
