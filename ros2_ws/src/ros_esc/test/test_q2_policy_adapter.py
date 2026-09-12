"""Q2 selector, exact paired wire receipts and state-authorized fallback checks.

These use the actual Humble frontend, generated messages and existing numerical
owner, with detached publishers. They do not launch a simulator or motion node.
"""

from copy import deepcopy
from dataclasses import replace
import json
import math
import sys
from types import SimpleNamespace

import pytest
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.config_parsing import parse_filter_config
from ros_esc.filter_node.filter_node_script import CustomFilter, parse_filter_arguments
from ros_esc.filter_node.rolling_gesc import RollingResult
from ros_esc.filter_node.v2_runtime import RollingFilterAdapter, policy_diagnostic_message
from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC,
    policy_config_sha256, policy_descriptor,
)
from ros_esc.v2_stream import canonical_json, time_to_ns
from ros_esc_interfaces.msg import AlgorithmState, GescDirectionPolicyDiagnostics, Timekeeper

from test_q1_launch_frontend import _commands, parsed_launch  # noqa: F401
from test_rolling_gesc import feed, ns, pose, times
from test_v2_runtime import CONFIG, FILTER, FakeNode, Publisher, make_state, messages, support


CLI = ['/test/augmented', '/test/encoder', '/test/timekeeper', '/test/output']
SELECTED = ['--continuous-search-mode', 'rolling_gesc_v2',
            '--algorithm_profile', 'robust_gaussian_v1', '--use-sim-time', 'true']


def make_policy_filter(policy):
    node = FakeNode()
    node.algorithm_profile, node.combine_data, node.enable_observability = 'robust_gaussian_v1', True, True
    node.custom_filter, node.z_vec = parse_filter_config(json.loads(FILTER.read_text()), [])
    node.filter_publisher = Publisher()
    node.publish_gesc_diagnostics = lambda *args, **kwargs: None
    args = SimpleNamespace(
        v2_run_id='test-v2', continuous_search_mode='rolling_gesc_v2',
        v2_direction_policy=policy, v2_stream_config_json=canonical_json(CONFIG), use_sim_time=True,
        json_config=str(FILTER), inp_value_topic=CONFIG['augmented_cost_topic'],
        inp_encoder_topic=CONFIG['encoder_topic'], inp_timekeeping_topic=CONFIG['timekeeper_topic'],
        v2_direction_diagnostics_topic='/test/direction', algorithm_state_topic='/test/state')
    adapter = RollingFilterAdapter(node, args)
    adapter.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    return node, adapter


def assert_pair(direction, companion, policy):
    for name in ('stamp', 'time_origin', 'run_id', 'stream_contract_id', 'frame_id',
                 'diagnostic_sequence', 'reset_sequence', 'reset_reason',
                 'objective_revision', 'objective_sha256', 'registry_digest', 'affine_revision',
                 'output_units', 'rolling_start', 'rolling_end', 'mean_full', 'coverage_valid',
                 'output_valid', 'fallback_used', 'blend_allowed', 'fallback_reason'):
        assert getattr(companion, name) == getattr(direction, name), name
    for name in ('source_sequence', 'observation_id', 'source_stamp', 'cost_source_stamp'):
        assert getattr(companion, name) == getattr(direction.observation, name), name
    assert companion.source_schema_version == direction.schema_version
    assert companion.policy_schema_version == 1
    assert companion.direction_policy == policy
    assert companion.policy_config_sha256 == policy_config_sha256(policy)
    assert companion.configured_mean_weight == policy_descriptor(policy)['configured_mean_weight']
    assert companion.actual_blend_weight == direction.blend_weight
    assert companion.selected_policy_qualified == direction.qualified


def test_cli_default_preserves_legacy_and_new_selection_is_explicit():
    default = parse_filter_arguments(CLI)
    assert default.v2_direction_policy == THREE_CYCLE_POLICY
    assert default.continuous_search_mode == 'stationary_v1'
    selected = parse_filter_arguments(CLI+SELECTED+['--v2-direction-policy', MOVING_CYCLE_POLICY])
    assert selected.v2_direction_policy == MOVING_CYCLE_POLICY


@pytest.mark.parametrize('selection', [
    [], ['--algorithm_profile', 'robust_gaussian_v1'],
    ['--continuous-search-mode', 'rolling_gesc_v2'],
    SELECTED+['--use-sim-time', 'false'],
])
def test_new_policy_incompatible_mode_rejected_before_any_node(monkeypatch, selection):
    from rclpy.node import Node

    monkeypatch.setattr(Node, '__init__', lambda *a, **kw: pytest.fail('ROS node created before refusal'))
    monkeypatch.setattr(sys, 'argv', ['filter_node']+CLI+selection+['--v2-direction-policy', MOVING_CYCLE_POLICY])
    with pytest.raises(ValueError):
        CustomFilter()


