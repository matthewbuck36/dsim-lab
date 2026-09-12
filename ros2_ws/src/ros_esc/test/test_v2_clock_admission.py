"""Acquisition keys survive coarse, independently delivered simulation clocks."""

from copy import deepcopy
from dataclasses import replace

import pytest
from nav_msgs.msg import Odometry

from ros_esc.filter_node.rolling_gesc import (
    AugmentedCost, DemodulatedSample, EncoderSample, ObjectiveIdentity,
    PoseSample, Provenance, RawCost, RollingGesc, SourceSynchronizer,
    StreamIdentity,
)
from ros_esc.v2_stream import set_time, stream_contract_id, time_to_ns
from ros_esc_interfaces.msg import CostBreakdown, StampedFloat64MultiArray
import test_v2_runtime as runtime
import ros_esc.filter_node.v2_runtime as adapter_module
import ros_esc.modified_cost_node.v2_objective as composer_module
from test_v2_recording_contract import chain
from ros_esc.experiment_recording.validate_run import v2_stream_contract_errors

NS = 1_000_000_000
IDENTITY = StreamIdentity('clock-test', 'contract', 'odom', 0,
                          cost_key_basis='model_input_time')


def synchronizer():
    core = SourceSynchronizer()
    core.set_context(IDENTITY)
    return core


def add_acquisition(core, stamp, *, publication=1_100_000_000, receipt=NS, index=1):
    key = stamp*1e-9
    records = (
        (core.add_pose, PoseSample(stamp, (0., 0.), 0., receipt, 'odom')),
        (core.add_encoder, EncoderSample(stamp, .2*index, receipt)),
        (core.add_raw_cost, RawCost(key, (-2.,), receipt)),
        (core.add_augmented, AugmentedCost(key, (-2.,), ObjectiveIdentity(1), receipt)),
        (core.add_provenance, Provenance(key, index, stamp, publication,
                                       (.18, 0.), .2*index, IDENTITY, receipt)),
    )
    for operation, message in records:
        result = operation(message, receipt)
        assert not result.faults, result.faults
        assert not result.observations


def test_distinct_acquisitions_share_publication_clock_without_sharing_keys():
    core = synchronizer()
    stamps = [1_010_000_000, 1_020_000_000, 1_030_000_000]
    for index, stamp in enumerate(stamps, 1):
        add_acquisition(core, stamp, index=index)
    assert not core.poll(1_030_000_000).observations
    batch = core.poll(1_100_000_000)
    assert not batch.faults
    assert [obs.source_stamp_ns for obs in batch.observations] == stamps
    assert len({obs.legacy_cost_source_timestamp_sec for obs in batch.observations}) == 3
    assert {obs.cost_source_stamp_ns for obs in batch.observations} == {1_100_000_000}
    for obs in batch.observations:
        assert obs.receipt_stamp_ns == obs.oldest_receipt_stamp_ns == NS
        assert obs.admission_stamp_ns == 1_100_000_000
        rolling = RollingGesc()
        rolling.update(DemodulatedSample(obs, (1., 0.)))
        assert not rolling.evaluate(1_090_000_000, 0., obs.source_stamp_ns).output_valid
        assert rolling.evaluate(1_100_000_000, 0., obs.source_stamp_ns).output_valid


def test_future_right_bracket_waits_and_current_pose_uses_only_clock_covered_samples():
    core = synchronizer()
    for stamp in (1_060_000_000, 1_140_000_000):
        assert not core.add_pose(PoseSample(stamp, (0., 0.), 0., NS, 'odom'), NS).faults
        assert not core.add_encoder(EncoderSample(stamp, 0., NS), NS).faults
    assert core.latest_admitted_pose(1_100_000_000).stamp_ns == 1_060_000_000
    key = 1.1
    core.add_raw_cost(RawCost(key, (-2.,), NS), NS)
    core.add_augmented(AugmentedCost(key, (-2.,), ObjectiveIdentity(1), NS), NS)
    core.add_provenance(Provenance(key, 1, 1_100_000_000, 1_100_000_000,
                                   (.18, 0.), 0., IDENTITY, NS), NS)
    assert not core.poll(1_130_000_000).observations
    batch = core.poll(1_140_000_000)
    assert len(batch.observations) == 1
    assert batch.observations[0].sync_error_ns == 40_000_000


