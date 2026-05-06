# Day-0 Plan

## Today's Objective

Do not optimize for experiment count.

Optimize for a clean start:

1. a precise scientific claim
2. a stable action ontology
3. one real dataset slice in the shared schema
4. one credible baseline path
5. explicit kill criteria

## Working Claim

Modern LLMs are trained to continue answering, but assistant usefulness depends on first deciding whether a defective query should be answered, clarified, challenged, or left unresolved.

## Day-0 Deliverables

1. Freeze the project framing in [research_master_plan.md](/data/sony/emnlp2026_critique_or_clarify/docs/research_master_plan.md).
2. Keep the four-action schema, but write down the boundary cases that could force a later narrowing in [action_ontology.md](/data/sony/emnlp2026_critique_or_clarify/docs/action_ontology.md).
3. Finish one real slice conversion: QACC is already the first one.
4. Lock the annotation process in [annotation_rubric.md](/data/sony/emnlp2026_critique_or_clarify/docs/annotation_rubric.md).
5. Prepare the second slice path: premise critique.
6. Define the first model matrix in [initial_model_matrix.md](/data/sony/emnlp2026_critique_or_clarify/docs/initial_model_matrix.md) rather than running a broad sweep.

## Day-0 Non-Goals

- no large training run
- no giant benchmark assembly
- no method paper claims yet
- no scaling to every model we can access

## Exact Tasks For Today

1. Audit 30 to 50 QACC examples manually.
2. Draft the action decision tree and annotation rubric.
3. Identify whether the full four-action framing is stable enough to keep.
4. Pick the first two open models for a controlled dev run.
5. Freeze the first reporting format in [reporting_template.md](/data/sony/emnlp2026_critique_or_clarify/docs/reporting_template.md).

## First Model Matrix

Start with:

1. one strong instruct model
2. one reasoning-style model

Do not add more until the first qualitative failure analysis is complete.

## Minimal Success Criteria For Today

- the plan is clear enough to explain in one paragraph
- the benchmark task boundaries are not hand-wavy
- at least one real dataset slice is ready
- the first baseline comparison is fully specified
