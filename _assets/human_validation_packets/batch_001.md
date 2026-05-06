# Human Validation Packet 001 / 005

Queue: `_assets/human_validation_work_queue.csv`
Split: `data/processed/day1_quick_plus_stale_pool.jsonl`

Record final decisions in the CSV, not in this packet. Allowed decisions: `accept`, `fix`, `reject`, `needs_second_pass`.

## HV-CL-001 | split_accounting_claim | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Verify that the expanded stale-pool split counts and slice labels match the JSONL file.
- AI prefill: total=51; answerable_control=12, conflicting_evidence=12, false_premise=12, stale_premise=15
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-002 | metric_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_05b_day1_quick_plus_stale_pool_metrics.json`
- Check: Verify the expanded stale-pool headline metrics for Qwen2.5-0.5B-Instruct.
- AI prefill: overall_action_accuracy=0.3137; overall_avg_utility=-0.6324; stale_action_accuracy=0; stale_avg_utility=-0.85; stale_over_answer_rate=0.8
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-003 | metric_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json`
- Check: Verify the expanded stale-pool headline metrics for Qwen2.5-1.5B-Instruct.
- AI prefill: overall_action_accuracy=0.7255; overall_avg_utility=-0.1863; stale_action_accuracy=0.7333; stale_avg_utility=0.1; stale_over_answer_rate=0.2667
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-004 | metric_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json`
- Check: Verify the expanded stale-pool headline metrics for DeepSeek-R1-Distill-Qwen-1.5B.
- AI prefill: overall_action_accuracy=0.2157; overall_avg_utility=-0.402; stale_action_accuracy=0.2667; stale_avg_utility=-0.3; stale_over_answer_rate=0.3333
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-005 | scale_delta_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_05b_day1_quick_plus_stale_pool_metrics.json | outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json`
- Check: Verify the overall Qwen 0.5B -> 1.5B scale delta on the expanded stale-pool split.
- AI prefill: action_accuracy_delta=+0.4118; avg_utility_delta=+0.4461
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-006 | scale_delta_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_05b_day1_quick_plus_stale_pool_metrics.json | outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json`
- Check: Verify the stale-premise Qwen 0.5B -> 1.5B scale delta on the expanded split.
- AI prefill: stale_action_accuracy_delta=+0.7333; stale_over_answer_delta=-0.5333
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-007 | matched_style_delta_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json | outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json`
- Check: Verify the overall matched 1.5B reasoning-vs-instruct delta on the expanded stale-pool split.
- AI prefill: action_accuracy_delta=-0.5098; avg_utility_delta=-0.2157
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-008 | matched_style_delta_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json | outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json`
- Check: Verify the stale-premise matched 1.5B reasoning-vs-instruct delta on the expanded split.
- AI prefill: stale_action_accuracy_delta=-0.4666; stale_over_answer_delta=+0.0666
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-009 | action_label_failure_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_15b_day1_quick_plus_stale_pool.jsonl`
- Check: Verify the wrong-action update-mention audit claim for Qwen2.5-1.5B-Instruct.
- AI prefill: stale_n=15; correct_challenge=11; wrong_action=4; wrong_plus_update=4; answer_plus_update=4
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-CL-010 | action_label_failure_claim | high

- Status: `pending`
- Source artifact: `outputs/day1/qwen25_05b_day1_quick_plus_stale_pool.jsonl`
- Check: Verify the wrong-action update-mention audit claim for Qwen2.5-0.5B-Instruct.
- AI prefill: stale_n=15; correct_challenge=0; wrong_action=15; wrong_plus_update=4; answer_plus_update=3
- Decision fields to fill in CSV: `human_decision`, `human_notes`

## HV-EX-003 | example_gold_label | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt contain a false or stale premise that should be challenged rather than answered?
- AI prefill: gold_action=challenge; source=PCBench; slice=false_premise; gold_answer=9; gold_response=The question contains an incorrect premise: The bag has 24 cookies.. The supported premise is: Th...; prompt=Jenny buys 1 bag of cookies a week. The bag has 36 cookies. The bag has 24 cookies. She puts 4 cookies in her son's lunch box 5 days a we...
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `pcbench-challenge-356`
- Source: `PCBench`
- Slice: `false_premise`
- Gold action: `challenge`
- Gold answer: 9
- Gold response: The question contains an incorrect premise: The bag has 24 cookies.. The supported premise is: The bag has 36 cookies.. If the premise is repaired, the correct answer is 9.

### Prompt

```text
Jenny buys 1 bag of cookies a week. The bag has 36 cookies. The bag has 24 cookies. She puts 4 cookies in her son's lunch box 5 days a week. Her husband eats 1 cookie a day for 7 days. Jenny eats the rest of the cookies. How many cookies does Jenny eat?
```

