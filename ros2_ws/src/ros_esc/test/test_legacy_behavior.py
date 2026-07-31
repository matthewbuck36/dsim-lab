"""Focused numerical-equivalence tests for opt-in Phase 01 diagnostics."""

import math
from pathlib import Path
import sys
import threading
import time

import numpy as np
import pytest
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from ros_esc.controller_node import controller_node_script
from ros_esc.controller_node.controller_node_script import CustomController
from ros_esc.controller_node.controller_objects.turtlebot_vehicle import (
    Directional_Controller,
)
from ros_esc.cost_function_node import cost_function_node_script
from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.cost_function_node.cost_function_objects.cost_function_objects import (
    Multi_Light_Source_Cost,
    Photoresistor_Interpolated_Map,
    Position_Based_Sympy_Expression,
)
from ros_esc.gaussian_fill_node import gaussian_fill_script
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from ros_esc.gaussian_fill_node.basin_estimator import CostSnapshot, PoseSnapshot
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.pde_cost_history_node import pde_cost_history_script
from ros_esc.rotate_frame_node import rotate_frame_node_script
from ros_esc.supervisor_node import supervisor_node_script
from ros_esc.supervisor_node.state_machine import (
    CANDIDATE_INFORMED_FILL_HEADER,
    CandidateCostSummary,
    encode_candidate_informed_fill_payload,
)
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill as GaussianFillMessage,
    StampedFloat64MultiArray,
)
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
FILTER_CONFIG = (
    REPOSITORY_ROOT
    / "ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files"
    / "turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
)
CONTROLLER_CONFIG = (
    REPOSITORY_ROOT
    / "ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files"
    / "turtlebot_vehicle/gradient_methods"
    / "gesc_controller_full_rotation_voltage.json"
)
DIAGNOSTIC_ACTIVATION = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
    'phase08_1_diagnostic_activation.yaml'
)


class Recorder:
    """Minimal publisher replacement that retains published messages."""

    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


def test_supervisor_owned_assist_arbitration_is_default_off_and_scoped():
    controller = object.__new__(CustomController)
    state = AlgorithmState()
    state.state = AlgorithmState.STATE_ESCAPE_ASSIST
    controller.latest_algorithm_state = state
    gesc = np.array([0.08, 0.0, 0.0, 0.0, 0.0, 7.095])
    supervisor = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.398])

    controller.open_field_escape_supervisor_owned_assist_enabled = False
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(gesc + supervisor)

    controller.open_field_escape_supervisor_owned_assist_enabled = True
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(supervisor)
    assert controller._authorized_combination(
        gesc,
        np.zeros(6),
    ) == pytest.approx(np.zeros(6))

    state.state = AlgorithmState.STATE_ESCAPE_REPULSE
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(gesc + supervisor)
    state.state = AlgorithmState.STATE_SEARCH
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(gesc)
    state.state = AlgorithmState.STATE_RECENTER
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(supervisor)
    state.state = AlgorithmState.STATE_GOAL_HOLD
    assert controller._authorized_combination(
        gesc,
        supervisor,
    ) == pytest.approx(np.zeros(6))


def test_recording_interlock_disabled_is_a_noop():
    controller = object.__new__(CustomController)
    controller.recording_ready_required = False

    assert controller._recording_fault_reason() is None


def test_recording_interlock_false_missing_and_stale_force_zero(monkeypatch):
    controller = object.__new__(CustomController)
    controller.recording_ready_required = True
    controller.recording_ready_stale_sec = 0.5
    controller.recording_ready = False
    controller.recording_ready_receipt_monotonic = None
    published = []
    controller._publish_zero = lambda reason, report_fault: published.append(reason)

    assert "missing" in controller._recording_fault_reason()
    message = Bool()
    message.data = False
    monkeypatch.setattr(controller_node_script.time, "monotonic", lambda: 10.0)
    controller.recording_ready_callback(message)
    assert published == ["recording readiness is false"]
    assert controller._recording_fault_reason() == "recording readiness is false"

    message.data = True
    controller.recording_ready_callback(message)
    assert controller._recording_fault_reason() is None
    monkeypatch.setattr(controller_node_script.time, "monotonic", lambda: 10.6)
    assert "stale" in controller._recording_fault_reason()


def test_recording_watchdog_zero_does_not_emit_latching_failsafe():
    controller = object.__new__(CustomController)
    controller.robust_profile = False
    controller.latest_algorithm_state = None
    controller._recording_fault_reason = lambda: "recording readiness is false"
    zeros = []
    controller._publish_zero = lambda reason, report_fault: zeros.append(
        (reason, report_fault)
    )
    controller._emit_local_fault_once = lambda reason: pytest.fail(
        f"recording gate emitted a latching event: {reason}"
    )

    controller.watchdog_callback()

    assert zeros == [("recording readiness is false", False)]


