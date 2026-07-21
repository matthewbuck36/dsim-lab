"""Focused numerical-equivalence tests for opt-in Phase 01 diagnostics."""

from pathlib import Path
import sys

import numpy as np
import pytest
import rclpy

from ros_esc.controller_node.controller_node_script import CustomController
from ros_esc.controller_node.controller_objects.turtlebot_vehicle import (
    Directional_Controller,
)
from ros_esc.filter_node.filter_node_script import CustomFilter
from ros_esc.cost_function_node.cost_function_objects.cost_function_objects import (
    Multi_Light_Source_Cost,
    Photoresistor_Interpolated_Map,
    Position_Based_Sympy_Expression,
)
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from ros_esc.gaussian_fill_node.basin_estimator import CostSnapshot, PoseSnapshot
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill as GaussianFillMessage,
    StampedFloat64MultiArray,
)


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


class Recorder:
    """Minimal publisher replacement that retains published messages."""

    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


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


def test_robust_affine_binds_once_to_supervisor_direction_revision(monkeypatch):
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
        state.state = AlgorithmState.STATE_ESCAPE_ASSIST
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
        state.state = AlgorithmState.STATE_SEARCH
        node.algorithm_state_cb(state)
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
        node.watchdog_callback()
        assert node.twist_publisher.messages[-1].linear.x == 0.0
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
    finally:
        node.destroy_node()
        rclpy.shutdown()
