"""Actual motion projection readiness boundaries; no bags, nodes or models."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from test_m4_evaluation_cli import cli, Obj, stamp
from test_m4_v10_motion import projected, NS
from test_m4_v10_science import v10_plan


def fixture():
    start, end = 100*NS, 106*NS
    aliases = ('algorithm_state', 'v2_verification_guidance',
               'control_diagnostics', 'command_final', 'pose')
    streams = {'/'+alias: [] for alias in aliases}
    for index, (state, guide, command, pose) in enumerate(zip(*projected())):
        t = state['stamp_ns']; vector = [.02+index*.0001, 0., 0., 0., 0., 0.]
        messages = {
            'algorithm_state': Obj(stamp=stamp(t/NS), state_valid=True,
                state=state['state'], previous_state=state['previous_state']),
            'v2_verification_guidance': Obj(stamp=stamp(t/NS), valid=True,
                linear_x_mps=.02, angular_z_radps=0., reason='centered tracking'),
            'control_diagnostics': Obj(stamp=stamp(t/NS), final_command_valid=True,
                final_command=list(vector), gesc_command_unsaturated=list(vector),
                combined_command_unsaturated=list(vector),
                gesc_command_unsaturated_valid=True, combined_command_unsaturated_valid=True),
            'command_final': Obj(linear=Obj(x=vector[0], y=0., z=0.),
                                 angular=Obj(x=0., y=0., z=0.)),
            'pose': Obj(header=Obj(stamp=stamp(t/NS)),
                pose=Obj(pose=Obj(position=Obj(x=pose['x'], y=0.))),
                twist=Obj(twist=Obj(linear=Obj(x=.02, y=0.), angular=Obj(z=0.)))),
        }
        for alias, message in messages.items():
            bag_ns = start+t+(1_000_000 if alias == 'command_final' else 0)
            streams['/'+alias].append(BagRecord('/'+alias, 'fixture', bag_ns,
                None if alias == 'command_final' else t, None, False, message, True))
    return BagData(Path('/unused'), {},
        {alias: {'alias': alias, 'topic': '/'+alias} for alias in aliases},
        streams, start, end)


def measure(data, **kwargs):
    planned = v10_plan('C', experiment_version='m4-pilot-v11')
    planned['resolved_scenario']['algorithm']['launch_overrides']['algorithm_pose_topic'] = '/pose'
    return cli._motion_metrics(data, planned, {'complete': kwargs.get('authority', True)})


def extra_zero(data, alias, bag_ns):
    original = deepcopy(data.records_by_topic['/'+alias][0])
    if alias == 'command_final':
        original.message.linear.x = 0.
    else:
        original.message.final_command = [0.]*6
    row = replace(original, bag_timestamp_ns=bag_ns,
        in_readiness_interval=data.readiness_start_ns <= bag_ns <= data.readiness_end_ns)
    rows = data.records_by_topic['/'+alias]
    rows.append(row); rows.sort(key=lambda value: value.bag_timestamp_ns)


@pytest.mark.parametrize('alias', ['command_final', 'control_diagnostics'])
@pytest.mark.parametrize('outside', ['pre', 'post'])
def test_unpaired_zero_outside_readiness_cannot_shift_scientific_pairs(alias, outside):
    data = fixture()
    extra_zero(data, alias, data.readiness_start_ns-1 if outside == 'pre'
               else data.readiness_end_ns+1)
    result = measure(data)
    assert result['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    assert result['command_pairing_complete'] and not result['command_pairing_errors']
    assert result['diagnostic_count'] == result['actual_command_count'] == 51
    assert result['command_pairing_scope'] == 'recorded_readiness_interval_v1'
    counts = result['command_pairing_input_counts'][alias]
    assert counts == dict(full=52, within=51, pre=int(outside == 'pre'), post=int(outside == 'post'))
    assert result['zero_publication_count'] == 0


@pytest.mark.parametrize('fault', ['missing_command', 'extra_command', 'empty',
    'invalid_diagnostic', 'nonfinite_command', 'vector_mismatch', 'time_mismatch',
    'source_regression', 'reordered_commands'])
def test_in_interval_pairing_faults_remain_unavailable(fault):
    data = fixture(); commands = data.records_by_topic['/command_final']
    diagnostics = data.records_by_topic['/control_diagnostics']
    if fault == 'missing_command':
        commands.pop(20)
    elif fault == 'extra_command':
        extra_zero(data, 'command_final', 102*NS+500_000)
    elif fault == 'empty':
        commands.clear(); diagnostics.clear()
    elif fault == 'invalid_diagnostic':
        diagnostics[20].message.final_command_valid = False
    elif fault == 'nonfinite_command':
        commands[20].message.angular.y = float('nan')
    elif fault == 'vector_mismatch':
        commands[20].message.linear.y = .01
    elif fault == 'time_mismatch':
        commands[:] = [replace(r, bag_timestamp_ns=r.bag_timestamp_ns+499_000_001) for r in commands]
    elif fault == 'source_regression':
        diagnostics[20].message.stamp = stamp(1.8)
    elif fault == 'reordered_commands':
        commands[20], commands[21] = commands[21], commands[20]
    result = measure(data)
    assert not result['command_pairing_complete']
    assert result['status'] == 'EVIDENCE_UNAVAILABLE' and not result['analysis_complete']
    assert result['mandatory_stopped_acquisitions'] is None


@pytest.mark.parametrize('start,end', [(None,106*NS), (100*NS,None),
    (-1,106*NS), (100*NS,100*NS), (True,106*NS)])
def test_missing_or_unusable_readiness_bounds_never_certify_motion(start, end):
    result = measure(replace(fixture(), readiness_start_ns=start, readiness_end_ns=end))
    assert not result['command_pairing_readiness_bounds']['valid']
    assert not result['command_pairing_complete'] and result['status'] == 'EVIDENCE_UNAVAILABLE'


@pytest.mark.parametrize('edge', ['start', 'end'])
def test_counterparts_straddling_a_readiness_boundary_are_not_guessed(edge):
    data = fixture(); d=data.records_by_topic['/control_diagnostics']; c=data.records_by_topic['/command_final']
    index, boundary = (0,data.readiness_start_ns) if edge == 'start' else (-1,data.readiness_end_ns)
    d[index] = replace(d[index], bag_timestamp_ns=boundary+(1 if edge == 'start' else -1))
    c[index] = replace(c[index], bag_timestamp_ns=boundary+(-1 if edge == 'start' else 1),
                       in_readiness_interval=False)
    result = measure(data)
    assert result['diagnostic_count'] == 51 and result['actual_command_count'] == 50
    assert result['status'] == 'EVIDENCE_UNAVAILABLE' and not result['command_pairing_complete']


def test_both_boundary_stamps_and_inclusive_half_second_pair_bound_are_retained():
    data=fixture(); c=data.records_by_topic['/command_final']; d=data.records_by_topic['/control_diagnostics']
    c[:] = [replace(row, bag_timestamp_ns=row.bag_timestamp_ns+499_000_000) for row in c]
    d[-1] = replace(d[-1], bag_timestamp_ns=data.readiness_end_ns-500_000_000)
    c[-1] = replace(c[-1], bag_timestamp_ns=data.readiness_end_ns)
    result = measure(data)
    assert result['command_pairing_complete'] and result['analysis_complete']
    assert result['command_pairing_input_counts']['command_final']['within'] == 51


def test_inconsistent_readiness_flags_cannot_drop_matching_interior_rows():
    data = fixture()
    for alias in ('command_final', 'control_diagnostics'):
        records=data.records_by_topic['/'+alias]
        records[20]=replace(records[20], in_readiness_interval=False)
    result=measure(data)
    assert not result['command_pairing_readiness_bounds']['membership_valid']
    assert not result['command_pairing_complete'] and result['status'] == 'EVIDENCE_UNAVAILABLE'


def test_readiness_pairing_does_not_override_authority_or_legacy_motion_owner():
    data=fixture(); result=measure(data, authority=False)
    assert result['command_pairing_complete'] and result['status'] == 'EVIDENCE_UNAVAILABLE'
    planned=v10_plan('C', experiment_version='m4-pilot-v9')
    legacy=cli._motion_metrics(data, planned)
    data.records_by_topic['/command_final'].clear()
    changed=cli._motion_metrics(replace(data, readiness_start_ns=None, readiness_end_ns=None), planned)
    assert changed == legacy and legacy['status'] == 'OBSERVED_NO_MANDATORY_STOP'
    assert 'command_pairing_scope' not in legacy
