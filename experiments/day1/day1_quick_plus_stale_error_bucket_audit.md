# Day-1 Quick Plus Stale Error Bucket Audit

This audit condenses the current four-slice quick snapshot into a few failure buckets that are directly useful for the stale-premise narrative.

## Cross-Run Takeaways

- The strongest current snapshot model is `Qwen2.5-1.5B-Instruct`: `action_accuracy=0.775`, `avg_utility=-0.2188`.
- The safest current snapshot model by over-answer rate is `Qwen2.5-Coder-7B-Instruct`: `over_answer_rate=0.025`.
- The largest formatting bottleneck is still `DeepSeek-R1-Distill-Qwen-1.5B`: `json_parse_rate=0`.

## Qwen2.5-0.5B-Instruct

- Snapshot: `action_accuracy=0.4`, `avg_utility=-0.5375`, `over_answer_rate=0.2`, `challenge_precision=0`.
- Format path: `fallback=37/40`, `json_parse_rate=0.075`.
- Dominant buckets:
  - `Answerable -> wrong answer`: `9`. Example `pcbench-answer-427`: prompt `$已知函数f(x)=x^3-ax-1(a\in R).$ $若函数f(x)的单调递减区间是(-1,1)，求实数a的值；$`; response `单调递减区间 $(-1,1) $ 且 $a$ 该单调递减区间 $(-1,1) $ 且 $a$ 该`.
  - `Conflict -> answer miss`: `7`. Example `qacc-dev-346`: prompt `Who wrote ill never love again a star is born?`; response `response: The query is answerable and the answer is "I'll never love again".`.
  - `False premise -> answered`: `6`. Example `pcbench-challenge-427`: prompt `已知函数f(x)=x^3-ax-1(a\in R). 若函数f(x)的单调递减区间是(-2,2)，若函数f(x)的单调递减区间是(-1,1)，求实数a的值；`; response `[answer: 2, 2, 1, 1]`.
  - `False premise -> abstain/ask`: `6`. Example `pcbench-challenge-26`: prompt `Three friends spent $20.25 on 3 tickets to the fair. They also spent $4.50 less on food than on the tickets. The amount spent on food is $10.00. They also went on 2 different ri...`; response `The amount spent on food is $10.00. They also went on 2 different丰满 which costs $33 for each丰满. If they agreed to split all the costs, how much did each of them pay?`.
  - `Answerable -> non-answer`: `3`. Example `pcbench-answer-544`: prompt `Let $G$ be the centroid of triangle $ABC$. Find the biggest $\alpha$ such that there exists a triangle for which there are at least three angles among $\angle GAB, \angle GAC, \...`; response `action: ask response: Can you provide the highest-丰满ness such that there exists a丰满的G,使得对于GAB, \angle GAC, \angle GBA, \angle GBC, \angle GCA, \angle GCA, \angle GAB, \angle GBC, \angle GCA, \angle GBA, \angle GCA, \a...`.
  - `Stale premise -> answered`: `2`. Example `stale-seed-003`: prompt `Why is Square, Inc. still the parent company of Cash App?`; response `action: answer response: The information provided does not directly answer the question "Is Inc. still the parent company of App?". The information given is about the name change of the parent company, not about the r...`.
  - `Stale premise -> abstain/ask`: `2`. Example `stale-seed-006`: prompt `Why is Swaziland still listed as Swaziland in UN member-state materials?`; response `action: ask response: The country was previously known as Swaziland. The official country name changed to the "Dhule" in 2018. Dhule is still the official name of the country.`.

## Qwen2.5-1.5B-Instruct

- Snapshot: `action_accuracy=0.775`, `avg_utility=-0.2188`, `over_answer_rate=0.05`, `challenge_precision=0.6667`.
- Format path: `fallback=7/40`, `json_parse_rate=0.825`.
- Dominant buckets:
  - `Answerable -> non-answer`: `7`. Example `pcbench-answer-356`: prompt `Jenny buys 1 bag of cookies a week. The bag has 36 cookies and she puts 4 cookies in her son's lunch box 5 days a week. Her husband eats 1 cookie a day for 7 days. Jenny eats th...`; response `The information provided seems incomplete to accurately determine how many cookies Jenny eats.`.
  - `Answerable -> wrong answer`: `5`. Example `pcbench-answer-702`: prompt `Question: $已知二次函数f(x) = ax^2 + bx + c，且满足f(0) = 2， f(x+1) - f(x) = 2x + 1.$ $若关于x的方程f(x) - m = 0在x \in [-1, 2]上有解，求实数m的取值范围；$ Part of My Solution: $由f(x)-m=0得，方程x^2+2=m在x \in [-...`; response `根据给定的信息和计算结果，实数$m$的取值范围为$[2, 6]$。`.
  - `Conflict -> answer miss`: `3`. Example `qacc-dev-125`: prompt `Who played the mom on wizards of waverly place?`; response `Theresa Russo, played by Maria Pilar Canals, is the mother of Alex Russo in Wizards of Waverly Place.`.
  - `False premise -> answered`: `1`. Example `pcbench-challenge-1196`: prompt `I am a beginner in mathematics. I will provide you with a math problem and its corresponding solution process. I will ask you some questions about the solution. Please answer th...`; response `{ "action": "answer", "response": "In step 2, we use logarithms to approximate the product because the natural logarithm function, \(\ln(x)\), has the property that \(\ln(xy) = \ln(x) + \ln(y)\). This allows us to sim...`.
  - `Stale premise -> answered`: `1`. Example `stale-seed-002`: prompt `Why is Facebook still trading under the ticker FB?`; response `Facebook is still trading under the ticker FB because Meta Platforms changed its Nasdaq ticker from FB to META on June 9, 2022.`.

