# EMNLP 2026 Oral Readability Lock

Date: 2026-04-27

Status: compiled-PDF 90-second reviewer-read lock for the current submission-freeze draft. This is an internal oral-readiness gate, not final human sign-off.

## Audit Inputs

- `paper/main.pdf`, extracted with `pypdf`, 13 pages.
- PDF pages 1-2 for title, abstract, running example, Figure 1, contributions, and Related Work handoff.
- PDF pages 5-7 for main results table, Figure 2, intervention scope, and qualitative memory hook.
- Existing first-two-page and figure audits: `docs/emnlp2026_first_two_page_oral_readiness_audit.md`, `docs/emnlp2026_first_two_page_visual_balance_audit.md`, and `docs/emnlp2026_figure2_audit.md`.
- Final local clarity pass: `docs/emnlp2026_final_local_clarity_pass.md`.

## Severity Summary

- `CRITICAL`: 0
- `MAJOR`: 0
- `MINOR`: 3

## 90-Second Reviewer Takeaway

The current PDF supports this short oral-level summary:

> This paper argues that assistants should be evaluated on the first action before generation: answer, ask, challenge, or abstain. It builds a shared action-decision benchmark for defective inputs, shows that open instruction and reasoning checkpoints remain far from saturated, and finds that reasoning traces do not guarantee calibrated first moves.

## Closed Checks

### CLOSED 1: The title and abstract expose the full paper arc.

Page 1 names the task as "next-action selection under defective user inputs." The abstract includes the shared action ontology, completed human-validation queue, DeepSeek-R1-Distill-Qwen-7B result, intervention caveat, and right-first-move thesis.

Oral-readability judgment:
No framing rewrite is needed. The abstract is dense, but it gives a reviewer the task, evidence, empirical surprise, and scope before the Introduction.

### CLOSED 2: The page-1 running example makes the failure concrete.

The Facebook `FB` example appears on page 1 and states that the failure is selecting `answer` when `challenge` is required. This creates a memorable wrong-first-move example before the paper introduces all four actions.

Oral-readability judgment:
Keep this example stable unless a stronger stale-premise example replaces it everywhere, including Figure 1, qualitative analysis, and reviewer-response seeds.

### CLOSED 3: Figure 1 is the oral schematic.

Figure 1 appears at the top of page 2. It shows answerable control, false premise, stale premise, and conflicting evidence flowing into one next-action decision, then `answer`, `ask`, `challenge`, or `abstain`.

Oral-readability judgment:
This is the figure a reviewer should remember. Do not shrink it or move it later without rerunning the first-two-page visual audit.

### CLOSED 4: Page 2 closes the intro loop before Related Work.

After Figure 1, page 2 resumes the benchmark setup, reports the 7B reasoning checkpoint preview, lists four contributions, and then starts Related Work with the "before judging answer text" boundary.

Oral-readability judgment:
The first two pages now answer "what is new?" and "why is this not benchmark soup?" before citation-heavy positioning begins.

### CLOSED 5: The main results pages carry the empirical surprise.

Table 2 on page 5 reports the completed local model matrix and shows that DeepSeek-R1-Distill-Qwen-7B reaches `0.3667` action accuracy and `-0.4313` utility. Figure 2 on page 6 states the visual takeaway: caution is not monotonic safety, because the 7B reasoning checkpoint remains weak on false/stale premise interruption while also abstaining heavily on clean answerable controls.

Oral-readability judgment:
The empirical surprise is visible in both table and figure form. Keep the reasoning claim scoped to the current prompt/parsing protocol.

### CLOSED 6: The intervention is useful but not allowed to overtake the benchmark.

Pages 5-6 report `decision_first` as improving Qwen2.5-1.5B quick+stale utility from `-0.2188` to `-0.1375`, action accuracy from `0.775` to `0.85`, and over-answer rate from `0.05` to `0`. The same paragraph says that more cautious variants over-challenge or damage answer-supported accuracy, and Table 4 remains at the Section 6 / Qualitative Analysis handoff in the current 13-page PDF.

Oral-readability judgment:
This is correctly framed as a narrow calibration lever. Do not promote it to a complete method without stronger controller evidence.

### CLOSED 7: The qualitative section gives the memory hook a second pass.

Pages 6-7 return to the Facebook stale-premise example and explain that the utility loss is not missing factual knowledge, but accepting an outdated framing as an answer request. The section also names the false-premise reasoning failure: fluent intermediate reasoning can rationalize a bad premise instead of interrupting it.

Oral-readability judgment:
The qualitative section reinforces the paper's central distinction between answer content and first action.

## Minor Findings

### MINOR 1: The abstract remains high-density.

The abstract carries task, benchmark, validation, 7B result, intervention caveat, and thesis. This is acceptable for the current oral-readiness target, but final human PDF review should check whether it feels breathless.

### MINOR 2: Page 2 carries many jobs.

Page 2 contains Figure 1, benchmark setup, results preview, contributions, and Related Work. This is dense but productive. Re-check only if edits push contributions off page 2.

### MINOR 3: Figure 2 is information-rich.

Figure 2 has three panels, utility labels, marker-size encoding, and a shared legend. It is useful for oral framing, but final PDF review should confirm the utility labels remain readable in the submitted PDF.

## Regression Rule

After any paper-facing edit, preserve these oral-readability anchors:

- `Critique or Clarify?` and `next-action selection under defective user inputs` in the title block.
- The page-1 Facebook `FB` stale-premise example.
- The phrase that answer generation and chain-of-thought reasoning do not guarantee the right first move.
- Figure 1 on page 2 as the action-before-generation schematic.
- Page-2 contributions before Related Work.
- Table 2 and Figure 2 both carrying the DeepSeek-R1-Distill-Qwen-7B calibration surprise.
- `decision_first` framed as a calibration lever, not a complete method.

## Lock Decision

Oral Readability Lock is closed for the current internal freeze. The next high-leverage edits should be local clarity and final human PDF review, not another framing rewrite.
