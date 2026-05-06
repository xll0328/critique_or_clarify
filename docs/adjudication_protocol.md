# Adjudication Protocol

## Purpose

This protocol turns manual review into a reproducible process instead of an informal discussion.

Use it whenever:

- two annotators disagree on the action
- an example has `low` confidence
- a slice shows systematic confusion between nearby actions

## What Counts As A Disagreement

A case must be adjudicated if any of the following happen:

- annotators disagree on `gold_action`
- annotators agree on the action but disagree on the decisive issue
- one annotator marks `low` confidence
- one annotator flags the example as unsuitable for the benchmark

## Inputs To Adjudication

Each disputed item should include:

- the prompt
- optional passages
- annotator A label and notes
- annotator B label and notes
- any source metadata that clarifies the intended setup

## Adjudication Questions

The adjudicator should answer these in order:

1. Is the main issue missing information, a false premise, or insufficient support?
2. Would a single user follow-up plausibly resolve the case?
3. Is the prompt itself incorrect or merely incomplete?
4. If the prompt were repaired, would the answer be supported?
5. Is this a good benchmark item, or is the case too muddy to keep?

## Allowed Outcomes

### Keep As Is

Use this when one annotator is clearly correct and the ontology already covers the case.

### Keep But Revise Notes

Use this when the label is stable but the rationale or gold response should be improved.

### Keep But Update Rubric

Use this when the item is valid but the disagreement reveals a systematic gap in the annotation rubric.

### Drop The Example

Use this when the case is too ambiguous, too source-dependent, or too style-sensitive to be a clean benchmark item.

## Adjudication Record Fields

For each disputed item, record:

| Field | Meaning |
| --- | --- |
| `id` | Example identifier |
| `annotator_a_action` | Action from annotator A |
| `annotator_b_action` | Action from annotator B |
| `adjudicated_action` | Final decision |
| `adjudication_status` | `kept`, `kept_revised`, `kept_rubric_update`, or `dropped` |
| `adjudicator_rationale` | Short explanation of the final decision |
| `rubric_issue` | The ontology or rubric gap exposed by the disagreement, if any |
| `final_confidence` | `high`, `medium`, or `low` |

## Quality Threshold

Do not scale a slice if adjudication repeatedly exposes the same unresolved boundary issue.

That means the ontology is not ready yet.

## First Week Rule

In the first week, prefer dropping borderline items over stretching the rubric.

A smaller clean benchmark is more valuable than a larger noisy one.
