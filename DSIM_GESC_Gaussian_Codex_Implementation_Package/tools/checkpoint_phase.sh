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
FREEZE_STATE="$DOCS/validation/phase_${PHASE}_v3_freeze_state.json"
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
  if [[ -s "$FREEZE_STATE" ]]; then
    echo "Freeze state: ${FREEZE_STATE#"$ROOT/"}"
    echo "Freeze state sha256: $(sha256sum "$FREEZE_STATE" | awk '{print $1}')"
    python3 - "$FREEZE_STATE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
for key in (
    "experiment_version",
    "freeze_status",
    "current_stage",
    "freeze_commit",
    "freeze_tree_sha256",
    "frozen_parameters_sha256",
    "acceptance_suite_ciphertext_sha256",
    "contract_sha256",
    "runtime_inputs_sha256",
):
    if key in payload:
        print(f"Freeze {key}: {payload[key]}")
PY
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
  awk '
    /^## Current milestone$/ {
      block = $0 ORS
      capture = 1
      next
    }
    /^## / && capture {
      latest = block
      capture = 0
    }
    capture {
      block = block $0 ORS
    }
    END {
      if (capture) {
        latest = block
      }
      count = split(latest, lines, ORS)
      for (i = 1; i <= count && i <= 30; i++) {
        print lines[i]
      }
    }
  ' "$STATUS"
  echo
  echo "This file describes the base HEAD and diff before the next commit; it is"
  echo "not a claim that the eventual commit contains itself or that tests passed."
} > "$OUT"

echo "Wrote $OUT"
