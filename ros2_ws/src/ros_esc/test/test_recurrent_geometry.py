"""Finite source-time tests for the integrated recurrent model and resets."""
import math
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from ros_esc.convergence_detector_node.recurrent_geometry import (
    RecurrentConfig, RecurrentGeometryDetector, RecurrentResult, diagnostic_model_fields,
)
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, recurrent_diagnostic_errors


def run_trace(kind, period=60., speed=0., radius=.25, phase=.37, duration=120.):
    detector = RecurrentGeometryDetector()
    detector.start_epoch('test:1', 0)
    rows = []
    for i in range(round(duration / .1) + 1):
        t = i / 10
        angle = 2 * math.pi * t / period + phase
        if kind == 'circle':
            point = (radius * math.cos(angle) + speed * t, radius * math.sin(angle))
        elif kind == 'oscillation':
            point = (radius * math.cos(angle) + speed * t, 0.)
        elif kind == 'spikes':
            point = (radius * math.cos(angle), 2. if i % 2 else 0.)
        else:
            point = (speed * t, 0.)
        rows.extend(detector.update(i * 100_000_000, point, 'odom'))
    return detector, rows


@pytest.mark.parametrize('kind', ['circle', 'oscillation'])
@pytest.mark.parametrize('period', [12., 24., 36., 48., 60., 72.])
def test_recurrent_positive_periods(kind, period):
    _, rows = run_trace(kind, period)
    confirmed = [r for r in rows if r.confirmed_event]
    assert len(confirmed) == 1
    first = confirmed[0]
    assert first.branch == kind
    assert first.end_ns >= first.represented_duration_ns + 12_000_000_000
    assert first.persistence_count == 3
    assert first.persistence_start_ns == first.start_ns - 12_000_000_000
    assert math.hypot(*first.mean_xy) < .002


@pytest.mark.parametrize('kind', ['circle', 'oscillation', 'straight'])
@pytest.mark.parametrize('speed', [.02, .04])
def test_translating_controls_do_not_confirm(kind, speed):
    _, rows = run_trace(kind, period=66., speed=speed)
    assert not any(r.confirmed_event for r in rows)


@pytest.mark.parametrize('kind', ['circle', 'spikes'])
def test_original_excursions_do_not_confirm(kind):
    _, rows = run_trace(kind, radius=1. if kind == 'circle' else .25)
    assert not any(r.confirmed_event for r in rows)


def test_static_epoch_reset_and_confirmation_latch():
    detector, rows = run_trace('static', duration=36.)
    assert [r.end_ns for r in rows if r.confirmed_event] == [30_000_000_000]
    detector.invalidate('readiness_lost')
    detector.start_epoch('test:1', 0)  # Same identity cannot rearm.
    result = []
    for i in range(360, 721):
        result.extend(detector.update(i * 100_000_000, (0., 0.), 'odom'))
    assert not any(r.confirmed_event for r in result)
    detector.start_epoch('test:2', 72_000_000_000)
    result = []
    for i in range(720, 1021):
        result.extend(detector.update(i * 100_000_000, (0., 0.), 'odom'))
    assert [r.end_ns for r in result if r.confirmed_event] == [102_000_000_000]


@pytest.mark.parametrize('fault,stamp,point,frame', [
    ('time_rollback', 100_000_000, (0., 0.), 'odom'),
    ('source_gap', 9_000_000_000, (0., 0.), 'odom'),
    ('conflicting_duplicate', 200_000_000, (1., 0.), 'odom'),
    ('frame_changed', 300_000_000, (0., 0.), 'map'),
    ('invalid_position', 300_000_000, (math.nan, 0.), 'odom'),
])
def test_source_faults_discard_history(fault, stamp, point, frame):
    detector = RecurrentGeometryDetector(); detector.start_epoch('epoch', 0)
    for i in range(3):
        detector.update(i * 100_000_000, (0., 0.), 'odom')
    row = detector.update(stamp, point, frame)[0]
    assert row.reset_reason == fault
    assert not row.full and not row.eligible
    assert detector.retained_point_count <= 1
    assert not any(detector._streaks.values())


