"""Simulation Clock duration through the existing recorder and shutdown owner."""

from types import SimpleNamespace

import pytest
import rclpy
from rosgraph_msgs.msg import Clock
import yaml

from ros_esc.experiment_recording import record_run as recorder


CLOCK_ENTRY = {
    'alias': 'clock', 'topic': '/q1_test/selected_clock',
    'type': 'rosgraph_msgs/msg/Clock',
}


def clock_message(seconds):
    message = Clock()
    message.clock.sec, message.clock.nanosec = divmod(round(seconds * 1e9), 10**9)
    return message


@pytest.fixture
def duration_node():
    rclpy.init()
    node = recorder.RecordingCoordinator(
        '/q1_test/ready', '/q1_test/stop', 10.0,
        mode='simulation', sim_duration_sec=2.0, clock_entry=CLOCK_ENTRY,
    )
    try:
        yield node
    finally:
        node.destroy_node()
        rclpy.shutdown()


@pytest.mark.parametrize('seconds', [-1.0, float('nan'), float('inf'), -float('inf'), True, None, 1e308, 1e-20])
def test_invalid_enabled_duration_is_rejected(seconds):
    with pytest.raises(ValueError):
        recorder._simulation_duration_ns('simulation', seconds, CLOCK_ENTRY)


def test_disabled_default_and_physical_mode_compatibility():
    assert recorder._simulation_duration_ns('simulation', 0.0, None) == 0
    assert recorder._simulation_duration_ns('physical', 0.0, None) == 0
    with pytest.raises(ValueError, match='only available in simulation'):
        recorder._simulation_duration_ns('physical', 1.0, CLOCK_ENTRY)


@pytest.mark.parametrize('entry', [None, {}, {**CLOCK_ENTRY, 'alias': 'pose'}, {**CLOCK_ENTRY, 'type': 'nav_msgs/msg/Odometry'}, {**CLOCK_ENTRY, 'topic': ''}])
def test_duration_requires_selected_clock_manifest_alias(entry):
    with pytest.raises(ValueError, match='manifest clock alias'):
        recorder._simulation_duration_ns('simulation', 1.0, entry)


def test_cli_adds_disabled_optional_duration_preserving_wall_argument():
    parser = recorder._parser()
    argv = ['--mode', 'simulation', '--metadata-input', '/unused', '--duration-sec', '7.5']
    parsed = parser.parse_args(argv)
    assert parsed.duration_sec == 7.5
    assert parsed.sim_duration_sec == 0.0
    parsed = parser.parse_args(argv + ['--sim-duration-sec', '125'])
    assert parsed.duration_sec == 7.5 and parsed.sim_duration_sec == 125.0


def test_actual_coordinator_subscribes_selected_alias_with_best_effort(duration_node):
    subscription = duration_node.duration_clock_subscription
    assert subscription.topic_name == CLOCK_ENTRY['topic']
    assert subscription.qos_profile.reliability == recorder.ReliabilityPolicy.BEST_EFFORT


def test_freeze_first_ready_clock_origin_not_receipt_or_timekeeper(duration_node, monkeypatch):
    wall = SimpleNamespace(now=1000.0)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)
    duration_node.v2_origin_ns = 99_000_000_000
    assert duration_node.authorize_if_safe()
    assert not duration_node.ready
    duration_node._duration_clock_callback(clock_message(8.0))
    wall.now += 0.1
    duration_node._duration_clock_callback(clock_message(8.5))
    assert not duration_node.authorize_if_safe()
    assert duration_node.ready
    assert duration_node.duration_origin_ns == 8_500_000_000
    duration_node._duration_clock_callback(clock_message(10.0))
    assert not duration_node.simulation_duration_complete()
    assert duration_node.authorize_if_safe()  # Authorization cannot restart its origin.
    assert duration_node.duration_origin_ns == 8_500_000_000
    duration_node._duration_clock_callback(clock_message(10.5))
    snapshot = duration_node.simulation_duration_snapshot()
    assert snapshot['completed']
    assert snapshot['ready_clock_ns'] == 8_500_000_000
    assert snapshot['target_clock_ns'] == 10_500_000_000
    assert snapshot['elapsed_sec'] == 2.0


