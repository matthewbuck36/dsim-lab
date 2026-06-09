#!/usr/bin/env python3

import argparse
import csv
import json
import math
import statistics
from pathlib import Path


def read_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            try:
                rows.append([float(value) for value in row])
            except ValueError:
                continue
    return rows


def latest_data_collection_dir(run_dir: Path) -> Path | None:
    data_root = run_dir / "data_collection"
    if not data_root.exists():
        return None
    candidates = [path for path in data_root.iterdir() if path.is_dir() and path.name.startswith("Test_")]
    if not candidates:
        return None
    return sorted(candidates)[-1]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def distance_metrics(odom_rows: list[list[float]], target: dict, success_radius: float) -> dict:
    if not odom_rows or "x" not in target or "y" not in target:
        return {}
    target_x = float(target["x"])
    target_y = float(target["y"])
    distances = []
    for row in odom_rows:
        if len(row) < 3:
            continue
        t, x, y = row[0], row[1], row[2]
        distances.append((t, math.hypot(x - target_x, y - target_y)))
    if not distances:
        return {}
    tail_count = max(1, len(distances) // 10)
    tail = [dist for _, dist in distances[-tail_count:]]
    time_to_success = ""
    for t, dist in distances:
        if dist <= success_radius:
            time_to_success = t
            break
    return {
        "final_distance_m": distances[-1][1],
        "min_distance_m": min(dist for _, dist in distances),
        "time_to_success_sec": time_to_success,
        "success_radius_m": success_radius,
        "tail_mean_distance_m": statistics.fmean(tail),
        "tail_std_distance_m": statistics.pstdev(tail) if len(tail) > 1 else 0.0,
    }


def path_length(odom_rows: list[list[float]]) -> float | str:
    if len(odom_rows) < 2:
        return ""
    total = 0.0
    prev = None
    for row in odom_rows:
        if len(row) < 3:
            continue
        point = (row[1], row[2])
        if prev is not None:
            total += math.hypot(point[0] - prev[0], point[1] - prev[1])
        prev = point
    return total


def control_metrics(control_rows: list[list[float]], controller_config: dict) -> dict:
    if not control_rows:
        return {}
    values = [row for row in control_rows if len(row) >= 7]
    if not values:
        return {}

    params = controller_config.get("params", {})
    radius = float(params.get("wheel_radius", 0.033))
    distance = float(params.get("wheel_distance", 0.158))
    wheel_max_rpm = float(params.get("wheel_max_rpm", 70))
    omega_max = wheel_max_rpm / 60.0 * 2.0 * math.pi
    default_max_vx = omega_max * radius
    default_max_wz = 2.0 * omega_max * radius / distance
    max_vx = params.get("set_max_vx")
    max_wz = params.get("set_max_wz")
    max_vx = default_max_vx if max_vx is None else float(max_vx)
    max_wz = default_max_wz if max_wz is None else float(max_wz)

    vxs = [row[1] for row in values]
    wzs = [row[6] for row in values]
    left_rpm = []
    right_rpm = []
    for vx, wz in zip(vxs, wzs):
        omega_left = (vx - wz * distance / 2.0) / radius
        omega_right = (vx + wz * distance / 2.0) / radius
        left_rpm.append(omega_left * 60.0 / (2.0 * math.pi))
        right_rpm.append(omega_right * 60.0 / (2.0 * math.pi))

    n = len(values)
    vx_sat = sum(1 for vx in vxs if abs(vx) >= 0.98 * max_vx) / n * 100.0 if max_vx else ""
    wz_sat = sum(1 for wz in wzs if abs(wz) >= 0.98 * max_wz) / n * 100.0 if max_wz else ""
    max_abs_vx = max(abs(vx) for vx in vxs)
    max_abs_wz = max(abs(wz) for wz in wzs)
    physical_label = "unknown"
    if max_abs_vx <= 0.22 and max_abs_wz <= 2.84 and max(max(map(abs, left_rpm)), max(map(abs, right_rpm))) <= 70:
        physical_label = "within_turtlebot3_burger_reference_limits"
    else:
        physical_label = "exceeds_turtlebot3_burger_reference_limits"

    return {
        "max_vx_cmd_mps": max_abs_vx,
        "max_wz_cmd_radps": max_abs_wz,
        "max_left_wheel_rpm": max(abs(value) for value in left_rpm),
        "max_right_wheel_rpm": max(abs(value) for value in right_rpm),
        "vx_saturation_pct": vx_sat,
        "wz_saturation_pct": wz_sat,
        "physical_feasibility_label": physical_label,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze one HBESC run directory.")
    parser.add_argument("run_dir")
    parser.add_argument("--success-radius", type=float, default=2.0)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    scenario = load_json(run_dir / "configs" / "scenario_used.json")
    data_dir = latest_data_collection_dir(run_dir)
    metrics: dict = {
        "run_dir": str(run_dir),
        "data_quality": "missing_data_collection",
    }

    if data_dir is not None:
        odom_rows = read_rows(data_dir / "odometry.csv") if (data_dir / "odometry.csv").exists() else []
        control_rows = read_rows(data_dir / "control_value.csv") if (data_dir / "control_value.csv").exists() else []
        metrics.update(distance_metrics(odom_rows, scenario.get("target", {}), args.success_radius))
        metrics["path_length_m"] = path_length(odom_rows)

        controller_config_path = scenario.get("launch", {}).get("controller_config_filepath", "")
        controller_config = {}
        if controller_config_path:
            controller_config = load_json(Path(controller_config_path).expanduser())
        metrics.update(control_metrics(control_rows, controller_config))
        metrics["data_quality"] = "ok" if odom_rows and control_rows else "incomplete_csv"

    out = run_dir / "summary_metrics.json"
    out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
