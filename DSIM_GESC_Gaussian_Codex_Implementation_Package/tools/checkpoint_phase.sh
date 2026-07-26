#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: checkpoint_phase.sh <phase 0-10>" >&2
}

if [[ "$#" -ne 1 ]] || [[ ! "$1" =~ ^(0?[0-9]|10)$ ]]; then
  usage
  exit 2
fi

PHASE_NUMBER=$((10#$1))
printf -v PHASE "%02d" "$PHASE_NUMBER"

ROOT="$(git rev-parse --show-toplevel)"
DOCS="$ROOT/docs/codex/gesc_gaussian"
STATUS="$DOCS/status/phase_${PHASE}_status.md"
PLAN="$DOCS/plans/phase_${PHASE}_plan.md"
SUBPHASE_PLAN="$(
  find "$DOCS/plans" -maxdepth 1 -type f \
    -name "phase_${PHASE}_[0-9]*_plan.md" -print |
    sort -V |
    tail -n 1
)"
OUT="$DOCS/checkpoints/phase_${PHASE}_checkpoint.txt"

if [[ ! -s "$STATUS" ]]; then
  echo "Missing or empty live status: $STATUS" >&2
  echo "Run init_phase_status.sh $PHASE and verify it first." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
cd "$ROOT"

{
  echo "# Phase $PHASE checkpoint"
  echo
  echo "Checkpoint kind: precommit material-boundary snapshot"
  echo "Generated: $(date --utc --iso-8601=seconds)"
  echo "Base HEAD: $(git rev-parse HEAD)"
  echo "Branch: $(git branch --show-current)"
  echo "Status: ${STATUS#"$ROOT/"}"
  echo "Status sha256: $(sha256sum "$STATUS" | awk '{print $1}')"
  if [[ -s "$PLAN" ]]; then
    echo "Plan: ${PLAN#"$ROOT/"}"
    echo "Plan sha256: $(sha256sum "$PLAN" | awk '{print $1}')"
  fi
  if [[ -s "$SUBPHASE_PLAN" ]]; then
    echo "Active subphase plan: ${SUBPHASE_PLAN#"$ROOT/"}"
    echo "Active subphase plan sha256: $(sha256sum "$SUBPHASE_PLAN" | awk '{print $1}')"
  fi
  echo "Unstaged diff sha256: $(git diff | sha256sum | awk '{print $1}')"
  echo "Staged diff sha256: $(git diff --cached | sha256sum | awk '{print $1}')"
  echo
  echo "## Git state"
  git status --short --branch
  echo
  echo "## Diff check"
  DIFF_CHECK=""
  CACHED_DIFF_CHECK=""
  if DIFF_CHECK="$(git diff --check 2>&1)" &&
    CACHED_DIFF_CHECK="$(git diff --cached --check 2>&1)"; then
    echo "unstaged and staged: pass"
  else
    echo "fail"
    echo "$DIFF_CHECK"
    echo "$CACHED_DIFF_CHECK"
  fi
  echo
  echo "## Changed-file summary"
  git diff --stat
  git diff --cached --stat
  echo
  echo "## Current milestone snapshot"
  sed -n '/^## Current milestone$/,/^## /p' "$STATUS" |
    sed '$d' |
    awk 'NR <= 30 { print }'
  echo
  echo "This file describes the base HEAD and diff before the next commit; it is"
  echo "not a claim that the eventual commit contains itself or that tests passed."
} > "$OUT"

echo "Wrote $OUT"