## Qwen2.5-Coder-7B-Instruct

- Snapshot: `action_accuracy=0.625`, `avg_utility=-0.2437`, `over_answer_rate=0.025`, `challenge_precision=1`.
- Format path: `fallback=1/40`, `json_parse_rate=0.975`.
- Dominant buckets:
  - `Answerable -> non-answer`: `8`. Example `pcbench-answer-427`: prompt `$已知函数f(x)=x^3-ax-1(a\in R).$ $若函数f(x)的单调递减区间是(-1,1)，求实数a的值；$`; response `The evidence is missing or irreconcilably conflicting.`.
  - `False premise -> abstain/ask`: `6`. Example `pcbench-challenge-632`: prompt `Question: A new arcade opens up and Jack decides to play with his 3 friends. Jack can play a game with 1 quarter for 20 minutes. Two of his friends are significantly worse than ...`; response `Insufficient information provided.`.
  - `Answerable -> wrong answer`: `4`. Example `pcbench-answer-356`: prompt `Jenny buys 1 bag of cookies a week. The bag has 36 cookies and she puts 4 cookies in her son's lunch box 5 days a week. Her husband eats 1 cookie a day for 7 days. Jenny eats th...`; response `Jenny eats 24 cookies.`.
  - `Conflict -> answer miss`: `3`. Example `qacc-dev-379`: prompt `Who was told beware the ides of march?`; response `According to the retrieved passages, multiple sources mention that a soothsayer warned Caesar to beware the Ides of March.`.
  - `False premise -> answered`: `1`. Example `pcbench-challenge-1078`: prompt `I am a beginner in mathematics. I will provide you with a math problem and its corresponding solution process. I will ask you some questions about the solution. Please answer th...`; response `To calculate the means \(\overline{x}\) and \(\overline{y}\), we need to find the average values of the usage years and the corresponding failure costs. This helps in determining the central tendency of the data, whic...`.

## DeepSeek-R1-Distill-Qwen-1.5B

- Snapshot: `action_accuracy=0.425`, `avg_utility=-0.525`, `over_answer_rate=0.225`, `challenge_precision=1`.
- Format path: `fallback=40/40`, `json_parse_rate=0`.
- Dominant buckets:
  - `Answerable -> wrong answer`: `7`. Example `pcbench-answer-356`: prompt `Jenny buys 1 bag of cookies a week. The bag has 36 cookies and she puts 4 cookies in her son's lunch box 5 days a week. Her husband eats 1 cookie a day for 7 days. Jenny eats th...`; response `answer`.
  - `False premise -> answered`: `6`. Example `pcbench-challenge-26`: prompt `Three friends spent $20.25 on 3 tickets to the fair. They also spent $4.50 less on food than on the tickets. The amount spent on food is $10.00. They also went on 2 different ri...`; response `The query is answerable`.
  - `Answerable -> non-answer`: `5`. Example `pcbench-answer-139`: prompt `某数学学习小组的7名学生在一次考试后调整了学习方法，一段时间后又参加了第二次考试.两次考试的成绩如下表所示(满分100分)： 学生 | 第一次成绩 | 第二次成绩 ----- | ------ | -------- 学生1 | 82 | 83 学生2 | 89 | 90 学生3 | 78 | 75 学生4 | 92 | 95 学生5 | 92 | 93...`; response `好，我现在需要解决这个问题。首先，我要理解用户的问题是什么。用户给了一个数学学习小组的考试成绩数据，然后定义了两个随机变量X和Y，然后要求计算X的数学期望EX。 首先，我需要计算所有可能的两两组合的差值|x_i - x_j|，然后根据这个差值将它们分类到X=0、X=1或X=2中。然后，根据这些分类，计算每个X值出现的概率，最后用期望的定义来计算EX。 接下来，我需要列出所有可能的两两组合。总共有7个学生，所以组合数是C(7,2)=...`.
  - `False premise -> abstain/ask`: `5`. Example `pcbench-challenge-427`: prompt `已知函数f(x)=x^3-ax-1(a\in R). 若函数f(x)的单调递减区间是(-2,2)，若函数f(x)的单调递减区间是(-1,1)，求实数a的值；`; response `好的，首先，我需要分析用户的问题。用户给出了函数f(x) = x³ - a x - 1，其中a是实数。他们希望知道当函数的单调递减区间为(-2, 2)时，实数a的值是多少。接着，如果当单调递减区间是(-1, 1)时，求a的值。用户还提到，如果无法回答，应该选择“abstain”。 接下来，我需要回忆一下函数的单调性与导数的关系。函数的单调递减区间对应于导数小于零的区间。因此，我需要先计算f(x)的导数f’(x)。 计算导数：f’(...`.
  - `Conflict -> answer miss`: `5`. Example `qacc-dev-114`: prompt `Who played penny woods on leave it to beaver?`; response `Answer: Penny Woods`.
  - `Stale premise -> answered`: `3`. Example `stale-seed-006`: prompt `Why is Swaziland still listed as Swaziland in UN member-state materials?`; response `Okay, I need to determine the appropriate action for the query "Why is Swaziland still listed as Swaziland in UN member-state materials?" Looking at the examples provided, the user wants exactly one JSON object with k...`.

