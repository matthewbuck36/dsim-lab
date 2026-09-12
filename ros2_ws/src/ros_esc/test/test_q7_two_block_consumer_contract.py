"""Independent selected-mode binding through stationary and moving consumers."""

from copy import deepcopy
from types import SimpleNamespace

import pytest
import rclpy
from rclpy.serialization import deserialize_message, serialize_message
from rclpy.time import Time

from ros_esc.experiment_recording.stationary_centroid_validation import (
    stationary_centroid_stream_errors,
)
from ros_esc.experiment_recording.v2_lifecycle_validation import lifecycle_stream_errors, TOPICS
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from ros_esc.stationary_fill_protocol import (
    centroid_configuration_errors, stationary_centroid_selected, stationary_request_errors,
)
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.state_machine import State, SupervisorStateMachine
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor
from ros_esc_interfaces.msg import Timekeeper

import test_q5_stationary_centroid_adapter as stationary
import test_q5_stationary_fill_protocol as protocol
import test_q5_stationary_recording_contract as recording
import test_v2_lifecycle_recording as lifecycle
import test_v2_supervisor as moving


MODES = ('centroid_windows_v2', 'centroid_two_block_v2')


def request(mode):
    msg = protocol.request()
    diag = msg.confirmation
    diag.metric_mode = mode
    # Both methods pass epsilon=.06 but have independently different scores:
    # five adjacent shifts .020 m versus two-block displacement .004/3 m.
    diag.centroid_x_m = [1., 1.004, 1., 1.004, 1., 1.004]
    diag.centroid_y_m = [2.]*6
    diag.displacement_m = [.004]*5
    diag.center_x_m, diag.center_y_m = 1.002, 2.
    diag.score_m = .02 if mode == MODES[0] else .004/3
    diag.confinement_radius_m = .01
    return protocol.rehash(msg)


@pytest.mark.parametrize('mode', MODES)
def test_stationary_roundtrip_selects_exact_formula_and_historical_helper_remains_unbound(mode):
    message = request(mode)
    assert protocol.errors(message) == []
    wire = deserialize_message(serialize_message(message), type(message))
    assert protocol.errors(wire, expected_metric_mode=mode) == []
    other = next(value for value in MODES if value != mode)
    assert protocol.errors(wire, expected_metric_mode=other)
    assert centroid_configuration_errors(wire.confirmation, 3., .06, .5,
                                        expected_metric_mode=other)
    assert centroid_configuration_errors(wire.confirmation, 3., .06, .5) == []


@pytest.mark.parametrize('mode', MODES)
def test_request_rehash_cannot_hide_formula_or_metric_substitution(mode):
    message = request(mode)
    other = next(value for value in MODES if value != mode)
    message.confirmation.score_m = .02 if other == MODES[0] else .004/3
    assert protocol.errors(protocol.rehash(message), expected_metric_mode=mode)
    message = request(other)  # Correct score under the unselected identity.
    assert protocol.errors(message) == []
    assert protocol.errors(message, expected_metric_mode=mode)


@pytest.mark.parametrize('mode', MODES)
def test_stationary_selection_preserves_legacy_and_simulation_only_boundary(mode):
    assert stationary_centroid_selected(mode, 'stationary_v1', 'robust_gaussian_v1', True)
    assert not stationary_centroid_selected(mode, 'rolling_gesc_v2', 'robust_gaussian_v1', True)
    assert not stationary_centroid_selected('pde_mean_v1', 'stationary_v1', 'robust_gaussian_v1', True)
    with pytest.raises(ValueError):
        stationary_centroid_selected(mode, 'stationary_v1', 'robust_gaussian_v1', False)
    with pytest.raises(ValueError):
        stationary_centroid_selected(mode, 'stationary_v1', 'legacy', True)


@pytest.mark.parametrize('bad', ['', 'centroid_two_block', 'pde_mean_v2'])
def test_unknown_metric_is_rejected_by_selection_and_request(bad):
    with pytest.raises(ValueError):
        stationary_centroid_selected(bad, 'stationary_v1', 'robust_gaussian_v1', True)
    msg = request(MODES[1]); msg.confirmation.metric_mode = bad
    assert protocol.errors(protocol.rehash(msg))


@pytest.mark.parametrize('mode', MODES)
def test_recorded_stationary_request_binds_selection_even_with_self_consistent_rehash(mode):
    msg = request(mode)
    selected = recording.config(); selected['metric_mode'] = mode
    errors, metrics = stationary_centroid_stream_errors(recording.stream(msg), selected)
    assert errors == [] and metrics['counts']['unique_requests'] == 1
    selected['metric_mode'] = next(value for value in MODES if value != mode)
    errors, metrics = stationary_centroid_stream_errors(recording.stream(msg), selected)
    assert errors and metrics['counts']['unique_requests'] == 0


