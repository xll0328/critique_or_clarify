# Human Validation Packet 005 / 005

Queue: `_assets/human_validation_work_queue.csv`
Split: `data/processed/day1_quick_plus_stale_pool.jsonl`

Record final decisions in the CSV, not in this packet. Allowed decisions: `accept`, `fix`, `reject`, `needs_second_pass`.

## HV-EX-050 | example_gold_label | medium

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt/evidence support answering, and is the gold answer acceptable?
- AI prefill: gold_action=answer; source=PCBench; slice=answerable_control; gold_answer=34; prompt=Three friends spent $20.25 on 3 tickets to the fair. They also spent $4.50 less on food than on the tickets. They also went on 2 differen...
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `pcbench-answer-26`
- Source: `PCBench`
- Slice: `answerable_control`
- Gold action: `answer`
- Gold answer: 34

### Prompt

```text
Three friends spent $20.25 on 3 tickets to the fair. They also spent $4.50 less on food than on the tickets. They also went on 2 different rides which costs $33 for each ride. If they agreed to split all the costs evenly, how much did each of them pay?
```
