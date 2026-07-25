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
  echo "Generated: $(date --utc --iso-8601=seconds)"
  echo "Status: ${STATUS#"$ROOT/"}"
  echo "Status sha256: $(sha256sum "$STATUS" | awk '{print $1}')"
  if [[ -s "$PLAN" ]]; then
    echo "Plan: ${PLAN#"$ROOT/"}"
    echo "Plan sha256: $(sha256sum "$PLAN" | awk '{print $1}')"
  fi
  echo
  echo "## Git state"
  git status --short --branch
  echo
  echo "## Recent commits"
  git log -5 --oneline
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
  echo "## Unstaged diff stat"
  git diff --stat
  echo
  echo "## Staged diff stat"
  git diff --cached --stat
  echo
  echo "## Unstaged changed files"
  git diff --name-only
  echo
  echo "## Staged changed files"
  git diff --cached --name-only
  echo
  echo "## Live status snapshot"
  sed -n '1,260p' "$STATUS"
} > "$OUT"

echo "Wrote $OUT"
