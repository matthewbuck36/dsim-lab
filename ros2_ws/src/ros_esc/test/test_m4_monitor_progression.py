"""D2 callback schedules using generated messages; no ROS context or process starts.

The existing monitor owns every verdict and deadline. The fake executor only
delivers a finite declared callback order, including late cross-topic companions.
"""

from copy import deepcopy
import math

import pytest
from nav_msgs.msg import Odometry
from rclpy.serialization import deserialize_message, serialize_message
from rosidl_runtime_py.convert import message_to_ordereddict
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState
from ros_esc.v2_lifecycle import hash_payload
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc.scenario_runner import run_scenario as runner

import test_m4_centroid_event_evaluation as centroid
import test_scenario_runner as inherited


STATE = '/gesc_gaussian/algorithm_state'
EVENT = '/gesc_gaussian/algorithm_events'
FILL = '/gesc_gaussian/gaussian_fills'
LEGACY_KEYS = {
    'return_code', 'timed_out', 'stdout', 'session_id', 'graceful_boundary_stop',
    'boundary_anchor_state', 'boundary_state', 'boundary_observed',
    'boundary_required_events', 'boundary_required_events_observed',
    'graceful_stage_a_timeout_stop', 'graceful_global_proximity_stop',
    'graceful_post_stage_a_timeout_stop', 'stage_a_observed_live',
    'fill_cardinality_observed_live', 'stage_a_monitor_started_sim_sec_live',
    'stage_a_latest_sim_sec_live', 'stage_a_timeout_sample_live',
    'global_proximity_observed_live', 'global_proximity_sample_live',
    'post_stage_a_started_sim_sec_live', 'post_stage_a_latest_sim_sec_live',
    'post_stage_a_timeout_sample_live', 'staged_monitor_error',
    'controller_ranked_goal_observed_live', 'controller_ranked_goal_evidence_live',
    'global_approach_observed_live', 'global_approach_sample_live',
    'global_closer_observed_live', 'global_closer_sample_live',
}


def wire_identity(message):
    """Hash every declared field, retaining the D1 nonfinite value tags.

    Repeated CDR allocations may differ in padding; their raw bytes are not a
    canonical message identity. Do not collapse NaN and infinities into null.
    """
    def tagged(value):
        if isinstance(value, float) and not math.isfinite(value):
            return {'__nonfinite_float__': 'NaN' if math.isnan(value) else
                    ('Infinity' if value > 0 else '-Infinity')}
        if isinstance(value, dict):
            return {key: tagged(item) for key, item in value.items()}
        if isinstance(value, (tuple, list)):
            return [tagged(item) for item in value]
        return value
    return hash_payload(tagged(message_to_ordereddict(message)))


def data(arm='B', *, ranked=False):
    values = centroid.fixture(arm)
    resolved, states, events, _, _, _ = values
    resolved['schema_version'] = 7
    resolved['success']['staged_recovery'].update(
        stage_a_timeout_sec=360., post_stage_a_timeout_sec=300.,
        global_approach_radius_m=1.2, global_closer_radius_m=.8)
    if ranked:
        resolved['algorithm']['launch_overrides'].update(
            extremum_classification_mode='counted_candidates', known_source_count=2)
        states[:] = [(n, m) for n, m in states if m.state != AlgorithmState.STATE_RECENTER]
        events[:] = [(n, m) for n, m in events if m.event_type not in (
            AlgorithmEvent.EVENT_RECENTER_STARTED, AlgorithmEvent.EVENT_RECENTER_COMPLETE)]
    return values


def odom(stamp, *, goal=False):
    message = Odometry()
    set_time(message.header.stamp, round(stamp*1_000_000_000))
    message.pose.pose.position.x = message.pose.pose.position.y = 3.5 if goal else 2.
    message.pose.pose.orientation.w = 1.
    return '/odom', message


def recovered(values):
    resolved, states, events, fills, diagnostics, origins = values
    selected = runner._m4_centroid_event_selection(resolved)
    sequence = [odom(0.)]
    if selected is not None:
        sequence += [(selected['timekeeper_topic'], origins[0][1]),
                     (selected['diagnostic_topic'], diagnostics[0][1])]
    sequence += [(topic, message) for _, topic, message in sorted(
        [(n, topic, message) for topic, rows in ((STATE, states), (EVENT, events), (FILL, fills))
         for n, message in rows], key=lambda row: row[0])]
    return sequence


