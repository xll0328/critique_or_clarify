# EMNLP 2026 Figure Plan

Date: 2026-04-26

Goal: make the paper's contribution legible in the first two pages and make the core empirical result easy to remember.

## Figure 1: Motivated Task Example

Figure type: motivated example plus task schematic.

Reason:

- The paper's main risk is being perceived as a collection of unrelated slices.
- Figure 1 must make the unified action-selection problem obvious before the benchmark details.

### Recommended Paradigm

Use a single running example canvas with a central decision point.

Avoid:

- A pure pipeline diagram, because that foregrounds dataset construction instead of the scientific idea.
- A four-column taxonomy only, because it can look like an ontology table rather than a task.

### Layout Sketch

Canvas: one-column friendly, but drawn at two-column width for readability.

Panel A: "User input + optional evidence"

- Show four compact input cards:
  - Answerable control: "What county is Old Forge, New York in?"
  - False premise: "Why did Marie Curie win the Nobel Prize in Literature?"
  - Stale premise: "Why is Facebook still trading under FB?"
  - Conflicting evidence: "Which year was the lighthouse built?" with two conflicting snippets.

Panel B: "Next-action selection"

- One central decision node:
  "Choose the highest-utility next action"
- Four outgoing arrows:
  `answer`, `ask`, `challenge`, `abstain`

Panel C: "Response behavior"

- Four short response templates:
  - answer: direct supported answer
  - ask: one missing detail question
  - challenge: correct the false/stale premise
  - abstain: explain insufficient/conflicting support

Key visual point:

- The model should not pass every input into the same "answer generator" path.
- The action decision sits before generation.

### Labeling Plan

- Use exact action labels in monospace: `answer`, `ask`, `challenge`, `abstain`.
- Use slice labels only as secondary text; actions are primary.
- Mark defective premise examples with a small "premise defect" tag.
- Mark evidence conflict examples with a small "support conflict" tag.

### Color Roles

Use color-blind-safe roles:

- blue: answerable / supported answer
- purple: ask / missing slot
- vermillion: challenge / false or stale premise
- gray: abstain / insufficient or irreconcilable evidence

Do not encode the action only by color; pair every color with text labels.

### Caption Draft

Figure 1. Next-action selection under defective inputs. Instead of treating every user query as an answer-generation request, the assistant first chooses whether to answer, ask a clarification, challenge a false or stale premise, or abstain under insufficient evidence.

## Figure 2: Main Empirical Finding

Figure type: experimental results.

Reason:

- The most memorable result should be a slice-level calibration failure, not a pooled score.
- The current strongest visual candidate is over-answer rate or utility by slice and model style.

### Current Generated Version

Artifacts:

- `experiments/day1/figures/emnlp2026_figure2_action_calibration.png`
- `experiments/day1/figures/emnlp2026_figure2_action_calibration.pdf`
- `experiments/day1/figures/emnlp2026_figure2_action_calibration.csv`
- `experiments/day1/figures/emnlp2026_figure2_action_calibration_caption.md`
- Generator: `scripts/plot_emnlp2026_figure2_action_calibration.py`

Paradigm:

- Panel A: dev action accuracy for the completed model matrix, with average utility labels and marker size indicating JSON adherence.
- Panel B: dev per-slice action accuracy for answerable controls, false premise, and conflicting evidence.
- Panel C: quick+stale false/stale-premise over-answer rate.

Rationale:

- Panel A shows the main model-level result without hiding utility.
- Panel B shows that the result is slice-structured rather than one pooled artifact.
- Panel C isolates the most intuitive defective-premise risk.

### Labeling Plan

- Mark reasoning-style models with diamond markers in Panel A.
- Keep exact numbers in tables and caption; avoid overloading the plot with many labels.
- Keep all accuracy and over-answer axes on `[0, 1]` for honest comparison.
- Keep y-axis from 0 to 1 for honest comparison.

### Caption Draft

Figure 2. Reasoning traces do not automatically yield calibrated next-action decisions. Panel A shows `day1_dev` action accuracy for the completed model matrix, with marker size proportional to JSON parse rate and text labels giving average utility. Panel B breaks action accuracy down by answerable controls, false-premise prompts, and conflicting-evidence questions. Panel C shows over-answer rates on false- and stale-premise items in the quick+stale split, using the shared model-color legend below the panels. The central pattern is that caution is not monotonic safety: the DeepSeek-R1-Distill-Qwen reasoning checkpoints remain weak on false/stale premise interruption and, for the 7B checkpoint, also abstain heavily on clean answerable controls.

## Figure 3: Intervention Result

Figure type: experimental results / companion method.

Status: conditional.

Use only if the final intervention remains worth reporting after dev-scale and 7B interaction checks.

### Recommended Paradigm

Two-panel before/after chart:

- Panel A: overall utility and over-answer rate for baseline vs `decision_first`.
- Panel B: per-slice action accuracy, showing whether answerable and conflict handling are preserved.

Current read:

- `decision_first` is promising but not final: it reduces over-answering and preserves overall dev utility, but does not yet clearly dominate across slices.
- `critique_first`, `decision_first_guarded`, and `decision_first_balanced` should be treated as negative ablations unless a later controller improves them.

## Table-Figure Division

Use figures for:

- problem framing
- over-answer behavior
- before/after intervention shape

Use tables for:

- exact metrics
- bootstrap CIs
- per-slice action accuracy
- validation counts

## Universal Audit

- Export schematic figures as vector PDF/SVG.
- Minimum font size after paper scaling: 8 pt.
- No dense paragraph text inside figures.
- No 3D bars, gradients, or decorative chart effects.
- Captions should state the finding in the first sentence.
- All plotted values must come from generated metric JSON or CSV artifacts.

## Top Three Figure Actions

1. Draft Figure 1 as a schematic immediately; it does not depend on pending 7B results.
2. Regenerate Figure 2 only after DeepSeek-R1-Distill-Qwen-7B metrics land.
3. Keep Figure 3 conditional until the intervention is either strengthened or scoped as a calibration-only result.
