#!/usr/bin/env python3

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


EXECUTE_SUCCESS_STATUSES = {"sim_time_reached", "smoke_sim_time_reached"}
DRY_RUN_SUCCESS_STATUSES = {"dry_run_passed"}
PLAN_FIELDS = [
    "order",
    "scenario_config",
    "scenario_id",
    "name",
    "phase",
    "stop_rule_sec",
    "method",
    "action",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "batch"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_paths_from_csv(path: Path) -> list[tuple[str, Path]]:
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    scenario_col = "scenario_config"
    if not rows or scenario_col not in rows[0]:
        raise SystemExit(f"{path} must contain a {scenario_col!r} column")
    return [(row[scenario_col], path) for row in rows if row.get(scenario_col)]


def resolve_scenario_path(raw_path: str, repo_root: Path, csv_path: Path | None = None) -> Path:
    expanded = os.path.expandvars(raw_path)
    path = Path(expanded).expanduser()
    if path.is_absolute():
        return path.resolve(strict=False)

    candidates = [Path.cwd() / path, repo_root / path]
    if csv_path is not None:
        candidates.append(csv_path.parent / path)
    candidates.append(path)

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve(strict=False)


def infer_method(scenario: dict) -> str:
    if scenario.get("launch", {}).get("use_pde_extensions") is True:
        return "gaussian_fill"
    return "baseline_hbesc"


def load_manifest_successes(manifest_path: Path, execute: bool) -> set[str]:
    if not manifest_path.exists() or manifest_path.stat().st_size == 0:
        return set()

    success_statuses = EXECUTE_SUCCESS_STATUSES if execute else DRY_RUN_SUCCESS_STATUSES
    successes: set[str] = set()
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") in success_statuses and row.get("scenario_id"):
                successes.add(row["scenario_id"])
    return successes


def write_plan(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, summary: dict) -> None:
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def run_command(cmd: list[str], env: dict, stdout_path: Path, stderr_path: Path) -> tuple[int, str, str]:
    completed = subprocess.run(cmd, check=False, text=True, capture_output=True, env=env)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode, completed.stdout, completed.stderr


def extract_run_dir(stdout: str, stderr: str) -> str:
    for line in reversed((stdout + "\n" + stderr).splitlines()):
        text = line.strip()
        if not text:
            continue
        if text.startswith("Run directory:"):
            return text.split("Run directory:", 1)[1].strip()
        path = Path(text)
        if path.is_absolute() and path.exists() and (path / "summary.json").exists():
            return str(path)
    return ""


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a reproducible batch of HBESC/Gaussian-fill scenario files."
    )
    parser.add_argument("scenarios", nargs="*", help="Scenario JSON files.")
    parser.add_argument("--csv", action="append", default=[], help="CSV with a scenario_config column.")
    parser.add_argument("--dry-run", action="store_true", help="Validate scenarios without starting Gazebo. This is the default.")
    parser.add_argument("--execute", action="store_true", help="Run Gazebo for each scenario.")
    parser.add_argument("--headless", action="store_true", help="Request gzserver and live_plot_mode None for each trial.")
    parser.add_argument("--wall-timeout", type=int, default=180, help="Per-trial wall-clock timeout for the sim-time monitor.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of scenarios to consider; 0 means no limit.")
    parser.add_argument("--resume", action="store_true", help="Skip scenarios already completed successfully in results_manifest.csv.")
    parser.add_argument("--retries", type=int, default=0, help="Retry each failed scenario once at most. Use 0 or 1.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first failed scenario.")
    parser.add_argument("--plan-only", action="store_true", help="Write the batch plan and summary, but do not run trials.")
    parser.add_argument("--batch-id", help="Optional stable batch id for results/batches/<batch-id>.")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if args.execute and args.dry_run:
        raise SystemExit("Choose either --execute or --dry-run, not both.")
    if args.wall_timeout <= 0:
        raise SystemExit("--wall-timeout must be positive.")
    if args.limit < 0:
        raise SystemExit("--limit cannot be negative.")
    if args.retries not in (0, 1):
        raise SystemExit("--retries supports 0 or 1 to keep batch retries bounded.")

    script_dir = Path(__file__).resolve().parent
    exp_dir = script_dir.parent
    repo_root = exp_dir.parent.parent
    manifest_path = exp_dir / "results_manifest.csv"
    run_one = script_dir / "run_one_trial.sh"
    execute = args.execute
    mode_name = "execute" if execute else "dry_run"

    scenario_specs: list[tuple[str, Path | None]] = [(item, None) for item in args.scenarios]
    for csv_arg in args.csv:
        csv_path = resolve_scenario_path(csv_arg, repo_root)
        scenario_specs.extend(scenario_paths_from_csv(csv_path))

    if not scenario_specs:
        raise SystemExit("No scenarios provided.")
    if args.limit > 0:
        scenario_specs = scenario_specs[: args.limit]

    completed_scenario_ids = load_manifest_successes(manifest_path, execute) if args.resume else set()
    batch_id = safe_token(args.batch_id) if args.batch_id else f"{utc_stamp()}_{mode_name}_batch"
    batch_dir = exp_dir / "results" / "batches" / batch_id
    if batch_dir.exists():
        raise SystemExit(f"Batch directory already exists: {batch_dir}")
    logs_dir = batch_dir / "logs"
    logs_dir.mkdir(parents=True)

    plan_rows: list[dict] = []
    items: list[dict] = []
    for order, (raw_path, csv_path) in enumerate(scenario_specs, start=1):
        scenario_path = resolve_scenario_path(raw_path, repo_root, csv_path)
        if not scenario_path.exists():
            raise SystemExit(f"Scenario file not found: {scenario_path}")
        scenario = read_json(scenario_path)
        scenario_id = scenario.get("test_id", scenario.get("name", scenario_path.stem))
        action = "skip_resume" if scenario_id in completed_scenario_ids else "run"
        row = {
            "order": order,
            "scenario_config": str(scenario_path),
            "scenario_id": scenario_id,
            "name": scenario.get("name", scenario_path.stem),
            "phase": scenario.get("phase", ""),
            "stop_rule_sec": scenario.get("stop_rule_sec", ""),
            "method": infer_method(scenario),
            "action": action,
        }
        plan_rows.append(row)
        items.append({"path": scenario_path, "scenario": scenario, "plan": row})

    write_plan(batch_dir / "batch_plan.csv", plan_rows)
    summary = {
        "batch_id": batch_id,
        "mode": mode_name,
        "headless": args.headless,
        "wall_timeout": args.wall_timeout,
        "resume": args.resume,
        "retries": args.retries,
        "plan_only": args.plan_only,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "batch_dir": str(batch_dir),
        "plan_csv": str(batch_dir / "batch_plan.csv"),
        "results": [],
    }
    write_summary(batch_dir / "batch_summary.json", summary)

    print(f"Batch directory: {batch_dir}")
    print(f"Planned scenarios: {len(plan_rows)}")
    if args.plan_only:
        print("Plan-only mode; no trials started.")
        return 0

    failures = 0
    for item in items:
        plan = item["plan"]
        order = int(plan["order"])
        scenario_id = plan["scenario_id"]
        scenario_path = item["path"]
        result = {
            "order": order,
            "scenario_id": scenario_id,
            "scenario_config": str(scenario_path),
            "action": plan["action"],
            "attempts": [],
            "final_returncode": 0,
            "run_dir": "",
        }

        if plan["action"] == "skip_resume":
            result["status"] = "skipped_resume"
            summary["results"].append(result)
            write_summary(batch_dir / "batch_summary.json", summary)
            print(f"[{order}/{len(items)}] Skipping completed scenario: {scenario_id}")
            continue

        print(f"[{order}/{len(items)}] Running {scenario_id}: {scenario_path}")
        max_attempts = args.retries + 1
        scenario_failed = True
        for attempt in range(1, max_attempts + 1):
            cmd = [
                str(run_one),
                "--execute" if execute else "--dry-run",
                "--wall-timeout",
                str(args.wall_timeout),
            ]
            if args.headless:
                cmd.append("--headless")
            cmd.append(str(scenario_path))

            log_token = safe_token(f"{order:03d}_{scenario_id}_attempt{attempt}")
            stdout_path = logs_dir / f"{log_token}.stdout"
            stderr_path = logs_dir / f"{log_token}.stderr"
            cmd_path = logs_dir / f"{log_token}.cmd.txt"
            cmd_path.write_text(" ".join(cmd) + "\n", encoding="utf-8")

            env = os.environ.copy()
            returncode, stdout, stderr = run_command(cmd, env, stdout_path, stderr_path)
            run_dir = extract_run_dir(stdout, stderr)
            attempt_result = {
                "attempt": attempt,
                "returncode": returncode,
                "stdout": str(stdout_path),
                "stderr": str(stderr_path),
                "command": str(cmd_path),
                "run_dir": run_dir,
            }
            result["attempts"].append(attempt_result)
            result["final_returncode"] = returncode
            if run_dir:
                result["run_dir"] = run_dir

            if returncode == 0:
                scenario_failed = False
                break
            if attempt < max_attempts:
                print(f"Retrying failed scenario once: {scenario_id}", file=sys.stderr)

        result["status"] = "failed" if scenario_failed else "succeeded"
        if scenario_failed:
            failures += 1
        summary["results"].append(result)
        write_summary(batch_dir / "batch_summary.json", summary)

        if scenario_failed and args.fail_fast:
            print(f"Stopping after failed scenario: {scenario_id}", file=sys.stderr)
            break

    summary["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    summary["failure_count"] = failures
    write_summary(batch_dir / "batch_summary.json", summary)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
