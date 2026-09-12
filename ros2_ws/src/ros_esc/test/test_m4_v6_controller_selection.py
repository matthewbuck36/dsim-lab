"""Prospective matched controller selection through existing owners only.

Pure archived builder fixtures retain all 80 prior-version argv/metadata pairs.
Synthetic controller callbacks exercise the existing parser/gates/saturation;
these tests do not derive a field or perform a Gazebo acquisition.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import yaml
from geometry_msgs.msg import Twist

from ros_esc.controller_node.controller_objects.turtlebot_vehicle import Directional_Controller
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner import scenario_schema as schema
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray
from test_q1_launch_frontend import parsed_launch, _commands  # noqa: F401
import test_v2_controller_motion as motion
from test_v2_controller_motion import node_factory  # noqa: F401

ROOT = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_matched_gain_v1/controller_selection')
OLD = runner.GESC_CONTROLLER
NEW = OLD.with_name('gesc_controller_full_rotation_voltage_m4_v6_gain_half.json')
OLD_SHA = '3f255699385cc16d830fd79f560d91f1206321606b763be2971bdbc9bf6912a1'
NEW_SHA = 'e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606'
OPTION = 'controller_config_filepath'


def inherited_rows():
    path = ROOT/'legacy_builder_fixtures_v1.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == '9d96aa9ec346a2ba3c092373cebe669d6c101a43871b8b58279a0a8120f201ca'
    return json.loads(path.read_text())


def selected_resolved(path):
    row = inherited_rows()[0]
    resolved = deepcopy(row['resolved'])
    resolved['algorithm']['launch_overrides'][OPTION] = path
    return resolved, row['kwargs']


def launch_values(argv):
    return dict(token.split(':=', 1) for token in argv if ':=' in token)


def metadata(resolved, run_id):
    return runner.build_metadata(resolved, 'retained-fixture', 'legacy-parity',
        'Pure builder fixture; no runtime acquisition.', run_id=run_id)


def test_new_json_is_exact_single_gain_delta_and_original_bytes_are_unchanged():
    original, selected = OLD.read_bytes(), NEW.read_bytes()
    assert hashlib.sha256(original).hexdigest() == OLD_SHA
    assert hashlib.sha256(selected).hexdigest() == NEW_SHA
    assert original.count(b'"k_vx": 1.0') == 1
    assert selected == original.replace(b'"k_vx": 1.0', b'"k_vx": 0.5')
    expected = json.loads(original)
    expected['gains']['k_vx'] = .5
    assert json.loads(selected) == expected


@pytest.mark.parametrize('version', range(1, 6))
def test_all_prior_version_argv_and_metadata_pairs_remain_exact(version):
    rows = [row for row in inherited_rows() if row['version'] == version]
    assert len(rows) == 16
    for row in rows:
        resolved = row['resolved']
        assert OPTION not in resolved['algorithm']['launch_overrides']
        original = deepcopy(resolved)
        assert runner.build_launch_command(resolved, **row['kwargs']) == row['launch_argv']
        assert metadata(resolved, row['kwargs']['run_id']) == row['metadata']
        assert resolved == original
    assert runner.resolve_controller_config_filepath({}) == OLD


@pytest.mark.parametrize('spelling', ['absolute', 'relative', 'tilde', 'symlink'])
def test_selected_path_canonicalizes_after_overrides_and_matches_metadata(tmp_path, monkeypatch, spelling):
    path = NEW if spelling == 'tilde' else tmp_path/'selected controller.json'
    if spelling != 'tilde':
        path.write_bytes(NEW.read_bytes())
    monkeypatch.chdir(tmp_path)
    if spelling == 'absolute':
        selected = str(path)
    elif spelling == 'relative':
        selected = './'+path.name
    elif spelling == 'tilde':
        selected = '~/'+str(path.relative_to(Path.home()))
    else:
        link = tmp_path/'controller-link.json'
        link.symlink_to(path)
        selected = str(link)
    resolved, kwargs = selected_resolved(selected)
    before = deepcopy(resolved)
    schema._validate_correction_overrides(resolved['algorithm']['launch_overrides'],
                                          resolved['algorithm']['ablations'], 'selection')
    argv = runner.build_launch_command(resolved, **kwargs)
    assert launch_values(argv)[OPTION] == str(path.resolve())
    assert metadata(resolved, kwargs['run_id'])['parameter_files'][2] == str(path.resolve())
    assert sum(token.startswith(OPTION+':=') for token in argv) == 1
    assert resolved == before


@pytest.mark.parametrize('value', [None, False, True, 1, [], {}, '', '  ', 'bad\x00path', 'bad\npath'])
def test_malformed_explicit_path_fails_schema_and_both_builders(value):
    resolved, kwargs = selected_resolved(value)
    with pytest.raises(ValueError, match=OPTION):
        schema._validate_correction_overrides(resolved['algorithm']['launch_overrides'],
                                              resolved['algorithm']['ablations'], 'selection')
    with pytest.raises(ValueError, match=OPTION):
        runner.build_launch_command(resolved, **kwargs)
    with pytest.raises(ValueError, match=OPTION):
        metadata(resolved, kwargs['run_id'])


@pytest.mark.parametrize('kind', ['missing', 'directory', 'broken_symlink'])
def test_nonfile_explicit_path_is_rejected_before_dispatch(tmp_path, kind):
    path = tmp_path/'controller.json'
    if kind == 'directory':
        path.mkdir()
    elif kind == 'broken_symlink':
        path.symlink_to(tmp_path/'missing-target.json')
    resolved, kwargs = selected_resolved(str(path))
    with pytest.raises(ValueError, match='existing file'):
        schema._validate_correction_overrides(resolved['algorithm']['launch_overrides'],
                                              resolved['algorithm']['ablations'], 'selection')
    with pytest.raises(ValueError, match='existing file'):
        runner.build_launch_command(resolved, **kwargs)
    with pytest.raises(ValueError, match='existing file'):
        metadata(resolved, kwargs['run_id'])


def test_actual_schema_roundtrip_and_launch_frontend_keep_exact_selected_argument(tmp_path, parsed_launch):
    path = runner.ROS_ESC_ROOT/'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
    original = path.read_bytes()
    document = yaml.safe_load(original)
    document['cases'][0]['algorithm']['launch_overrides'][OPTION] = str(NEW)
    scenario = tmp_path/'selected.yaml'
    scenario.write_text(yaml.safe_dump(document))
    runs, _ = schema.expand_suite(schema.load_suite(scenario))
    assert len(runs) == 2
    assert {run['profile'] for run in runs} == {'robust_gaussian_v1', 'legacy'}
    for resolved in runs:
        values = launch_values(runner.build_launch_command(resolved))
        assert values[OPTION] == str(NEW.resolve())
        assert metadata(resolved, 'frontend-selection')['parameter_files'][2] == str(NEW.resolve())
        _, commands = _commands(parsed_launch, values)
        controller = next(argv for argv in commands if argv[3] == 'controller_node')
        parsed = motion.controller.parse_controller_arguments(controller[4:])
        assert Path(parsed.config).resolve() == NEW.resolve()
    assert path.read_bytes() == original


@pytest.mark.parametrize('qx,qy', [(.08, .04), (-.08, -.04), (0., .02)])
def test_real_directional_controller_halves_unsaturated_translation_only(qx, qy):
    original, selected = json.loads(OLD.read_bytes()), json.loads(NEW.read_bytes())
    old = Directional_Controller(original['gains'], original['params'])
    new = Directional_Controller(selected['gains'], selected['params'])
    previous = old.controller_output(0., np.zeros(6), np.array([qx, qy]))
    current = new.controller_output(0., np.zeros(6), np.array([qx, qy]))
    assert current[0] == pytest.approx(previous[0]/2)
    assert current[1:] == pytest.approx(previous[1:])
    assert new.max_vx == old.max_vx == .1
    assert new.max_wz == old.max_wz == .5


@pytest.mark.parametrize('qx,qy', [(1., 1.), (-1., -1.)])
def test_real_directional_controller_keeps_shared_saturation(qx, qy):
    original, selected = json.loads(OLD.read_bytes()), json.loads(NEW.read_bytes())
    old = Directional_Controller(original['gains'], original['params'])
    new = Directional_Controller(selected['gains'], selected['params'])
    previous = old.controller_output(0., np.zeros(6), np.array([qx, qy]))
    current = new.controller_output(0., np.zeros(6), np.array([qx, qy]))
    assert current == pytest.approx(previous)
    assert abs(current[0]) == .1 and abs(current[5]) == .5


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
def test_actual_selected_controller_retains_supervisor_owned_assist_ceiling(node_factory, monkeypatch, mode):
    monkeypatch.setattr(motion, 'CONFIG', NEW)
    node = node_factory(mode)
    node.open_field_escape_supervisor_owned_assist_enabled = True
    message = motion.state(AlgorithmState.STATE_ESCAPE_ASSIST)
    message.safe_direction_valid = message.safe_direction_revision_valid = True
    message.safe_direction_revision, message.safe_direction_x = 1, 1.
    motion.prepare(node, message)
    assert node.controller_obj.k_vx == .5
    command = Twist()
    command.linear.x, command.angular.z = .2, -.8
    node.supervisor_command_callback(command)
    node.input_value_callback(StampedFloat64MultiArray(timestamp=10., data=[.08, .04]))
    assert node.controller_publisher.messages[-1].data == pytest.approx([.1, 0., 0., 0., 0., -.5])
    assert node.controller_obj.max_vx == .1 and node.controller_obj.max_wz == .5


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_v6_runner_centroid_evaluator_admits_only_exact_fresh_suite(arm):
    row = next(row for row in inherited_rows() if row['version'] == 5
               and row['kwargs']['run_id'].split('-')[-2] == arm)
    old = deepcopy(row['resolved'])
    current = deepcopy(old)
    current['suite_id'] = 'm4_pilot_v6'
    assert runner._m4_centroid_event_selection(current) == runner._m4_centroid_event_selection(old)
    current['suite_id'] = 'm4_pilot_v06'
    assert runner._m4_centroid_event_selection(current) is None


@pytest.mark.parametrize('mode,strict,accepted', [
    ('subreaper_group_v3', True, True), ('subreaper_group_v3', False, False),
    ('subreaper_v2', True, False), ('observed_tree_v1', True, False),
])
def test_v6_runner_admission_keeps_exact_existing_owner_without_execution(monkeypatch, mode, strict, accepted):
    class ReachedExpansion(Exception):
        pass
    monkeypatch.setattr(runner, 'load_suite', lambda path: {'suite_id': 'm4_pilot_v6'})
    def stop_before_execution(*args, **kwargs):
        raise ReachedExpansion()
    monkeypatch.setattr(runner, 'expand_suite', stop_before_execution)
    expected = ReachedExpansion if accepted else ValueError
    with pytest.raises(expected):
        runner.execute_suite('/synthetic/not-opened.yaml', 'fixture',
                             process_ownership_mode=mode, strict_cleanup=strict)
