#!/usr/bin/env python3

import csv
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parents[1]
MATRIX = EXP_DIR / "configs" / "scenarios" / "phase5_expanded_characterization_matrix.csv"
MANIFEST = EXP_DIR / "results_manifest.csv"
BATCH_DIR = EXP_DIR / "results" / "batches" / "phase5_expanded_execute"
FIGURES_DIR = BATCH_DIR / "figures"
METRICS_CSV = BATCH_DIR / "phase5_expanded_metrics.csv"
SUMMARY_JSON = BATCH_DIR / "phase5_expanded_summary.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def resolve_path(value: str) -> Path:
    path = Path(os.path.expandvars(os.path.expanduser(value)))
    if path.is_absolute():
        return path
    return (EXP_DIR.parents[1] / path).resolve()


def to_float(value) -> float | None:
    if value in ("", None):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def latest_success_by_scenario(rows: list[dict]) -> dict[str, dict]:
    successes = [row for row in rows if row.get("status") == "sim_time_reached"]
    latest: dict[str, dict] = {}
    for row in successes:
        scenario_id = row.get("scenario_id", "")
        if not scenario_id.startswith("P5B-"):
            continue
        previous = latest.get(scenario_id)
        if previous is None or row.get("completed_at", "") > previous.get("completed_at", ""):
            latest[scenario_id] = row
    return latest


def load_metrics(row: dict) -> dict:
    run_dir = Path(row["data_dir"])
    metrics_path = run_dir / "summary_metrics.json"
    if not metrics_path.exists():
        return {}
    return read_json(metrics_path)


def build_rows() -> list[dict]:
    matrix_rows = read_csv(MATRIX)
    manifest_rows = read_csv(MANIFEST)
    latest = latest_success_by_scenario(manifest_rows)
    output_rows: list[dict] = []

    for matrix_row in matrix_rows:
        scenario_id = matrix_row["scenario_id"]
        manifest_row = latest.get(scenario_id)
        if manifest_row is None:
            raise SystemExit(f"Missing successful execute row for {scenario_id}")

        scenario = read_json(resolve_path(matrix_row["scenario_config"]))
        metrics = load_metrics(manifest_row)
        launch = scenario.get("launch", {})
        row = {
            "scenario_id": scenario_id,
            "run_id": manifest_row.get("run_id", ""),
            "axis": matrix_row.get("axis", ""),
            "method": matrix_row.get("method", ""),
            "cost_family": matrix_row.get("cost_family", ""),
            "speed_label": matrix_row.get("speed_label", ""),
            "start_x": matrix_row.get("start_x", ""),
            "start_y": matrix_row.get("start_y", ""),
            "stop_rule_sec": matrix_row.get("stop_rule_sec", ""),
            "status": manifest_row.get("status", ""),
            "run_dir": manifest_row.get("data_dir", ""),
            "cost_function_config": launch.get("cost_function_config_filepath", ""),
            "controller_config": launch.get("controller_config_filepath", ""),
            "barrier_alpha": scenario.get("barrier_alpha", ""),
            "cross_valley_beta": scenario.get("cross_valley_beta", ""),
            "tilt_gamma": scenario.get("tilt_gamma", ""),
            "noise_std_dev": scenario.get("noise_std_dev", ""),
            "noise_seed": scenario.get("noise_seed", ""),
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
        }
        row["entered_success_radius"] = "yes" if row["time_to_success_sec"] not in ("", None) else "no"
        output_rows.append(row)
    return output_rows


