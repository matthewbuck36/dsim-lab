#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel)}"
OUT="${2:-$ROOT/codex_context_bundle.txt}"
DOCS="$ROOT/docs/codex/gesc_gaussian"
PHASE08_STATUS="$DOCS/status/phase_08_status.md"
PHASE08_FREEZE_STATE="$DOCS/validation/phase_08_v3_freeze_state.json"
PHASE08_CONTRACT="$DOCS/validation/phase_08_v3_acceptance_contract.json"
ACTIVE_PHASE08_PLAN="$(
  find "$DOCS/plans" -maxdepth 1 -type f \
    -name "phase_08_[0-9]*_plan.md" -print 2>/dev/null |
    sort -V |
    tail -n 1
)"

print_last_status_section() {
  local heading="$1"
  local path="$2"
  local maximum_lines="$3"
  awk -v heading="$heading" -v maximum_lines="$maximum_lines" '
    $0 == heading {
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
      for (i = 1; i <= count && i <= maximum_lines; i++) {
        print lines[i]
      }
    }
  ' "$path"
}

print_freeze_summary() {
  local path="$1"
  python3 - "$path" <<'PY'
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
    "acceptance_suite_sha256",
    "contract_sha256",
    "runtime_inputs_sha256",
):
    if key in payload:
        print(f"- {key}: `{payload[key]}`")
PY
}

cd "$ROOT"

{
  echo "# DSIM Codex Context Bundle"
  echo
  echo "## Repository agent instructions"
  if [[ -s AGENTS.md ]]; then
    sed -n '1,260p' AGENTS.md
  else
    echo "AGENTS.md is missing."
  fi
  echo
  echo "## Git"
  git status --short --branch
  echo
  git log -5 --oneline
  echo
  echo "### Unstaged diff"
  git diff --stat
  git diff --name-only
  echo
  echo "### Staged diff"
  git diff --cached --stat
  git diff --cached --name-only
  echo
  echo "## Active Phase 08 recovery"
  if [[ -s "$ACTIVE_PHASE08_PLAN" ]]; then
    echo "Active subphase Plan: ${ACTIVE_PHASE08_PLAN#"$ROOT/"}"
    echo "Active subphase Plan sha256: $(sha256sum "$ACTIVE_PHASE08_PLAN" | awk '{print $1}')"
  else
    echo "No active Phase 08 subphase Plan found."
  fi
  if [[ -s "$PHASE08_STATUS" ]]; then
    echo "Live status: ${PHASE08_STATUS#"$ROOT/"}"
    echo "Live status sha256: $(sha256sum "$PHASE08_STATUS" | awk '{print $1}')"
    echo
    print_last_status_section "## Current milestone" "$PHASE08_STATUS" 40
  else
    echo "Phase 08 live status is missing."
  fi
  echo
  if [[ -s "$PHASE08_FREEZE_STATE" ]]; then
    echo "Freeze state: ${PHASE08_FREEZE_STATE#"$ROOT/"}"
    echo "Freeze state sha256: $(sha256sum "$PHASE08_FREEZE_STATE" | awk '{print $1}')"
    print_freeze_summary "$PHASE08_FREEZE_STATE"
  else
    echo "Freeze state: not created"
  fi
  if [[ -s "$PHASE08_CONTRACT" ]]; then
    echo "Acceptance contract: ${PHASE08_CONTRACT#"$ROOT/"}"
    echo "Acceptance contract sha256: $(sha256sum "$PHASE08_CONTRACT" | awk '{print $1}')"
  else
    echo "Acceptance contract: not created"
  fi
  if [[ -s "$ACTIVE_PHASE08_PLAN" ]]; then
    echo
    sed -n '/^## Terminal boundary$/,$p' "$ACTIVE_PHASE08_PLAN" |
      awk 'NR <= 40 { print }'
  fi
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
  echo "## Live phase statuses"
  while IFS= read -r f; do
    echo
    echo "### $f"
    sed -n '1,260p' "$f"
  done < <(find docs/codex/gesc_gaussian/status -maxdepth 1 -type f -name 'phase_*_status.md' -print 2>/dev/null | sort)
  echo
  echo "## Phase checkpoints"
  find docs/codex/gesc_gaussian/checkpoints -maxdepth 1 -type f -name 'phase_*_checkpoint.txt' -print 2>/dev/null | sort || true
} > "$OUT"

echo "Wrote $OUT"
