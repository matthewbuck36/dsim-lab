"""Actual transaction and composer owners under independently delivered ROS clocks.

These synthetic callback tests use the existing Gaussian transaction fixture;
they neither start ROS nor substitute the activation/composition owners.
"""
from copy import deepcopy
from types import MethodType, SimpleNamespace

import pytest

from builtin_interfaces.msg import Time
from ros_esc_interfaces.msg import (
    AlgorithmState, CostBreakdown, FillResult, SourceSampleProvenance,
    StampedFloat64MultiArray, Timekeeper,
)
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.modified_cost_node.v2_fill_activation import AtomicFillActivation
from ros_esc.modified_cost_node.v2_objective import V2ObjectiveComposer
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256
from ros_esc.v2_stream import set_time, time_to_ns

from test_v2_fill_transactions import (
    CONTRACT, Node, Publisher, activate, authorize, command, owner, prepare,
)


def committed_result():
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    _, result = activate(runtime, cmd)
    assert result.result == FillResult.ACTIVATED
    assert node.fill_registry.generation == 1
    return result


def actual_composer(now_ns):
    node = Node()
    node.now_ns = now_ns
    node.get_logger = lambda: SimpleNamespace(
        error=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
    )
    # Missing state/sensor input deliberately cannot authorize cost output, but
    # must not prevent reconciliation of an already committed registry result.
    node.algorithm_state = None
    node.v2_composer = V2ObjectiveComposer(node)
    node.v2_fill_activation = AtomicFillActivation(node)
    node.v2_composer.set_timekeeper(Timekeeper(mode='sim time', start_time=0.))
    return node, node.v2_composer, node.v2_fill_activation


def test_valid_commit_100ms_ahead_waits_without_envelope_fault():
    result = committed_result()
    node, composer, activation = actual_composer(
        time_to_ns(result.committed_at) - 100_000_000)

    accepted = activation.accept(result)

    assert accepted, activation.last_fault
    assert activation.fault_count == composer.fault_count == 0
    assert activation.generation == 0 and node.robust_terms == {}
    assert fill_registry_digest(activation.active.values()) == result.registry_digest_before
    assert not composer.publisher.messages and node.affine_syncs == 0


def test_single_delivered_commit_applies_once_on_composer_clock_coverage():
    result = committed_result()
    node, composer, activation = actual_composer(
        time_to_ns(result.committed_at) - 100_000_000)
    activation.accept(result)  # Exactly one delivery; no command/result retry.
    assert activation.generation == 0

    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()

    assert activation.generation == 1, activation.last_fault
    assert set(node.robust_terms) == {result.fill.fill_id}
    assert fill_registry_digest(activation.active.values()) == result.registry_digest_after
    assert node.affine_syncs == 1
    for _ in range(3):
        composer.poll()
    assert activation.generation == 1 and node.affine_syncs == 1
    assert not composer.publisher.messages  # Registry apply alone is not sensor output.


@pytest.mark.parametrize('coverage_delay_ns', [600_000_000, 20_000_000_000])
def test_pending_commit_is_durable_past_sensor_lease_and_preparation_expiry(coverage_delay_ns):
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    assert activation.accept(result)
    for _ in range(4):
        composer.poll()  # Paused ROS clock never grants early coverage.
    assert activation.generation == node.affine_syncs == 0
    node.now_ns += coverage_delay_ns
    composer.poll()
    assert activation.generation == node.affine_syncs == 1
    assert fill_registry_digest(activation.active.values()) == result.registry_digest_after
    assert not activation.last_fault


def test_first_delivery_after_original_preparation_deadline_still_applies_commit():
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.expires_at)+10_000_000_000)
    assert activation.accept(result)
    assert activation.generation == node.affine_syncs == 1
    composer.poll()
    assert activation.generation == node.affine_syncs == 1


@pytest.mark.parametrize('lead_ns, accepted', [(500_000_000, True), (500_000_001, False)])
def test_initial_lead_bound_is_exact_and_is_not_a_commit_ttl(lead_ns, accepted):
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-lead_ns)
    assert activation.accept(result) is accepted
    assert activation.generation == node.affine_syncs == 0
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == int(accepted)
    assert node.affine_syncs == int(accepted)


