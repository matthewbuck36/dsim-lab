#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
REQ=(
  "$ROOT/docs/codex/gesc_gaussian/repo_audit.md"
  "$ROOT/docs/codex/gesc_gaussian/repo_map.md"
  "$ROOT/docs/codex/gesc_gaussian/interface_map.md"
  "$ROOT/docs/codex/gesc_gaussian/test_commands.md"
  "$ROOT/docs/codex/gesc_gaussian/implementation_sequence.md"
)

missing=0
for f in "${REQ[@]}"; do
  if [[ ! -s "$f" ]]; then
    echo "Missing or empty: $f" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  exit 1
fi

echo "All Phase 00 audit documents exist."
