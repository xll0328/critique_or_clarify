from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
PACKET = DOCS / "emnlp2026_venue_form_transfer_packet.md"


def test_venue_form_transfer_packet_covers_required_form_areas() -> None:
    text = PACKET.read_text(encoding="utf-8")

    required_fragments = [
        "Data Sources And Provenance",
        "Annotation And Human Validation",
        "Privacy And Identifying Information",
        "Risks, Misuse, And Limitations",
        "Reproducibility And Artifacts",
        "Environmental Or Compute Disclosure",
        "Human-Only Final Checks",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_venue_form_transfer_packet_preserves_scoped_gate_outputs() -> None:
    text = PACKET.read_text(encoding="utf-8")

    required_fragments = [
        "not the official venue form",
        "not a substitute for final human sign-off",
        "not from private user logs",
        "human_validation_queue_ok completed=61/61",
        "DeepSeek-R1-Distill-Qwen-7B dev action accuracy `0.3667`",
        "full test suite `129 passed`",
        "`paper/main.pdf`, 13 pages",
        "submission_lock_checks_ok",
        "Do not invent energy, emissions, or hardware utilization numbers.",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]
    assert missing == []


def test_status_docs_point_to_venue_form_transfer_packet() -> None:
    docs_to_check = [
        DOCS / "emnlp2026_manuscript_gap_list.md",
        DOCS / "emnlp2026_submission_readiness_checklist.md",
        DOCS / "emnlp2026_responsible_nlp_checklist.md",
        DOCS / "emnlp2026_reproducibility_appendix.md",
    ]

    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in docs_to_check
        if "docs/emnlp2026_venue_form_transfer_packet.md"
        not in path.read_text(encoding="utf-8")
    ]

    assert missing == []
