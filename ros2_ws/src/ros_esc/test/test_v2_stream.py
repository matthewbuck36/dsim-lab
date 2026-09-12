"""Source-independent contract identity, timestamp and geometry regressions."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
import yaml
from launch import LaunchContext
from launch.actions import ExecuteProcess
from launch.frontend import Parser
from launch.utilities import perform_substitutions

from ros_esc.v2_stream import (
    SUPPORTED_GEOMETRY, TOPIC_KEYS, canonical_json, relative_stamp_ns,
    sensor_geometry_descriptor, set_time, stream_contract_id, time_to_ns,
    validate_mode_identity, validate_stream_config,
)


def descriptor(version=1):
    result = {**{key: '/test/' + key for key in TOPIC_KEYS},
              'schema_version': version, 'selected_channel': 0, 'frame_id': 'odom',
              'sensor_geometry_config_sha256': 'a' * 64,
              'sensor_geometry': dict(SUPPORTED_GEOMETRY)}
    if version == 2:
        result['cost_key_basis'] = 'model_input_time'
    return result


def resolve_frontend_command(command, values):
    """Humble tokenizes static fragments before atomically resolving values."""
    context = LaunchContext()
    context.launch_configurations.update(values)
    return [perform_substitutions(context, argument)
            for argument in ExecuteProcess._parse_cmdline(command, Parser())]


@pytest.mark.parametrize('version', [1, 2])
def test_canonical_identity_ignores_json_key_order_but_binds_origin_and_topics(version):
    config = descriptor(version)
    permuted = dict(reversed(list(config.items())))
    expected = stream_contract_id(config, 123)
    assert stream_contract_id(json.dumps(permuted, indent=2), 123) == expected
    assert stream_contract_id(config, 124) != expected
    config['pose_topic'] = '/delayed_pose'
    assert stream_contract_id(config, 123) != expected


def test_schema1_identity_bytes_and_implicit_publication_basis_remain_unchanged():
    config = validate_stream_config(descriptor())
    assert 'cost_key_basis' not in config
    assert config.get('cost_key_basis', 'publication_time') == 'publication_time'
    assert stream_contract_id(config, 123) == '8ccca3f1c7259e04381fee0664a09ecb74c2e5ab1e928ec105a1f7638477face'
    assert stream_contract_id(descriptor(2), 123) != stream_contract_id(config, 123)


@pytest.mark.parametrize('basis', [None, '', 'publication_time', True, 1, ['model_input_time']])
def test_schema2_rejects_missing_or_wrong_cost_key_basis(basis):
    config = descriptor(2)
    if basis is None:
        config.pop('cost_key_basis')
    else:
        config['cost_key_basis'] = basis
    with pytest.raises(ValueError):
        validate_stream_config(config)


def test_schema1_rejects_new_basis_key_and_schema2_rejects_unknown_keys():
    config = descriptor()
    config['cost_key_basis'] = 'publication_time'
    with pytest.raises(ValueError):
        validate_stream_config(config)
    config = descriptor(2)
    config['future_key'] = 'ignored?'
    with pytest.raises(ValueError):
        validate_stream_config(config)


@pytest.mark.parametrize('key,value', [
    ('schema_version', True), ('schema_version', 2), ('schema_version', 3),
    ('selected_channel', 1),
    ('selected_channel', False), ('frame_id', ''), ('frame_id', '/odom'),
    ('frame_id', "odom'unsafe"), ('frame_id', 'odom frame'),
    ('pose_topic', 'relative_pose'), ('pose_topic', '/bad//pose'),
    ('sensor_geometry_config_sha256', 'xyz'), ('sensor_geometry', {}),
])
def test_rejects_incomplete_or_unsupported_descriptor(key, value):
    config = descriptor()
    config[key] = value
    with pytest.raises(ValueError):
        validate_stream_config(config)


@pytest.mark.parametrize('version', [1, 2])
def test_descriptor_result_cannot_mutate_input_and_rejects_extra_keys(version):
    config = descriptor(version)
    result = validate_stream_config(config)
    result['sensor_geometry']['radial_offset_m'] = 10
    assert config['sensor_geometry']['radial_offset_m'] == .18
    config['extra'] = 'ignored?'
    with pytest.raises(ValueError):
        validate_stream_config(config)


@pytest.mark.parametrize('value', [-1, True, 1.0, 2_147_483_648_000_000_000])
def test_rejects_invalid_absolute_origin(value):
    with pytest.raises(ValueError):
        stream_contract_id(descriptor(), value)


def test_relative_source_conversion_is_not_legacy_join_key():
    origin = 20_000_000_000
    assert relative_stamp_ns(origin, .123456789) == 20_123_456_789
    assert .1 != .10000000001
    assert relative_stamp_ns(origin, .1) == relative_stamp_ns(origin, .10000000001)
    stamp = SimpleNamespace(sec=0, nanosec=0)
    set_time(stamp, origin + 234)
    assert time_to_ns(stamp) == origin + 234
    stamp.nanosec = 1_000_000_000
    with pytest.raises(ValueError):
        time_to_ns(stamp)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), 1e308, -1, True])
def test_invalid_relative_source_time(value):
    with pytest.raises(ValueError):
        relative_stamp_ns(0, value)


@pytest.mark.parametrize('version', [1, 2])
def test_mode_requires_explicit_shared_identity_and_simulation(version):
    assert validate_mode_identity('stationary_v1', 'legacy', '', '') is None
    config = descriptor(version)
    assert validate_mode_identity('rolling_gesc_v2', 'robust_gaussian_v1', 'run_1', config) == config
    for profile, run, simulation in [('legacy', 'run', True), ('robust_gaussian_v1', '', True), ('robust_gaussian_v1', 'run', False)]:
        with pytest.raises(ValueError):
            validate_mode_identity('rolling_gesc_v2', profile, run, config, simulation=simulation)


def test_geometry_hash_matches_exact_file_and_rejects_unsupported_mount(tmp_path):
    config_path = Path(__file__).parents[1] / 'ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json'
    result = sensor_geometry_descriptor(config_path)
    assert result['sensor_geometry'] == SUPPORTED_GEOMETRY
    parsed = json.loads(config_path.read_text())
    entry = next(iter(parsed.values()))
    entry['params']['joint_position'][0] = .01
    changed = tmp_path / 'changed.json'
    changed.write_text(json.dumps(parsed))
    with pytest.raises(ValueError, match='unsupported'):
        sensor_geometry_descriptor(changed)


@pytest.mark.parametrize('sensor_delay,pose_delay', [(0., 0.), (.1, 0.), (0., .1), (.1, .1)])
def test_runner_binds_schema2_model_input_basis_to_resolved_streams(sensor_delay, pose_delay):
    from ros_esc.scenario_runner.run_scenario import build_v2_stream_config

    config = build_v2_stream_config({'disturbances': {
        'sensor_delay_sec': sensor_delay, 'pose_delay_sec': pose_delay,
    }})
    assert config['schema_version'] == 2
    assert config['cost_key_basis'] == 'model_input_time'
    assert config == validate_stream_config(canonical_json(config))
    assert config['pose_topic'].endswith('pose_delayed') == bool(pose_delay)
    for key in ('raw_cost_topic', 'source_cost_topic', 'provenance_topic'):
        assert config[key].endswith('_delayed') == bool(sensor_delay)


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
def test_selected_launch_routes_mode_to_both_upstream_clock_owners(mode):
    launch_path = Path(__file__).parents[2] / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    launch = ET.parse(launch_path).getroot()
    values = {entry.attrib['name']: entry.attrib.get('default', '')
              for entry in launch.findall('arg')}
    assert values['continuous_search_mode'] == 'stationary_v1'
    values['continuous_search_mode'] = mode
    commands = {}
    for entry in launch.findall('executable'):
        command = entry.attrib['cmd']
        if not any(f'ros2 run ros_esc {name}' in command
                   for name in ('encoder_node', 'sensor_pose_node')):
            continue
        argv = resolve_frontend_command(command, values)
        assert argv.count(f'--continuous-search-mode={mode}') == 1
        commands[argv[3]] = argv
    assert set(commands) == {'encoder_node', 'sensor_pose_node'}
    assert commands['encoder_node'][4] == '/joint_states'
    assert commands['sensor_pose_node'][4] == '/odom'


@pytest.mark.parametrize('version', [1, 2])
def test_both_descriptor_schemas_survive_selected_launch_argument_syntax(version):
    launch_path = Path(__file__).parents[2] / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    launch = ET.parse(launch_path).getroot()
    values = {entry.attrib['name']: entry.attrib.get('default', '')
              for entry in launch.findall('arg')}
    config = canonical_json(descriptor(version))
    values.update(continuous_search_mode='rolling_gesc_v2', v2_run_id='test_run',
                  v2_stream_config_json=config)
    consumers = []
    for entry in launch.findall('executable'):
        command = entry.attrib['cmd']
        if '$(var v2_stream_config_json)' not in command:
            continue
        argv = resolve_frontend_command(command, values)
        config_arguments = [arg for arg in argv if arg.startswith(
            ('--v2-stream-config-json=', 'v2_stream_config_json:='))]
        assert len(config_arguments) == 1
        arg = config_arguments[0]
        restored = (arg.split('=', 1)[1] if arg.startswith('--')
                    else yaml.safe_load(arg.split(':=', 1)[1]))
        assert restored == config
        assert validate_stream_config(restored) == descriptor(version)
        consumers.append(argv[3])
    assert sorted(consumers) == ['convergence_detector_node',
                                 'cost_function_node', 'cost_function_node',
                                 'filter_node', 'filter_node', 'gaussian_fill_node',
                                 'modified_cost_node', 'pde_history_node', 'supervisor_node']