def test_clock_wait_preserves_original_age_and_duplicate_cannot_extend_it():
    core = synchronizer()
    raw = RawCost(1.1, (-2.,), NS)
    assert not core.add_raw_cost(raw, NS).faults
    assert not core.add_raw_cost(replace(raw, receipt_ns=1_400_000_000), 1_400_000_000).faults
    assert core.poll(1_500_000_001).faults[0].reason == 'pending_expired'


@pytest.mark.parametrize('kind', ['pose', 'encoder'])
def test_conflicting_support_is_not_readmitted_after_reset(kind):
    core = synchronizer()
    if kind == 'pose':
        operation = core.add_pose
        first = PoseSample(1_100_000_000, (0., 0.), 0., NS, 'odom')
        conflict = replace(first, xy=(1., 0.))
    else:
        operation = core.add_encoder
        first = EncoderSample(1_100_000_000, 0., NS)
        conflict = replace(first, phase=1.)
    assert not operation(first, NS).faults
    assert operation(conflict, NS).faults
    assert not operation(replace(conflict, receipt_ns=1_100_000_000), 1_100_000_000).observations
    assert not (core._poses if kind == 'pose' else core._encoders)
    assert not operation(replace(first, stamp_ns=1_110_000_000, receipt_ns=1_100_000_000), 1_100_000_000).faults
    assert len(core._poses if kind == 'pose' else core._encoders) == 1


@pytest.mark.parametrize('bad', ['too_far_ahead', 'wrong_key', 'publication_before_source', 'rollback'])
def test_clock_admission_retains_invalid_input_gates(bad):
    core = synchronizer()
    if bad == 'too_far_ahead':
        batch = core.add_encoder(EncoderSample(1_500_000_001, 0., NS), NS)
    elif bad == 'rollback':
        core.add_encoder(EncoderSample(1_020_000_000, 0., NS), NS)
        batch = core.add_encoder(EncoderSample(1_010_000_000, 0., NS), NS)
    else:
        source = 1_100_000_000
        batch = core.add_provenance(Provenance(
            1.2 if bad == 'wrong_key' else 1.1, 1, source,
            source-1 if bad == 'publication_before_source' else 1_200_000_000,
            (.18, 0.), 0., IDENTITY, NS), NS)
    assert batch.faults and not batch.observations


@pytest.fixture
def schema2(monkeypatch):
    config = dict(runtime.CONFIG, schema_version=2, cost_key_basis='model_input_time')
    monkeypatch.setattr(runtime, 'CONFIG', config)
    return config


def acquisition_messages(source_ns):
    rows = runtime.messages(source_ns)
    key = source_ns*1e-9
    for name in ('raw', 'augmented'):
        rows[name].timestamp = key
    for name in ('provenance', 'objective'):
        rows[name].schema_version = 2
        rows[name].legacy_cost_source_timestamp_sec = key
    set_time(rows['provenance'].cost_publication_stamp, 1_100_000_000)
    set_time(rows['objective'].composition_stamp, 1_100_000_000)
    return rows


def test_filter_waits_for_its_clock_without_restamping_receipts(schema2):
    node, adapter = runtime.make_filter()
    node.now_ns = NS
    adapter.add_state(runtime.make_state(NS))
    for stamp in (1_010_000_000, 1_020_000_000, 1_030_000_000):
        pose = Odometry()
        pose.header.frame_id, pose.pose.pose.orientation.w = 'odom', 1.
        set_time(pose.header.stamp, stamp)
        adapter.add_pose(pose)
        adapter.add_encoder(StampedFloat64MultiArray(timestamp=stamp*1e-9, data=[.4]))
        for name, message in acquisition_messages(stamp).items():
            getattr(adapter, 'add_'+name)(message)
    assert not node.filter_publisher.messages
    node.now_ns = 1_100_000_000
    adapter.poll()
    assert len(node.filter_publisher.messages) == 3
    wire = adapter.publisher.messages[-1].observation
    assert time_to_ns(wire.receipt_stamp) == NS
    assert time_to_ns(wire.admission_stamp) == node.now_ns
    assert time_to_ns(wire.source_stamp) == 1_030_000_000
    node.now_ns = 1_510_000_000
    adapter.poll()
    assert not adapter.publisher.messages[-1].output_valid
    assert len(node.filter_publisher.messages) == 3


