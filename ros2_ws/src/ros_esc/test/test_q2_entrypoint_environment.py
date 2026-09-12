"""Explicit Q2 installed-build binding, without ROS/node startup or dispatch."""

from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import rclpy
from rclpy.context import Context
from rclpy.node import Node


REPOSITORY = Path(__file__).resolve().parents[4]
HELPER = REPOSITORY / 'docs/codex/gesc_gaussian/v2/tools/q1_environment.py'
SOURCE_PACKAGE = REPOSITORY / 'ros2_ws/src/ros_esc'
INITIAL_BUILD = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial')
Q2_BUILD = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1')


@pytest.fixture(scope='module')
def helper():
    spec = importlib.util.spec_from_file_location('q2_explicit_environment_under_test', HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def forbid_ros_startup(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Installed binding must not initialize ROS or create a node')

    monkeypatch.setattr(rclpy, 'init', forbidden)
    monkeypatch.setattr(Context, 'init', forbidden)
    monkeypatch.setattr(Node, '__init__', forbidden)


@pytest.fixture
def binding(helper):
    return helper.installed_entry_points(expected_build=Q2_BUILD)


def test_actual_q2_prefix_metadata_and_all_console_wrappers_bound_without_startup(helper, binding):
    assert binding['package_prefix'] == str(Q2_BUILD / 'install/ros_esc')
    assert binding['python_executable'] == str(Path(sys.executable).resolve())
    assert binding['node_entry_points_called'] is False
    assert len(binding['entry_points']) == len({row['name'] for row in binding['entry_points']}) == 21
    assert {Path(row['path']).name for row in binding['metadata_files']} == {'entry_points.txt', 'PKG-INFO'}
    for row in binding['metadata_files']:
        assert Path(row['path']).parent == Q2_BUILD / 'build/ros_esc/ros_esc.egg-info'
    for entry in binding['entry_points']:
        assert Path(entry['wrapper']['path']) == Q2_BUILD / 'install/ros_esc/lib/ros_esc' / entry['name']
        assert Path(entry['module']['path']).is_relative_to(SOURCE_PACKAGE / 'ros_esc')
    for ref in binding['metadata_files'] + [entry[kind] for entry in binding['entry_points']
                                          for kind in ('wrapper', 'module')]:
        assert hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest() == ref['sha256']
    assert helper.verify_environment({'installed_entry_points': binding},
                                     {'environment': helper.selected_environment()}, expected_build=Q2_BUILD) is None


@pytest.mark.parametrize('explicit', [False, True])
def test_initial_default_does_not_auto_accept_current_q2_install(helper, monkeypatch, explicit):
    def no_target_import(*args, **kwargs):
        pytest.fail('Wrong expected prefix must reject before console target loading')

    monkeypatch.setattr(helper.importlib.metadata.EntryPoint, 'load', no_target_import)
    assert helper.BUILD == INITIAL_BUILD
    with pytest.raises(ValueError, match='prefix is not'):
        helper.installed_entry_points(**({'expected_build': INITIAL_BUILD} if explicit else {}))


@pytest.mark.parametrize('expected', [None, '', 'q2_policy_runtime_v1', 123])
def test_build_is_an_explicit_absolute_input_not_inferred(helper, monkeypatch, expected):
    monkeypatch.setattr(helper, 'get_package_prefix', lambda *a: pytest.fail('Invalid expected build used environment'))
    with pytest.raises(ValueError, match='absolute path'):
        helper.installed_entry_points(expected_build=expected)


def test_changed_ament_prefix_rejected_before_console_target_loading(helper, monkeypatch):
    monkeypatch.setattr(helper, 'get_package_prefix', lambda name: str(INITIAL_BUILD / 'install/ros_esc'))
    monkeypatch.setattr(helper.importlib.metadata.EntryPoint, 'load',
                        lambda *a: pytest.fail('Wrong prefix reached target import'))
    with pytest.raises(ValueError, match='prefix is not'):
        helper.installed_entry_points(expected_build=Q2_BUILD)


def test_mixed_python_metadata_and_ament_build_rejected_before_target_loading(helper, monkeypatch):
    actual = helper.importlib.metadata.distribution('ros-esc')
    metadata_names = {'entry_points.txt', 'PKG-INFO'}

    def locate_file(item):
        if Path(item).name in metadata_names:
            return INITIAL_BUILD / 'build/ros_esc/ros_esc.egg-info' / Path(item).name
        return actual.locate_file(item)

    mixed = SimpleNamespace(entry_points=actual.entry_points, files=actual.files, locate_file=locate_file)
    monkeypatch.setattr(helper.importlib.metadata, 'distribution', lambda name: mixed)
    monkeypatch.setattr(helper.importlib.metadata.EntryPoint, 'load',
                        lambda *a: pytest.fail('Mixed metadata reached target import'))
    with pytest.raises(ValueError, match='isolated build metadata'):
        helper.installed_entry_points(expected_build=Q2_BUILD)


@pytest.mark.parametrize('fault', ['wrapper_hash', 'wrapper_path', 'metadata_hash', 'metadata_path',
                                   'module_hash', 'missing_entry', 'prefix'])
def test_frozen_q2_binding_cannot_substitute_another_owner(helper, binding, fault):
    changed = deepcopy(binding)
    if fault == 'prefix': changed['package_prefix'] = str(INITIAL_BUILD / 'install/ros_esc')
    elif fault == 'missing_entry': changed['entry_points'].pop()
    elif fault.startswith('metadata'):
        changed['metadata_files'][0]['sha256' if fault.endswith('hash') else 'path'] = 'wrong'
    else:
        kind = fault.split('_')[0]
        changed['entry_points'][0][kind]['sha256' if fault.endswith('hash') else 'path'] = 'wrong'
    with pytest.raises(ValueError, match='console binding differs'):
        helper.verify_environment({'installed_entry_points': changed},
                                   {'environment': helper.selected_environment()}, expected_build=Q2_BUILD)


def test_q2_environment_change_rejected_before_entrypoint_loading(helper, binding, monkeypatch):
    release = {'environment': helper.selected_environment()}
    monkeypatch.setenv('PYTHONPATH', os.environ.get('PYTHONPATH', '') + os.pathsep + '/wrong')
    monkeypatch.setattr(helper, 'installed_entry_points',
                        lambda **kw: pytest.fail('Changed release environment reached imports'))
    with pytest.raises(ValueError, match='process environment differs'):
        helper.verify_environment({'installed_entry_points': binding}, release, expected_build=Q2_BUILD)


def test_stale_source_metadata_prepend_rejected_despite_explicit_q2_expectation():
    script = '''
import importlib.metadata as metadata
import importlib.util
import json
import sys
import rclpy
from rclpy.context import Context
from rclpy.node import Node
def forbidden(*args, **kwargs):
    raise AssertionError('stale metadata reached target load or ROS startup')
rclpy.init = forbidden
Context.init = forbidden
Node.__init__ = forbidden
metadata.EntryPoint.load = forbidden
spec = importlib.util.spec_from_file_location('q2_explicit_environment_child', sys.argv[1])
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
try:
    helper.installed_entry_points(expected_build=sys.argv[2])
except ValueError as exc:
    assert 'console metadata differs' in str(exc), str(exc)
    print(json.dumps({'rejected': str(exc)}))
else:
    raise AssertionError('stale source metadata was accepted')
'''
    environment = dict(os.environ)
    environment['PYTHONPATH'] = str(SOURCE_PACKAGE) + os.pathsep + environment.get('PYTHONPATH', '')
    result = subprocess.run([sys.executable, '-c', script, str(HELPER), str(Q2_BUILD)],
                            env=environment, cwd=REPOSITORY, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'console metadata differs' in json.loads(result.stdout)['rejected']


def test_q2_actual_recorder_wrapper_help_exits_before_recorder_start(helper):
    helper.installed_entry_points(expected_build=Q2_BUILD)
    assert str(SOURCE_PACKAGE) not in os.environ.get('PYTHONPATH', '').split(os.pathsep)
    result = subprocess.run(['ros2', 'run', 'ros_esc', 'record_run', '--help'], cwd=REPOSITORY,
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '--sim-duration-sec' in result.stdout and '--metadata-input' in result.stdout
    assert result.stderr == ''
