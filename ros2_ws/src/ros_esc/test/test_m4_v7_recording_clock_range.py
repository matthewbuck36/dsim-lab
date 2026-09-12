"""Whole-validator clock-range regressions using synthetic recording inputs.

These tests exercise the existing validator and its inherited recording
fixture. They neither initialize ROS nor read a real bag. Scan counts establish
the performance regression without a wall-time benchmark.
"""

import builtins
from collections import Counter
from types import SimpleNamespace

import pytest

from ros_esc.experiment_recording import validate_run as validator
from test_experiment_recording import _run_validator_synthetic_fixture


def stamp_ns(value):
    return SimpleNamespace(sec=value // 1_000_000_000, nanosec=value % 1_000_000_000)


def typed_record(bag_stamp, source_stamp):
    return bag_stamp, SimpleNamespace(header=SimpleNamespace(stamp=stamp_ns(source_stamp)))


def set_clocks(fixture, values):
    fixture.clocks[:] = [
        (index + 1, SimpleNamespace(clock=stamp_ns(value)))
        for index, value in enumerate(values)
    ]


def reference_report(monkeypatch, fixture, clock_values, **records):
    """Re-evaluate synthetic inputs with the original per-item range reduction.

    Reuse the public timestamp predicate and complete validator. Recomputing
    the extrema here supplies an independent reference for cached bounds; no
    report field or failure is removed from the comparison.
    """
    predicate = validator.timestamps_within_clock

    def uncached(values, _minimum, _maximum, tolerance):
        return predicate(values, min(clock_values), max(clock_values), tolerance)

    with monkeypatch.context() as context:
        context.setattr(validator, 'timestamps_within_clock', uncached)
        return fixture.validate([], [], **records)


def test_clock_range_scans_are_constant_for_admitted_typed_stamps(
    monkeypatch, tmp_path, record_property,
):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    clocks = [1_000_000_000, 2_000_000_000]
    set_clocks(fixture, clocks)
    scans = Counter()

    def instrument(name):
        original = getattr(builtins, name)

        def wrapped(*args, **kwargs):
            # Other min/max uses inspect bag timestamps, not this ROS range.
            if len(args) == 1 and isinstance(args[0], list) and args[0] == clocks:
                scans[name] += 1
            return original(*args, **kwargs)

        return wrapped

    monkeypatch.setattr(validator, 'min', instrument('min'), raising=False)
    monkeypatch.setattr(validator, 'max', instrument('max'), raising=False)
    records = [typed_record(20 + index, 1_500_000_000) for index in range(64)]
    report = fixture.validate([], [], joint_records=[], singleton_records=records)
    assert report['checks']['typed_timestamps_within_clock']['passed']
    for name in ('min', 'max'):
        record_property(f'clock_{name}_scans', scans[name])
    record_property('admitted_typed_stamps', len(records))
    assert scans == {'min': 1, 'max': 1}, (
        'clock extrema must each scan once per validation, regardless of typed count',
        dict(scans),
    )


@pytest.mark.parametrize('clock_values', [
    [1_000_000_000, 2_000_000_000],
    [1_500_000_000, 2_000_000_000, 1_000_000_000, 1_500_000_000],
    [1_000_000_000, 1_000_000_000],
], ids=['ordered', 'unordered_with_duplicate', 'equal'])
def test_exact_report_boundaries_readiness_and_duplicate_order(
    monkeypatch, tmp_path, clock_values,
):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    set_clocks(fixture, clock_values)
    lower, upper = min(clock_values) - 150_000_000, max(clock_values) + 150_000_000
    joint = [
        typed_record(5, lower - 2),  # Before readiness: ignored by timestamp checks.
        typed_record(20, lower - 1),
        typed_record(21, lower),
    ]
    singleton = [
        typed_record(22, upper),
        typed_record(23, upper + 1),
        typed_record(24, upper + 1),
        typed_record(101, upper + 2),  # After readiness: ignored.
    ]
    records = dict(joint_records=joint, singleton_records=singleton)
    report = fixture.validate([], [], **records)
    assert report == reference_report(monkeypatch, fixture, clock_values, **records)
    check = report['checks']['typed_timestamps_within_clock']
    assert check == {'passed': False, 'detail': [
        {'topic': fixture.topics['joint_states'][0], 'stamp': lower - 1},
        {'topic': fixture.topics['typed_singleton'][0], 'stamp': upper + 1},
        {'topic': fixture.topics['typed_singleton'][0], 'stamp': upper + 1},
    ]}
    assert report['checks']['simulation_clock_monotonic']['passed'] == all(
        current >= previous for previous, current in zip(clock_values, clock_values[1:])
    )
    assert report['checks']['typed_timestamps_nonregressing']['passed']


@pytest.mark.parametrize('mode,clock_values', [
    ('simulation', []),
    ('physical', []),
    ('physical', [2_000_000_000, 1_000_000_000]),
], ids=['simulation_empty', 'physical_empty', 'physical_with_regressing_clock'])
def test_unselected_clock_checks_stay_unselected(monkeypatch, tmp_path, mode, clock_values):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    fixture.metadata['mode'] = mode
    set_clocks(fixture, clock_values)

    def unexpected(*_args):
        pytest.fail('timestamp range predicate must not run without selected simulation clocks')

    monkeypatch.setattr(validator, 'timestamps_within_clock', unexpected)
    report = fixture.validate([], [])
    assert 'typed_timestamps_within_clock' not in report['checks']
    assert 'algorithm_event_emission_fresh' not in report['checks']
    if mode == 'physical':
        assert 'simulation_clock_monotonic' not in report['checks']
    else:
        assert report['checks']['simulation_clock_monotonic']['passed'] is False


def test_nonempty_clock_without_admitted_timestamps_keeps_exact_report(monkeypatch, tmp_path):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    clock_values = [2_000_000_000, 1_000_000_000]
    set_clocks(fixture, clock_values)
    records = dict(joint_records=[], singleton_records=[])
    report = fixture.validate([], [], **records)
    assert report == reference_report(monkeypatch, fixture, clock_values, **records)
    assert report['checks']['typed_timestamps_within_clock'] == {'passed': True, 'detail': []}


def test_clock_extrema_are_fresh_on_the_next_validation(monkeypatch, tmp_path):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    records = dict(joint_records=[], singleton_records=[typed_record(20, 1_500_000_000)])
    set_clocks(fixture, [1_000_000_000, 2_000_000_000])
    first = fixture.validate([], [], **records)
    set_clocks(fixture, [10_000_000_000, 11_000_000_000])
    second = fixture.validate([], [], **records)
    assert first['checks']['typed_timestamps_within_clock']['passed']
    assert second['checks']['typed_timestamps_within_clock'] == {
        'passed': False, 'detail': [
            {'topic': fixture.topics['typed_singleton'][0], 'stamp': 1_500_000_000},
        ],
    }


def test_regression_and_first_twenty_outliers_keep_exact_report(monkeypatch, tmp_path):
    fixture = _run_validator_synthetic_fixture(monkeypatch, tmp_path)
    clock_values = [1_000_000_000, 2_000_000_000]
    set_clocks(fixture, clock_values)
    joint = [typed_record(20 + index, 3_000_000_000) for index in range(10)]
    singleton = [typed_record(30 + index, 4_000_000_000) for index in range(15)]
    # Keep the single-owner regression distinct from the range violations.
    singleton.extend([typed_record(45, 1_800_000_000), typed_record(46, 1_000_000_000)])
    records = dict(joint_records=joint, singleton_records=singleton)
    report = fixture.validate([], [], **records)
    assert report == reference_report(monkeypatch, fixture, clock_values, **records)
    assert report['checks']['typed_timestamps_nonregressing']['passed'] is False
    assert report['checks']['typed_timestamps_within_clock']['detail'] == [
        *[{'topic': fixture.topics['joint_states'][0], 'stamp': 3_000_000_000}] * 10,
        *[{'topic': fixture.topics['typed_singleton'][0], 'stamp': 4_000_000_000}] * 10,
    ]