def test_composer_waits_for_publication_clock_without_refreshing_first_receipt(schema2):
    node, composer = runtime.make_composer()
    node.now_ns = NS
    node.algorithm_state = runtime.make_state(NS)
    rows = acquisition_messages(1_030_000_000)
    source = CostBreakdown()
    source.source_timestamp = rows['raw'].timestamp
    source.source_timestamp_valid = source.raw_cost_valid = True
    source.channel_count, source.raw_cost = 1, [-1.]
    composer.add_raw(source)
    composer.add_selected_raw(rows['raw'])
    composer.add_provenance(rows['provenance'])
    assert not node.pub.messages
    node.now_ns = 1_100_000_000
    composer.poll()
    assert len(node.pub.messages) == len(composer.publisher.messages) == 1
    assert composer.publisher.messages[0].legacy_cost_source_timestamp_sec == 1.03
    assert time_to_ns(composer.publisher.messages[0].composition_stamp) == node.now_ns


@pytest.mark.parametrize('late_component', ['augmented', 'objective', 'raw', 'provenance'])
def test_filter_reports_latest_original_receipt_across_every_input(schema2, late_component):
    node, adapter = runtime.make_filter()
    node.now_ns = NS
    adapter.add_state(runtime.make_state(NS))
    stamp = 1_030_000_000
    pose = Odometry()
    pose.header.frame_id, pose.pose.pose.orientation.w = 'odom', 1.
    set_time(pose.header.stamp, stamp)
    adapter.add_pose(pose)
    adapter.add_encoder(StampedFloat64MultiArray(timestamp=1.03, data=[.4]))
    rows = acquisition_messages(stamp)
    for name, message in rows.items():
        if name != late_component:
            getattr(adapter, 'add_'+name)(message)
    node.now_ns = 1_100_000_000
    getattr(adapter, 'add_'+late_component)(rows[late_component])
    adapter.poll()
    assert len(node.filter_publisher.messages) == 1
    observation = adapter.publisher.messages[-1].observation
    assert time_to_ns(observation.oldest_receipt_stamp) == NS
    assert time_to_ns(observation.receipt_stamp) == 1_100_000_000
    assert time_to_ns(observation.admission_stamp) == 1_100_000_000


@pytest.mark.parametrize('component', ['raw', 'augmented', 'provenance', 'objective'])
def test_receipt_is_captured_before_callback_work_advances_the_clock(schema2, monkeypatch, component):
    node, adapter = runtime.make_filter()
    node.now_ns = NS
    rows = acquisition_messages(1_030_000_000)
    original = adapter_module.deepcopy
    def delayed_copy(value):
        result = original(value)
        node.now_ns = 1_100_000_000
        return result
    monkeypatch.setattr(adapter_module, 'deepcopy', delayed_copy)
    getattr(adapter, 'add_'+component)(rows[component])
    assert adapter.pending[1.03]['receipts'][component] == NS
    assert adapter.pending[1.03]['receipt'] == NS
    if component in ('raw', 'provenance'):
        assert adapter.sync._pending[1.03][component].receipt_ns == NS


@pytest.mark.parametrize('component', ['raw', 'selected_raw', 'provenance'])
def test_composer_preserves_receipt_across_callback_work(schema2, monkeypatch, component):
    node, composer = runtime.make_composer()
    node.now_ns = NS
    node.algorithm_state = runtime.make_state(NS)
    rows = acquisition_messages(1_030_000_000)
    source = CostBreakdown()
    source.source_timestamp = 1.03
    source.source_timestamp_valid = source.raw_cost_valid = True
    source.channel_count, source.raw_cost = 1, [-1.]
    message = {'raw': source, 'selected_raw': rows['raw'], 'provenance': rows['provenance']}[component]
    original = composer_module.deepcopy
    def delayed_copy(value):
        result = original(value)
        node.now_ns = 1_100_000_000
        return result
    monkeypatch.setattr(composer_module, 'deepcopy', delayed_copy)
    getattr(composer, 'add_'+component)(message)
    assert getattr(composer, component)[1.03][1] == NS


def test_composer_clock_rollback_discards_pending_but_accepts_new_source_frontier(schema2):
    node, composer = runtime.make_composer()
    node.now_ns = 1_100_000_000
    composer.poll()
    node.now_ns = NS
    composer.poll()
    assert composer.last_fault_reason == 'clock_rollback'
    assert not composer.origin_fault
    node.now_ns = 1_200_000_000
    node.algorithm_state = runtime.make_state(node.now_ns)
    rows = acquisition_messages(1_190_000_000)
    set_time(rows['provenance'].cost_publication_stamp, node.now_ns)
    source = CostBreakdown()
    source.source_timestamp = rows['raw'].timestamp
    source.source_timestamp_valid = source.raw_cost_valid = True
    source.channel_count, source.raw_cost = 1, [-1.]
    composer.add_raw(source)
    composer.add_selected_raw(rows['raw'])
    composer.add_provenance(rows['provenance'])
    assert len(node.pub.messages) == 1


