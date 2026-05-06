# Boundary-Case Table For The Action Ontology

Status: paper/appendix material. This table compresses the ontology into reviewer-facing boundary rules.

## Main Boundary Table

| Boundary | Choose This | Not This | Decisive Question | Example Signal |
| --- | --- | --- | --- | --- |
| Missing slot vs false premise | `ask` | `challenge` | Is the user missing information, or assuming something incorrect? | "Which one do you mean?" is useful only when the premise itself is not wrong. |
| False/stale premise vs answer | `challenge` | `answer` | Would directly answering silently accept a premise that should be corrected first? | A recoverable intended question still receives `challenge` if the stated premise is false. |
| False/stale premise vs insufficient support | `challenge` | `abstain` | Can the defect be corrected with supported information? | Use `challenge` when the corrected fact is known; use `abstain` when even the correction is unsupported. |
| Missing slot vs insufficient support | `ask` | `abstain` | Could one user follow-up plausibly unlock the answer? | Use `ask` for missing entity/time/preference; use `abstain` for unknowable future facts or absent evidence. |
| Retrieval conflict vs answer | `answer` | `abstain` | Is there still enough reliable support for one answer despite noise? | Retrieval conflict alone does not force `abstain`. |
| Conflict with no authority resolution | `abstain` | `answer` | Can the benchmark justify preferring one passage? | If the evidence remains unresolved, the next best action is not to invent a tie-breaker. |
| Caution vs answerability | `answer` | `ask` or `abstain` | Is the item already sufficiently specified and supported? | Do not reward caution when the helpful action is a concise answer. |

## Manuscript Wording

We label the assistant's next best action, not the surface style of its response. The key boundary is whether the defect is user-resolvable (`ask`), premise-level (`challenge`), evidence-level (`abstain`), or absent enough to answer directly (`answer`). This distinction prevents the benchmark from collapsing into either generic refusal evaluation or standard question answering: a model can fail by answering through a false premise, by challenging a valid answerable question, or by abstaining when enough support exists.

## Appendix Note

The stale-premise slice is treated as a premise-defect case when the prompt assumes an outdated fact that should be corrected before answering. It differs from ordinary temporal QA because the model is not merely asked for the current fact; it is asked a question whose wording would make a stale assumption valid unless interrupted. It differs from conflicting-evidence abstention because a stale premise often has a supported correction, while unresolved conflict may not.
