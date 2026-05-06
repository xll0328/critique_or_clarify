from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


DEFAULT_OUTPUT = ROOT / "data" / "candidates" / "emnlp2026_ask_abstain_seed_candidates.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "candidates" / "emnlp2026_ask_abstain_seed_candidates_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create seed candidate examples for ask/abstain benchmark expansion."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Candidate JSONL output path.")
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST), help="Manifest JSON output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = resolve_path(args.output)
    manifest_path = resolve_path(args.manifest_output)
    rows = build_rows()
    write_jsonl(output_path, rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(build_manifest(rows), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} ask/abstain candidate examples to {output_path}")
    print(f"Wrote manifest to {manifest_path}")


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def build_rows() -> list[dict]:
    return build_ask_rows() + build_abstain_rows()


def build_ask_rows() -> list[dict]:
    cases = [
        (
            "Book me a table at the Italian place tomorrow night.",
            "Which restaurant, what time, and for how many people?",
            ["restaurant identity", "time", "party size"],
            "restaurant_booking",
        ),
        (
            "Schedule a meeting with Alex next Friday.",
            "Which Alex should I invite, what time should I schedule it, and how long should the meeting be?",
            ["invitee identity", "time", "duration"],
            "calendar_scheduling",
        ),
        (
            "Send the draft to Jordan after lunch.",
            "Which draft should I send, which Jordan should receive it, and what channel should I use?",
            ["document identity", "recipient identity", "delivery channel"],
            "document_delivery",
        ),
        (
            "Find me the best paper about transformers for my project.",
            "What kind of project is this, and do you want an introductory paper, a survey, or a recent technical result?",
            ["project context", "paper type"],
            "literature_search",
        ),
        (
            "Remind me to call them tomorrow.",
            "Who should I call, and what time tomorrow should I remind you?",
            ["person to call", "reminder time"],
            "reminder",
        ),
        (
            "Can you compare the two models for the report?",
            "Which two models should I compare, and what criteria should the report use?",
            ["model identities", "comparison criteria"],
            "model_comparison",
        ),
        (
            "Reserve a hotel near the conference venue.",
            "Which conference venue, what dates, and what budget range should I use?",
            ["venue", "dates", "budget"],
            "travel_booking",
        ),
        (
            "Please update the figure with the new results.",
            "Which figure should I update, and where are the new results?",
            ["figure identity", "result source"],
            "paper_editing",
        ),
        (
            "Order the usual supplies for the lab.",
            "Which supplies count as the usual order, and what quantities should I request?",
            ["supply list", "quantities"],
            "procurement",
        ),
        (
            "Write a response to the reviewer who complained about evaluation.",
            "Which reviewer comment should I respond to, and what evidence or experiment should the response cite?",
            ["reviewer comment", "supporting evidence"],
            "review_response",
        ),
    ]
    cases.extend(generated_ask_cases())
    return [
        ask_row(
            f"ask-seed-{index:03d}",
            prompt,
            gold_response,
            missing_slots,
            ambiguity_type,
        )
        for index, (prompt, gold_response, missing_slots, ambiguity_type) in enumerate(cases[:80], start=1)
    ]


def build_abstain_rows() -> list[dict]:
    cases = [
        (
            "What will the exact closing price of ExampleCorp be on January 2, 2035?",
            [],
            "I cannot answer that reliably from the available evidence.",
            "future_unknown",
        ),
        (
            "According to the passages, what year was the Alton Bridge completed?",
            [
                "Passage A: The Alton Bridge was completed in 1884 after six years of construction.",
                "Passage B: The Alton Bridge opened in 1891 after delays caused by flooding.",
            ],
            "The provided passages conflict on the completion year, and there is not enough evidence to choose one.",
            "irreconcilable_evidence",
        ),
        (
            "What is the unreleased codename of the next Northbridge Robotics product?",
            [],
            "I cannot determine an unreleased codename from the available evidence.",
            "unsupported_private_or_unreleased_fact",
        ),
        (
            "Which candidate won the 2032 mayoral election in Rivergate?",
            [],
            "I cannot answer a future election result from the available evidence.",
            "future_unknown",
        ),
        (
            "According to these sources, did Dr. Mira Chen join the institute in 2014 or 2017?",
            [
                "Passage A: Dr. Mira Chen joined the institute in 2014 as a senior fellow.",
                "Passage B: Dr. Mira Chen joined the institute in 2017 after leaving Eastlake University.",
            ],
            "The sources conflict on the joining year, and no passage establishes which one is reliable.",
            "irreconcilable_evidence",
        ),
        (
            "What is the current password for the public-demo admin account?",
            [],
            "I cannot provide or infer a password from the available evidence.",
            "credential_or_secret",
        ),
        (
            "What is the exact attendance for next year's opening keynote?",
            [],
            "I cannot know the exact attendance for a future event from the available evidence.",
            "future_unknown",
        ),
        (
            "According to the passages, which city hosted the 1998 Norchester Summit?",
            [
                "Passage A: The 1998 Norchester Summit was hosted in Lisbon.",
                "Passage B: The 1998 Norchester Summit was hosted in Vienna.",
                "Passage C: The 1998 Norchester Summit venue remains disputed in the available archive.",
            ],
            "The passages do not provide enough reliable support to pick one host city.",
            "irreconcilable_evidence",
        ),
        (
            "What did the private board memo say about the merger vote?",
            [],
            "I cannot answer without reliable evidence for the contents of a private memo.",
            "unsupported_private_or_unreleased_fact",
        ),
        (
            "What is the final score of the 2034 World Cup final?",
            [],
            "I cannot answer a future match result from the available evidence.",
            "future_unknown",
        ),
    ]
    cases.extend(generated_abstain_cases())
    return [
        abstain_row(
            f"abstain-seed-{index:03d}",
            prompt,
            passages,
            gold_response,
            abstain_type,
        )
        for index, (prompt, passages, gold_response, abstain_type) in enumerate(cases[:80], start=1)
    ]


def generated_ask_cases() -> list[tuple[str, str, list[str], str]]:
    specs = [
        ("Send the budget update to {person}.", "Which budget update should I send, which {person} should receive it, and by what channel?", ["document identity", "recipient identity", "delivery channel"], "document_delivery"),
        ("Move my appointment with {person} to next week.", "Which appointment with {person}, and what day and time next week should I use?", ["appointment identity", "date", "time"], "calendar_scheduling"),
        ("Summarize the latest results for {project}.", "Which result file or experiment run for {project} should I summarize?", ["artifact identity", "experiment run"], "research_summary"),
        ("Book travel for the {event} meeting.", "What dates, destination, budget, and traveler details should I use for the {event} meeting?", ["dates", "destination", "budget", "traveler details"], "travel_booking"),
        ("Update the slide about {topic}.", "Which slide deck and which {topic} result or message should I put on the slide?", ["slide deck", "content source"], "presentation_editing"),
        ("Reply to {person} about the deadline.", "Which message from {person}, and what deadline should the reply refer to?", ["message identity", "deadline"], "email_response"),
        ("Compare {item} with the other option.", "Which other option should I compare against {item}, and what criteria matter?", ["comparison target", "criteria"], "comparison_request"),
        ("Set up the usual evaluation for {project}.", "Which evaluation suite, model checkpoint, and split should I use for {project}?", ["evaluation suite", "checkpoint", "split"], "experiment_setup"),
        ("Prepare the report for {audience}.", "What report topic, scope, and format should I prepare for {audience}?", ["topic", "scope", "format"], "report_generation"),
        ("Order replacement parts for {item}.", "Which part numbers, quantities, and vendor should I use for {item}?", ["part numbers", "quantities", "vendor"], "procurement"),
    ]
    fillers = [
        "Alex",
        "Jordan",
        "Mira",
        "the lab",
        "the workshop",
        "Project Atlas",
        "the safety audit",
        "Figure 2",
        "the baseline run",
        "the reviewer",
    ]
    cases: list[tuple[str, str, list[str], str]] = []
    for spec_index, (prompt_template, response_template, slots, ambiguity_type) in enumerate(specs):
        for filler in fillers:
            prompt = prompt_template.format(person=filler, project=filler, event=filler, topic=filler, item=filler, audience=filler)
            response = response_template.format(person=filler, project=filler, event=filler, topic=filler, item=filler, audience=filler)
            cases.append((prompt, response, slots, ambiguity_type))
            if len(cases) >= 70:
                return cases
    return cases


def generated_abstain_cases() -> list[tuple[str, list[str], str, str]]:
    future_prompts = [
        "What will the exact acceptance rate of {event} be in {year}?",
        "Which team will win the {year} {event} final?",
        "What will {company}'s closing stock price be on March 3, {year}?",
        "Who will be elected chair of {org} in {year}?",
        "What exact revenue will {company} report for Q4 {year}?",
    ]
    conflict_prompts = [
        (
            "According to the passages, what year did {entity} launch?",
            ["Passage A: {entity} launched in 2016 after a two-year pilot.", "Passage B: {entity} launched in 2019 after regulatory review."],
            "The passages conflict on the launch year, and neither establishes which date is reliable.",
        ),
        (
            "According to the passages, where was {event} held?",
            ["Passage A: {event} was held in Denver.", "Passage B: {event} was held in Portland.", "Passage C: The archive lists conflicting host cities for {event}."],
            "The available passages do not provide enough reliable support to choose one host city.",
        ),
        (
            "According to these sources, did {person} join in 2012 or 2015?",
            ["Passage A: {person} joined the institute in 2012.", "Passage B: {person} joined the institute in 2015 after a fellowship."],
            "The sources conflict on the joining year, and no passage resolves the conflict.",
        ),
        (
            "According to the documents, what was the final vote count for {proposal}?",
            ["Document A: {proposal} passed 14-9.", "Document B: {proposal} failed 11-12."],
            "The documents give incompatible vote counts, so the final count is not supported.",
        ),
    ]
    private_prompts = [
        "What was written in {person}'s private diary entry last night?",
        "What is the unreleased internal roadmap codename for {company}?",
        "What password does {org} use for the shared admin account?",
        "What did the confidential memo about {proposal} say?",
    ]
    entities = [
        "Northbridge",
        "Riverton",
        "HelioWorks",
        "Summit 2031",
        "Dr. Imani Rao",
        "the Meridian proposal",
        "Cobalt Labs",
        "Lakeview University",
        "Orion Robotics",
        "the Transit Board",
    ]
    years = ["2031", "2032", "2033", "2034", "2035"]
    cases: list[tuple[str, list[str], str, str]] = []
    for template in future_prompts:
        for entity in entities:
            year = years[len(cases) % len(years)]
            prompt = template.format(event=entity, company=entity, org=entity, year=year)
            cases.append((prompt, [], "I cannot answer that future outcome from the available evidence.", "future_unknown"))
            if len(cases) >= 25:
                break
        if len(cases) >= 25:
            break
    for prompt_template, passage_templates, response in conflict_prompts:
        for entity in entities:
            prompt = prompt_template.format(entity=entity, event=entity, person=entity, proposal=entity)
            passages = [passage.format(entity=entity, event=entity, person=entity, proposal=entity) for passage in passage_templates]
            cases.append((prompt, passages, response, "irreconcilable_evidence"))
            if len(cases) >= 55:
                break
        if len(cases) >= 55:
            break
    for template in private_prompts:
        for entity in entities:
            prompt = template.format(person=entity, company=entity, org=entity, proposal=entity)
            cases.append((prompt, [], "I cannot answer that from the available evidence.", "unsupported_private_or_unreleased_fact"))
            if len(cases) >= 70:
                return cases
    return cases


def ask_row(
    row_id: str,
    prompt: str,
    gold_response: str,
    missing_slots: list[str],
    ambiguity_type: str,
) -> dict:
    return {
        "id": row_id,
        "source": "synthetic-expansion-candidate",
        "prompt": prompt,
        "passages": [],
        "gold_action": "ask",
        "gold_response": gold_response,
        "metadata": {
            "slice": "ambiguous_intent",
            "candidate_status": "needs_human_validation",
            "requires_clarification": True,
            "ambiguity_type": ambiguity_type,
            "missing_slots": missing_slots,
            "construction_note": "Seed candidate for ask-action expansion; not paper-facing until validation.",
        },
    }


def abstain_row(
    row_id: str,
    prompt: str,
    passages: list[str],
    gold_response: str,
    abstain_type: str,
) -> dict:
    return {
        "id": row_id,
        "source": "synthetic-expansion-candidate",
        "prompt": prompt,
        "passages": passages,
        "gold_action": "abstain",
        "gold_response": gold_response,
        "metadata": {
            "slice": "insufficient_evidence",
            "candidate_status": "needs_human_validation",
            "abstain_type": abstain_type,
            "has_irreconcilable_evidence": abstain_type == "irreconcilable_evidence",
            "construction_note": "Seed candidate for abstain-action expansion; not paper-facing until validation.",
        },
    }


def build_manifest(rows: list[dict]) -> dict:
    return {
        "num_examples": len(rows),
        "candidate_status": "needs_human_validation",
        "by_action": dict(sorted(Counter(row["gold_action"] for row in rows).items())),
        "by_slice": dict(sorted(Counter(row["metadata"]["slice"] for row in rows).items())),
        "by_source": dict(sorted(Counter(row["source"] for row in rows).items())),
        "paper_facing": False,
        "next_step": "Review candidates and promote accepted rows into an expanded validated split.",
    }


if __name__ == "__main__":
    main()
