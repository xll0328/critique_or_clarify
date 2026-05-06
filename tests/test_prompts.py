from coc.prompts import build_messages, resolve_inline_protocol, resolve_system_prompt
from coc.schema import Action, Example


def test_decision_first_prompt_mentions_action_before_response() -> None:
    example = Example(
        id="ex1",
        prompt="Why did Marie Curie win the Nobel Prize in Literature?",
        passages=[],
        gold_action=Action.CHALLENGE,
        source="test",
    )

    messages = build_messages(example, style="decision_first")
    joined = "\n".join(message["content"] for message in messages)

    assert "decide" in resolve_system_prompt("decision_first").lower()
    assert "before drafting" in joined
    assert "action" in resolve_inline_protocol("decision_first")


def test_critique_first_prompt_mentions_premise_and_conflict_audit() -> None:
    example = Example(
        id="ex2",
        prompt="Which source is correct?",
        passages=["A says 1999.", "B says 2001."],
        gold_action=Action.ABSTAIN,
        source="test",
    )

    messages = build_messages(example, style="critique_first", include_system_prompt=False)
    joined = "\n".join(message["content"] for message in messages)

    assert "false, stale" in resolve_system_prompt("critique_first")
    assert "evidence conflicts" in joined
    assert "Prefer challenge over answer" in resolve_inline_protocol("critique_first")


def test_decision_first_guarded_prompt_preserves_conflict_boundary() -> None:
    example = Example(
        id="ex3",
        prompt="What county is Old Forge, New York in?",
        passages=["Old Forge is in Herkimer County.", "Old Forge is a hamlet in New York."],
        gold_action=Action.ANSWER,
        source="test",
    )

    messages = build_messages(example, style="decision_first_guarded", include_system_prompt=False)
    joined = "\n".join(message["content"] for message in messages)

    assert "not for merely missing passage support" in joined
    assert "Use challenge only" in resolve_inline_protocol("decision_first_guarded")
    assert "Answer if a supported answer is available" in resolve_system_prompt("decision_first_guarded")


def test_decision_first_balanced_prompt_keeps_rules_short() -> None:
    example = Example(
        id="ex4",
        prompt="Why is Facebook still trading under FB?",
        passages=["Meta changed its ticker from FB to META in 2022."],
        gold_action=Action.CHALLENGE,
        source="test",
    )

    messages = build_messages(example, style="decision_first_balanced")
    joined = "\n".join(message["content"] for message in messages)

    assert "Choose the action before" in resolve_system_prompt("decision_first_balanced")
    assert "Use `challenge` only" in joined
    assert "Use answer when" in resolve_inline_protocol("decision_first_balanced")
