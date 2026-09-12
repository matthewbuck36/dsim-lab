"""Analytic trajectory and source-time tests for V2 positional confinement."""

import math

import pytest

from ros_esc.convergence_detector_node import centroid_windows
from ros_esc.convergence_detector_node.centroid_windows import (
    CentroidConfig,
    CentroidWindowDetector,
)


NS = 1_000_000_000


def _detector(**parameters):
    detector = CentroidWindowDetector(CentroidConfig(**parameters))
    detector.start_epoch('search-1')
    return detector


def _run(detector, trajectory, times, offset_ns=0, frame='odom'):
    return [
        result
        for time in times
        for result in detector.update(
            offset_ns + round(time * NS), trajectory(time), frame,
        )
    ]


def _times(end, rate=20):
    return [step / rate for step in range(round(end * rate) + 1)]


def _events(results):
    return [result for result in results if result.confirmed_event]


def test_stationary_requires_six_complete_windows_and_emits_once():
    detector = _detector()
    results = _run(detector, lambda t: (2.0, -3.0), _times(30))
    events = _events(results)
    assert len(events) == 1
    event = events[0]
    assert event.stamp_ns == 18 * NS
    assert (event.start_ns, event.end_ns) == (0, 18 * NS)
    assert event.window_bounds_ns == tuple(
        (start * NS, (start + 3) * NS) for start in range(0, 18, 3)
    )
    assert event.mean_xy == pytest.approx((2.0, -3.0))
    assert event.score_m == pytest.approx(0.0, abs=1e-12)
    assert event.radius_m == pytest.approx(0.0, abs=1e-12)
    assert event.sample_count == 361
    assert event.max_source_gap_ns == 50_000_000
    assert event.represented_duration_ns == 18 * NS
    assert all(not item.full for item in results if item.stamp_ns < 18 * NS)
    assert all(len(item.centroids) <= 6 for item in results)
    assert detector.retained_point_count <= 6 * 62 + 2


@pytest.mark.parametrize('amplitude', [0.001, 0.20])
def test_fixed_center_oscillation_needs_no_minimum_travel(amplitude):
    detector = _detector()
    results = _run(
        detector,
        lambda t: (amplitude * math.sin(2.0 * math.pi * t / 3.0), 0.0),
        _times(21),
    )
    assert _events(results)[0].stamp_ns == 18 * NS
    assert _events(results)[0].radius_m <= amplitude + 1e-12


def test_fixed_center_circle_is_detected_while_moving():
    detector = _detector()
    results = _run(
        detector,
        lambda t: (
            1.2 + 0.2 * math.cos(2 * math.pi * t / 3),
            -0.7 + 0.2 * math.sin(2 * math.pi * t / 3),
        ),
        _times(21),
    )
    event = _events(results)[0]
    assert event.stamp_ns == 18 * NS
    assert event.mean_xy == pytest.approx((1.2, -0.7), abs=1e-12)
    assert event.radius_m == pytest.approx(0.2, abs=1e-12)


@pytest.mark.parametrize('window_seconds', [3.0, 6.0, 9.0])
def test_declared_drift_rejected_at_largest_grid_threshold(window_seconds):
    detector = _detector(
        window_seconds=window_seconds, epsilon_m=0.24, max_radius_m=0.75,
    )
    results = _run(
        detector,
        lambda t: (0.02 * t + 0.1 * math.cos(2 * math.pi * t / 3),
                   0.1 * math.sin(2 * math.pi * t / 3)),
        _times(7 * window_seconds),
    )
    assert not _events(results)
    assert results[-1].score_m == pytest.approx(5 * 0.02 * window_seconds)


def test_translation_is_not_stationary_despite_small_per_sample_steps():
    detector = _detector()
    results = _run(detector, lambda t: (0.02 * t, 0.0), _times(21, rate=100))
    assert not _events(results)
    assert results[-1].score_m == pytest.approx(0.30)


@pytest.mark.parametrize('spiral', [False, True])
def test_large_loop_and_expanding_spiral_fail_confinement(spiral):
    detector = _detector()

    def trajectory(time):
        radius = 0.01 + 0.06 * time if spiral else 1.0
        phase = 2 * math.pi * time / 3
        return radius * math.cos(phase), radius * math.sin(phase)

    results = _run(detector, trajectory, _times(24))
    assert not _events(results)
    assert results[-1].radius_m > 0.5


def test_sampling_equivalence_for_same_piecewise_linear_path_and_large_epoch():
    def triangle(time):
        phase = time % 3
        value = -0.2 + (0.4 / 1.5) * min(phase, 3 - phase)
        return value, 4.0 + value / 2

    # Both meshes contain every corner and represent the same linear path.
    regular = _times(18, rate=20)
    irregular = sorted(set(
        [18.0]
        + [corner / 2 for corner in range(37)]
        + [step * 0.37 for step in range(49) if step * 0.37 <= 18]
    ))
    offset = 1_790_000_000 * NS + 123
    first = _events(_run(_detector(), triangle, regular, offset))[0]
    second = _events(_run(_detector(), triangle, irregular, offset))[0]
    assert first.stamp_ns == second.stamp_ns == offset + 18 * NS
    assert first.score_m == pytest.approx(second.score_m, abs=1e-12)
    assert first.radius_m == pytest.approx(second.radius_m, abs=1e-12)
    for a, b in zip(first.centroids, second.centroids):
        assert a == pytest.approx(b, abs=1e-12)
    assert first.sample_count != second.sample_count


