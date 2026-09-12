"""Resolve actual Humble frontend arguments without starting launch actions."""

import json
from pathlib import Path

import pytest
import yaml
from launch import LaunchContext
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.frontend import Parser
from launch.launch_description_sources import get_launch_description_from_frontend_launch_file
from launch.utilities import perform_substitutions
from rclpy.utilities import remove_ros_args


PACKAGE = Path(__file__).resolve().parents[1]
LAUNCH = PACKAGE.parent / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
SCENARIO = PACKAGE / 'ros_esc/scenario_runner/scenarios/q1_primary_shadow_v1.yaml'
JSON_OWNERS = sorted([
    'cost_function_node', 'cost_function_node', 'filter_node', 'filter_node',
    'modified_cost_node', 'pde_history_node', 'convergence_detector_node',
    'gaussian_fill_node', 'supervisor_node',
])


@pytest.fixture
def parsed_launch(monkeypatch):
    def forbidden_execution(*args, **kwargs):
        pytest.fail('Frontend validation must not execute a process or timer')

    monkeypatch.setattr(ExecuteProcess, 'execute', forbidden_execution)
    monkeypatch.setattr(TimerAction, 'execute', forbidden_execution)
    # The complete XML is parsed, including commands in disabled branches and
    # the delayed controller. No LaunchService is created or run.
    return get_launch_description_from_frontend_launch_file(str(LAUNCH))


def _commands(description, overrides=None):
    context = LaunchContext()
    context.launch_configurations.update(overrides or {})
    for action in description.entities:
        if isinstance(action, DeclareLaunchArgument):
            if action.name not in context.launch_configurations:
                context.launch_configurations[action.name] = perform_substitutions(
                    context, action.default_value)

    def processes(actions):
        for action in actions:
            if type(action) is ExecuteProcess:
                yield action
            elif isinstance(action, TimerAction):
                yield from processes(action.actions)

    commands = []
    for action in processes(description.entities):
        argv = [perform_substitutions(context, arg) for arg in action.cmd]
        if argv[:3] == ['ros2', 'run', 'ros_esc']:
            commands.append(argv)
    return context, commands


def _assert_strings(commands, run_id, config, geometry=None):
    json_owners = []
    id_owners = []
    geometry_owners = []
    for argv in commands:
        if '--ros-args' in argv:
            # Exercise the real RCL command-line parser with the resolved YAML
            # overrides. This parses arguments without creating a ROS context/node.
            remove_ros_args(args=argv)
        for index, arg in enumerate(argv):
            if arg.startswith('--v2-run-id='):
                assert arg == '--v2-run-id=' + run_id
                id_owners.append(argv[3])
            elif arg.startswith('v2_run_id:='):
                assert argv[index - 1] == '-p'
                assert type(yaml.safe_load(arg.split(':=', 1)[1])) is str
                assert yaml.safe_load(arg.split(':=', 1)[1]) == run_id
                id_owners.append(argv[3])
            elif arg.startswith('--v2-stream-config-json='):
                assert arg == '--v2-stream-config-json=' + config
                json_owners.append(argv[3])
            elif arg.startswith('v2_stream_config_json:='):
                assert argv[index - 1] == '-p'
                restored = yaml.safe_load(arg.split(':=', 1)[1])
                assert type(restored) is str
                assert restored == config
                json_owners.append(argv[3])
            elif arg.startswith('--v2-sensor-geometry-config=') and geometry is not None:
                assert arg == '--v2-sensor-geometry-config=' + geometry
                geometry_owners.append(argv[3])
    assert sorted(json_owners) == JSON_OWNERS
    assert sorted(id_owners) == sorted(JSON_OWNERS + ['controller_node'])
    if geometry is not None:
        assert geometry_owners == ['cost_function_node', 'cost_function_node']


def test_actual_humble_frontend_preserves_empty_legacy_defaults(parsed_launch):
    context, commands = _commands(parsed_launch)
    assert context.launch_configurations['continuous_search_mode'] == 'stationary_v1'
    assert context.launch_configurations['v2_qualification_observation_only'] == 'false'
    _assert_strings(commands, '', '')


