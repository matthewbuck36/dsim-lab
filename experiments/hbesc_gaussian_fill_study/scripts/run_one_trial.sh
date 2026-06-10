#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_one_trial.sh [--dry-run|--execute] [--wall-timeout SEC] SCENARIO_JSON

Default mode is --dry-run. --execute starts the existing HBESC scenario runner,
monitors /clock, and terminates the started process group after stop_rule_sec.
EOF
}

MODE="dry-run"
WALL_TIMEOUT="180"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --execute)
      MODE="execute"
      shift
      ;;
    --wall-timeout)
      WALL_TIMEOUT="${2:-}"
      if [ -z "${WALL_TIMEOUT}" ]; then
        echo "--wall-timeout requires a value" >&2
        exit 2
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -ne 1 ]; then
  usage >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${EXP_DIR}/../.." && pwd)"
SCENARIO_INPUT="$1"
RUNNER="${REPO_ROOT}/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash"
MANIFEST="${EXP_DIR}/results_manifest.csv"

if [ ! -f "${SCENARIO_INPUT}" ]; then
  echo "Scenario file not found: ${SCENARIO_INPUT}" >&2
  exit 2
fi

if [ ! -x "${RUNNER}" ] && [ ! -f "${RUNNER}" ]; then
  echo "Scenario runner not found: ${RUNNER}" >&2
  exit 2
fi

RUN_INFO="$(
  python3 - "${SCENARIO_INPUT}" "${EXP_DIR}" "${MODE}" <<'PY'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

scenario_path = Path(sys.argv[1]).expanduser().resolve()
exp_dir = Path(sys.argv[2]).resolve()
mode = sys.argv[3]
scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
name = scenario.get("name") or scenario_path.stem
safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "scenario"
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
run_id = f"{stamp}_{safe_name}_{mode.replace('-', '_')}"
run_dir = exp_dir / "results" / "runs" / run_id
print(run_id)
print(run_dir)
print(name)
print(scenario.get("test_id", name))
print(scenario.get("stop_rule_sec", 60))
print(scenario.get("phase", 2))
PY
)"

RUN_ID="$(printf '%s\n' "${RUN_INFO}" | sed -n '1p')"
RUN_DIR="$(printf '%s\n' "${RUN_INFO}" | sed -n '2p')"
SCENARIO_NAME="$(printf '%s\n' "${RUN_INFO}" | sed -n '3p')"
SCENARIO_ID="$(printf '%s\n' "${RUN_INFO}" | sed -n '4p')"
STOP_RULE_SEC="$(printf '%s\n' "${RUN_INFO}" | sed -n '5p')"
PHASE="$(printf '%s\n' "${RUN_INFO}" | sed -n '6p')"

mkdir -p "${RUN_DIR}/logs" "${RUN_DIR}/configs" "${RUN_DIR}/data_collection"
mkdir -p "${RUN_DIR}/logs/ros" "${RUN_DIR}/logs/matplotlib"
export ROS_LOG_DIR="${RUN_DIR}/logs/ros"
export MPLCONFIGDIR="${RUN_DIR}/logs/matplotlib"

RUN_HASH="$(python3 - "${RUN_ID}" <<'PY'
import sys
print(sum(ord(ch) for ch in sys.argv[1]))
PY
)"
export ROS_DOMAIN_ID="${HBESC_ROS_DOMAIN_ID:-$((20 + RUN_HASH % 180))}"
export GAZEBO_MASTER_URI="${HBESC_GAZEBO_MASTER_URI:-http://127.0.0.1:$((11345 + RUN_HASH % 1000))}"

SCENARIO_USED="${RUN_DIR}/configs/scenario_used.json"
METADATA_JSON="${RUN_DIR}/trial_metadata.json"

python3 - "${SCENARIO_INPUT}" "${SCENARIO_USED}" "${METADATA_JSON}" "${RUN_DIR}" "${RUN_ID}" "${MODE}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

src = Path(sys.argv[1]).expanduser().resolve()
dst = Path(sys.argv[2]).resolve()
metadata_path = Path(sys.argv[3]).resolve()
run_dir = Path(sys.argv[4]).resolve()
run_id = sys.argv[5]
mode = sys.argv[6]

scenario = json.loads(src.read_text(encoding="utf-8"))
launch = scenario.setdefault("launch", {})
launch["data_collection_filepath"] = str(run_dir / "data_collection")
dst.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")