def test_boundary_interpolation_avoids_extrapolation_and_synthetic_counts():
    detector = _detector(window_seconds=1.0)
    results = _run(
        detector, lambda t: (2 * t, -t), [i * 0.4 for i in range(6)],
    )
    complete = [r for r in results if r.window_completed]
    assert [r.end_ns for r in complete] == [NS, 2 * NS]
    assert complete[0].centroids[0] == pytest.approx((1.0, -0.5))
    assert complete[0].sample_count == 3  # Source stamps 0, .4, .8 only.
    assert complete[1].sample_count == 6
    assert complete[1].centroids[-1] == pytest.approx((3.0, -1.5))
    assert complete[1].max_source_gap_ns == 400_000_000


def test_one_source_segment_can_complete_multiple_windows_in_order():
    detector = _detector(window_seconds=0.1, max_gap_seconds=1.0)
    detector.update(0, (0.0, 0.0), 'odom')
    results = detector.update(NS, (0.0, 0.0), 'odom')
    assert len(results) == 10
    assert [r.stamp_ns for r in results] == [
        i * 100_000_000 for i in range(1, 11)
    ]
    assert len(_events(results)) == 1
    assert _events(results)[0].end_ns == 600_000_000
    assert _events(results)[0].sample_count == 1


def test_strict_score_boundary_and_inclusive_radius_boundary():
    exact_score = _detector(window_seconds=1, epsilon_m=5, max_radius_m=4)
    result = _run(exact_score, lambda t: (t, 0), _times(6, rate=4))[-1]
    assert result.score_m == 5
    assert not result.eligible

    def triangle(time):
        phase = time % 1
        return (-1 + 4 * min(phase, 1 - phase), 0)

    exact_radius = _detector(window_seconds=1, max_radius_m=1)
    result = _run(exact_radius, triangle, _times(6, rate=4))[-1]
    assert result.score_m == 0
    assert result.radius_m == 1
    assert result.confirmed_event
    smaller_radius = _detector(window_seconds=1, max_radius_m=0.999)
    assert not _events(_run(smaller_radius, triangle, _times(6, rate=4)))


def test_radius_checks_intermediate_trajectory_points_not_only_centroids():
    detector = _detector(window_seconds=1, max_radius_m=0.5)
    results = _run(
        detector,
        lambda t: (0.8 * math.sin(2 * math.pi * t), 0),
        _times(6, rate=4),
    )
    assert results[-1].score_m == pytest.approx(0, abs=1e-12)
    assert results[-1].radius_m == pytest.approx(0.8)
    assert not results[-1].eligible


def test_duplicate_stamp_cannot_move_pose_or_add_observation_time():
    detector = _detector()
    detector.update(0, (0, 0), 'odom')
    sequence = detector.reset_sequence
    for _ in range(10):
        status = detector.update(0, (999, 999), 'odom')[0]
        assert not status.full
    assert detector.reset_sequence == sequence
    assert detector.retained_point_count == 1
    results = _run(detector, lambda t: (0, 0), _times(18)[1:])
    assert _events(results)[0].radius_m == 0


@pytest.mark.parametrize(
    ('sample', 'reason'),
    [
        ((NS, (math.nan, 0), 'odom'), 'invalid_position'),
        ((NS, (math.inf, 0), 'odom'), 'invalid_position'),
        ((NS, (0,), 'odom'), 'invalid_position'),
        ((NS, '12', 'odom'), 'invalid_position'),
        ((1.5, (0, 0), 'odom'), 'invalid_stamp'),
        ((-1, (0, 0), 'odom'), 'invalid_stamp'),
        ((True, (0, 0), 'odom'), 'invalid_stamp'),
        ((NS, (0, 0), ''), 'invalid_frame'),
    ],
)
def test_invalid_source_clears_history(sample, reason):
    detector = _detector()
    _run(detector, lambda t: (0, 0), _times(3))
    sequence = detector.reset_sequence
    result = detector.update(*sample)[0]
    assert result.reset_reason == reason
    assert not result.full
    assert not result.centroids
    assert detector.retained_point_count == 0
    assert detector.reset_sequence == sequence + 1


@pytest.mark.parametrize(
    ('stamp_ns', 'frame', 'reason'),
    [(2 * NS, 'odom', 'time_rollback'),
     (4 * NS, 'odom', 'source_gap'),
     (3 * NS, 'map', 'frame_changed')],
)
def test_discontinuity_seeds_history_at_new_sample(stamp_ns, frame, reason):
    detector = _detector()
    _run(detector, lambda t: (0, 0), _times(3))
    result = detector.update(stamp_ns, (2, 3), frame)[0]
    assert result.reset_reason == reason
    assert not result.full
    assert detector.retained_point_count == 1
    results = _run(
        detector, lambda t: (2, 3), _times(18)[1:],
        offset_ns=stamp_ns, frame=frame,
    )
    assert _events(results)[0].start_ns == stamp_ns


