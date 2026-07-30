"""Deterministic numerical coverage for Phase 04 escape and recentering."""

import math

import numpy as np
import pytest

from ros_esc.supervisor_node.escape_recenter import (
    DirectionConfig,
    EscapeGeometry,
    EscapeProgressConfig,
    EscapeProgressTracker,
    FillAvoidance,
    OperatingBounds,
    Pose2D,
    PostRecoveryProgressConfig,
    PostRecoveryProgressTracker,
    RecenterControlConfig,
    RecenterHoldTracker,
    RecenterRoutePlanner,
    command_sweep_is_safe,
    evaluate_direction,
    evaluate_direction_safety,
    preferred_escape_direction,
    recent_approach,
    recenter_command,
    select_post_recovery_direction,
    select_recenter_direction,
    select_safe_recenter_target,
    select_safe_direction,
    wrap_angle,
)


def pose(stamp, x, y, yaw=0.0):
    return Pose2D(float(stamp), float(x), float(y), float(yaw))


def geometry(**overrides):
    values = {
        "initial_fill_id": 7,
        "center_x": 0.0,
        "center_y": 0.0,
        "exit_radius": 1.0,
        "started_sec": 0.0,
        "approach_x": 1.0,
        "approach_y": 0.0,
    }
    values.update(overrides)
    return EscapeGeometry(**values)


def test_radial_progress_is_interpolated_at_exact_window_boundary():
    tracker = EscapeProgressTracker(
        geometry(),
        EscapeProgressConfig(stall_window_sec=3.0),
    )
    first = tracker.update(pose(0.0, 0.1, 0.0))
    tracker.update(pose(2.0, 0.3, 0.0))
    current = tracker.update(pose(4.0, 0.8, 0.0))

    assert first.radial_distance == pytest.approx(0.1)
    assert first.radial_progress_valid is False
    assert math.isnan(first.radial_progress)
    assert current.radial_progress_valid is True
    assert current.radial_progress == pytest.approx(0.6)


def test_stall_threshold_equality_is_not_stalled_but_inward_motion_is():
    tracker = EscapeProgressTracker(
        geometry(),
        EscapeProgressConfig(
            stall_window_sec=1.0,
            minimum_radial_progress_m=0.05,
        ),
    )
    tracker.update(pose(0.0, 0.5, 0.0))
    exact = tracker.update(pose(1.0, 0.55, 0.0))
    inward = tracker.update(pose(2.0, 0.50, 0.0))
    assert exact.radial_progress == pytest.approx(0.05)
    assert exact.stalled is False
    assert inward.radial_progress < 0.0
    assert inward.stalled is True


def test_strict_exit_requires_nonnegative_progress_hold_and_resets():
    tracker = EscapeProgressTracker(
        geometry(),
        EscapeProgressConfig(stall_window_sec=1.0, escape_exit_hold_sec=1.0),
    )
    tracker.update(pose(0.0, 0.9, 0.0))
    at_radius = tracker.update(pose(1.0, 1.0, 0.0))
    outside = tracker.update(pose(1.5, 1.1, 0.0))
    held = tracker.update(pose(2.5, 1.1, 0.0))
    reset = tracker.update(pose(3.0, 0.95, 0.0))
    assert at_radius.exit_hold_elapsed_valid is False
    assert outside.exit_hold_elapsed_sec == 0.0
    assert outside.stalled is False
    assert held.stable_exit is True
    assert reset.exit_hold_elapsed_valid is False


def test_frozen_geometry_is_not_changed_by_a_replacement_fill():
    frozen = geometry(center_x=1.0, center_y=2.0, exit_radius=0.8)
    tracker = EscapeProgressTracker(frozen)
    replacement = geometry(
        initial_fill_id=8,
        center_x=9.0,
        center_y=9.0,
        exit_radius=4.0,
    )
    del replacement
    tracker.update(pose(0.0, 1.4, 2.0))
    assert tracker.geometry.initial_fill_id == 7
    assert tracker.geometry.center.tolist() == [1.0, 2.0]
    assert tracker.geometry.exit_radius == 0.8


