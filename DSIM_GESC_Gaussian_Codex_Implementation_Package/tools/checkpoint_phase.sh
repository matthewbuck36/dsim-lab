#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:?Usage: checkpoint_phase.sh <phase-number>}"
ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/docs/codex/gesc_gaussian/checkpoints/phase_${PHASE}_checkpoint.txt"

mkdir -p "$(dirname "$OUT")"

{
  echo "# Phase $PHASE checkpoint"
  date --iso-8601=seconds
  echo
  git status --short --branch
  echo
  echo "## Recent commits"
  git log -5 --oneline
  echo
  echo "## Diff stat"
  git diff --stat
  echo
  echo "## Changed files"
  git diff --name-only
} > "$OUT"

echo "Wrote $OUT"
