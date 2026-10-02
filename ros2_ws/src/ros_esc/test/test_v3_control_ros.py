"""Finite local ROS graph checks; no Gazebo, hardware or recorder is started."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest
import rclpy
from rclpy.context import Context
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import SensorObservation

from ros_esc.gesc_v3.node import V3Controller
from ros_esc.gesc_v3.observation_node import set_stamp


class Driver(Node):
    def __init__(self, context):
        super().__init__('v3_test_driver', context=context)
        self.pose = self.create_publisher(Odometry, '/odom', 10)
        self.sample = self.create_publisher(SensorObservation, '/gesc/observation', 10)
        self.commands = []
        self.create_subscription(Twist, '/cmd_vel',
            lambda message: self.commands.append((time.monotonic(), message.linear.x,
                                                   message.angular.z)), 100)
        self.sequence = 0

    def publish_inputs(self, *, cost=True, duplicate=None):
        stamp = self.get_clock().now().nanoseconds*1e-9
        pose = Odometry()
        set_stamp(pose.header.stamp, stamp)
        pose.header.frame_id = 'odom'
        pose.pose.pose.orientation.w = 1.
        self.pose.publish(pose)
        message = None
        if cost:
            if duplicate is not None:
                message = duplicate
            else:
                message = SensorObservation()
                set_stamp(message.stamp, stamp)
                set_stamp(message.receipt_stamp, stamp)
                self.sequence += 1
                message.sequence = self.sequence
                message.source_instance = 'isolated_test_acquisition'
                message.timestamp_basis = message.RECEIPT_TIME
                message.acquisition_uncertainty_sec = float('nan')
                message.frame_id = 'odom'
                # A changing signal supplies a real direction after startup
                # priming; a constant level correctly has no initial gradient.
                message.raw_cost = -2. - .01*self.sequence
                message.phase_rad = 0.
                message.sensor_x_m = .18
                message.valid = True
            self.sample.publish(message)
        return message


@pytest.fixture
def graph():
    # Localhost + a test-specific DDS domain isolates /cmd_vel from real robots.
    assert os.environ.get('ROS_LOCALHOST_ONLY') == '1'
    context = Context()
    rclpy.init(context=context, domain_id=189)
    driver = Driver(context)
    executor = SingleThreadedExecutor(context=context)
    executor.add_node(driver)
    try:
        yield context, driver, executor
    finally:
        executor.remove_node(driver)
        driver.destroy_node()
        executor.shutdown()
        context.try_shutdown()


def run_for(driver, executor, duration, *, cost=True, duplicate=None):
    deadline = time.monotonic()+duration
    next_sample = 0.
    last = None
    while time.monotonic() < deadline:
        now = time.monotonic()
        last = driver.publish_inputs(cost=cost and now >= next_sample, duplicate=duplicate) or last
        if now >= next_sample:
            next_sample = now+.2
        executor.spin_once(timeout_sec=.005)
        time.sleep(.005)
    return last


def test_optional_heavy_worker_and_input_expiry_recovery(graph):
    context, driver, executor = graph
    owner = V3Controller(context=context, parameter_overrides=[
        Parameter('environment', value='physical'), Parameter('use_sim_time', value=False)])
    executor.add_node(owner)
    try:
        last = run_for(driver, executor, 1.2)
        assert any(vx != 0 for _, vx, _ in driver.commands)
        assert owner.core.availability == 'ACTIVE'
        assert owner.worker.ready
        assert owner.worker.submit(('test_heavy_optional_work',), time.sleep, (2.,), timeout=3.)
        begin = len(driver.commands)
        run_for(driver, executor, .8)
        moving = driver.commands[begin:]
        assert len(moving) >= 8 and all(vx != 0 for _, vx, _ in moving)
        assert max(b[0]-a[0] for a, b in zip(moving, moving[1:])) < .2
        # Even repeatedly delivered old messages cannot renew source age.
        run_for(driver, executor, .9, duplicate=last)
        assert driver.commands[-1][1:] == (0., 0.)
        assert owner.core.availability == 'WAITING_INPUT'
        run_for(driver, executor, .5)
        assert driver.commands[-1][1] != 0
        assert owner.core.availability == 'ACTIVE'
        owner.stop()
        for _ in range(10):
            executor.spin_once(timeout_sec=.01)
        assert driver.commands[-1][1:] == (0., 0.)
        assert owner.core.availability == 'STOPPED'
        assert owner.count_publishers('/cmd_vel') == 1
    finally:
        owner.stop()
        executor.remove_node(owner)
        owner.destroy_node()


def test_process_sigint_publishes_final_zero(graph, tmp_path):
    from ament_index_python.packages import get_package_prefix
    _, driver, executor = graph
    environment = dict(os.environ, ROS_DOMAIN_ID='189', ROS_LOCALHOST_ONLY='1')
    log = (tmp_path/'controller.log').open('w')
    executable = Path(get_package_prefix('ros_esc'))/'lib/ros_esc/controller_node'
    process = subprocess.Popen([str(executable), '--v3',
        '--ros-args', '-p', 'environment:=physical', '-p', 'use_sim_time:=false'],
        env=environment, stdout=log, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic()+8.
        while not any(vx != 0 for _, vx, _ in driver.commands) and time.monotonic() < deadline:
            assert process.poll() is None
            run_for(driver, executor, .2)
        assert any(vx != 0 for _, vx, _ in driver.commands)
        process.send_signal(signal.SIGINT)
        deadline = time.monotonic()+3.
        while process.poll() is None and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=.02)
        assert process.wait(timeout=1.) == 0
        for _ in range(10):
            executor.spin_once(timeout_sec=.01)
        assert driver.commands[-1][1:] == (0., 0.)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=2.)
        log.close()


def test_repeated_sigint_during_real_process_cleanup_keeps_final_zero(graph, tmp_path):
    _, driver, executor = graph
    environment = dict(os.environ, ROS_DOMAIN_ID='189', ROS_LOCALHOST_ONLY='1')
    marker = tmp_path/'worker_cleanup.txt'
    log_path = tmp_path/'repeated_signals_controller.log'
    # Deliberately expose the real main() cleanup window. The actual numerical
    # worker still starts and closes; only its close latency is extended.
    script = '''
import sys
import time
from pathlib import Path
from ros_esc.gesc_v3 import node as runtime

class SlowCloseWorker(runtime.NumericalWorker):
    def close(self):
        marker = Path(sys.argv[1])
        marker.write_text('closing')
        time.sleep(.4)
        super().close()
        marker.write_text('closed')

if __name__ == '__main__':
    runtime.NumericalWorker = SlowCloseWorker
    runtime.main(args=['--ros-args', '-p', 'environment:=physical',
                       '-p', 'use_sim_time:=false'])
'''
    with log_path.open('w') as log:
        process = subprocess.Popen([sys.executable, '-c', script, str(marker)],
            env=environment, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic()+8.
            while not any(vx != 0 for _, vx, _ in driver.commands) and time.monotonic() < deadline:
                assert process.poll() is None
                run_for(driver, executor, .2)
            assert any(vx != 0 for _, vx, _ in driver.commands)
            process.send_signal(signal.SIGINT)
            deadline = time.monotonic()+2.
            while not marker.exists() and time.monotonic() < deadline:
                assert process.poll() is None
                executor.spin_once(timeout_sec=.01)
            assert marker.read_text() == 'closing'
            process.send_signal(signal.SIGINT)
            time.sleep(.02)
            assert process.poll() is None
            process.send_signal(signal.SIGINT)
            deadline = time.monotonic()+3.
            while process.poll() is None and time.monotonic() < deadline:
                executor.spin_once(timeout_sec=.02)
            assert process.wait(timeout=1.) == 0
            assert marker.read_text() == 'closed'
            for _ in range(10):
                executor.spin_once(timeout_sec=.01)
            assert driver.commands[-1][1:] == (0., 0.)
            assert 'KeyboardInterrupt' not in log_path.read_text()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2.)
