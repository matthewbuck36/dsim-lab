#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: init_phase_status.sh <phase 0-10>" >&2
}

if [[ "$#" -ne 1 ]] || [[ ! "$1" =~ ^(0?[0-9]|10)$ ]]; then
  usage
  exit 2
fi

PHASE_NUMBER=$((10#$1))
printf -v PHASE "%02d" "$PHASE_NUMBER"

ROOT="$(git rev-parse --show-toplevel)"
TEMPLATE="$ROOT/DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/codex_phase_status.md"
OUT="$ROOT/docs/codex/gesc_gaussian/status/phase_${PHASE}_status.md"

if [[ ! -s "$TEMPLATE" ]]; then
  echo "Missing or empty status template: $TEMPLATE" >&2
  exit 1
fi

if [[ -e "$OUT" ]]; then
  if [[ -s "$OUT" ]]; then
    echo "Status already exists; preserved $OUT"
    exit 0
  fi
  echo "Refusing to overwrite empty existing status file: $OUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
TIMESTAMP="$(date --utc --iso-8601=seconds)"
BRANCH="$(git -C "$ROOT" branch --show-current)"
HEAD="$(git -C "$ROOT" rev-parse HEAD)"
CONTENT="$(<"$TEMPLATE")"
CONTENT="${CONTENT//Phase XX/Phase $PHASE}"
CONTENT="${CONTENT//phase_XX/phase_$PHASE}"
CONTENT="${CONTENT//__TIMESTAMP__/$TIMESTAMP}"
CONTENT="${CONTENT//__BRANCH__/$BRANCH}"
CONTENT="${CONTENT//__HEAD__/$HEAD}"
printf '%s\n' "$CONTENT" > "$OUT"
echo "Created $OUT"
