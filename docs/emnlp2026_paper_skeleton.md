# EMNLP 2026 Paper Skeleton

Working title:

> Critique or Clarify? Evaluating Next-Action Selection Under Defective User Inputs

## One-Sentence Contribution

We introduce and evaluate a unified assistant action-selection problem in which a model must decide whether to answer, ask a clarification, challenge a false or stale premise, or abstain when the input or evidence is defective.

## Benchmark Five-Pillar Check

| Pillar | Current Plan | Status | Reviewer Risk |
| --- | --- | --- | --- |
| Research gap | Existing evaluations separately test QA, ambiguity, false premises, stale facts, and retrieval conflict, but assistants face them as one next-action decision. | strong | Must not sound like a loose dataset merge. |
| Construction pipeline | Convert and curate multiple slices under one action ontology; add grounded stale-premise items; validate active queue with human decisions. | strong | Need a compact pipeline figure and a source/label table. |
| Evaluation framework | Four-action taxonomy plus utility metric, over-answer rate, per-slice reporting, confusion matrices, and bootstrap CIs. | strong | Need to explain why utility weights are defensible. |
| Empirical findings | Current baselines show non-saturation and slice-specific failures; both completed DeepSeek reasoning checkpoints underperform the strongest instruct baselines on the Day-1 action-selection metrics. | strong | Scope the claim to the local checkpoint matrix and note low JSON adherence for reasoning outputs. |
| Companion method | Decision-first prompting has a positive quick+stale pilot and a near-neutral dev confirmation; critique-first and longer guarded variants are negative ablations. | promising | Still needs careful framing as a calibration lever, not a solved method. |

## Abstract Shape

1. Problem:
   LLM evaluation usually asks whether a model can answer, but real assistants often need to decide whether answering is appropriate.

2. Task:
   Define next-action selection over four actions: `answer`, `ask`, `challenge`, and `abstain`.

3. Benchmark:
   Build a multi-slice evaluation covering answerable controls, false premises, stale premises, and conflicting evidence, with a utility-centered metric and human validation.

4. Finding:
   Current open models show slice-specific calibration failures; the completed reasoning-style checkpoints do not automatically fix the problem and remain weak on defective-premise interruption and clean-answer willingness.

5. Intervention:
   Report the lightweight decision-first pilot as a promising calibration lever if the final main results remain aligned; otherwise present it as an exploratory appendix result.

## Introduction Outline

Paragraph 1: Answer generation is not enough.

- Modern LLMs are strong answer generators.
- Many real user inputs are defective: underspecified, based on a false premise, stale, or paired with conflicting evidence.
- In those cases, the first helpful action is not always an answer.

Paragraph 2: Fragmented existing evaluations miss the unified decision.

- Ambiguity, false premise correction, stale facts, and conflicting evidence are often evaluated separately.
- A deployed assistant faces them as one policy problem: what should I do next?

Paragraph 3: Define the action-selection problem.

- Four actions: answer, ask, challenge, abstain.
- The target is expected user utility, not surface style.
- This gives a single evaluation lens across multiple defect types.

Paragraph 4: Benchmark and metric.

- Multi-slice benchmark from answerable controls, premise defects, stale facts, and conflicting evidence.
- Utility metric penalizes harmful over-answering.
- Human validation and boundary rules reduce subjectivity.

Paragraph 5: Empirical surprise.

- Strong baselines remain far from ceiling.
- Failure is slice-specific.
- Reasoning-style checkpoints do not automatically improve action calibration.
- The 7B reasoning run closes the Day-1 scale/reasoning gate but should be reported with its low JSON adherence.

Paragraph 6: Contributions.

1. A formal next-action selection task for defective inputs.
2. A validated multi-slice benchmark and utility-centered evaluation.
3. A model analysis showing where instruction and reasoning models fail.
4. A lightweight decision-first intervention pilot and negative prompt-ablation analysis.

## Section Plan

### 1. Introduction

Goal: make the problem feel inevitable and the task clean.

Must include:

- One memorable example.
- The four-action framing.
- A concise statement that this is not just refusal or hallucination evaluation.

### 2. Related Work

Buckets:

- Ambiguity and clarification in QA/dialogue.
- False premise and presupposition correction.
- Retrieval conflict and abstention.
- Stale knowledge / temporal robustness.
- LLM calibration, over-answering, and selective prediction.

Rule:

- Related Work must support the "fragmented prior tasks, unified next-action setting" argument.

### 3. Task Definition

Must include:

- Input format: user query plus optional evidence passages.
- Output format: action plus concise response.
- Action ontology.
- Decision tree.
- Utility metric.

Draft source:

- `docs/emnlp2026_boundary_case_table.md`

### 4. Benchmark Construction

Must include:

- Slice definitions.
- Source datasets and conversions.
- Stale-premise construction protocol.
- Human validation summary.
- Gold label distribution.

Draft source:

- `docs/emnlp2026_data_quality_section_v0.md`

### 5. Models And Protocol

Must include:

- Model families and sizes.
- Prompt format.
- Parsing/reparse protocol.
- Random seeds and decoding settings.
- Hardware/cache notes as reproducibility details.

### 6. Main Results

Must include:

- Main table.
- Per-slice table.
- Bootstrap CIs.
- Confusion matrix or over-answer plot.
- DeepSeek-R1-Distill-Qwen-7B row is now available.

Draft source:

- `docs/emnlp2026_results_section_v0.md`

### 7. Intervention Or Analysis

Primary path:

- Decision-first controller or critique-first prompt.
- Utility and answerability guardrail.

Fallback path:

- If the intervention remains weak at final scale, make this a deeper failure analysis section and move intervention to appendix.

### 8. Qualitative Analysis

Must include:

- One example of false-premise over-answering.
- One stale-premise example.
- One conflicting-evidence example.
- One answerable-control hesitation example.

Draft source:

- `docs/emnlp2026_qualitative_examples_shortlist.md`

### 9. Limitations And Ethics

Must include:

- Text-only scope.
- Small but curated benchmark.
- English-heavy / source limitations where applicable.
- Human validation process.
- Risks of overusing challenge or abstain.

## Figure Plan

Figure 1:

- Four-action task schematic.
- Show one input flowing into action selection before generation.
- Include examples of false premise, stale premise, conflicting evidence, and answerable control.

Figure 2:

- Main action-calibration result from `experiments/day1/figures/emnlp2026_figure2_action_calibration.pdf`.
- Shows overall dev action accuracy, dev per-slice action accuracy, and quick+stale false/stale over-answer.

Figure 3:

- Utility/action accuracy before and after decision-first intervention, if Sprint 2 succeeds.

## Main Table Plan

Table 1:

- Dataset/slice summary and gold action distribution.

Table 2:

- Main model comparison: utility, action accuracy, over-answer rate, answer contains rate, JSON parse rate.

Table 3:

- Intervention ablation with answerability guardrail, generated at `experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_main.tex`.

Appendix:

- Full per-slice tables.
- Confusion matrices.
- Bootstrap CI tables.
- Human-validation packet summary.

## First Draft Rule

The first full draft should be written around evidence that already exists. Pending results may be marked as placeholders, but no paragraph should depend on an uncompleted experiment.