def write_metrics(rows: list[dict]) -> None:
    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict]) -> dict:
    axis_counts = Counter(row["axis"] for row in rows)
    axis_success = defaultdict(int)
    method_success = defaultdict(int)
    physical_counts = Counter(row["physical_feasibility_label"] or "unknown" for row in rows)
    for row in rows:
        if row["entered_success_radius"] == "yes":
            axis_success[row["axis"]] += 1
            method_success[row["method"]] += 1

    return {
        "matrix_csv": str(MATRIX),
        "metrics_csv": str(METRICS_CSV),
        "batch_dir": str(BATCH_DIR),
        "total_rows": len(rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "axis_counts": dict(axis_counts),
        "axis_success_counts": dict(axis_success),
        "method_counts": dict(Counter(row["method"] for row in rows)),
        "method_success_counts": dict(method_success),
        "physical_feasibility_counts": dict(physical_counts),
        "gaussian_fill_rows": sum(1 for row in rows if row["method"] == "gaussian_fill"),
        "baseline_rows": sum(1 for row in rows if row["method"] == "baseline_hbesc"),
        "success_radius_entries": sum(1 for row in rows if row["entered_success_radius"] == "yes"),
    }


def save_summary(summary: dict) -> None:
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def plot_success_by_axis(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    axes = sorted(set(row["axis"] for row in rows))
    counts = [sum(1 for row in rows if row["axis"] == axis) for axis in axes]
    successes = [sum(1 for row in rows if row["axis"] == axis and row["entered_success_radius"] == "yes") for axis in axes]
    pct = [successes[i] / counts[i] * 100.0 for i in range(len(axes))]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(axes)), pct, color="#356ca5")
    ax.set_xticks(range(len(axes)))
    ax.set_xticklabels(axes, rotation=35, ha="right")
    ax.set_ylabel("Entered 2 m radius (%)")
    ax.set_title("Phase 5B Success Rate By Characterization Axis")
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_success_by_axis.png", dpi=160)
    plt.close(fig)