def test_post_recovery_progress_uses_exact_window_interpolation():
    tracker = PostRecoveryProgressTracker(
        pose(0.0, 1.0, 0.0),
        [0.0, 0.0],
        PostRecoveryProgressConfig(
            window_sec=3.0,
            minimum_path_length_m=0.60,
            maximum_displacement_m=0.20,
        ),
    )
    tracker.update(pose(2.0, 1.4, 0.0))
    current = tracker.update(pose(4.0, 1.8, 0.0))

    assert current.fill_distance_m == pytest.approx(1.8)
    assert current.outward_progress_m == pytest.approx(0.8)
    assert current.net_displacement_m == pytest.approx(0.8)
    assert current.path_length_m == pytest.approx(0.8)
    assert current.window_valid is True
    assert current.window_path_length_m == pytest.approx(0.6)
    assert current.window_displacement_m == pytest.approx(0.6)
    assert current.stalled is False


def test_post_recovery_liveness_detects_path_without_translation():
    tracker = PostRecoveryProgressTracker(
        pose(0.0, 1.0, 0.0),
        [0.0, 0.0],
        PostRecoveryProgressConfig(
            window_sec=4.0,
            minimum_path_length_m=0.60,
            maximum_displacement_m=0.20,
        ),
    )
    tracker.update(pose(1.0, 1.2, 0.0))
    tracker.update(pose(2.0, 1.2, 0.2))
    tracker.update(pose(3.0, 1.0, 0.2))
    loop = tracker.update(pose(4.0, 1.0, 0.0))

    assert loop.window_valid is True
    assert loop.window_path_length_m == pytest.approx(0.8)
    assert loop.window_displacement_m == pytest.approx(0.0)
    assert loop.stalled is True

    reset = tracker.reset_liveness_window()
    assert reset.window_valid is False
    assert reset.path_length_m == pytest.approx(0.8)
    assert reset.outward_progress_m == pytest.approx(0.0)


def test_post_recovery_tracker_ignores_duplicate_and_rejects_backward_time():
    tracker = PostRecoveryProgressTracker(
        pose(1.0, 1.0, 0.0),
        [0.0, 0.0],
    )
    first = tracker.update(pose(2.0, 1.1, 0.0))
    duplicate = tracker.update(pose(2.0, 99.0, 99.0))

    assert duplicate is first
    assert duplicate.net_displacement_m == pytest.approx(0.1)
    with pytest.raises(ValueError, match="timestamps must increase"):
        tracker.update(pose(1.5, 1.2, 0.0))


def test_recent_approach_interpolates_and_unbounded_policy_reverses_it():
    history = [pose(0.0, 0.0, 0.0), pose(2.0, 2.0, 0.0), pose(4.0, 5.0, 0.0)]
    approach = recent_approach(history, 3.0)
    assert approach == pytest.approx([4.0, 0.0])
    frozen = geometry(approach_x=approach[0], approach_y=approach[1])
    preferred = preferred_escape_direction([5.0, 0.0], frozen, bounds=None)
    assert preferred == pytest.approx([-1.0, 0.0])


def test_bounded_policy_prefers_center_then_radial_fallback():
    bounds = OperatingBounds()
    preferred = preferred_escape_direction([1.0, 0.0], geometry(), bounds)
    assert preferred == pytest.approx([-1.0, 0.0])
    radial = preferred_escape_direction(
        [0.0, 0.0],
        geometry(center_x=-1.0, center_y=0.0, approach_x=0.0),
        bounds,
    )
    assert radial == pytest.approx([1.0, 0.0])
    with pytest.raises(ValueError, match="nonzero"):
        preferred_escape_direction(
            [0.0, 0.0],
            geometry(approach_x=0.0, center_x=0.0),
            bounds=None,
        )


def test_wall_rejection_selects_positive_rotation_before_negative_tie():
    bounds = OperatingBounds()
    selection = select_safe_direction(
        [1.60, 0.0],
        [1.0, 0.0],
        [],
        DirectionConfig(lookahead_m=0.5),
        bounds,
    )
    assert selection is not None
    assert selection.rotation_rad == pytest.approx(math.pi / 2.0)
    assert selection.y > 0.0


def test_fill_avoidance_rejects_entry_and_allows_only_outward_recovery():
    fill = FillAvoidance(1, 1, 0.0, 0.0, 0.5)
    config = DirectionConfig(lookahead_m=0.5)
    safe, _ = evaluate_direction([0.6, 0.0], [-1.0, 0.0], [-1.0, 0.0], [fill], config)
    assert safe is False
    inward, _ = evaluate_direction([0.2, 0.0], [-1.0, 0.0], [-1.0, 0.0], [fill], config)
    outward, clearance = evaluate_direction([0.2, 0.0], [1.0, 0.0], [1.0, 0.0], [fill], config)
    assert inward is False
    assert outward is True
    assert clearance == pytest.approx(0.2)


