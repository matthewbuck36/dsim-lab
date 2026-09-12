"""Installed Q1 console bindings and release environment, without ROS startup."""

from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import rclpy
from rclpy.context import Context
from rclpy.node import Node


REPOSITORY = Path(__file__).resolve().parents[4]
HELPER = REPOSITORY / 'docs/codex/gesc_gaussian/v2/tools/q1_environment.py'
SOURCE_PACKAGE = REPOSITORY / 'ros2_ws/src/ros_esc'
BUILD = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial')


@pytest.fixture(scope='module')
def helper():
    spec = importlib.util.spec_from_file_location('q1_environment_under_test', HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def forbid_ros_startup(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Environment preflight must not initialize ROS or create a node')

    monkeypatch.setattr(rclpy, 'init', forbidden)
    monkeypatch.setattr(Context, 'init', forbidden)
    monkeypatch.setattr(Node, '__init__', forbidden)


@pytest.fixture
def binding(helper):
    return helper.installed_entry_points()


def test_actual_overlay_resolves_all_console_targets_without_startup(helper, binding):
    assert binding['node_entry_points_called'] is False
    assert binding['python_executable'] == str(Path(sys.executable).resolve())
    assert binding['package_prefix'] == str(BUILD / 'install/ros_esc')
    entries = binding['entry_points']
    assert len(entries) == 21
    assert len({entry['name'] for entry in entries}) == 21
    assert {'record_run', 'run_scenario', 'supervisor_node', 'convergence_detector_node',
            'gaussian_fill_node', 'filter_node', 'modified_cost_node'} <= {
                entry['name'] for entry in entries}
    assert {Path(item['path']).name for item in binding['metadata_files']} == {
        'entry_points.txt', 'PKG-INFO'}
    for item in binding['metadata_files']:
        assert Path(item['path']).parent == BUILD / 'build/ros_esc/ros_esc.egg-info'
    for entry in entries:
        assert Path(entry['wrapper']['path']) == BUILD / 'install/ros_esc/lib/ros_esc' / entry['name']
        assert Path(entry['module']['path']).is_relative_to(SOURCE_PACKAGE / 'ros_esc')
    for item in binding['metadata_files'] + [
            entry[kind] for entry in entries for kind in ('wrapper', 'module')]:
        assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256']
    assert helper.verify_environment(
        {'installed_entry_points': binding}, {'environment': helper.selected_environment()}) is None


def test_stale_source_prepend_rejected_before_any_target_load_in_fresh_process():
    script = '''
import importlib.metadata as metadata
import importlib.util
import json
import sys
import rclpy
from rclpy.context import Context
from rclpy.node import Node
def forbidden(*args, **kwargs):
    raise AssertionError('stale metadata must be rejected before load or ROS startup')
rclpy.init = forbidden
Context.init = forbidden
Node.__init__ = forbidden
metadata.EntryPoint.load = forbidden
spec = importlib.util.spec_from_file_location('q1_environment_child', sys.argv[1])
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
selected = metadata.distribution('ros-esc')
assert len(selected.entry_points) == 7
try:
    helper.installed_entry_points()
except ValueError as exc:
    assert 'console metadata differs' in str(exc), str(exc)
    print(json.dumps({'rejected': str(exc), 'selected': str(selected._path)}))
else:
    raise AssertionError('stale source metadata was accepted')
'''
    environment = dict(os.environ)
    environment['PYTHONPATH'] = str(SOURCE_PACKAGE) + os.pathsep + environment.get('PYTHONPATH', '')
    result = subprocess.run([sys.executable, '-c', script, str(HELPER)],
                            env=environment, cwd=REPOSITORY, capture_output=True,
                            text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(result.stdout)
    assert Path(receipt['selected']) == SOURCE_PACKAGE / 'ros_esc.egg-info'
    assert 'console metadata differs' in receipt['rejected']


@pytest.mark.parametrize('key', [
    'ROS_DOMAIN_ID', 'PYTHONPATH', 'AMENT_PREFIX_PATH', 'COLCON_PREFIX_PATH',
    'LD_LIBRARY_PATH', 'DISPLAY', 'RMW_IMPLEMENTATION', 'ROS_LOCALHOST_ONLY',
])
def test_changed_release_environment_rejected_before_entrypoint_import(helper, monkeypatch, key):
    frozen = helper.selected_environment()
    assert key in frozen
    changed = '' if frozen[key] is None else frozen[key] + '_changed'
    monkeypatch.setenv(key, changed)

    def no_import():
        pytest.fail('Environment mismatch must reject before importing console targets')

    monkeypatch.setattr(helper, 'installed_entry_points', no_import)
    with pytest.raises(ValueError, match='process environment differs'):
        helper.verify_environment({}, {'environment': frozen})


@pytest.mark.parametrize('missing', [None, {}, {'ROS_DOMAIN_ID': '191'}])
def test_missing_release_environment_cannot_authorize(helper, monkeypatch, missing):
    monkeypatch.setattr(helper, 'installed_entry_points',
                        lambda: pytest.fail('missing release must reject before imports'))
    release = {} if missing is None else {'environment': missing}
    with pytest.raises(ValueError, match='process environment differs'):
        helper.verify_environment({}, release)


@pytest.mark.parametrize('changed_field', [
    'python_executable', 'package_prefix', 'metadata_hash', 'metadata_path',
    'wrapper_hash', 'module_hash', 'target', 'missing_entry', 'startup_flag',
])
def test_changed_frozen_binding_rejected_against_actual_install(helper, binding, changed_field):
    changed = deepcopy(binding)
    if changed_field in ('python_executable', 'package_prefix'):
        changed[changed_field] += '_changed'
    elif changed_field.startswith('metadata_'):
        key = 'sha256' if changed_field == 'metadata_hash' else 'path'
        changed['metadata_files'][0][key] += '_changed'
    elif changed_field in ('wrapper_hash', 'module_hash'):
        kind = changed_field.split('_', 1)[0]
        changed['entry_points'][0][kind]['sha256'] = '0' * 64
    elif changed_field == 'target':
        changed['entry_points'][0]['target'] = 'wrong.module:main'
    elif changed_field == 'missing_entry':
        changed['entry_points'].pop()
    else:
        changed['node_entry_points_called'] = True
    with pytest.raises(ValueError, match='console binding differs'):
        helper.verify_environment({'installed_entry_points': changed},
                                  {'environment': helper.selected_environment()})


def test_safe_actual_record_run_console_help_uses_corrected_environment(helper):
    # record_run.main parses arguments before run(); argparse --help exits
    # before recorder construction, target launch, ROS initialization or writes.
    assert str(SOURCE_PACKAGE) not in os.environ.get('PYTHONPATH', '').split(os.pathsep)
    helper.installed_entry_points()
    result = subprocess.run(['ros2', 'run', 'ros_esc', 'record_run', '--help'],
                            cwd=REPOSITORY, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '--sim-duration-sec' in result.stdout
    assert '--metadata-input' in result.stdout
    assert result.stderr == ''
