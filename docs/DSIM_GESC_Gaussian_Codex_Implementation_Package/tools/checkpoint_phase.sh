#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: checkpoint_phase.sh <phase 0-10|v2>" >&2
}

if [[ "$#" -ne 1 ]] || [[ "$1" != "v2" && ! "$1" =~ ^(0?[0-9]|10)$ ]]; then
  usage
  exit 2
fi

if [[ "$1" == "v2" ]]; then
  PHASE=v2
else
  PHASE_NUMBER=$((10#$1))
  printf -v PHASE "%02d" "$PHASE_NUMBER"
fi

ROOT="$(git rev-parse --show-toplevel)"
DOCS="$ROOT/docs/codex/gesc_gaussian"
if [[ "$PHASE" == "v2" ]]; then
  STATUS="$DOCS/v2/status.md"
  PLAN="$DOCS/v2/plan.md"
  SUBPHASE_PLAN=""
  FREEZE_STATE=""
  OUT="$DOCS/v2/checkpoint.txt"
else
  STATUS="$DOCS/status/phase_${PHASE}_status.md"
  PLAN="$DOCS/plans/phase_${PHASE}_plan.md"
  SUBPHASE_PLAN="$(
    find "$DOCS/plans" -maxdepth 1 -type f \
      -name "phase_${PHASE}_[0-9]*_plan.md" \
      -printf '%f\t%p\n' |
      sort -t_ -k3,3n -k4,4n -k5,5n |
      tail -n 1 |
      cut -f2-
  )"
  FREEZE_STATE="$(
    find "$DOCS/validation" -maxdepth 1 -type f \
      -name "phase_${PHASE}_v[0-9]*_freeze_state.json" -print 2>/dev/null |
      sort -V |
      tail -n 1
  )"
  OUT="$DOCS/checkpoints/phase_${PHASE}_checkpoint.txt"
fi

if [[ ! -s "$STATUS" ]]; then
  echo "Missing or empty live status: $STATUS" >&2
  echo "Run init_phase_status.sh $PHASE and verify it first." >&2
  exit 1
fi

if [[ "$PHASE" == "v2" && ! -s "$PLAN" ]]; then
  echo "Missing or empty V2 plan: $PLAN" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
cd "$ROOT"
WRITE_OUT="$OUT"
if [[ "$PHASE" == "v2" ]]; then
  WRITE_OUT="$(mktemp "$DOCS/v2/.checkpoint.XXXXXXXX")"
  trap 'rm -f "$WRITE_OUT"' EXIT
  EXCLUDE_TEMP=":(exclude)${WRITE_OUT#"$ROOT/"}"
fi

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
    "acceptance_suite_sha256",
    "contract_sha256",
    "runtime_inputs_sha256",
):
    if key in payload:
        print(f"Freeze {key}: {payload[key]}")
PY
  fi
  if [[ "$PHASE" == "v2" ]]; then
    # The generated checkpoint cannot contain its own content hash.
    EXCLUDE_OUT=":(exclude)${OUT#"$ROOT/"}"
    echo "Checkpoint self-exclusion: ${OUT#"$ROOT/"}"
    echo "Unstaged binary diff sha256: $(git diff --binary -- . "$EXCLUDE_OUT" "$EXCLUDE_TEMP" | sha256sum | awk '{print $1}')"
    echo "Staged binary diff sha256: $(git diff --cached --binary -- . "$EXCLUDE_OUT" "$EXCLUDE_TEMP" | sha256sum | awk '{print $1}')"
    echo
    echo "## Dirty and untracked file hashes"
    python3 - "${OUT#"$ROOT/"}" "${WRITE_OUT#"$ROOT/"}" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

excluded = {os.fsencode(path) for path in sys.argv[1:]}
paths = set()
for args in (
    ["ls-files", "--modified", "--deleted", "--others", "--exclude-standard", "-z"],
    ["diff", "--cached", "--name-only", "--no-renames", "-z"],
):
    paths.update(subprocess.check_output(["git", *args]).split(b"\0"))
manifest = hashlib.sha256()
for raw_path in sorted(paths - {b""} - excluded):
    path = Path(os.fsdecode(raw_path))
    entry = {"path": os.fsdecode(raw_path)}
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        entry["type"] = "deleted"
    else:
        entry["mode"] = oct(stat.S_IMODE(mode))
        if stat.S_ISLNK(mode):
            entry["type"] = "symlink"
            entry["sha256"] = hashlib.sha256(os.readlink(raw_path)).hexdigest()
        elif stat.S_ISREG(mode):
            entry["type"] = "file"
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            entry["sha256"] = digest.hexdigest()
        else:
            raise SystemExit(f"Cannot hash changed non-file path: {path}")
    line = json.dumps(entry, sort_keys=True)
    print(line)
    manifest.update((line + "\n").encode("utf-8"))
print(f"Dirty and untracked manifest sha256: {manifest.hexdigest()}")
PY
  else
    echo "Unstaged diff sha256: $(git diff | sha256sum | awk '{print $1}')"
    echo "Staged diff sha256: $(git diff --cached | sha256sum | awk '{print $1}')"
  fi
  echo
  echo "## Git state"
  if [[ "$PHASE" == "v2" ]]; then
    git status --short --branch -- . "$EXCLUDE_TEMP"
  else
    git status --short --branch
  fi
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
      if (capture) {
        latest = block
      }
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
} > "$WRITE_OUT"

if [[ "$PHASE" == "v2" ]]; then
  mv "$WRITE_OUT" "$OUT"
fi

echo "Wrote $OUT"