def test_no_safe_candidate_returns_none():
    bounds = OperatingBounds(x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5, wall_margin=0.1)
    selection = select_safe_direction(
        [0.0, 0.0],
        [1.0, 0.0],
        [],
        DirectionConfig(lookahead_m=1.0),
        bounds,
    )
    assert selection is None


def test_recenter_selector_allows_temporary_motion_away_from_target():
    fill = FillAvoidance(1, 1, 0.0, 0.0, 0.5)
    config = DirectionConfig(lookahead_m=0.5)
    position = np.array([0.2, 0.0])
    selection = select_recenter_direction(
        position,
        [0.0, 0.0],
        [fill],
        config,
    )
    assert selection is not None
    endpoint = position + config.lookahead_m * selection.direction
    assert np.linalg.norm(endpoint) > np.linalg.norm(position)
    assert np.dot(selection.direction, -position) <= 1e-12
    safe, _ = evaluate_direction_safety(
        position,
        selection.direction,
        [fill],
        config,
    )
    assert safe is True


def test_recenter_selector_uses_deterministic_rotation_tie_break():
    fill = FillAvoidance(1, 1, 0.0, 0.0, 0.4)
    selection = select_recenter_direction(
        [0.8, 0.0],
        [-1.0, 0.0],
        [fill],
        DirectionConfig(lookahead_m=0.5),
        OperatingBounds(),
    )
    assert selection is not None
    assert selection.candidate_index == 1
    assert selection.rotation_rad == pytest.approx(math.pi / 4.0)
    assert selection.y < 0.0


def test_recenter_selector_respects_multiple_fills_walls_and_no_candidate():
    bounds = OperatingBounds()
    fills = (
        FillAvoidance(2, 2, 0.0, 0.3, 0.25),
        FillAvoidance(1, 1, 0.0, -0.3, 0.25),
    )
    config = DirectionConfig(lookahead_m=0.5)
    selection = select_recenter_direction(
        [1.4, 0.0],
        [0.0, 0.0],
        fills,
        config,
        bounds,
    )
    assert selection is not None
    safe, _ = evaluate_direction_safety(
        [1.4, 0.0],
        selection.direction,
        fills,
        config,
        bounds,
    )
    assert safe is True

    blocked_bounds = OperatingBounds(
        x_min=-0.5,
        x_max=0.5,
        y_min=-0.5,
        y_max=0.5,
        wall_margin=0.1,
    )
    assert select_recenter_direction(
        [0.0, 0.0],
        [0.2, 0.0],
        [],
        DirectionConfig(lookahead_m=1.0),
        blocked_bounds,
    ) is None


def test_command_sweep_blocks_inward_reentry_and_wall_crossing():
    fill = FillAvoidance(1, 1, 0.0, 0.0, 0.5)
    assert command_sweep_is_safe(
        [0.2, 0.0], math.pi, 0.1, 0.5, [fill]
    ) is False
    assert command_sweep_is_safe(
        [0.2, 0.0], 0.0, 0.1, 0.5, [fill]
    ) is True
    assert command_sweep_is_safe(
        [0.6, 0.0], math.pi, 0.5, 0.5, [fill]
    ) is False
    assert command_sweep_is_safe(
        [0.6, 0.0], math.pi / 2.0, 0.1, 0.5, [fill]
    ) is True
    assert command_sweep_is_safe(
        [1.64, 0.0],
        0.0,
        0.1,
        0.5,
        [],
        OperatingBounds(),
    ) is False
    assert command_sweep_is_safe(
        [0.2, 0.0], math.pi, 0.0, 0.5, [fill]
    ) is True


def test_boundary_recovery_allows_only_physical_safe_inward_motion():
    bounds = OperatingBounds(
        x_min=-0.25,
        x_max=3.75,
        y_min=-0.25,
        y_max=3.75,
        center_x=1.75,
        center_y=1.75,
        wall_margin=0.20,
    )
    position = [3.56, 1.75]

    assert bounds.contains(position) is False
    assert bounds.contains_physical(position) is True
    assert command_sweep_is_safe(
        position,
        math.pi,
        0.10,
        0.50,
        [],
        bounds,
        allow_inward_from_margin=True,
    ) is True
    assert command_sweep_is_safe(
        position,
        0.0,
        0.10,
        0.50,
        [],
        bounds,
        allow_inward_from_margin=True,
    ) is False
    assert command_sweep_is_safe(
        [3.53, 1.75],
        0.0,
        0.02,
        0.50,
        [],
        bounds,
        allow_inward_from_margin=True,
        boundary_trigger_clearance_m=0.025,
    ) is False
    assert command_sweep_is_safe(
        [3.54, 1.75],
        0.0,
        0.10,
        0.50,
        [],
        bounds,
        allow_inward_from_margin=True,
    ) is False
    assert command_sweep_is_safe(
        [3.76, 1.75],
        math.pi,
        0.10,
        0.50,
        [],
        bounds,
        allow_inward_from_margin=True,
    ) is False


