"""ROS-independent proof for idempotent controller-load recovery."""

import importlib.util
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
HELPER_PATH = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/turtlebot3_rotating_sensor/scripts/'
    'idempotent_controller_spawner.py'
)


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        'idempotent_controller_spawner',
        HELPER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Logger:
    def __init__(self):
        self.warnings = []

    def warning(self, message):
        self.warnings.append(message)


class _Node:
    def __init__(self):
        self.logger = _Logger()

    def get_logger(self):
        return self.logger


class _Response:
    def __init__(self, ok):
        self.ok = bool(ok)


def test_successful_load_returns_without_state_confirmation():
    helper = _load_helper()
    calls = []
    confirmations = []

    def service_call(*args, **kwargs):
        calls.append((args, kwargs))
        return _Response(True)

    def loaded_check(*args):
        confirmations.append(args)
        return False

    response = helper.idempotent_load_controller(
        _Node(),
        '/controller_manager',
        'velocity_controller',
        service_call=service_call,
        loaded_check=loaded_check,
    )

    assert response.ok is True
    assert len(calls) == 1
    assert calls[0][1]['max_attempts'] == 1
    assert confirmations == []


def test_lost_response_accepts_only_one_confirmed_loaded_request():
    helper = _load_helper()
    node = _Node()
    calls = []
    confirmations = []
    lost_response = RuntimeError('load response timed out')

    def service_call(*args, **kwargs):
        calls.append((args, kwargs))
        raise lost_response

    def loaded_check(*args):
        confirmations.append(args)
        return True

    response = helper.idempotent_load_controller(
        node,
        '/controller_manager',
        'joint_state_broadcaster',
        service_call=service_call,
        loaded_check=loaded_check,
    )

    assert response.ok is True
    assert len(calls) == 1
    assert len(confirmations) == 1
    assert 'confirmed loaded' in node.logger.warnings[-1]


def test_lost_response_without_confirmed_load_fails_without_retry():
    helper = _load_helper()
    calls = []
    confirmations = []
    lost_response = RuntimeError('load response timed out')

    def service_call(*args, **kwargs):
        calls.append((args, kwargs))
        raise lost_response

    def loaded_check(*args):
        confirmations.append(args)
        return False

    with pytest.raises(RuntimeError, match='load response timed out'):
        helper.idempotent_load_controller(
            _Node(),
            '/controller_manager',
            'velocity_controller',
            service_call=service_call,
            loaded_check=loaded_check,
        )

    assert len(calls) == 1
    assert len(confirmations) == 1


def test_negative_response_without_confirmed_load_fails_nonzero_path():
    helper = _load_helper()
    calls = []

    def service_call(*args, **kwargs):
        calls.append((args, kwargs))
        return _Response(False)

    with pytest.raises(RuntimeError, match='was not confirmed loaded'):
        helper.idempotent_load_controller(
            _Node(),
            '/controller_manager',
            'velocity_controller',
            service_call=service_call,
            loaded_check=lambda *args: False,
        )

    assert len(calls) == 1


def test_main_substitutes_only_upstream_load_operation(monkeypatch):
    helper = _load_helper()
    called = []
    original = helper.spawner.load_controller
    monkeypatch.setattr(
        helper.spawner,
        'main',
        lambda: called.append(True) or 0,
    )
    try:
        assert helper.main() == 0
        assert helper.spawner.load_controller is (
            helper.idempotent_load_controller
        )
        assert called == [True]
    finally:
        helper.spawner.load_controller = original