def test_source_epoch_anchor_no_boundary_extrapolation_and_bounded_history():
    detector = RecurrentGeometryDetector(); detector.start_epoch('epoch', 100_000_000)
    rows = []
    for i in range(2, 1501):
        rows.extend(detector.update(i * 100_000_000, (0., 0.), 'odom'))
    # First scheduled30.1 support would start before first actual source .2.
    assert min(r.end_ns for r in rows if r.confirmed_event) == 36_100_000_000
    assert detector.retained_point_count <= 542
    assert all(r.end_ns % 6_000_000_000 == 100_000_000 for r in rows if r.full)


def diagnostic(row):
    stamp = lambda ns: SimpleNamespace(sec=(ns or 0)//1_000_000_000, nanosec=(ns or 0)%1_000_000_000)
    values = diagnostic_model_fields(row)
    values.update(stamp=stamp(row.end_ns), receipt_stamp=stamp(row.end_ns), source_stamp=stamp(row.end_ns),
                  epoch_started_at=stamp(0), history_start=stamp(row.start_ns), history_end=stamp(row.end_ns),
                  persistence_start=stamp(row.persistence_start_ns), run_id='test', frame_id='odom',
                  source_pose_topic='/odom', metric_mode=RECURRENT_MODE, reset_reason='', search_epoch=1,
                  confirmation_sequence=1, reset_sequence=row.reset_sequence, source_valid=True,
                  history_valid=row.full, metric_valid=True, confinement_valid=True, eligible=row.eligible,
                  confirmed=row.confirmed_event, center_x_m=row.mean_xy[0], center_y_m=row.mean_xy[1],
                  score_m=row.score_m, confinement_radius_m=row.radius_m, maximum_radius_m=.5,
                  represented_duration_sec=row.represented_duration_ns*1e-9,
                  maximum_source_gap_sec=row.max_source_gap_ns*1e-9, sample_count=row.sample_count)
    return SimpleNamespace(**values)


@pytest.mark.parametrize('kind', ['circle', 'oscillation', 'static'])
def test_declared_contract_rejects_score_and_persistence_corruption(kind):
    _, rows = run_trace(kind)
    row = next(r for r in rows if r.confirmed_event)
    msg = diagnostic(row)
    assert recurrent_diagnostic_errors([msg]) == []
    msg.score_m += .01
    assert any('units' in error for error in recurrent_diagnostic_errors([msg]))
    msg = diagnostic(row); msg.persistence_count = 0
    assert recurrent_diagnostic_errors([msg])


def test_same_width_persistence_fault_requires_new_three_endpoints():
    detector = RecurrentGeometryDetector(); detector.start_epoch('epoch', 0)
    observed = []
    for i in range(1201):
        t = i / 10
        # A source spike after two circle30 passes must reset every affected fit.
        point = (.25 * math.cos(2 * math.pi * t / 60), .25 * math.sin(2 * math.pi * t / 60))
        if i == 370:
            point = (2., 0.)
        observed.extend(detector.update(i * 100_000_000, point, 'odom'))
    first = next(r for r in observed if r.confirmed_event)
    assert first.end_ns >= 84_000_000_000
    assert first.persistence_count == 3


def test_contract_rejects_nonfinite_support_without_throwing():
    _, rows = run_trace('static', duration=30.)
    msg = diagnostic(next(r for r in rows if r.confirmed_event))
    msg.support_duration_sec = math.nan
    assert any('unsupported branch or duration' in error for error in recurrent_diagnostic_errors([msg]))


def test_sample_capacity_invalidates_without_unbounded_growth(monkeypatch):
    from ros_esc.convergence_detector_node import recurrent_geometry as core
    monkeypatch.setattr(core, 'MAX_RETAINED_POINTS', 5)
    detector = RecurrentGeometryDetector(); detector.start_epoch('bounded', 0)
    rows = []
    for i in range(7):
        rows.extend(detector.update(i * 10_000_000, (0., 0.), 'odom'))
    assert any(r.reset_reason == 'sample_capacity' for r in rows)
    assert detector.retained_point_count < 5