## HV-EX-004 | example_gold_label | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt contain a false or stale premise that should be challenged rather than answered?
- AI prefill: gold_action=challenge; source=PCBench; slice=false_premise; gold_answer=$0.99$; gold_response=The question contains an incorrect premise: \sum ^{7}_{i=1}(x_i-\overline{x})^2 = (1-4)^2+(2-4)^2...; prompt=I am a beginner in mathematics. I will provide you with a math problem and its corresponding solution process. I will ask you some questi...
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `pcbench-challenge-1078`
- Source: `PCBench`
- Slice: `false_premise`
- Gold action: `challenge`
- Gold answer: $0.99$
- Gold response: The question contains an incorrect premise: \sum ^{7}_{i=1}(x_i-\overline{x})^2 = (1-4)^2+(2-4)^2+(3-4)^2+(4-4)^2+(5-4)^2+(6-4)^2+(7-4)^2 = 24，. The supported premise is: \sum ^{7}_{i=1}(x_i-\overline{x})^2 = (1-4)^2+(2-4)^2+(3-4)^2+(4-4)^2+(5-4)^2+(6-4)^2+(7-4)^2 = 28，. If the premise is repaired, the correct answer is $0.99$.

### Prompt

```text
I am a beginner in mathematics. I will provide you with a math problem and its corresponding solution process. I will ask you some questions about the solution. Please answer them.### Problem:
$某种机械设备随着使用年限的增加，它的使用功能逐渐减退，使用价值逐年减少，通常把它使用价值逐年减少的“量”换算成费用，称之为“失效费".某种机械设备的使用年限x(单位：年)与失效费y(单位：万元)的统计数据如下表所示：$

| 使用年限x(单位：年) |   1  |   2  |  3   |  4   |  5   |   6   |  7   |
| ----- | ---- | ---- | ---- | ---- | ---- | ----- | ---- |
| 失效费y(单位：万元)  | 2.90 | 3.30 | 3.60 | 4.40 | 4.80 | 5.20  | 5.90 |

参考公式：
$相关系数r=\frac{{\sum \limits^{{n}}_{{i=1}}(x_i-\overline{{x}})(y_i-\overline{{y}})}}{{\sqrt{{\sum \limits^{{n}}_{{i=1}}(x_i-\overline{{x}})^2\sum \limits^{{n}}_{{i=1}}(y_i-\overline{{y}})^2}}}}.$
$线性回归方程\hat{{y}}=\hat{{b}}x+\hat{{a}}中斜率和截距的最小二乘估计公式：\hat{{b}}=\frac{{\sum \limits^{{n}}_{{i=1}}(x_i-\overline{{x}})(y_i-\overline{{y}})}}{{\sum \limits^{{n}}_{{i=1}}(x_i-\overline{{x}})^2}}，\hat{{a}}=\overline{{y}}-\hat{{b}}\overline{{x}}.$
$参考数据：\sum \limits^{{7}}_{{i=1}}(x_i-\overline{{x}})(y_i-\overline{{y}})=14.00，$
$\sum \limits^{{7}}_{{i=1}}(y_i-\overline{{y}})^2=7.08，\sqrt{{198.24}}\approx 14.08.$
$由上表数据可知，可用线性回归模型拟合y与x的关系，请用相关系数加以说明；(精确到0.01)$
### Solution:
由题意，知 \overline{x} = \frac{1+2+3+4+5+6+7}{7} = 4, \overline{y} = \frac{2.90+3.30+3.60+4.40+4.80+5.20+5.90}{7} = 4.30, \sum ^{7}_{i=1}(x_i-\overline{x})^2 = (1-4)^2+(2-4)^2+(3-4)^2+(4-4)^2+(5-4)^2+(6-4)^2+(7-4)^2 = 24， \Rightarrow r = \frac{14.00}{\sqrt{28\times 7.08}} = \frac{14.00}{\sqrt{198.24}} \approx \frac{14.00}{14.08} \approx 0.99. 由于 y 与 x 的相关系数约为0.99， 所以 y 与 x 的线性相关程度相当大，从而可以用线性回归模型拟合 y 与 x 的关系.
### My query about the solution:为什么要计算 \overline{x} 和 \overline{y} 呢？
```