def plot_alpha_speed(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    selected = [
        row
        for row in rows
        if row["axis"] == "double_well_alpha_speed" and row["method"] == "baseline_hbesc"
    ]
    speeds = ["vx005", "vx010", "vx015", "vx020", "real"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for speed in speeds:
        points = []
        for row in selected:
            if row["speed_label"] != speed:
                continue
            alpha = to_float(row["barrier_alpha"])
            final_distance = to_float(row["final_distance_m"])
            if alpha is not None and final_distance is not None:
                points.append((alpha, final_distance))
        points.sort()
        if points:
            ax.plot([p[0] for p in points], [p[1] for p in points], marker="o", label=speed)
    ax.set_xlabel("Double-well alpha")
    ax.set_ylabel("Final distance to target (m)")
    ax.set_title("Phase 5B Baseline Double-Well Alpha-Speed Sweep")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_alpha_speed_final_distance.png", dpi=160)
    plt.close(fig)


def plot_alpha_speed_heatmap(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    selected = [
        row
        for row in rows
        if row["axis"] == "double_well_alpha_speed" and row["method"] == "baseline_hbesc"
    ]
    alphas = sorted({to_float(row["barrier_alpha"]) for row in selected if to_float(row["barrier_alpha"]) is not None})
    speeds = ["vx005", "vx010", "vx015", "vx020", "real"]
    values = np.full((len(alphas), len(speeds)), np.nan)

    for row in selected:
        alpha = to_float(row["barrier_alpha"])
        final_distance = to_float(row["final_distance_m"])
        if alpha is None or final_distance is None or row["speed_label"] not in speeds:
            continue
        values[alphas.index(alpha), speeds.index(row["speed_label"])] = final_distance

    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(speeds)))
    ax.set_xticklabels(speeds)
    ax.set_yticks(range(len(alphas)))
    ax.set_yticklabels([f"{alpha:g}" for alpha in alphas])
    ax.set_xlabel("Speed authority")
    ax.set_ylabel("Double-well alpha")
    ax.set_title("Phase 5B Final Distance Heatmap: Alpha x Speed")
    for row_idx, alpha in enumerate(alphas):
        for col_idx, _speed in enumerate(speeds):
            value = values[row_idx, col_idx]
            if not np.isnan(value):
                ax.text(col_idx, row_idx, f"{value:.2f}", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(image, ax=ax, label="Final distance to target (m)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_alpha_speed_final_distance_heatmap.png", dpi=160)
    plt.close(fig)


def plot_axis_method_success_heatmap(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    axes = sorted(set(row["axis"] for row in rows))
    methods = ["baseline_hbesc", "gaussian_fill"]
    values = np.full((len(axes), len(methods)), np.nan)

    for row_idx, axis in enumerate(axes):
        for col_idx, method in enumerate(methods):
            subset = [row for row in rows if row["axis"] == axis and row["method"] == method]
            if not subset:
                continue
            successes = sum(1 for row in subset if row["entered_success_radius"] == "yes")
            values[row_idx, col_idx] = successes / len(subset) * 100.0

    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(values, cmap="Blues", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=20, ha="right")
    ax.set_yticks(range(len(axes)))
    ax.set_yticklabels(axes)
    ax.set_title("Phase 5B Success-Rate Heatmap: Axis x Method")
    for row_idx, _axis in enumerate(axes):
        for col_idx, _method in enumerate(methods):
            value = values[row_idx, col_idx]
            if not np.isnan(value):
                ax.text(col_idx, row_idx, f"{value:.0f}%", ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(image, ax=ax, label="Entered 2 m radius (%)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_axis_method_success_heatmap.png", dpi=160)
    plt.close(fig)


def plot_start_grid(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    selected = [row for row in rows if row["axis"] == "starting_position_grid"]
    fig, ax = plt.subplots(figsize=(7, 6))
    for method, marker in [("baseline_hbesc", "o"), ("gaussian_fill", "s")]:
        xs = []
        ys = []
        colors = []
        for row in selected:
            if row["method"] != method:
                continue
            start_x = to_float(row["start_x"])
            start_y = to_float(row["start_y"])
            final_distance = to_float(row["final_distance_m"])
            if start_x is not None and start_y is not None and final_distance is not None:
                xs.append(start_x)
                ys.append(start_y)
                colors.append(final_distance)
        if xs:
            scatter = ax.scatter(xs, ys, c=colors, marker=marker, s=90, label=method, cmap="viridis")
    ax.scatter([10], [10], marker="*", s=180, color="red", label="target")
    ax.scatter([2], [2], marker="x", s=120, color="black", label="local basin")
    ax.set_xlabel("start x")
    ax.set_ylabel("start y")
    ax.set_title("Phase 5B Start Grid Final Distance")
    ax.legend()
    fig.colorbar(scatter, ax=ax, label="Final distance (m)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_start_grid_final_distance.png", dpi=160)
    plt.close(fig)


def plot_physical_feasibility(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    labels = sorted(set(row["physical_feasibility_label"] or "unknown" for row in rows))
    methods = ["baseline_hbesc", "gaussian_fill"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = [0] * len(methods)
    for label in labels:
        values = [sum(1 for row in rows if row["method"] == method and (row["physical_feasibility_label"] or "unknown") == label) for method in methods]
        ax.bar(methods, values, bottom=bottom, label=label)
        bottom = [bottom[i] + values[i] for i in range(len(values))]
    ax.set_ylabel("Run count")
    ax.set_title("Phase 5B Physical Feasibility Labels")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5b_physical_feasibility.png", dpi=160)
    plt.close(fig)


def make_plots(rows: list[dict]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    mpl_config = FIGURES_DIR / "mplconfig"
    mpl_config.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))
    plot_success_by_axis(rows)
    plot_alpha_speed(rows)
    plot_alpha_speed_heatmap(rows)
    plot_axis_method_success_heatmap(rows)
    plot_start_grid(rows)
    plot_physical_feasibility(rows)


def main() -> int:
    rows = build_rows()
    write_metrics(rows)
    summary = build_summary(rows)
    save_summary(summary)
    make_plots(rows)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
