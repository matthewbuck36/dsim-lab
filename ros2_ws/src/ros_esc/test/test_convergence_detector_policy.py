"""Focused robust convergence lifecycle and motion-policy tests."""

import numpy as np
import pytest
import rclpy

from ros_esc.convergence_detector_node.convergence_detector_node_script import (
    CROSSING_COUNT,
    QUALIFIED_DWELL,
    ConvergenceDetector,
    QualifiedDwellPolicy,
    motion_qualified,
    SearchEpochGate,
    trajectory_motion_statistics,
)
from ros_esc_interfaces.msg import AlgorithmState


def _state(value, run_id='run-a', valid=True):
    message = AlgorithmState()
    message.state = value
    message.state_valid = valid
    message.run_id = run_id
    message.run_id_valid = True
    return message


def test_search_epoch_gate_resets_only_on_typed_boundaries_and_new_runs():
    gate = SearchEpochGate(enabled=True)

    assert gate.active is False
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) == gate.ENTERED
    assert gate.active is True
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) is None
    assert gate.update(_state(AlgorithmState.STATE_VERIFY_EXTREMUM)) == gate.LEFT
    assert gate.active is False
    assert gate.update(_state(AlgorithmState.STATE_VERIFY_EXTREMUM)) is None
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) == gate.ENTERED
    assert gate.update(
        _state(AlgorithmState.STATE_SEARCH, run_id='run-b')
    ) == gate.ENTERED


def test_search_epoch_gate_disarms_invalid_state_and_legacy_gate_stays_open():
    gated = SearchEpochGate(enabled=True)
    assert gated.update(_state(AlgorithmState.STATE_SEARCH)) == gated.ENTERED
    assert gated.update(
        _state(AlgorithmState.STATE_SEARCH, valid=False)
    ) == gated.LEFT
    assert gated.active is False

    legacy = SearchEpochGate(enabled=False)
    assert legacy.active is True
    assert legacy.update(_state(AlgorithmState.STATE_FAILSAFE)) is None
    assert legacy.active is True


def test_motion_policy_rejects_translation_and_accepts_compact_orbit():
    translation = np.column_stack(
        (np.linspace(0.0, 0.30, 301), np.zeros(301))
    )
    path, net, efficiency = trajectory_motion_statistics(translation)
    assert path == pytest.approx(0.30)
    assert net == pytest.approx(0.30)
    assert efficiency == pytest.approx(1.0)
    assert not motion_qualified(path, efficiency, 0.20, 0.35)

    angles = np.linspace(0.0, 2.0 * np.pi, 301)
    orbit = np.column_stack((0.15 * np.cos(angles), 0.15 * np.sin(angles)))
    path, net, efficiency = trajectory_motion_statistics(orbit)
    assert path > 0.90
    assert net == pytest.approx(0.0, abs=1e-12)
    assert efficiency == pytest.approx(0.0, abs=1e-12)
    assert motion_qualified(path, efficiency, 0.20, 0.35)


def test_motion_policy_rejects_stationary_and_short_histories():
    stationary = np.zeros((301, 2), dtype=np.float64)
    path, net, efficiency = trajectory_motion_statistics(stationary)
    assert (path, net, efficiency) == (0.0, 0.0, 0.0)
    assert not motion_qualified(path, efficiency, 0.20, 0.35)

    with pytest.raises(ValueError):
        trajectory_motion_statistics(np.zeros((1, 2), dtype=np.float64))


def test_qualified_dwell_accumulates_only_below_entry_and_confirms_once():
    policy = QualifiedDwellPolicy(dwell_sec=2.0, exit_metric=0.5)

    assert policy.update(0.0, -0.1) is False
    assert policy.update(1.0, -0.1) is False
    assert policy.accumulated_sec == pytest.approx(1.0)

    assert policy.update(1.5, 0.1) is False
    assert policy.episode_active is True
    assert policy.accumulated_sec == pytest.approx(1.0)
    assert policy.update(2.0, -0.1) is False
    assert policy.update(3.0, -0.1) is True
    assert policy.confirmed is True
    assert policy.accumulated_sec == pytest.approx(2.0)
    assert policy.update(4.0, -0.1) is False


