# Day-1 Results Template

## Run Metadata

| Field | Value |
| --- | --- |
| Date |  |
| Model |  |
| GPUs |  |
| Data | `data/processed/day1_dev.jsonl` |
| Prompt format | action-selection JSON |
| Max new tokens |  |
| Temperature |  |

## Main Metrics

| Metric | Value |
| --- | --- |
| Overall utility |  |
| Action accuracy |  |
| Answer EM |  |
| Over-answer rate |  |
| JSON parse rate |  |

## Per-Slice Metrics

| Slice | Count | Utility | Action Acc. | Answer EM | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- |
| answerable_control |  |  |  |  |  |  |
| false_premise |  |  |  |  |  |  |
| conflicting_evidence |  |  |  |  |  |  |

## Confusion Notes

- answer -> challenge:
- challenge -> answer:
- answer -> abstain:

## Qualitative Failures

1. 
2. 
3. 
4. 
5. 

## Interpretation

- Does the model over-answer on false premises?
- Does the model stay useful on clean answerable controls?
- Does conflict in retrieval push the model toward brittle answers or calibrated answers?

## Decision

- Continue as planned
- Narrow one slice
- Revisit prompt format
- Pivot model choice
