from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"


def _section(name: str) -> str:
    return (PAPER_DIR / "sections" / name).read_text(encoding="utf-8")


def test_day1_action_coverage_is_scoped() -> None:
    benchmark = _section("03_benchmark.tex")
    limitations = _section("08_limitations.tex")

    assert "Day-1 empirical matrix stresses the boundary between \\texttt{answer} and \\texttt{challenge}" in benchmark
    assert "\\texttt{ask} and hard \\texttt{abstain} cases are defined by the ontology" in benchmark
    assert "Claims about \\texttt{ask} and hard \\texttt{abstain} should therefore remain slice-scoped" in limitations


def test_utility_is_presented_as_diagnostic_not_standalone() -> None:
    task = _section("02_task.tex")
    limitations = _section("08_limitations.tex")

    assert "asymmetric harm ordering, not a universal user-cost model" in task
    assert "never interpret utility alone" in task
    assert "claims should rest on agreement between the summary score and these disaggregated behaviors" in limitations


def test_reasoning_model_claim_is_scoped_to_completed_protocol() -> None:
    results = _section("05_results.tex")
    limitations = _section("08_limitations.tex")

    assert "completed Day-1 model-and-prompt matrix" in results
    assert "under the current prompt protocol" in results
    assert "broader claims about reasoning models should remain scoped to this prompt and parsing setup" in limitations


def test_slice_balanced_stress_split_is_not_canonicalized() -> None:
    results = _section("05_results.tex")
    limitations = _section("08_limitations.tex")

    assert "600-example split as sensitivity evidence rather than as a replacement benchmark" in results
    assert "the headline remains the canonical 560-example split" in results
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