def next_pair(values, order='event_first'):
    diagnostic = deepcopy(values[4][0][1])
    diagnostic.search_epoch += 1
    diagnostic.confirmation_sequence += 1
    for stamp in [getattr(diagnostic, name) for name in (
            'stamp', 'receipt_stamp', 'source_stamp', 'history_start', 'history_end')
            ] + list(diagnostic.window_start) + list(diagnostic.window_end):
        set_time(stamp, time_to_ns(stamp)+330_000_000_000)
    event = deepcopy(values[2][0][1])
    set_time(event.stamp, time_to_ns(diagnostic.stamp)+100_000_000)
    event.values = [diagnostic.score_m, diagnostic.confinement_radius_m,
                    diagnostic.center_x_m, diagnostic.center_y_m,
                    float(diagnostic.search_epoch), float(diagnostic.confirmation_sequence)]
    topic = runner._m4_centroid_event_selection(values[0])['diagnostic_topic']
    pair = [(EVENT, event), (topic, diagnostic)]
    return pair if order == 'event_first' else pair[::-1]


def ranked_goal():
    message = AlgorithmEvent()
    message.event_type = AlgorithmEvent.EVENT_GOAL_REACHED
    message.detail = 'candidate is strictly lower than every filled candidate'
    message.value_names = ['candidate_raw_cost_upper', 'candidate_ordinal',
        'filled_candidate_count', 'known_source_count',
        'comparison_filled_raw_cost_lower', 'candidate_strict_separation_margin']
    message.values = [-2., 2., 1., 2., -1., 1.]
    return EVENT, message


def run_callbacks(monkeypatch, resolved, schedule):
    callbacks, delivered, signals, lifecycle = {}, [], [], []
    remaining = list(schedule)
    context = object()

    class Node:
        def create_subscription(self, kind, topic, callback, depth):
            del kind, depth
            callbacks[topic] = callback
        def destroy_node(self):
            lifecycle.append('node_destroyed')

    class Process:
        def __init__(self, command, stdout, **kwargs):
            assert command == ['record'] and kwargs['start_new_session']
            self.pid, self.returncode = 7321, None
            stdout.write('finite D2 callback fixture\n')
        def poll(self):
            return self.returncode
        def wait(self, timeout=None):
            assert timeout is None or timeout > 0
            self.returncode = 0
            return 0

    node = Node()
    def spin(timeout_sec):
        assert 0 < timeout_sec <= .1
        assert remaining, 'monitor did not terminate at the declared finite schedule boundary'
        topic, message = remaining.pop(0)
        delivered.append((topic, message))
        callbacks[topic](message)

    monkeypatch.setattr(runner.rclpy.context, 'Context', lambda: context)
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: lifecycle.append('context_shutdown'))
    monkeypatch.setattr(runner.rclpy, 'create_node', lambda *a, **k: node)
    inherited._install_boundary_executor(monkeypatch, context, node, spin, lifecycle)
    monkeypatch.setattr(runner.subprocess, 'Popen', Process)
    monkeypatch.setattr(runner.os, 'killpg', lambda pid, sig: signals.append((pid, sig)))
    original = [(topic, message, wire_identity(message)) for topic, message in schedule]
    public_events = [(message, serialize_message(message), message.source_timestamp_valid,
                      float(message.source_timestamp).hex())
                     for _, message in schedule if isinstance(message, AlgorithmEvent)]
    result = runner._run_record_to_global_proximity(['record'], 5., 1., resolved)
    assert signals == [(7321, runner.signal.SIGINT)]
    assert lifecycle == ['created', 'added', 'removed', 'shutdown', 'node_destroyed', 'context_shutdown']
    for ordinal, (topic, message, expected) in enumerate(original):
        assert wire_identity(message) == expected, (ordinal, topic, 'message fields changed')
    for message, blob, source_valid, source_value in public_events:
        assert message.source_timestamp_valid is source_valid
        assert float(message.source_timestamp).hex() == source_value
        assert wire_identity(deserialize_message(blob, AlgorithmEvent)) == wire_identity(message)
    return result, remaining, delivered


def assert_original_b_timeout(result, *, started=100.):
    assert result['graceful_stage_a_timeout_stop'] is False
    assert result['stage_a_timeout_sample_live'] is None
    assert result['stage_a_monitor_started_sim_sec_live'] == 0.
    assert result['post_stage_a_started_sim_sec_live'] == started
    assert result['post_stage_a_latest_sim_sec_live'] == started+300.
    assert result['graceful_post_stage_a_timeout_stop'] is True
    assert result['post_stage_a_timeout_sample_live']['elapsed_sim_sec'] == 300.
    assert result['post_stage_a_timeout_sample_live']['timeout_sec'] == 300.
    proof = result['stage_a_completion_evidence_live']
    assert proof['completed_episode_count'] == 1
    assert proof['created_cluster_ids'] == [42]
    assert proof['stage_a_completion_stamp'] is not None


