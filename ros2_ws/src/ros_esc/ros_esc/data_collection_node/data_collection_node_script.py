#!/usr/bin/env python3
"""Optional Matplotlib display; this process never records or commands motion."""

import argparse
import os
import sys
import threading


def display_available(environ=None):
    """Do not start a GUI on a headless host."""
    environ = os.environ if environ is None else environ
    return bool(environ.get('DISPLAY') or environ.get('WAYLAND_DISPLAY'))


def main(args=None):
    """Keep the familiar position/cost/trajectory display independently optional."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('2D', '3D'), default='2D')
    parser.add_argument('--odom-topic', default='/odom')
    parser.add_argument('--cost-topic', default='/turtlebot3/cost_value_chatter')
    from rclpy.utilities import remove_ros_args
    argv = sys.argv if args is None else ['live_plot_node', *args]
    options = parser.parse_args(remove_ros_args(args=argv)[1:])
    if not display_available():
        print('live_plot_node: no display; plotting skipped', file=sys.stderr)
        return 0

    node = executor = thread = None
    stop = threading.Event()
    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        import rclpy
        from rclpy.executors import SingleThreadedExecutor
        from rclpy.node import Node
        from nav_msgs.msg import Odometry
        from ros_esc_interfaces.msg import StampedFloat64MultiArray
        from .live_plot_animation import (
            append_cost, append_position, initialize_animation, update_plot,
        )

        rclpy.init(args=args)
        node = Node('live_plot_node')
        figure, data = initialize_animation(options.mode)

        def odometry(message):
            stamp = message.header.stamp
            position = message.pose.pose.position
            append_position(data, stamp.sec + stamp.nanosec * 1e-9,
                            position.x, position.y, position.z)

        def cost(message):
            append_cost(data, message.timestamp, message.data)

        node.create_subscription(Odometry, options.odom_topic, odometry, 10)
        node.create_subscription(StampedFloat64MultiArray, options.cost_topic, cost, 10)
        executor = SingleThreadedExecutor()
        executor.add_node(node)

        def spin():
            try:
                while not stop.is_set() and rclpy.ok():
                    executor.spin_once(timeout_sec=0.1)
            except Exception as error:  # A display failure has no control authority.
                print(f'live_plot_node: subscription stopped: {error}', file=sys.stderr)
            finally:
                stop.set()

        def animate(frame):
            if stop.is_set():
                plt.close(figure)
            else:
                update_plot(frame, data)

        animation = FuncAnimation(figure, animate, interval=100, cache_frame_data=False)
        thread = threading.Thread(target=spin, name='live_plot_subscriptions', daemon=True)
        thread.start()
        plt.show()
        del animation
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(f'live_plot_node: plotting unavailable: {error}', file=sys.stderr)
    finally:
        stop.set()
        if thread is not None:
            thread.join(timeout=1.0)
        if executor is not None:
            executor.shutdown(timeout_sec=1.0)
        if node is not None:
            node.destroy_node()
        if 'rclpy' in locals():
            rclpy.try_shutdown()
        if 'plt' in locals():
            plt.close('all')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