def test_robust_startup_waits_once_then_latches_strict_freshness():
    def controller_at(now_sec):
        controller = object.__new__(CustomController)
        controller.robust_profile = True
        controller.robust_controller_compatible = True
        controller.robust_inputs_ready = False
        controller.controller_started_sec = 100.0
        controller.startup_timeout_sec = 5.0
        controller.supervisor_state_stale_sec = 0.5
        controller.supervisor_command_stale_sec = 0.5
        controller.stale_pose_sec = 0.5
        controller.stale_filter_sec = 0.5
        controller._now_sec = lambda: now_sec[0]
        controller.input_value = np.zeros(2)
        controller.state_value = np.zeros(6)
        controller.supervisor_command = np.zeros(6)
        state = AlgorithmState()
        state.algorithm_profile = 'robust_gaussian_v1'
        state.state = AlgorithmState.STATE_SEARCH
        state.state_valid = True
        state.weights_valid = True
        controller.latest_algorithm_state = state
        controller._recording_fault_reason = lambda: None
        return controller

    now_sec = [101.0]
    controller = controller_at(now_sec)
    controller.supervisor_state_receipt_sec = now_sec[0]
    controller.supervisor_command_receipt_sec = now_sec[0]
    controller.input_receipt_sec = now_sec[0]
    controller.pose_receipt_sec = 100.0
    zero_reasons = []
    fault_reasons = []
    controller._publish_zero = (
        lambda reason, report_fault: zero_reasons.append(
            (reason, report_fault)
        )
    )
    controller._emit_local_fault_once = fault_reasons.append

    assert controller._robust_fault_reason() == 'startup waiting for pose'
    controller.watchdog_callback()
    assert zero_reasons == [('startup waiting for pose', False)]
    assert fault_reasons == []
    assert controller.robust_inputs_ready is False

    now_sec[0] = 101.1
    controller.supervisor_state_receipt_sec = now_sec[0]
    controller.supervisor_command_receipt_sec = now_sec[0]
    controller.pose_receipt_sec = now_sec[0]
    controller.input_receipt_sec = now_sec[0]
    assert controller._robust_fault_reason() is None
    assert controller.robust_inputs_ready is True

    now_sec[0] = 101.8
    controller.supervisor_state_receipt_sec = now_sec[0]
    controller.supervisor_command_receipt_sec = now_sec[0]
    controller.input_receipt_sec = now_sec[0]
    controller.watchdog_callback()
    assert fault_reasons == ['pose missing or stale']
    assert zero_reasons[-1] == ('pose missing or stale', False)

    never_ready_now = [106.0]
    never_ready = controller_at(never_ready_now)
    never_ready.supervisor_state_receipt_sec = never_ready_now[0]
    never_ready.supervisor_command_receipt_sec = never_ready_now[0]
    never_ready.input_receipt_sec = never_ready_now[0]
    never_ready.pose_receipt_sec = 100.0
    assert never_ready._robust_fault_reason() == 'pose missing or stale'
    assert never_ready.robust_inputs_ready is False


@pytest.mark.parametrize(
    ("node_module", "node_factory_name"),
    [
        (controller_node_script, "CustomController"),
        (cost_function_node_script, "CostFunction"),
        (supervisor_node_script, "SupervisorNode"),
        (pde_cost_history_script, "PDECostHistory"),
        (rotate_frame_node_script, "RotateFrame"),
    ],
)
def test_sigint_cleanup_publishes_zero_before_context_shutdown(
    monkeypatch,
    node_module,
    node_factory_name,
):
    events = []

    class FakeNode:
        def destroy_node(self):
            assert node_module.rclpy.ok()
            events.append("zero_then_destroy")

    class FakeExecutor:
        def __init__(self):
            events.append("executor_created")

        def add_node(self, node):
            assert isinstance(node, FakeNode)
            events.append("node_added")

        def spin_once(self, timeout_sec):
            assert timeout_sec == 0.05
            events.append("spin_once")
            raise KeyboardInterrupt

        def remove_node(self, node):
            assert isinstance(node, FakeNode)
            events.append("node_removed")

        def shutdown(self):
            events.append("executor_shutdown")

    def fake_init(*, args, signal_handler_options):
        assert args == ["--test"]
        assert signal_handler_options == node_module.SignalHandlerOptions.NO
        events.append("context_initialized_without_signal_handlers")

    monkeypatch.setattr(node_module.rclpy, "init", fake_init)
    monkeypatch.setattr(node_module.rclpy, "ok", lambda: True)
    monkeypatch.setattr(
        node_module.rclpy,
        "try_shutdown",
        lambda: events.append("context_shutdown"),
    )
    monkeypatch.setattr(node_module, "SingleThreadedExecutor", FakeExecutor)
    monkeypatch.setattr(node_module, node_factory_name, FakeNode)

    node_module.main(args=["--test"])

    assert events == [
        "context_initialized_without_signal_handlers",
        "executor_created",
        "node_added",
        "spin_once",
        "node_removed",
        "executor_shutdown",
        "zero_then_destroy",
        "context_shutdown",
    ]


