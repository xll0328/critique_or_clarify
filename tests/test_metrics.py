from coc.metrics import evaluate_predictions
from coc.schema import Action, Example, Prediction


def test_evaluate_predictions_smoke_case() -> None:
    examples = [
        Example(
            id="ex1",
            prompt="Who wrote Pride and Prejudice?",
            passages=["Pride and Prejudice is a novel by Jane Austen."],
            gold_action=Action.ANSWER,
            gold_answer="Jane Austen",
            source="test",
        ),
        Example(
            id="ex2",
            prompt="Book me a table there tomorrow.",
            passages=[],
            gold_action=Action.ASK,
            gold_response="Which restaurant?",
            source="test",
        ),
    ]
    predictions = [
        Prediction(example_id="ex1", action=Action.ANSWER, response="Jane Austen"),
        Prediction(example_id="ex2", action=Action.ANSWER, response="Done"),
    ]

    summary, details = evaluate_predictions(examples, predictions)

    assert summary["num_examples"] == 2
    assert summary["action_accuracy"] == 0.5
    assert summary["answer_em"] == 1.0
    assert summary["answer_contains_rate"] == 1.0
    assert len(details) == 2


def test_answer_contains_recovers_short_gold_inside_sentence() -> None:
    examples = [
        Example(
            id="ex1",
            prompt="Who plays lucas mendoza in alexa and katie?",
            passages=[],
            gold_action=Action.ANSWER,
            gold_answer="Emery Kelly",
            source="test",
        )
    ]
    predictions = [
        Prediction(
            example_id="ex1",
            action=Action.ANSWER,
            response="Emery Kelly plays Lucas Mendoza in Alexa & Katie.",
        )
    ]

    summary, details = evaluate_predictions(examples, predictions)

    assert summary["answer_em"] == 0.0
    assert summary["answer_contains_rate"] == 1.0
    assert summary["per_slice"]["unknown"]["answer_contains_rate"] == 1.0
    assert details[0]["answer_exact_match"] is False
    assert details[0]["answer_contains_match"] is True
