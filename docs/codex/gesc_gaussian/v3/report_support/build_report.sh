#!/usr/bin/env bash
set -euo pipefail

# Report authoring only. This command never starts ROS, Gazebo or hardware.
# Requires Pandoc and Tectonic; set the *_BIN variables for non-PATH tools.
v3_report_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
v3_support_dir="$v3_report_dir/v3/report_support"
v3_pandoc="${PANDOC_BIN:-pandoc}"
v3_tectonic="${TECTONIC_BIN:-tectonic}"
v3_build_dir="${REPORT_BUILD_DIR:-$(mktemp -d /tmp/dsim-v3-report.XXXXXX)}"
mkdir -p -- "$v3_build_dir"
cd -- "$v3_report_dir"

timeout 60s "$v3_pandoc" FINAL_PROJECT_REPORT_V3.md \
  --from markdown+tex_math_dollars --to latex --standalone \
  --number-sections --toc --toc-depth=2 --listings \
  --metadata title='GESC Gaussian V3 Complete Project and Learning Report' \
  --metadata author='DSIM Lab' --metadata date='October 5 2026' \
  --lua-filter="$v3_support_dir/report_filter.lua" \
  --include-in-header="$v3_support_dir/report_header.tex" \
  -V fontsize=10pt -V papersize=letter -V geometry:margin=0.75in \
  -o FINAL_PROJECT_REPORT_V3.tex

timeout 180s "$v3_tectonic" --keep-logs --outdir "$v3_build_dir" FINAL_PROJECT_REPORT_V3.tex
cp -- "$v3_build_dir/FINAL_PROJECT_REPORT_V3.pdf" FINAL_PROJECT_REPORT_V3.pdf
printf 'Report build receipt directory: %s\n' "$v3_build_dir"
