# EMNLP 2026 Introduction v0

Date: 2026-04-26

Status: story draft with Day-1 7B metrics incorporated.

## Running Example

Use the stale-premise example:

> "Why is Facebook still trading under FB?"

Why this example works:

- It is simple enough for page 1.
- A fluent answer is actively bad because it accepts an outdated premise.
- The correct behavior is not refusal; it is a targeted `challenge` with the updated fact.
- It naturally motivates the distinction between answer generation and action selection.

Backup example:

> "Why did Marie Curie win the Nobel Prize in Literature?"

This is cleaner for false premise, but less modern and less connected to stale knowledge.

## Six-Paragraph Introduction Chain

### Paragraph 1: Motivation

Modern language models are usually evaluated as answer generators: given a question and, sometimes, retrieved evidence, the model is expected to produce the correct response. This framing misses a basic requirement of real assistants. Many user inputs are not immediately answerable: they may omit essential details, presuppose a false or outdated fact, or arrive with conflicting evidence. For example, a user might ask why Facebook is still trading under the ticker `FB`. A direct explanation would be misleading; the helpful move is first to correct the outdated premise. The failure is not merely a stale fact in the final answer, but choosing the wrong first move: selecting `answer` when `challenge` is required.

Purpose:

- Make the problem intuitive before naming the task.
- Show that the failure is not merely hallucination or refusal.

### Paragraph 2: Gap In Existing Evaluation

Prior evaluations study pieces of this problem separately: clarification for ambiguous questions, abstention under uncertainty, false-premise correction, temporal robustness, and retrieval conflict. These settings are valuable, but a deployed assistant does not encounter them as separate benchmark labels. It faces a single next-action decision: should it answer, ask a follow-up, challenge the premise, or abstain because support is insufficient? The central object is therefore not another defect category, but the action decision that precedes generation. Evaluating these behaviors separately can reward systems that are good at one repair action while missing calibration failures across the broader action space.

Purpose:

- Defuse the "benchmark soup" objection.
- Establish why one unified decision problem is the contribution.

Citation needs:

- Clarification / ambiguous QA.
- Selective prediction / abstention.
- False premise or presupposition correction.
- Temporal robustness and stale knowledge.
- Retrieval conflict / RAG reliability.

### Paragraph 3: Task Definition

We formulate next-action selection under defective inputs. Given a user query and optional retrieved passages, a model must choose exactly one action: `answer` when the query is specified and supported, `ask` when a missing user-provided detail would unlock the answer, `challenge` when the query contains a false or stale premise, and `abstain` when evidence is missing or irreconcilably conflicting. The target is expected user utility rather than surface style: a model should not receive credit for a fluent answer that accepts a bad premise.

Purpose:

- State the formal problem in plain language.
- Put the four actions on page 1.

### Paragraph 4: Benchmark And Evaluation Design

We build a multi-slice benchmark that instantiates this unified decision problem across answerable controls, false-premise prompts, grounded stale-premise prompts, and conflicting-evidence questions. All slices are mapped into a shared action-decision record and action ontology, so the slice source is secondary to the first-move label being evaluated. The active validation queue has been human-signed-off for the current Day-1 evidence bundle. We evaluate models with action accuracy, per-slice metrics, over-answer rate, and a utility-centered score that penalizes harmful direct answering under defective inputs.

Purpose:

- Explain why the benchmark is disciplined.
- Mention human validation without overclaiming objectivity.

Evidence:

- `docs/action_ontology.md`
- `docs/annotation_rubric.md`
- `_assets/human_validation_work_queue_summary.md`
- `experiments/day1/day1_dataset_slice_summary.md`

### Paragraph 5: Findings

Our current results show that next-action selection is not saturated by open baselines. Models make slice-specific errors that pooled answer accuracy would hide: some hesitate on self-contained answerable controls, while others answer through false or stale premises. In the completed Day-1 matrix, reasoning-style DeepSeek-R1-Distill-Qwen checkpoints do not automatically improve action calibration: the 7B reasoning checkpoint reaches `0.3667` action accuracy and `-0.4313` utility on `day1_dev`, below the strongest instruct baselines, with especially weak false-premise interruption and low JSON adherence. The result supports a scoped claim: explicit reasoning traces are not sufficient for deciding when an assistant should answer, challenge, or abstain.

Purpose:

- Preview evidence with the completed 7B gate.
- Keep the claim scoped to the local checkpoint matrix and prompt protocol.

Current safe evidence:

- `experiments/day1/day1_results_snippets.md`
- `experiments/day1/day1_pairwise_deltas.md`
- `experiments/day1/day1_error_bucket_audit.md`
- `experiments/day1/day1_scale_reasoning_comparison.md`
- `experiments/day1/deepseek_r1_qwen7b_day1_report.md`
- `experiments/day1/interventions/qwen25_15b_dev_decision_first_intervention.md`

### Paragraph 6: Contributions

This paper makes four contributions. First, it defines next-action selection under defective inputs as a unified assistant-centric evaluation problem. Second, it introduces a multi-slice benchmark with a shared action ontology, utility-centered evaluation, and human-validated evidence bundle. Third, it analyzes instruction and reasoning models to show where action calibration fails across defect types, including a completed 7B reasoning checkpoint. Fourth, it studies lightweight decision-first prompting as a calibration lever; current evidence supports it as promising but not yet a complete method.

Purpose:

- Keep claims aligned with completed evidence.
- Avoid selling the intervention as solved too early.

## Flow Checks

| Link | Status | Note |
| --- | --- | --- |
| Running example -> task | locked | The `FB` example directly motivates `challenge` and states that the failure is the wrong first move. |
| Prior-work gap -> unified action space | locked | The limitation is fragmentation across repair behaviors; the central object is the action decision before generation. |
| Task -> benchmark | pass | Slices instantiate one action ontology. |
| Benchmark -> findings | pass | DeepSeek-R1-Distill-Qwen-7B metrics are incorporated. |
| Findings -> intervention | weak | `decision_first` is promising but not yet a strong method result. |

## Immediate Revision Hooks

- Keep `tests/test_paper_story_flow.py` passing after any first-two-page prose edit.
- Decide whether the intervention remains a main contribution or moves to analysis/appendix after any stronger controller attempt.
