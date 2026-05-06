#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

pdflatex -interaction=nonstopmode -halt-on-error main.tex
BSTINPUTS=.:styles: bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

if grep -nE "Overfull|undefined|Fatal|Emergency|Error" main.log main.blg >/tmp/coc_paper_latex_issues.txt; then
  cat /tmp/coc_paper_latex_issues.txt >&2
  exit 1
fi

echo "Built paper/main.pdf"
