#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


BASE_FILES = [
    "trial_metadata.json",
    "configs/scenario_used.json",
    "launch_command.txt",
    "logs/scenario_dry_run.stdout",
    "logs/scenario_dry_run.stderr",
    "summary.json",
]

EXPECTED_DATA_FILES = [
    "odometry.csv",
    "sensor_transform.csv",
    "cost_value.csv",
    "filter_value.csv",
    "control_value.csv",
    "comments.txt",
]


def latest_data_collection_dir(run_dir: Path) -> Path | None:
    data_root = run_dir / "data_collection"
    if not data_root.exists():
        return None
    candidates = [path for path in data_root.iterdir() if path.is_dir() and path.name.startswith("Test_")]
    if not candidates:
        return None
    return sorted(candidates)[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check required files for one HBESC trial run directory.")
    parser.add_argument("run_dir")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    report = {
        "run_dir": str(run_dir),
        "status": "pass",
        "missing": [],
        "present": [],
        "warnings": [],
    }

    for rel in BASE_FILES:
        path = run_dir / rel
        if path.exists():
            report["present"].append(rel)
        else:
            report["missing"].append(rel)

    summary_path = run_dir / "summary.json"
    summary = {}
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

    if summary.get("mode") == "execute":
        data_dir = latest_data_collection_dir(run_dir)
        if data_dir is None:
            report["warnings"].append("No data_collection/Test_* directory found.")
        else:
            for name in EXPECTED_DATA_FILES:
                rel = str(data_dir.relative_to(run_dir) / name)
                if (data_dir / name).exists():
                    report["present"].append(rel)
                else:
                    report["missing"].append(rel)

    if report["missing"]:
        report["status"] = "fail"

    output_path = run_dir / "validation_report.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