metadata = {
    "run_id": run_id,
    "mode": mode,
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_scenario": str(src),
    "scenario_used": str(dst),
    "run_dir": str(run_dir),
    "scenario_name": scenario.get("name", src.stem),
    "scenario_id": scenario.get("test_id", scenario.get("name", src.stem)),
    "stop_rule_sec": scenario.get("stop_rule_sec"),
    "data_collection_filepath": launch.get("data_collection_filepath"),
    "ros_domain_id": __import__("os").environ.get("ROS_DOMAIN_ID", ""),
    "gazebo_master_uri": __import__("os").environ.get("GAZEBO_MASTER_URI", ""),
    "ros_log_dir": __import__("os").environ.get("ROS_LOG_DIR", ""),
    "mplconfigdir": __import__("os").environ.get("MPLCONFIGDIR", ""),
}
metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
PY

record_manifest() {
  local status="$1"
  local notes="$2"
  python3 "${SCRIPT_DIR}/record_trial_metadata.py" \
    --manifest "${MANIFEST}" \
    --run-dir "${RUN_DIR}" \
    --scenario "${SCENARIO_USED}" \
    --run-id "${RUN_ID}" \
    --phase "${PHASE}" \
    --status "${status}" \
    --notes "${notes}"
}

DRY_STDOUT="${RUN_DIR}/logs/scenario_dry_run.stdout"
DRY_STDERR="${RUN_DIR}/logs/scenario_dry_run.stderr"
USE_PDE_EXTENSIONS="$(
  python3 - "${SCENARIO_USED}" <<'PY'
import json
import sys
from pathlib import Path

scenario = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("true" if scenario.get("launch", {}).get("use_pde_extensions") is True else "false")
PY
)"

if bash "${RUNNER}" --dry-run "${SCENARIO_USED}" >"${DRY_STDOUT}" 2>"${DRY_STDERR}"; then
  tail -n 1 "${DRY_STDOUT}" > "${RUN_DIR}/launch_command.txt"
else
  printf '{"run_id":"%s","mode":"%s","status":"dry_run_failed"}\n' "${RUN_ID}" "${MODE}" > "${RUN_DIR}/summary.json"
  record_manifest "dry_run_failed" "scenario runner dry-run failed; see logs"
  echo "Dry-run failed. Run directory: ${RUN_DIR}" >&2
  exit 1
fi

if [ "${MODE}" = "dry-run" ]; then
  python3 - "${RUN_DIR}" "${RUN_ID}" "${SCENARIO_NAME}" "${SCENARIO_ID}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
