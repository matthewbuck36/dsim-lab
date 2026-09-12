"""R22 full publication pairing opt-in; existing BagData and motion owners only."""
from copy import deepcopy
from dataclasses import replace

import pytest

from test_m4_evaluation_cli import cli, stamp
from test_m4_v10_motion import NS
from test_m4_v10_science import v10_plan
from test_r9_motion_readiness import fixture, extra_zero


BASIS = 'full_publication_order_v1'


def measure(data, *, basis=BASIS, authority=True):
    planned = v10_plan('C', experiment_version='m4-pilot-v13')
    planned['resolved_scenario']['algorithm']['launch_overrides']['algorithm_pose_topic'] = '/pose'
    return cli._v10_motion_metrics(data, planned, {'complete': authority}, pairing_basis=basis)


def unavailable(result):
    assert result['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['analysis_complete'] is False
    assert result['mandatory_stopped_acquisitions'] is None


def outside_pair(data, *, post=False):
    """Append an authentic matching zero pair in monotone per-topic order."""
    boundary = data.readiness_end_ns if post else data.readiness_start_ns
    for alias in ('command_final', 'control_diagnostics'):
        source = data.records_by_topic['/'+alias][-1 if post else 0]
        record = deepcopy(source)
        if alias == 'command_final':
            record.message.linear.x = 0.
        else:
            record.message.final_command = [0.]*6
            record.message.stamp = stamp(6. if post else 0.)
        record = replace(record, bag_timestamp_ns=boundary+(1 if post else -1),
                         in_readiness_interval=False)
        data.records_by_topic['/'+alias].insert(len(data.records_by_topic['/'+alias]) if post else 0, record)


@pytest.mark.parametrize('edge', ['start', 'end'])
@pytest.mark.parametrize('outside_alias', ['command_final', 'control_diagnostics'])
def test_only_pairs_with_both_receipts_ready_contribute_to_motion(edge, outside_alias):
    data = fixture()
    index = 0 if edge == 'start' else 50
    boundary = data.readiness_start_ns if edge == 'start' else data.readiness_end_ns
    for alias in ('command_final', 'control_diagnostics'):
        rows = data.records_by_topic['/'+alias]
        outside = alias == outside_alias
        delta = (-1 if outside else 1) if edge == 'start' else (1 if outside else -1)
        rows[index] = replace(rows[index], bag_timestamp_ns=boundary+delta,
                              in_readiness_interval=not outside)
    data.records_by_topic['/command_final'][index].message.linear.x = 0.
    data.records_by_topic['/control_diagnostics'][index].message.final_command = [0.]*6
    legacy = measure(data, basis=None)
    unavailable(legacy)
    assert not legacy['command_pairing_complete']
    assert legacy['command_pairing_scope'] == 'recorded_readiness_interval_v1'
    selected = measure(data)
    assert selected['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    assert selected['analysis_complete'] and selected['command_pairing_complete']
    assert selected['mandatory_stopped_acquisitions'] == 0
    assert selected['zero_publication_count'] == 0
    assert selected['command_pairing_scope'] == BASIS
    assert selected['command_pairing_full_counts'] == dict(control_diagnostics=51, command_final=51)
    assert selected['command_pairing_admitted_pair_count'] == 50
    assert selected['diagnostic_count'] == (50 if outside_alias == 'control_diagnostics' else 51)
    assert selected['actual_command_count'] == (50 if outside_alias == 'command_final' else 51)
    assert selected['command_pairing_excluded_boundary_pairs'] == [dict(index=index,
        command_bag_ns=data.records_by_topic['/command_final'][index].bag_timestamp_ns,
        diagnostic_bag_ns=data.records_by_topic['/control_diagnostics'][index].bag_timestamp_ns,
        command_in_readiness=outside_alias != 'command_final',
        diagnostic_in_readiness=outside_alias != 'control_diagnostics',
        stamp_ns=index*100_000_000, zero=True)]
    assert all(r['coverage_complete'] and r['positive_motion_evidence']
               for r in selected['acquisition_segments'])


def test_clean_c_control_preserves_all_original_motion_fields_and_default_dispatch():
    data = fixture()
    planned = v10_plan('C', experiment_version='m4-pilot-v13')
    planned['resolved_scenario']['algorithm']['launch_overrides']['algorithm_pose_topic'] = '/pose'
    implicit = cli._v10_motion_metrics(data, planned, {'complete': True})
    legacy = measure(data, basis=None)
    assert implicit == legacy
    selected = measure(data)
    for key, value in legacy.items():
        if key != 'command_pairing_scope':
            assert selected[key] == value, key
    assert selected['command_pairing_full_counts'] == dict(control_diagnostics=51, command_final=51)
    assert selected['command_pairing_admitted_pair_count'] == 51
    assert selected['command_pairing_excluded_boundary_pairs'] == []
    assert selected['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'


@pytest.mark.parametrize('alias,post', [('command_final', False), ('control_diagnostics', True)])
def test_unpaired_outside_record_cannot_be_dropped_to_repair_full_stream(alias, post):
    data = fixture()
    extra_zero(data, alias, data.readiness_end_ns+1 if post else data.readiness_start_ns-1)
    assert measure(data, basis=None)['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    selected = measure(data)
    assert not selected['command_pairing_complete']
    unavailable(selected)


@pytest.mark.parametrize('fault', ['missing_command', 'extra_command', 'empty',
    'interior_vector_mismatch', 'invalid_diagnostic', 'nonfinite_actual',
    'nonfinite_diagnostic', 'source_rollback', 'receipt_gap'])
def test_full_stream_faults_never_become_qualified_motion(fault):
    data = fixture()
    commands = data.records_by_topic['/command_final']
    diagnostics = data.records_by_topic['/control_diagnostics']
    if fault == 'missing_command':
        commands.pop(20)
    elif fault == 'extra_command':
        extra_zero(data, 'command_final', 102*NS+500_000)
    elif fault == 'empty':
        commands.clear(); diagnostics.clear()
    elif fault == 'interior_vector_mismatch':
        commands[20].message.linear.y = .01
    elif fault == 'invalid_diagnostic':
        diagnostics[20].message.final_command_valid = False
    elif fault == 'nonfinite_actual':
        commands[20].message.angular.y = float('nan')
    elif fault == 'nonfinite_diagnostic':
        diagnostics[20].message.final_command[0] = float('inf')
    elif fault == 'source_rollback':
        diagnostics[20].message.stamp = stamp(1.8)
    elif fault == 'receipt_gap':
        # Original 1ms plus this offset is exactly 0.5s+1ns; order remains valid.
        commands[:] = [replace(r, bag_timestamp_ns=r.bag_timestamp_ns+499_000_001) for r in commands]
    result = measure(data)
    assert not result['command_pairing_complete']
    unavailable(result)


@pytest.mark.parametrize('post', [False, True])
@pytest.mark.parametrize('fault', ['mismatch', 'invalid'])
def test_matching_outside_pair_is_validated_before_readiness_selection(post, fault):
    data = fixture(); outside_pair(data, post=post)
    index = -1 if post else 0
    if fault == 'mismatch':
        data.records_by_topic['/command_final'][index].message.linear.x = .04
    else:
        data.records_by_topic['/control_diagnostics'][index].message.final_command_valid = False
    assert measure(data, basis=None)['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    selected = measure(data)
    assert selected['command_pairing_errors'] == [51 if post else 0]
    assert not selected['command_pairing_complete']
    unavailable(selected)


@pytest.mark.parametrize('alias', ['command_final', 'control_diagnostics'])
def test_nonmonotone_bag_receipts_reject_even_when_vectors_and_half_second_bound_match(alias):
    data = fixture(); rows = data.records_by_topic['/'+alias]
    rows[20] = replace(rows[20], bag_timestamp_ns=rows[19].bag_timestamp_ns-1)
    assert measure(data, basis=None)['command_pairing_complete']
    selected = measure(data)
    assert not selected['command_pairing_complete']
    unavailable(selected)


@pytest.mark.parametrize('field,value', [('sec', -1), ('nanosec', 1_000_000_000)])
def test_invalid_diagnostic_stamp_components_are_not_authoritative(field, value):
    data = fixture()
    setattr(data.records_by_topic['/control_diagnostics'][20].message.stamp, field, value)
    selected = measure(data)
    assert not selected['command_pairing_complete']
    unavailable(selected)


def test_half_second_receipt_bound_remains_inclusive():
    data = fixture(); commands = data.records_by_topic['/command_final']
    commands[:] = [replace(r, bag_timestamp_ns=r.bag_timestamp_ns+499_000_000) for r in commands]
    selected = measure(data)
    assert selected['command_pairing_complete'] and selected['analysis_complete']
    assert selected['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'


def test_unrelated_nan_source_field_on_valid_outside_zero_diagnostic_remains_allowed():
    data = fixture(); outside_pair(data)
    diagnostic = data.records_by_topic['/control_diagnostics'][0]
    diagnostic.message.source_timestamp = float('nan')
    diagnostic.message.source_timestamp_valid = False
    data.records_by_topic['/control_diagnostics'][0] = replace(diagnostic,
        source_timestamp_sec=float('nan'), source_timestamp_valid=False)
    selected = measure(data)
    assert selected['command_pairing_complete'] and selected['analysis_complete']
    assert selected['zero_publication_count'] == 0
    assert selected['command_pairing_admitted_pair_count'] == 51


@pytest.mark.parametrize('fault', ['missing_end', 'inconsistent_membership'])
def test_pairing_still_requires_real_readiness_bounds_and_membership(fault):
    data = fixture()
    if fault == 'missing_end':
        data = replace(data, readiness_end_ns=None)
    else:
        rows = data.records_by_topic['/command_final']
        rows[20] = replace(rows[20], in_readiness_interval=False)
    selected = measure(data)
    assert not selected['command_pairing_complete']
    unavailable(selected)


def test_valid_pairing_never_supplies_missing_intervention_authority():
    result = measure(fixture(), authority=False)
    assert result['command_pairing_complete']
    assert not result['authority_complete']
    unavailable(result)


@pytest.mark.parametrize('stopped', ['pose', 'command'])
def test_true_sustained_stop_is_preserved_after_full_pairing(stopped):
    data = fixture()
    for index in range(12, 21):
        if stopped == 'pose':
            message = data.records_by_topic['/pose'][index].message
            message.twist.twist.linear.x = 0.
            message.pose.pose.position.x = .024
        else:
            data.records_by_topic['/command_final'][index].message.linear.x = 0.
            data.records_by_topic['/control_diagnostics'][index].message.final_command = [0.]*6
    result = measure(data)
    assert result['command_pairing_complete'] and result['analysis_complete']
    assert result['status'] == ('OBSERVED_STATIONARY_INTERVAL' if stopped == 'pose'
                                else 'OBSERVED_ZERO_COMMAND_INTERVAL')
    assert result['mandatory_stopped_acquisitions'] is None
    field = 'sustained_stationary_interval' if stopped == 'pose' else 'sustained_zero_command_interval'
    assert result['acquisition_segments'][0][field]
    assert result['source_gap_limit_sec'] == result['stationary_duration_limit_sec'] == .5


def test_unsupported_basis_is_rejected_without_silent_fallback():
    with pytest.raises(ValueError):
        measure(fixture(), basis='nearest_matching_vector')
