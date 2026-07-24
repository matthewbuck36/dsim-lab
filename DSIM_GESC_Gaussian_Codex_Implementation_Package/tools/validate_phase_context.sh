#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: validate_phase_context.sh <phase 0-10> <plan|implement>" >&2
}

if [[ "$#" -ne 2 ]]; then
  usage
  exit 2
fi

PHASE_INPUT="$1"
STAGE="$2"

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
  "$PACKAGE/START_HERE.md"
  "$PACKAGE/00_MASTER_IMPLEMENTATION_PLAN.md"
  "$PACKAGE/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md"
  "$PACKAGE/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md"
)

if (( PHASE_NUMBER > 0 )); then
  required+=(
    "$DOCS/repo_audit.md"
    "$DOCS/repo_map.md"
    "$DOCS/interface_map.md"
    "$DOCS/test_commands.md"
    "$DOCS/implementation_sequence.md"
  )

  for ((i = 0; i < PHASE_NUMBER; i++)); do
    printf -v prior "%02d" "$i"
    required+=("$DOCS/handoffs/phase_${prior}_handoff.md")
  done
fi

if (( PHASE_NUMBER >= 6 )); then
  required+=(
    "$DOCS/knowledge_bridge_phase_00_05.md"
    "$DOCS/handoffs/phase_05_5_handoff.md"
  )
fi

if (( PHASE_NUMBER == 8 )) && [[ "$STAGE" == "implement" ]]; then
  required+=("$DOCS/handoffs/phase_07_5_handoff.md")
fi

if [[ "$STAGE" == "implement" ]]; then
  required+=("$DOCS/plans/phase_${PHASE}_plan.md")
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

echo "Phase $PHASE $STAGE context is complete."