## HV-EX-005 | example_gold_label | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt contain a false or stale premise that should be challenged rather than answered?
- AI prefill: gold_action=challenge; source=stale-fact-seed; slice=stale_premise; gold_response=The premise is outdated: the country name changed to Türkiye at the United Nations in June 2022.; source_url=https://turkiye.un.org/en/184798-turkeys-name-changed-t%C3%BCrkiye; prompt=Why is the UN still using Turkey instead of Türkiye?
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `stale-seed-008`
- Source: `stale-fact-seed`
- Slice: `stale_premise`
- Gold action: `challenge`
- Gold response: The premise is outdated: the country name changed to Türkiye at the United Nations in June 2022.
- Stale claim: The UN still uses Turkey as the country's name.
- Corrected fact: The UN uses Türkiye.
- Source URL: https://turkiye.un.org/en/184798-turkeys-name-changed-t%C3%BCrkiye

### Passages

1. Background: The country was commonly referred to in English as Turkey.
2. Update: The country's name changed to Türkiye at the United Nations after an official request received on June 1, 2022.

### Prompt

```text
Why is the UN still using Turkey instead of Türkiye?
```

## HV-EX-006 | example_gold_label | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt contain a false or stale premise that should be challenged rather than answered?
- AI prefill: gold_action=challenge; source=PCBench; slice=false_premise; gold_answer=7 \frac{1}{3}; gold_response=The question contains an incorrect premise: The expected number of cartons needed to collect '虎虎生...; prompt=Brave NiuNiu (a milk drink company) organizes a promotion during the Chinese New Year: one gets a red packet when buying a carton of milk...
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `pcbench-challenge-233`
- Source: `PCBench`
- Slice: `false_premise`
- Gold action: `challenge`
- Gold answer: 7 \frac{1}{3}
- Gold response: The question contains an incorrect premise: The expected number of cartons needed to collect '虎虎生威' is always 6, regardless of the probabilities of obtaining each required character in the red packets.. The supported premise is: The expected number of cartons needed to collect '虎虎生威' depends on the probabilities of obtaining each required character in the red packets.. If the premise is repaired, the correct answer is 7 \frac{1}{3}.

### Prompt

```text
Brave NiuNiu (a milk drink company) organizes a promotion during the Chinese New Year: one gets a red packet when buying a carton of milk of their brand, and there is one of the following characters in the red packet "虎"(Tiger), "生"(Gain), "威"(Strength). If one collects two "虎", one "生" and one "威", then they form a Chinese phrases "虎虎生威" (Pronunciation: hu hu sheng wei), which means "Have the courage and strength of the tiger". This is a nice blessing because the Chinese zodiac sign for the year 2022 is tiger. Soon, the product of Brave NiuNiu becomes quite popular and people hope to get a collection of "虎虎生威". Suppose that the characters in every packet are independently random, and each character has probability $\frac{{1}}{{3}}$. The expected number of cartons needed to collect '虎虎生威' is always 6, regardless of the probabilities of obtaining each required character in the red packets. What is the expectation of cartons of milk to collect "虎虎生威" (i.e. one collects at least 2 copies of "虎", 1 copy of "生", 1 copy of "威")? Options: (A) $6 \frac{{1}}{{3}}$, (B) $7 \frac{{1}}{{3}}$, (C) $8 \frac{{1}}{{3}}$, (D) $9 \frac{{1}}{{3}}$, (E) None of the above.
```

## HV-EX-008 | example_gold_label | high

- Status: `pending`
- Source artifact: `data/processed/day1_quick_plus_stale_pool.jsonl`
- Check: Does the prompt contain a false or stale premise that should be challenged rather than answered?
- AI prefill: gold_action=challenge; source=stale-fact-seed; slice=stale_premise; gold_response=The premise is outdated: the Raiders officially became the Las Vegas Raiders on January 22, 2020.; source_url=https://www.raiders.com/news/las-vegas-raiders-silver-and-black-officially-welcomed-to-the-silver-state; prompt=Why are the Raiders still the Oakland Raiders?
- Decision fields to fill in CSV: `human_decision`, `human_notes`

### Example Context

- Example ID: `stale-seed-015`
- Source: `stale-fact-seed`
- Slice: `stale_premise`
- Gold action: `challenge`
- Gold response: The premise is outdated: the Raiders officially became the Las Vegas Raiders on January 22, 2020.
- Stale claim: The Raiders are still the Oakland Raiders.
- Corrected fact: The NFL team is the Las Vegas Raiders.
- Source URL: https://www.raiders.com/news/las-vegas-raiders-silver-and-black-officially-welcomed-to-the-silver-state

### Passages

1. Background: The Raiders franchise previously played as the Oakland Raiders.
2. Update: The Raiders announced on January 22, 2020 that they officially became the Las Vegas Raiders.

### Prompt

```text
Why are the Raiders still the Oakland Raiders?
```
