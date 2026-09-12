"""Strict opt-in admission and existing frontend/recorder heartbeat binding."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import time

import pytest
import rclpy
from rclpy.exceptions import InvalidParameterTypeException, ParameterUninitializedException
import yaml

from ros_esc.convergence_detector_node.convergence_detector_node_script import ConvergenceDetector
from ros_esc.experiment_recording.record_run import require_selected_algorithm_topics
from ros_esc.scenario_runner.scenario_schema import _validate_correction_overrides, expand_suite, load_suite
from ros_esc.scenario_runner.run_scenario import build_launch_command
from test_q1_launch_frontend import parsed_launch  # noqa: F401
from test_q7_launch_selection import parameters
from test_q7_recording_selection import entries, target, PACKAGE, ALIAS

OPTION = 'centroid_invalid_status_heartbeat_enabled'
MARKER = 'algorithm_invalid_status_heartbeat_enabled'
MODES = ('centroid_windows_v2', 'centroid_two_block_v2')
BEFORE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_centroid_heartbeat_v1/before_v1')


@pytest.mark.parametrize('metric,sim_time', [('pde_mean_v1', 'true'), *[(mode, 'false') for mode in MODES]])
def test_true_requires_centroid_and_actual_simulation_clock(metric, sim_time):
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:='+sim_time,
        '-p', 'algorithm_profile:=robust_gaussian_v1', '-p', 'state_gating_enabled:=true',
        '-p', 'convergence_metric_mode:='+metric, '-p', OPTION+':=true'])
    try:
        with pytest.raises(ValueError, match='requires centroid simulation'):
            ConvergenceDetector()
    finally:
        rclpy.shutdown()


@pytest.mark.parametrize('value', ["'false'", '1', '[]'])
def test_runtime_boolean_does_not_accept_truthy_nonbooleans(value):
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true', '-p', OPTION+':='+value])
    try:
        with pytest.raises((InvalidParameterTypeException, ParameterUninitializedException, ValueError)):
            ConvergenceDetector()
    finally:
        rclpy.shutdown()


@pytest.mark.parametrize('metric', MODES)
@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
def test_actual_frontend_forwards_selected_flag_to_detector_only(parsed_launch, metric, mode):
    _, owners = parameters(parsed_launch, dict(algorithm_profile='robust_gaussian_v1',
        convergence_metric_mode=metric, continuous_search_mode=mode, **{OPTION:'True'}))
    assert owners['convergence_detector_node'][OPTION] is True
    assert all(OPTION not in owners[key] for key in ('supervisor_node', 'gaussian_fill_node'))
    _, old = parameters(parsed_launch, {})
    assert old['convergence_detector_node'][OPTION] is False


@pytest.mark.parametrize('metric', MODES)
@pytest.mark.parametrize('selected', [None, 'false', 'False'])
def test_recorder_default_false_matches_exact_retained_behavior(metric, selected):
    path=BEFORE/'ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py'
    spec=importlib.util.spec_from_file_location('heartbeat_old_record_run', path)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    argv=target(metric)+([] if selected is None else [OPTION+':='+selected])
    current=require_selected_algorithm_topics(entries(), 'simulation', argv)
    assert current == old.require_selected_algorithm_topics(entries(), 'simulation', argv)
    assert all(MARKER not in entry for entry in current)


@pytest.mark.parametrize('metric', MODES)
def test_recording_selected_descriptor_is_exact_and_idempotent(metric):
    original=entries();retained=deepcopy(original);argv=target(metric)+[OPTION+':=True']
    selected=require_selected_algorithm_topics(original, 'simulation', argv)
    assert original==retained
    entry=next(row for row in selected if row['alias']==ALIAS)
    assert entry[MARKER] is True and entry['algorithm_maximum_diagnostic_gap_sec']==1.
    assert require_selected_algorithm_topics(selected, 'simulation', argv)==selected
    for changed in [target(metric), target(metric)+[OPTION+':=False']]:
        with pytest.raises(ValueError, match='heartbeat differs'):
            require_selected_algorithm_topics(selected, 'simulation', changed)
    old=require_selected_algorithm_topics(original,'simulation',target(metric))
    with pytest.raises(ValueError, match='lacks selected'):
        require_selected_algorithm_topics(old,'simulation',argv)


@pytest.mark.parametrize('value', ['1', '', 'null', 'yes', "'false'"])
def test_recorder_rejects_malformed_selector_before_pde_early_return(value):
    with pytest.raises(ValueError, match='must be true or false'):
        require_selected_algorithm_topics(entries(),'simulation',target('pde_mean_v1')+[OPTION+':='+value])


@pytest.mark.parametrize('metric,environment', [('pde_mean_v1','simulation'),*[(mode,'physical') for mode in MODES]])
def test_recorder_rejects_incompatible_selected_route(metric,environment):
    with pytest.raises(ValueError, match='requires centroid simulation'):
        require_selected_algorithm_topics(entries(),environment,target(metric)+[OPTION+':=true'])


@pytest.mark.parametrize('value', ['false', 1, None, []])
def test_schema_requires_true_boolean(value):
    with pytest.raises(ValueError, match='must be true or false'):
        _validate_correction_overrides({OPTION:value},{},'heartbeat')


def test_schema_does_not_accept_true_on_pde():
    with pytest.raises(ValueError, match='requires centroid mode'):
        _validate_correction_overrides({OPTION:True},{},'heartbeat')


def test_existing_no_argument_moving_readiness_keeps_ordinary_rollback_reset():
    from test_v2_epoch_binding import Host, arm, V2DetectorBinding
    node = Host(centroid=True)
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    adapter.latest_pose_steady_ns = time.monotonic_ns()
    assert adapter.centroid_ready()
    resets = node.reset_count
    node.now_ns -= 1
    assert not adapter.centroid_ready()
    assert adapter.binding.context is None
    assert node.reset_count > resets
    assert adapter.binding.last_now_ns == node.now_ns


@pytest.mark.parametrize('metric', MODES)
@pytest.mark.parametrize('mode', ['stationary_v1','rolling_gesc_v2'])
def test_actual_schema_roundtrip_retains_selection_and_existing_gates(tmp_path,metric,mode):
    original=PACKAGE/'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
    retained=original.read_bytes();document=yaml.safe_load(retained);case=document['cases'][0]
    case['profiles']=['robust_gaussian_v1']
    case['algorithm']['launch_overrides']={OPTION:True,'convergence_metric_mode':metric,
        'continuous_search_mode':mode,'convergence_state_gating_enabled':True}
    if mode=='rolling_gesc_v2':
        case['algorithm']['launch_overrides'].update(v2_candidate_radius_m=.75,v2_candidate_epsilon_m=.15)
    path=tmp_path/'heartbeat.yaml';path.write_text(yaml.safe_dump(document))
    runs,_=expand_suite(load_suite(path));assert len(runs)==1
    argv=build_launch_command(runs[0],run_id='heartbeat-selection')
    assert OPTION+':=True' in argv
    descriptor=next(row for row in require_selected_algorithm_topics(entries(),'simulation',argv) if row['alias']==ALIAS)
    assert descriptor[MARKER] is True
    assert original.read_bytes()==retained
