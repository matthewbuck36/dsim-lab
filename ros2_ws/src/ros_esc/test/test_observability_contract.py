"""Focused tests for the Phase 01 typed observability contract."""

import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pytest
import rclpy
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.gaussian_fill_node.gaussian_fill_script import (
    robust_fill_redesign_target,
)
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
    CostBreakdown,
    GaussianFill,
    GescDiagnostics,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
LAUNCH_FILE = (
    REPOSITORY_ROOT
    / "ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml"
)
CONTROL_LAUNCH_FILE = (
    REPOSITORY_ROOT
    / "ros2_ws/src/turtlebot3_rotating_sensor/launch/control.launch.py"
)
COST_CONFIG = (
    REPOSITORY_ROOT
    / "ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC"
    / "cost_function/2D_local_min.json"
)
PHOTORESISTOR_COST_CONFIG = (
    REPOSITORY_ROOT
    / "ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC"
    / "cost_function/multi_light_source_photoresistor.json"
)


class Recorder:
    """Minimal publisher replacement that retains published messages."""

    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


@pytest.mark.parametrize(
    "message_type",
    [
        CostBreakdown,
        GescDiagnostics,
        ControlDiagnostics,
        GaussianFill,
        AlgorithmState,
        AlgorithmEvent,
    ],
)
def test_messages_serialize_and_deserialize(message_type):
    message = message_type()
    message.stamp.sec = 12
    message.stamp.nanosec = 345
    message.source_timestamp = 6.25
    message.source_timestamp_valid = True

    restored = deserialize_message(serialize_message(message), message_type)

    assert restored.stamp.sec == 12
    assert restored.stamp.nanosec == 345
    assert restored.source_timestamp == 6.25
    assert restored.source_timestamp_valid is True


def test_unavailable_fields_are_explicit_and_event_values_are_paired():
    channel_count = 2
    message = CostBreakdown()
    message.channel_count = channel_count
    message.raw_sensor_value = [math.nan] * channel_count
    message.filtered_sensor_value = [math.nan] * channel_count
    message.source_score = [math.nan] * channel_count
    message.raw_sensor_valid = False
    message.filtered_sensor_valid = False
    message.source_score_valid = False

    assert len(message.raw_sensor_value) == message.channel_count
    assert len(message.filtered_sensor_value) == message.channel_count
    assert len(message.source_score) == message.channel_count
    assert all(math.isnan(value) for value in message.raw_sensor_value)
    assert all(math.isnan(value) for value in message.filtered_sensor_value)
    assert all(math.isnan(value) for value in message.source_score)

    event = AlgorithmEvent()
    event.value_names = ["metric", "count_remaining"]
    event.values = [-0.1, 0.0]
    assert len(event.value_names) == len(event.values)


def test_isotropic_fill_contract_and_reserved_state_constants():
    sigma = 0.4
    fill = GaussianFill()
    fill.fill_id = 1
    fill.cluster_id = 1
    fill.revision = 1
    fill.covariance_xx = sigma ** 2
    fill.covariance_xy = 0.0
    fill.covariance_yy = sigma ** 2
    fill.sigma_major = sigma
    fill.sigma_minor = sigma
    fill.covariance_valid = True
    fill.principal_widths_valid = True
    fill.active = True
    fill.superseded = False

    assert fill.fill_id == fill.cluster_id == 1
    assert fill.revision == 1
    assert fill.covariance_xx == pytest.approx(sigma ** 2)
    assert fill.covariance_yy == pytest.approx(sigma ** 2)
    assert fill.sigma_major == fill.sigma_minor == sigma
    assert AlgorithmState.STATE_SEARCH != AlgorithmState.STATE_UNAVAILABLE
    assert AlgorithmState.STATE_FAILSAFE != AlgorithmState.STATE_UNAVAILABLE
    assert AlgorithmEvent.EVENT_STATE_TRANSITION == 3
    assert AlgorithmEvent.EVENT_FILL_MERGED == 22
    assert AlgorithmEvent.EVENT_FILL_SUPERSEDED == 23
    assert AlgorithmEvent.EVENT_FILL_DESIGN_ESCALATED == 24
    assert AlgorithmEvent.EVENT_FILL_DESIGN_FAILED == 25
    assert AlgorithmEvent.EVENT_FILL_LOW_CONFIDENCE == 26


