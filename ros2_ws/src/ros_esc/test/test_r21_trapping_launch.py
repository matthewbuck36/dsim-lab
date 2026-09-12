"""R21 actual launch selection and filtered science routing; no process launch."""
from copy import deepcopy

import pytest

from ros_esc.plotting_scripts.m4_pilot import science_aliases
from ros_esc.scenario_runner.run_scenario import build_launch_command
from ros_esc.scenario_runner.scenario_schema import _validate_correction_overrides
from ros_esc.v2_stream import TOPIC_KEYS
from test_q1_launch_frontend import parsed_launch  # noqa: F401
from test_q7_launch_selection import parameters
from test_v2_source_contract import resolved


POLICY = 'recurrent_trapping_v1'
SELECTED = dict(continuous_search_mode='rolling_gesc_v2',
    convergence_metric_mode='recurrent_geometry_v3',
    convergence_state_gating_enabled=True,
    v2_verification_motion_mode='centered_tracking_v1',
    v2_verification_evidence_policy=POLICY,
    v2_candidate_radius_m=.5, v2_candidate_epsilon_m=.06)


def test_actual_frontend_retains_default_policy_and_old_command_type_route(parsed_launch):
    context, owners = parameters(parsed_launch, {})
    assert context.launch_configurations['v2_verification_evidence_policy'] == 'angular_profiles_v1'
    for name in ('supervisor_node', 'gaussian_fill_node'):
        assert owners[name]['v2_verification_evidence_policy'] == 'angular_profiles_v1'
        assert owners[name]['v2_verification_motion_mode'] == 'rolling_neighborhood_v1'
        assert owners[name]['candidate_cost_mad_scale'] == 3.
    assert owners['gaussian_fill_node']['v2_fill_command_topic'] == '/gesc_gaussian/v2/fill_commands'


def test_actual_runner_frontend_forwards_one_selected_policy_and_shared_raw_scale(parsed_launch):
    run = resolved()
    run['algorithm']['launch_overrides'].update(SELECTED, candidate_cost_mad_scale=2.5)
    command = build_launch_command(run, run_id='r21_frontend')
    overrides = dict(arg.split(':=', 1) for arg in command[4:])
    _, owners = parameters(parsed_launch, overrides)
    for name in ('supervisor_node', 'gaussian_fill_node'):
        params = owners[name]
        assert params['v2_verification_evidence_policy'] == POLICY
        assert params['v2_verification_motion_mode'] == 'centered_tracking_v1'
        assert params['convergence_metric_mode'] == 'recurrent_geometry_v3'
        assert params['continuous_search_mode'] == 'rolling_gesc_v2'
        assert params['algorithm_profile'] == 'robust_gaussian_v1'
        assert params['candidate_cost_mad_scale'] == 2.5
    assert owners['supervisor_node']['use_sim_time'] is True
    assert owners['gaussian_fill_node']['v2_fill_command_topic'] == '/gesc_gaussian/v2/recurrent_fill_commands'
    assert 'v2_verification_evidence_policy' not in owners['convergence_detector_node']


def validate(overrides):
    _validate_correction_overrides(overrides,
        dict(gaussian_fill_enabled=True, affine_assist_enabled=True, recenter_enabled=True),
        'r21.launch_overrides')


def test_schema_accepts_explicit_selected_policy_and_preserves_old_default():
    validate(deepcopy(SELECTED))
    validate({})


@pytest.mark.parametrize('change', [
    dict(convergence_metric_mode='pde_mean_v1'),
    dict(continuous_search_mode='stationary_v1'),
    dict(v2_verification_motion_mode='rolling_neighborhood_v1'),
    dict(v2_verification_evidence_policy='unknown'),
])
def test_schema_rejects_incompatible_selected_policy(change):
    with pytest.raises(ValueError):
        validate({**SELECTED, **change})


def test_existing_filtered_science_union_keeps_selected_wrappers_and_old_union_exact():
    stream = {key: '/r21/'+key for key in TOPIC_KEYS}
    aliases = {'clock', 'algorithm_state', 'recording_ready',
        'v2_direction_diagnostics', 'v2_direction_policy_diagnostics',
        'v2_detector_confirmation', 'v2_search_epoch', 'v2_fill_results'}
    entries = [dict(alias=name, topic='/r21/'+name) for name in sorted(aliases)]
    entries += [dict(alias=key, topic=topic) for key, topic in stream.items()]
    old = [*entries, dict(alias='v2_candidate_snapshots', topic='/gesc_gaussian/v2/candidate_snapshots'),
        dict(alias='v2_fill_commands', topic='/gesc_gaussian/v2/fill_commands')]
    old_expected = aliases | set(stream) | {'v2_candidate_snapshots', 'v2_fill_commands'}
    assert set(science_aliases(old, pose_topic=stream['pose_topic'], stream_config=stream)) == old_expected
    selected = [*entries,
        dict(alias='v2_recurrent_candidate_snapshots', topic='/gesc_gaussian/v2/recurrent_candidate_snapshots'),
        dict(alias='v2_recurrent_fill_commands', topic='/gesc_gaussian/v2/recurrent_fill_commands')]
    assert set(science_aliases(selected, pose_topic=stream['pose_topic'], stream_config=stream)) == (
        aliases | set(stream) | {'v2_recurrent_candidate_snapshots', 'v2_recurrent_fill_commands'})