@pytest.mark.parametrize('order', [
    ('provenance', 'raw', 'augmented', 'objective'),
    ('objective', 'augmented', 'raw', 'provenance'),
])
@pytest.mark.parametrize('invalidate_at', [0, 2, 4])
def test_revoked_source_key_cannot_be_restored_by_cross_topic_delivery(schema2, order, invalidate_at):
    node, adapter = runtime.make_filter()
    stamp = 1_030_000_000
    runtime.support(node, adapter, stamp)
    node.now_ns = 1_100_000_000
    rows = acquisition_messages(stamp)
    invalid = deepcopy(rows['provenance'])
    invalid.model_input_stamp_valid = invalid.sensor_transform_valid = False
    for index in range(5):
        if index == invalidate_at:
            adapter.add_provenance(invalid)
        if index < 4:
            getattr(adapter, 'add_'+order[index])(rows[order[index]])
    initial_count = len(node.filter_publisher.messages)
    assert initial_count == (1 if invalidate_at == 4 else 0)
    reset = adapter.sync.reset_sequence
    adapter.add_provenance(invalid)
    assert adapter.sync.reset_sequence == reset
    for name in reversed(order):
        getattr(adapter, 'add_'+name)(rows[name])
    adapter.poll()
    assert len(node.filter_publisher.messages) == initial_count
    assert not adapter.publisher.messages[-1].output_valid


@pytest.mark.parametrize('invalidate_after_raw', [False, True])
def test_composer_revocation_suppresses_late_previously_valid_metadata(schema2, invalidate_after_raw):
    node, composer = runtime.make_composer()
    node.now_ns = 1_100_000_000
    node.algorithm_state = runtime.make_state(node.now_ns)
    rows = acquisition_messages(1_030_000_000)
    invalid = deepcopy(rows['provenance'])
    invalid.model_input_stamp_valid = invalid.sensor_transform_valid = False
    source = CostBreakdown()
    source.source_timestamp = rows['raw'].timestamp
    source.source_timestamp_valid = source.raw_cost_valid = True
    source.channel_count, source.raw_cost = 1, [-1.]
    if invalidate_after_raw:
        composer.add_raw(source)
    composer.add_provenance(invalid)
    composer.add_selected_raw(rows['raw'])
    composer.add_raw(source)
    composer.add_provenance(rows['provenance'])
    composer.poll()
    assert not node.pub.messages and not composer.publisher.messages


def acquisition_chain():
    messages, identity, provenance, objective, direction = chain()
    config = identity['stream_config']
    config.update(schema_version=2, cost_key_basis='model_input_time')
    contract = stream_contract_id(config, 10_000_000_000)
    for message in (provenance, objective, direction, direction.observation):
        message.schema_version = 2
        message.stream_contract_id = contract
    for topic in ('raw_cost_topic', 'augmented_cost_topic'):
        messages[config[topic]][0][1].timestamp = .25
    for message in (provenance, objective, direction.observation):
        message.legacy_cost_source_timestamp_sec = .25
    set_time(direction.observation.receipt_stamp, 10_200_000_000)
    set_time(direction.observation.oldest_receipt_stamp, 10_200_000_000)
    set_time(direction.observation.admission_stamp, 10_280_000_000)
    return messages, identity, provenance, direction


def test_recorded_clock_admission_accepts_original_receipts_before_acquisition():
    messages, identity, _, _ = acquisition_chain()
    assert v2_stream_contract_errors(messages, identity) == []


@pytest.mark.parametrize('mutation', ['early_admission', 'wrong_acquisition_key', 'late_admission'])
def test_validator_rejects_impossible_clock_or_key_claims(mutation):
    messages, identity, provenance, direction = acquisition_chain()
    if mutation == 'wrong_acquisition_key':
        provenance.legacy_cost_source_timestamp_sec = .27
    else:
        set_time(direction.observation.admission_stamp,
                 10_260_000_000 if mutation == 'early_admission' else 10_300_000_000)
    assert v2_stream_contract_errors(messages, identity)