def test_escape_state_contract_and_robust_request_header_semantics():
    state = AlgorithmState()
    state.escape_center_x = 1.0
    state.escape_center_y = -2.0
    state.escape_exit_radius = 0.8
    state.escape_geometry_valid = True
    state.radial_distance = 0.5
    state.radial_distance_valid = True
    state.radial_progress = 0.1
    state.radial_progress_valid = True
    state.escape_stalled = False
    state.escape_stalled_valid = True
    state.safe_direction_x = 0.0
    state.safe_direction_y = 1.0
    state.safe_direction_clearance_m = 0.3
    state.safe_direction_valid = True
    state.safe_direction_revision = 2
    state.safe_direction_revision_valid = True
    state.recenter_target_x = 0.0
    state.recenter_target_y = 0.0
    state.recenter_target_valid = True
    state.recenter_distance = 1.2
    state.recenter_distance_valid = True

    restored = deserialize_message(serialize_message(state), AlgorithmState)
    assert restored.escape_geometry_valid is True
    assert restored.radial_progress == 0.1
    assert restored.safe_direction_revision == 2
    assert restored.recenter_distance == 1.2
    assert robust_fill_redesign_target("ROBUST_FILL_REDESIGN:17") == 17
    assert robust_fill_redesign_target("ROBUST_FILL_CREATE") is None
    assert robust_fill_redesign_target("older_request_header") is None
    assert robust_fill_redesign_target("ROBUST_FILL_REDESIGN:bad") is None


def test_rotation_aware_goal_defaults_are_explicit_in_central_launch():
    root = ET.parse(LAUNCH_FILE).getroot()
    defaults = {
        element.attrib["name"]: element.attrib.get("default")
        for element in root.findall("arg")
    }

    assert defaults["goal_score_rotation_period_sec"] == "3.0"
    assert defaults["goal_score_required_rotations"] == "2"
    assert defaults['verification_max_sec'] == '12.0'
    evidence_duration = (
        float(defaults['goal_score_rotation_period_sec'])
        * int(defaults['goal_score_required_rotations'])
    )
    dwell_duration = max(
        float(defaults['goal_hold_sec']),
        float(defaults['undesired_score_hold_sec']),
    )
    timing_margin = (
        float(defaults['verification_max_sec'])
        - evidence_duration
        - dwell_duration
    )
    assert timing_margin == 3.0


def test_robust_fill_lifecycle_and_all_designed_fields_are_explicit():
    fill = GaussianFill()
    fill.fill_id = 4
    fill.cluster_id = 2
    fill.revision = 3
    fill.center_x = 1.0
    fill.center_y = -2.0
    fill.amplitude = 0.8
    fill.covariance_xx = 0.25
    fill.covariance_xy = 0.05
    fill.covariance_yy = 0.16
    fill.sigma_major = 0.52
    fill.sigma_minor = 0.37
    fill.orientation = 0.4
    fill.support_radius = 1.56
    fill.exit_radius = 1.30
    fill.confidence = 0.75
    fill.sample_count = 80
    fill.fit_residual = 0.01
    fill.fit_condition_number = 20.0
    fill.design_escalations = 2
    fill.covariance_valid = True
    fill.principal_widths_valid = True
    fill.support_radius_valid = True
    fill.exit_radius_valid = True
    fill.confidence_valid = True
    fill.sample_count_valid = True
    fill.fit_residual_valid = True
    fill.fit_condition_number_valid = True
    fill.design_escalations_valid = True
    fill.active = True
    fill.superseded = False

    assert fill.fill_id != fill.cluster_id
    assert fill.revision > 1
    assert all(
        (
            fill.covariance_valid,
            fill.principal_widths_valid,
            fill.support_radius_valid,
            fill.exit_radius_valid,
            fill.confidence_valid,
            fill.sample_count_valid,
            fill.fit_residual_valid,
            fill.fit_condition_number_valid,
            fill.design_escalations_valid,
        )
    )


