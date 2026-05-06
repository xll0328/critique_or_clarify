# Figure 2 Audit

Figure: `experiments/day1/figures/emnlp2026_figure2_action_calibration.pdf`

Status: oral-readiness polish pass current after adding a shared model-color legend and a stronger finding-first caption.

## Severity Summary

- `CRITICAL`: 0
- `MAJOR`: 0
- `MINOR`: 3

## Findings

### CLOSED 1: Panel C no longer relies on Panel B for model colors.

Previous risk:
If the figure was cropped or if a reader scanned only Panel C, the bars were not self-contained.

Current fix:
The generated figure now includes a shared model-color legend below panels B and C, and Panel C labels that the colors use the shared legend. The paper caption also names this legend.

### MINOR 1: Marker size encodes JSON parse rate through the panel title and caption, not a separate size legend.

Risk:
The caption and Panel A title explain it, but a reader may still not decode exact size values immediately.

Fix:
Acceptable for the current paper draft because JSON parse rate is a secondary visual cue. Add a small size legend only if reviewers or coauthors find Panel A ambiguous.

### MINOR 2: Utility labels in Panel A are compact but close to some markers.

Risk:
Readable in the current PNG/PDF, but should be checked after paper scaling.

Fix:
Verify minimum text size after LaTeX placement. Increase figure width or move utility values into the caption if needed.

### MINOR 3: The title and caption are deliberately finding-first.

Risk:
Good for internal draft and oral framing, but the camera-ready version may need a more neutral caption/title.

Fix:
Use the current title for story clarity. Soften only if the final paper tone becomes too argumentative.

## Universal Audit

- Vector PDF exists.
- PNG preview is nonblank and readable.
- Axes use honest `[0, 1]` ranges for accuracy and over-answer.
- No decorative chart effects.
- Values come from generated metric JSON via `scripts/plot_emnlp2026_figure2_action_calibration.py`.
- Caption states the finding in the first sentence.
- Caption states the oral-readiness takeaway: caution is not monotonic safety.
- Shared model-color legend is present below the panels.
