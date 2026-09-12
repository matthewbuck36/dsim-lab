"""Prospective observation selection and independent duration clocks."""

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import yaml

from ros_esc.scenario_runner.scenario_schema import load_suite, expand_suite, _validate_correction_overrides
from ros_esc.scenario_runner.run_scenario import build_launch_command, build_record_command, build_metadata

PACKAGE = Path(__file__).resolve().parents[1]
SMOKE = PACKAGE / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'


def selected_document():
    document = yaml.safe_load(SMOKE.read_text())
    document['execution'].update(run_timeout_sec=0., simulation_duration_sec=125.)
    case = document['cases'][0]
    case['profiles'] = ['robust_gaussian_v1']
    case['algorithm']['launch_overrides'] = {
        'continuous_search_mode': 'rolling_gesc_v2',
        'v2_qualification_observation_only': True,
        'v2_candidate_radius_m': .75, 'v2_candidate_epsilon_m': .15,
    }
    return document


def load_document(tmp_path, document):
    path = tmp_path / 'q1.yaml'
    path.write_text(yaml.safe_dump(document))
    return load_suite(path)


def test_sim_duration_is_explicit_and_wall_duration_can_be_disabled_only_when_enabled(tmp_path):
    suite = load_document(tmp_path, selected_document())
    resolved = expand_suite(suite)[0][0]
    launch = build_launch_command(resolved, run_id='q1-contract')
    assert 'v2_qualification_observation_only:=True' in launch
    command = build_record_command(resolved, 'q1-contract', '/metadata.yaml', '/runs', suite['execution'], launch)
    assert command[command.index('--sim-duration-sec')+1] == '125.0'
    assert command[command.index('--duration-sec')+1] == '0.0'
    assert command[command.index('--')+1:] == launch
    metadata = build_metadata(resolved, 'test', 'q1-test', '', run_id='q1-contract')
    assert metadata['scenario_runner']['algorithm']['launch_overrides']['v2_qualification_observation_only']
    document = selected_document(); document['execution']['simulation_duration_sec'] = 0.
    with pytest.raises(ValueError, match='run_timeout_sec'):
        load_document(tmp_path, document)


@pytest.mark.parametrize('value', [-1., float('nan'), float('inf'), True, '125'])
def test_invalid_simulated_duration_rejected(tmp_path, value):
    document = selected_document(); document['execution']['simulation_duration_sec'] = value
    with pytest.raises(ValueError, match='simulation_duration_sec'):
        load_document(tmp_path, document)


def test_legacy_duration_and_launch_defaults_unchanged():
    suite = load_suite(SMOKE)
    resolved = expand_suite(suite)[0][0]
    command = build_record_command(resolved, 'old', '/metadata.yaml', '/runs', suite['execution'], ['launch'])
    assert '--sim-duration-sec' not in command
    assert command[command.index('--duration-sec')+1] == '5.0'
    xml = ET.parse(PACKAGE.parent / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml')
    assert next(a for a in xml.findall('arg') if a.attrib['name'] == 'v2_qualification_observation_only').attrib['default'] == 'false'
    supervisor = next(n.attrib['cmd'] for n in xml.findall('executable') if 'ros_esc supervisor_node' in n.attrib['cmd'])
    assert '-p v2_qualification_observation_only:=$(var v2_qualification_observation_only)' in supervisor


@pytest.mark.parametrize('value', ['true', 1, None])
def test_observation_selector_requires_actual_boolean(value):
    with pytest.raises(ValueError, match='v2_qualification_observation_only'):
        _validate_correction_overrides({'v2_qualification_observation_only': value}, {}, 'test')


def test_observation_selector_refuses_stationary_mode():
    with pytest.raises(ValueError, match='rolling_gesc_v2'):
        _validate_correction_overrides({'v2_qualification_observation_only': True}, {}, 'test')
