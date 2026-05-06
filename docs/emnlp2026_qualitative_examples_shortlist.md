# Qualitative Examples Shortlist

Status: shortlist from completed Qwen2.5-1.5B quick+stale artifacts plus DeepSeek-R1-Distill-Qwen-7B dev artifacts.

## Selection Principle

Use examples that reveal the wrong next action, not merely a wrong final answer. Each manuscript example should show:

1. the input defect or lack of defect,
2. the gold action,
3. the model action,
4. the utility loss in one sentence.

## Candidate Examples

| Role In Paper | Example ID | Slice | Gold Action | Qwen2.5-1.5B Action | Why It Helps |
| --- | --- | --- | --- | --- | --- |
| Stale-premise over-answering | `stale-seed-002` | stale_premise | `challenge` | `answer` | The prompt asks why Facebook still trades as `FB`; the model answers while itself mentioning the ticker changed to `META`. This cleanly shows answering through a stale premise. |
| False-premise rationalization | `pcbench-challenge-1196` | false_premise | `challenge` | `answer` | The user asks about a flawed step in a provided math solution; the model explains the flawed step instead of interrupting the premise. |
| Answerable-control hesitation | `pcbench-answer-356` | answerable_control | `answer` | `challenge` | A simple cookie-counting problem is fully specified, but the model claims the information is incomplete. This illustrates over-caution on clean inputs. |
| Harder answerable-control hesitation | `pcbench-answer-233` | answerable_control | `answer` | `challenge` | A probability problem has enough information and a gold answer, but the model treats the prompt as incomplete. Use only if a more technical example is desired. |
| Conflict but answerable | `qacc-dev-379` | conflicting_evidence | `answer` | `answer` | Retrieved passages contain noise and conflict, but enough evidence supports "Julius Caesar." This is a useful positive boundary case: conflict alone does not imply `abstain`. |
| 7B false-premise non-interruption | `pcbench-challenge-844` | false_premise | `challenge` | `abstain` | DeepSeek-R1-Distill-Qwen-7B reasons about the problem but does not explicitly correct the false `3^t` premise to the supported `2^t` premise. |
| 7B clean-answer over-abstention | `pcbench-answer-501` | answerable_control | `answer` | `abstain` | The 7B reasoning checkpoint works through a valid problem but fails to commit to the supported answer, illustrating over-abstention on clean inputs. |
| 7B conflict positive boundary | `qacc-dev-287` | conflicting_evidence | `answer` | `answer` | The 7B checkpoint correctly treats noisy retrieval as answerable when the evidence still supports Brooks Koepka. |

## Manuscript-Ready Mini Examples

### Stale Premise

Prompt excerpt: "Why is Facebook still trading under the ticker FB?"

Gold next action: `challenge`.

Model next action: `answer`.

Use in paper:
The model gives an answer that contains the correction, saying Meta changed its ticker from `FB` to `META`, but still frames the response as if the stale premise should be answered. This is the central failure mode: factual knowledge is present, but the next action is wrong.

### False Premise

Prompt excerpt: the user asks why a flawed logarithmic approximation is used in a proposed solution.

Gold next action: `challenge`.

Model next action: `answer`.

Use in paper:
The model explains the flawed step instead of challenging it, showing how fluent reasoning can rationalize a bad premise when the task is framed as answer generation.

### Answerable Control

Prompt excerpt: Jenny buys 36 cookies, packs 20 for her son, her husband eats 7, and the question asks how many Jenny eats.

Gold next action: `answer`.

Model next action: `challenge`.

Use in paper:
The input is fully specified and the answer is 9, but the model claims the problem is incomplete. This guards against an intervention that merely becomes more cautious.

### Conflict But Answerable

Prompt excerpt: "Who was told beware the ides of March?"

Gold next action: `answer`.

Model next action: `answer`.

Use in paper:
Despite noisy retrieved passages, enough evidence supports Julius Caesar. This example helps explain why the ontology does not reduce all evidence conflict to abstention.

## 7B-Specific Use

Use `pcbench-challenge-844` and `pcbench-answer-501` in the Results or Error Analysis section if the paper needs to explain why the 7B reasoning result is not simply "more cautious is safer." The model often produces substantial reasoning text, but the action remains wrong: either it does not interrupt a false premise, or it refuses to commit on a clean answerable problem.

Still useful to add before submission:

- one 7B stale-premise example from the quick+stale run,
- one example where Qwen2.5-1.5B and DeepSeek-R1-Distill-Qwen-7B make different action choices on the same item.
