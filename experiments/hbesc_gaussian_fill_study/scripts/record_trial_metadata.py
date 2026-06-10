#!/usr/bin/env python3

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "run_id",
    "phase",
    "scenario_id",
    "method",
    "status",
    "scenario_config",
    "cost_function_config",
    "controller_config",
    "filter_config",
    "rotate_frame_config",
    "sensor_transform_config",
    "data_dir",
    "sim_duration_sec",
    "started_at",
    "completed_at",
    "final_distance_m",
    "min_distance_m",
    "time_to_success_sec",
    "success_radius_m",
    "tail_mean_distance_m",
    "tail_std_distance_m",
    "path_length_m",
    "max_vx_cmd_mps",
    "max_wz_cmd_radps",
    "max_left_wheel_rpm",
    "max_right_wheel_rpm",
    "vx_saturation_pct",
    "wz_saturation_pct",
    "physical_feasibility_label",
    "gaussian_fill_count",
    "notes",
]


def infer_method(scenario: dict) -> str:
    launch = scenario.get("launch", {})
    if launch.get("use_pde_extensions") is True:
        return "gaussian_fill"
    return "baseline_hbesc"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Append or replace one results manifest row.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--phase", default="2")
    parser.add_argument("--status", required=True)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    run_dir = Path(args.run_dir)
    scenario_path = Path(args.scenario)
    scenario = read_json(scenario_path)
    launch = scenario.get("launch", {})
    summary = read_json(run_dir / "summary.json")
    metrics = read_json(run_dir / "summary_metrics.json")
    metadata = read_json(run_dir / "trial_metadata.json")

    completed = summary.get("completed_at_utc") or datetime.now(timezone.utc).isoformat()
    started = metadata.get("created_at_utc", "")

    row = {
        "run_id": args.run_id,
        "phase": args.phase,
        "scenario_id": scenario.get("test_id", scenario.get("name", "")),
        "method": infer_method(scenario),
        "status": args.status,
        "scenario_config": str(scenario_path),
        "cost_function_config": launch.get("cost_function_config_filepath", ""),
        "controller_config": launch.get("controller_config_filepath", ""),
        "filter_config": launch.get("filter_config_filepath", ""),
        "rotate_frame_config": launch.get("rotate_frame_config_filepath", ""),
        "sensor_transform_config": launch.get("sensor_transform_config_filepath", ""),
        "data_dir": str(run_dir),
        "sim_duration_sec": scenario.get("stop_rule_sec", ""),
        "started_at": started,
        "completed_at": completed,
        "final_distance_m": metrics.get("final_distance_m", ""),
        "min_distance_m": metrics.get("min_distance_m", ""),
        "time_to_success_sec": metrics.get("time_to_success_sec", ""),
        "success_radius_m": metrics.get("success_radius_m", ""),
        "tail_mean_distance_m": metrics.get("tail_mean_distance_m", ""),
        "tail_std_distance_m": metrics.get("tail_std_distance_m", ""),
        "path_length_m": metrics.get("path_length_m", ""),
        "max_vx_cmd_mps": metrics.get("max_vx_cmd_mps", ""),
        "max_wz_cmd_radps": metrics.get("max_wz_cmd_radps", ""),
        "max_left_wheel_rpm": metrics.get("max_left_wheel_rpm", ""),
        "max_right_wheel_rpm": metrics.get("max_right_wheel_rpm", ""),
        "vx_saturation_pct": metrics.get("vx_saturation_pct", ""),
        "wz_saturation_pct": metrics.get("wz_saturation_pct", ""),
        "physical_feasibility_label": metrics.get("physical_feasibility_label", ""),
        "gaussian_fill_count": metrics.get("gaussian_fill_count", ""),
        "notes": args.notes,
    }

    existing = []
    if manifest_path.exists() and manifest_path.stat().st_size > 0:
        with manifest_path.open(newline="", encoding="utf-8") as handle:
            existing = list(csv.DictReader(handle))

    existing = [entry for entry in existing if entry.get("run_id") != args.run_id]
    existing.append(row)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(existing)

    print(f"Recorded manifest row for {args.run_id}: {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