def _run_modified_cost(monkeypatch, observability, bias_all=True):
    argv = ["modified_cost_node", "/test/raw", "/test/fill", "/test/out"]
    monkeypatch.setattr(sys, "argv", argv)
    ros_args = [
        "--ros-args",
        "-p",
        f"enable_observability:={'true' if observability else 'false'}",
        "-p",
        f"bias_all_channels:={'true' if bias_all else 'false'}",
    ]
    rclpy.init(args=ros_args)
    node = ModifiedCost2D()
    try:
        node.pub = Recorder()
        if observability:
            node.cost_breakdown_publisher = Recorder()
            node.algorithm_state_publisher = Recorder()
            node.algorithm_event_publisher = Recorder()
        node.xy = np.array([0.0, 0.0])
        node.sensor_xy = np.array([[0.0, 0.0], [1.0, 0.0]])
        node.terms = [(0.7, 0.0, 0.0, 0.5)]
        node.affine_terms = []

        source = StampedFloat64MultiArray()
        source.header = "Cost Values"
        source.timestamp = 9.75
        source.data = [-1.0, -2.0]
        node.cost_cb(source)

        legacy = node.pub.messages[-1]
        breakdown = (
            node.cost_breakdown_publisher.messages[-1]
            if observability
            else None
        )
        return legacy, breakdown
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_fill_design_services_clock_and_stamps_at_emission(monkeypatch):
    """Keep /clock live while the bounded fill request callback is active."""
    monkeypatch.setattr(sys, 'argv', ['gaussian_fill_node'])
    rclpy.init(
        args=[
            '--ros-args',
            '-p',
            'algorithm_profile:=robust_gaussian_v1',
            '-p',
            'minimum_valid_samples:=20',
            '-p',
            'maximum_position_speed_mps:=100.0',
            '-p',
            'amplitude_max:=10.0',
            '-p',
            'sigma_ceiling_m:=2.0',
        ]
    )
    node = GaussianFill()
    peer = Node('gaussian_fill_clock_peer')
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    executor.add_node(peer)
    events = []
    peer.create_subscription(
        AlgorithmEvent,
        '/gesc_gaussian/algorithm_events',
        events.append,
        10,
    )
    request_publisher = peer.create_publisher(
        StampedFloat64MultiArray,
        '/gesc_gaussian/fill_requests',
        10,
    )
    clock_publisher = peer.create_publisher(
        Clock,
        '/clock',
        QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
        ),
    )
    design_entered = threading.Event()
    release_design = threading.Event()
    original_synchronize = gaussian_fill_script.synchronize_samples

    def blocked_synchronize(*args, **kwargs):
        design_entered.set()
        assert release_design.wait(timeout=3.0)
        return original_synchronize(*args, **kwargs)

    monkeypatch.setattr(
        gaussian_fill_script,
        'synchronize_samples',
        blocked_synchronize,
    )
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    def wait_for(predicate, timeout_sec=3.0):
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.01)
        return False

    def advance_clock(seconds):
        message = Clock()
        message.clock.sec = int(seconds)
        message.clock.nanosec = int(
            round((seconds - int(seconds)) * 1_000_000_000)
        )
        deadline = time.monotonic() + 3.0
        expected = int(round(seconds * 1_000_000_000))
        while time.monotonic() < deadline:
            clock_publisher.publish(message)
            if node.get_clock().now().nanoseconds == expected:
                return True
            time.sleep(0.01)
        return False

    try:
        assert wait_for(
            lambda: (
                request_publisher.get_subscription_count() == 1
                and clock_publisher.get_subscription_count() >= 1
                and node.algorithm_event_publisher.get_subscription_count()
                >= 1
            )
        )
        assert advance_clock(1.0)
        for index in range(60):
            stamp = 0.41 + index * 0.01
            angle = index * 2.0 * np.pi / 20.0
            radius = 0.30 - 0.003 * index
            x_value = radius * np.cos(angle)
            y_value = radius * np.sin(angle)
            cost = 0.05 * (x_value ** 2 + y_value ** 2)
            node.pose_snapshots.append(
                PoseSnapshot(stamp, x_value, y_value, angle, True)
            )
            node.cost_snapshots.append(
                CostSnapshot(
                    stamp,
                    float('nan'),
                    False,
                    cost,
                    0.2,
                    True,
                    AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                    True,
                )
            )
        request = StampedFloat64MultiArray()
        request.header = 'ROBUST_FILL_CREATE'
        request.timestamp = 42.0
        request.data = [0.0] * 8
        request_publisher.publish(request)
        assert design_entered.wait(timeout=3.0)

        assert advance_clock(2.0)
        release_design.set()
        assert wait_for(
            lambda: any(
                20 <= event.event_type <= 26
                for event in events
            )
        )
        fill_event = next(
            event
            for event in events
            if 20 <= event.event_type <= 26
        )
        assert fill_event.stamp.sec == 2
        assert fill_event.stamp.nanosec == 0
        assert fill_event.source_timestamp == 42.0
        assert fill_event.source_timestamp_valid is True
    finally:
        release_design.set()
        executor.shutdown()
        spin_thread.join(timeout=1.0)
        assert not spin_thread.is_alive()
        executor.remove_node(peer)
        executor.remove_node(node)
        peer.destroy_node()
        node.destroy_node()
        rclpy.shutdown()


def test_gaussian_fill_main_uses_two_thread_executor_and_cleans_up(
    monkeypatch,
):
    """Exercise the production executor lifecycle without starting ROS."""
    events = []

    class FakeNode:
        def destroy_node(self):
            events.append('node_destroyed')

    class FakeExecutor:
        def __init__(self, *, num_threads):
            assert num_threads == 2
            events.append('executor_created')

        def add_node(self, node):
            assert isinstance(node, FakeNode)
            events.append('node_added')

        def spin(self):
            events.append('executor_spun')

        def remove_node(self, node):
            assert isinstance(node, FakeNode)
            events.append('node_removed')

        def shutdown(self):
            events.append('executor_shutdown')

    monkeypatch.setattr(
        gaussian_fill_script.rclpy,
        'init',
        lambda: events.append('context_initialized'),
    )
    monkeypatch.setattr(
        gaussian_fill_script.rclpy,
        'try_shutdown',
        lambda: events.append('context_shutdown'),
    )
    monkeypatch.setattr(gaussian_fill_script, 'GaussianFill', FakeNode)
    monkeypatch.setattr(
        gaussian_fill_script,
        'MultiThreadedExecutor',
        FakeExecutor,
    )

    gaussian_fill_script.main()

    assert events == [
        'context_initialized',
        'executor_created',
        'node_added',
        'executor_spun',
        'node_removed',
        'executor_shutdown',
        'node_destroyed',
        'context_shutdown',
    ]


def test_modified_cost_is_identical_with_observability_enabled(monkeypatch):
    disabled, _ = _run_modified_cost(monkeypatch, False)
    enabled, breakdown = _run_modified_cost(monkeypatch, True)

    assert enabled.timestamp == disabled.timestamp == 9.75
    assert enabled.header == disabled.header == "Modified Cost 2D"
    assert list(enabled.data) == list(disabled.data)
    recombined = (
        np.array(breakdown.raw_cost)
        + np.array(breakdown.gaussian_cost)
        + np.array(breakdown.affine_cost)
    )
    assert recombined.tolist() == list(enabled.data)
    assert list(breakdown.augmented_cost) == list(enabled.data)
    assert breakdown.source_timestamp == enabled.timestamp


def test_bias_all_false_preserves_first_channel_only(monkeypatch):
    legacy, breakdown = _run_modified_cost(monkeypatch, True, bias_all=False)

    assert legacy.data[0] != -1.0
    assert legacy.data[1] == -2.0
    assert breakdown.gaussian_cost[1] == 0.0
    assert breakdown.affine_cost[1] == 0.0
    assert (
        breakdown.raw_cost[0]
        + breakdown.gaussian_cost[0]
        + breakdown.affine_cost[0]
    ) == legacy.data[0]


