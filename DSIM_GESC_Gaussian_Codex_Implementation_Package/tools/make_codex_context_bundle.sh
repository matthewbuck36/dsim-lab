#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel)}"
OUT="${2:-$ROOT/codex_context_bundle.txt}"

cd "$ROOT"

{
  echo "# DSIM Codex Context Bundle"
  echo
  echo "## Git"
  git status --short --branch
  echo
  git log -5 --oneline
  echo
  echo "## Repository tree (filtered)"
  find . \
    \( -path './.git' -o -path './build' -o -path './install' -o -path './log' -o -path './.venv' -o -path './venv' \) -prune \
    -o -maxdepth 5 -type f \
    \( -name 'package.xml' -o -name 'CMakeLists.txt' -o -name 'setup.py' -o -name 'setup.cfg' \
       -o -name '*.launch.py' -o -name '*.yaml' -o -name '*.yml' -o -name '*.msg' -o -name '*.srv' \
       -o -name '*.action' -o -name 'README*' \) -print | sort
  echo
  echo "## ROS package manifests"
  while IFS= read -r f; do
    echo
    echo "### $f"
    sed -n '1,220p' "$f"
  done < <(find . \
    \( -path './.git' -o -path './build' -o -path './install' -o -path './log' \) -prune \
    -o -name package.xml -print | sort)
  echo
  echo "## Phase 00 audit documents"
  find docs/codex/gesc_gaussian -maxdepth 1 -type f -name '*.md' -print 2>/dev/null | sort || true
  echo
  echo "## Saved phase plans"
  find docs/codex/gesc_gaussian/plans -maxdepth 1 -type f -name 'phase_*_plan.md' -print 2>/dev/null | sort || true
  echo
  echo "## Implementation handoffs"
  find docs/codex/gesc_gaussian/handoffs -maxdepth 1 -type f -name 'phase_*_handoff.md' -print 2>/dev/null | sort || true
  echo
  echo "## Phase checkpoints"
  find docs/codex/gesc_gaussian/checkpoints -maxdepth 1 -type f -name 'phase_*_checkpoint.txt' -print 2>/dev/null | sort || true
} > "$OUT"

echo "Wrote $OUT"
