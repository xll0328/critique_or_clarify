# Grounded Stale-Premise Seed Comparison

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | Qwen2.5 | instruct | -0.5714 | 0 | 0 | 0 | 0.4286 | 0 | 0 | 0 | 0 |
| Qwen2.5-Coder-7B-Instruct | Qwen2.5-Coder | instruct | 0.2857 | 0.8571 | 0 | 0 | 0.1429 | 0 | 1 | 0 | 1 |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek/Qwen | reasoning | -0.5714 | 0.2857 | 0 | 0 | 0.7143 | 0 | 1 | 0 | 0 |

## Per-Slice Table

| Model | Stale Premise |
| --- | --- |
| Qwen2.5-0.5B-Instruct | -0.5714 / 0 |
| Qwen2.5-Coder-7B-Instruct | 0.2857 / 0.8571 |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.5714 / 0.2857 |

## Confusion Tables

### Qwen2.5-0.5B-Instruct (`qwen25_05b_stale_seed_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 0 | 0 | 0 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 3 | 4 | 0 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-Coder-7B-Instruct (`qwen25_coder_7b_stale_seed_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 0 | 0 | 0 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 0 | 6 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-1.5B (`deepseek_r1_qwen15b_stale_seed_grounded_useronlyfixed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 0 | 0 | 0 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 5 | 0 | 2 | 0 |
| abstain | 0 | 0 | 0 | 0 |