@pytest.mark.parametrize('run_id', ['q1-source-v2', '123', 'false'])
@pytest.mark.parametrize('version', [1, 2])
def test_populated_cli_and_yaml_strings_are_atomic_after_substitution(parsed_launch, run_id, version):
    from test_v2_stream import descriptor

    # Valid descriptors have structural JSON quotes/punctuation and may have
    # spaces. Their fixed grammar contains no apostrophes. No arbitrary-payload
    # quoting contract is claimed for an invalid descriptor.
    config = json.dumps(descriptor(version), sort_keys=True)
    assert ' ' in config and '"' in config and "'" not in config
    geometry = '/tmp/geometry with spaces; apostrophe\'s [v2].json'
    _, commands = _commands(parsed_launch, {
        'continuous_search_mode': 'rolling_gesc_v2',
        'v2_run_id': run_id,
        'v2_stream_config_json': config,
        'sensor_transform_config_filepath': geometry,
    })
    _assert_strings(commands, run_id, config, geometry)


@pytest.mark.parametrize('case_index', range(4))
def test_actual_q1_runner_arguments_reach_every_selected_owner(parsed_launch, case_index):
    from ros_esc.scenario_runner.run_scenario import build_launch_command
    from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite

    runs, _ = expand_suite(load_suite(SCENARIO))
    run_id = f'q1-frontend-{case_index}'
    command = build_launch_command(runs[case_index], run_id=run_id)
    assert command[:4] == ['ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml']
    overrides = dict(argument.split(':=', 1) for argument in command[4:])
    context, commands = _commands(parsed_launch, overrides)
    assert context.launch_configurations['continuous_search_mode'] == 'rolling_gesc_v2'
    assert context.launch_configurations['v2_qualification_observation_only'].lower() == 'true'
    _assert_strings(commands, run_id, overrides['v2_stream_config_json'])


@pytest.mark.parametrize('broken_command', [
    "owner --v2-run-id='$(var v2_run_id)'",
    "owner --v2-stream-config-json='$(var v2_stream_config_json)'",
    "owner --ros-args -p 'v2_stream_config_json:=|-\n  $(var v2_stream_config_json)'",
])
def test_retained_failure_is_static_fragment_quoting(broken_command):
    with pytest.raises(ValueError, match='No closing quotation'):
        ExecuteProcess._parse_cmdline(broken_command, Parser())


@pytest.mark.parametrize('version, run_id', [(None, ''), (1, '123'), (2, 'false')])
def test_actual_rcl_parameter_values_remain_strings(parsed_launch, version, run_id):
    import rclpy
    from rclpy.context import Context
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from test_v2_stream import descriptor

    config = '' if version is None else json.dumps(descriptor(version), sort_keys=True)
    _, commands = _commands(parsed_launch, {
        'v2_run_id': run_id, 'v2_stream_config_json': config,
    })
    argv = next(command for command in commands if command[3] == 'supervisor_node')
    selected = [value for value in argv if value.startswith(
        ('v2_run_id:=', 'v2_stream_config_json:='))]
    assert len(selected) == 2
    ros_args = ['--ros-args']
    for value in selected:
        ros_args.extend(['-p', value])
    context = Context()
    rclpy.init(args=[], context=context)
    node = None
    try:
        # An inert parameter-only node verifies the actual RCL YAML types. It
        # does not create any algorithm owner, executor, command or simulator.
        node = Node('q1_frontend_parameter_probe', context=context, cli_args=ros_args,
                    start_parameter_services=False, enable_rosout=False)
        for name, expected in [('v2_run_id', run_id), ('v2_stream_config_json', config)]:
            parameter = node.declare_parameter(name, '')
            assert parameter.type_ == Parameter.Type.STRING
            assert parameter.value == expected
    finally:
        if node is not None:
            node.destroy_node()
        context.shutdown()
