from __future__ import annotations

import argparse
from datetime import date
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "docs" / "emnlp2026_oral_best_paper_quality_audit.md"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "emnlp2026_oral_best_paper_quality_audit.json"
DEFAULT_COVERAGE = ROOT / "experiments" / "emnlp2026" / "expanded_dev_with_answer_topup_coverage_audit.json"
DEFAULT_CANDIDATE_COVERAGE = ROOT / "experiments" / "emnlp2026" / "expanded_dev_with_answer_topup_coverage_audit.json"
DEFAULT_FULL_COVERAGE = ROOT / "experiments" / "emnlp2026" / "expanded_dev_with_full_answer_topup_coverage_audit.json"
DEFAULT_CANDIDATE_MANIFEST = ROOT / "data" / "processed" / "emnlp2026_expanded_dev_with_answer_topup_manifest.json"
DEFAULT_MAIN_TABLE = ROOT / "experiments" / "day1" / "tables" / "day1_scale_reasoning_main.tex"
DEFAULT_API_TABLE = ROOT / "experiments" / "day1" / "tables" / "day1_api_baseline_dev.tex"
DEFAULT_QWENPLUS_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_QWENPLUS_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_QWENPLUS_CANONICAL_GUARDED = (
    ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded_metrics.json"
)
DEFAULT_QWENPLUS_FULL_GUARDED = (
    ROOT / "outputs" / "day1" / "aihubmix_qwenpluslatest_day1_expanded_dev_with_full_answer_topup_decision_first_guarded_metrics.json"
)
DEFAULT_GPT41_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_GPT41_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_gpt41mini_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_QWENTURBO_CANONICAL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json"
DEFAULT_QWENTURBO_FULL_MAIN = ROOT / "outputs" / "day1" / "aihubmix_qwenturbo_day1_expanded_dev_with_full_answer_topup_metrics.json"
DEFAULT_GPT5CHAT_CANONICAL_MAIN = (
    ROOT / "outputs" / "day1" / "aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json"
)
DEFAULT_GPT5CHAT_FULL_MAIN = (
    ROOT / "outputs" / "day1" / "aihubmix_gpt5chatlatest_day1_expanded_dev_with_full_answer_topup_metrics.json"
)
DEFAULT_REFERENCES = ROOT / "paper" / "references.bib"
DEFAULT_SECTIONS = ROOT / "paper" / "sections"
DEFAULT_FIGURES = ROOT / "paper" / "figures"
DEFAULT_SENSITIVITY_TABLE = ROOT / "paper" / "tables" / "day1_full_split_sensitivity.tex"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit whether the current artifact looks like an EMNLP oral/best-paper candidate."
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD), help="Markdown audit output path.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="JSON audit output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload()
    output_md = resolve_path(args.output_md)
    output_json = resolve_path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    print(f"Wrote oral/best-paper quality audit to {relative_display(output_md)}")


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def relative_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_payload() -> dict[str, Any]:
    figures = sorted(DEFAULT_FIGURES.glob("*.pdf"))
    coverage = read_json(DEFAULT_COVERAGE)
    full_coverage = read_json(DEFAULT_FULL_COVERAGE)
    candidate_coverage = read_json(DEFAULT_CANDIDATE_COVERAGE)
    candidate_manifest = read_json(DEFAULT_CANDIDATE_MANIFEST)
    local_model_rows = parse_model_rows(DEFAULT_MAIN_TABLE)
    api_model_rows = parse_model_rows(DEFAULT_API_TABLE)
    combined_model_rows = dedupe_preserve_order(local_model_rows + api_model_rows)
    reference_text = DEFAULT_REFERENCES.read_text(encoding="utf-8") if DEFAULT_REFERENCES.exists() else ""
    section_texts = [
        path.read_text(encoding="utf-8")
        for path in sorted(DEFAULT_SECTIONS.glob("*.tex"))
        if path.name != "00_abstract.tex"
    ]
    citation_commands_by_section = {
        path.name: path.read_text(encoding="utf-8").count("\\cite")
        for path in sorted(DEFAULT_SECTIONS.glob("*.tex"))
    }
    paper_facing = coverage.get("combined_unique", {})
    full_split = full_coverage.get("combined_unique", {})
    candidate_combined = candidate_coverage.get("combined_unique", {})
    targets = coverage.get("targets", {})
    gaps = coverage.get("gaps", {})
    full_gaps = full_coverage.get("gaps", {})
    qwenplus_stress = build_qwenplus_stress_summary(
        canonical_main=read_metric_summary(DEFAULT_QWENPLUS_CANONICAL_MAIN),
        full_main=read_metric_summary(DEFAULT_QWENPLUS_FULL_MAIN),
        canonical_guarded=read_metric_summary(DEFAULT_QWENPLUS_CANONICAL_GUARDED),
        full_guarded=read_metric_summary(DEFAULT_QWENPLUS_FULL_GUARDED),
    )
    gpt41_stress_main = build_pair_summary(
        read_metric_summary(DEFAULT_GPT41_CANONICAL_MAIN),
        read_metric_summary(DEFAULT_GPT41_FULL_MAIN),
    )
    qwenturbo_stress_main = build_pair_summary(
        read_metric_summary(DEFAULT_QWENTURBO_CANONICAL_MAIN),
        read_metric_summary(DEFAULT_QWENTURBO_FULL_MAIN),
    )
    gpt5chat_stress_main = build_pair_summary(
        read_metric_summary(DEFAULT_GPT5CHAT_CANONICAL_MAIN),
        read_metric_summary(DEFAULT_GPT5CHAT_FULL_MAIN),
    )
    full_split_stress_model_count = 1 if qwenplus_stress.get("main", {}).get("available") else 0
    if gpt41_stress_main.get("available"):
        full_split_stress_model_count += 1
    if qwenturbo_stress_main.get("available"):
        full_split_stress_model_count += 1
    if gpt5chat_stress_main.get("available"):
        full_split_stress_model_count += 1

    metrics = {
        "paper_facing_unique_examples": paper_facing.get("unique_examples", 0),
        "paper_facing_action_counts": paper_facing.get("by_action", {}),
        "full_split_unique_examples": full_split.get("unique_examples", 0),
        "full_split_action_counts": full_split.get("by_action", {}),
        "candidate_augmented_unique_examples": candidate_combined.get("unique_examples", 0),
        "candidate_augmented_action_counts": candidate_combined.get("by_action", {}),
        "oral_target_unique_examples": targets.get("total_unique", 0),
        "paper_facing_unique_gap": gaps.get("total_unique", {}).get("gap", 0),
        "candidate_paper_facing": candidate_manifest.get("paper_facing"),
        "candidate_status": (
            candidate_manifest.get("candidate_status")
            or ("accepted" if candidate_manifest.get("paper_facing", False) else "needs_human_validation")
        ),
        "slice_gaps": gaps.get("by_slice", {}),
        "full_split_slice_gaps": full_gaps.get("by_slice", {}),
        "model_rows": len(combined_model_rows),
        "model_rows_local": len(local_model_rows),
        "model_rows_api": len(api_model_rows),
        "model_names": combined_model_rows,
        "model_names_local": local_model_rows,
        "model_names_api": api_model_rows,
        "figure_count": len(figures),
        "figure_files": [relative_display(path) for path in figures],
        "bib_entries": len(re.findall(r"(?m)^@", reference_text)),
        "citation_commands": sum(text.count("\\cite") for text in section_texts),
        "citation_commands_by_section": citation_commands_by_section,
        "qwenplus_stress": qwenplus_stress,
        "gpt41_stress_main": gpt41_stress_main,
        "qwenturbo_stress_main": qwenturbo_stress_main,
        "gpt5chat_stress_main": gpt5chat_stress_main,
        "full_split_stress_model_count": full_split_stress_model_count,
        "sensitivity_table_present": DEFAULT_SENSITIVITY_TABLE.exists(),
    }
    findings = build_findings(metrics)
    return {
        "date": date.today().isoformat(),
        "status": "not_oral_ready",
        "recommendation": "major_revision_before_oral_or_best_paper_claim",
        "metrics": metrics,
        "findings": findings,
        "next_actions": build_next_actions(metrics),
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_metric_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    return summary if isinstance(summary, dict) else {}


def parse_model_rows(path: Path) -> list[str]:
    if not path.exists():
        return []
    rows: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if "&" not in line or "\\\\" not in line or line.startswith("\\"):
            continue
        model_name = line.split("&", 1)[0].strip()
        if model_name and model_name != "Model":
            rows.append(model_name)
    return rows


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def delta(full_value: Any, canonical_value: Any) -> float:
    try:
        return float(full_value) - float(canonical_value)
    except (TypeError, ValueError):
        return 0.0


def build_pair_summary(canonical: dict[str, Any], full: dict[str, Any]) -> dict[str, Any]:
    if not canonical or not full:
        return {"available": False}
    return {
        "available": True,
        "canonical_examples": canonical.get("num_examples"),
        "full_examples": full.get("num_examples"),
        "canonical_action_accuracy": canonical.get("action_accuracy"),
        "full_action_accuracy": full.get("action_accuracy"),
        "delta_action_accuracy": delta(full.get("action_accuracy"), canonical.get("action_accuracy")),
        "canonical_avg_utility": canonical.get("avg_utility"),
        "full_avg_utility": full.get("avg_utility"),
        "delta_avg_utility": delta(full.get("avg_utility"), canonical.get("avg_utility")),
        "canonical_over_answer_rate": canonical.get("over_answer_rate"),
        "full_over_answer_rate": full.get("over_answer_rate"),
        "delta_over_answer_rate": delta(full.get("over_answer_rate"), canonical.get("over_answer_rate")),
        "canonical_json_parse_rate": canonical.get("json_parse_rate"),
        "full_json_parse_rate": full.get("json_parse_rate"),
        "delta_json_parse_rate": delta(full.get("json_parse_rate"), canonical.get("json_parse_rate")),
    }


def build_qwenplus_stress_summary(
    *,
    canonical_main: dict[str, Any],
    full_main: dict[str, Any],
    canonical_guarded: dict[str, Any],
    full_guarded: dict[str, Any],
) -> dict[str, Any]:
    return {
        "main": build_pair_summary(canonical_main, full_main),
        "decision_first_guarded": build_pair_summary(canonical_guarded, full_guarded),
    }


def build_findings(metrics: dict[str, Any]) -> list[dict[str, str]]:
    findings = []
    if metrics["paper_facing_unique_examples"] < 500:
        findings.append(
            finding(
                "CRITICAL",
                "paper_facing_evidence_scale",
                f"Paper-facing coverage is {metrics['paper_facing_unique_examples']} unique examples, "
                f"leaving a {metrics['paper_facing_unique_gap']} example gap to the 500-example oral target.",
                "Complete the expanded split and validation loop before claiming a broad benchmark release.",
            )
        )
    action_counts = metrics["paper_facing_action_counts"]
    if action_counts.get("ask", 0) == 0 or action_counts.get("abstain", 0) == 0:
        findings.append(
            finding(
                "CRITICAL",
                "missing_validated_actions",
                "The paper-facing split still has ask=0 and abstain=0; current ask/abstain rows are pending candidates.",
                "Validate and promote accepted ambiguous-intent and insufficient-evidence rows before expanding model claims.",
            )
        )
    if metrics["model_rows"] < 8:
        findings.append(
            finding(
                "MAJOR",
                "model_matrix_too_narrow",
                f"The combined local+API matrix has {metrics['model_rows']} model rows (local={metrics['model_rows_local']}, api={metrics['model_rows_api']}); this is credible for a pilot but thin for oral-level empirical breadth.",
                "Add at least one stronger non-reasoning instruction model, one stronger reasoning model, and one API/frontier reference if allowed.",
            )
        )
    if metrics["model_rows_api"] < 4:
        findings.append(
            finding(
                "MAJOR",
                "frontier_api_coverage_thin",
                f"Only {metrics['model_rows_api']} API/frontier rows are present in the paper-facing table.",
                "Add at least one additional strong API/frontier control and report it under the same protocol.",
            )
        )
    if metrics["figure_count"] < 4:
        findings.append(
            finding(
                "MAJOR",
                "visual_story_too_sparse",
                f"The paper has {metrics['figure_count']} paper-facing PDF figures.",
                "Add a richer motivated example figure, an ontology/boundary matrix, and an expanded per-slice result figure.",
            )
        )
    if metrics["bib_entries"] < 25:
        findings.append(
            finding(
                "MAJOR",
                "related_work_too_thin",
                f"The bibliography has {metrics['bib_entries']} entries and {metrics['citation_commands']} citation commands.",
                "Broaden close-work coverage for clarification, abstention/selective prediction, truthfulness, temporal QA, RAG conflict, calibration, and refusal/safety evaluation.",
            )
        )
    elif metrics["bib_entries"] < 35:
        findings.append(
            finding(
                "MINOR",
                "bibliography_oral_headroom",
                f"The bibliography has {metrics['bib_entries']} entries; this is acceptable for submission but still below typical oral-level breadth.",
                "Expand to roughly 35-40 tightly relevant entries, with citations anchored in Introduction/Task/Results and not only Related Work.",
            )
        )
    if metrics["citation_commands_by_section"].get("01_introduction.tex", 0) < 2:
        findings.append(
            finding(
                "MAJOR",
                "introduction_under_cited",
                "Introduction has fewer than two citation commands, making the motivation and scope easy to challenge in review.",
                "Add targeted citations in Introduction for ambiguity, premise defects, and retrieval-conflict framing claims.",
            )
        )
    section_cites = metrics["citation_commands_by_section"]
    non_related_cites = sum(
        count for section, count in section_cites.items() if section not in {"02_related_work.tex"}
    )
    if non_related_cites <= 1:
        findings.append(
            finding(
                "MINOR",
                "citations_overconcentrated",
                "Almost all citations are in Related Work; the task, benchmark, and metric sections read under-grounded.",
                "Add targeted citations near the claims they support, especially utility/action calibration and benchmark construction.",
            )
        )
    slice_gaps = metrics.get("slice_gaps", {})
    high_gaps = [name for name, payload in slice_gaps.items() if int(payload.get("gap", 0)) > 0]
    if high_gaps:
        detail = ", ".join(
            f"{name} gap={slice_gaps[name]['gap']}" for name in sorted(high_gaps)
        )
        full_slice_gaps = metrics.get("full_split_slice_gaps", {})
        full_high_gaps = [name for name, payload in full_slice_gaps.items() if int(payload.get("gap", 0)) > 0]
        qwenplus_stress = metrics.get("qwenplus_stress", {})
        main_stress = qwenplus_stress.get("main", {})
        guarded_stress = qwenplus_stress.get("decision_first_guarded", {})
        gpt41_stress_main = metrics.get("gpt41_stress_main", {})
        qwenturbo_stress_main = metrics.get("qwenturbo_stress_main", {})
        gpt5chat_stress_main = metrics.get("gpt5chat_stress_main", {})
        if not full_high_gaps and main_stress.get("available") and guarded_stress.get("available"):
            extras = []
            if gpt41_stress_main.get("available"):
                extras.append(
                    f"gpt-4.1-mini decision-first Δaction={gpt41_stress_main['delta_action_accuracy']:+.4f}"
                )
            if qwenturbo_stress_main.get("available"):
                extras.append(
                    f"qwen-turbo decision-first Δaction={qwenturbo_stress_main['delta_action_accuracy']:+.4f}"
                )
            if gpt5chat_stress_main.get("available"):
                extras.append(
                    f"gpt-5-chat-latest decision-first Δaction={gpt5chat_stress_main['delta_action_accuracy']:+.4f}"
                )
            extra = f" Additional stress rows: {', '.join(extras)}." if extras else ""
            findings.append(
                finding(
                    "MINOR",
                    "slice_balance_scope_canonical_only",
                    f"Canonical split still has unresolved slice gaps ({detail}), but a slice-balanced 600-example stress split is available and evaluated (qwen-plus-latest main Δaction={main_stress['delta_action_accuracy']:+.4f}, guarded Δaction={guarded_stress['delta_action_accuracy']:+.4f}).{extra}",
                    "Keep headline claims scoped to the canonical split and report full-split sensitivity as stress evidence, not as a replacement benchmark.",
                )
            )
        else:
            findings.append(
                finding(
                    "MAJOR",
                    "slice_balance_risk",
                    f"Canonical split still has unresolved slice gaps: {detail}.",
                    "Close slice gaps (especially answerable_control and conflicting_evidence) before making slice-universal conclusions.",
                )
            )
    return findings


def finding(severity: str, key: str, evidence: str, action: str) -> dict[str, str]:
    return {"severity": severity, "key": key, "evidence": evidence, "action": action}


def build_next_actions(metrics: dict[str, Any]) -> list[str]:
    gpt5chat_stress_main = metrics.get("gpt5chat_stress_main", {})
    if metrics.get("model_rows_api", 0) >= 5 and gpt5chat_stress_main.get("available"):
        actions = [
            "Use the completed GPT-5-chat-latest row as the strong API/frontier control; do not broaden the model matrix further unless it answers a specific reviewer objection.",
            "Keep the full-split sensitivity claims CI-aware: the delta intervals overlap zero, so report the 600-example split as stress evidence rather than a stronger replacement benchmark.",
        ]
    else:
        actions = [
            "Run at least one additional strong API/frontier control and keep the same prompt/decoding protocol for comparability.",
            "Propagate CI/error bars into all headline delta figures and keep claim text uncertainty-aware.",
        ]
    if metrics["bib_entries"] < 35:
        actions.insert(
            1,
            f"Expand bibliography from {metrics['bib_entries']} entries toward 35-40 tightly relevant entries with citations distributed outside Related Work.",
        )
    elif metrics["bib_entries"] < 40:
        actions.insert(
            1,
            f"Bibliography breadth now meets the 35-entry oral threshold; only add more citations if they support a concrete claim not already covered.",
        )
    slice_gaps = metrics.get("slice_gaps", {})
    high_gaps = [name for name, payload in slice_gaps.items() if int(payload.get("gap", 0)) > 0]
    full_slice_gaps = metrics.get("full_split_slice_gaps", {})
    full_high_gaps = [name for name, payload in full_slice_gaps.items() if int(payload.get("gap", 0)) > 0]
    qwenplus_stress = metrics.get("qwenplus_stress", {})
    main_stress = qwenplus_stress.get("main", {})
    guarded_stress = qwenplus_stress.get("decision_first_guarded", {})
    full_split_stress_model_count = int(metrics.get("full_split_stress_model_count", 0))
    sensitivity_table_present = bool(metrics.get("sensitivity_table_present"))
    if high_gaps and (not full_high_gaps) and main_stress.get("available") and guarded_stress.get("available"):
        if sensitivity_table_present:
            if full_split_stress_model_count < 2:
                actions.insert(
                    1,
                    "Run at least one additional frontier/API model on the 600-example split to confirm the sensitivity pattern is not qwen-plus-only.",
                )
            elif full_split_stress_model_count < 3:
                actions.insert(
                    1,
                    "Add one lower-cost API row on the 600-example split to triangulate high/medium/low frontier behavior under slice-balanced stress.",
                )
            else:
                stress_scope = "frontier/high/medium/low" if gpt5chat_stress_main.get("available") else "high/medium/low"
                actions.insert(
                    1,
                    f"Keep the 600-example split framed as stress evidence: {stress_scope} API rows now triangulate slice-balance sensitivity, but the canonical 560 remains the headline benchmark.",
                )
        else:
            actions.insert(
                1,
                "Add a compact sensitivity table (canonical 560 vs full 600) and explicitly mark the 600 split as stress evidence.",
            )
    elif high_gaps:
        actions.insert(
            1,
            "Close remaining slice gaps in the canonical split before upgrading per-slice claims.",
        )
    return actions


def render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    findings = payload["findings"]
    stress = metrics.get("qwenplus_stress", {})
    main_stress = stress.get("main", {})
    guarded_stress = stress.get("decision_first_guarded", {})
    gpt41_stress_main = metrics.get("gpt41_stress_main", {})
    qwenturbo_stress_main = metrics.get("qwenturbo_stress_main", {})
    gpt5chat_stress_main = metrics.get("gpt5chat_stress_main", {})
    lines = [
        "# EMNLP 2026 Oral / Best Paper Quality Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: not oral-ready. The current artifact is a credible submission-freeze candidate, but it is not yet an oral/best-paper-grade evidence package.",
        "",
        "## Scorecard",
        "",
        f"- Paper-facing unique examples: `{metrics['paper_facing_unique_examples']}` / `{metrics['oral_target_unique_examples']}`",
        f"- Slice-balanced stress split: `{metrics['full_split_unique_examples']}`",
        f"- Candidate-augmented unique examples: `{metrics['candidate_augmented_unique_examples']}`",
        f"- Paper-facing actions: `{format_counts(metrics['paper_facing_action_counts'])}`",
        f"- Stress split actions: `{format_counts(metrics['full_split_action_counts'])}`",
        f"- Candidate-augmented actions: `{format_counts(metrics['candidate_augmented_action_counts'])}`",
        f"- Candidate status: `{metrics['candidate_status']}`, paper-facing: `{metrics['candidate_paper_facing']}`",
        f"- Main model rows: `{metrics['model_rows']}` (local `{metrics['model_rows_local']}`, API `{metrics['model_rows_api']}`)",
        f"- Paper-facing figures: `{metrics['figure_count']}`",
        f"- Bibliography entries: `{metrics['bib_entries']}`",
        f"- Citation commands: `{metrics['citation_commands']}`",
    ]
    if main_stress.get("available"):
        lines.append(
            f"- Qwen-plus-latest (main) 600-vs-560 delta: `Δaction={main_stress['delta_action_accuracy']:+.4f}`, `Δutility={main_stress['delta_avg_utility']:+.4f}`"
        )
    if guarded_stress.get("available"):
        lines.append(
            f"- Qwen-plus-latest (guarded) 600-vs-560 delta: `Δaction={guarded_stress['delta_action_accuracy']:+.4f}`, `Δutility={guarded_stress['delta_avg_utility']:+.4f}`"
        )
    if gpt41_stress_main.get("available"):
        lines.append(
            f"- GPT-4.1-mini (decision-first) 600-vs-560 delta: `Δaction={gpt41_stress_main['delta_action_accuracy']:+.4f}`, `Δutility={gpt41_stress_main['delta_avg_utility']:+.4f}`"
        )
    if qwenturbo_stress_main.get("available"):
        lines.append(
            f"- Qwen-turbo (decision-first) 600-vs-560 delta: `Δaction={qwenturbo_stress_main['delta_action_accuracy']:+.4f}`, `Δutility={qwenturbo_stress_main['delta_avg_utility']:+.4f}`"
        )
    if gpt5chat_stress_main.get("available"):
        lines.append(
            f"- GPT-5-chat-latest (decision-first) 600-vs-560 delta: `Δaction={gpt5chat_stress_main['delta_action_accuracy']:+.4f}`, `Δutility={gpt5chat_stress_main['delta_avg_utility']:+.4f}`"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Severity | Finding | Evidence | Required Action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in findings:
        lines.append(
            f"| `{item['severity']}` | `{item['key']}` | {item['evidence']} | {item['action']} |"
        )
    lines.extend(
        [
            "",
            "## Top Actions",
            "",
        ]
    )
    for index, action in enumerate(payload["next_actions"], start=1):
        lines.append(f"{index}. {action}")
    lines.append("")
    return "\n".join(lines)


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


if __name__ == "__main__":
    main()