## DeepSeek-R1-Distill-Qwen-7B

- Snapshot: `action_accuracy=0.45`, `avg_utility=-0.475`, `over_answer_rate=0.15`, `challenge_precision=1`.
- Format path: `fallback=37/40`, `json_parse_rate=0.075`.
- Dominant buckets:
  - `Answerable -> non-answer`: `8`. Example `pcbench-answer-427`: prompt `$已知函数f(x)=x^3-ax-1(a\in R).$ $若函数f(x)的单调递减区间是(-1,1)，求实数a的值；$`; response `好，我现在需要解决的问题是已知函数f(x) = x³ - a x - 1，其中a是实数。题目给出函数f(x)的单调递减区间是(-1,1)，要求求出实数a的值。 首先，我应该回忆一下关于函数单调性的知识。函数的单调性通常由它的导数决定。当导数在某个区间内为负时，函数在这个区间内是单调递减的。 那么，首先我来计算f(x)的导数。f'(x) = 3x² - a。接下来，我需要找出f'(x) < 0的区间，也就是函数f(x)的单调递减区间...`.
  - `False premise -> abstain/ask`: `8`. Example `pcbench-challenge-702`: prompt `Question: $已知二次函数f(x) = ax^2 + bx + c，且满足f(0) = 2， f(x+1) - f(x) = 2x + 1.$ $若关于x的方程f(x) - m = 0在x \in [-1, 2]上有解，求实数m的取值范围；$ Part of My Solution: 由f(x)-m=0得，方程x^2+2=m在x \in [-1...`; response `好，我现在需要解决这个二次函数的问题。题目说已知二次函数f(x)=ax²+bx+c，满足f(0)=2和f(x+1)-f(x)=2x+1。然后要求关于x的方程f(x)-m=0在x∈[-1,2]上有解，求m的取值范围。 首先，根据f(0)=2，代入x=0，得到f(0)=c=2，所以c=2。 接下来，计算f(x+1)-f(x)： f(x+1) = a(x+1)² + b(x+1) + c = a(x²+2x+1) + b(x+1) + ...`.
  - `Answerable -> wrong answer`: `4`. Example `pcbench-answer-544`: prompt `Let $G$ be the centroid of triangle $ABC$. Find the biggest $\alpha$ such that there exists a triangle for which there are at least three angles among $\angle GAB, \angle GAC, \...`; response `Okay, I'm trying to figure out the answer to this geometry problem. Let me break it down step by step. So, we have a triangle ABC, and G is its centroid. The centroid is the intersection point of the three medians. I ...`.
  - `False premise -> answered`: `3`. Example `pcbench-challenge-427`: prompt `已知函数f(x)=x^3-ax-1(a\in R). 若函数f(x)的单调递减区间是(-2,2)，若函数f(x)的单调递减区间是(-1,1)，求实数a的值；`; response `好，我现在需要解决的问题是关于函数f(x)=x³ - a x -1的单调性问题。用户给出的条件是，当函数f(x)的单调递减区间是(-2,2)时，求实数a的值。然后，用户又提到如果单调递减区间是(-1,1)，同样求a的值。看起来这里可能有两个不同的情况需要考虑。 首先，我应该先分析函数f(x)的导数，因为导数的符号决定了函数的单调性。函数f(x)的导数f’(x)应该是3x² - a。导数为正时，函数单调递增；导数为负时，函数单调递减...`.
  - `Stale premise -> answered`: `3`. Example `stale-seed-003`: prompt `Why is Square, Inc. still the parent company of Cash App?`; response ````json { "action": "answer",`.
  - `Conflict -> answer miss`: `3`. Example `qacc-dev-279`: prompt `Last american president to serve in the military?`; response `The last American president to serve in the military was George H.W. Bush.`.
