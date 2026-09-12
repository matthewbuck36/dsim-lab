"""Cost-join expiry restarts evidence while retaining valid source support."""
from copy import deepcopy
from dataclasses import replace
from itertools import permutations
import math

import numpy as np
import pytest

from ros_esc.filter_node.rolling_gesc import (
    AugmentedCost, EncoderSample, GescSyncConfig, ObjectiveIdentity, PoseSample,
    Provenance, RawCost, SourceSynchronizer, StreamIdentity,
)
from ros_esc.v2_stream import set_time, time_to_ns
from test_v2_clock_admission import acquisition_messages as clock_messages, schema2
import test_v2_runtime as runtime

NS = 1_000_000_000
IDENTITY = StreamIdentity('expiry', 'contract', 'odom', 0, cost_key_basis='model_input_time')


def acquisition_messages(stamp):
    bundle = clock_messages(stamp)
    # The imported fixture fixes publication at1.1s to test held clocks;
    # these multi-time recovery cases need publication following each source.
    set_time(bundle['provenance'].cost_publication_stamp, stamp + 5_000_000)
    set_time(bundle['objective'].composition_stamp, stamp + 6_000_000)
    return bundle


def ns(t):
    return round(t * NS)


def core_with_support(config=GescSyncConfig(), identity=IDENTITY):
    core = SourceSynchronizer(config)
    core.set_context(identity)
    support(core, .9, .9)
    return core


def support(core, stamp, now):
    for op, sample in (
        (core.add_pose, PoseSample(ns(stamp), (0., 0.), 0., ns(now), 'odom')),
        (core.add_encoder, EncoderSample(ns(stamp), .2, ns(now))),
    ):
        assert not op(sample, ns(now)).faults


def rows(stamp, now, identity=IDENTITY, sequence=1):
    return (RawCost(stamp, (-1.,), ns(now)),
            AugmentedCost(stamp, (-1.,), ObjectiveIdentity(1), ns(now)),
            Provenance(stamp, sequence, ns(stamp), ns(now), (.18, 0.), .2, identity, ns(now)))


def push(core, components, now):
    results = []
    for op, sample in zip((core.add_raw_cost, core.add_augmented, core.add_provenance), components):
        batch = op(sample, ns(now))
        assert not batch.faults, batch.faults
        results.extend(batch.observations)
    return results


def expired_core():
    core = core_with_support()
    assert len(push(core, rows(.9, .9), .9)) == 1
    core.add_raw_cost(rows(1., 1.)[0], ns(1.))
    core.add_provenance(rows(1.1, 1.1, sequence=2)[2], ns(1.1))
    support(core, 1.48, 1.48)
    support(core, 1.52, 1.48)
    saved = (list(core._poses), list(core._encoders), core._last_source, core._last_sequence)
    batch = core.poll(ns(1.51))
    return core, saved, batch


def test_expiry_retires_every_partial_and_preserves_support_receipts_and_frontiers():
    core, saved, batch = expired_core()
    assert [f.reason for f in batch.faults] == ['pending_expired']
    assert not batch.observations
    assert set(batch.retired_keys) == {1., 1.1}
    assert not core._pending
    assert (core._poses, core._encoders, core._last_source, core._last_sequence) == saved
    observation, = push(core, rows(1.5, 1.52, sequence=3), 1.52)
    assert observation.pose_left_stamp_ns == ns(1.48)
    assert observation.pose_right_stamp_ns == ns(1.52)
    assert observation.oldest_receipt_stamp_ns == ns(1.48)


@pytest.mark.parametrize('index', range(3))
def test_late_retired_components_beyond_freshness_do_not_recreate_or_reset(index):
    core, saved, _ = expired_core()
    sequence = core.reset_sequence
    operation = (core.add_raw_cost, core.add_augmented, core.add_provenance)[index]
    for now in (1.6, 2., 3.):
        batch = operation(rows(1., 1.)[index], ns(now))
        assert not batch.faults and not batch.observations
        assert not core._pending
        assert core.reset_sequence == sequence
        assert core._poses == saved[0] and core._encoders == saved[1]


