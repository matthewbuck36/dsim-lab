"""A's real fit does not import the Arm B adapter or require its new IDL."""

import builtins
import os
from types import SimpleNamespace

import rclpy
from rclpy.time import Time
import ros_esc_interfaces.msg as messages

from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from test_q5_stationary_gaussian_contract import seed_support


def test_actual_legacy_fit_has_no_stationary_request_interface_dependency(monkeypatch):
    available = hasattr(messages, 'StationaryFillRequest')
    if os.environ.get('Q5_REQUIRE_OLD_INTERFACES') == '1':
        assert not available, 'This command must use the original Q2 interface overlay only'
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == 'ros_esc.gaussian_fill_node.stationary_fill':
            raise AssertionError('Legacy fit imported the selected-only Arm B adapter')
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', guarded_import)
    rclpy.init(args=['--ros-args', '-p', 'algorithm_profile:=robust_gaussian_v1',
                    '-p', 'convergence_metric_mode:=pde_mean_v1',
                    '-p', 'continuous_search_mode:=stationary_v1', '-p', 'use_sim_time:=true'])
    node = None
    try:
        node = GaussianFill()
        now = 1_025_000_000_000
        node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now))
        seed_support(node, now)
        request = messages.StampedFloat64MultiArray(
            header='ROBUST_FILL_CREATE', timestamp=25., data=[0.] * 8)
        node.trigger_cb(request)
        assert node.stationary_fill is None and node.v2_fill is None
        assert node.fill_registry.generation == 1
        active, = node.fill_registry.active_clusters
        assert active.active_fill.source_timestamp == 25.
        assert active.active_fill.amplitude > 0.
        print('Q5_LEGACY_INTERFACE new_request_type_available=' + str(available)
              + ' real_registry_generation=1 correlation_sec=25.0')
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()
