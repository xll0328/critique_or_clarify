# Annotation Rubric

## Goal

This rubric exists to make the benchmark defensible.

We are not labeling whether a model output sounds reasonable. We are labeling the **assistant's next best action** under the action ontology in [action_ontology.md](/data/sony/emnlp2026_critique_or_clarify/docs/action_ontology.md).

## Annotation Unit

Each item contains:

- a user prompt
- optional retrieved passages
- optional metadata from the source dataset

Each item must receive:

- one gold action
- a short rationale
- optional gold answer or gold response
- a confidence tag
- an adjudication flag if disputed

## Mandatory Label Fields

For each example, annotators should fill:

| Field | Meaning |
| --- | --- |
| `gold_action` | One of `answer`, `ask`, `challenge`, `abstain` |
| `rationale` | One to three sentences explaining the label |
| `gold_answer` | Required for `answer` when a short supported answer exists |
| `gold_response` | Required for `ask`, `challenge`, or `abstain` when a canonical response is useful |
| `confidence` | `high`, `medium`, or `low` |
| `disputed` | `yes` if the example should be adjudicated |
| `notes` | Freeform comments on ambiguity or evidence quality |

## Core Label Rule

Always ask:

**What should a good assistant do next, before trying to be helpful through fluent continuation?**

This is an action-choice task, not a free-form response-quality task.

## Action Definitions

Use the definitions in [action_ontology.md](/data/sony/emnlp2026_critique_or_clarify/docs/action_ontology.md).

The short operational version is:

- `ask`: missing information the user can plausibly provide now
- `challenge`: false or stale premise that should be corrected
- `answer`: enough reliable support to answer directly
- `abstain`: insufficient or irreconcilable support that a follow-up question would not fix

## Annotation Procedure

### Step 1: Ignore Model Capability

Do not ask whether a frontier model could eventually rescue the query through clever inference.

Ask only what the assistant should do as its next move.

### Step 2: Run The Decision Tree

1. Is the request missing essential information the user can provide now?
   If yes, label `ask`.

2. If not, is the prompt built on a false or stale premise?
   If yes, label `challenge`.

3. If not, is there enough reliable evidence to answer?
   If yes, label `answer`.

4. Otherwise label `abstain`.

### Step 3: Write A Minimal Rationale

The rationale should point to the decisive issue:

- missing slot
- false premise
- stale premise
- conflicting evidence
- insufficient evidence
- enough reliable support

### Step 4: Mark Confidence

- `high`: the label is clear and likely robust
- `medium`: one nearby alternative exists but the best action is still defensible
- `low`: the example is borderline and should usually be reviewed

## Slice-Specific Guidance

### `underspecified_intent`

Prefer `ask` only if the user can plausibly resolve the ambiguity in one short reply.

Do not use `ask` as a hedge when the answer is already recoverable.

### `false_premise`

Prefer `challenge` when the prompt presupposes something incorrect and correcting it is the most helpful next move.

Even if the intended question is guessable, do not silently repair and label `answer`.

### `stale_premise`

Treat outdated assumptions the same way as false premises if the right next move is correction.

If the prompt includes a time condition that makes the older fact valid, then do not label `challenge`.

### `conflicting_evidence`

Conflicting retrieval alone does not imply `abstain`.

Use `answer` if one or more passages still provide enough reliable support.

Use `abstain` only when the conflict remains unresolved and no authoritative support is available.

## Boundary Cases

### `ask` vs `challenge`

If the main issue is that the user premise is wrong, choose `challenge`.

If the main issue is that the user has not specified enough information, choose `ask`.

Do not choose `ask` just to avoid correcting a false premise.

### `challenge` vs `abstain`

Choose `challenge` when the problem can be usefully corrected.

Choose `abstain` when the evidence is too weak or conflicting to support even the correction.

### `answer` vs `abstain`

If the evidence supports a concrete answer, label `answer` even if some noise exists.

If the evidence leaves the key fact unresolved, label `abstain`.

## Gold Response Expectations

### For `answer`

- short
- factual
- directly grounded in the evidence

### For `ask`

- one minimal follow-up if possible
- no broad conversational wandering

### For `challenge`

- explicitly state the false or stale premise
- give the correction when supported
- only continue beyond that if the continuation is clearly grounded

### For `abstain`

- briefly explain why the evidence is insufficient or unresolved
- do not speculate

## Exclusion Rules

Reject or defer examples that have any of these problems:

- the source itself is too broken to interpret
- the query requires specialized knowledge outside the available evidence and the intended label is unclear
- the example depends on unobservable conversational context
- the gold action depends mostly on style preference rather than utility

## Adjudication Protocol

### Pilot Round

Before large-scale conversion, annotate a diverse pilot set.

Recommended minimum:

- 15 examples per slice
- at least 60 examples total if four slices are active

### Independent Annotation

Each pilot example should be labeled independently by at least two annotators.

### Disagreement Handling

If annotators disagree on `gold_action`:

1. compare the decisive issue in each rationale
2. check the decision tree
3. revise the ontology or rubric if the disagreement exposes a systematic ambiguity
4. adjudicate the final label manually

Use [adjudication_protocol.md](/data/sony/emnlp2026_critique_or_clarify/docs/adjudication_protocol.md) for the actual adjudication record and keep-or-drop decision.

### Agreement Targets

Targets for moving forward:

- raw agreement on `gold_action` above `0.80`
- Cohen's kappa or Krippendorff-style agreement above `0.70`

If agreement stays below this, narrow the ontology or simplify the slices before scaling.

## Quality Gates

Do not scale a slice until:

1. at least 80 percent of pilot items are `high` or `medium` confidence
2. the main disagreement modes are documented
3. at least one adjudicator can explain the hard cases cleanly

## Known Failure Modes During Annotation

- overusing `ask` because it feels polite
- overusing `abstain` because conflict looks scary
- silently repairing false premises and calling them `answer`
- conflating response style with action choice
- treating one noisy passage as enough to force `abstain`

## Minimal Audit Form

Use the following fields during manual review:

| id | slice | proposed_action | final_action | confidence | disputed | decisive_issue | short_notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Day-0 Use

This week, use this rubric to:

1. audit 30 to 50 QACC examples
2. identify edge cases that QACC does not cover
3. prepare the premise-critique and stale-premise slices