def test_stale_pre_ready_clock_cannot_authorize(duration_node, monkeypatch):
    wall = SimpleNamespace(now=10.0)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)
    duration_node._duration_clock_callback(clock_message(8.0))
    wall.now += 0.500001
    assert any('clock receipt is stale' in error for error in duration_node.authorize_if_safe())
    assert duration_node.duration_origin_ns is None
    duration_node._duration_clock_callback(clock_message(8.1))
    assert not duration_node.authorize_if_safe()
    assert duration_node.duration_origin_ns == 8_100_000_000


def test_duplicate_clock_does_not_advance_elapsed_duration(duration_node, monkeypatch):
    wall = SimpleNamespace(now=0.0)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)
    duration_node._duration_clock_callback(clock_message(5.0))
    assert not duration_node.authorize_if_safe()
    for _ in range(20):
        wall.now += 1.0
        duration_node._duration_clock_callback(clock_message(5.0))
    assert duration_node.simulation_duration_snapshot()['elapsed_sec'] == 0.0
    assert not duration_node.simulation_duration_complete()


@pytest.mark.parametrize('after_ready', [False, True])
def test_clock_rollback_is_terminal_and_cannot_be_rehabilitated(duration_node, after_ready):
    duration_node._duration_clock_callback(clock_message(8.0))
    if after_ready:
        assert not duration_node.authorize_if_safe()
    duration_node._duration_clock_callback(clock_message(7.999999999))
    duration_node._duration_clock_callback(clock_message(200.0))
    assert duration_node.duration_clock_ns == 8_000_000_000
    with pytest.raises(RuntimeError, match='moved backward'):
        duration_node.simulation_duration_complete()
    if not after_ready:
        assert duration_node.authorize_if_safe()
        assert not duration_node.ready


def test_malformed_clock_does_not_supply_a_receipt_based_origin(duration_node):
    duration_node._duration_clock_callback(SimpleNamespace(clock=SimpleNamespace(sec=1, nanosec=10**9)))
    assert duration_node.authorize_if_safe()
    assert duration_node.duration_clock_ns is None
    assert duration_node.duration_origin_ns is None
    with pytest.raises(RuntimeError, match='invalid ROS time'):
        duration_node.simulation_duration_complete()


class Process:
    returncode = None

    def poll(self):
        return self.returncode


def run_wait(node, monkeypatch, updates, *, wall_duration=0.0, target=None, bag=None, shutdown=None):
    wall = SimpleNamespace(now=0.0)
    updates = iter(updates)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)

    def advance(seconds):
        wall.now += seconds
        next(updates)()

    monkeypatch.setattr(recorder.time, 'sleep', advance)
    reason = recorder._wait_for_recording_duration(
        node, target or Process(), bag or Process(),
        shutdown or SimpleNamespace(requested=False), wall_duration, 2.0,
    )
    return reason, wall.now


def test_slow_clock_runs_to_source_duration_beyond_two_wall_seconds(duration_node, monkeypatch):
    duration_node._duration_clock_callback(clock_message(5.0))
    assert not duration_node.authorize_if_safe()
    updates = [
        lambda i=i: duration_node._duration_clock_callback(clock_message(5.0 + i / 20))
        for i in range(1, 41)
    ]
    reason, wall_elapsed = run_wait(duration_node, monkeypatch, updates)
    assert reason == 'simulation_duration_elapsed'
    assert wall_elapsed == pytest.approx(4.0)
    assert duration_node.simulation_duration_snapshot()['elapsed_sec'] == 2.0


def test_paused_clock_reaches_explicit_wall_limit_as_failure(duration_node, monkeypatch):
    duration_node._duration_clock_callback(clock_message(5.0))
    assert not duration_node.authorize_if_safe()
    with pytest.raises(TimeoutError, match='wall duration elapsed before'):
        run_wait(duration_node, monkeypatch, [lambda: None] * 10, wall_duration=0.3)
    assert not duration_node.simulation_duration_complete()


@pytest.mark.parametrize('which', ['target', 'bag'])
def test_early_process_exit_wins_over_simultaneous_duration_completion(duration_node, monkeypatch, which):
    duration_node._duration_clock_callback(clock_message(5.0))
    assert not duration_node.authorize_if_safe()
    process = Process()

    def finish_and_exit():
        duration_node._duration_clock_callback(clock_message(7.0))
        process.returncode = 0

    expected = 'target exited' if which == 'target' else 'rosbag exited'
    with pytest.raises(RuntimeError, match=expected):
        run_wait(duration_node, monkeypatch, [finish_and_exit], **{which: process})


