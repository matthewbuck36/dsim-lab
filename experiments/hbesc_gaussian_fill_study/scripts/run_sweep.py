#!/usr/bin/env python3

import argparse
import csv
import subprocess
import sys
from pathlib import Path


def scenario_paths_from_csv(path: Path) -> list[Path]:
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    scenario_col = "scenario_config"
    if not rows or scenario_col not in rows[0]:
        raise SystemExit(f"{path} must contain a {scenario_col!r} column")
    return [Path(row[scenario_col]) for row in rows if row.get(scenario_col)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a controlled list of HBESC scenario files.")
    parser.add_argument("scenarios", nargs="*", help="Scenario JSON files.")
    parser.add_argument("--csv", help="CSV with a scenario_config column.")
    parser.add_argument("--execute", action="store_true", help="Run Gazebo instead of dry-run.")
    parser.add_argument("--wall-timeout", type=int, default=180)
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of scenarios to run; 0 means no limit.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    run_one = script_dir / "run_one_trial.sh"

    scenarios = [Path(item) for item in args.scenarios]
    if args.csv:
        scenarios.extend(scenario_paths_from_csv(Path(args.csv)))

    if not scenarios:
        raise SystemExit("No scenarios provided.")

    if args.limit > 0:
        scenarios = scenarios[: args.limit]

    mode_arg = "--execute" if args.execute else "--dry-run"
    failures = 0
    for scenario in scenarios:
        cmd = [
            str(run_one),
            mode_arg,
            "--wall-timeout",
            str(args.wall_timeout),
            str(scenario),
        ]
        print(" ".join(cmd), flush=True)
        completed = subprocess.run(cmd, check=False)
        if completed.returncode != 0:
            failures += 1
            if args.execute:
                print(f"Scenario failed: {scenario}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
