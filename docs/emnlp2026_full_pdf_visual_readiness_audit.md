# EMNLP 2026 Full PDF Visual Readiness Audit

Date: 2026-05-06

Status: automated full-manuscript PDF render/readability preflight. This is not final human sign-off.

Audit input:

- Rendered `paper/main.pdf` to PNG pages under `tmp/pdf_review/full_visual` with PyMuPDF.
- Page count: `13`.
- Average extracted text per page: `4502` characters.
- Minimum extracted text on any page: `3443` characters.
- Minimum sampled non-white rendered area: `0.1097`.
- Checked story anchors across title/task/results/stress/limitations text.

## Severity Summary

- `CRITICAL`: 0
- `MAJOR`: 0
- `MINOR`: 1

## Closed Checks

### CLOSED 1: The compiled PDF renders all pages.

All `13` pages rendered to PNG files under `tmp/pdf_review/full_visual`. No page has zero dimensions, and no rendered page was sampled as blank.

### CLOSED 2: The full-manuscript story anchors survive compilation.

The compiled PDF text contains the title/task anchor, the four-action ontology, the external API contrast, the slice-balance sensitivity language, and the Limitations section.

### CLOSED 3: The check remains separate from human review.

This audit can catch missing pages, blank renders, and lost story anchors, but it is not a substitute for a human author reading the final submitted PDF.

## Page Render Summary

| Page | Text chars | Non-white share | Render |
| --- | ---: | ---: | --- |
| 1 | 4356 | 0.1158 | `tmp/pdf_review/full_visual/page_01.png` |
| 2 | 4036 | 0.1212 | `tmp/pdf_review/full_visual/page_02.png` |
| 3 | 4988 | 0.1360 | `tmp/pdf_review/full_visual/page_03.png` |
| 4 | 5171 | 0.1414 | `tmp/pdf_review/full_visual/page_04.png` |
| 5 | 4028 | 0.1457 | `tmp/pdf_review/full_visual/page_05.png` |
| 6 | 4991 | 0.1319 | `tmp/pdf_review/full_visual/page_06.png` |
| 7 | 4700 | 0.1275 | `tmp/pdf_review/full_visual/page_07.png` |
| 8 | 4061 | 0.1163 | `tmp/pdf_review/full_visual/page_08.png` |
| 9 | 3443 | 0.1423 | `tmp/pdf_review/full_visual/page_09.png` |
| 10 | 4777 | 0.1256 | `tmp/pdf_review/full_visual/page_10.png` |
| 11 | 4876 | 0.1302 | `tmp/pdf_review/full_visual/page_11.png` |
| 12 | 4825 | 0.1220 | `tmp/pdf_review/full_visual/page_12.png` |
| 13 | 4274 | 0.1097 | `tmp/pdf_review/full_visual/page_13.png` |

## Findings

| Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- |
| `MINOR` | `human_signoff_still_required` | Automated PyMuPDF rendering found no blank pages or missing story anchors in the compiled PDF. | A human author should still read the final PDF before external submission. |

## Regression Rule

After any paper-facing layout edit, rerun:

```bash
python scripts/audit_full_pdf_visual_readiness.py
```

Keep `CRITICAL=0` and `MAJOR=0`, and do not treat this automated audit as final human submission approval.