@pytest.mark.parametrize('fault', ['raw_nan', 'raw_empty', 'wrong_identity', 'bad_geometry', 'future_publication', 'bad_objective'])
def test_retirement_does_not_excuse_malformed_or_wrong_context_components(fault):
    core, _, _ = expired_core()
    raw, augmented, provenance = rows(1., 1.)
    if fault == 'raw_nan': sample, op = replace(raw, values=(math.nan,)), core.add_raw_cost
    elif fault == 'raw_empty': sample, op = replace(raw, values=()), core.add_raw_cost
    elif fault == 'wrong_identity': sample, op = replace(provenance, identity=replace(IDENTITY, frame_id='map')), core.add_provenance
    elif fault == 'bad_geometry': sample, op = replace(provenance, sensor_xy=(math.nan, 0.)), core.add_provenance
    elif fault == 'future_publication': sample, op = replace(provenance, cost_publication_ns=ns(9.)), core.add_provenance
    else: sample, op = replace(augmented, objective=ObjectiveIdentity(1, sensor_weight=math.nan)), core.add_augmented
    assert op(sample, ns(2.)).faults
    assert not core._poses and not core._encoders


def test_preserved_support_does_not_become_fresh_and_frontier_rejects_old_source():
    core, _, _ = expired_core()
    # Original receipts remain1.48s: they cannot support a1.5s target at2.1s.
    batch = core.add_raw_cost(rows(1.5, 2.1)[0], ns(2.1))
    assert batch.faults[0].reason == 'stale_or_future_cost'
    core, _, _ = expired_core()
    # A new key cannot evade the original sequence frontier preserved by expiry.
    batch_rows = rows(1.5, 1.52, sequence=1)
    core.add_raw_cost(batch_rows[0], ns(1.52))
    core.add_augmented(batch_rows[1], ns(1.52))
    assert core.add_provenance(batch_rows[2], ns(1.52)).faults[0].reason == 'source_rollback'


def test_true_used_conflict_revocation_clock_and_context_keep_strict_semantics():
    core, _, _ = expired_core()
    assert core.add_raw_cost(RawCost(.9, (-9.,), ns(1.51)), ns(1.51)).faults
    core, _, _ = expired_core()
    assert core.invalidate_key(1.).faults
    assert not core.is_retired(1.)  # Hard poison takes precedence.
    assert core.add_raw_cost(RawCost(1., (-1.,), ns(1.6)), ns(1.6)).faults
    core, _, _ = expired_core()
    assert core.poll(ns(1.4)).faults[0].reason == 'clock_rollback'
    assert not core._poses
    core.set_context(replace(IDENTITY, run_id='new-run'))
    assert not core._retired and not core._used


def test_retirement_is_bounded_and_invalid_far_future_keys_never_register():
    core = core_with_support(GescSyncConfig(max_pending_costs=2))
    core.expire_pending(extra_keys=(.5, .6, .7, .8, .9), now_ns=ns(.9))
    assert tuple(core._retired) == (.6, .7, .8, .9)
    before = dict(core._retired)
    assert core.retire_keys((math.nan, -1., 1e308, 30.), ns(1.)) == ()
    assert core._retired == before


def test_legacy_publication_key_expiry_still_clears_support():
    legacy = replace(IDENTITY, cost_key_basis='publication_time')
    core = core_with_support(identity=legacy)
    core.add_raw_cost(RawCost(1., (-1.,), NS), NS)
    assert core.poll(ns(1.51)).faults[0].reason == 'pending_expired'
    assert not core._poses and not core._encoders and not core._retired


def adapter_expiry(schema2):
    node, adapter = runtime.make_filter()
    runtime.support(node, adapter, ns(.9))
    for name, message in acquisition_messages(ns(.9)).items():
        getattr(adapter, 'add_' + name)(message)
    node.now_ns = ns(1.02)
    missing = acquisition_messages(NS)
    adapter.add_objective(missing['objective'])  # Adapter-only partial, no core join.
    node.z_vec[:] = 123.
    runtime.support(node, adapter, ns(1.58))
    saved = (list(adapter.sync._poses), list(adapter.sync._encoders))
    adapter.poll()
    return node, adapter, missing, saved


def test_adapter_only_expiry_coordinates_retirement_and_fresh_empty_history(schema2):
    node, adapter, missing, saved = adapter_expiry(schema2)
    assert adapter.sync.is_retired(1.)
    assert not adapter.pending and not adapter.sync._pending
    assert adapter.sync._poses == saved[0] and adapter.sync._encoders == saved[1]
    assert node.z_vec == pytest.approx(adapter.initial_state)
    assert adapter.previous_source_ns is None
    assert adapter.publisher.messages[-1].reset_reason == 'pending_receipt_expired'
    assert not adapter.publisher.messages[-1].output_valid
    for name, message in acquisition_messages(ns(1.58)).items():
        getattr(adapter, 'add_' + name)(message)
    diag = adapter.publisher.messages[-1]
    assert diag.output_valid and diag.fallback_used and not diag.qualified
    assert diag.completed_revolutions == 0
    assert time_to_ns(diag.observation.source_stamp) == ns(1.58)
    assert node.z_vec == pytest.approx(adapter.initial_state)  # First recovered dt=0.