def test_pending_result_is_detached_and_retry_preserves_first_receipt_and_commit():
    result = committed_result()
    original = deepcopy(result)
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    receipt_ns = node.now_ns
    assert activation.accept(result)
    pending = activation.pending
    assert pending.receipt_ns == receipt_ns
    result.fill.amplitude = 999.
    result.registry_digest_after = 'mutated caller storage'
    retry = deepcopy(original)
    retry.result, retry.command_sequence = FillResult.ALREADY_ACTIVATED, 9
    set_time(retry.stamp, node.now_ns+50_000_000)
    retry.committed_sha256 = result_sha256(retry)
    node.now_ns += 50_000_000
    assert activation.accept(retry)
    assert activation.pending is pending
    assert pending.receipt_ns == receipt_ns
    assert pending.result == original
    node.now_ns = time_to_ns(original.committed_at)
    composer.poll()
    assert node.robust_terms[original.fill.fill_id]['amplitude'] == original.fill.amplitude
    assert activation.generation == node.affine_syncs == 1
    assert activation.accept(retry)
    assert activation.generation == node.affine_syncs == 1


@pytest.mark.parametrize('change', [
    'schema', 'run', 'frame', 'origin', 'contract', 'hash', 'candidate',
    'preparation', 'evidence', 'prepared_hash', 'commit_after_deadline',
    'prepared_after_commit', 'generation', 'expected_generation', 'before_digest',
    'after_digest', 'geometry', 'fill_frame',
])
def test_invalid_future_commit_cannot_become_pending_authority(change):
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    bad = deepcopy(result)
    if change == 'schema': bad.schema_version += 1
    elif change == 'run': bad.run_id = 'wrong-run'
    elif change == 'frame': bad.frame_id = 'map'
    elif change == 'origin': set_time(bad.time_origin, 1)
    elif change == 'contract': bad.stream_contract_id = 'b'*64
    elif change == 'hash': bad.committed_sha256 = 'b'*64
    elif change == 'candidate': bad.candidate_id = 0
    elif change == 'preparation': bad.preparation_id = 0
    elif change == 'evidence': bad.evidence_sha256 = ''
    elif change == 'prepared_hash': bad.prepared_sha256 = ''
    elif change == 'commit_after_deadline': set_time(bad.expires_at, time_to_ns(bad.committed_at)-1)
    elif change == 'prepared_after_commit': set_time(bad.prepared_at, time_to_ns(bad.committed_at)+1)
    elif change == 'generation': bad.registry_generation += 1
    elif change == 'expected_generation': bad.expected_registry_generation += 1
    elif change == 'before_digest': bad.registry_digest_before = 'b'*64
    elif change == 'after_digest': bad.registry_digest_after = 'b'*64
    elif change == 'geometry': bad.fill.covariance_xx = -1.
    elif change == 'fill_frame': bad.fill.frame_id = 'map'
    if change != 'hash': bad.committed_sha256 = result_sha256(bad)
    assert not activation.accept(bad)
    assert activation.pending is None and activation.generation == 0
    assert node.robust_terms == {} and node.affine_syncs == 0
    assert activation.fault_count == 1
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == 0
    # A rejected envelope must not consume the valid next generation.
    assert activation.accept(result)
    assert activation.generation == node.affine_syncs == 1


def test_conflicting_pending_identity_is_rejected_without_replacing_original():
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    assert activation.accept(result)
    pending = activation.pending
    conflict = deepcopy(result)
    conflict.candidate_id += 1
    conflict.committed_sha256 = result_sha256(conflict)
    assert not activation.accept(conflict)
    assert activation.pending is pending and activation.generation == 0
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == 1
    assert fill_registry_digest(activation.active.values()) == result.registry_digest_after
    assert not activation.accept(conflict)
    assert activation.generation == node.affine_syncs == 1