def test_directional_controller_retains_exact_saturation_diagnostics():
    gains = {"k_vx": 1.0, "k_wz": 5.0}
    params = {
        "wheel_radius": 0.033,
        "wheel_distance": 0.158,
        "wheel_max_rpm": 70,
        "set_max_vx": 0.1,
        "set_max_wz": 0.5,
    }
    controller = Directional_Controller(gains, params)
    output = controller.controller_output(
        2.0,
        np.zeros(6),
        np.array([0.25, -0.2]),
    )

    assert output.tolist() == [0.1, 0.0, 0.0, 0.0, 0.0, -0.5]
    assert controller.last_command_unsaturated.tolist() == [
        0.25,
        0.0,
        0.0,
        0.0,
        0.0,
        -1.0,
    ]
    assert controller.last_command_saturated.tolist() == output.tolist()
    assert controller.last_saturation_flags.tolist() == [
        True,
        False,
        False,
        False,
        False,
        True,
    ]


@pytest.mark.parametrize("mode", ["Resistance", "Voltage"])
def test_photoresistor_source_score_uses_model_endpoints(mode):
    model = Photoresistor_Interpolated_Map(
        {"mode": mode, "x_optimal": 1.0, "y_optimal": 2.0}
    )
    dark = float(model.max_value)
    near = float(model.min_value)
    if mode == "Voltage":
        dark = model.convert_resistance_to_voltage(dark)
        near = model.convert_resistance_to_voltage(near)
    assert model.source_score(dark) == pytest.approx(0.0)
    assert model.source_score(near) == pytest.approx(1.0)
    assert model.source_score((dark + near) / 2.0) == pytest.approx(0.5)
    assert model.source_score(near + 10.0 * (near - dark)) == pytest.approx(1.0)


def test_multi_light_score_does_not_depend_on_light_positions():
    first = Multi_Light_Source_Cost(
        {
            "mode": "Voltage",
            "light_sources": [{"x": 1.0, "y": 2.0, "intensity_lumens": 500.0}],
        }
    )
    second = Multi_Light_Source_Cost(
        {
            "mode": "Voltage",
            "light_sources": [{"x": 9.0, "y": -4.0, "intensity_lumens": 5000.0}],
        }
    )
    cost = first._convert_resistance_to_voltage(1000.0)
    assert first.source_score(cost) == second.source_score(cost)


@pytest.mark.parametrize(
    ('relative_input', 'expected_score'),
    [
        (450.0, 0.7785034367102063),
        (800.0, 0.945004139473373),
        (1200.0, 1.0),
        (2500.0, 1.0),
    ],
)
def test_one_source_best_case_score_bounds_activation_contract(
    relative_input,
    expected_score,
):
    """Lock the live model bound used by Phase 08.1 classification cases."""
    model = Multi_Light_Source_Cost({
        'mode': 'Voltage',
        'reference_intensity_lumens': 1000.0,
        'light_sources': [{
            'x': 0.0,
            'y': 0.0,
            'intensity_lumens': relative_input,
        }],
    })
    best_case_cost = model.cost_output(0.0, np.eye(4))

    assert model.source_score(best_case_cost) == pytest.approx(expected_score)


def test_phase08_1_local_centers_remain_below_controller_target():
    """Keep every intended first local classification numerically reachable."""
    document = yaml.safe_load(
        DIAGNOSTIC_ACTIVATION.read_text(encoding='utf-8')
    )
    case_ids = {
        'activation_fill_create',
        'activation_pure_escape',
        'activation_stalled_assist',
        'activation_fill_merge',
        'activation_recenter_resume',
    }
    checked = {}
    for case in document['cases']:
        if case['case_id'] not in case_ids:
            continue
        model = Multi_Light_Source_Cost({
            'mode': 'Voltage',
            'reference_intensity_lumens': 1000.0,
            'light_sources': [
                {
                    'x': source['x_m'],
                    'y': source['y_m'],
                    'intensity_lumens': source['relative_lumen_input'],
                }
                for source in case['sources']
            ],
        })
        for source in case['sources']:
            if source['evaluation_role'] != 'local_minimum':
                continue
            scores = []
            for angle in np.linspace(0.0, 2.0 * math.pi, 721):
                cosine = math.cos(angle)
                sine = math.sin(angle)
                transform = np.array([
                    [cosine, -sine, 0.0, source['x_m']],
                    [sine, cosine, 0.0, source['y_m']],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ])
                scores.append(
                    model.source_score(model.cost_output(0.0, transform))
                )
            checked[f"{case['case_id']}:{source['id']}"] = max(scores)

    assert set(checked) == {
        'activation_fill_create:local',
        'activation_pure_escape:local',
        'activation_stalled_assist:local',
        'activation_fill_merge:local_a',
        'activation_fill_merge:local_b',
        'activation_recenter_resume:local',
    }
    assert max(checked.values()) < 0.95


def test_unsupported_cost_model_reports_invalid_score():
    model = Position_Based_Sympy_Expression(
        {
            "function": "x**2 + y**2",
            "symbols": ["t", "x", "y", "z"],
        }
    )
    assert np.isnan(model.source_score(0.0))


