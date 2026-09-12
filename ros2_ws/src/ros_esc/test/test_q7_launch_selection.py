"""Actual Humble frontend selection; process execution is forbidden."""

import pytest
import yaml
from rclpy.utilities import remove_ros_args

from ros_esc.scenario_runner.run_scenario import build_launch_command
from test_q1_launch_frontend import _commands, parsed_launch  # noqa: F401
from test_v2_source_contract import resolved


MODES = ('pde_mean_v1', 'centroid_windows_v2', 'centroid_two_block_v2')
OWNERS = ('convergence_detector_node', 'supervisor_node', 'gaussian_fill_node')


def parameters(description, overrides):
    context, commands = _commands(description, overrides)
    selected = {}
    for argv in commands:
        if '--ros-args' in argv:
            remove_ros_args(args=argv)
        if argv[3] in OWNERS:
            selected[argv[3]] = {
                arg.split(':=', 1)[0]: yaml.safe_load(arg.split(':=', 1)[1])
                for index, arg in enumerate(argv) if index and argv[index-1] == '-p'}
    assert set(selected) == set(OWNERS)
    return context, selected


@pytest.mark.parametrize('metric', MODES)
@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('ready', ['False', 'True'])
def test_actual_frontend_selects_exact_metric_and_stationary_pose_owner(
        parsed_launch, metric, mode, ready):
    overrides = dict(algorithm_profile='robust_gaussian_v1',
        convergence_metric_mode=metric, continuous_search_mode=mode,
        entity_name='q7_probe', algorithm_pose_topic='/q7/selected',
        gaussian_fill_pose_topic='/q7/fill', recording_ready_required=ready)
    context, selected = parameters(parsed_launch, overrides)
    for params in selected.values():
        assert params['convergence_metric_mode'] == metric
        assert params['continuous_search_mode'] == mode
        assert params['recording_ready_required'] is (ready == 'True')
        assert params['centroid_window_sec'] == 3.
        assert params['centroid_epsilon_m'] == .06
        assert params['centroid_maximum_radius_m'] == .5
        assert params['centroid_pose_stale_sec'] == .5
    stationary_centroid = metric != 'pde_mean_v1' and mode == 'stationary_v1'
    assert selected['gaussian_fill_node']['pose_topic'] == (
        '/q7/selected' if stationary_centroid else '/q7/fill')
    assert selected['supervisor_node']['pose_topic'] == '/q7/selected'
    assert selected['convergence_detector_node']['pose_topic'] == '/q7/selected'
    for owner in ('gaussian_fill_node', 'supervisor_node'):
        assert selected[owner]['timekeeper_topic'] == '/q7_probe/timekeeper_chatter'
        assert selected[owner]['fill_design_timeout_sec'] == 5.
    assert float(context.launch_configurations['centroid_maximum_gap_sec']) == .5


def test_actual_frontend_legacy_default_and_explicit_two_block_parameters(parsed_launch):
    context, _ = parameters(parsed_launch, {})
    assert context.launch_configurations['convergence_metric_mode'] == 'pde_mean_v1'
    _, selected = parameters(parsed_launch, dict(
        convergence_metric_mode='centroid_two_block_v2', centroid_window_sec='6.0',
        centroid_epsilon_m='0.18', centroid_maximum_radius_m='0.50'))
    for params in selected.values():
        assert (params['centroid_window_sec'], params['centroid_epsilon_m'],
                params['centroid_maximum_radius_m']) == (6., .18, .5)


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('metric', MODES)
@pytest.mark.parametrize('pose_delay,sensor_delay', [(0., 0.), (.1, .1)])
def test_runner_disturbance_routing_survives_actual_frontend(
        parsed_launch, mode, metric, pose_delay, sensor_delay):
    run = resolved(pose_delay=pose_delay, sensor_delay=sensor_delay)
    run['algorithm']['launch_overrides'].update(
        continuous_search_mode=mode, convergence_metric_mode=metric)
    command = build_launch_command(run, run_id='q7_frontend')
    overrides = dict(arg.split(':=', 1) for arg in command[4:])
    context, selected = parameters(parsed_launch, overrides)
    expected_pose = '/gesc_gaussian/simulation/pose_delayed' if pose_delay else '/odom'
    assert context.launch_configurations['simulation_pose_delay_sec'] == str(pose_delay)
    assert context.launch_configurations['algorithm_pose_topic'] == expected_pose
    assert context.launch_configurations['algorithm_source_cost_topic'] == (
        '/gesc_gaussian/simulation/source_cost_delayed' if sensor_delay
        else '/gesc_gaussian/source_cost')
    for params in selected.values():
        assert params['convergence_metric_mode'] == metric
        assert params['pose_topic'] == expected_pose