def test_gap_limit_is_inclusive_and_faults_preserve_confirmed_latch():
    detector = _detector()
    assert _events(_run(detector, lambda t: (0, 0), _times(18, rate=2)))
    assert detector.confirmed
    result = detector.update(19 * NS, (0, 0), 'odom')[0]
    assert result.reset_reason == 'source_gap'
    assert not _events(_run(
        detector, lambda t: (0, 0), _times(18, rate=2)[1:], offset_ns=19 * NS,
    ))
    detector.invalidate('source_stale')
    assert detector.confirmed
    assert not _events(_run(
        detector, lambda t: (0, 0), _times(18), offset_ns=40 * NS,
    ))


def test_same_epoch_is_idempotent_new_epoch_rearms_with_fresh_full_support():
    detector = _detector()
    _run(detector, lambda t: (0, 0), _times(18))
    sequence = detector.reset_sequence
    detector.start_epoch('search-1')
    assert detector.confirmed
    assert detector.reset_sequence == sequence
    detector.start_epoch('search-2')
    assert not detector.confirmed
    assert detector.retained_point_count == 0
    results = _run(detector, lambda t: (0, 0), _times(18), offset_ns=50 * NS)
    assert _events(results)[0].epoch_id == 'search-2'
    assert _events(results)[0].stamp_ns == 68 * NS


def test_capacity_exhaustion_is_explicit_and_preserves_latch(monkeypatch):
    detector = _detector()
    _run(detector, lambda t: (0, 0), _times(18))
    monkeypatch.setattr(centroid_windows, 'MAX_RETAINED_POINTS', 12)
    result = detector.update(18 * NS + 100_000_000, (0, 0), 'odom')[0]
    assert result.reset_reason == 'sample_capacity'
    assert detector.retained_point_count == 1
    assert detector.confirmed


def test_pathological_window_size_has_bounded_work_per_source_sample():
    detector = _detector(window_seconds=1e-9)
    detector.update(0, (0, 0), 'odom')
    result = detector.update(100_000_000, (0, 0), 'odom')[0]
    assert result.reset_reason == 'window_capacity'
    assert detector.retained_point_count == 1
    assert not result.confirmed_event


def test_capacity_guard_covers_interpolated_window_boundaries(monkeypatch):
    monkeypatch.setattr(centroid_windows, 'MAX_RETAINED_POINTS', 8)
    detector = _detector(window_seconds=0.01)
    detector.update(0, (0, 0), 'odom')
    results = detector.update(100_000_000, (0, 0), 'odom')
    assert results[-1].reset_reason == 'sample_capacity'
    assert detector.retained_point_count == 1
    assert not _events(results)


@pytest.mark.parametrize('alternating', [False, True])
def test_extreme_coordinates_never_emit_nonfinite_diagnostics(alternating):
    detector = _detector()

    def trajectory(time):
        sign = -1 if alternating and int(time * 2) % 2 else 1
        return sign * 1e308, 1e308

    results = _run(detector, trajectory, _times(21, rate=2))
    for result in results:
        assert result.reset_reason in (
            '', 'epoch_started', 'numerical_overflow',
        )
        values = (*result.deltas_m, *(result.mean_xy or ()))
        assert all(math.isfinite(value) for value in values)
        assert result.score_m is None or math.isfinite(result.score_m)
        assert result.radius_m is None or math.isfinite(result.radius_m)


def test_overflowing_difference_explicitly_resets_observation_history():
    detector = _detector(window_seconds=1)
    results = _run(
        detector, lambda t: (1.7e308 if t <= 1 else -1.7e308, 0),
        _times(4, rate=2),
    )
    assert any(
        result.reset_reason == 'numerical_overflow' for result in results
    )
    assert not _events(results)


def test_epoch_required_before_samples_are_retained():
    detector = CentroidWindowDetector()
    result = detector.update(0, (0, 0), 'odom')[0]
    assert result.reset_reason == 'epoch_not_started'
    assert detector.retained_point_count == 0
    with pytest.raises(ValueError):
        detector.start_epoch('')


@pytest.mark.parametrize('field', [
    'window_seconds', 'epsilon_m', 'max_radius_m', 'max_gap_seconds',
])
@pytest.mark.parametrize('value', [0, -1, math.inf, math.nan, True, '3'])
def test_invalid_configuration_rejected(field, value):
    with pytest.raises(ValueError):
        CentroidConfig(**{field: value})


@pytest.mark.parametrize('field', ['window_seconds', 'max_gap_seconds'])
def test_subnanosecond_time_configuration_rejected(field):
    with pytest.raises(ValueError):
        CentroidConfig(**{field: 1e-12})
