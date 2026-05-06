# EMNLP 2026 Reviewer Response Seed Memo

Date: 2026-04-27

Status: reviewer-attack hardening pass after the first-two-page story, visual-balance, validation, and lock-gate audits.

## Severity Summary

- `CRITICAL`: 0 open for response prep
- `MAJOR`: 4 hardened
- `MINOR`: 0 open for response prep

## How To Use

These are not copy-paste rebuttals. They are seeds for planned paper edits and author-response wording after reviewer comments arrive. Keep the final response tailored to the actual review text, acknowledge the concern first, then point to the scoped evidence.

Tracked major attack-path slugs: benchmark-soup, utility-weight, reasoning-overclaim, intervention-overclaim.

Core discipline: do not claim broad assistant helpfulness from utility alone.

## R1: Benchmark Soup / Dataset Mixture

Likely attack:
The benchmark could be read as a loose combination of ambiguity, false premise, stale fact, and retrieval-conflict examples rather than one task.

Paper-side defense:

- The evaluated object is one action decision: answer, ask, challenge, or abstain.
- Each row follows the same input/evidence -> action -> constrained response pipeline.
- Figure 1 and the first two pages present the benchmark as next-action selection under defective inputs, not as four unrelated subtasks.
- The Day-1 evidence is strongest for answer-vs-challenge and evidence-conflict calibration; the paper should not imply that every slice is equally mature.

Response seed:
The benchmark does not score four unrelated tasks. It scores the same first-move decision under different ways an input can become unreliable: missing intent, false premise, stale premise, or conflicting evidence. We agree that slice coverage is uneven at Day-1 scale, so the claim is scoped to a shared action ontology and to the answer-vs-challenge/conflict calibration patterns supported by the current results.

Do not say:

- "universal taxonomy"
- "objective benchmark"
- "complete evaluation of all defective-input behavior"

Evidence:

- `paper/sections/01_introduction.tex`
- `paper/sections/02_task.tex`
- `paper/sections/03_benchmark.tex`
- `docs/emnlp2026_first_two_page_oral_readiness_audit.md`
- `docs/emnlp2026_first_two_page_visual_balance_audit.md`

## R2: Utility Weights Are Arbitrary

Likely attack:
The utility score may look like the paper bakes in arbitrary preferences and then optimizes to those weights.

Paper-side defense:

- Utility is a diagnostic summary, not a universal user-cost model.
- The weights encode an asymmetric harm ordering: over-answering defective inputs is treated as more harmful than cautious behavior on answerable inputs.
- The paper also reports action accuracy, over-answer rate, answer-supported accuracy, slice-level metrics, and qualitative examples.
- Intervention claims must be read through guardrails, not only through the highest raw utility value.

Response seed:
We agree utility is not a universal user-cost model. We use it as a compact diagnostic for an explicit asymmetric harm ordering, and we avoid interpreting it alone. The main claims are backed by disaggregated action accuracy, over-answering, answer-supported behavior, per-slice metrics, and examples that show which first action incurred the loss.

Do not say:

- "the utility function captures real user costs"
- "utility is the main objective by itself"
- "higher utility proves broad assistant helpfulness"

Evidence:

- `paper/sections/02_task.tex`
- `paper/sections/05_results.tex`
- `paper/sections/06_intervention.tex`
- `paper/sections/08_limitations.tex`
- `docs/emnlp2026_numeric_claim_audit.md`

## R3: Reasoning-Model Overclaim

Likely attack:
Reviewers may object if the paper appears to claim that reasoning models are generally worse or that a model family cannot handle the task.

Paper-side defense:

- The claim is limited to completed Day-1 local checkpoints under the current prompt and parsing protocol.
- Format adherence is part of the measured behavior because the benchmark requires an explicit action decision before response content.
- The result is a calibration warning, not a general statement about all reasoning models or all inference setups.

Response seed:
Our claim is limited to completed Day-1 local checkpoints under the current prompt and parsing protocol. In that setting, the DeepSeek reasoning checkpoints did not improve next-action calibration over the strongest instruction baselines. We treat JSON/action-format adherence as part of the measured task behavior because the benchmark explicitly evaluates the first action decision.

Do not say:

- "reasoning models fail at defective-input handling"
- "chain-of-thought is harmful"
- "this proves instruction models are better in general"

Evidence:

- `experiments/day1/reports/day1_scale_reasoning_comparison.md`
- `experiments/day1/reports/day1_quick_plus_stale_comparison.md`
- `paper/tables/day1_scale_reasoning_macros.tex`
- `paper/tables/day1_quick_stale_macros.tex`
- `docs/emnlp2026_reviewer_attack_memo.md`

## R4: Intervention Overclaim

Likely attack:
The intervention may look like a method contribution that is too small, or like utility can be gamed by becoming more cautious.

Paper-side defense:

- The intervention is an exploratory calibration probe, not a complete method.
- Lead with `decision_first`, not the highest raw utility variant.
- Report answer-supported and defective-premise guardrails alongside utility.
- Keep negative prompt variants visible because they show that generic caution can damage answerable/control behavior.

Response seed:
We intentionally present `decision_first` as an exploratory calibration probe. The point is not that a prompt is a deployable solution, but that forcing the action decision before response generation can reduce wrong first moves under defective inputs. We therefore report the guarded row first and keep variants that over-correct visible in the table.

Do not say:

- "the intervention solves the task"
- "the prompt is a robust controller"
- "the highest-utility prompt is best overall"

Evidence:

- `paper/sections/06_intervention.tex`
- `paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex`
- `docs/emnlp2026_claim_ledger.md`
- `docs/emnlp2026_reviewer_attack_memo.md`

## R5: Ask And Hard Abstain Coverage

Likely attack:
The ontology has four actions, but Day-1 active evidence mostly exercises answer/challenge boundaries.

Paper-side defense:

- The paper already scopes the current evidence to answer-vs-challenge and conflict calibration.
- Ask and hard abstain are ontology-defined and present in the paper-facing split through ambiguous-intent and insufficient-evidence slices, but they are not yet balanced evidence for all possible clarification or abstention settings.
- Future benchmark expansion should broaden source diversity and model-analysis depth for ambiguous-intent and irreconcilable-evidence slices before claiming broad four-action coverage.

Response seed:
The current Day-1 evidence most strongly supports answer-vs-challenge and conflict-calibration claims. The paper-facing split includes ask and abstain examples because they are necessary actions for the broader task, but we keep claims about clarification and abstention behavior tied to the documented ambiguous-intent and insufficient-evidence slices.

Do not say:

- "all four actions are equally validated"
- "the benchmark fully covers ambiguous intent"
- "abstention behavior is solved"

Evidence:

- `paper/sections/03_benchmark.tex`
- `paper/sections/08_limitations.tex`
- `docs/emnlp2026_reviewer_attack_memo.md`

## Final Response Discipline

For each real review:

1. Acknowledge the concern.
2. Scope the claim to completed evidence.
3. Point to the relevant table, figure, section, or audit.
4. Avoid universal claims, deployment claims, and broad model-family claims.
5. Do not claim broad assistant helpfulness from utility alone.