def test_post_recovery_selector_can_reverse_safely_at_corner():
    bounds = OperatingBounds(
        x_min=-0.25,
        x_max=3.75,
        y_min=-0.25,
        y_max=3.75,
        center_x=1.75,
        center_y=1.75,
        wall_margin=0.20,
    )
    position = np.array([3.50, 3.50])
    preferred = position - bounds.center
    config = DirectionConfig(lookahead_m=0.50)

    assert select_safe_direction(
        position, preferred, [], config, bounds
    ) is None
    selected = select_post_recovery_direction(
        position, preferred, [], config, bounds
    )

    assert selected is not None
    assert np.dot(selected.direction, preferred) < 0.0
    safe, unused_clearance = evaluate_direction_safety(
        position, selected.direction, [], config, bounds
    )
    assert safe is True


def test_m3_infeasible_center_gets_safe_proxy_and_persistent_route():
    position = np.array(
        [1.5791701368124422, 2.2524772001799636],
        dtype=np.float64,
    )
    yaw = 0.0
    fill = FillAvoidance(
        1,
        1,
        1.7022778813575337,
        1.8159857225368554,
        0.6086747487,
    )
    bounds = OperatingBounds(
        x_min=-0.25,
        x_max=3.75,
        y_min=-0.25,
        y_max=3.75,
        center_x=1.75,
        center_y=1.75,
        wall_margin=0.20,
    )
    direction_config = DirectionConfig(lookahead_m=0.50)
    control_config = RecenterControlConfig(tolerance_m=0.35)
    target = select_safe_recenter_target(
        position,
        bounds.center,
        [fill],
        bounds,
        clearance_m=0.05,
    )

    assert np.linalg.norm(bounds.center - fill.center) < fill.radius
    assert target is not None
    assert bounds.contains(target)
    assert np.linalg.norm(target - fill.center) > fill.radius + 0.05

    planner = RecenterRoutePlanner()
    hold = RecenterHoldTracker(control_config)
    locked_sides = []
    dt = 0.05
    completed_at = None
    for step in range(1201):
        now_sec = step * dt
        target_distance = float(np.linalg.norm(target - position))
        outside_fill = float(np.linalg.norm(position - fill.center)) > fill.radius
        completion_distance = (
            target_distance
            if outside_fill
            else control_config.tolerance_m + 1.0
        )
        if hold.update(now_sec, completion_distance):
            completed_at = now_sec
            break
        if outside_fill and target_distance <= control_config.tolerance_m:
            linear = 0.0
            angular = 0.0
        else:
            selection = planner.select(
                position,
                target,
                [fill],
                direction_config,
                bounds,
            )
            assert selection is not None
            if planner.side:
                locked_sides.append(planner.side)
            linear, angular = recenter_command(
                selection.direction,
                yaw,
                completion_distance,
                control_config,
            )
            if not command_sweep_is_safe(
                position,
                yaw,
                linear,
                0.50,
                [fill],
                bounds,
                allow_inward_from_margin=True,
            ):
                linear = 0.0
        position = position + linear * dt * np.array(
            [math.cos(yaw), math.sin(yaw)]
        )
        yaw = wrap_angle(yaw + angular * dt)

    assert completed_at is not None
    assert completed_at < 60.0
    assert set(locked_sides) == {-1}
    assert np.linalg.norm(position - fill.center) > fill.radius


@pytest.mark.parametrize(
    'yaw,velocity,horizon',
    [
        (math.nan, 0.1, 0.5),
        (0.0, math.nan, 0.5),
        (0.0, 0.1, math.nan),
        (0.0, -0.1, 0.5),
        (0.0, 0.1, -0.5),
    ],
)
def test_command_sweep_rejects_invalid_values(yaw, velocity, horizon):
    with pytest.raises(ValueError):
        command_sweep_is_safe([0.0, 0.0], yaw, velocity, horizon, [])


