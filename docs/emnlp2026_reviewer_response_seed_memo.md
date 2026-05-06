# EMNLP 2026 Reviewer Response Seed Memo

Date: 2026-05-06

Status: reviewer-attack hardening pass synchronized with the 2026-05-06 final-push abstract framing, virtual-prereview roadmap, first-two-page story, visual-balance, validation, and lock-gate audits.

## Severity Summary

- `CRITICAL`: 0 open for response prep
- `MAJOR`: 7 hardened
- `MINOR`: 0 open for response prep

## How To Use

These are not copy-paste rebuttals. They are seeds for planned paper edits and author-response wording after reviewer comments arrive. Keep the final response tailored to the actual review text, acknowledge the concern first, then point to the scoped evidence.

Tracked major attack-path slugs: benchmark-soup, construction-transparency, parse-confound, utility-weight, reasoning-overclaim, intervention-overclaim, statistics-overclaim.

Core discipline: do not claim broad assistant helpfulness from utility alone.

Latest first-move wording anchor: the abstract now opens with `Answer quality is an incomplete target` when the user input itself may be defective, because the assistant must choose the right first move before generating. Rebuttal language should preserve this scoped target: next-action calibration, not broad assistant helpfulness or final-answer quality alone.

## R1: Benchmark Soup / Dataset Mixture

Likely attack:
The benchmark could be read as a loose combination of ambiguity, false premise, stale fact, and retrieval-conflict examples rather than one task.

Paper-side defense:

- The evaluated object is one action decision: answer, ask, challenge, or abstain.
- Each row follows the same input/evidence -> action -> constrained response pipeline.
- Figure 1 and the first two pages present the benchmark as next-action selection under defective inputs, not as four unrelated subtasks.
- The abstract frames final-answer quality as incomplete without the right first move, keeping the benchmark contribution ahead of the prompt intervention.
- The submission evidence is strongest for answer-vs-challenge and evidence-conflict calibration; the paper should not imply that every slice is equally mature.

Response seed:
The benchmark does not score four unrelated tasks. It scores the same first-move decision under different ways an input can become unreliable: missing intent, false premise, stale premise, or conflicting evidence. The central target is not final-answer quality alone, but whether the assistant chooses the right first move before generating. We agree that slice coverage is uneven in the current submission, so the claim is scoped to a shared action ontology and to the answer-vs-challenge/conflict calibration patterns supported by the current results.

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

## R2: Dataset Construction Transparency

Likely attack:
Synthetic-expansion candidates may look like opaque generated examples, and reviewers may not know how they became part of the split.

Paper-side defense:

- Synthetic candidates are not directly benchmark examples.
- Candidate generators mark rows as not benchmark-facing until validation.
- Promotion requires `human_decision=accept` in the validation queue.
- The promotion script checks duplicate identifiers, accepted-row counts, source tags, slice/action counts, and writes a manifest.
- The paper should still avoid implying independent inter-annotator agreement unless a human agreement study is completed.

Response seed:
We agree that construction details matter for a benchmark paper. We therefore revised the benchmark-construction section to distinguish generated seed candidates from accepted benchmark rows. Candidate rows are promoted only after a validation-queue decision, and the frozen split is backed by source/action/slice manifests and duplicate checks. This is a construction audit trail, not a claim that the ontology has independent inter-annotator agreement.

Do not say:

- "synthetic rows are automatically valid"
- "candidate generation is equivalent to annotation"
- "human validation proves the ontology is objective"

Evidence:

- `paper/sections/03_benchmark.tex`
- `scripts/prepare_answer_challenge_seed_candidates.py`
- `scripts/prepare_ask_abstain_seed_candidates.py`
- `scripts/prepare_answer_topup_seed_candidates.py`
- `scripts/promote_validated_expansion_candidates.py`
- `data/processed/emnlp2026_expanded_dev_with_answer_topup_manifest.json`

## R3: Parsing And Format Confound

Likely attack:
Low JSON adherence, especially for reasoning checkpoints, may confound action-selection capability with format-following.

Paper-side defense:

- The current paper treats format adherence as part of the measured protocol because the task requires an explicit next action.
- The claim remains scoped to the current prompt and parsing protocol.
- A parse-sensitivity audit now quantifies how strict JSON-or-abstain scoring differs from the current deterministic parser, especially for low-adherence runs.

Response seed:
We agree that parsing and action quality should be separated as much as the saved artifacts allow. The paper reports JSON parse rate precisely because protocol adherence can affect the measured action. Our current claim is local to the prompt and deterministic parsing protocol; the saved-output parse audit confirms that low-adherence runs are protocol-sensitive, and stronger model-family conclusions would require format-control or alternative-extraction runs.

Do not say:

- "format failures are irrelevant"
- "JSON adherence fully explains the result"
- "the current protocol proves model-intrinsic action ability"