def test_robust_weighted_cost_keeps_raw_sample_and_evaluates_bias_once(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["modified_cost_node", "/test/raw", "/test/fill", "/test/out"],
    )
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
        ]
    )
    node = ModifiedCost2D()
    try:
        node.pub = Recorder()
        node.cost_breakdown_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        node.xy = np.array([0.0, 0.0])
        calls = []

        def components(_x, _y):
            calls.append(1)
            return 2.0, 3.0, 5.0

        node._bias_components_at_xy = components
        state = AlgorithmState()
        state.algorithm_profile = "robust_gaussian_v1"
        state.state = AlgorithmState.STATE_ESCAPE_ASSIST
        state.state_valid = True
        state.sensor_weight = 0.0
        state.gaussian_weight = 1.0
        state.affine_weight = 1.0
        state.weights_valid = True
        node.algorithm_state_cb(state)

        source = CostBreakdown()
        source.source_timestamp = 12.0
        source.source_timestamp_valid = True
        source.channel_count = 1
        source.raw_cost = [-3.0]
        source.raw_cost_valid = True
        source.source_score = [0.4]
        source.source_score_valid = True
        node.source_cost_cb(source)

        assert len(calls) == 1
        assert list(node.pub.messages[-1].data) == [5.0]
        breakdown = node.cost_breakdown_publisher.messages[-1]
        assert list(breakdown.raw_cost) == [-3.0]
        assert list(breakdown.source_score) == [0.4]
        assert breakdown.sensor_weight == 0.0
        assert breakdown.gaussian_weight == 1.0
        assert breakdown.affine_weight == 1.0
        assert list(breakdown.augmented_cost) == [5.0]
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_anisotropic_revision_replaces_without_double_count(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["modified_cost_node", "/test/raw", "/test/fill", "/test/out"],
    )
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
            "-p",
            "enable_affine_bias:=false",
        ]
    )
    node = ModifiedCost2D()
    try:
        def fill(fill_id, revision, amplitude, active=True, superseded=False):
            message = GaussianFillMessage()
            message.source_timestamp = float(revision)
            message.source_timestamp_valid = True
            message.fill_id = fill_id
            message.cluster_id = 1
            message.revision = revision
            message.center_x = 0.0
            message.center_y = 0.0
            message.amplitude = amplitude
            message.covariance_xx = 0.25
            message.covariance_xy = 0.05
            message.covariance_yy = 0.16
            message.sigma_major = 0.52
            message.sigma_minor = 0.37
            message.covariance_valid = True
            message.principal_widths_valid = True
            message.active = active
            message.superseded = superseded
            return message

        first = fill(1, 1, 1.0)
        node.robust_fill_cb(first)
        assert node._gaussian_bias_at_xy(0.0, 0.0) == pytest.approx(1.0)

        tombstone = fill(1, 1, 1.0, active=False, superseded=True)
        node.robust_fill_cb(tombstone)
        assert node._gaussian_bias_at_xy(0.0, 0.0) == 0.0

        replacement = fill(2, 2, 2.0)
        node.robust_fill_cb(replacement)
        assert node._gaussian_bias_at_xy(0.0, 0.0) == pytest.approx(2.0)
        assert list(node.robust_terms) == [2]

        node.robust_fill_cb(first)
        assert node._gaussian_bias_at_xy(0.0, 0.0) == pytest.approx(2.0)
        assert list(node.robust_terms) == [2]
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_affine_binds_once_in_repulse_and_clears_in_search(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["modified_cost_node", "/test/raw", "/test/fill", "/test/out"],
    )
    rclpy.init(
        args=["--ros-args", "-p", "algorithm_profile:=robust_gaussian_v1"]
    )
    node = ModifiedCost2D()
    try:
        fill = GaussianFillMessage()
        fill.fill_id = 1
        fill.cluster_id = 1
        fill.revision = 1
        fill.active = True
        fill.center_x = 0.0
        fill.center_y = 0.0
        fill.amplitude = 1.0
        fill.covariance_xx = 0.16
        fill.covariance_xy = 0.0
        fill.covariance_yy = 0.16
        fill.sigma_major = 0.4
        fill.sigma_minor = 0.4
        fill.covariance_valid = True
        fill.principal_widths_valid = True
        node.robust_fill_cb(fill)
        assert not node.robust_affine_terms

        state = AlgorithmState()
        state.state = AlgorithmState.STATE_ESCAPE_REPULSE
        state.state_valid = True
        state.sensor_weight = 0.0
        state.gaussian_weight = 1.0
        state.affine_weight = 1.0
        state.weights_valid = True
        state.active_escape_fill_id = 1
        state.active_escape_fill_id_valid = True
        state.safe_direction_x = 0.0
        state.safe_direction_y = 1.0
        state.safe_direction_valid = True
        state.safe_direction_revision = 1
        state.safe_direction_revision_valid = True
        node.algorithm_state_cb(state)

        term = node.robust_affine_terms[1]
        first_start = term["t0"]
        assert term["b0"] == pytest.approx([0.0, node.affine_gain])
        assert node._affine_bias_at_xy(0.0, 1.0) < 0.0
        assert node._affine_bias_at_xy(0.0, -1.0) > 0.0

        node.algorithm_state_cb(state)
        assert node.robust_affine_terms[1]["t0"] == first_start
        state.state = AlgorithmState.STATE_ESCAPE_ASSIST
        node.algorithm_state_cb(state)
        assert node.robust_affine_terms[1]["t0"] == first_start
        state.state = AlgorithmState.STATE_SEARCH
        state.affine_weight = 0.0
        node.algorithm_state_cb(state)
        assert not node.robust_affine_terms

        state.affine_weight = 1.0
        state.safe_direction_revision = 2
        state.safe_direction_x = 1.0
        state.safe_direction_y = 0.0
        node.algorithm_state_cb(state)
        assert node.robust_affine_terms[1]["b0"] == pytest.approx(
            [node.affine_gain, 0.0]
        )
        node.robust_affine_terms[1]["t0"] -= node.affine_max_age + 1.0
        assert node._affine_bias_at_xy(1.0, 0.0) == 0.0
        assert not node.robust_affine_terms
    finally:
        node.destroy_node()
        rclpy.shutdown()


