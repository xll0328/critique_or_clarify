# Qwen2.5-1.5B Dev Decision-First Intervention

This dev run checks whether the promising quick+stale `decision_first` result survives on the 120-example main day-1 split.

## Readout

- The dev-scale effect is small but directionally useful: utility moves from `-0.2229` to `-0.2208`, action accuracy stays flat at `0.7667`, JSON parse rate improves from `0.8083` to `0.8417`, and over-answer rate drops from `0.0083` to `0.0`.
- The main benefit is calibration rather than broad capability: answerable-control action accuracy improves from `0.35` to `0.475`, but conflicting-evidence action accuracy falls from `0.975` to `0.875`.
- This is not yet a strong main-method claim. It is a promising companion-method result that needs one of two upgrades: either a better controller that keeps the false-premise safety gain without hurting conflict handling, or a narrower claim that decision-first prompting reduces over-answering while preserving overall utility.
- For the oral/best-paper path, use this as Sprint 2 evidence, not as the final intervention.

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2229 | 0.7667 | 0.0125 | 0.475 | 0.0083 | 0 | 0.5909 | 0 | 0.8083 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2208 | 0.7667 | 0.0125 | 0.475 | 0 | 0 | 0.5938 | 0 | 0.8417 |

## Per-Slice Table

| Model | Answerable | False Premise | Conflicting Evidence |
| --- | --- | --- | --- |
| Qwen2.5-1.5B-Instruct | -0.625 / 0.35 | 0.4625 / 0.975 | -0.5062 / 0.975 |
| Qwen2.5-1.5B-Instruct | -0.5938 / 0.475 | 0.4625 / 0.95 | -0.5312 / 0.875 |

## Confusion Tables

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 53 | 0 | 27 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 0 | 39 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_dev_decision_first`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 54 | 0 | 26 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 0 | 1 | 38 | 1 |
| abstain | 0 | 0 | 0 | 0 |
