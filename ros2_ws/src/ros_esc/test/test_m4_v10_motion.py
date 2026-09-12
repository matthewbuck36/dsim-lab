"""Fixed V10 motion coverage and retained zero-publication semantics."""
from copy import deepcopy

import pytest
from ros_esc.plotting_scripts.m4_pilot import continuous_acquisition_metrics

NS = 1_000_000_000


def projected():
    states, guidance, commands, poses = [], [], [], []
    for i in range(51):
        t = i*100_000_000
        state = 2 if NS <= t < 3*NS else 3 if 3*NS <= t < 4*NS else 1
        states.append(dict(stamp_ns=t, valid=True, state=state, previous_state=2 if state == 3 else 1))
        guidance.append(dict(stamp_ns=t, valid=True, proposal_valid=True,
            proposal_nonzero=True, reason='centered tracking'))
        commands.append(dict(stamp_ns=t, bag_ns=100*NS+t, valid=True, zero=False))
        poses.append(dict(stamp_ns=t, valid=True, x=.02*t/NS, y=0., moving=True))
    return states, guidance, commands, poses


def measure(values, **kwargs):
    return continuous_acquisition_metrics(*values,
        **dict(dict(authority_complete=True, command_pairing_complete=True), **kwargs))


def test_source_covered_motion_establishes_verify_and_design_continuity():
    result = measure(projected())
    assert result['analysis_complete'] and result['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    assert result['mandatory_stopped_acquisitions'] == 0
    assert [r['state'] for r in result['acquisition_segments']] == [2,3]
    assert all(r['coverage_complete'] and r['positive_motion_evidence'] for r in result['acquisition_segments'])


def test_same_tick_zero_publication_retains_actual_bag_gap_without_invented_source_dwell():
    values = projected(); commands = values[2]
    original = deepcopy(commands[20])
    commands[20]['zero'] = True
    original['bag_ns'] += 25_659_000  # Retained D02 maximum-scale transient.
    commands.insert(21, original)
    result = measure(values)
    assert result['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    row = result['acquisition_segments'][0]['zero_publications'][0]
    assert row['duration_sec'] == 0. and row['bag_duration_sec'] == pytest.approx(.025659)
    assert result['zero_publication_count'] == 1


@pytest.mark.parametrize('channel', [0,1,2,3], ids=['state','guidance','command','pose'])
def test_missing_source_coverage_is_unavailable(channel):
    values = list(projected())
    values[channel] = [r for r in values[channel] if not 1.5*NS <= r['stamp_ns'] <= 2.1*NS]
    result = measure(values)
    assert result['status'] == 'EVIDENCE_UNAVAILABLE' and not result['analysis_complete']
    assert not result['acquisition_segments'][0]['coverage_complete']


@pytest.mark.parametrize('flag', ['authority_complete', 'command_pairing_complete'])
def test_invalid_authority_or_actual_command_pairing_never_certifies_motion(flag):
    result = measure(projected(), **{flag: False})
    assert not result['analysis_complete'] and result['mandatory_stopped_acquisitions'] is None


def test_sustained_measured_stop_is_complete_observation_without_claiming_mandatory_sweep():
    values = projected()
    for row in values[3]:
        if 1.2*NS <= row['stamp_ns'] <= 2*NS:
            row.update(moving=False, x=.024)
    result = measure(values)
    assert result['analysis_complete'] and result['status'] == 'OBSERVED_STATIONARY_INTERVAL'
    assert result['mandatory_stopped_acquisitions'] is None
    assert result['acquisition_segments'][0]['maximum_observed_stationary_duration_sec'] == pytest.approx(.8)


def test_sustained_zero_commands_are_separate_from_positive_measured_motion():
    values = projected()
    for row in values[2]:
        if 1.2*NS <= row['stamp_ns'] < 1.8*NS:
            row['zero'] = True
    result = measure(values)
    assert result['analysis_complete'] and result['status'] == 'OBSERVED_ZERO_COMMAND_INTERVAL'
    assert result['acquisition_segments'][0]['positive_motion_evidence']
    assert not result['acquisition_segments'][0]['sustained_stationary_interval']


def test_no_candidate_is_complete_negative_exposure_not_positive_acquisition():
    values = projected()
    for row in values[0]: row['state'] = 1
    result = measure(values)
    assert result['analysis_complete'] and result['status'] == 'NO_ACQUISITION_OBSERVED'
    assert result['acquisition_segment_count'] == 0 and result['mandatory_stopped_acquisitions'] is None


def test_unclosed_segment_reports_censoring_and_cannot_establish_continuity():
    values = [rows[:26] for rows in projected()]
    result = measure(values)
    assert not result['analysis_complete'] and result['acquisition_segments'][0]['censored']


def test_speed_claim_without_measured_path_is_insufficient():
    values = projected()
    for row in values[3]: row['x'] = 0.
    result = measure(values)
    assert result['status'] == 'EVIDENCE_UNAVAILABLE' and not result['analysis_complete']


def test_unbracketed_phase_edge_is_not_repaired_by_internal_dense_samples():
    values = list(projected())
    values[3] = [r for r in values[3] if r['stamp_ns'] > NS]
    result = measure(values)
    assert result['status'] == 'EVIDENCE_UNAVAILABLE'
    assert not result['acquisition_segments'][0]['coverage_complete']


@pytest.mark.parametrize('changed_command', [False, True])
@pytest.mark.parametrize('experiment_version', ['m4-pilot-v10', 'm4-pilot-v11'])
def test_actual_bagdata_projection_uses_selected_planar_motion_and_final_twist(changed_command, experiment_version):
    from dataclasses import replace
    from test_m4_evaluation_cli import cli, bag, Obj, stamp
    from test_m4_v10_science import v10_plan
    values = projected()
    streams = {name: [] for name in ('algorithm_state', 'v2_verification_guidance',
        'control_diagnostics', 'command_final', 'pose_delayed')}
    vector = [.02,0.,0.,0.,0.,0.]
    for state, guide, command, pose in zip(*values):
        t = state['stamp_ns']/NS
        streams['algorithm_state'].append((t, Obj(stamp=stamp(t), state_valid=True,
            state=state['state'], previous_state=state['previous_state'])))
        streams['v2_verification_guidance'].append((t, Obj(stamp=stamp(t), valid=True,
            linear_x_mps=.02, angular_z_radps=0., reason='centered tracking')))
        # Ordinary GESC diagnostics are invalid during the selected proposal.
        streams['control_diagnostics'].append((t, Obj(stamp=stamp(t), final_command_valid=True,
            final_command=list(vector), gesc_command_unsaturated_valid=False)))
        streams['command_final'].append((t+.001, Obj(linear=Obj(x=.02,y=0.,z=0.), angular=Obj(x=0.,y=0.,z=0.))))
        streams['pose_delayed'].append((t, Obj(header=Obj(stamp=stamp(t)),
            pose=Obj(pose=Obj(position=Obj(x=0.,y=pose['x']))),
            twist=Obj(twist=Obj(linear=Obj(x=0.,y=.02), angular=Obj(z=0.))))))
    if changed_command:
        streams['command_final'][20][1].linear.x = .03
    planned = v10_plan(experiment_version=experiment_version); planned['condition'] = 'delay'
    planned['resolved_scenario']['algorithm']['launch_overrides']['algorithm_pose_topic'] = '/pose_delayed'
    recorded = replace(bag(streams), readiness_start_ns=0, readiness_end_ns=6*NS)
    result = cli._motion_metrics(recorded, planned, {'complete': True})
    assert result['selected_pose_topic'] == '/pose_delayed'
    assert result['command_pairing_complete'] is (not changed_command)
    assert result['status'] == ('EVIDENCE_UNAVAILABLE' if changed_command else 'OBSERVED_CONTINUOUS_ACQUISITION')