def committed_redesign_pair():
    node, worker, runtime = owner()
    cmd = prepare(node, worker, runtime)
    _, first = activate(runtime, cmd)
    node.now_ns += 100_000_000
    authorize(node, runtime, previous=4)
    redesign = command(3, 2, generation=1, target=(1, 1, 1))
    prepare(node, worker, runtime, redesign, target=(1, 1, 1))
    _, second = activate(runtime, redesign, 4)
    assert second.result == FillResult.ACTIVATED and second.has_superseded_fill
    return first, second


def test_pending_supersession_preserves_old_fill_and_rebuilds_current_affine_swap():
    first, second = committed_redesign_pair()
    node, composer, activation = actual_composer(time_to_ns(first.committed_at))
    assert activation.accept(first)
    node.robust_affine_terms[1] = {'old-target': True}
    assert activation.accept(second)
    assert activation.generation == 1 and set(node.robust_terms) == {1}
    assert fill_registry_digest(activation.active.values()) == first.registry_digest_after
    # A separately owned affine update between receipt and application must not
    # be lost to a stale staged dictionary; its payload is not evaluated here.
    unrelated = {'new-unrelated-update': [1., 2.]}
    node.robust_affine_terms[99] = unrelated
    node.now_ns = time_to_ns(second.committed_at)
    composer.poll()
    assert activation.generation == 2 and set(node.robust_terms) == {2}
    assert node.robust_cluster_fill_ids == {1: 2}
    assert node.robust_affine_terms == {99: unrelated}
    assert fill_registry_digest(activation.active.values()) == second.registry_digest_after
    assert node.affine_syncs == 2


def test_later_generation_cannot_bypass_pending_predecessor():
    first, second = committed_redesign_pair()
    node, composer, activation = actual_composer(time_to_ns(first.committed_at)-100_000_000)
    assert activation.accept(first)
    pending = activation.pending
    assert not activation.accept(second)
    assert activation.pending is pending and activation.generation == 0
    node.now_ns = time_to_ns(second.committed_at)
    composer.poll()
    assert activation.generation == 1
    assert activation.accept(second) and activation.generation == 2


def test_commit_capacity_rejects_new_generation_but_retains_duplicate_identity(monkeypatch):
    import ros_esc.modified_cost_node.v2_fill_activation as module
    first, second = committed_redesign_pair()
    node, composer, activation = actual_composer(time_to_ns(first.committed_at))
    monkeypatch.setattr(module, 'MAX_COMMANDS', 1)
    assert activation.accept(first)
    assert not activation.accept(second)
    assert activation.pending is None and activation.generation == 1
    assert activation.accept(first)
    assert activation.generation == node.affine_syncs == 1


@pytest.mark.parametrize('new_origin', [-1., 1.])
def test_origin_fault_fences_durable_pending_commit(new_origin):
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    assert activation.accept(result)
    composer.set_timekeeper(Timekeeper(mode='sim time', start_time=new_origin))
    assert composer.origin_fault
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == node.affine_syncs == 0
    assert not activation.accept(result)
    assert node.robust_terms == {}


def test_same_origin_rollback_preserves_pending_and_original_first_receipt():
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    assert activation.accept(result)
    pending = activation.pending
    node.now_ns -= 1_000_000_000
    composer.poll()
    assert activation.pending is pending and activation.generation == 0
    # A valid durable retry is the same accepted authority even if rollback now
    # places its original committed_at more than the initial lead bound ahead.
    assert activation.accept(result)
    assert activation.pending is pending
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == node.affine_syncs == 1


def test_revalidate_current_registry_at_admission_does_not_apply_stale_staged_swap():
    result = committed_result()
    node, composer, activation = actual_composer(time_to_ns(result.committed_at)-100_000_000)
    assert activation.accept(result)
    # Simulate an intervening inconsistent owner mutation. Coverage cannot turn
    # the previously checked digest into authority over different current state.
    activation.active[7] = deepcopy(result.fill)
    original_terms = node.robust_terms
    node.now_ns = time_to_ns(result.committed_at)
    composer.poll()
    assert activation.generation == 0 and node.robust_terms is original_terms
    assert node.affine_syncs == 0 and activation.fault_count == 1