@pytest.mark.parametrize('arm', ['B', 'D'])
@pytest.mark.parametrize('order', ['event_first', 'diagnostic_first'])
def test_later_pair_cannot_restart_completed_stage_a_or_extend_stage_b(monkeypatch, arm, order):
    values = data(arm)
    first, second = next_pair(values, order)
    schedule = recovered(values)+[odom(100.), first, odom(368.), second, odom(399.), odom(400.)]
    result, remaining, _ = run_callbacks(monkeypatch, values[0], schedule)
    assert not remaining
    assert_original_b_timeout(result)
    assert result['stage_a_observed_live'] and result['fill_cardinality_observed_live']
    assert result['staged_monitor_error'] is None
    assert len(result['centroid_event_timestamp_bindings_live']) == 2


@pytest.mark.parametrize('arm', ['B', 'D'])
@pytest.mark.parametrize('order', ['event_first', 'diagnostic_first'])
def test_permanently_missing_pair_consumes_original_b_allowance_and_stays_invalid(monkeypatch, arm, order):
    values = data(arm)
    first, _ = next_pair(values, order)
    result, remaining, _ = run_callbacks(monkeypatch, values[0],
        recovered(values)+[odom(100.), first, odom(368.), odom(400.)])
    assert not remaining
    assert_original_b_timeout(result)
    assert not result['stage_a_observed_live'] and not result['fill_cardinality_observed_live']
    assert result['staged_monitor_error']
    assert not result['global_proximity_observed_live']


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_pending_before_first_b_odometry_still_starts_the_completed_phase_once(monkeypatch, arm):
    values = data(arm)
    first, second = next_pair(values)
    result, remaining, _ = run_callbacks(monkeypatch, values[0],
        recovered(values)+[first, odom(368.), second, odom(667.), odom(668.)])
    assert not remaining
    assert_original_b_timeout(result, started=368.)
    assert result['stage_a_latest_sim_sec_live'] == 368.


@pytest.mark.parametrize('arm', ['B', 'D'])
@pytest.mark.parametrize('eventually_complete', [False, True])
def test_ranked_goal_and_near_pose_during_pending_do_not_authorize_early_acceptance(monkeypatch, arm, eventually_complete):
    values = data(arm, ranked=True)
    first, second = next_pair(values)
    schedule = recovered(values)+[odom(100.), first, ranked_goal(), odom(368., goal=True)]
    if eventually_complete:
        # The old pose cannot be accepted retroactively when its companion arrives.
        schedule += [second, odom(369.), odom(400., goal=True)]
    else:
        schedule += [odom(400., goal=True)]
    result, remaining, _ = run_callbacks(monkeypatch, values[0], schedule)
    assert not remaining
    assert result['controller_ranked_goal_observed_live']  # Recorded claim, not goal acceptance.
    assert result['post_stage_a_started_sim_sec_live'] == 100.
    assert not result['graceful_stage_a_timeout_stop']
    assert result['global_proximity_observed_live'] is eventually_complete
    assert result['global_approach_observed_live'] is eventually_complete
    assert result['global_closer_observed_live'] is eventually_complete
    if eventually_complete:
        assert result['global_proximity_sample_live']['sample_sim_sec'] == 400.
        assert result['graceful_global_proximity_stop']
        assert not result['graceful_post_stage_a_timeout_stop']
        assert result['staged_monitor_error'] is None
    else:
        assert_original_b_timeout(result)
        assert result['global_approach_sample_live'] is None
        assert result['global_closer_sample_live'] is None
        assert result['staged_monitor_error']


@pytest.mark.parametrize('goal', [False, True])
def test_complete_evidence_at_exact_b_deadline_preserves_proximity_precedence(monkeypatch, goal):
    values = data()
    result, remaining, _ = run_callbacks(monkeypatch, values[0],
        recovered(values)+[odom(100.), odom(400., goal=goal)])
    assert not remaining
    assert result['post_stage_a_started_sim_sec_live'] == 100.
    assert result['graceful_global_proximity_stop'] is goal
    assert result['graceful_post_stage_a_timeout_stop'] is not goal


@pytest.mark.parametrize('fault', ['diagnostic_conflict', 'event_conflict', 'publication_500ms_plus_1ns'])
def test_later_contradiction_never_hides_behind_completed_recovery(monkeypatch, fault):
    values = data('D')
    event, diagnostic = next_pair(values)
    extra = []
    if fault == 'diagnostic_conflict':
        changed = deepcopy(diagnostic[1]); changed.reset_reason = 'contradiction'
        extra = [(diagnostic[0], changed)]
    elif fault == 'event_conflict':
        changed = deepcopy(event[1]); changed.detail = 'contradiction'
        extra = [(EVENT, changed)]
    else:
        set_time(event[1].stamp, time_to_ns(diagnostic[1].stamp)+500_000_001)
    schedule = recovered(values)+[odom(100.), event, diagnostic]+extra+[odom(368., goal=True), odom(400., goal=True)]
    result, remaining, _ = run_callbacks(monkeypatch, values[0], schedule)
    assert not remaining
    assert_original_b_timeout(result)
    assert not result['stage_a_observed_live']
    assert not result['global_proximity_observed_live']
    assert not result['global_approach_observed_live']
    assert result['staged_monitor_error']


