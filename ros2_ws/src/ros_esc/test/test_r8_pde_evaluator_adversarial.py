"""Malformed PDE joins cannot authorize private fill-association evidence."""

from copy import deepcopy
import math

import pytest

from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.v2_lifecycle import message_payload
from ros_esc.v2_stream import set_time, time_to_ns

from test_r8_pde_evaluator_timestamp import fixture, normalize


def payloads(records):
    return [(stamp, message_payload(message)) for stamp, message in records]


@pytest.mark.parametrize('fault', [
    'run', 'stream', 'frame', 'origin', 'epoch', 'sequence',
    'source_history_disagreement', 'history_before_epoch',
    'source_after_publication', 'event_before_confirmation', 'late_event',
    'legacy_timestamp', 'legacy_values', 'nonfinite_legacy',
    'conflicting_event_name', 'conflicting_typed_identity',
    'ambiguous_typed_identity', 'changed_observed_origin',
])
def test_untrusted_join_preserves_public_event_and_returns_no_adaptation(fault):
    data = fixture(origin_ns=1_000_000_000)
    event = data[2][0][1]
    confirmation = data[4][0][1]
    legacy = data[5][0][1]
    if fault == 'run':
        confirmation.run_id = 'unrelated-run'
    elif fault == 'stream':
        confirmation.stream_contract_id = '0' * 64
    elif fault == 'frame':
        confirmation.frame_id = 'map'
    elif fault == 'origin':
        set_time(confirmation.time_origin, time_to_ns(confirmation.time_origin) + 1)
    elif fault == 'epoch':
        confirmation.search_epoch = 0
    elif fault == 'sequence':
        confirmation.confirmation_sequence = 0
    elif fault == 'source_history_disagreement':
        set_time(confirmation.source_stamp, time_to_ns(confirmation.history_end) - 1)
    elif fault == 'history_before_epoch':
        set_time(confirmation.history_start, time_to_ns(confirmation.epoch_started_at) - 1)
    elif fault == 'source_after_publication':
        future = time_to_ns(confirmation.stamp) + 1
        set_time(confirmation.source_stamp, future)
        set_time(confirmation.history_end, future)
    elif fault == 'event_before_confirmation':
        set_time(event.stamp, time_to_ns(confirmation.stamp) - 1)
    elif fault == 'late_event':
        set_time(event.stamp, time_to_ns(confirmation.stamp) + 500_000_001)
    elif fault == 'legacy_timestamp':
        legacy.timestamp += .001
    elif fault == 'legacy_values':
        values = list(legacy.data)
        values[3] += .001
        legacy.data = values
    elif fault == 'nonfinite_legacy':
        values = list(legacy.data)
        values[0] = math.nan
        legacy.data = values
    elif fault == 'conflicting_event_name':
        event.value_names = [*event.value_names, 'metric']
        event.values = [*event.values, confirmation.legacy_snapshot[0] + .001]
    elif fault == 'conflicting_typed_identity':
        conflict = deepcopy(confirmation)
        conflict.reason = 'different payload under the same confirmation identity'
        data[4].append((data[4][0][0] + 1, conflict))
    elif fault == 'ambiguous_typed_identity':
        other = deepcopy(confirmation)
        other.search_epoch += 1
        other.confirmation_sequence += 1
        data[4].append((data[4][0][0] + 1, other))
    elif fault == 'changed_observed_origin':
        changed = deepcopy(data[6][0][1])
        changed.start_time += .001
        data[6].append((data[6][0][0] + 1, changed))
    else:
        raise AssertionError(fault)

    original = payloads(data[2])
    events, _, error = normalize(data)
    assert error, fault
    assert events is data[2]
    assert payloads(data[2]) == original


@pytest.mark.parametrize('missing_index', [4, 5, 6], ids=['typed', 'legacy', 'origin'])
def test_pending_cross_topic_data_cannot_supply_evidence_until_exact_input_arrives(missing_index):
    data = fixture(origin_ns=1_000_000_000)
    original = payloads(data[2])
    delayed = list(data[missing_index])
    data[missing_index].clear()
    events, _, error = normalize(data)
    assert error  # Live refresh may wait; final evaluation must expose this error.
    assert events is data[2] and payloads(data[2]) == original

    data[missing_index].extend(delayed)
    events, audit, error = normalize(data)
    assert error is None, error
    assert audit
    confirmation = data[4][0][1]
    expected = (time_to_ns(confirmation.source_stamp)
                - time_to_ns(confirmation.time_origin)) * 1e-9
    assert events[0][1].source_timestamp == expected
    assert payloads(data[2]) == original


@pytest.mark.parametrize('scope', ['stationary', 'unselected_suite', 'historical_v9'])
def test_new_bridge_does_not_reinterpret_unselected_legacy_scope(scope):
    data = fixture()
    if scope == 'stationary':
        data[0]['algorithm']['launch_overrides']['continuous_search_mode'] = 'stationary_v1'
    elif scope == 'historical_v9':
        data[0]['suite_id'] = 'm4_pilot_v9'
    else:
        data[0]['suite_id'] = 'unselected_timestamp_fixture'
    # Out-of-scope selection must not impose the new typed prerequisites.
    for index in (4, 5, 6):
        data[index].clear()
    assert runner._m4_pde_event_selection(data[0]) is None
    original = payloads(data[2])
    events, audit, error = normalize(data)
    assert events is data[2] and audit == [] and error is None
    assert payloads(data[2]) == original


def test_identical_retransmission_keeps_original_support_and_decision_clocks():
    data = fixture(origin_ns=1_000_000_000)
    original = payloads(data[2])
    expected, _, error = normalize(data)
    assert error is None, error
    for index in (4, 5, 6):
        stamp, message = data[index][0]
        data[index].append((stamp + 1000, deepcopy(message)))
    events, audit, error = normalize(data)
    assert error is None, error
    assert audit
    assert payloads(events) == payloads(expected)
    assert payloads(data[2]) == original
