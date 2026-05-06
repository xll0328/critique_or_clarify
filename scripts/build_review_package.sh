#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
OUTPUT_ROOT="$REPO_ROOT/_review_package"
PACKAGE_NAME=critique_or_clarify_emnlp2026_review
RUN_BUILD=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_ROOT=$2
      shift 2
      ;;
    --no-build)
      RUN_BUILD=0
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

PACKAGE_DIR="$OUTPUT_ROOT/$PACKAGE_NAME"
PAPER_DIR="$PACKAGE_DIR/paper"

clean_latex_artifacts() {
  find "$PAPER_DIR" \( \
    -name '*.aux' -o \
    -name '*.log' -o \
    -name '*.out' -o \
    -name '*.blg' -o \
    -name '*.bbl' \
  \) -delete
}

rm -rf "$PACKAGE_DIR"
mkdir -p "$PAPER_DIR"

cp "$REPO_ROOT/paper/main.tex" "$PAPER_DIR/main.tex"
cp "$REPO_ROOT/paper/references.bib" "$PAPER_DIR/references.bib"
cp "$REPO_ROOT/paper/build.sh" "$PAPER_DIR/build.sh"
cp "$REPO_ROOT/paper/main.pdf" "$PAPER_DIR/main.pdf"
cp -R "$REPO_ROOT/paper/sections" "$PAPER_DIR/sections"
cp -R "$REPO_ROOT/paper/tables" "$PAPER_DIR/tables"
cp -R "$REPO_ROOT/paper/figures" "$PAPER_DIR/figures"
cp -R "$REPO_ROOT/paper/styles" "$PAPER_DIR/styles"

cat > "$PAPER_DIR/README.md" <<'EOF'
# Critique-or-Clarify Review Paper Package

This package contains the anonymized paper source, generated figures, generated tables, ACL style files, bibliography, and the current built PDF.

## Build

```bash
cd paper
./build.sh
```

The build script runs LaTeX and BibTeX from this directory and fails on overfull boxes, undefined references, fatal errors, or emergency stops.
EOF

clean_latex_artifacts

if grep -R -nE '/data/sony|sony|model_cache|outputs/day1|experiments/day1|_assets/' "$PACKAGE_DIR"; then
  echo "Review package contains internal paths or artifacts." >&2
  exit 1
fi

if [[ "$RUN_BUILD" -eq 1 ]]; then
  "$PAPER_DIR/build.sh"
  clean_latex_artifacts
fi

if command -v zip >/dev/null 2>&1; then
  (
    cd "$OUTPUT_ROOT"
    rm -f "$PACKAGE_NAME.zip"
    zip -qr "$PACKAGE_NAME.zip" "$PACKAGE_NAME"
  )
fi

echo "Built review package at $PACKAGE_DIR"
