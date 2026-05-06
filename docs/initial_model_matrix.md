# Initial Model Matrix

## Purpose

The first model matrix is not for leaderboard coverage.

It is for testing the paper's main claim with the smallest set of models that can still produce a sharp result.

## Selection Principle

The first controlled comparison should isolate:

1. a strong instruct model
2. a reasoning-style model from a related family if possible
3. one larger instruct checkpoint only after the first pair is understood

Do not start with five or six models.

## Recommended Day-1 Matrix

### Pair A

- `Qwen/Qwen2.5-7B-Instruct`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`

Why:

- similar scale
- good enough quality to matter
- a clean instruct vs reasoning-style contrast
- feasible on the available hardware

### Pair B

- `Qwen/Qwen2.5-14B-Instruct`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`

Why:

- useful only after Pair A shows a real signal
- checks whether the effect survives modest scale-up

### Optional Cross-Family Check

- one Llama-class instruct model in the 8B range

Why:

- guards against the result being a single-family artifact

## Execution Order

1. smoke run on the local schema
2. QACC dev subset on Pair A
3. manual inspection of failure cases
4. only then expand to Pair B or another family

## Stop Rules

Do not add more models yet if:

- prompt formatting is still unstable
- action parsing is noisy
- the first pair has not been qualitatively audited

## First Metrics To Report

For each model, report:

- overall utility
- overall action accuracy
- answer EM on answerable items
- over-answer rate
- per-slice utility
- per-slice action confusion

## Interpretation Rules

### If reasoning wins cleanly

That weakens the current main hypothesis.

Then we should check:

- whether the ontology is too easy
- whether the prompt makes the action decision too explicit
- whether the slice mix is too answer-heavy

### If reasoning over-answers more

That is a strong signal for the main paper story.

### If both models are near ceiling

Do not brute-force more scale.

Instead:

- make the benchmark sharper
- add harder slices
- narrow to the slices with the strongest nontrivial gap

## Practical Constraints On This Machine

- use `2` GPUs for the first serious run if the machine is busy
- treat `4` GPUs as the stable ceiling for repeated experiments
- avoid assuming all `8` GPUs are simultaneously free

## Command Template

```bash
python scripts/run_baseline.py \
  --backend transformers \
  --model Qwen/Qwen2.5-7B-Instruct \
  --data data/processed/qacc_dev.jsonl \
  --output outputs/day0/qacc_qwen25_7b_dev.jsonl \
  --eval-json outputs/day0/qacc_qwen25_7b_dev_metrics.json \
  --max-new-tokens 160 \
  --temperature 0.0
```

## Rule Of Restraint

A clean two-model story beats a messy eight-model table in the first week.