@pytest.mark.parametrize('malformed', [False, True])
def test_later_fill_failure_keeps_current_cardinality_strict_and_historical_proof_safe(monkeypatch, malformed):
    values = data()
    added_fill = deepcopy(values[3][0][1])
    if malformed:
        added_fill.cluster_id += 1  # Same fill ID with a conflicting typed identity.
        extra = [(FILL, added_fill)]
    else:
        added_fill.fill_id, added_fill.cluster_id = 8, 43
        added_fill.source_timestamp += .001
        event = deepcopy(next(m for _, m in values[2] if m.event_type == AlgorithmEvent.EVENT_FILL_CREATED))
        event.fill_id, event.values = 8, [43., 1.]
        event.source_timestamp = added_fill.source_timestamp
        extra = [(FILL, added_fill), (EVENT, event)]
    result, remaining, _ = run_callbacks(monkeypatch, values[0],
        recovered(values)+[odom(100.)]+extra+[odom(368., goal=True), odom(400., goal=True)])
    assert not remaining
    assert_original_b_timeout(result)
    assert not result['fill_cardinality_observed_live']
    assert not result['global_proximity_observed_live']
    assert not result['global_approach_observed_live']
    assert bool(result['staged_monitor_error']) is malformed
    if not malformed:
        # A successful final bag cannot erase the live extra-fill verdict.
        final_valid = classification(values)
        classified = classification(values, live_evidence=result)
        assert final_valid['passed']
        assert not classified['passed']
        assert classified['infrastructure_status'] == 'live_monitor_evidence_failed'
        assert 'cardinality' in classified['infrastructure_reason']
        assert classified['predicate_results'] == final_valid['predicate_results']


def classification(values, *, live_error=None, live_evidence=None,
                   extraction_error=None, complete=True, cleanup=True):
    resolved = values[0]
    outcomes = runner._unavailable_outcomes('synthetic final bag result')
    outcomes.update(readiness_interval_available=True, outcome_error=extraction_error,
        local_recovery_stage_passed=True, fill_cardinality_passed=True,
        post_recovery_global_proximity_passed=True, collision_expectation_passed=True)
    process = dict(timed_out=False, return_code=0, graceful_global_proximity_stop=True,
                   staged_monitor_error=live_error)
    if live_evidence is not None:
        process.update({key: live_evidence[key] for key in (
            'stage_a_completion_evidence_live', 'stage_a_observed_live',
            'fill_cardinality_observed_live', 'staged_monitor_error')})
    return runner.classify_result(resolved, {'passed': complete}, {'passed': cleanup},
        outcomes, process, metadata={}, run_directory_available=True)


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_terminal_live_error_fails_even_when_final_bag_and_all_other_predicates_pass(arm):
    values = data(arm)
    valid = classification(values)
    assert valid['passed'] and valid['infrastructure_status'] == 'completed'
    reason = 'M4 centroid convergence timestamp binding: typed centroid confirmation lacks matching convergence event'
    result = classification(values, live_error=reason)
    assert not result['passed'] and result['infrastructure_status'] != 'completed'
    assert result['infrastructure_reason'] == reason
    assert result['predicate_results'] == valid['predicate_results']


@pytest.mark.parametrize('fault,status', [('extraction', 'evidence_extraction_failed'),
    ('recording', 'recording_evidence_invalid'), ('cleanup', 'cleanup_failed')])
def test_live_error_does_not_mask_existing_failure_priorities(fault, status):
    result = classification(data(), live_error='unresolved live companion',
        extraction_error='recorded contradiction' if fault == 'extraction' else None,
        complete=fault != 'recording', cleanup=fault != 'cleanup')
    assert not result['passed'] and result['infrastructure_status'] == status
    assert result['infrastructure_reason'] != 'unresolved live companion'


def test_nonselected_default_paths_preserve_full_result_shape_and_error_classification(monkeypatch):
    results = []
    for selector in ('historical_suite', 'legacy_metric'):
        values = data()
        for _, event in values[2]:
            if event.event_type == AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED:
                event.source_timestamp, event.source_timestamp_valid = 37., True
        if selector == 'historical_suite':
            values[0]['suite_id'] = 'historical-q5'
        else:
            values[0]['algorithm']['launch_overrides']['convergence_metric_mode'] = 'pde_mean_v1'
        result, remaining, _ = run_callbacks(monkeypatch, values[0],
            recovered(values)+[odom(100.), odom(400., goal=True)])
        assert not remaining and set(result) == LEGACY_KEYS
        assert result['graceful_global_proximity_stop']
        assert classification(values, live_error='historical uninterpreted error')['passed']
        results.append(result)
    assert results[0] == results[1]