def test_qualified_dwell_hysteresis_rearms_only_above_exit():
    policy = QualifiedDwellPolicy(dwell_sec=1.0, exit_metric=0.5)
    policy.update(0.0, -0.1)
    assert policy.update(1.0, -0.1) is True

    assert policy.update(2.0, 0.5) is False
    assert policy.confirmed is True
    assert policy.update(3.0, 0.500001) is False
    assert policy.confirmed is False
    assert policy.episode_active is False

    policy.update(4.0, -0.1)
    assert policy.update(5.0, -0.1) is True


def test_qualified_dwell_resets_on_motion_loss_invalidity_and_backward_time():
    policy = QualifiedDwellPolicy(dwell_sec=2.0, exit_metric=0.5)
    policy.update(0.0, -0.1)
    policy.update(1.0, -0.1)
    assert policy.accumulated_sec == pytest.approx(1.0)

    assert policy.update(2.0, -0.1, qualified=False) is False
    assert policy.accumulated_sec == 0.0
    policy.update(3.0, -0.1)
    assert policy.update(4.0, np.nan, valid=False) is False
    assert policy.episode_active is False

    policy.update(5.0, -0.1)
    assert policy.update(4.0, -0.1) is False
    assert policy.accumulated_sec == 0.0
    assert policy.episode_active is True


@pytest.mark.parametrize(
    ("dwell_sec", "exit_metric"),
    [
        (0.0, 0.5),
        (np.nan, 0.5),
        (1.0, 0.0),
        (1.0, np.nan),
    ],
)
def test_qualified_dwell_rejects_invalid_configuration(
    dwell_sec,
    exit_metric,
):
    with pytest.raises(ValueError):
        QualifiedDwellPolicy(dwell_sec, exit_metric)


def test_detector_resets_counter_and_decay_on_typed_search_boundaries():
    rclpy.init(
        args=[
            '--ros-args',
            '-p',
            'algorithm_profile:=robust_gaussian_v1',
            '-p',
            'state_gating_enabled:=true',
        ]
    )
    node = ConvergenceDetector()
    try:
        assert node.confirmation_policy == CROSSING_COUNT
        node.count_remaining = 1
        node.first_time = 10.0
        node.t0 = 11.0
        node.last_metric = -0.1

        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        assert node.search_gate.active is True
        assert node.count_remaining == node.count_start
        assert node.first_time is None
        assert node.t0 is None
        assert node.last_metric is None

        node.first_time = 12.0
        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        assert node.first_time == 12.0

        node.algorithm_state_cb(_state(AlgorithmState.STATE_VERIFY_EXTREMUM))
        assert node.search_gate.active is False
        assert node.first_time is None
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_detector_resets_qualified_dwell_on_search_epoch_boundaries():
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
            "-p",
            "state_gating_enabled:=true",
            "-p",
            f"convergence_confirmation_policy:={QUALIFIED_DWELL}",
            "-p",
            "convergence_confirmation_dwell_sec:=6.0",
            "-p",
            "convergence_confirmation_exit_threshold_scale:=1.5",
        ]
    )
    node = ConvergenceDetector()
    try:
        assert node.confirmation_policy == QUALIFIED_DWELL
        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        node.qualified_dwell_policy.update(10.0, -0.1)
        node.qualified_dwell_policy.update(12.0, -0.1)
        assert node.qualified_dwell_policy.accumulated_sec == pytest.approx(2.0)

        node.algorithm_state_cb(
            _state(AlgorithmState.STATE_VERIFY_EXTREMUM)
        )
        assert node.search_gate.active is False
        assert node.qualified_dwell_policy.accumulated_sec == 0.0
        assert node.qualified_dwell_policy.episode_active is False
    finally:
        node.destroy_node()
        rclpy.shutdown()