@pytest.mark.parametrize('mode', MODES)
def test_moving_recording_binds_confirmation_diagnostic_and_snapshot_metric(mode):
    data = lifecycle.fixture(mode)
    errors, metrics = lifecycle_stream_errors(data[0], data[1], metric_mode=mode)
    assert errors == [] and metrics['counts']['unique_commits'] == 1
    other = next(value for value in MODES if value != mode)
    assert lifecycle_stream_errors(data[0], data[1], metric_mode=other)[0]
    poisoned = deepcopy(data)
    poisoned[0][TOPICS['centroid_convergence_diagnostics']][0][1].metric_mode = other
    errors, _ = lifecycle_stream_errors(poisoned[0], poisoned[1], metric_mode=mode)
    assert any('matching diagnostic support' in error for error in errors)
    # No selected-metric argument retains the old API, but empty wire identity
    # never becomes a valid named method by implication.
    poisoned[0][TOPICS['centroid_convergence_diagnostics']][0][1].metric_mode = ''
    assert lifecycle_stream_errors(poisoned[0], poisoned[1])[0]


@pytest.fixture(params=MODES)
def actual_stationary_owners(request):
    mode = request.param
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'continuous_search_mode:=stationary_v1',
        '-p', 'convergence_metric_mode:='+mode, '-p', 'pose_topic:=/selected/odom',
        '-p', 'operating_bounds_enabled:=false', '-p', 'recenter_after_escape:=false'])
    nodes = []
    try:
        supervisor = SupervisorNode(); nodes.append(supervisor)
        gaussian = GaussianFill(); nodes.append(gaussian)
        now = protocol.ORIGIN_NS+19_000_000_000
        for node in nodes:
            node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now))
        supervisor.machine = SupervisorStateMachine(
            now_sec=protocol.ORIGIN_NS*1e-9, config=supervisor.machine.config)
        supervisor.stationary_centroid.timekeeper(Timekeeper(mode='sim time', start_time=1000.))
        gaussian.stationary_fill.set_timekeeper(Timekeeper(mode='sim time', start_time=1000.))
        stationary.heartbeat(supervisor)
        yield mode, supervisor, gaussian
    finally:
        for node in reversed(nodes): node.destroy_node()
        rclpy.try_shutdown()


def test_actual_stationary_owners_reject_other_metric_without_consuming_candidate(actual_stationary_owners):
    mode, supervisor, gaussian = actual_stationary_owners
    adapter = supervisor.stationary_centroid
    other = next(value for value in MODES if value != mode)
    bad = request(other); bad.confirmation.run_id = supervisor.run_id
    protocol.rehash(bad)
    adapter.confirmation(bad.confirmation)
    assert adapter.accepted is None and not adapter.confirmations
    assert gaussian.stationary_fill._errors(bad)
    good = request(mode); good.confirmation.run_id = supervisor.run_id
    protocol.rehash(good)
    assert gaussian.stationary_fill._errors(good) == []
    adapter.confirmation(good.confirmation)
    assert adapter.accepted is not None, adapter.last_reason
    assert adapter.accepted.message.metric_mode == mode
    assert supervisor.machine.state == State.SEARCH


@pytest.mark.parametrize('mode', (*MODES, 'pde_mean_v1'))
def test_moving_live_selection_rejects_other_identity_before_allocating_epoch(mode, monkeypatch):
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns',
                        lambda: 1_000_000_000)
    node = moving.Node()
    values = dict(convergence_metric_mode=mode, recording_ready_required=True,
                  recording_ready_stale_sec=.5, recording_ready_topic='/ready',
                  v2_direction_diagnostics_topic='/direction')
    node.get_parameter = lambda name: SimpleNamespace(value=values[name])
    owner = MovingSupervisor(node, moving.config(), .5, .1); node.adapter = owner
    owner.timekeeper(Timekeeper(mode='sim time', start_time=0.))
    moving.stream(owner)
    other = MODES[1] if mode != MODES[1] else MODES[0]
    wrong = moving.confirm(owner, other)
    wrong.history_kind = 'centroid_windows'
    owner.confirmation(wrong)
    assert owner.candidate is None and owner.accepted_epoch is None
    correct = deepcopy(wrong); correct.metric_mode = mode
    if mode == 'pde_mean_v1': correct.history_kind = 'pde_input_support'
    owner.confirmation(correct)
    assert owner.candidate is not None
    assert owner.candidate.confirmation.metric_mode == mode
    assert owner.candidate.deadline_ns-owner.candidate.accepted_ns == 12_000_000_000
