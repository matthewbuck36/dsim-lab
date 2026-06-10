#!/usr/bin/env python3

import argparse
import ast
import csv
import json
import os
from pathlib import Path


ALLOWED_EXPR_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
}

ALLOWED_EXPR_NAMES = {
    "t",
    "x",
    "y",
    "z",
    "exp",
    "sqrt",
    "sin",
    "cos",
    "tan",
    "pi",
}


def latest_data_collection_dir(run_dir: Path) -> Path | None:
    data_root = run_dir / "data_collection"
    if not data_root.exists():
        return None
    candidates = [path for path in data_root.iterdir() if path.is_dir() and path.name.startswith("Test_")]
    if not candidates:
        return None
    return sorted(candidates)[-1]


def read_xy(path: Path) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) < 3:
                continue
            try:
                xs.append(float(row[1]))
                ys.append(float(row[2]))
            except ValueError:
                continue
    return xs, ys


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def scenario_path(run_dir: Path) -> Path:
    return run_dir / "configs" / "scenario_used.json"


def load_scenario(run_dir: Path) -> dict:
    path = scenario_path(run_dir)
    if not path.exists():
        return {}
    return read_json(path)


def load_cost_expression(scenario: dict) -> str | None:
    cost_path_value = scenario.get("launch", {}).get("cost_function_config_filepath")
    if not cost_path_value:
        return None
    cost_path = resolve_path(str(cost_path_value))
    if not cost_path.exists():
        return None
    cost_config = read_json(cost_path)
    params = cost_config.get("CostFunction", {}).get("params", {})
    expression = params.get("function")
    return str(expression) if expression else None


def validate_expression(expression: str) -> ast.Expression:
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_EXPR_NODES:
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in ALLOWED_EXPR_NAMES:
            raise ValueError(f"Unsupported expression name: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_EXPR_NAMES:
                raise ValueError("Unsupported expression call")
    return tree


def build_plot_bounds(xs: list[float], ys: list[float], scenario: dict) -> tuple[float, float, float, float]:
    points_x = list(xs)
    points_y = list(ys)
    launch = scenario.get("launch", {})
    for key_x, key_y in (("init_x_position", "init_y_position"),):
        try:
            points_x.append(float(launch[key_x]))
            points_y.append(float(launch[key_y]))
        except (KeyError, TypeError, ValueError):
            pass
    for key in ("target", "local_basin"):
        point = scenario.get(key)
        if isinstance(point, dict):
            try:
                points_x.append(float(point["x"]))
                points_y.append(float(point["y"]))
            except (KeyError, TypeError, ValueError):
                pass

    xmin = min(points_x)
    xmax = max(points_x)
    ymin = min(points_y)
    ymax = max(points_y)
    span = max(xmax - xmin, ymax - ymin, 4.0)
    margin = max(1.0, 0.12 * span)
    xmid = 0.5 * (xmin + xmax)
    ymid = 0.5 * (ymin + ymax)
    half = 0.5 * span + margin
    return xmid - half, xmid + half, ymid - half, ymid + half


def evaluate_cost_grid(expression: str, bounds: tuple[float, float, float, float], resolution: int = 220):
    import numpy as np

    tree = validate_expression(expression)
    code = compile(tree, "<cost_function>", "eval")
    xmin, xmax, ymin, ymax = bounds
    grid_x = np.linspace(xmin, xmax, resolution)
    grid_y = np.linspace(ymin, ymax, resolution)
    x_grid, y_grid = np.meshgrid(grid_x, grid_y)
    env = {
        "__builtins__": {},
        "x": x_grid,
        "y": y_grid,
        "z": 0.0,
        "t": 0.0,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "pi": np.pi,
    }
    z_grid = eval(code, env, {})
    z_grid = np.asarray(z_grid, dtype=float)
    if z_grid.shape == ():
        z_grid = np.full_like(x_grid, float(z_grid))
    return x_grid, y_grid, z_grid


def finite_level_range(z_grid) -> tuple[float, float] | None:
    import numpy as np

    finite = z_grid[np.isfinite(z_grid)]
    if finite.size == 0:
        return None
    low, high = np.percentile(finite, [2, 98])
    if not np.isfinite(low) or not np.isfinite(high) or low == high:
        low = float(np.min(finite))
        high = float(np.max(finite))
    if low == high:
        return None
    return float(low), float(high)


def plot_point(ax, point: dict | None, marker: str, color: str, label: str) -> None:
    if not isinstance(point, dict):
        return
    try:
        x_value = float(point["x"])
        y_value = float(point["y"])
    except (KeyError, TypeError, ValueError):
        return
    ax.scatter([x_value], [y_value], marker=marker, s=90, color=color, edgecolor="black", linewidth=0.8, label=label, zorder=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create basic plots for one HBESC run directory.")
    parser.add_argument("run_dir")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    data_dir = latest_data_collection_dir(run_dir)
    figures_dir = run_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    mpl_config = figures_dir / "mplconfig"
    mpl_config.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

    if data_dir is None:
        print("No data_collection/Test_* directory found; no plots generated.")
        return 0

    odom = data_dir / "odometry.csv"
    if not odom.exists():
        print("No odometry.csv found; no trajectory plot generated.")
        return 0

    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception as exc:
        print(f"matplotlib unavailable; no plots generated: {exc}")
        return 0

    xs, ys = read_xy(odom)
    if not xs:
        print("No odometry samples found; no plots generated.")
        return 0

    scenario = load_scenario(run_dir)
    bounds = build_plot_bounds(xs, ys, scenario)
    expression = load_cost_expression(scenario)

    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    if expression:
        try:
            x_grid, y_grid, z_grid = evaluate_cost_grid(expression, bounds)
            level_range = finite_level_range(z_grid)
            if level_range is not None:
                low, high = level_range
                filled_levels = np.linspace(low, high, 28)
                line_levels = np.linspace(low, high, 12)
                filled = ax.contourf(
                    x_grid,
                    y_grid,
                    np.clip(z_grid, low, high),
                    levels=filled_levels,
                    cmap="terrain",
                    alpha=0.82,
                    extend="both",
                )
                lines = ax.contour(
                    x_grid,
                    y_grid,
                    z_grid,
                    levels=line_levels,
                    colors="black",
                    linewidths=0.45,
                    alpha=0.45,
                )
                ax.clabel(lines, inline=True, fontsize=6, fmt="%.2g")
                cbar = fig.colorbar(filled, ax=ax, fraction=0.046, pad=0.04)
                cbar.set_label("cost")
        except Exception as exc:
            print(f"Cost contour unavailable; plotting trajectory only: {exc}")

    ax.plot(xs, ys, color="#17202a", linewidth=1.8, label="trajectory", zorder=4)
    ax.scatter([xs[0]], [ys[0]], marker="o", s=64, color="#1f77b4", edgecolor="white", linewidth=0.8, label="start", zorder=6)
    ax.scatter([xs[-1]], [ys[-1]], marker="s", s=64, color="#d62728", edgecolor="white", linewidth=0.8, label="end", zorder=6)
    plot_point(ax, scenario.get("target"), marker="*", color="#ffbf00", label="target")
    plot_point(ax, scenario.get("local_basin"), marker="X", color="#9467bd", label="local basin")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(color="white", linewidth=0.45, alpha=0.35)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc="upper left", framealpha=0.88, fontsize=8)
    fig.tight_layout()
    output = figures_dir / "trajectory.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