def enable_actual_cost_composition(node):
    """Attach existing numerical methods to the transaction's clock/publisher fixture."""
    for name in ('_apply_cost', '_bias_components_at_xy', '_gaussian_bias_at_xy', '_affine_bias_at_xy'):
        setattr(node, name, MethodType(getattr(ModifiedCost2D, name), node))
    node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(
        nanoseconds=node.now_ns, to_msg=lambda: set_time(Time(), node.now_ns)))
    node._now_sec = lambda: node.now_ns*1e-9
    node.xy = node.sensor_xy = None
    node.robust_profile = node.bias_all = node.enable_affine_bias = True
    node.enable_observability = False
    node.affine_decay_rate, node.affine_max_age, node.affine_min_norm = .0000005, 30., 1e-4
    node.pub = Publisher()


def deliver_current_cost(node, sequence):
    """Real public composer callbacks, with exact single-channel schema2 keys."""
    ns = node.now_ns
    state = AlgorithmState(run_id='test-m3', state=AlgorithmState.STATE_SEARCH,
        state_valid=True, weights_valid=True, run_id_valid=True,
        sensor_weight=1., gaussian_weight=1.)
    set_time(state.stamp, ns)
    node.algorithm_state = state
    raw = StampedFloat64MultiArray(timestamp=ns*1e-9, data=[-1.])
    source = CostBreakdown(source_timestamp=raw.timestamp, source_timestamp_valid=True,
        channel_count=1, raw_cost=[-1.], raw_cost_valid=True)
    set_time(source.stamp, ns)
    provenance = SourceSampleProvenance(schema_version=2, run_id='test-m3',
        stream_contract_id=CONTRACT, frame_id='odom', source_sequence=sequence,
        legacy_cost_source_timestamp_sec=raw.timestamp, channel_count=1,
        sensor_x_m=[0.], sensor_y_m=[0.], sensor_world_phase_rad=[0.],
        model_input_stamp_valid=True, sensor_transform_valid=True)
    set_time(provenance.model_input_stamp, ns)
    set_time(provenance.cost_publication_stamp, ns)
    composer = node.v2_composer
    composer.add_selected_raw(raw)
    composer.add_raw(source)
    composer.add_provenance(provenance)


def test_output_uses_old_law_while_pending_then_fences_applied_fill_during_rollback():
    result = committed_result()
    commit_ns = time_to_ns(result.committed_at)
    node, composer, activation = actual_composer(commit_ns-100_000_000)
    enable_actual_cost_composition(node)
    assert activation.accept(result)
    deliver_current_cost(node, 1)
    assert len(composer.publisher.messages) == 1
    old = composer.publisher.messages[-1]
    assert old.registry_digest == result.registry_digest_before
    assert list(old.gaussian_cost) == [0.] and activation.generation == 0

    node.now_ns = commit_ns
    composer.poll()
    assert activation.generation == 1
    deliver_current_cost(node, 2)
    covered = composer.publisher.messages[-1]
    assert len(composer.publisher.messages) == 2
    assert covered.registry_digest == result.registry_digest_after
    assert covered.objective_revision == old.objective_revision+1
    assert list(covered.gaussian_cost) == [result.fill.amplitude]

    node.now_ns = commit_ns-50_000_000
    composer.poll()
    deliver_current_cost(node, 3)
    assert len(composer.publisher.messages) == len(node.pub.messages) == 2
    assert activation.generation == node.affine_syncs == 1
    assert activation.accept(result)  # Idempotency survives rollback.
    node.now_ns = commit_ns+100_000_000
    composer.poll()
    deliver_current_cost(node, 4)
    assert len(composer.publisher.messages) >= 3
    assert all(time_to_ns(msg.composition_stamp) >= commit_ns
               for msg in composer.publisher.messages[1:])
    assert composer.publisher.messages[-1].registry_digest == result.registry_digest_after
    assert activation.generation == node.affine_syncs == 1
