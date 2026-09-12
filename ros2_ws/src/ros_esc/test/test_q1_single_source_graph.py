"""Selected simulation source graph and recorder gates; no processes launched."""

from copy import deepcopy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
import yaml
from launch import LaunchContext
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import get_launch_description_from_frontend_launch_file
from launch.utilities import perform_substitutions
from launch_ros.actions import Node

from ros_esc.experiment_recording import record_run as recorder, validate_run as validator
from test_v2_recording_contract import prepared


PACKAGE = Path(__file__).resolve().parents[1]
CONTROL = PACKAGE.parent / 'turtlebot3_rotating_sensor/launch/control.launch.py'
GAZEBO = CONTROL.with_name('gazebo.launch.xml')
MANIFEST = PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml'


@pytest.fixture
def control(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Launch selection tests must not execute a process')

    monkeypatch.setattr(ExecuteProcess, 'execute', forbidden)
    monkeypatch.setattr(Node, 'execute', forbidden)
    spec = importlib.util.spec_from_file_location('q1_control_launch', CONTROL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _argv(action, context):
    return [perform_substitutions(context, argument) for argument in action.cmd]


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('recovery', ['False', 'True'])
def test_actual_gazebo_include_and_spawner_actions_select_one_or_two_sources(control, mode, recovery, monkeypatch):
    description = get_launch_description_from_frontend_launch_file(str(GAZEBO))
    context = LaunchContext()
    context.launch_configurations.update(continuous_search_mode=mode,
                                        controller_spawner_load_recovery_enabled=recovery)
    include = next(action for action in description.entities
                   if isinstance(action, IncludeLaunchDescription)
                   and 'continuous_search_mode' in {
                       perform_substitutions(context, name) for name, _ in action.launch_arguments})
    forwarded = {perform_substitutions(context, name): perform_substitutions(context, value)
                 for name, value in include.launch_arguments}
    assert forwarded == {'continuous_search_mode': mode,
                         'controller_spawner_load_recovery_enabled': recovery}
    child_context = LaunchContext()
    child_context.launch_configurations.update(forwarded)
    # Resolve the real frontend include path, then load the current source
    # module rather than the intentionally not-yet-rebuilt installed copy.
    def load_current_control(location):
        assert Path(location).name == 'control.launch.py'
        return control.generate_launch_description()

    monkeypatch.setattr(include.launch_description_source, '_get_launch_description', load_current_control)
    child_description = include.launch_description_source.get_launch_description(context)
    declarations = {action.name: perform_substitutions(child_context, action.default_value)
                    for action in child_description.entities if isinstance(action, DeclareLaunchArgument)}
    assert declarations['continuous_search_mode'] == 'stationary_v1'
    assert declarations['controller_spawner_load_recovery_enabled'] == 'False'
    selection = next(action for action in child_description.entities if isinstance(action, OpaqueFunction))
    actions = selection.execute(child_context)  # Constructs Node actions; never executes them.
    commands = [_argv(action, child_context) for action in actions]
    controllers = ['joint_state_broadcaster', 'velocity_controller'] if mode == 'stationary_v1' else ['velocity_controller']
    if recovery == 'True':
        assert len(commands) == 1
        assert Path(commands[0][0]).name == 'idempotent_controller_spawner.py'
        assert commands[0][1:] == controllers + ['--service-call-timeout', '30.0', '--ros-args']
    else:
        assert len(commands) == len(controllers)
        for command, controller_name in zip(commands, controllers):
            assert Path(command[0]).name == 'spawner'
            assert command[1:] == [controller_name, '--service-call-timeout', '30.0', '--ros-args']
    # The selected URDF source/rate/topic remains intact in both launch modes.
    urdf = ET.parse(PACKAGE.parent / 'turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf')
    plugin = urdf.find(".//plugin[@name='turtlebot3_joint_state']")
    assert plugin.get('filename') == 'libgazebo_ros_joint_state_publisher.so'
    assert plugin.findtext('update_rate') == '30'
    assert plugin.findtext('joint_name') == 'rotating_frame_joint'
    assert plugin.findtext('ros/remapping') == '~/out:=joint_states'


def test_direct_controller_include_default_preserves_legacy_and_rejects_unknown_mode(control):
    context = LaunchContext()
    context.launch_configurations['controller_spawner_load_recovery_enabled'] = 'False'
    assert len(control._controller_spawners(context)) == 2
    context.launch_configurations['continuous_search_mode'] = 'misspelled_mode'
    with pytest.raises(ValueError, match='unsupported continuous_search_mode'):
        control._controller_spawners(context)


def inputs(mode='rolling_gesc_v2', delay=0.):
    target, metadata, manifest = prepared(delay)
    if mode == 'stationary_v1':
        target = [argument for argument in target
                  if not argument.startswith(('continuous_search_mode:=', 'v2_'))]
        metadata['scenario_runner'].pop('v2_identity')
    config = recorder.operational_config_for_mode(manifest, 'simulation')
    entries = recorder.applicable_topics(manifest, 'simulation')
    return target, metadata, manifest, config, entries


def selected(mode='rolling_gesc_v2', delay=0.):
    target, metadata, manifest, config, entries = inputs(mode, delay)
    result, selected_config = recorder.resolve_operational_target_config(entries, config, metadata, target)
    joint = next(entry for entry in result if entry['alias'] == 'joint_states')
    return joint, selected_config


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('delay', [0., .1])
def test_selected_recorder_contract_matches_graph_without_mutating_base_manifest(mode, delay, tmp_path):
    target, metadata, manifest, config, entries = inputs(mode, delay)
    original = deepcopy((manifest, config, entries))
    result, derived = recorder.resolve_operational_target_config(entries, config, metadata, target)
    assert (manifest, config, entries) == original
    joint = next(entry for entry in result if entry['alias'] == 'joint_states')
    if mode == 'rolling_gesc_v2':
        assert joint['expected_publishers'] == ['/turtlebot3_joint_state']
        assert joint['singleton_publisher'] is True
        assert joint['timestamp_ordering'] == 'single_stream'
        assert derived['required_active_controllers'] == ['velocity_controller']
    else:
        assert joint == next(entry for entry in entries if entry['alias'] == 'joint_states')
        assert derived['required_active_controllers'] == ['joint_state_broadcaster', 'velocity_controller']
        assert joint['timestamp_ordering'] == 'multi_publisher_within_clock'
    assert recorder.topic_evidence_contract_errors(joint) == []
    assert derived['target_disturbance_coupling']['sensor_delay_sec'] == delay
    assert derived['target_disturbance_coupling']['pose_delay_sec'] == 0.
    assert derived['target_disturbance_coupling']['consumer_topics']['sensor_delay_sec']
    path = tmp_path / 'resolved_topics.yaml'
    recorder.atomic_yaml(path, {'topics': result, 'operational_readiness': {'configuration': derived}})
    retained = yaml.safe_load(path.read_text())
    assert retained['topics'] == result
    assert retained['operational_readiness']['configuration'] == derived
    assert recorder.load_manifest(MANIFEST) == manifest


@pytest.mark.parametrize('owners, passed', [
    (['/turtlebot3_joint_state'], True), ([], False),
    (['/joint_state_broadcaster'], False), (['/unexpected'], False),
    (['/turtlebot3_joint_state', '/joint_state_broadcaster'], False),
    (['/turtlebot3_joint_state', '/turtlebot3_joint_state'], False),
])
def test_v2_readiness_requires_exact_single_expected_publisher(owners, passed):
    joint, config = selected()
    errors = recorder.preflight_errors([joint], {'/joint_states': [joint['type']]},
                                      {'/joint_states': owners}, {'/joint_states'}, True, True)
    assert (not errors) is passed


@pytest.mark.parametrize('states, passed', [
    ([('velocity_controller', 'active')], True), ([], False),
    ([('velocity_controller', 'inactive')], False),
    ([('joint_state_broadcaster', 'active')], False),
])
def test_v2_requires_active_velocity_control(states, passed):
    joint, config = selected()
    error = recorder.controller_state_error(
        [SimpleNamespace(name=name, state=state) for name, state in states],
        config['required_active_controllers'])
    assert (error is None) is passed


def test_legacy_readiness_still_requires_both_publishers_and_controllers():
    joint, config = selected('stationary_v1')
    both = ['/joint_state_broadcaster', '/turtlebot3_joint_state']
    assert recorder.expected_publisher_error(joint, both) is None
    assert recorder.expected_publisher_error(joint, both[1:]) is not None
    assert recorder.controller_state_error([SimpleNamespace(name='velocity_controller', state='active')]) is not None
    assert recorder.controller_state_error([SimpleNamespace(name=name, state='active')
                                            for name in config['required_active_controllers']]) is None
    assert recorder.operational_config_for_mode(recorder.load_manifest(MANIFEST), 'physical') == {}
    assert 'joint_states' not in {entry['alias'] for entry in recorder.applicable_topics(
        recorder.load_manifest(MANIFEST), 'physical')}


@pytest.mark.parametrize('fault', ['target_prefix', 'run_id', 'missing_identity', 'delay', 'consumer'])
def test_source_selection_requires_validated_target_metadata_and_delayed_consumers(fault):
    target, metadata, manifest, config, entries = inputs(delay=.1)
    if fault == 'target_prefix':
        target[3] = 'other.launch.xml'
    elif fault == 'run_id':
        target = [argument.replace('v2_run_id:=run_test', 'v2_run_id:=wrong') for argument in target]
    elif fault == 'missing_identity':
        metadata['scenario_runner'].pop('v2_identity')
    elif fault == 'delay':
        target = [argument.replace('simulation_sensor_delay_sec:=0.1', 'simulation_sensor_delay_sec:=0.0') for argument in target]
    else:
        target = [argument.replace('pde_cost_history_topic:=/gesc_gaussian/simulation/raw_cost_delayed',
                                   'pde_cost_history_topic:=/turtlebot3/cost_value_chatter') for argument in target]
    before = deepcopy((entries, config))
    with pytest.raises(ValueError):
        recorder.resolve_operational_target_config(entries, config, metadata, target)
    assert (entries, config) == before


@pytest.mark.parametrize('fault', ['publisher', 'controller'])
def test_derivation_does_not_silently_repair_an_invalid_base_contract(fault):
    target, metadata, manifest, config, entries = inputs()
    entries = deepcopy(entries)
    if fault == 'publisher':
        next(entry for entry in entries if entry['alias'] == 'joint_states')['expected_publishers'] = ['/unexpected']
    else:
        config['required_active_controllers'] = ['joint_state_broadcaster']
    with pytest.raises(ValueError, match='contract'):
        recorder.resolve_operational_target_config(entries, config, metadata, target)


def test_actual_record_run_derives_v2_contract_before_any_runtime_start(monkeypatch, tmp_path):
    target, metadata, manifest, config, entries = inputs()
    captured = []
    original = recorder.resolve_operational_target_config

    def observe(*args):
        result = original(*args)
        captured.append(result)
        return result

    def before_runtime():
        raise RuntimeError('test stops after source contract derivation before runtime')

    monkeypatch.setattr(recorder, 'resolve_operational_target_config', observe)
    monkeypatch.setattr(recorder, 'load_metadata_input', lambda *_: metadata)
    monkeypatch.setattr(recorder.rosbag2_py, 'get_registered_writers', before_runtime)
    monkeypatch.setattr(recorder.rclpy, 'init', lambda **_: pytest.fail('ROS must not initialize'))
    arguments = SimpleNamespace(manifest=str(MANIFEST), metadata_input='unused',
                                mode='simulation', target=target, storage_id='sqlite3',
                                runs_root=str(tmp_path / 'must_not_exist'))
    with pytest.raises(RuntimeError, match='before runtime'):
        recorder.run(arguments)
    assert len(captured) == 1
    joint = next(entry for entry in captured[0][0] if entry['alias'] == 'joint_states')
    assert joint['expected_publishers'] == ['/turtlebot3_joint_state']
    assert captured[0][1]['required_active_controllers'] == ['velocity_controller']
    assert not Path(arguments.runs_root).exists()


@pytest.mark.parametrize('mode,publishers,reversed_stamps,publishers_pass,ordering_pass', [
    ('rolling_gesc_v2', ['/turtlebot3_joint_state'], False, True, True),
    ('rolling_gesc_v2', ['/turtlebot3_joint_state'], True, True, False),
    ('rolling_gesc_v2', ['/turtlebot3_joint_state', '/joint_state_broadcaster'], False, False, True),
    ('stationary_v1', ['/joint_state_broadcaster', '/turtlebot3_joint_state'], True, True, True),
    ('stationary_v1', ['/turtlebot3_joint_state'], True, False, False),
])
def test_offline_validator_uses_retained_selected_contract_and_preserves_old_bags(
        monkeypatch, tmp_path, mode, publishers, reversed_stamps, publishers_pass, ordering_pass):
    """Exercise central checker wiring, with only source/clock bag records."""
    target, metadata, manifest, config, entries = inputs(mode)
    entries, config = recorder.resolve_operational_target_config(entries, config, metadata, target)
    for entry in entries:
        entry['publishers'] = list(entry.get('expected_publishers', ()))
    joint = next(entry for entry in entries if entry['alias'] == 'joint_states')
    joint['publishers'] = publishers
    metadata.update(target_argv=target, run_id='run_test', git={}, recording={})
    recorder.atomic_yaml(tmp_path / 'metadata.yaml', metadata)
    recorder.atomic_yaml(tmp_path / 'resolved_topics.yaml', {
        'topics': entries, 'validation': manifest['validation'],
        'operational_readiness': {'configuration': config},
    })
    recorder.atomic_yaml(tmp_path / 'resolved_parameters.yaml', {'failures': []})
    (tmp_path / 'notes.md').write_text('Synthetic source contract checker fixture.\n')
    (tmp_path / 'console.log').write_text('')

    def stamp(nanoseconds):
        return SimpleNamespace(sec=nanoseconds // 1_000_000_000,
                               nanosec=nanoseconds % 1_000_000_000)

    source_stamps = [1_200_000_000, 1_800_000_000]
    if reversed_stamps:
        source_stamps.reverse()
    messages = {
        '/clock': [(1, SimpleNamespace(clock=stamp(1_000_000_000))),
                   (100, SimpleNamespace(clock=stamp(3_000_000_000)))],
        '/joint_states': [(20 + index, SimpleNamespace(header=SimpleNamespace(stamp=stamp(value))))
                          for index, value in enumerate(source_stamps)],
    }
    bag_types = {entry['topic']: entry['type'] for entry in entries}
    monkeypatch.setattr(validator, '_read_bag', lambda *_: (bag_types, messages))
    # No current manifest is loaded during old-bag validation: the durable
    # resolved contract, including its original publisher mode, is authoritative.
    monkeypatch.setattr(recorder, 'load_manifest', lambda *_: pytest.fail('must use recorded contract'))
    report = validator.validate_run_directory(tmp_path, write_report=False)
    assert report['checks']['timestamp_ordering_contract_valid']['passed']
    assert report['checks']['expected_publishers_match']['passed'] is publishers_pass
    assert report['checks']['typed_timestamps_nonregressing']['passed'] is ordering_pass
    assert report['checks']['typed_timestamps_within_clock']['passed']
    scoped = report['checks']['multi_publisher_timestamp_scope']['detail']
    assert bool(scoped) is (mode == 'stationary_v1' and publishers_pass)
    if scoped:
        assert scoped[0]['topic'] == '/joint_states'