def test_legacy_wall_completion_never_reads_simulation_clock(monkeypatch):
    wall = SimpleNamespace(now=0.0)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)
    monkeypatch.setattr(recorder.time, 'sleep', lambda seconds: setattr(wall, 'now', wall.now + seconds))
    reason = recorder._wait_for_recording_duration(
        object(), Process(), Process(), SimpleNamespace(requested=False), 0.2,
    )
    assert reason == 'wall_duration_elapsed'
    assert wall.now == 0.2


@pytest.mark.parametrize('finish', ['duration', 'rollback', 'interrupt'])
def test_all_stop_paths_use_existing_ordered_final_zero_cleanup(duration_node, monkeypatch, finish):
    duration_node._duration_clock_callback(clock_message(5.0))
    assert not duration_node.authorize_if_safe()
    shutdown = SimpleNamespace(requested=False)
    target, bag = Process(), Process()
    trace = []
    expected = None
    if finish == 'duration':
        update = lambda: duration_node._duration_clock_callback(clock_message(7.0))
    elif finish == 'rollback':
        update = lambda: duration_node._duration_clock_callback(clock_message(4.0))
        expected = RuntimeError
    else:
        update = lambda: setattr(shutdown, 'requested', True)
        expected = KeyboardInterrupt

    real_stop = duration_node.request_stop

    def stop():
        trace.append('request_stop')
        real_stop()
        assert not duration_node.ready

    monkeypatch.setattr(duration_node, 'request_stop', stop)
    monkeypatch.setattr(duration_node, 'final_zero_after', lambda _when: trace.append('final_zero') or True)
    monkeypatch.setattr(duration_node, 'destroy_node', lambda: trace.append('destroy_node'))
    monkeypatch.setattr(recorder, '_stop_process', lambda process, *_args, **_kwargs: (trace.append('target' if process is target else 'bag') or (0, True)))
    monkeypatch.setattr(recorder.rclpy, 'try_shutdown', lambda: None)
    caught = None
    try:
        run_wait(duration_node, monkeypatch, [update], target=target, bag=bag, shutdown=shutdown)
    except (RuntimeError, KeyboardInterrupt) as exc:
        caught = type(exc)
    finally:
        # Let the unchanged shutdown owner's post-zero wait run without consuming inputs.
        monkeypatch.setattr(recorder.time, 'sleep', lambda _seconds: None)
        result = recorder._shutdown_recording_resources(
            node=duration_node, executor=None, spin_thread=None,
            target_process=target, bag_process=bag,
            shutdown_zero_timeout_sec=1.0, post_zero_record_sec=0.0,
            target_exit_timeout_sec=1.0,
        )
    assert caught is expected
    assert result['zero_complete'] and result['target_clean'] and result['bag_clean']
    assert not result['errors']
    assert trace == ['request_stop', 'final_zero', 'target', 'bag', 'destroy_node']


