#!/usr/bin/env python3

import argparse
import csv
import os
from pathlib import Path


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
    except Exception as exc:
        print(f"matplotlib unavailable; no plots generated: {exc}")
        return 0

    xs, ys = read_xy(odom)
    if not xs:
        print("No odometry samples found; no plots generated.")
        return 0

    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, linewidth=1.5)
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.axis("equal")
    plt.tight_layout()
    output = figures_dir / "trajectory.png"
    plt.savefig(output, dpi=150)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