def _make_cost_node(monkeypatch, enabled):
    argv = [
        "cost_function_node",
        "/test/transforms",
        "/test/timekeeper",
        "/test/raw_cost",
        str(COST_CONFIG),
        "--enable_observability",
        "True" if enabled else "False",
        "--publish_final_breakdown",
        "True",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    return CostFunction()


def test_cost_owner_creates_publishers_only_when_enabled(monkeypatch):
    disabled = _make_cost_node(monkeypatch, False)
    try:
        assert disabled.cost_breakdown_publisher is None
        assert disabled.source_cost_publisher is None
        assert disabled.algorithm_state_publisher is None
        assert disabled.algorithm_event_publisher is None
    finally:
        disabled.destroy_node()
        rclpy.shutdown()


def test_robust_source_owner_publishes_score_without_state_duplication(monkeypatch):
    argv = [
        "cost_function_node",
        "/test/transforms",
        "/test/timekeeper",
        "/test/raw_cost",
        str(PHOTORESISTOR_COST_CONFIG),
        "--algorithm_profile",
        "robust_gaussian_v1",
        "--publish_final_breakdown",
        "False",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    rclpy.init(args=argv)
    node = CostFunction()
    try:
        assert node.source_cost_publisher is not None
        assert node.cost_breakdown_publisher is None
        assert node.algorithm_state_publisher is None
        node.source_cost_publisher = Recorder()
        node.algorithm_event_publisher = Recorder()
        dark = node.cost_function._convert_resistance_to_voltage(
            node.cost_function.max_value
        )
        near = node.cost_function._convert_resistance_to_voltage(
            node.cost_function.min_value
        )
        node.publish_observability([dark, near], source_timestamp=2.0)
        source = node.source_cost_publisher.messages[-1]
        assert list(source.raw_cost) == [dark, near]
        assert list(source.source_score) == pytest.approx([0.0, 1.0])
        assert source.source_score_valid is True
    finally:
        node.destroy_node()
        rclpy.shutdown()

    enabled = _make_cost_node(monkeypatch, True)
    try:
        assert enabled.cost_breakdown_publisher is not None
        assert enabled.source_cost_publisher is not None
        assert enabled.algorithm_state_publisher is not None
        assert enabled.algorithm_event_publisher is not None

        enabled.cost_breakdown_publisher = Recorder()
        enabled.source_cost_publisher = Recorder()
        enabled.algorithm_state_publisher = Recorder()
        enabled.algorithm_event_publisher = Recorder()
        enabled.publish_observability([-1.5, -2.5], source_timestamp=3.0)

        breakdown = enabled.cost_breakdown_publisher.messages[-1]
        source = enabled.source_cost_publisher.messages[-1]
        state = enabled.algorithm_state_publisher.messages[-1]
        assert source.raw_cost == breakdown.raw_cost
        assert all(math.isnan(value) for value in source.source_score)
        assert all(math.isnan(value) for value in breakdown.source_score)
        assert breakdown.channel_count == 2
        assert list(breakdown.raw_cost) == [-1.5, -2.5]
        assert list(breakdown.augmented_cost) == list(breakdown.raw_cost)
        assert breakdown.sensor_weight == 1.0
        assert breakdown.gaussian_weight == 0.0
        assert breakdown.affine_weight == 0.0
        assert breakdown.raw_sensor_valid is False
        assert breakdown.source_score_valid is False
        assert all(math.isnan(value) for value in breakdown.source_score)
        assert state.state == AlgorithmState.STATE_UNAVAILABLE
        assert state.state_valid is False
        assert state.algorithm_profile == "legacy"
        assert state.escape_geometry_valid is False
        assert math.isnan(state.escape_center_x)
        assert state.radial_progress_valid is False
        assert math.isnan(state.radial_progress)
        assert state.safe_direction_revision == 0
        assert state.safe_direction_revision_valid is False
        assert state.recenter_target_valid is False
        assert math.isnan(state.recenter_distance)
        assert all(
            len(event.value_names) == len(event.values)
            for event in enabled.algorithm_event_publisher.messages
        )
    finally:
        enabled.destroy_node()
        rclpy.shutdown()


def test_launch_contract_has_canonical_defaults_and_one_final_owner():
    root = ET.parse(LAUNCH_FILE).getroot()
    args = {
        element.attrib['name']: element.attrib.get('default')
        for element in root.findall('arg')
    }
    expected = {
        "algorithm_profile": "legacy",
        "supervisor_use_sim_time": "True",
        'supervisor_command_stale_sec': '0.50',
        "enable_observability": "False",
        "cost_breakdown_topic": "/gesc_gaussian/cost_breakdown",
        "gesc_diagnostics_topic": "/gesc_gaussian/gesc_diagnostics",
        "control_diagnostics_topic": "/gesc_gaussian/control_diagnostics",
        "gaussian_fill_diagnostics_topic": "/gesc_gaussian/gaussian_fills",
        "algorithm_state_topic": "/gesc_gaussian/algorithm_state",
        "algorithm_event_topic": "/gesc_gaussian/algorithm_events",
        "observability_source_mode": "simulation",
        "source_cost_topic": "/gesc_gaussian/source_cost",
        "convergence_status_topic": "/gesc_gaussian/convergence_status",
        "fill_request_topic": "/gesc_gaussian/fill_requests",
        "supervisor_command_topic": "/gesc_gaussian/supervisor_command",
        "supervisor_stop_topic": "/gesc_gaussian/stop_requested",
        "recording_ready_required": "False",
        "recording_ready_topic": "/gesc_gaussian/recording_ready",
        "recording_ready_stale_sec": "0.50",
        "escape_exit_hold_sec": "1.0",
        "stall_window_sec": "3.0",
        "minimum_radial_progress_m": "0.05",
        "approach_history_window_sec": "3.0",
        "room_bounds_x_min_m": "-2.0",
        "room_bounds_x_max_m": "2.0",
        "room_bounds_y_min_m": "-2.0",
        "room_bounds_y_max_m": "2.0",
        "room_center_x_m": "0.0",
        "room_center_y_m": "0.0",
        "wall_margin_m": "0.35",
        "direction_lookahead_m": "0.50",
        "adaptive_recenter_lookahead_enabled": "False",
        "direction_candidate_step_rad": "0.7853981633974483",
        "fill_avoidance_margin_m": "0.10",
        "recenter_tolerance_m": "0.25",
        "recenter_hold_sec": "1.0",
        "recenter_linear_gain": "0.50",
        "recenter_angular_gain": "1.50",
        "recenter_max_linear_velocity_mps": "0.10",
        "recenter_max_angular_velocity_rps": "0.40",
        "recenter_rotate_in_place_angle_rad": "1.0471975511965976",
        "post_recovery_progress_enabled": "False",
        "post_recovery_guidance_min_progress_m": "0.60",
        "post_recovery_liveness_window_sec": "12.0",
        "post_recovery_liveness_min_path_length_m": "0.60",
        "post_recovery_liveness_max_displacement_m": "0.20",
        "post_recovery_direction_refresh_limit": "0",
        "post_recovery_source_led_handoff_enabled": "False",
        "robust_search_epoch_reset_enabled": "False",
        "gaussian_fill_pose_topic": "/odom",
        "gaussian_fill_estimation_channel_index": "0",
        "gaussian_fill_sample_sync_tolerance_sec": "0.05",
        "gaussian_fill_maximum_position_speed_mps": "0.20",
        "gaussian_fill_outlier_mad_threshold": "3.5",
        "gaussian_fill_maximum_cluster_samples": "4000",
        "gaussian_fill_estimation_window_sec": "8.0",
        "gaussian_fill_minimum_valid_samples": "40",
        "gaussian_fill_maximum_sample_age_sec": "12.0",
        "gaussian_fill_mean_shift_iterations": "5",
        "gaussian_fill_center_tolerance_m": "0.005",
        "gaussian_fill_position_kernel_bandwidth_m": "0.25",
        "gaussian_fill_cost_temperature_normalized": "0.05",
        "gaussian_fill_covariance_eigenvalue_min_m2": "0.0025",
        "gaussian_fill_covariance_eigenvalue_max_m2": "0.25",
        "gaussian_fill_quadratic_ridge_lambda": "1e-6",
        "gaussian_fill_quadratic_condition_number_max": "1e8",
        "gaussian_fill_center_cost_percentile": "10.0",
        "gaussian_fill_shoulder_cost_percentile": "80.0",
        "gaussian_fill_inner_mahalanobis_radius": "1.0",
        "gaussian_fill_minimum_basin_depth": "0.02",
        "gaussian_fill_covariance_scale": "2.5",
        "gaussian_fill_sigma_floor_m": "0.15",
        "gaussian_fill_sigma_ceiling_m": "1.25",
        "gaussian_fill_amplitude_depth_scale": "1.5",
        "gaussian_fill_amplitude_curvature_scale": "1.2",
        "gaussian_fill_amplitude_min": "0.10",
        "gaussian_fill_amplitude_max": "3.00",
        "gaussian_fill_validation_grid_points_per_axis": "41",
        "gaussian_fill_validation_support_sigma": "3.0",
        "gaussian_fill_maximum_design_escalations": "5",
        "gaussian_fill_amplitude_escalation_factor": "1.5",
        "gaussian_fill_width_escalation_factor": "1.25",
        "gaussian_fill_grid_minimum_tolerance": "1e-9",
        "gaussian_fill_support_sigma": "3.0",
        "gaussian_fill_exit_sigma": "2.5",
        "gaussian_fill_merge_bandwidth_m": "0.50",
        "gaussian_fill_merge_radius_scale": "2.0",
        "gaussian_fill_minimum_merge_probability": "0.60",
        "gaussian_fill_low_confidence_threshold": "0.60",
    }
    for name, default in expected.items():
        assert args[name] == default

    cost_commands = [
        element
        for element in root.findall("executable")
        if "cost_function_node" in element.attrib.get("cmd", "")
    ]
    assert len(cost_commands) == 2
    non_pde = next(element for element in cost_commands if "unless" in element.attrib)
    pde = next(element for element in cost_commands if "if" in element.attrib)
    non_pde_tokens = non_pde.attrib["cmd"].split()
    pde_tokens = pde.attrib["cmd"].split()
    non_pde_flag = non_pde_tokens.index("--publish_final_breakdown")
    pde_flag = pde_tokens.index("--publish_final_breakdown")
    assert non_pde_tokens[non_pde_flag + 1] == "True"
    assert pde_tokens[pde_flag + 1] == "False"
    assert "$(var use_pde_extensions)" in non_pde.attrib["unless"]
    assert "$(var use_pde_extensions)" in pde.attrib["if"]

    supervisor_commands = [
        element
        for element in root.findall('executable')
        if 'supervisor_node' in element.attrib.get('cmd', '')
    ]
    assert len(supervisor_commands) == 1
    assert "robust_gaussian_v1" in supervisor_commands[0].attrib["if"]
    assert (
        "-p use_sim_time:=$(var supervisor_use_sim_time)"
        in supervisor_commands[0].attrib["cmd"]
    )
    assert (
        '-p supervisor_command_stale_sec:=$(var supervisor_command_stale_sec)'
        in supervisor_commands[0].attrib['cmd']
    )
    assert 'light_source' not in supervisor_commands[0].attrib['cmd']
    assert 'evaluation_role' not in supervisor_commands[0].attrib['cmd']
    assert 'global_source' not in supervisor_commands[0].attrib['cmd']
    for name in (
        'post_recovery_progress_enabled',
        'post_recovery_guidance_min_progress_m',
        'post_recovery_liveness_window_sec',
        'post_recovery_liveness_min_path_length_m',
        'post_recovery_liveness_max_displacement_m',
        'post_recovery_direction_refresh_limit',
        'post_recovery_source_led_handoff_enabled',
        'adaptive_recenter_lookahead_enabled',
    ):
        assert (
            f'-p {name}:=$(var {name})'
            in supervisor_commands[0].attrib['cmd']
        )
    pde_history_commands = [
        element
        for element in root.findall('executable')
        if 'ros2 run ros_esc pde_history_node'
        in element.attrib.get('cmd', '')
    ]
    pde_cost_history_commands = [
        element
        for element in root.findall('executable')
        if 'ros2 run ros_esc pde_cost_history_node'
        in element.attrib.get('cmd', '')
    ]
    assert len(pde_history_commands) == 1
    assert len(pde_cost_history_commands) == 1
    for element in pde_history_commands + pde_cost_history_commands:
        command = element.attrib['cmd']
        assert '-p algorithm_profile:=$(var algorithm_profile)' in command
        assert (
            '-p robust_search_epoch_reset_enabled:='
            '$(var robust_search_epoch_reset_enabled)'
        ) in command
        assert (
            '-p algorithm_state_topic:=$(var algorithm_state_topic)'
            in command
        )
    gaussian_commands = [
        element
        for element in root.findall("executable")
        if "gaussian_fill_node" in element.attrib.get("cmd", "")
    ]
    modified_cost_commands = [
        element
        for element in root.findall("executable")
        if "modified_cost_node" in element.attrib.get("cmd", "")
    ]
    assert len(gaussian_commands) == 1
    assert len(modified_cost_commands) == 1
    assert "gaussian_fill_diagnostics_topic" in modified_cost_commands[0].attrib["cmd"]
    controller_commands = [
        element
        for element in root.iter("executable")
        if "controller_node" in element.attrib.get("cmd", "")
    ]
    assert len(controller_commands) == 1
    controller_command = controller_commands[0].attrib["cmd"]
    assert "--recording_ready_required" in controller_command
    assert "$(var recording_ready_required)" in controller_command
    assert "--recording_ready_topic" in controller_command
    assert "$(var recording_ready_topic)" in controller_command
    assert "--recording_ready_stale_sec" in controller_command


def test_controller_spawners_allow_bounded_gazebo_startup_latency():
    source = CONTROL_LAUNCH_FILE.read_text(encoding="utf-8")

    assert source.count("'--service-call-timeout'") == 2
    assert source.count("'30.0'") == 2
