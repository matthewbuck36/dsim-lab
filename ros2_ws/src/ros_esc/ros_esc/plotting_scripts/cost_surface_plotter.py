#!/usr/bin/env python3

"""Plot a 3D cost-function surface from a ros_esc cost JSON."""

import argparse
import copy
import json
import math
import os
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from ros_esc_interfaces.msg import StampedFloat64MultiArray

from ros_esc.config_parsing import parse_object_config


def _create_transform(x_pos, y_pos, theta):
    """Create a 4x4 sensor transform at XY with yaw theta."""

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    transform = np.eye(4)
    transform[0, 0] = cos_theta
    transform[0, 1] = -sin_theta
    transform[1, 0] = sin_theta
    transform[1, 1] = cos_theta
    transform[0, 3] = x_pos
    transform[1, 3] = y_pos

    return transform


def _normalize_bool(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _parse_light_sources(args):
    light_sources = []
    for light_idx in range(1, 6):
        light_sources.append({
            "x": getattr(args, f"light_source_{light_idx}_x"),
            "y": getattr(args, f"light_source_{light_idx}_y"),
            "intensity_lumens": getattr(
                args,
                f"light_source_{light_idx}_intensity_lumens",
            ),
        })

    return light_sources


def _configure_launch_lights(cost_function, args):
    if not hasattr(cost_function, "configure_light_sources"):
        return

    cost_function.configure_light_sources(
        args.light_source_count,
        _parse_light_sources(args),
    )


def _evaluate_cost(cost_function, x_pos, y_pos, angles, orientation_mode):
    if orientation_mode == "fixed":
        return float(cost_function.cost_output(0.0, _create_transform(x_pos, y_pos, 0.0)))

    values = np.array([
        float(cost_function.cost_output(0.0, _create_transform(x_pos, y_pos, theta)))
        for theta in angles
    ])

    if orientation_mode == "min":
        return float(np.min(values))
    if orientation_mode == "max":
        return float(np.max(values))

    return float(np.mean(values))


def _load_cost_function(config_path, args):
    with open(os.path.expanduser(config_path), encoding="utf-8") as handle:
        config = json.load(handle)

    if "CostFunction" not in config:
        raise KeyError(f"CostFunction key missing from {config_path}")

    cost_function = parse_object_config(copy.deepcopy(config["CostFunction"]))
    _configure_launch_lights(cost_function, args)

    return cost_function


def _plot_surface(x_grid, y_grid, z_grid, args, lights):
    plot = CostSurfacePlot(x_grid, y_grid, z_grid, args, lights)
    plot.draw()

    _save_snapshot(plot, args, "static")

    if not args.no_show:
        plt.show()


def _snapshot_path(args, suffix):
    output = str(args.output).strip()
    if output:
        return os.path.expanduser(output)

    output_dir = str(args.output_dir).strip()
    if not output_dir:
        return ""

    output_dir = os.path.expanduser(output_dir)
    if args.output_latest_test_dir:
        output_dir = _latest_test_dir(output_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"cost_surface_{suffix}_{timestamp}.png"
    return os.path.join(output_dir, filename)


def _latest_test_dir(output_dir):
    if not os.path.isdir(output_dir):
        return output_dir

    candidates = []
    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)
        if name.startswith("Test_") and os.path.isdir(path):
            candidates.append(path)

    if not candidates:
        return output_dir

    return max(candidates, key=os.path.getmtime)


def _save_snapshot(plot, args, suffix):
    path = _snapshot_path(args, suffix)
    if not path:
        return ""

    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    plot.fig.canvas.draw()
    plot.fig.savefig(path, dpi=args.dpi)
    return path


class CostSurfacePlot:
    """Own the Matplotlib artists for a static or live cost-surface window."""

    def __init__(self, x_grid, y_grid, base_z_grid, args, lights):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.base_z_grid = base_z_grid
        self.z_grid = np.array(base_z_grid, copy=True)
        self.args = args
        self.lights = lights
        self.fill_terms = []
        self.trajectory = []
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.colorbar = None
        self.contour_offset = 0.0
        self.trajectory_line = None
        self.trajectory_dot = None
        self.base_z_min = float(np.nanmin(self.base_z_grid))
        self.base_z_max = float(np.nanmax(self.base_z_grid))
        self.base_z_span = max(self.base_z_max - self.base_z_min, 1e-9)
        self.base_contour_offset = self.base_z_min - 0.08 * self.base_z_span

    def draw(self):
        self.ax.clear()

        z_axis_min, z_axis_max, color_min, color_max = self._plot_limits()
        z_span = max(z_axis_max - z_axis_min, 1e-9)
        self.contour_offset = z_axis_min - 0.08 * z_span
        norm = colors.Normalize(vmin=color_min, vmax=color_max, clip=True)
        display_z_grid = self._display_z_grid(z_axis_min, z_axis_max)

        surface = self.ax.plot_surface(
            self.x_grid,
            self.y_grid,
            display_z_grid,
            cmap=self.args.cmap,
            norm=norm,
            linewidth=0,
            antialiased=True,
            alpha=0.88,
        )
        if self.fill_terms and self.args.show_base_wireframe:
            stride = max(1, int(self.args.resolution // 30))
            self.ax.plot_wireframe(
                self.x_grid,
                self.y_grid,
                self.base_z_grid,
                rstride=stride,
                cstride=stride,
                color="0.25",
                linewidth=0.45,
                alpha=0.28,
                label="original surface",
            )
        if float(np.nanmax(display_z_grid) - np.nanmin(display_z_grid)) > 1e-12:
            self.ax.contour(
                self.x_grid,
                self.y_grid,
                display_z_grid,
                zdir="z",
                offset=self.contour_offset,
                levels=self.args.contours,
                cmap=self.args.cmap,
                norm=norm,
                linewidths=0.8,
            )

        min_idx = np.unravel_index(np.nanargmin(self.z_grid), self.z_grid.shape)
        self.ax.scatter(
            [self.x_grid[min_idx]],
            [self.y_grid[min_idx]],
            [display_z_grid[min_idx]],
            c="black",
            s=55,
            marker="x",
            label="grid min",
        )

        for light_idx, light in enumerate(self.lights, start=1):
            if (
                light["x"] is None
                or light["y"] is None
                or light["intensity_lumens"] is None
            ):
                continue
            z_value = _nearest_surface_value(
                self.x_grid,
                self.y_grid,
                self.z_grid,
                light["x"],
                light["y"],
            )
            z_value = self._clip_z_for_display(z_value)
            self.ax.scatter(
                [light["x"]],
                [light["y"]],
                [z_value],
                s=45,
                marker="o",
                label=f"L{light_idx}: {light['intensity_lumens']:.0f} lm",
            )

        for fill_idx, (amplitude, mu_x, mu_y, sigma) in enumerate(
            self.fill_terms,
            start=1,
        ):
            z_value = _nearest_surface_value(
                self.x_grid,
                self.y_grid,
                self.z_grid,
                mu_x,
                mu_y,
            )
            z_value = self._clip_z_for_display(z_value)
            self.ax.scatter(
                [mu_x],
                [mu_y],
                [z_value],
                c="magenta",
                s=60,
                marker="^",
                label=f"fill {fill_idx}: A={amplitude:.2f}, sigma={sigma:.2f}",
            )

        self.trajectory_line, = self.ax.plot(
            [],
            [],
            [],
            c="red",
            linewidth=2.0,
            label="robot path",
        )
        self.trajectory_dot = self.ax.scatter(
            [],
            [],
            [],
            c="red",
            s=55,
            marker="o",
            depthshade=False,
            label="robot",
        )
        self._update_trajectory_artists()

        self.ax.set_title(self.args.title)
        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.set_zlabel("cost")
        self.ax.set_zlim(self.contour_offset, z_axis_max)
        self.ax.view_init(elev=self.args.elev, azim=self.args.azim)
        self.ax.legend(loc="upper right")

        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(
                surface,
                ax=self.ax,
                shrink=0.65,
                pad=0.1,
                label="cost",
            )
        else:
            self.colorbar.update_normal(surface)

        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

    def _plot_limits(self):
        z_min = float(np.nanmin(self.z_grid))
        z_max = float(np.nanmax(self.z_grid))

        if self.args.z_scale_mode == "base":
            return (
                self.base_z_min,
                self.base_z_max,
                self.base_z_min,
                self.base_z_max,
            )

        return z_min, z_max, z_min, z_max

    def _clip_z_for_display(self, z_value):
        if self.args.z_scale_mode != "base":
            return z_value

        return float(np.clip(z_value, self.base_z_min, self.base_z_max))

    def _display_z_grid(self, z_axis_min, z_axis_max):
        if self.args.z_scale_mode != "base":
            return self.z_grid

        return np.clip(self.z_grid, z_axis_min, z_axis_max)

    def add_trajectory_point(self, x_pos, y_pos):
        self.trajectory.append((float(x_pos), float(y_pos)))
        if len(self.trajectory) > self.args.trajectory_max_points:
            self.trajectory = self.trajectory[-self.args.trajectory_max_points:]
        self._update_trajectory_artists()

    def add_fill_term(self, amplitude, mu_x, mu_y, sigma):
        sigma = max(float(sigma), 1e-9)
        self.fill_terms.append((
            float(amplitude),
            float(mu_x),
            float(mu_y),
            sigma,
        ))
        self._recompute_modified_surface()
        self.draw()

    def _recompute_modified_surface(self):
        self.z_grid = np.array(self.base_z_grid, copy=True)
        for amplitude, mu_x, mu_y, sigma in self.fill_terms:
            dx_grid = self.x_grid - mu_x
            dy_grid = self.y_grid - mu_y
            radius_sq_grid = dx_grid*dx_grid + dy_grid*dy_grid
            self.z_grid += amplitude * np.exp(
                -radius_sq_grid / (2.0 * sigma * sigma)
            )

    def _update_trajectory_artists(self):
        if self.trajectory_line is None or self.trajectory_dot is None:
            return

        if not self.trajectory:
            self.trajectory_line.set_data([], [])
            self.trajectory_line.set_3d_properties([])
            self.trajectory_dot._offsets3d = ([], [], [])
            return

        x_values = [point[0] for point in self.trajectory]
        y_values = [point[1] for point in self.trajectory]
        z_values = [self.contour_offset for _ in self.trajectory]
        self.trajectory_line.set_data(x_values, y_values)
        self.trajectory_line.set_3d_properties(z_values)
        self.trajectory_dot._offsets3d = (
            [x_values[-1]],
            [y_values[-1]],
            [self.contour_offset],
        )
        self.fig.canvas.draw_idle()


class LiveCostSurfaceNode(Node):
    """Subscribe to trajectory and fill topics for live plot updates."""

    def __init__(self, plot, args):
        super().__init__("cost_surface_plotter")
        self.plot = plot
        self.args = args
        self.last_trajectory_update_sec = None
        self.create_subscription(
            Odometry,
            args.odom_topic,
            self.odom_callback,
            10,
        )
        self.create_subscription(
            StampedFloat64MultiArray,
            args.fill_topic,
            self.fill_callback,
            10,
        )
        self.get_logger().info(
            "Live cost surface plotter subscribed to "
            f"{args.odom_topic} and {args.fill_topic}."
        )

    def odom_callback(self, msg):
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        if (
            self.last_trajectory_update_sec is not None
            and now_sec - self.last_trajectory_update_sec < self.args.trajectory_period
        ):
            return

        self.last_trajectory_update_sec = now_sec
        self.plot.add_trajectory_point(
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
        )

    def fill_callback(self, msg):
        data = list(msg.data)
        if len(data) != 4:
            self.get_logger().warn(
                f"Ignoring fill message with len={len(data)}; expected 4."
            )
            return

        amplitude, mu_x, mu_y, sigma = map(float, data)
        if not all(math.isfinite(value) for value in (amplitude, mu_x, mu_y, sigma)):
            self.get_logger().warn("Ignoring non-finite fill message.")
            return

        self.plot.add_fill_term(amplitude, mu_x, mu_y, sigma)
        self.get_logger().info(
            f"Updated surface with fill: A={amplitude:.3f}, "
            f"mu=({mu_x:.3f},{mu_y:.3f}), sigma={sigma:.3f}."
        )


def _run_live_plot(x_grid, y_grid, z_grid, args, lights):
    plot = CostSurfacePlot(x_grid, y_grid, z_grid, args, lights)
    plot.draw()
    plt.show(block=False)
    plt.pause(0.001)

    rclpy.init(args=None)
    node = LiveCostSurfaceNode(plot, args)

    try:
        while rclpy.ok() and plt.fignum_exists(plot.fig.number):
            rclpy.spin_once(node, timeout_sec=0.01)
            plt.pause(max(0.001, 1.0 / args.refresh_hz))
    finally:
        saved_path = _save_snapshot(plot, args, "final")
        if saved_path:
            node.get_logger().info(
                f"Saved final cost surface snapshot to {saved_path}"
            )
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def _nearest_surface_value(x_grid, y_grid, z_grid, x_pos, y_pos):
    distance_sq = (x_grid - x_pos)**2 + (y_grid - y_pos)**2
    idx = np.unravel_index(np.nanargmin(distance_sq), distance_sq.shape)

    return float(z_grid[idx])


def build_parser():
    parser = argparse.ArgumentParser(
        description="Plot a 3D topographic surface for a ros_esc cost JSON.",
    )
    parser.add_argument("config", help="Cost-function JSON filepath.")
    parser.add_argument("--x-min", type=float, default=0.0)
    parser.add_argument("--x-max", type=float, default=12.0)
    parser.add_argument("--y-min", type=float, default=0.0)
    parser.add_argument("--y-max", type=float, default=12.0)
    parser.add_argument("--resolution", type=int, default=80)
    parser.add_argument(
        "--orientation-mode",
        choices=("average", "fixed", "min", "max"),
        default="average",
        help="How to reduce orientation-dependent costs into one XY surface.",
    )
    parser.add_argument("--orientation-samples", type=int, default=24)
    parser.add_argument("--title", default="Cost Surface")
    parser.add_argument("--cmap", default="viridis")
    parser.add_argument("--contours", type=int, default=24)
    parser.add_argument(
        "--z-scale-mode",
        choices=("base", "auto"),
        default="base",
        help=(
            "base locks the z/color scale to the original surface; "
            "auto rescales after fills."
        ),
    )
    parser.add_argument(
        "--show-base-wireframe",
        nargs="?",
        const=True,
        default=True,
        type=_normalize_bool,
        help="Overlay the original surface as a gray wireframe after fills.",
    )
    parser.add_argument("--elev", type=float, default=35.0)
    parser.add_argument("--azim", type=float, default=-45.0)
    parser.add_argument("--output", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument(
        "--output-latest-test-dir",
        nargs="?",
        const=True,
        default=False,
        type=_normalize_bool,
        help="Save into the newest Test_* folder under --output-dir.",
    )
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument(
        "--live",
        nargs="?",
        const=True,
        default=False,
        type=_normalize_bool,
        help="Subscribe to ROS topics and update robot path/fills live.",
    )
    parser.add_argument("--odom-topic", default="/odom")
    parser.add_argument("--fill-topic", default="/cost_bias")
    parser.add_argument("--refresh-hz", type=float, default=10.0)
    parser.add_argument(
        "--trajectory-period",
        type=float,
        default=0.2,
        help="Minimum seconds between plotted odometry points.",
    )
    parser.add_argument("--trajectory-max-points", type=int, default=2000)
    parser.add_argument(
        "--light_source_count",
        "--number_of_lights",
        dest="light_source_count",
        type=int,
        default=None,
    )
    for light_idx in range(1, 6):
        parser.add_argument(f"--light_source_{light_idx}_x", type=float, default=None)
        parser.add_argument(f"--light_source_{light_idx}_y", type=float, default=None)
        parser.add_argument(
            f"--light_source_{light_idx}_intensity_lumens",
            type=float,
            default=None,
        )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    args.resolution = max(2, int(args.resolution))
    args.orientation_samples = max(1, int(args.orientation_samples))
    args.refresh_hz = max(0.5, float(args.refresh_hz))
    args.trajectory_period = max(0.0, float(args.trajectory_period))
    args.trajectory_max_points = max(1, int(args.trajectory_max_points))
    args.no_show = bool(args.no_show or _normalize_bool(os.environ.get("COST_SURFACE_NO_SHOW", "False")))

    cost_function = _load_cost_function(args.config, args)

    x_values = np.linspace(args.x_min, args.x_max, args.resolution)
    y_values = np.linspace(args.y_min, args.y_max, args.resolution)
    x_grid, y_grid = np.meshgrid(x_values, y_values)
    angles = np.linspace(0.0, 2.0*np.pi, args.orientation_samples, endpoint=False)

    z_grid = np.empty_like(x_grid, dtype=float)
    for row_idx in range(args.resolution):
        for col_idx in range(args.resolution):
            z_grid[row_idx, col_idx] = _evaluate_cost(
                cost_function,
                x_grid[row_idx, col_idx],
                y_grid[row_idx, col_idx],
                angles,
                args.orientation_mode,
            )

    lights = _parse_light_sources(args)

    if args.live and not args.no_show:
        _run_live_plot(x_grid, y_grid, z_grid, args, lights)
    else:
        _plot_surface(x_grid, y_grid, z_grid, args, lights)


if __name__ == "__main__":
    main()
