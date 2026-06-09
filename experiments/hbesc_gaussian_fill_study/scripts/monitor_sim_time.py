#!/usr/bin/env python3

import argparse
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor /clock until a sim-time duration elapses.")
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--wall-timeout", type=float, default=180.0)
    args = parser.parse_args()

    try:
        import rclpy
        from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
        from rosgraph_msgs.msg import Clock
    except Exception as exc:  # pragma: no cover - depends on ROS environment
        print(f"Unable to import ROS clock dependencies: {exc}", file=sys.stderr)
        return 3

    rclpy.init()
    node = rclpy.create_node("hbesc_phase2_sim_time_monitor")
    state = {"first": None, "latest": None}

    def callback(msg: Clock) -> None:
        current = float(msg.clock.sec) + float(msg.clock.nanosec) * 1e-9
        if state["first"] is None:
            state["first"] = current
        state["latest"] = current

    clock_qos = QoSProfile(depth=1)
    clock_qos.reliability = ReliabilityPolicy.BEST_EFFORT
    clock_qos.durability = DurabilityPolicy.VOLATILE
    node.create_subscription(Clock, "/clock", callback, clock_qos)

    wall_start = time.monotonic()
    exit_code = 2
    try:
        while (time.monotonic() - wall_start) < args.wall_timeout:
            rclpy.spin_once(node, timeout_sec=0.5)
            if state["first"] is None or state["latest"] is None:
                continue
            elapsed = state["latest"] - state["first"]
            print(f"sim_time_elapsed={elapsed:.3f}", flush=True)
            if elapsed >= args.duration:
                exit_code = 0
                break
    finally:
        node.destroy_node()
        rclpy.shutdown()

    if exit_code == 2:
        print(
            f"Timed out after {args.wall_timeout:.1f}s wall time before {args.duration:.1f}s sim time.",
            file=sys.stderr,
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
