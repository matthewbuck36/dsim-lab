#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: validate_phase_context.sh <phase 0-10> <plan|implement> [--strict-history]" >&2
}

if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  usage
  exit 2
fi

PHASE_INPUT="$1"
STAGE="$2"
STRICT_HISTORY=false

if [[ "$#" -eq 3 ]]; then
  if [[ "$3" != "--strict-history" ]]; then
    echo "Invalid option: $3" >&2
    usage
    exit 2
  fi
  STRICT_HISTORY=true
fi

if [[ ! "$PHASE_INPUT" =~ ^(0?[0-9]|10)$ ]]; then
  echo "Invalid phase: $PHASE_INPUT" >&2
  usage
  exit 2
fi

if [[ "$STAGE" != "plan" && "$STAGE" != "implement" ]]; then
  echo "Invalid stage: $STAGE" >&2
  usage
  exit 2
fi

PHASE_NUMBER=$((10#$PHASE_INPUT))
printf -v PHASE "%02d" "$PHASE_NUMBER"

if ! ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "Unable to locate the Git repository root." >&2
  exit 2
fi

PACKAGE="$ROOT/DSIM_GESC_Gaussian_Codex_Implementation_Package"
DOCS="$ROOT/docs/codex/gesc_gaussian"

required=(
  "$ROOT/AGENTS.md"
  "$PACKAGE/START_HERE.md"
  "$PACKAGE/00_MASTER_IMPLEMENTATION_PLAN.md"
  "$PACKAGE/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md"
  "$PACKAGE/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md"
  "$PACKAGE/templates/codex_phase_status.md"
  "$PACKAGE/tools/init_phase_status.sh"
  "$PACKAGE/tools/checkpoint_phase.sh"
)
historical=()

if (( PHASE_NUMBER > 0 )); then
  required+=(
    "$DOCS/implementation_sequence.md"
  )
  historical+=(
    "$DOCS/repo_audit.md"
    "$DOCS/repo_map.md"
    "$DOCS/interface_map.md"
    "$DOCS/test_commands.md"
  )

  for ((i = 0; i < PHASE_NUMBER; i++)); do
    printf -v prior "%02d" "$i"
    historical+=("$DOCS/handoffs/phase_${prior}_handoff.md")
  done

  printf -v immediate_prior "%02d" "$((PHASE_NUMBER - 1))"
  required+=("$DOCS/handoffs/phase_${immediate_prior}_handoff.md")
fi

if (( PHASE_NUMBER >= 6 )); then
  required+=(
    "$DOCS/knowledge_bridge_phase_00_05.md"
    "$DOCS/handoffs/phase_05_5_handoff.md"
  )
fi

if [[ "$STRICT_HISTORY" == true ]]; then
  required+=("${historical[@]}")
fi

if (( PHASE_NUMBER == 8 )) && [[ "$STAGE" == "implement" ]]; then
  required+=("$DOCS/handoffs/phase_07_5_handoff.md")
fi

if [[ "$STAGE" == "implement" ]]; then
  required+=(
    "$DOCS/plans/phase_${PHASE}_plan.md"
    "$DOCS/status/phase_${PHASE}_status.md"
  )
fi

missing=0
for path in "${required[@]}"; do
  if [[ ! -s "$path" ]]; then
    echo "Missing or empty: $path" >&2
    missing=1
  fi
done

if (( missing != 0 )); then
  echo "Phase $PHASE $STAGE context validation failed." >&2
  exit 1
fi

if [[ "$STRICT_HISTORY" == false ]]; then
  for path in "${historical[@]}"; do
    if [[ ! -s "$path" ]]; then
      echo "Historical context warning: missing or empty: $path" >&2
      echo "Reconstruct the needed claim from current code, Git, and relevant retained evidence." >&2
    fi
  done
fi

for path in \
  "$PACKAGE/tools/init_phase_status.sh" \
  "$PACKAGE/tools/checkpoint_phase.sh"; do
  if [[ ! -x "$path" ]]; then
    echo "Required context tool is not executable: $path" >&2
    missing=1
  fi
done

if (( missing != 0 )); then
  echo "Phase $PHASE $STAGE context validation failed." >&2
  exit 1
fi

if [[ "$STAGE" == "implement" ]]; then
  status="$DOCS/status/phase_${PHASE}_status.md"
  headings=(
    "## Verified repository state"
    "## Current milestone"
    "## Validation checkpoints"
    "## Attempts not to repeat"
    "## Remaining work"
    "## Compaction recovery"
  )
  for heading in "${headings[@]}"; do
    if ! grep -Fqx "$heading" "$status"; then
      echo "Live status is missing required heading: $heading" >&2
      missing=1
    fi
  done
  if (( missing != 0 )); then
    echo "Phase $PHASE $STAGE context validation failed." >&2
    exit 1
  fi
fi

echo "Phase $PHASE $STAGE context is complete."
