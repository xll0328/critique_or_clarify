from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


def _section(name: str) -> str:
    return (PAPER_DIR / "sections" / name).read_text(encoding="utf-8")


def test_day1_action_coverage_is_scoped() -> None:
    benchmark = _section("03_benchmark.tex")
    limitations = _section("08_limitations.tex")

    assert "current empirical matrix stresses the boundary between \\texttt{answer} and \\texttt{challenge}" in benchmark
    assert "\\texttt{ask} and hard \\texttt{abstain} cases are defined by the ontology" in benchmark
    assert "Claims about \\texttt{ask} and hard \\texttt{abstain} should therefore remain slice-scoped" in limitations
    assert "initial curated benchmark rather than a final large-scale evaluation" in limitations


def test_utility_is_presented_as_diagnostic_not_standalone() -> None:
    task = _section("02_task.tex")
    limitations = _section("08_limitations.tex")

    assert "asymmetric harm ordering, not a universal user-cost model" in task
    assert "never interpret utility alone" in task
    assert "claims should rest on agreement between the summary score and these disaggregated behaviors" in limitations
    assert "saved-output utility-weight sensitivity audits as claim guardrails" in limitations


def test_reasoning_model_claim_is_scoped_to_completed_protocol() -> None:
    results = _section("05_results.tex")
    limitations = _section("08_limitations.tex")

    assert "completed local model-and-prompt matrix" in results
    assert "under the current prompt protocol" in results
    assert "saved-output parse-sensitivity audits show that low-adherence rows are protocol-sensitive" in limitations
    assert "broader claims about reasoning models should remain scoped to this prompt and parsing setup" in limitations


def test_dataset_construction_transparency_is_visible() -> None:
    benchmark = _section("03_benchmark.tex")
    table = (PAPER_DIR / "tables" / "day1_dataset_slice_summary.tex").read_text(encoding="utf-8")

    required_fragments = [
        "synthetic-expansion rows are produced as seed candidates rather than directly as benchmark examples",
        "marked as not benchmark-facing until validation",
        "promoted only when the validation queue records \\texttt{human\\_decision=accept}",
        "duplicate identifiers, source tags, slice/action counts",
        "validated expansion candidates under an explicit audit trail",
        "canonical\\_560",
        "canonical submission split is the 560-example split",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in benchmark + "\n" + table]
    assert missing == []


def test_main_tables_avoid_internal_split_name_and_ison_typo() -> None:
    table_text = "\n".join(path.read_text(encoding="utf-8") for path in (PAPER_DIR / "tables").glob("*.tex"))

    assert "ISON" not in table_text
    assert "emnlp2026\\_expanded\\_dev\\_with\\_answer\\_topup" not in table_text


def test_slice_balanced_stress_split_is_not_canonicalized() -> None:
    results = _section("05_results.tex")
    limitations = _section("08_limitations.tex")
    table = (PAPER_DIR / "tables" / "day1_full_split_sensitivity.tex").read_text(encoding="utf-8")

    assert "600-example split as sensitivity evidence rather than as a replacement benchmark" in results
    assert "the headline remains the canonical 560-example split" in results
    assert "not a replacement headline benchmark" in table
    assert "The slice-balanced 600-example variant is a stress split, not the canonical benchmark" in limitations
    assert "Headline benchmark claims remain tied to the canonical 560-example split" in limitations


def test_confidence_intervals_are_not_overread_as_model_ranking() -> None:
    results = _section("05_results.tex")
    limitations = _section("08_limitations.tex")

    assert "coarse patterns from small rank differences" in results
    assert "not that every adjacent model difference is statistically separated" in results
    assert "uncertainty-qualified point estimates rather than as a fine-grained significance ranking" in results
    assert "local uncertainty checks over the current split samples" in limitations
    assert "guard against over-reading point estimates rather than as proof of a stable model ordering" in limitations


def test_intervention_claim_reports_answerability_guardrail() -> None:
    intervention = _section("06_intervention.tex")

    assert "does not come from sacrificing answer-supported behavior" in intervention
    assert "defective-premise accuracy rises" in intervention
    assert "This supports a narrow method claim" in intervention
