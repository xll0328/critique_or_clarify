# Research Master Plan

## North Star

This project should not be framed as "a benchmark that mixes several failure modes."

It should be framed as:

**LLMs are optimized to continue answering, but real assistants must first choose the right conversational repair action when the input itself is defective.**

The paper-worthy version of the project is therefore:

- a **unified decision problem**: answer vs ask vs challenge vs abstain
- under **defective inputs**: ambiguity, false premise, stale premise, conflicting evidence
- with a **clear empirical claim**: stronger reasoning does not automatically imply better action calibration, and may worsen over-answering
- plus an optional **lightweight intervention** only if the benchmark signal is strong

## One-Sentence Story

Modern LLMs are good at generating answers, but poor at deciding when the user query should be repaired before answering.

## First Impression

Category:

- `New Setting` with a possible `Novel Method` follow-up

What makes it interesting is not any single slice. The interesting part is turning several fragmented failure modes into one assistant-centric decision problem.

## Fatal-Flaw Audit

### `MAJOR`: Benchmark soup risk

If this becomes "QACC + PCBench + some stale questions + some ambiguous prompts," the work will look assembled rather than designed.

Mitigation:

- define one task formally before adding more data
- write a strict action ontology and annotation rubric
- treat each dataset as one slice of the same decision problem, not as separate mini-tasks

### `MAJOR`: Label-boundary risk

The line between `ask`, `challenge`, and `abstain` can become subjective. If annotators disagree, the paper weakens quickly.

Mitigation:

- define the action choice by expected user utility, not style
- create a decision tree with canonical edge cases
- measure agreement early on a small but diverse set before scaling

## Capability And Lifecycle Fit

Fit: `Green`

Why:

- 4x4090 is enough for the core phase because the early value comes from evaluation, controlled data curation, and lightweight policy tuning
- the project can produce publishable signal before any large training run
- the scope can be narrowed aggressively if a slice underperforms

What would make it turn `Yellow`:

- trying to build a giant benchmark and a full new training pipeline at the same time
- trying to beat frontier models with scale rather than with task design

## Five-Dimension Score

| Dimension | Score | Why |
| --- | --- | --- |
| Higher | 7/10 | Potentially strong gains in action utility and factual helpfulness, but not necessarily raw QA accuracy |
| Faster | 6/10 | Decision-first prompting may reduce wasted multi-step reasoning and tool use |
| Stronger | 9/10 | The core value is robustness under ambiguity, false premises, and conflict |
| Cheaper | 8/10 | High leverage from curation and inference, without requiring large pretraining |
| Broader | 8/10 | Useful for QA, assistants, tool-using agents, and retrieval systems |

Top dimensions to emphasize:

- `Stronger`
- `Broader`
- `Cheaper`

## Paradigm-Shift Probe

1. Does it challenge a hidden assumption?
   Yes. Most current evaluation assumes the query should be answered rather than repaired.

2. Does it target an elephant-in-the-room issue?
   Yes. Real users often ask flawed or underspecified questions, and models still over-answer.

3. Does it benefit from a new technology cycle?
   Yes. Reasoning models and agentic systems make the action-selection problem more visible and more important.

4. If solved, would the field change?
   Partially yes. It would change how we evaluate assistant usefulness and calibration, especially for agents and retrieval-augmented systems.

Disruptive potential:

- `Yes, if the empirical finding is sharp and the evaluation design is disciplined`

## What Must Be True For This To Be Oral-Caliber

At least three of the following must happen:

1. Strong models are **not close to ceiling**.
2. Reasoning models show a **systematic over-answering pattern**.
3. The failure persists across at least **three defect types**, not just one niche slice.
4. A simple intervention improves utility **without collapsing normal answerability**.
5. Human judges agree the benchmark is measuring genuinely useful assistant behavior.

If these do not happen, the project may still be a decent findings paper, but not the oral-level version we want.

## Scope Discipline

### In Scope

- text-only user queries
- optional retrieved passages
- four actions: `answer`, `ask`, `challenge`, `abstain`
- three to four high-precision slices
- open-source models in the 7B to 14B range for the first serious sweep

### Out of Scope For Now

- multimodal interaction
- large-scale agent environments
- full RL pipelines
- long-horizon tool-use benchmarks
- custom pretraining or full SFT from scratch

## Recommended Scientific Framing

The project should be written around **action selection under defective inputs**, not around a vague notion of safety or calibration.

The benchmark should answer:

1. When should a model answer directly?
2. When should it ask for missing information?
3. When should it correct the user's premise?
4. When should it refuse to decide because the evidence is insufficient or irreconcilable?

The method section is secondary until the benchmark signal is validated.

## Core Hypotheses

### H1