summary = {
    "run_id": sys.argv[2],
    "scenario_name": sys.argv[3],
    "scenario_id": sys.argv[4],
    "mode": "dry-run",
    "status": "dry_run_passed",
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    "notes": "No Gazebo simulation was started.",
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
  record_manifest "dry_run_passed" "Phase ${PHASE} dry-run; no Gazebo simulation started"
  python3 "${SCRIPT_DIR}/check_trial_outputs.py" "${RUN_DIR}" > "${RUN_DIR}/logs/check_trial_outputs.stdout"
  echo "${RUN_DIR}"
  exit 0
fi

RUN_STDOUT="${RUN_DIR}/logs/scenario_run.stdout"
RUN_STDERR="${RUN_DIR}/logs/scenario_run.stderr"

setsid bash "${RUNNER}" "${SCENARIO_USED}" >"${RUN_STDOUT}" 2>"${RUN_STDERR}" &
RUNNER_PID="$!"
sleep 1

PGID="$(ps -o pgid= -p "${RUNNER_PID}" | tr -d ' ')"
if [ -z "${PGID}" ]; then
  PGID="${RUNNER_PID}"
fi
RUNNER_SID="$(ps -o sid= -p "${RUNNER_PID}" | tr -d ' ')"
if [ -z "${RUNNER_SID}" ]; then
  RUNNER_SID="${RUNNER_PID}"
fi

DIAG_PID=""
DIAG_PGID=""
DIAG_SID=""
if [ "${USE_PDE_EXTENSIONS}" = "true" ]; then
  mkdir -p "${RUN_DIR}/diagnostics"
  setsid bash -lc "source /opt/ros/humble/setup.bash 2>/dev/null || true; source '${REPO_ROOT}/ros2_ws/install/setup.bash' 2>/dev/null || true; ros2 bag record -o '${RUN_DIR}/diagnostics/gaussian_fill_topics' /cost_bias /pde_history /convergence_event /convergence_metric /convergence_r /cost_modified /turtlebot3/cost_value_chatter" \
    > "${RUN_DIR}/logs/rosbag_gaussian_fill.stdout" \
    2> "${RUN_DIR}/logs/rosbag_gaussian_fill.stderr" &
  DIAG_PID="$!"
  sleep 1
  DIAG_PGID="$(ps -o pgid= -p "${DIAG_PID}" | tr -d ' ')"
  if [ -z "${DIAG_PGID}" ]; then
    DIAG_PGID="${DIAG_PID}"
  fi
  DIAG_SID="$(ps -o sid= -p "${DIAG_PID}" | tr -d ' ')"
  if [ -z "${DIAG_SID}" ]; then
    DIAG_SID="${DIAG_PID}"
  fi
fi

STATUS="unknown"
NOTES=""

kill_session() {
  local sid="$1"
  local signal="$2"
  if [ -z "${sid}" ]; then
    return 0
  fi
  mapfile -t session_pids < <(ps -eo pid=,sid= | awk -v sid="${sid}" '$2 == sid {print $1}')
  if [ "${#session_pids[@]}" -gt 0 ]; then
    kill "-${signal}" "${session_pids[@]}" 2>/dev/null || true
  fi
}

cleanup_runner() {
  if [ -n "${DIAG_PID}" ]; then
    kill_session "${DIAG_SID}" TERM
    kill -TERM "-${DIAG_PGID}" 2>/dev/null || true
    sleep 2
    kill_session "${DIAG_SID}" KILL
    kill -KILL "-${DIAG_PGID}" 2>/dev/null || true
    wait "${DIAG_PID}" 2>/dev/null || true
  fi
  kill_session "${RUNNER_SID}" TERM
  kill -TERM "-${PGID}" 2>/dev/null || true
  sleep 5
  kill_session "${RUNNER_SID}" KILL
  kill -KILL "-${PGID}" 2>/dev/null || true
  wait "${RUNNER_PID}" 2>/dev/null || true
}

trap 'cleanup_runner; exit 130' INT TERM
trap 'cleanup_runner' EXIT

set +e
bash -lc "source /opt/ros/humble/setup.bash 2>/dev/null || true; source '${REPO_ROOT}/ros2_ws/install/setup.bash' 2>/dev/null || true; python3 '${SCRIPT_DIR}/monitor_sim_time.py' --duration '${STOP_RULE_SEC}' --wall-timeout '${WALL_TIMEOUT}'" \
  > "${RUN_DIR}/logs/monitor_sim_time.stdout" \
  2> "${RUN_DIR}/logs/monitor_sim_time.stderr"
MONITOR_STATUS="$?"
set -e

case "${MONITOR_STATUS}" in
  0)
    if [ "${PHASE}" = "2" ]; then
      STATUS="smoke_sim_time_reached"
    else
      STATUS="sim_time_reached"
    fi
    NOTES="sim-time stop_rule_sec reached; runner process session terminated"
    ;;
  2)
    if [ "${PHASE}" = "2" ]; then
      STATUS="smoke_wall_timeout"
    else
      STATUS="wall_timeout"
    fi
    NOTES="wall-time timeout before sim-time duration; runner process session terminated"
    ;;
  *)
    if [ "${PHASE}" = "2" ]; then
      STATUS="smoke_monitor_failed"
    else
      STATUS="monitor_failed"
    fi
    NOTES="sim-time monitor failed; runner process session terminated"
    ;;
esac

cleanup_runner

python3 - "${RUN_DIR}" "${RUN_ID}" "${SCENARIO_NAME}" "${SCENARIO_ID}" "${MODE}" "${STATUS}" "${NOTES}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
summary = {
    "run_id": sys.argv[2],
    "scenario_name": sys.argv[3],
    "scenario_id": sys.argv[4],
    "mode": sys.argv[5],
    "status": sys.argv[6],
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    "notes": sys.argv[7],
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY

CHECK_STATUS=0
python3 "${SCRIPT_DIR}/check_trial_outputs.py" "${RUN_DIR}" > "${RUN_DIR}/logs/check_trial_outputs.stdout" || CHECK_STATUS="$?"
python3 "${EXP_DIR}/analysis/analyze_results.py" "${RUN_DIR}" > "${RUN_DIR}/logs/analyze_results.stdout" 2> "${RUN_DIR}/logs/analyze_results.stderr" || true
if [ "${CHECK_STATUS}" -ne 0 ] && { [ "${STATUS}" = "smoke_sim_time_reached" ] || [ "${STATUS}" = "sim_time_reached" ]; }; then
  if [ "${PHASE}" = "2" ]; then
    STATUS="smoke_outputs_missing"
  else
    STATUS="outputs_missing"
  fi
  NOTES="sim-time stop_rule_sec reached, but required data collection files are missing"
  python3 - "${RUN_DIR}" "${RUN_ID}" "${SCENARIO_NAME}" "${SCENARIO_ID}" "${MODE}" "${STATUS}" "${NOTES}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
summary = {
    "run_id": sys.argv[2],
    "scenario_name": sys.argv[3],
    "scenario_id": sys.argv[4],
    "mode": sys.argv[5],
    "status": sys.argv[6],
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    "notes": sys.argv[7],
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY
fi
record_manifest "${STATUS}" "${NOTES}"
echo "${RUN_DIR}"