@pytest.mark.parametrize('finish', ['duration', 'interrupt', 'rollback', 'target_exit'])
def test_run_retains_completion_failure_and_precleanup_clock_snapshot(
    duration_node, monkeypatch, tmp_path, finish,
):
    """Run actual orchestration with external graph/process I/O replaced by fixtures."""
    from ros_esc.experiment_recording import validate_run as validator

    entry = {**CLOCK_ENTRY, 'required': True, 'modes': ['simulation']}
    manifest = {'topics': [entry], 'storage_id': 'sqlite3'}
    metadata_input = {'mode': 'simulation', 'algorithm_profile': 'legacy', 'scenario_id': 'duration', 'operator_notes': 'fixture'}
    monkeypatch.setattr(recorder, 'load_manifest', lambda _path: manifest)
    monkeypatch.setattr(recorder, 'load_metadata_input', lambda *_args: metadata_input)
    monkeypatch.setattr(recorder, 'operational_config_for_mode', lambda *_args: {})
    monkeypatch.setattr(recorder.rosbag2_py, 'get_registered_writers', lambda: ['sqlite3'])
    monkeypatch.setattr(recorder, 'git_state', lambda _root: {})
    monkeypatch.setattr(recorder.rclpy, 'init', lambda **_kwargs: None)
    wall = SimpleNamespace(now=0.0)
    monkeypatch.setattr(recorder.time, 'monotonic', lambda: wall.now)
    duration_node._duration_clock_callback(clock_message(5.0))
    duration_node.zero_observed_at[recorder.ZERO_TOPICS[0]] = 0.0

    def coordinator(*_args, **kwargs):
        assert kwargs['clock_entry'] == entry
        assert kwargs['sim_duration_sec'] == 2.0
        return duration_node

    monkeypatch.setattr(recorder, 'RecordingCoordinator', coordinator)
    monkeypatch.setattr(recorder, 'SingleThreadedExecutor', lambda: SimpleNamespace(add_node=lambda _node: None, spin=lambda: None))
    monkeypatch.setattr(recorder, '_ConsoleCapture', lambda _path: SimpleNamespace(fatal_lines=[], log=lambda *_args: None, attach=lambda *_args: None, close=lambda: None))
    processes = []

    def process(*_args):
        result = Process()
        processes.append(result)
        return result

    monkeypatch.setattr(recorder, '_process', process)
    monkeypatch.setattr(recorder, '_graph_snapshot', lambda _node, _entries: (
        {entry['topic']: [entry['type']]}, {entry['topic']: ['/fixture_owner']},
        {entry['topic']}, {'/custom_controller'},
    ))
    monkeypatch.setattr(recorder, '_capture_parameters', lambda *_args, **_kwargs: {'nodes': {}, 'failures': []})

    def advance(seconds):
        wall.now += seconds
        if finish == 'interrupt':
            raise KeyboardInterrupt
        if finish == 'target_exit':
            processes[1].returncode = 0
        duration_node._duration_clock_callback(clock_message(4.0 if finish == 'rollback' else 7.0))

    monkeypatch.setattr(recorder.time, 'sleep', advance)
    cleanup_calls = []

    def cleanup(**kwargs):
        cleanup_calls.append(kwargs)
        duration_node.request_stop()
        # The real cleanup ordering is covered above. Its recording tail must not
        # retroactively qualify an interrupted acquisition or inflate elapsed time.
        duration_node._duration_clock_callback(clock_message(100.0))
        return {'zero_complete': True, 'target_code': 0, 'target_clean': True,
                'bag_code': 0, 'bag_clean': True, 'errors': []}

    monkeypatch.setattr(recorder, '_shutdown_recording_resources', cleanup)
    monkeypatch.setattr(validator, 'validate_run_directory', lambda path, **_kwargs: {
        'passed': yaml.safe_load((path / 'metadata.yaml').read_text())['recording']['complete'],
    })
    arguments = recorder._parser().parse_args([
        '--mode', 'simulation', '--metadata-input', '/fixture',
        '--runs-root', str(tmp_path), '--run-id', 'q1-duration-fixture',
        '--sim-duration-sec', '2', '--duration-sec', '0', '--', 'fixture_target',
    ])
    assert recorder.run(arguments) == (0 if finish == 'duration' else 1)
    assert len(cleanup_calls) == 1
    assert cleanup_calls[0]['node'] is duration_node
    recording = yaml.safe_load(next(tmp_path.glob('*/q1-duration-fixture/metadata.yaml')).read_text())['recording']
    snapshot = recording['simulation_duration']
    assert snapshot['ready_clock_ns'] == 5_000_000_000
    assert snapshot['latest_clock_ns'] != 100_000_000_000
    assert recording['final_zero_observed']
    if finish == 'duration':
        assert recording['completion_reason'] == 'simulation_duration_elapsed'
        assert snapshot['elapsed_sec'] == 2.0
        assert recording['infrastructure_status'] == 'completed'
    else:
        assert recording['failure_stage'] == 'recording'
        assert recording['infrastructure_status'] == 'runtime_failed'
        expected = {'interrupt': 'simulation duration was not completed',
                    'rollback': 'moved backward', 'target_exit': 'target exited'}[finish]
        assert expected in recording['run_error']
    if finish == 'interrupt':
        assert not snapshot['completed']
        assert snapshot['elapsed_sec'] == 0.0