def test_unknown_policy_is_not_silently_defaulted():
    with pytest.raises(SystemExit) as error:
        parse_filter_arguments(CLI+SELECTED+['--v2-direction-policy', 'moving_cycle'])
    assert error.value.code == 2


@pytest.mark.parametrize('policy', [None, THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
def test_humble_frontend_routes_selector_to_both_filter_branches(parsed_launch, policy):
    overrides = {} if policy is None else {'v2_direction_policy': policy}
    if policy == MOVING_CYCLE_POLICY:
        overrides.update(continuous_search_mode='rolling_gesc_v2', algorithm_profile='robust_gaussian_v1')
    context, commands = _commands(parsed_launch, overrides)
    expected = THREE_CYCLE_POLICY if policy is None else policy
    assert context.launch_configurations['v2_direction_policy'] == expected
    filters = [argv for argv in commands if argv[3] == 'filter_node']
    assert len(filters) == 2
    for argv in filters:
        assert [item for item in argv if item.startswith('--v2-direction-policy=')] == [
            '--v2-direction-policy='+expected]
        assert parse_filter_arguments(argv[4:]).v2_direction_policy == expected


@pytest.mark.parametrize('policy', [THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
def test_adapter_threads_policy_and_pairs_startup_admitted_and_repeated_receipts(policy):
    node, adapter = make_policy_filter(policy)
    assert adapter.rolling.config.direction_policy == policy
    assert node.publishers[POLICY_DIAGNOSTICS_TOPIC] is adapter.policy_publisher
    adapter.publish_diagnostics(adapter.rolling.evaluate(0, math.nan, 0))
    support(node, adapter, ns(1))
    for name, wire in messages().items():
        getattr(adapter, 'add_'+name)(wire)
    assert len(node.filter_publisher.messages) == 1
    first = deepcopy(adapter.publisher.messages[-1])
    assert first.observation.observation_id > 0 and first.output_valid
    # Same source support, later publication. No new numerical integration or
    # observation is performed by a timer status publication.
    node.now_ns += 1_000_000
    adapter.poll()
    assert len(adapter.publisher.messages) == len(adapter.policy_publisher.messages) == 3
    for direction, companion in zip(adapter.publisher.messages, adapter.policy_publisher.messages):
        assert_pair(direction, companion, policy)
        restored = deserialize_message(serialize_message(companion), GescDirectionPolicyDiagnostics)
        assert_pair(direction, restored, policy)
    last = adapter.publisher.messages[-1]
    assert last.observation.observation_id == first.observation.observation_id
    assert time_to_ns(last.stamp) > time_to_ns(first.stamp)
    assert last.diagnostic_sequence == first.diagnostic_sequence+1
    assert len(node.filter_publisher.messages) == 1


def test_companion_retains_selected_gate_and_numerical_interval_without_relabeling_old_control():
    node, adapter = make_policy_filter(MOVING_CYCLE_POLICY)
    feed(adapter.rolling, times(12), vector=lambda t: (math.cos(.4*t), math.sin(.4*t)))
    result = adapter.rolling.evaluate(ns(12), .3, ns(12))
    assert result.qualified and not result.cycles_valid
    node.now_ns = ns(12)
    adapter.state, adapter.state_receipt_ns = make_state(node.now_ns), node.now_ns
    adapter.publish_diagnostics(result)
    direction, companion = adapter.publisher.messages[-1], adapter.policy_publisher.messages[-1]
    assert_pair(direction, companion, MOVING_CYCLE_POLICY)
    assert direction.qualified and not direction.cycles_valid
    assert companion.warmup_valid and companion.coherence_available
    assert companion.actual_blend_weight == .75
    assert companion.coherence_threshold == .25
    for name in ('norm_denominator', 'norm_error', 'coherence', 'coherence_lower', 'coherence_upper',
                 'norm_new_evaluations', 'norm_window_evaluations'):
        assert getattr(companion, name) == getattr(result, name)
    assert companion.numerator_margin == pytest.approx(math.sqrt(2)*(1e-10+1e-8*result.mean_magnitude))
    assert companion.numerical_reason == result.coherence_reason
    detached = policy_diagnostic_message(direction, result, MOVING_CYCLE_POLICY)
    direction.stamp.sec += 2
    direction.observation.source_stamp.sec += 3
    assert detached.stamp != direction.stamp
    assert detached.source_stamp != direction.observation.source_stamp


@pytest.mark.parametrize('policy', [THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
def test_unavailable_receipt_retains_explicit_nan_and_reason(policy):
    _, adapter = make_policy_filter(policy)
    adapter.publish_diagnostics(adapter.rolling.invalidate('synthetic_source_reset'))
    direction, companion = adapter.publisher.messages[-1], adapter.policy_publisher.messages[-1]
    assert_pair(direction, companion, policy)
    assert not companion.output_valid and not companion.coherence_available
    for name in ('norm_denominator', 'norm_error', 'numerator_margin', 'coherence', 'coherence_lower', 'coherence_upper'):
        assert math.isnan(getattr(companion, name))
    assert companion.numerical_reason == ('synthetic_source_reset' if policy == MOVING_CYCLE_POLICY else 'not_selected')


@pytest.mark.parametrize('state', [AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM,
                                  AlgorithmState.STATE_DESIGN_OR_MERGE_FILL])
def test_moving_states_keep_informative_mixture_with_zero_instant(state):
    node, adapter = make_policy_filter(MOVING_CYCLE_POLICY)
    feed(adapter.rolling, times(10), vector=lambda t: (1., 0.))
    feed(adapter.rolling, [10.025], vector=lambda t: (0., 0.))
    node.now_ns = ns(10.025)
    adapter.state, adapter.state_receipt_ns = make_state(node.now_ns, state), node.now_ns
    adapter.latest_pose = pose(10.025, yaw=.3)
    result = adapter._output_result(node.now_ns)
    assert result.output_valid and result.actual_blend_weight == .75
    assert not result.fallback_used and result.instantaneous_magnitude == 0.


@pytest.mark.parametrize('policy', [THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
@pytest.mark.parametrize('instant', [(0., 0.), (1e-6, 0.), (2., 1.)])
def test_nonmoving_state_preserves_instant_objective_and_new_weak_fallback_rule(monkeypatch, policy, instant):
    node, adapter = make_policy_filter(policy)
    node.now_ns = ns(1)
    adapter.state = make_state(node.now_ns, AlgorithmState.STATE_ESCAPE_REPULSE)
    adapter.state_receipt_ns = node.now_ns
    adapter.latest_pose = pose(1., yaw=.3)
    result = RollingResult(instant_world=instant, mean_world=(2., 0.), final_body=(1., 0.),
                          final_magnitude=1., output_valid=True, qualified=True,
                          actual_blend_weight=.75 if policy == MOVING_CYCLE_POLICY else .5)
    monkeypatch.setattr(adapter.rolling, 'evaluate', lambda *args: result)
    actual = adapter._output_result(node.now_ns)
    assert actual.actual_blend_weight == 0.
    if policy == MOVING_CYCLE_POLICY and math.hypot(*instant) <= 1e-6:
        assert not actual.output_valid and not actual.fallback_used and actual.final_body is None
        assert actual.fallback_reason == 'state_instantaneous_direction_weak'
    else:
        assert actual.output_valid and actual.fallback_used
        assert actual.final_body == pytest.approx((math.cos(.3)*instant[0]+math.sin(.3)*instant[1],
                                                   -math.sin(.3)*instant[0]+math.cos(.3)*instant[1]))
        assert actual.fallback_reason == 'state_preserves_instantaneous_objective'


@pytest.mark.parametrize('fault', ['state', 'pose'])
def test_state_or_pose_expiry_cannot_turn_qualified_mean_into_fresh_output(monkeypatch, fault):
    node, adapter = make_policy_filter(MOVING_CYCLE_POLICY)
    node.now_ns = ns(1)
    adapter.state, adapter.state_receipt_ns = make_state(node.now_ns), node.now_ns
    adapter.latest_pose = pose(1.)
    if fault == 'state':
        adapter.state_receipt_ns = ns(.499)
    else:
        adapter.latest_pose = replace(adapter.latest_pose, receipt_ns=ns(.499))
    result = RollingResult(instant_world=(1., 0.), mean_world=(2., 0.), final_body=(1.75, 0.),
                          final_magnitude=1.75, output_valid=True, qualified=True, actual_blend_weight=.75)
    monkeypatch.setattr(adapter.rolling, 'evaluate', lambda *args: result)
    actual = adapter._output_result(node.now_ns)
    assert not actual.output_valid and actual.final_body is None
    assert actual.actual_blend_weight == 0. and actual.fallback_reason == 'stale_state_or_pose'