def _run_filter(monkeypatch, observability):
    argv = [
        "filter_node",
        "/test/cost",
        "/test/encoder",
        "/test/timekeeper",
        "/test/filter",
        "--filter_file",
        str(FILTER_CONFIG),
        "--append_encoder_data",
        "True",
        "--enable_observability",
        "True" if observability else "False",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    node = CustomFilter()
    try:
        node.filter_publisher = Recorder()
        if observability:
            node.gesc_diagnostics_publisher = Recorder()
        node.start_time = 0.0
        node.timekeeping_mode = "sim time"
        node.encoder_value = np.array([0.4])
        node.input_value = np.array([-1.25])
        node.input_value_timestamp = 0.1
        node.publish_filter_value()
        return (
            node.filter_publisher.messages[-1],
            np.array(node.z_vec, copy=True),
            node.gesc_diagnostics_publisher.messages[-1]
            if observability
            else None,
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_filter_output_and_state_are_unchanged(monkeypatch):
    disabled_output, disabled_state, _ = _run_filter(monkeypatch, False)
    enabled_output, enabled_state, diagnostics = _run_filter(monkeypatch, True)

    assert enabled_output.data == disabled_output.data
    assert np.array_equal(enabled_state, disabled_state)
    assert list(diagnostics.filter_output) == list(enabled_output.data)
    assert list(diagnostics.filter_state_after) == enabled_state.tolist()
    assert diagnostics.dither_phase_rad == 0.4
    assert diagnostics.dither_amplitude_valid is False
    assert diagnostics.dither_angular_frequency_valid is False


def test_controller_legacy_and_typed_final_commands_match(monkeypatch):
    argv = [
        "controller_node",
        "/test/filter",
        "/test/odom",
        "/test/timekeeper",
        "/test/control",
        "/test/cmd_vel",
        str(CONTROLLER_CONFIG),
        "--enable_observability",
        "True",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    node = CustomController()
    try:
        node.twist_publisher = Recorder()
        node.controller_publisher = Recorder()
        node.control_diagnostics_publisher = Recorder()
        node.start_time = 0.0
        node.timekeeping_mode = "sim time"
        node.state_value = np.zeros(6)
        node.input_value = [0.25, -0.2]
        node.input_value_timestamp = 2.0
        node.publish_control_value()

        legacy = node.controller_publisher.messages[-1]
        twist = node.twist_publisher.messages[-1]
        diagnostics = node.control_diagnostics_publisher.messages[-1]
        assert list(legacy.data) == [0.1, 0.0, 0.0, 0.0, 0.0, -0.5]
        assert list(diagnostics.final_command) == list(legacy.data)
        assert list(diagnostics.gesc_command_unsaturated) == [
            0.25,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
        ]
        assert list(diagnostics.saturation_flags) == [
            True,
            False,
            False,
            False,
            False,
            True,
        ]
        assert diagnostics.supervisor_contribution_valid is False
        assert twist.linear.x == legacy.data[0]
        assert twist.angular.z == legacy.data[5]
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_controller_combines_then_saturates_and_gates_goal(monkeypatch):
    argv = [
        "controller_node",
        "/test/filter",
        "/test/odom",
        "/test/timekeeper",
        "/test/control",
        "/test/cmd_vel",
        str(CONTROLLER_CONFIG),
        "--algorithm_profile",
        "robust_gaussian_v1",
        "--supervisor_state_stale_sec",
        "5.0",
        "--supervisor_command_stale_sec",
        "5.0",
        "--stale_pose_sec",
        "5.0",
        "--stale_filter_sec",
        "5.0",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    node = CustomController()
    try:
        node.twist_publisher = Recorder()
        node.controller_publisher = Recorder()
        node.control_diagnostics_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        node.start_time = 0.0
        node.timekeeping_mode = "sim time"
        node.state_value = np.zeros(6)
        node.input_value = [0.08, 0.04]
        node.input_value_timestamp = 2.0
        now_sec = node._now_sec()
        node.pose_receipt_sec = now_sec
        node.input_receipt_sec = now_sec
        node.supervisor_state_receipt_sec = now_sec
        node.supervisor_command_receipt_sec = now_sec
        node.supervisor_command = np.array([0.05, 0, 0, 0, 0, 0.4])
        state = AlgorithmState()
        state.algorithm_profile = "robust_gaussian_v1"
        state.state = AlgorithmState.STATE_SEARCH
        state.state_valid = True
        state.weights_valid = True
        node.latest_algorithm_state = state

        node.publish_control_value()
        diagnostics = node.control_diagnostics_publisher.messages[-1]
        assert list(diagnostics.gesc_command_unsaturated) == [
            0.08, 0.0, 0.0, 0.0, 0.0, 0.2,
        ]
        assert list(diagnostics.combined_command_unsaturated) == pytest.approx([
            0.13, 0.0, 0.0, 0.0, 0.0, 0.6,
        ])
        assert list(diagnostics.final_command) == [
            0.1, 0.0, 0.0, 0.0, 0.0, 0.5,
        ]

        node.latest_algorithm_state.state = AlgorithmState.STATE_RECENTER
        node.publish_control_value()
        diagnostics = node.control_diagnostics_publisher.messages[-1]
        assert list(diagnostics.combined_command_unsaturated) == [
            0.05, 0.0, 0.0, 0.0, 0.0, 0.4,
        ]
        assert list(diagnostics.final_command) == [
            0.05, 0.0, 0.0, 0.0, 0.0, 0.4,
        ]

        node.latest_algorithm_state.state = AlgorithmState.STATE_GOAL_HOLD
        node.publish_control_value()
        assert list(node.controller_publisher.messages[-1].data) == [0.0] * 6
        assert list(node.control_diagnostics_publisher.messages[-1].final_command) == [
            0.0
        ] * 6

        node.latest_algorithm_state.state = AlgorithmState.STATE_SEARCH
        node.input_receipt_sec = None
        node.controller_started_sec = node._now_sec() - 10.0
        node.recording_ready_required = True
        node.recording_ready = False
        node.recording_ready_receipt_monotonic = (
            controller_node_script.time.monotonic()
        )
        node.algorithm_event_publisher.messages.clear()
        node.publish_control_value()
        assert list(node.controller_publisher.messages[-1].data) == [0.0] * 6
        assert node.algorithm_event_publisher.messages == []

        node.recording_ready_required = False
        node.watchdog_callback()
        assert node.twist_publisher.messages[-1].linear.x == 0.0
        assert any(
            event.event_type == AlgorithmEvent.EVENT_FAILSAFE
            for event in node.algorithm_event_publisher.messages
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_controller_supervisor_owns_only_enabled_assist(monkeypatch):
    argv = [
        "controller_node",
        "/test/filter",
        "/test/odom",
        "/test/timekeeper",
        "/test/control",
        "/test/cmd_vel",
        str(CONTROLLER_CONFIG),
        "--algorithm_profile",
        "robust_gaussian_v1",
        "--open_field_escape_supervisor_owned_assist_enabled",
        "True",
        "--supervisor_state_stale_sec",
        "5.0",
        "--supervisor_command_stale_sec",
        "5.0",
        "--stale_pose_sec",
        "5.0",
        "--stale_filter_sec",
        "5.0",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    node = CustomController()
    try:
        node.twist_publisher = Recorder()
        node.controller_publisher = Recorder()
        node.control_diagnostics_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        node.start_time = 0.0
        node.timekeeping_mode = "sim time"
        node.state_value = np.zeros(6)
        node.input_value = [0.08, 0.04]
        node.input_value_timestamp = 2.0
        now_sec = node._now_sec()
        node.pose_receipt_sec = now_sec
        node.input_receipt_sec = now_sec
        node.supervisor_state_receipt_sec = now_sec
        node.supervisor_command_receipt_sec = now_sec
        node.supervisor_command = np.array(
            [0.15, 0.0, 0.0, 0.0, 0.0, 0.60]
        )
        state = AlgorithmState()
        state.algorithm_profile = "robust_gaussian_v1"
        state.state = AlgorithmState.STATE_ESCAPE_ASSIST
        state.state_valid = True
        state.weights_valid = True
        state.safe_direction_x = 1.0
        state.safe_direction_y = 0.0
        state.safe_direction_valid = True
        state.safe_direction_revision = 1
        state.safe_direction_revision_valid = True
        node.latest_algorithm_state = state

        node.publish_control_value()
        diagnostics = node.control_diagnostics_publisher.messages[-1]
        assert list(diagnostics.gesc_command_unsaturated) == pytest.approx(
            [0.08, 0.0, 0.0, 0.0, 0.0, 0.2]
        )
        assert list(
            diagnostics.combined_command_unsaturated
        ) == pytest.approx(node.supervisor_command)
        assert list(diagnostics.supervisor_contribution) == pytest.approx(
            [0.07, 0.0, 0.0, 0.0, 0.0, 0.4]
        )
        assert list(diagnostics.final_command) == pytest.approx(
            [0.1, 0.0, 0.0, 0.0, 0.0, 0.5]
        )

        node.supervisor_command = np.zeros(6)
        node.supervisor_command_receipt_sec = node._now_sec()
        node.publish_control_value()
        diagnostics = node.control_diagnostics_publisher.messages[-1]
        assert list(
            diagnostics.combined_command_unsaturated
        ) == pytest.approx(np.zeros(6))
        assert list(diagnostics.final_command) == pytest.approx(
            np.zeros(6)
        )

        state.safe_direction_valid = False
        node.supervisor_state_receipt_sec = node._now_sec()
        node.supervisor_command_receipt_sec = node._now_sec()
        node.publish_control_value()
        assert list(
            node.control_diagnostics_publisher.messages[-1].final_command
        ) == pytest.approx(np.zeros(6))
        assert any(
            event.event_type == AlgorithmEvent.EVENT_FAILSAFE
            for event in node.algorithm_event_publisher.messages
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_gaussian_fill_keeps_legacy_layout_and_publishes_fit_record(monkeypatch):
    argv = ["gaussian_fill_node"]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "enable_observability:=true",
            "-p",
            "min_points:=20",
            "-p",
            "min_sigma:=0.1",
            "-p",
            "max_sigma:=1.0",
            "-p",
            "amplitude:=0.5",
        ]
    )
    node = GaussianFill()
    try:
        node.pub = Recorder()
        node.gaussian_fill_diagnostics_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        x_values = np.linspace(-0.8, 0.8, 8)
        y_values = np.linspace(-0.8, 0.8, 8)
        node.buf_xy = np.array(
            [(x_value, y_value) for x_value in x_values for y_value in y_values]
        )
        radius_sq = np.sum(node.buf_xy ** 2, axis=1)
        node.buf_cost = -(1.2 * np.exp(-radius_sq / (2.0 * 0.35 ** 2)) + 0.1)

        trigger = StampedFloat64MultiArray()
        trigger.timestamp = 4.5
        trigger.data = [-0.1, 0.01, 0.1, 0.0, 0.0, 0.2, 0.2, 0.0]
        node.trigger_cb(trigger)

        legacy = node.pub.messages[-1]
        fill = node.gaussian_fill_diagnostics_publisher.messages[-1]
        assert len(legacy.data) == 4
        assert legacy.data[0] == 0.5
        assert fill.fill_id == fill.cluster_id == 1
        assert fill.revision == 1
        assert fill.center_x == legacy.data[1]
        assert fill.center_y == legacy.data[2]
        assert fill.sigma_major == fill.sigma_minor == legacy.data[3]
        assert fill.covariance_xx == pytest.approx(legacy.data[3] ** 2)
        assert fill.sample_count_valid is True
        assert fill.fit_residual_valid is True
        created = [
            event
            for event in node.algorithm_event_publisher.messages
            if event.event_type == AlgorithmEvent.EVENT_FILL_CREATED
        ]
        assert len(created) == 1
        assert len(created[0].value_names) == len(created[0].values)
        assert all(np.isfinite(created[0].values))
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_fill_applies_and_reports_candidate_amplitude_floor(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gaussian_fill_node"])
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
            "-p",
            "minimum_valid_samples:=20",
            "-p",
            "maximum_position_speed_mps:=100.0",
            "-p",
            "candidate_informed_fill_enabled:=true",
            "-p",
            "candidate_informed_fill_amplitude_scale:=1.25",
            "-p",
            "amplitude_max:=6.25",
            "-p",
            "sigma_floor_m:=0.5",
            "-p",
            "sigma_ceiling_m:=1.25",
            "-p",
            "exit_sigma:=2.7",
            "-p",
            "max_fills:=1",
        ]
    )
    node = GaussianFill()
    try:
        node.pub = Recorder()
        node.gaussian_fill_diagnostics_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        for index in range(60):
            stamp = -5.9 + index * 0.1
            angle = index * 2.0 * np.pi / 20.0
            radius = 0.30 - 0.003 * index
            x_value = radius * np.cos(angle)
            y_value = radius * np.sin(angle)
            cost = 0.05 * (x_value ** 2 + y_value ** 2)
            node.pose_snapshots.append(
                PoseSnapshot(stamp, x_value, y_value, angle, True)
            )
            node.cost_snapshots.append(
                CostSnapshot(
                    stamp,
                    float("nan"),
                    False,
                    cost,
                    0.2,
                    True,
                    AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                    True,
                )
            )

        summary = CandidateCostSummary(
            estimate=-1.572582366887451,
            mad=0.2898819545479434,
            uncertainty=0.8696458636438302,
            rotation_count=3,
            pretrigger_rotation_count=6,
            verification_rotation_count=3,
            available_rotation_count=9,
        )
        request = StampedFloat64MultiArray()
        request.header = CANDIDATE_INFORMED_FILL_HEADER
        request.timestamp = 42.0
        request.data = list(
            encode_candidate_informed_fill_payload([0.0] * 8, summary)
        )
        node.trigger_cb(request)

        assert len(node.gaussian_fill_diagnostics_publisher.messages) == 1
        fill = node.gaussian_fill_diagnostics_publisher.messages[0]
        expected_floor = 1.25 * 2.4422282305312812
        assert expected_floor <= fill.amplitude <= 6.25
        assert fill.sigma_major >= 0.5
        assert fill.sigma_minor >= 0.5
        assert fill.exit_radius == pytest.approx(2.7 * fill.sigma_major)
        created = next(
            event
            for event in node.algorithm_event_publisher.messages
            if event.event_type == AlgorithmEvent.EVENT_FILL_CREATED
        )
        diagnostics = dict(zip(created.value_names, created.values))
        assert diagnostics["candidate_fill_raw_cost_lower"] == pytest.approx(
            -2.4422282305312812
        )
        assert diagnostics[
            "candidate_fill_requested_amplitude_floor"
        ] == pytest.approx(expected_floor)
        assert diagnostics[
            "candidate_fill_applied_amplitude_floor"
        ] == pytest.approx(expected_floor)
        assert diagnostics["candidate_fill_amplitude_floor_capped"] == 0.0
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_robust_fill_owner_merges_into_one_frozen_revision(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gaussian_fill_node"])
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
            "-p",
            "minimum_valid_samples:=20",
            "-p",
            "maximum_position_speed_mps:=100.0",
            "-p",
            "amplitude_max:=10.0",
            "-p",
            "sigma_ceiling_m:=2.0",
            "-p",
            "max_fills:=1",
        ]
    )
    node = GaussianFill()
    try:
        node.pub = Recorder()
        node.gaussian_fill_diagnostics_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()

        def load_window(center_x):
            node.pose_snapshots.clear()
            node.cost_snapshots.clear()
            for index in range(10):
                stamp = -100.0 + index * 0.1
                node.pose_snapshots.append(
                    PoseSnapshot(stamp, center_x, 0.0, 0.0, True)
                )
                node.cost_snapshots.append(
                    CostSnapshot(
                        stamp,
                        float('nan'),
                        False,
                        1.0,
                        0.2,
                        True,
                        AlgorithmState.STATE_SEARCH,
                        True,
                    )
                )
            for index in range(60):
                stamp = -5.9 + index * 0.1
                angle = index * 2.0 * np.pi / 20.0
                radius = 0.30 - 0.003 * index
                x_value = center_x + radius * np.cos(angle)
                y_value = radius * np.sin(angle)
                cost = 0.05 * ((x_value - center_x) ** 2 + y_value ** 2)
                node.pose_snapshots.append(
                    PoseSnapshot(stamp, x_value, y_value, angle, True)
                )
                node.cost_snapshots.append(
                    CostSnapshot(
                        stamp,
                        float("nan"),
                        False,
                        cost,
                        0.2,
                        True,
                        AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                        True,
                    )
                )

        trigger = StampedFloat64MultiArray()
        trigger.data = [0.0] * 8
        load_window(0.0)
        trigger.timestamp = 42.0
        node.trigger_cb(trigger)
        load_window(0.05)
        trigger.timestamp = 43.0
        trigger.header = "ROBUST_FILL_REDESIGN:1"
        node.trigger_cb(trigger)

        lifecycle = node.gaussian_fill_diagnostics_publisher.messages
        assert [message.fill_id for message in lifecycle] == [1, 1, 2]
        assert [message.revision for message in lifecycle] == [1, 1, 2]
        assert lifecycle[1].active is False
        assert lifecycle[1].superseded is True
        assert lifecycle[2].cluster_id == 1
        assert lifecycle[2].active is True
        assert node.fill_registry.active_count == 1
        assert len(node.pub.messages) == 2
        assert any(
            event.event_type == AlgorithmEvent.EVENT_FILL_MERGED
            for event in node.algorithm_event_publisher.messages
        )
        created = next(
            event
            for event in node.algorithm_event_publisher.messages
            if event.event_type == AlgorithmEvent.EVENT_FILL_CREATED
        )
        diagnostics = dict(zip(created.value_names, created.values))
        assert diagnostics['pose_snapshot_count'] == 70.0
        assert diagnostics['cost_snapshot_count'] == 70.0
        assert diagnostics['candidate_pose_count'] == 60.0
        assert diagnostics['candidate_cost_count'] == 60.0
        assert 0.0 <= diagnostics['design_duration_wall_sec'] < 1.0
    finally:
        node.destroy_node()
        rclpy.shutdown()
