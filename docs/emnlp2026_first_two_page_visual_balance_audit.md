# EMNLP 2026 First-Two-Page Visual Balance Audit

Date: 2026-04-27

Status: current human-scale PDF visual-balance pass after the first-two-page oral-readiness story audit.

Audit input:

- Rendered `paper/main.pdf` pages 1-2 to PNG at 2x scale with PyMuPDF.
- Visual inspection of page density, title/abstract balance, Figure 1 readability, contribution visibility, and Related Work handoff.
- Cross-check against `docs/emnlp2026_first_two_page_oral_readiness_audit.md`.

## Severity Summary

- `CRITICAL`: 0
- `MAJOR`: 0
- `MINOR`: 4

## Page-Level Findings

### CLOSED 1: Page 1 is dense but readable and story-forward.

The title and abstract are centered cleanly, and the abstract ends with the field-level takeaway that fluent answer generation and chain-of-thought reasoning do not guarantee the right first move. The Introduction starts on page 1 and reaches the Facebook ticker example plus the explicit wrong-first-move phrase: selecting `answer` when `challenge` is required.

Current judgment:
No re-layout needed. The page is dense, but the density is doing useful work: problem, example, task gap, and action ontology all appear before page 2.

### CLOSED 2: Figure 1 is readable at paper scale.

Figure 1 occupies the top of page 2 and remains legible at rendered PDF scale. The four input/evidence cases, central next-action decision, and four action outputs are visually separable. The caption is long, but it states the evaluated object and preserves the first-move action framing.

Current judgment:
Keep Figure 1 at the current size unless later prose expansion forces page pressure. Do not shrink it below current scale without another visual check.

### CLOSED 3: Contributions and Related Work both appear on page 2.

The benchmark/result preview resumes under Figure 1, the four contributions appear before Related Work, and the first Related Work paragraph repeats the same boundary: before judging answer text, the assistant must decide whether answering is the right next action at all.

Current judgment:
This is good for oral-readiness. Reviewers see the task schematic, empirical surprise, contribution list, and positioning handoff within two pages.

### CLOSED 4: The first-two-page visual path is coherent.

The visual reading order is:

1. Title: "Critique or Clarify?" plus next-action selection.
2. Abstract: task, benchmark, 7B result, intervention caveat, right-first-move takeaway.
3. Introduction example: Facebook `FB` stale premise.
4. Figure 1: action before generation.
5. Contributions and Related Work boundary.

This path supports the intended reviewer memory hook: the paper evaluates the assistant's first move, not only the final answer.

## Minor Findings

### MINOR 1: The abstract is long.

Risk:
The abstract carries task, benchmark construction, 7B result, intervention caveat, and thesis. It is readable, but it is doing many jobs.

Decision:
Keep for now because the abstract must front-load the oral-level contribution. Compress only if the final PDF needs space or if a human coauthor finds it breathless.

### MINOR 2: The Figure 1 caption is long.

Risk:
The caption adds visual weight to the top of page 2.

Decision:
Accept because it makes the figure self-contained. If space pressure appears, shorten the caption only after confirming the figure itself still carries the first-move framing.

### MINOR 3: Contributions are prose-only.

Risk:
The four contribution statements are visible but not visually isolated as bullets under ACL style.

Decision:
Keep prose format for compactness. Do not convert to bullets unless page flow or reviewer readability clearly improves.

### MINOR 4: Related Work starts on page 2 but continues the density.

Risk:
The reader moves from contributions directly into citation-heavy prose.

Decision:
Accept because the first Related Work paragraph is short and starts with the key positioning boundary. Re-check after citation edits.

## Regression Rule

Any future edit that affects pages 1-2 should preserve all of the following:

- Abstract ends with the right-first-move thesis.
- The Facebook `FB` example appears on page 1.
- Figure 1 appears on page 2 and remains legible at paper scale.
- Contributions appear before Related Work.
- Related Work begins with the "before judging answer text" boundary.

## Recommendation

The first two pages are visually acceptable for an internal oral-readiness pass. The next highest-leverage work is reviewer-attack hardening: write concise planned responses for benchmark-soup, utility-weight, reasoning-overclaim, and intervention-overclaim objections.