def test_combined_full_queues_retire_entire_union_without_late_fragment_resets(schema2):
    node, adapter = runtime.make_filter()
    adapter.sync.config = replace(adapter.sync.config, max_pending_costs=2)
    runtime.support(node, adapter, ns(1.1))
    messages = [acquisition_messages(ns(key)) for key in (1.4, 1.41, 1.42, 1.43)]
    bundles = {bundle['raw'].timestamp: bundle for bundle in messages}
    keys = tuple(bundles)  # Joins retain the exact wire float, without rounding.
    for key in keys[:2]:
        assert not adapter.sync.add_raw_cost(
            RawCost(key, (-1.,), node.now_ns), node.now_ns).faults
    for key in keys[2:]:
        adapter.add_objective(bundles[key]['objective'])
    assert len(adapter.sync._pending) == len(adapter.pending) == 2
    runtime.support(node, adapter, ns(1.58))
    saved = (list(adapter.sync._poses), list(adapter.sync._encoders))
    node.now_ns = ns(1.63)
    adapter.poll()
    assert set(adapter.sync._retired) == set(keys)
    assert not adapter.pending and not adapter.sync._pending
    sequence = adapter.sync.reset_sequence
    node.now_ns = ns(2.3)
    for key in reversed(keys):
        for name in ('objective', 'provenance', 'augmented', 'raw'):
            getattr(adapter, 'add_' + name)(bundles[key][name])
    assert adapter.sync.reset_sequence == sequence
    assert not adapter.pending and not adapter.sync._pending
    assert (adapter.sync._poses, adapter.sync._encoders) == saved


def test_adapter_partial_capacity_uses_declared_core_bound(schema2):
    node, adapter = runtime.make_filter()
    adapter.sync.config = replace(adapter.sync.config, max_pending_costs=2)
    runtime.support(node, adapter, ns(1.1))
    for key in (1.4, 1.41, 1.42):
        adapter.add_objective(acquisition_messages(ns(key))['objective'])
    assert not adapter.pending and not adapter.sync._pending
    assert not adapter.sync._poses and not adapter.sync._encoders
    assert adapter.rolling.evaluate(ns(1.1), 0., ns(1.1)).reset_reason == 'pending_capacity'


@pytest.mark.parametrize('order', list(permutations(('raw', 'augmented', 'provenance', 'objective'))))
def test_adapter_late_retired_pieces_in_any_order_do_not_reset_or_refresh(order, schema2):
    node, adapter, missing, saved = adapter_expiry(schema2)
    sequence = adapter.sync.reset_sequence
    node.now_ns = ns(2.3)
    for name in order:
        getattr(adapter, 'add_' + name)(missing[name])
    assert adapter.sync.reset_sequence == sequence
    assert not adapter.pending and not adapter.sync._pending
    assert adapter.sync._poses == saved[0] and adapter.sync._encoders == saved[1]


@pytest.mark.parametrize('fault', ['raw_nan', 'augmented_empty', 'provenance_frame', 'provenance_nan', 'objective_nan', 'future_key'])
def test_adapter_retired_or_invalid_fragments_do_not_bypass_hard_validation(fault, schema2):
    node, adapter, missing, _ = adapter_expiry(schema2)
    sequence = adapter.sync.reset_sequence
    node.now_ns = ns(2.3)
    if fault == 'raw_nan': name = 'raw'; missing[name].data = [math.nan]
    elif fault == 'augmented_empty': name = 'augmented'; missing[name].data = []
    elif fault == 'provenance_frame': name = 'provenance'; missing[name].frame_id = 'map'
    elif fault == 'provenance_nan': name = 'provenance'; missing[name].sensor_x_m = [math.nan]
    elif fault == 'objective_nan': name = 'objective'; missing[name].sensor_x_m = [math.nan]
    else: name = 'augmented'; missing[name].timestamp = 1e300
    getattr(adapter, 'add_' + name)(missing[name])
    assert adapter.sync.reset_sequence > sequence
    assert not adapter.sync._poses and not adapter.sync._encoders
    assert not adapter.sync.is_retired(1e300)
