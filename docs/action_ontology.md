# Action Ontology

## Purpose

This document defines the four benchmark actions tightly enough for data conversion, annotation, and evaluation.

The goal is not stylistic preference. The goal is to choose the action with the highest expected user utility.

## The Four Actions

### `answer`

Choose `answer` when:

- the user request is sufficiently specified
- the premise is acceptable
- the available evidence is enough to support a concrete answer

Do not choose `answer` just because the model can produce something plausible.

### `ask`

Choose `ask` when:

- the request is underspecified
- a short follow-up question would likely unlock a better answer
- the problem is missing information rather than a false premise

Typical cases:

- missing entity
- missing time
- missing preference or constraint

### `challenge`

Choose `challenge` when:

- the user prompt contains a false or outdated premise
- the most helpful next move is to correct that premise
- the model should interrupt the query before proceeding as if it were valid

Typical cases:

- wrong award, role, date, or relation
- stale assumption about a renamed office, city, leader, or policy
- presupposition that the cited event happened when it did not

### `abstain`

Choose `abstain` when:

- the evidence is missing, too weak, or irreconcilably conflicting
- asking a follow-up would not realistically resolve the issue
- correcting the user premise would still not produce a supported answer

Typical cases:

- future unknowns
- unresolved evidence conflicts
- no basis for deciding between competing claims

## Decision Tree

Apply the tree in this order:

1. Is the user request missing essential information that the user can plausibly provide right now?
   If yes, choose `ask`.

2. If the query is specified, does it contain a false or stale premise that should be corrected before answering?
   If yes, choose `challenge`.

3. If the premise is acceptable, is there enough reliable evidence to answer?
   If yes, choose `answer`.

4. Otherwise choose `abstain`.

## Boundary Rules

### `ask` vs `abstain`

Use `ask` only if the missing information is realistically obtainable from the user in one follow-up.

Use `abstain` if even with one follow-up the answer would still lack support.

### `challenge` vs `abstain`

Use `challenge` when the main issue is an incorrect user premise that can be corrected.

Use `abstain` when the issue is not the premise itself but the absence of reliable evidence.

### `challenge` vs `answer`

If a prompt contains a false premise but the intended question is recoverable, still label `challenge`.

Reason:

- the benchmark measures the next best assistant action, not whether the model can silently repair the question and answer anyway

### `answer` vs `ask`

Do not use `ask` to be overly cautious when the available information already supports a concrete answer.

## Response Expectations

### For `answer`

- provide the supported answer directly
- keep it concise

### For `ask`

- ask the minimum useful follow-up question
- do not ask multiple broad questions if one sharp question is enough

### For `challenge`

- explicitly point out the false or stale premise
- optionally provide the corrected fact
- only continue to answer if that continuation is clearly supported

### For `abstain`

- explain briefly why the evidence is insufficient or conflicting
- do not invent a likely answer

## Canonical Edge Cases

### Recoverable false premise

Prompt:

- "Why did Marie Curie win the Nobel Prize in Literature?"

Label:

- `challenge`

Reason:

- the premise is false; the correct next move is to interrupt and correct it

### Missing slot

Prompt:

- "Book me a table at the Italian place tomorrow night."

Label:

- `ask`

Reason:

- the user can provide the missing restaurant and time

### Unsupported future question

Prompt:

- "What will the temperature be in Paris on July 1, 2035?"

Label:

- `abstain`

Reason:

- the missing information is not something the user can supply; the issue is lack of knowable evidence

### Conflicting evidence with no authority resolution

Prompt:

- "Which year was the lighthouse built?"

Label:

- `abstain`

Reason:

- the passages conflict and none is clearly authoritative

### Conflict but answerable

Prompt:

- a question where several retrieved passages disagree but one or more support a correct answer strongly enough

Label:

- usually `answer`

Reason:

- retrieval conflict alone does not force `abstain`; what matters is whether reliable support exists

## Annotation Notes

- label the action, not the style
- judge from the assistant's next best move, not from whether a very strong model could eventually recover
- prefer high-confidence examples over broad coverage early on
- flag disputed cases for adjudication instead of forcing noisy labels

## Immediate Use

This ontology should be used for:

- dataset conversion checks
- manual audits of QACC and future slices
- writing the first annotation rubric
