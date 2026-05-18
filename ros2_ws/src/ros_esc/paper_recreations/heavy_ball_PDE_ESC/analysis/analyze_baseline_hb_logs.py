#!/usr/bin/env python3
"""Analyze baseline Heavy-Ball ESC experiment logs.

The script reads the writing-folder baseline report manifest by default. Fill
in the run_folder column after each manual Gazebo run, then run this script to
create a metrics CSV and, optionally, report figures.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev


DEFAULT_MANIFEST = (
    "~/dsim-lab/writing/heavy_ball_PDE_ESC/"
    "baseline_hb_report/baseline_hb_run_manifest.csv"
)
DEFAULT_OUTPUT_DIR = (
    "~/dsim-lab/writing/heavy_ball_PDE_ESC/"
    "baseline_hb_report/figures"
)


def expand_path(path_str: str) -> Path:
    return Path(path_str).expanduser()


def read_numeric_csv(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            rows.append([float(value) for value in row])
    return rows


def first_time_inside(rows: list[list[float]], cx: float, cy: float, radius: float):
    for row in rows:
        if math.hypot(row[1] - cx, row[2] - cy) < radius:
            return row[0]
    return ""


def last_time_inside(rows: list[list[float]], cx: float, cy: float, radius: float):
    last = ""
    for row in rows:
        if math.hypot(row[1] - cx, row[2] - cy) < radius:
            last = row[0]
    return last


def finite_rows(rows: list[list[float]]) -> bool:
    return all(all(math.isfinite(value) for value in row) for row in rows)


def summarize_run(entry: dict[str, str], tail_seconds: float, sat_tol: float):
    run_folder = expand_path(entry["run_folder"])
    odom = read_numeric_csv(run_folder / "odometry.csv")
    cost = read_numeric_csv(run_folder / "cost_value.csv")
    control = read_numeric_csv(run_folder / "control_value.csv")

    target_x = float(entry["target_x"])
    target_y = float(entry["target_y"])
    max_vx = float(entry["max_vx_limit"])
    max_wz = float(entry["max_wz_limit"])
    end_time = odom[-1][0]
    tail_start = max(0.0, end_time - tail_seconds)

    tail_odom = [row for row in odom if row[0] >= tail_start]
    tail_cost = [row for row in cost if row[0] >= tail_start]
    tail_control = [row for row in control if row[0] >= tail_start]

    target_dist = [math.hypot(row[1] - target_x, row[2] - target_y) for row in odom]
    tail_target_dist = [
        math.hypot(row[1] - target_x, row[2] - target_y) for row in tail_odom
    ]
    closest_index = min(range(len(target_dist)), key=target_dist.__getitem__)

    vx_values = [abs(row[1]) for row in control]
    wz_values = [abs(row[6]) for row in control]
    vx_sat = [value >= sat_tol * max_vx for value in vx_values] if max_vx > 0 else []
    wz_sat = [value >= sat_tol * max_wz for value in wz_values] if max_wz > 0 else []

    local_x = entry.get("local_x", "").strip()
    local_y = entry.get("local_y", "").strip()
    if local_x and local_y:
        lx = float(local_x)
        ly = float(local_y)
        first_local = first_time_inside(odom, lx, ly, 1.0)
        last_local = last_time_inside(odom, lx, ly, 1.0)
        closest_local = min(math.hypot(row[1] - lx, row[2] - ly) for row in odom)
    else:
        first_local = ""
        last_local = ""
        closest_local = ""

    all_finite = finite_rows(odom) and finite_rows(cost) and finite_rows(control)

    return {
        "test_id": entry["test_id"],
        "run_folder": str(run_folder),
        "duration_sec": f"{end_time:.3f}",
        "final_x": f"{odom[-1][1]:.6f}",
        "final_y": f"{odom[-1][2]:.6f}",
        "final_dist_to_target": f"{target_dist[-1]:.6f}",
        "closest_dist_to_target": f"{target_dist[closest_index]:.6f}",
        "closest_target_time": f"{odom[closest_index][0]:.3f}",
        "tail_mean_x": f"{mean(row[1] for row in tail_odom):.6f}",
        "tail_mean_y": f"{mean(row[2] for row in tail_odom):.6f}",
        "tail_mean_dist_to_target": f"{mean(tail_target_dist):.6f}",
        "tail_std_dist_to_target": f"{pstdev(tail_target_dist):.6f}",
        "final_cost": f"{cost[-1][1]:.6f}",
        "tail_mean_cost": f"{mean(row[1] for row in tail_cost):.6f}",
        "tail_min_cost": f"{min(row[1] for row in tail_cost):.6f}",
        "max_abs_vx": f"{max(vx_values):.6f}",
        "max_abs_wz": f"{max(wz_values):.6f}",
        "tail_mean_abs_vx": f"{mean(abs(row[1]) for row in tail_control):.6f}",
        "tail_mean_abs_wz": f"{mean(abs(row[6]) for row in tail_control):.6f}",
        "vx_saturation_percent": f"{100.0 * sum(vx_sat) / len(vx_sat):.2f}",
        "wz_saturation_percent": f"{100.0 * sum(wz_sat) / len(wz_sat):.2f}",
        "first_time_inside_target_radius_2m": first_time_inside(
            odom, target_x, target_y, 2.0
        ),
        "first_time_inside_local_radius_1m": first_local,
        "last_time_inside_local_radius_1m": last_local,
        "closest_dist_to_local": closest_local,
        "all_values_finite": str(all_finite),
        "notes": entry.get("notes", ""),
    }


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_metrics(rows: list[dict[str, str]], output_csv: Path):
    if not rows:
        return
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_cost_function_from_scenario(scenario_path: Path):
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr

    with scenario_path.open("r", encoding="utf-8") as handle:
        scenario = json.load(handle)

    cost_path = expand_path(scenario["launch"]["cost_function_config_filepath"])
    with cost_path.open("r", encoding="utf-8") as handle:
        cost_config = json.load(handle)

    params = cost_config["CostFunction"]["params"]
    expression = parse_expr(params["function"])
    substitutions = params.get("substitutions", {})
    for name, value in substitutions.items():
        if isinstance(value, str):
            value = parse_expr(value)
        expression = expression.subs(sp.Symbol(name), value)

    symbols = [sp.Symbol(symbol_name) for symbol_name in params["symbols"]]
    function = sp.lambdify(symbols, expression, "numpy")
    return function, params["symbols"]


def make_plots(entry: dict[str, str], output_dir: Path, tail_seconds: float):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    run_folder = expand_path(entry["run_folder"])
    odom = read_numeric_csv(run_folder / "odometry.csv")
    cost = read_numeric_csv(run_folder / "cost_value.csv")
    control = read_numeric_csv(run_folder / "control_value.csv")

    target_x = float(entry["target_x"])
    target_y = float(entry["target_y"])
    max_vx = float(entry["max_vx_limit"])
    max_wz = float(entry["max_wz_limit"])
    test_id = entry["test_id"]

    xs = np.array([row[1] for row in odom])
    ys = np.array([row[2] for row in odom])
    times = np.array([row[0] for row in odom])
    dist = np.hypot(xs - target_x, ys - target_y)

    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    try:
        cost_fn, symbol_names = parse_cost_function_from_scenario(
            expand_path(entry["scenario_path"])
        )
        margin = 1.0
        x_min = min(-1.0, float(xs.min()) - margin, target_x - 3.0)
        x_max = max(12.0, float(xs.max()) + margin, target_x + 3.0)
        y_min = min(-1.0, float(ys.min()) - margin, target_y - 3.0)
        y_max = max(12.0, float(ys.max()) + margin, target_y + 3.0)
        grid_x, grid_y = np.meshgrid(
            np.linspace(x_min, x_max, 160),
            np.linspace(y_min, y_max, 160),
        )
        values = []
        for symbol_name in symbol_names:
            if symbol_name == "t":
                values.append(0.0)
            elif symbol_name == "x":
                values.append(grid_x)
            elif symbol_name == "y":
                values.append(grid_y)
            elif symbol_name == "z":
                values.append(0.0)
            else:
                values.append(0.0)
        z_grid = cost_fn(*values)
        ax.contour(grid_x, grid_y, z_grid, levels=20, linewidths=0.6)
    except Exception as exc:  # pragma: no cover - plotting should be best effort
        ax.text(0.02, 0.02, f"Contour skipped: {exc}", transform=ax.transAxes)

    ax.plot(xs, ys, color="tab:blue", linewidth=1.5, label="trajectory")
    ax.scatter([xs[0]], [ys[0]], color="tab:green", label="start", zorder=3)
    ax.scatter([target_x], [target_y], color="tab:red", label="target", zorder=3)
    if entry.get("local_x", "").strip() and entry.get("local_y", "").strip():
        ax.scatter(
            [float(entry["local_x"])],
            [float(entry["local_y"])],
            color="tab:orange",
            label="local basin",
            zorder=3,
        )
    ax.set_title(f"{test_id}: trajectory")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / f"{test_id}_trajectory.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(7.0, 7.5), sharex=False)
    axes[0].plot([row[0] for row in cost], [row[1] for row in cost])
    axes[0].set_title(f"{test_id}: cost")
    axes[0].set_ylabel("cost")

    axes[1].plot(times, dist)
    axes[1].axhline(2.0, color="tab:gray", linestyle="--", linewidth=0.8)
    axes[1].set_title("distance to target")
    axes[1].set_ylabel("distance [m]")

    ctrl_time = [row[0] for row in control]
    axes[2].plot(ctrl_time, [abs(row[1]) for row in control], label="|vx|")
    axes[2].plot(ctrl_time, [abs(row[6]) for row in control], label="|wz|")
    axes[2].axhline(max_vx, color="tab:blue", linestyle="--", linewidth=0.8)
    axes[2].axhline(max_wz, color="tab:orange", linestyle="--", linewidth=0.8)
    axes[2].set_title("control magnitudes")
    axes[2].set_xlabel("time [s]")
    axes[2].legend()

    fig.tight_layout()
    fig.savefig(output_dir / f"{test_id}_timeseries.png", dpi=200)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--output-csv",
        default=(
            "~/dsim-lab/writing/heavy_ball_PDE_ESC/"
            "baseline_hb_report/baseline_hb_metrics.csv"
        ),
    )
    parser.add_argument("--figures-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tail-seconds", type=float, default=30.0)
    parser.add_argument("--sat-tol", type=float, default=0.98)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(expand_path(args.manifest))
    metrics_rows = []
    skipped = []

    for entry in manifest:
        run_folder = entry.get("run_folder", "").strip()
        if not run_folder:
            skipped.append(entry["test_id"])
            continue
        metrics_rows.append(summarize_run(entry, args.tail_seconds, args.sat_tol))
        if args.plots:
            make_plots(entry, expand_path(args.figures_dir), args.tail_seconds)

    write_metrics(metrics_rows, expand_path(args.output_csv))
    print(f"Analyzed {len(metrics_rows)} completed runs.")
    if skipped:
        print("Skipped tests with blank run_folder: " + ", ".join(skipped))
    if metrics_rows:
        print(f"Wrote metrics: {expand_path(args.output_csv)}")
        if args.plots:
            print(f"Wrote figures under: {expand_path(args.figures_dir)}")


if __name__ == "__main__":
    main()
