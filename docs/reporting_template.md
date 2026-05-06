# Reporting Template

## Purpose

This document fixes the first reporting format before the experiments start.

The goal is to reduce result-shopping and make sure early findings are easy to compare.

## Primary Research Questions

### RQ1

Do strong open-source LLMs choose the correct action under defective inputs?

### RQ2

Do reasoning-style models over-answer more than instruct models?

### RQ3

Does the failure generalize across defect types rather than only one slice?

### RQ4

Can a lightweight decision-first intervention improve utility without hurting clean answerability?

## Main Table Template

Use one primary table early on.

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |

Notes:

- `Style` is usually `instruct` or `reasoning`
- `Answer EM` should be computed on the answerable subset
- `Over-Answer Rate` means the model answered when it should have asked, challenged, or abstained

## Slice Table Template

Always include a per-slice table.

| Model | Answerable | Ambiguous | False Premise | Stale Premise | Conflicting Evidence |
| --- | --- | --- | --- | --- | --- |
|  | utility / acc. | utility / acc. | utility / acc. | utility / acc. | utility / acc. |

If a slice does not exist yet, leave it out rather than filling a placeholder.

## Confusion Table Template

This table often explains the result better than one scalar metric.

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer |  |  |  |  |
| ask |  |  |  |  |
| challenge |  |  |  |  |
| abstain |  |  |  |  |

Early on, report one confusion matrix per flagship model.

## Qualitative Error Buckets

For every serious run, log examples into these buckets:

- answered despite missing slot information
- answered despite false premise
- answered despite unresolved evidence conflict
- challenged when a direct answer was enough
- abstained when a supported answer existed
- asked a vague follow-up instead of the minimal useful one

## Human Evaluation Template

If human evaluation is added, use three questions:

1. Was the selected action appropriate?
2. If the action was non-answer, was the response helpful?
3. If the model answered, was the answer adequately supported?

Keep human evaluation narrow and high quality rather than broad and noisy.

## Figure Plan

The first paper-facing figure should probably be:

- a grouped bar chart of `over-answer rate` by slice and model style

The second should be:

- a utility comparison plot for instruct vs reasoning families

Do not start with decorative plots.

## Claim Discipline

What we may claim early:

- models differ in action calibration
- reasoning can amplify over-answering
- some defect types are more stable than others

What we may not claim early:

- broad safety improvements
- general alignment gains
- agent robustness in the large

## Reporting Rules

Always report:

1. overall metrics
2. per-slice metrics
3. at least five qualitative failures
4. the exact prompt format
5. whether the result comes from a subset or full split

Never report:

- only the best-looking slice
- only one metric
- pooled results without slice context

## First Week Deliverables

By the end of the first serious week, the report should contain:

- one main result table
- one per-slice table
- one confusion matrix
- one short qualitative section
- one decision on whether the full project is oral-caliber, findings-caliber, or should pivot
