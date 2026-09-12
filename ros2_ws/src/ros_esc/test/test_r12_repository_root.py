"""Cwd-first repository discovery without a normal import subprocess."""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from ros_esc.scenario_runner import run_scenario as runner


@pytest.fixture(autouse=True)
def clean_git_environment(monkeypatch):
    for name in tuple(os.environ):
        if name.startswith('GIT_'):
            monkeypatch.delenv(name)


def checkout(path, *, marker='directory'):
    (path / 'ros2_ws/src/ros_esc').mkdir(parents=True)
    if marker == 'directory':
        (path / '.git').mkdir()
    elif marker == 'file':
        (path / '.git').write_text('gitdir: /unused/shared/worktrees/example\n')
    return path


def module_at(monkeypatch, root):
    monkeypatch.setattr(
        runner, '__file__',
        str(root / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py'),
    )


def forbid_git(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail('ordinary checkout discovery must not launch a subprocess')
    monkeypatch.setattr(runner.subprocess, 'run', unexpected)


def git_result(monkeypatch, root=None, error=None):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        if error is not None:
            raise error
        return SimpleNamespace(stdout=str(root) + '\n')

    monkeypatch.setattr(runner.subprocess, 'run', run)
    return calls


@pytest.mark.parametrize('marker', ['directory', 'file'])
@pytest.mark.parametrize('nested', [False, True])
def test_cwd_checkout_precedes_other_module_checkout_without_git(
    monkeypatch, tmp_path, marker, nested,
):
    selected = checkout(tmp_path / 'selected', marker=marker)
    module_at(monkeypatch, checkout(tmp_path / 'other'))
    cwd = selected / 'nested/deep' if nested else selected
    cwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(cwd)
    monkeypatch.setenv('GIT_PAGER', 'cat')
    forbid_git(monkeypatch)
    assert runner._repository_root() == selected


@pytest.mark.parametrize('marker', ['directory', 'file'])
def test_nearest_non_dsim_git_marker_blocks_outer_checkout(
    monkeypatch, tmp_path, marker,
):
    outer = checkout(tmp_path / 'outer')
    nested = outer / 'unrelated'
    nested.mkdir()
    if marker == 'directory':
        (nested / '.git').mkdir()
    else:
        (nested / '.git').write_text('gitdir: /unused/unrelated\n')
    cwd = nested / 'deep'
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    fallback = checkout(tmp_path / 'module')
    module_at(monkeypatch, fallback)
    calls = git_result(monkeypatch, nested)
    assert runner._repository_root() == fallback
    assert len(calls) == 1


@pytest.mark.parametrize('name', [
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR',
    'GIT_CEILING_DIRECTORIES', 'GIT_DISCOVERY_ACROSS_FILESYSTEM',
    'GIT_CONFIG_COUNT', 'GIT_CONFIG_PARAMETERS',
])
def test_explicit_git_selection_override_keeps_git_authority(
    monkeypatch, tmp_path, name,
):
    monkeypatch.chdir(checkout(tmp_path / 'cwd'))
    selected = checkout(tmp_path / 'git-selected')
    monkeypatch.setenv(name, 'explicit')
    calls = git_result(monkeypatch, selected)
    assert runner._repository_root() == selected
    assert calls == [(
        ['git', 'rev-parse', '--show-toplevel'],
        dict(check=True, capture_output=True, text=True, timeout=5.0),
    )]


def test_unresolved_cwd_uses_existing_git_fallback(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    selected = checkout(tmp_path / 'git-selected')
    calls = git_result(monkeypatch, selected)
    assert runner._repository_root() == selected
    assert len(calls) == 1


@pytest.mark.parametrize('error', [
    FileNotFoundError('git unavailable'),
    runner.subprocess.CalledProcessError(128, 'git'),
    runner.subprocess.TimeoutExpired('git', 5.0),
])
def test_git_failure_retains_module_fallback(monkeypatch, tmp_path, error):
    monkeypatch.chdir(tmp_path)
    selected = checkout(tmp_path / 'module', marker=None)
    module_at(monkeypatch, selected)
    calls = git_result(monkeypatch, error=error)
    assert runner._repository_root() == selected
    assert len(calls) == 1


@pytest.mark.parametrize('conventional_exists', [False, True])
def test_conventional_fallback_and_exhausted_error(
    monkeypatch, tmp_path, conventional_exists,
):
    monkeypatch.chdir(tmp_path)
    module_at(monkeypatch, tmp_path / 'no-module-layout')
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path))
    git_result(monkeypatch, error=FileNotFoundError('git unavailable'))
    if conventional_exists:
        selected = checkout(tmp_path / 'dsim-lab', marker=None)
        assert runner._repository_root() == selected
    else:
        with pytest.raises(RuntimeError, match='cannot locate dsim-lab'):
            runner._repository_root()


def test_selected_installed_module_paths_unchanged_without_git(monkeypatch):
    expected = Path(__file__).resolve().parents[4]
    monkeypatch.chdir(expected / 'ros2_ws/src/ros_esc')
    forbid_git(monkeypatch)
    assert runner._repository_root() == runner.REPOSITORY_ROOT == expected
    assert runner.ROS_ESC_ROOT == expected / 'ros2_ws/src/ros_esc'
    for path in (
        runner.MULTI_LIGHT_COST, runner.GESC_CONTROLLER, runner.GESC_FILTER,
        runner.SENSOR_GEOMETRY, runner.VALIDATION_WORLD,
        runner.CORNER_ORIGIN_VALIDATION_WORLD,
    ):
        assert path.is_file()
        assert path.is_relative_to(expected)
