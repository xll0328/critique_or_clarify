# EMNLP 2026 First-Two-Page Oral-Readiness Audit

Date: 2026-04-27

Status: current PDF-level story audit after the Figure 2 oral-readiness polish and first-page wrong-first-move wording lock.

Audit input:

- PDF text extraction from `paper/main.pdf` pages 1-2 using `pypdf`.
- Source check over `paper/sections/00_abstract.tex`, `paper/sections/01_introduction.tex`, `paper/sections/02_related_work.tex`, and `paper/sections/02_task.tex`.
- Existing story-flow lock in `tests/test_paper_story_flow.py`.

## Severity Summary

- `CRITICAL`: 0
- `MAJOR`: 0
- `MINOR`: 3

## Oral Thesis

The first two pages now support this one-sentence reviewer takeaway:

> LLMs fail not only when they generate the wrong answer, but when they choose the wrong first move under defective inputs; next-action calibration measures whether the assistant should answer, ask, challenge, or abstain before generating.

## Closed Checks

### CLOSED 1: Page 1 names the field-level evaluation gap.

PDF page 1 opens by contrasting answer generation with the assistant's first decision about whether answering is appropriate. The abstract states that answerable controls, false premises, stale premises, and conflicting evidence share one action-decision record, action ontology, metric suite, and completed human-validation queue.

### CLOSED 2: The running example now names the wrong-first-move failure.

The Facebook ticker example appears on page 1 and states the failure as choosing the wrong first move: selecting `answer` when `challenge` is required. This makes the task concrete before the paper introduces the full action ontology.

### CLOSED 3: The unified-object argument appears before Figure 1.

Page 1 states that the central object is not another defect category but the action decision that precedes generation. This directly addresses the benchmark-soup objection before the figure and before Related Work.

### CLOSED 4: Figure 1 appears at the top of page 2 and is self-contained.

Figure 1 appears before the Introduction resumes on page 2. Its caption says the evaluated object is the first-move action between input/evidence and response, and it lists `answer`, `ask`, `challenge`, and `abstain` in the figure itself.

### CLOSED 5: Results preview and contributions appear before Related Work.

Page 2 includes the Day-1 7B result preview, the four contribution statements, and the start of Related Work. The first Related Work paragraph reinforces the same boundary: before judging answer text, the assistant must decide whether answering is the right next action at all.

## Minor Findings

### MINOR 1: The benchmark-design paragraph is split by Figure 1.

This is acceptable because the split occurs after the unified decision problem is already introduced, and Figure 1 restates the same object. Re-check if Figure 1 placement changes.

### MINOR 2: Page 2 carries many jobs.

Page 2 includes Figure 1, benchmark design, results preview, contributions, and the start of Related Work. This is dense but useful for oral-readiness because it gets the full story into the first two pages. Re-check if future prose expansion pushes contributions later.

### MINOR 3: The intervention appears only in the abstract and contributions before page 3.

This is intentional. The benchmark/evaluation contribution remains the lead claim; the intervention should stay scoped as a calibration probe unless stronger controller evidence lands.

## Regression Rule

Any edit that changes the abstract, first Introduction page, Figure 1, or the opening Related Work handoff should preserve these fragments:

- `do not guarantee the right first move`
- `selecting \\texttt{answer} when \\texttt{challenge} is required`
- `not another defect category, but the action decision that precedes generation`
- `the evaluated object is the first-move action`
- `before judging the answer text, the assistant must decide whether answering is the right next action at all`

## Recommendation

The first two pages are ready for internal oral-readiness review. The next useful pass should be a human-scale PDF read for compression and visual balance, not another framing rewrite.
