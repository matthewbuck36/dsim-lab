"""Deterministic numerical coverage for Phase 04 escape and recentering."""

import math
from types import SimpleNamespace

import numpy as np
import pytest

from ros_esc.supervisor_node import escape_recenter as escape_recenter_module
from ros_esc.supervisor_node.escape_recenter import (
    ApproachContinuityEvidence,
    DirectionConfig,
    EscapeGeometry,
    EscapeProgressConfig,
    EscapeProgressTracker,
    FillAvoidance,
    OperatingBounds,
    Pose2D,
    PostRecoveryProgressConfig,
    PostRecoveryProgressTracker,
    approach_continuity_evidence,
    projected_direction_progress,
    RecenterControlConfig,
    RecenterHoldTracker,
    RecenterRoutePlanner,
    command_sweep_is_safe,
    evaluate_direction,
    evaluate_direction_safety,
    latch_direct_escape_direction,
    preferred_escape_direction,
    recent_approach,
    recenter_command,
    select_post_recovery_direction,
    select_recenter_direction,
    select_safe_recenter_target,
    select_safe_direction,
    select_source_continuity_direction,
    source_continuity_evidence,
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


def test_approach_continuity_uses_newest_pose_strictly_outside_exit():
    center = np.array([1.0, 1.0])
    evidence = approach_continuity_evidence(
        [
            pose(0.0, -1.0, 1.0),
            pose(1.0, -0.5, 1.0),
            pose(2.0, 0.0, 1.0),
            pose(3.0, 0.5, 1.0),
        ],
        center,
        1.0,
    )

    assert evidence.anchor == pytest.approx([-0.5, 1.0])
    assert evidence.anchor_stamp_sec == pytest.approx(1.0)
    assert evidence.displacement_m == pytest.approx(1.5)
    assert evidence.history_age_sec == pytest.approx(2.0)
    assert evidence.direction == pytest.approx([1.0, 0.0])
    assert evidence.exclusion_radius_m == pytest.approx(1.0)
    assert evidence.anchor_mode == "outside_radius"


def test_approach_continuity_interior_fallback_is_bounded_and_deterministic():
    center = np.array([1.0, 1.0])
    history = [
        pose(0.0, 0.4, 1.0),
        pose(1.0, 1.0, 0.4),
        pose(2.0, 0.8, 1.0),
    ]

    evidence = approach_continuity_evidence(
        history,
        center,
        1.0,
        interior_anchor_fallback_enabled=True,
        interior_anchor_min_displacement_m=0.60,
    )

    assert evidence.anchor == pytest.approx([0.4, 1.0])
    assert evidence.anchor_stamp_sec == pytest.approx(0.0)
    assert evidence.displacement_m == pytest.approx(0.60)
    assert evidence.history_age_sec == pytest.approx(2.0)
    assert evidence.direction == pytest.approx([1.0, 0.0])
    assert evidence.anchor_mode == "interior_farthest"


def test_approach_continuity_outside_anchor_has_priority_over_fallback():
    evidence = approach_continuity_evidence(
        [
            pose(0.0, -1.0, 0.0),
            pose(1.0, -0.75, 0.0),
            pose(2.0, -2.0, 0.0),
            pose(3.0, -0.25, 0.0),
        ],
        [0.0, 0.0],
        1.0,
        interior_anchor_fallback_enabled=True,
        interior_anchor_min_displacement_m=0.50,
    )

    assert evidence.anchor == pytest.approx([-2.0, 0.0])
    assert evidence.anchor_stamp_sec == pytest.approx(2.0)
    assert evidence.anchor_mode == "outside_radius"


def test_approach_continuity_interior_exact_tie_uses_earliest_history_pose():
    evidence = approach_continuity_evidence(
        [
            pose(0.0, -0.6, 0.0),
            pose(1.0, 0.6, 0.0),
            pose(2.0, 0.1, 0.0),
        ],
        [0.0, 0.0],
        1.0,
        interior_anchor_fallback_enabled=True,
        interior_anchor_min_displacement_m=0.50,
    )

    assert evidence.anchor == pytest.approx([-0.6, 0.0])
    assert evidence.anchor_stamp_sec == pytest.approx(0.0)
    assert evidence.direction == pytest.approx([1.0, 0.0])


def test_approach_continuity_scans_physical_length_history_without_numpy_per_pose(
    monkeypatch,
):
    history = [
        pose(
            index * 0.05,
            -2.0 if index == 1200 else -0.25,
            0.0,
        )
        for index in range(3114)
    ]
    finite_vector_calls = []
    original_finite_vector = escape_recenter_module._finite_vector

    def counting_finite_vector(values, name):
        finite_vector_calls.append(name)
        return original_finite_vector(values, name)

    monkeypatch.setattr(
        escape_recenter_module,
        "_finite_vector",
        counting_finite_vector,
    )

    evidence = approach_continuity_evidence(history, [0.0, 0.0], 1.0)

    assert finite_vector_calls == ["approach-continuity fill center"]
    assert evidence.anchor == pytest.approx([-2.0, 0.0])
    assert evidence.anchor_stamp_sec == pytest.approx(60.0)
    assert evidence.history_age_sec == pytest.approx(95.65)
    assert evidence.direction == pytest.approx([1.0, 0.0])


def test_v8_12_failed_seed_19931_critical_odometry_replay():
    center = [1.0699606541859803, 0.7605913520944112]
    radius = 1.3667708293638696
    history = [
        pose(0.0, 4.718067908752316e-06, 2.7129102748803485e-05),
        pose(1.0, -0.0019376353428124755, -0.0021311540019673843),
        pose(2.0, 1.069992273318767, 0.7620317121328785),
    ]

    assert approach_continuity_evidence(history, center, radius) is None
    evidence = approach_continuity_evidence(
        history,
        center,
        radius,
        interior_anchor_fallback_enabled=True,
        interior_anchor_min_displacement_m=0.50,
    )

    assert evidence.anchor == pytest.approx(
        [-0.0019376353428124755, -0.0021311540019673843]
    )
    assert evidence.displacement_m == pytest.approx(1.3155651121858971)
    assert evidence.direction == pytest.approx(
        [0.8147816323190298, 0.579767963616081]
    )
    assert evidence.anchor_mode == "interior_farthest"


def test_approach_continuity_interior_fallback_rejects_tiny_or_bad_history():
    kwargs = {
        "interior_anchor_fallback_enabled": True,
        "interior_anchor_min_displacement_m": 0.50,
    }
    assert approach_continuity_evidence([], [0.0, 0.0], 1.0, **kwargs) is None
    assert approach_continuity_evidence(
        [pose(0.0, 0.49, 0.0), pose(1.0, 0.0, 0.0)],
        [0.0, 0.0],
        1.0,
        **kwargs,
    ) is None
    with pytest.raises(ValueError, match="timestamps must increase"):
        approach_continuity_evidence(
            [pose(1.0, 0.6, 0.0), pose(1.0, 0.0, 0.0)],
            [0.0, 0.0],
            1.0,
            **kwargs,
        )
    bad_pose = SimpleNamespace(
        position=np.array([float("nan"), 0.0]),
        stamp_sec=0.0,
        x=float("nan"),
        y=0.0,
    )
    with pytest.raises(ValueError, match="finite poses"):
        approach_continuity_evidence(
            [bad_pose],
            [0.0, 0.0],
            1.0,
            **kwargs,
        )
    with pytest.raises(ValueError, match="must be boolean"):
        approach_continuity_evidence(
            [pose(0.0, 0.6, 0.0)],
            [0.0, 0.0],
            1.0,
            interior_anchor_fallback_enabled=1,
        )
    with pytest.raises(ValueError, match="minimum displacement"):
        approach_continuity_evidence(
            [pose(0.0, 0.6, 0.0)],
            [0.0, 0.0],
            1.0,
            interior_anchor_fallback_enabled=True,
            interior_anchor_min_displacement_m=0.0,
        )


def test_approach_continuity_evidence_rejects_unknown_anchor_mode():
    with pytest.raises(ValueError, match="anchor mode"):
        ApproachContinuityEvidence(
            anchor_x=0.0,
            anchor_y=0.0,
            anchor_stamp_sec=0.0,
            direction_x=1.0,
            direction_y=0.0,
            displacement_m=1.0,
            history_age_sec=0.0,
            exclusion_radius_m=1.0,
            anchor_mode="unknown",
        )


def test_approach_continuity_rejects_bad_history_and_missing_evidence():
    assert approach_continuity_evidence([], [0.0, 0.0], 1.0) is None
    assert approach_continuity_evidence(
        [pose(0.0, 0.0, 0.0), pose(1.0, 0.5, 0.0)],
        [0.0, 0.0],
        1.0,
    ) is None
    with pytest.raises(ValueError, match="timestamps must increase"):
        approach_continuity_evidence(
            [pose(1.0, 2.0, 0.0), pose(1.0, 0.0, 0.0)],
            [0.0, 0.0],
            1.0,
        )
    with pytest.raises(ValueError, match="finite and positive"):
        approach_continuity_evidence(
            [pose(0.0, 2.0, 0.0)],
            [0.0, 0.0],
            0.0,
        )
    with pytest.raises(ValueError, match="displacement must be positive"):
        ApproachContinuityEvidence(
            anchor_x=0.0,
            anchor_y=0.0,
            anchor_stamp_sec=0.0,
            direction_x=1.0,
            direction_y=0.0,
            displacement_m=0.0,
            history_age_sec=0.0,
            exclusion_radius_m=1.0,
        )


@pytest.mark.parametrize(
    "center,current,anchor,expected_continuity,expected_radial",
    [
        (
            [0.9063138817160753, 1.187088911496894],
            [0.9074572187525843, 1.1858862198329585],
            [0.19706456831241406, 0.01716688229276277],
            [0.9712414607743503, 0.238096671276409],
            [0.6889964737348437, -0.7247646922836064],
        ),
        (
            [1.3150554594020005, 1.0298134346805476],
            [1.3149823259225, 1.0301479155128903],
            [0.34901700592311424, 0.061924829606774014],
            [0.7064299821700579, 0.7077829330318807],
            [-0.21360154392691805, 0.976920867026617],
        ),
        (
            [1.2960568694674788, 0.9713325216094635],
            [1.2957895816020304, 0.9724226694049221],
            [0.2974907931237344, 0.034798152725139274],
            [0.7293991768649621, 0.684088328206757],
            [-0.23813171183223117, 0.9712328700264686],
        ),
        (
            [1.2159934811154662, 0.9927434160879254],
            [1.216355464277686, 0.9938346463446656],
            [0.24976300129360293, 0.024695456966771282],
            [0.7064420603695425, 0.7077708777145579],
            [0.3148494834874919, 0.9491416136423793],
        ),
        (
            [0.9024309599026483, 1.2748722127037169],
            [0.9031537479081813, 1.2741645958174819],
            [0.31732117094725015, 0.03934286786719746],
            [0.9417105674149527, 0.3364241477941317],
            [0.7145662868677917, -0.6995677391589588],
        ),
    ],
)
def test_v8_4_retained_fill_acceptance_replay_is_forward_and_fill_safe(
    center,
    current,
    anchor,
    expected_continuity,
    expected_radial,
):
    exit_radius = 1.3667708293638696
    avoidance = FillAvoidance(
        1,
        1,
        center[0],
        center[1],
        1.618634254848744,
    )
    config = DirectionConfig(lookahead_m=0.50)
    evidence = approach_continuity_evidence(
        [
            pose(0.0, anchor[0], anchor[1]),
            pose(1.0, current[0], current[1]),
        ],
        center,
        exit_radius,
    )

    continuity = select_source_continuity_direction(
        current,
        evidence.direction,
        [avoidance],
        config,
        None,
    )
    radial = select_safe_direction(
        current,
        np.asarray(current) - np.asarray(center),
        [avoidance],
        config,
        None,
    )

    assert continuity.direction == pytest.approx(expected_continuity)
    assert radial.direction == pytest.approx(expected_radial)
    assert np.dot(continuity.direction, evidence.direction) >= -1e-12
    safe, unused_clearance = evaluate_direction_safety(
        current,
        continuity.direction,
        [avoidance],
        config,
        None,
    )
    assert safe is True


def test_v8_4_failed_seed_stall_replay_avoids_old_reverse_hemisphere():
    center = np.array([0.9024309599026483, 1.2748722127037169])
    anchor = np.array([0.31732117094725015, 0.03934286786719746])
    stall = np.array([0.8512191620399492, 1.2598740198016434])
    evidence = approach_continuity_evidence(
        [pose(0.0, *anchor), pose(1.0, *stall)],
        center,
        1.3667708293638696,
    )
    avoidance = FillAvoidance(
        1,
        1,
        center[0],
        center[1],
        1.618634254848744,
    )
    config = DirectionConfig(lookahead_m=0.50)

    old_radial = select_safe_direction(
        stall,
        stall - center,
        [avoidance],
        config,
        None,
    )
    selected = select_source_continuity_direction(
        stall,
        evidence.direction,
        [avoidance],
        config,
        None,
    )

    assert old_radial.direction == pytest.approx(
        [-0.9596900358585478, -0.2810605541050169]
    )
    assert selected.direction == pytest.approx(
        [-0.33642414779413166, 0.9417105674149527]
    )
    assert np.dot(old_radial.direction, evidence.direction) < 0.0
    assert np.dot(selected.direction, evidence.direction) > 0.0
    safe, unused_clearance = evaluate_direction_safety(
        stall,
        selected.direction,
        [avoidance],
        config,
        None,
    )
    assert safe is True


@pytest.mark.parametrize(
    "center,current,anchor,expected_v8_4",
    [
        (
            [0.9063138817160753, 1.187088911496894],
            [0.9074572187525843, 1.1858862198329585],
            [0.19706456831241406, 0.01716688229276277],
            [0.9712414607743503, 0.238096671276409],
        ),
        (
            [1.3150554594020005, 1.0298134346805476],
            [1.3149823259225, 1.0301479155128903],
            [0.34901700592311424, 0.061924829606774014],
            [0.7064299821700579, 0.7077829330318807],
        ),
        (
            [1.2960568694674788, 0.9713325216094635],
            [1.2957895816020304, 0.9724226694049221],
            [0.2974907931237344, 0.034798152725139274],
            [0.7293991768649621, 0.684088328206757],
        ),
        (
            [1.2159934811154662, 0.9927434160879254],
            [1.216355464277686, 0.9938346463446656],
            [0.24976300129360293, 0.024695456966771282],
            [0.7064420603695425, 0.7077708777145579],
        ),
        (
            [0.9024309599026483, 1.2748722127037169],
            [0.9031537479081813, 1.2741645958174819],
            [0.31732117094725015, 0.03934286786719746],
            [0.9417105674149527, 0.3364241477941317],
        ),
        (
            [0.9193437680003431, 1.206038462432671],
            [0.9204599467913561, 1.205191387188364],
            [0.21883897048812004, 0.03011067851068248],
            [0.969370050048291, 0.24560477615342463],
        ),
        (
            [1.1802901360361109, 1.000947632559398],
            [1.1807017996123272, 1.0018878747455646],
            [0.23788157417248793, 0.00987028910360638],
            [0.6890895569114577, 0.724676191519751],
        ),
        (
            [1.0694882817937204, 1.314024891709896],
            [1.070101672495912, 1.3123173373351547],
            [0.5192862749000959, 0.05929134639020261],
            [0.9158203493840072, -0.40158820656756716],
        ),
    ],
)
def test_v8_5_retained_geometries_latch_direct_active_fill_transit(
    center,
    current,
    anchor,
    expected_v8_4,
):
    evidence = approach_continuity_evidence(
        [pose(0.0, *anchor), pose(1.0, *current)],
        center,
        1.3667708293638696,
    )
    active = FillAvoidance(
        1,
        1,
        center[0],
        center[1],
        1.618634254848744,
    )
    config = DirectionConfig(lookahead_m=0.50)

    unchanged_v8_4 = select_source_continuity_direction(
        current,
        evidence.direction,
        [active],
        config,
        None,
    )
    latched_v8_5 = latch_direct_escape_direction(
        current,
        evidence.direction,
        [],
        config,
    )

    assert unchanged_v8_4.direction == pytest.approx(expected_v8_4)
    assert latched_v8_5.direction == pytest.approx(evidence.direction)
    assert latched_v8_5.rotation_rad == pytest.approx(0.0)
    assert latched_v8_5.candidate_index == 0


def test_v8_5_failed_seed_direct_corridor_ignores_only_active_fill():
    center = np.array([1.0694882817937204, 1.314024891709896])
    current = np.array([1.070101672495912, 1.3123173373351547])
    preferred = np.array([0.4015882065675672, 0.9158203493840072])
    config = DirectionConfig(lookahead_m=0.50)
    active = FillAvoidance(
        1,
        1,
        center[0],
        center[1],
        1.618634254848744,
    )

    safe_with_active, unused_clearance = evaluate_direction_safety(
        current,
        preferred,
        [active],
        config,
        None,
    )
    at_start = latch_direct_escape_direction(
        current,
        preferred,
        [],
        config,
    )
    after_old_reversal = latch_direct_escape_direction(
        [-0.3808628950823218, 1.3271483177165915],
        preferred,
        [],
        config,
    )

    assert safe_with_active is False
    assert at_start.direction == pytest.approx(preferred)
    assert after_old_reversal.direction == pytest.approx(preferred)

    retained_other = FillAvoidance(
        2,
        2,
        current[0] + 0.25 * preferred[0],
        current[1] + 0.25 * preferred[1],
        0.10,
    )
    assert (
        latch_direct_escape_direction(
            current,
            preferred,
            [retained_other],
            config,
        )
        is None
    )


def test_m4_5_retained_radius_two_rejects_exact_radial_reversal():
    anchor = np.array([1.2320122160, 1.4710422281])
    current = np.array([1.3775, 1.5451])
    fill_center = np.array([1.8278297781, 1.7700514862])
    fill = FillAvoidance(
        1,
        1,
        fill_center[0],
        fill_center[1],
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
    config = DirectionConfig(lookahead_m=0.50)

    evidence = source_continuity_evidence(
        anchor,
        current,
        fill_center,
        minimum_displacement_m=0.05,
        reversal_dot_threshold=-0.90,
    )
    assert evidence is not None
    assert evidence.displacement_m == pytest.approx(0.1632521022)
    assert evidence.radial_alignment == pytest.approx(-0.9999712891)

    unchanged_fallback = select_post_recovery_direction(
        current,
        current - fill_center,
        [fill],
        config,
        bounds,
    )
    assert unchanged_fallback is not None
    assert unchanged_fallback.direction == pytest.approx(
        [-0.8945966998, -0.4468744173]
    )
    assert (
        np.dot(unchanged_fallback.direction, evidence.direction)
        < -0.999
    )

    selected = select_safe_direction(
        current,
        evidence.direction,
        [fill],
        config,
        bounds,
    )
    assert selected is not None
    assert selected.direction == pytest.approx(
        [-0.4536405406, 0.8911847507]
    )
    assert np.dot(selected.direction, evidence.direction) >= -1e-12
    safe, unused_clearance = evaluate_direction_safety(
        current,
        selected.direction,
        [fill],
        config,
        bounds,
    )
    assert safe is True


def test_m4_7_live_geometry_reacquires_source_aligned_safe_candidates():
    anchor = np.array([1.2274432561, 1.4964333762])
    source_direction = np.array([0.9909899820, 0.1339360130])
    source_direction /= np.linalg.norm(source_direction)
    arm = anchor + 0.1147496923 * source_direction
    fill_center = np.array([1.8189935808, 1.7649913445])
    fills = [
        FillAvoidance(
            4,
            1,
            fill_center[0],
            fill_center[1],
            0.6086747487,
        )
    ]
    bounds = OperatingBounds(
        x_min=-0.25,
        x_max=3.75,
        y_min=-0.25,
        y_max=3.75,
        center_x=1.75,
        center_y=1.75,
        wall_margin=0.20,
    )
    config = DirectionConfig(
        lookahead_m=0.50,
        candidate_step_rad=math.pi / 4.0,
    )
    tangent = np.array([
        source_direction[1],
        -source_direction[0],
    ])

    initial = select_source_continuity_direction(
        arm,
        source_direction,
        fills,
        config,
        bounds,
    )
    assert initial is not None
    assert math.degrees(initial.rotation_rad) == pytest.approx(-90.0)
    assert initial.direction == pytest.approx(tangent)

    after_point_two = arm + 0.200 * tangent
    upgraded = select_source_continuity_direction(
        after_point_two,
        source_direction,
        fills,
        config,
        bounds,
    )
    generic = select_safe_direction(
        after_point_two,
        source_direction,
        fills,
        config,
        bounds,
    )
    assert upgraded is not None
    assert generic is not None
    assert math.degrees(upgraded.rotation_rad) == pytest.approx(-45.0)
    assert np.dot(
        upgraded.direction,
        source_direction,
    ) == pytest.approx(math.sqrt(0.5))
    assert math.degrees(generic.rotation_rad) == pytest.approx(-90.0)

    after_point_four_two_five = arm + 0.425 * tangent
    direct = select_source_continuity_direction(
        after_point_four_two_five,
        source_direction,
        fills,
        config,
        bounds,
    )
    generic = select_safe_direction(
        after_point_four_two_five,
        source_direction,
        fills,
        config,
        bounds,
    )
    assert direct is not None
    assert generic is not None
    assert math.degrees(direct.rotation_rad) == pytest.approx(0.0)
    assert np.dot(
        direct.direction,
        source_direction,
    ) == pytest.approx(1.0)
    assert math.degrees(generic.rotation_rad) == pytest.approx(-90.0)


def test_m4_7_projected_source_progress_is_signed_and_exact():
    direction = [3.0, 4.0]
    anchor = [1.0, 2.0]
    unit = np.array(direction) / 5.0

    assert projected_direction_progress(
        anchor,
        np.array(anchor) + 0.20 * unit,
        direction,
    ) == pytest.approx(0.20)
    assert projected_direction_progress(
        anchor,
        np.array(anchor) - 0.05 * unit,
        direction,
    ) == pytest.approx(-0.05)

    with pytest.raises(ValueError, match='two finite values'):
        projected_direction_progress(
            anchor,
            [math.nan, 2.0],
            direction,
        )
    with pytest.raises(ValueError, match='nonzero'):
        projected_direction_progress(anchor, anchor, [0.0, 0.0])


def test_m4_5_retained_repeat_18412_does_not_trigger_source_continuity():
    evidence = source_continuity_evidence(
        [1.611808451194171, 1.7397204167873679],
        [1.450235452155, 1.780275516562],
        [1.0851493296583232, 1.004903555591676],
        minimum_displacement_m=0.05,
        reversal_dot_threshold=-0.90,
    )

    assert evidence is None


def test_source_continuity_requires_finite_meaningful_reversal_geometry():
    assert source_continuity_evidence(
        [0.0, 0.0],
        [0.049, 0.0],
        [1.0, 0.0],
        minimum_displacement_m=0.05,
        reversal_dot_threshold=-0.90,
    ) is None

    with pytest.raises(ValueError, match='two finite values'):
        source_continuity_evidence(
            [0.0, 0.0],
            [math.nan, 0.0],
            [1.0, 0.0],
            minimum_displacement_m=0.05,
            reversal_dot_threshold=-0.90,
        )
    with pytest.raises(ValueError, match='undefined at fill center'):
        source_continuity_evidence(
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 0.0],
            minimum_displacement_m=0.05,
            reversal_dot_threshold=-0.90,
        )
    with pytest.raises(ValueError, match=r'\[-1, 0\)'):
        source_continuity_evidence(
            [0.0, 0.0],
            [1.0, 0.0],
            [2.0, 0.0],
            minimum_displacement_m=0.05,
            reversal_dot_threshold=0.0,
        )


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


def test_m4_4_replays_corner_route_then_selects_quarter_meter_horizon():
    """Resolve the retained M4.3 wall/fill pinch without changing hard safety."""
    route = (
        (0.5504177645, 0.3885305741),
        (0.5389066854, 0.3772497381),
        (0.5419987232, 0.3064148789),
        (0.5724923686, 0.2450582289),
        (0.5854407757, 0.2473396178),
        (0.5987677698, 0.2442260660),
        (0.6045627958, 0.2275838651),
        (0.5628921985, 0.1649199236),
        (0.4843416814, 0.1145440045),
        (0.4114372722, 0.1003166989),
        (0.3169666577, 0.1234985172),
        (0.2990215844, 0.1212317053),
        (0.2860028888, 0.1193869414),
        (0.2727794802, 0.1229529479),
        (0.2628485227, 0.1319624873),
        (0.3052330114, 0.1914447476),
        (0.3863094261, 0.2373509193),
    )
    failure_pose = np.array([0.3963, 0.2401])
    target = np.array([1.75, 1.75])
    fill = FillAvoidance(
        1,
        1,
        0.5447780037,
        0.8569669278,
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
    full_config = DirectionConfig(lookahead_m=0.50)

    fixed = RecenterRoutePlanner()
    adaptive = RecenterRoutePlanner()
    for position in route:
        assert fixed.select(
            position, target, [fill], full_config, bounds
        ) is not None
        assert adaptive.select(
            position, target, [fill], full_config, bounds
        ) is not None
        assert fixed.side == adaptive.side == 1

    assert fixed.select(
        failure_pose,
        target,
        [fill],
        full_config,
        bounds,
    ) is None
    selection = adaptive.select(
        failure_pose,
        target,
        [fill],
        full_config,
        bounds,
        minimum_lookahead_m=0.05,
    )

    assert selection is not None
    assert adaptive.side == 1
    assert adaptive.selected_lookahead_m == pytest.approx(0.25)
    assert evaluate_direction_safety(
        failure_pose,
        selection.direction,
        [fill],
        full_config,
        bounds,
    )[0] is False
    assert evaluate_direction_safety(
        failure_pose,
        selection.direction,
        [fill],
        DirectionConfig(lookahead_m=0.25),
        bounds,
    )[0] is True
    assert bounds.contains_physical(failure_pose)
    assert command_sweep_is_safe(
        failure_pose,
        math.atan2(selection.y, selection.x),
        0.10,
        0.50,
        [fill],
        bounds,
        allow_inward_from_margin=True,
        boundary_trigger_clearance_m=0.025,
    ) is True


def test_adaptive_recenter_horizon_validation_preserves_default_selector():
    planner = RecenterRoutePlanner()
    config = DirectionConfig(lookahead_m=0.50)
    target = [1.0, 0.0]
    expected = planner.select([0.0, 0.0], target, [], config)
    actual = planner.select(
        [0.0, 0.0],
        target,
        [],
        config,
        minimum_lookahead_m=0.50,
    )

    assert actual == expected
    assert planner.selected_lookahead_m == pytest.approx(0.50)
    with pytest.raises(ValueError, match='finite and positive'):
        planner.select(
            [0.0, 0.0],
            target,
            [],
            config,
            minimum_lookahead_m=0.0,
        )
    with pytest.raises(ValueError, match='must not exceed'):
        planner.select(
            [0.0, 0.0],
            target,
            [],
            config,
            minimum_lookahead_m=0.51,
        )


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