Evidence:

- `paper/sections/04_protocol.tex`
- `paper/sections/05_results.tex`
- `paper/sections/08_limitations.tex`
- `experiments/day1/day1_parse_sensitivity_audit.md`
- `docs/emnlp2026_virtual_prereview_revision_plan.md`

## R4: Utility Weights Are Arbitrary

Likely attack:
The utility score may look like the paper bakes in arbitrary preferences and then optimizes to those weights.

Paper-side defense:

- Utility is a diagnostic summary, not a universal user-cost model.
- The weights encode an asymmetric harm ordering: over-answering defective inputs is treated as more harmful than cautious behavior on answerable inputs.
- The paper also reports action accuracy, over-answer rate, answer-supported accuracy, slice-level metrics, and qualitative examples.
- Intervention claims must be read through guardrails, not only through the highest raw utility value.
- The utility-weight sensitivity audit recomputes the local matrix under alternate harm orderings; the best instruction row remains above the best reasoning row under the tested schemes.

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
- `experiments/day1/day1_utility_weight_sensitivity_audit.md`

## R5: Reasoning-Model Overclaim

Likely attack:
Reviewers may object if the paper appears to claim that reasoning models are generally worse or that a model family cannot handle the task.

Paper-side defense:

- The claim is limited to completed local checkpoints under the current prompt and parsing protocol.
- Format adherence is part of the measured behavior because the benchmark requires an explicit action decision before response content.
- The result is a calibration warning, not a general statement about all reasoning models or all inference setups.

Response seed:
Our claim is limited to completed local checkpoints under the current prompt and parsing protocol. In that setting, the DeepSeek reasoning checkpoints did not improve next-action calibration over the strongest instruction baselines. We treat JSON/action-format adherence as part of the measured task behavior because the benchmark explicitly evaluates the first action decision.

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

## R6: Intervention Overclaim

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

## R7: Ask And Hard Abstain Coverage

Likely attack:
The ontology has four actions, but Day-1 active evidence mostly exercises answer/challenge boundaries.

Paper-side defense:

- The paper already scopes the current evidence to answer-vs-challenge and conflict calibration.
- Ask and hard abstain are ontology-defined and present in the paper-facing split through ambiguous-intent and insufficient-evidence slices, but they are not yet balanced evidence for all possible clarification or abstention settings.
- Future benchmark expansion should broaden source diversity and model-analysis depth for ambiguous-intent and irreconcilable-evidence slices before claiming broad four-action coverage.

Response seed:
The current submission evidence most strongly supports answer-vs-challenge and conflict-calibration claims. The canonical split includes ask and abstain examples because they are necessary actions for the broader task, but we keep claims about clarification and abstention behavior tied to the documented ambiguous-intent and insufficient-evidence slices.

Do not say:

- "all four actions are equally validated"
- "the benchmark fully covers ambiguous intent"
- "abstention behavior is solved"

Evidence:

- `paper/sections/03_benchmark.tex`
- `paper/sections/08_limitations.tex`
- `docs/emnlp2026_reviewer_attack_memo.md`

## R8: Statistical Confidence And CI Overclaim

Likely attack:
The bootstrap intervals may look too local for oral-strength claims, or the API rows may be read as unsupported fine-grained model rankings.

Paper-side defense:

- The intervals are local uncertainty checks over the current split samples, not proof of a stable model ordering.
- The paper uses CIs to separate coarse patterns from small rank differences.
- Full-minus-canonical 600-vs-560 deltas are reported as sensitivity evidence because the delta intervals overlap zero.
- API rows are described as uncertainty-qualified point estimates; the response should emphasize persistent action-boundary difficulty, not every adjacent rank.

Response seed:
We agree that the bootstrap intervals should not be read as a full uncertainty model over dataset construction, prompting, or future model releases. We use them as local checks on the current split samples and explicitly avoid fine-grained model-ranking claims. The supported claim is coarser: next-action calibration remains unsaturated, boundary slices remain difficult, and the 600-example split is sensitivity evidence rather than a replacement benchmark.

Do not say:

- "the CIs prove a stable model ordering"
- "every adjacent API difference is statistically separated"
- "the 600-example stress split is stronger than the canonical benchmark"

Evidence:

- `paper/sections/05_results.tex`
- `paper/sections/08_limitations.tex`
- `docs/emnlp2026_oral_best_paper_quality_audit.md`
- `docs/emnlp2026_reviewer_triage_revision_memo.md`

## Final Response Discipline

For each real review:

1. Acknowledge the concern.
2. Scope the claim to completed evidence.
3. Point to the relevant table, figure, section, or audit.
4. Avoid universal claims, deployment claims, and broad model-family claims.
5. Do not claim broad assistant helpfulness from utility alone.
6. Preserve the first-move framing: answer quality is incomplete if the model chooses the wrong action first.
