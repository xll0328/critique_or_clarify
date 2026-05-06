from coc.backends import parse_prediction
from coc.schema import Action


def test_parse_prediction_uses_final_response_after_think_block_for_answer() -> None:
    prediction = parse_prediction(
        "</think>\n\nMaria Canals-Barrera played Theresa Russo, the mom on Wizards of Waverly Place.",
        "ex1",
    )

    assert prediction.action == Action.ANSWER
    assert prediction.metadata["parsed_as"] == "fallback"


def test_parse_prediction_uses_final_response_after_think_block_for_ask() -> None:
    prediction = parse_prediction(
        "</think>\n\nCould you clarify which season you mean?",
        "ex2",
    )

    assert prediction.action == Action.ASK


def test_parse_prediction_prefers_explicit_challenge_cues_in_final_response() -> None:
    prediction = parse_prediction(
        "</think>\n\nThat premise is incorrect: the bag cannot have both 36 and 24 cookies.",
        "ex3",
    )

    assert prediction.action == Action.CHALLENGE


def test_parse_prediction_prefers_explicit_abstain_cues_in_final_response() -> None:
    prediction = parse_prediction(
        "</think>\n\nI cannot determine the answer from the provided evidence.",
        "ex4",
    )

    assert prediction.action == Action.ABSTAIN


def test_parse_prediction_uses_explicit_action_declaration_before_question_words() -> None:
    prediction = parse_prediction(
        (
            'The query is "Which artist is representative of the Detroit blues style?" '
            "The premise is acceptable and the query is answerable, so I should use the "
            '"answer" action.'
        ),
        "ex5",
    )

    assert prediction.action == Action.ANSWER


def test_parse_prediction_response_uses_final_response_after_think_block() -> None:
    prediction = parse_prediction(
        "</think>\n\nMaria Canals-Barrera played Theresa Russo.",
        "ex6",
    )

    assert prediction.response == "Maria Canals-Barrera played Theresa Russo."


def test_parse_prediction_treats_follow_up_question_tail_as_ask() -> None:
    prediction = parse_prediction(
        "</think>\n\nThe query is underspecified and a follow-up question is",
        "ex7",
    )

    assert prediction.action == Action.ASK