Instruction and reasoning models are over-optimized for answer continuation and therefore over-answer under defective inputs.

### H2

Reasoning-style models often intensify the problem by rationalizing a bad premise instead of interrupting it.

### H3

A lightweight decision-first policy or critique-first controller can improve utility with much less compute than full model retraining.

## Evaluation Design Principles

### Primary Metric

Use a **utility-centered metric** that penalizes confident but wrong answering more than a cautious clarification or abstention.

### Secondary Metrics

- action accuracy
- answer exact match or F1 on answerable cases
- challenge precision
- clarification usefulness
- over-answer rate

### Mandatory Controls

- a clean answerable subset so the policy does not win simply by becoming timid
- per-slice reporting instead of only pooled reporting
- qualitative analysis for each action type

## The Real Plan

### Phase 0: Nail The Task Definition

Goal:

- freeze the task ontology and annotation decision tree

Deliverables:

- formal definitions for each action
- boundary cases
- a small adjudicated set of examples that stress the boundaries
- initial ontology documented in [action_ontology.md](/data/sony/emnlp2026_critique_or_clarify/docs/action_ontology.md)
- annotation rules documented in [annotation_rubric.md](/data/sony/emnlp2026_critique_or_clarify/docs/annotation_rubric.md)

Kill criterion:

- if we cannot define the actions clearly enough for consistent labeling, narrow the task

### Phase 1: Get A Strong Empirical Signal

Goal:

- show that good current models fail in a consistent and interesting way

Deliverables:

- QACC slice converted and evaluated
- premise-critique slice converted and evaluated
- one stale-premise slice collected or derived
- at least two model families compared

Success criterion:

- a meaningful utility gap between ordinary answer generation and correct action selection

Kill criterion:

- if strong 7B to 14B models are already near ceiling across slices, pivot early

### Phase 2: Validate Benchmark Quality

Goal:

- prove the benchmark is coherent, not arbitrary

Deliverables:

- annotation rubric
- inter-annotator agreement on a representative subset
- ablations showing each slice matters
- evidence that the primary metric aligns with human preference
- reporting locked to [reporting_template.md](/data/sony/emnlp2026_critique_or_clarify/docs/reporting_template.md)
- adjudication handled by [adjudication_protocol.md](/data/sony/emnlp2026_critique_or_clarify/docs/adjudication_protocol.md)

### Phase 3: Add A Lightweight Intervention

Goal:

- improve action choice without brute-force scale

Candidate interventions:

- critique-first prompting
- two-stage policy: decide action, then generate response
- small LoRA or preference-tuned policy head

Rule:

- do not start this phase until Phase 1 already shows a clear failure gap

## Day-0 Priority Reset

Today should not be optimized for "running many experiments."

Today should be optimized for:

1. freezing the scientific claim
2. freezing the task boundaries
3. preparing one real slice and one real baseline path
4. identifying the first kill criteria

That is a much better start than prematurely launching a full model sweep.

## This Week's Concrete Plan

### Today

- finalize the master framing and action ontology
- add the annotation rubric
- convert QACC and inspect 30 to 50 random examples manually
- start the premise-critique data path
- define the first reporting table template
- freeze the first model matrix in [initial_model_matrix.md](/data/sony/emnlp2026_critique_or_clarify/docs/initial_model_matrix.md)

### Next 2 Days

- write the annotation rubric
- build the stale-premise slice
- run 2 to 3 open models on a small but real dev set

### End Of Week

- decide whether the project shows oral-level signal
- either commit to full benchmark build or narrow to the strongest two slices

## Kill Criteria

We should pivot or narrow aggressively if any of these happen:

1. The action labels cannot be stabilized.
2. Strong baselines perform too well too early.
3. The benchmark is dominated by data-source artifacts instead of action reasoning.
4. The intervention only works by overusing `abstain`.
5. The story cannot be explained cleanly in one paragraph.

## Fallback Paths

If the full four-action version is too loose, fall back in this order:

1. `answer` vs `repair`
2. `answer` vs `challenge`
3. `answer under conflicting evidence` with a stronger utility metric

The fallback still preserves a viable paper if the full ontology proves unstable.

## Human And Codex Responsibilities

### Human

- final scientific judgment
- novelty claims
- annotation-policy decisions
- deciding whether a result is meaningful enough to keep

### Codex

- repo-local implementation
- data conversion scripts
- evaluation pipelines
- baseline running and debugging
- tables, plots, and experiment bookkeeping

## Final Verdict

Verdict:

- `Accept with Revisions`

Interpretation:

- the idea is strong enough to pursue now
- the current repo direction is useful but too engineering-first
- the project becomes much stronger if we prioritize task definition, empirical sharpness, and early kill criteria before scaling experiments