def test_recenter_controller_wraps_rotates_and_caps_commands():
    config = RecenterControlConfig()
    assert wrap_angle(3.0 * math.pi) == pytest.approx(-math.pi)
    linear, angular = recenter_command([1.0, 0.0], math.pi, 2.0, config)
    assert linear == 0.0
    assert abs(angular) == config.max_angular_velocity_rps
    linear, angular = recenter_command([1.0, 0.0], 0.2, 2.0, config)
    assert 0.0 < linear <= config.max_linear_velocity_mps
    assert abs(angular) <= config.max_angular_velocity_rps


def test_recenter_hold_completes_and_resets_after_leaving_tolerance():
    tracker = RecenterHoldTracker(RecenterControlConfig(tolerance_m=0.25, hold_sec=1.0))
    assert tracker.update(0.0, 0.2) is False
    assert tracker.update(0.5, 0.3) is False
    assert math.isnan(tracker.elapsed_sec)
    assert tracker.update(1.0, 0.2) is False
    assert tracker.update(2.0, 0.2) is True


def test_retained_m6_recenter_geometry_completes_safely_with_margin():
    position = np.array([-0.922899286, 0.299448541], dtype=np.float64)
    yaw = -0.395048403
    fill = FillAvoidance(
        1,
        1,
        -0.625781953,
        -0.056395888,
        0.608674749,
    )
    fills = (fill,)
    bounds = OperatingBounds(
        x_min=-2.0,
        x_max=2.0,
        y_min=-2.0,
        y_max=2.0,
        wall_margin=0.35,
    )
    direction_config = DirectionConfig(
        lookahead_m=0.5,
        candidate_step_rad=math.pi / 4.0,
    )
    control_config = RecenterControlConfig()
    hold = RecenterHoldTracker(control_config)
    dt = 0.1
    horizon_sec = 0.5
    exited_fill = False
    completed_at = None

    for step in range(201):
        now_sec = step * dt
        distance = float(np.linalg.norm(bounds.center - position))
        if hold.update(now_sec, distance):
            completed_at = now_sec
            break

        if distance <= control_config.tolerance_m:
            linear = 0.0
            angular = 0.0
        else:
            selection = select_recenter_direction(
                position,
                bounds.center,
                fills,
                direction_config,
                bounds,
            )
            assert selection is not None
            linear, angular = recenter_command(
                selection.direction,
                yaw,
                distance,
                control_config,
            )
            if not command_sweep_is_safe(
                position,
                yaw,
                linear,
                horizon_sec,
                fills,
                bounds,
            ):
                linear = 0.0

        assert 0.0 <= linear <= control_config.max_linear_velocity_mps
        assert abs(angular) <= control_config.max_angular_velocity_rps
        start_fill_distance = float(np.linalg.norm(position - fill.center))
        next_position = position + linear * dt * np.array(
            [math.cos(yaw), math.sin(yaw)]
        )
        next_fill_distance = float(
            np.linalg.norm(next_position - fill.center)
        )
        if start_fill_distance <= fill.radius + 1e-12:
            assert next_fill_distance >= start_fill_distance - 1e-12
        else:
            exited_fill = True
            assert next_fill_distance > fill.radius
        assert bounds.contains(next_position)
        position = next_position
        yaw = wrap_angle(yaw + angular * dt)

    assert exited_fill is True
    assert completed_at is not None
    assert completed_at <= 20.0
    assert np.linalg.norm(bounds.center - position) <= control_config.tolerance_m


@pytest.mark.parametrize(
    "factory",
    [
        lambda: OperatingBounds(x_min=1.0, x_max=0.0),
        lambda: OperatingBounds(wall_margin=2.0),
        lambda: OperatingBounds(center_x=1.9),
        lambda: EscapeProgressConfig(stall_window_sec=0.0),
        lambda: PostRecoveryProgressConfig(window_sec=0.0),
        lambda: PostRecoveryProgressConfig(
            minimum_path_length_m=0.20,
            maximum_displacement_m=0.20,
        ),
        lambda: DirectionConfig(lookahead_m=math.nan),
        lambda: RecenterControlConfig(max_linear_velocity_mps=0.0),
        lambda: pose(0.0, math.nan, 0.0),
    ],
)
def test_invalid_geometry_and_controller_settings_are_rejected(factory):
    with pytest.raises(ValueError):
        factory()
