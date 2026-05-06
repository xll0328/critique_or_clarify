# EMNLP 2026 Virtual Prereview Literature Triage

Date: 2026-05-06

Status: first-pass verification of the virtual prereview's suggested missing related work. Do not add unverified entries to `paper/references.bib`.

## Rule

Treat reviewer-suggested titles as leads, not citations. A work can enter the bibliography only after:

1. title and authors are verified through a paper index or primary paper page;
2. the local relevance to next-action selection is stated;
3. the paper text or abstract is read enough to support the exact related-work sentence;
4. the citation is placed near the claim it supports.

## Verified Leads

| Status | Suggested Item | Verified Metadata | Relevance | Next Action |
| --- | --- | --- | --- | --- |
| verified | `AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions` | Kirichenko, Ibrahim, and Chaudhuri, 2025, arXiv DOI `10.48550/arxiv.2506.09038` | Directly relevant to hard abstention and unanswerable questions. | Read abstract/full text before adding to abstention paragraph. |
| verified | `Judge Before Answer: Can MLLM Discern the False Premise in Question?` | Li, Fang, and Zhao, 2025, arXiv DOI `10.48550/arxiv.2510.10965` | Directly relevant to false-premise detection before answering, although multimodal. | Read enough to compare text-only vs multimodal false-premise framing. |
| verified | `Premise Order Matters in Reasoning with Large Language Models` | Chen, Chi, and Wang, 2024, arXiv DOI `10.48550/arxiv.2402.08939` | Methodologically adjacent for evidence/premise presentation sensitivity. | Consider only if protocol-sensitivity discussion needs support. |
| title-mismatch | `Metacognitive Prompting Improves Understanding in LLMs` | Scite resolves `Metacognitive Prompting Improves Understanding in Large Language Models`, Wang and Yun, 2023, arXiv DOI `10.48550/arxiv.2308.05342` | Relevant to prompt-level self-monitoring, but the prereview title/year were imprecise. | Verify primary paper before citing near intervention. |

## Not Yet Verified

These should stay out of `paper/references.bib` until a reliable paper record is found:

- `PAVE: Premise-Aware Validation and Editing for Retrieval-Augmented LLMs`
- `The Entity-Deduction Arena: A Playground for Probing the Conversational Reasoning and Planning Capabilities of LLMs`
- `I-CALM: Incentivizing Confidence-Aware Abstention for LLM Hallucination Mitigation`
- `ProactiveBench: Benchmarking Proactiveness in Multimodal Large Language Models`
- `LLM-as-Judge Is the Wrong Default: Reliable Evaluation via Criteria-Based Decomposition`
- `Over-Searching in Augmented LLMs`

## Current Decision

No bibliography edit in this chunk. The safe move is to first stabilize benchmark-construction, parsing, and utility validity. Related-work additions should happen in a separate citation pass so the paper does not inherit hallucinated reviewer references.

