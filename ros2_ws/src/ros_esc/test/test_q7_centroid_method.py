"""Independent arithmetic and declared ideal trajectories for the Q7 method."""

from copy import deepcopy
import math

import pytest

from ros_esc.convergence_detector_node.centroid_contract import (
    CENTROID_TWO_BLOCK_V2, CENTROID_WINDOWS_V2, centroid_diagnostic_errors, centroid_score,
)
from ros_esc.convergence_detector_node.centroid_windows import CentroidConfig
from test_centroid_windows import _detector, _events, _run, _times
from test_v2_detector_contract import valid_centroid_diagnostic


def selected(**kwargs):
    return _detector(**dict(dict(window_seconds=6., epsilon_m=.18, max_radius_m=.5,
                                metric_mode=CENTROID_TWO_BLOCK_V2), **kwargs))


def test_explicit_scores_differ_and_default_is_historical():
    points = ((0., 0.), (3., 0.), (0., 0.), (0., 4.), (3., 4.), (0., 4.))
    assert centroid_score(points, CENTROID_TWO_BLOCK_V2) == 4.
    assert centroid_score(points) == 16.
    assert CentroidConfig().metric_mode == CENTROID_WINDOWS_V2


@pytest.mark.parametrize('mode', ['', 'pde_mean_v1', 'two_blocks', None, 2])
def test_unknown_core_mode_is_rejected(mode):
    with pytest.raises(ValueError, match='mode'):
        CentroidConfig(metric_mode=mode)
    with pytest.raises(ValueError, match='mode'):
        centroid_score([(0., 0.)] * 6, mode)


@pytest.mark.parametrize('period', [3., 6., 12.2819299136, 18., 24.])
@pytest.mark.parametrize('phase', [0., .73, math.pi / 2])
@pytest.mark.parametrize('projection', [False, True])
def test_selected_fixed_circle_and_fore_aft_confirm_at_36_seconds(period, phase, projection):
    def path(t):
        angle = 2 * math.pi * t / period + phase
        return (.35 * math.cos(angle), 0. if projection else .35 * math.sin(angle))
    results = _run(selected(), path, _times(42, rate=10))
    event, = _events(results)
    assert event.end_ns == 36_000_000_000
    assert event.score_m < .18 and event.radius_m <= .5
    # Independent continuous-time adjacent 18s means with a conservative
    # sampled interpolation margin from Q6; not a new empirical calibration.
    omega = 2 * math.pi / period
    def mean(a, b):
        x = .35 * (math.sin(omega*b+phase)-math.sin(omega*a+phase)) / (omega*(b-a))
        y = .35 * (math.cos(omega*a+phase)-math.cos(omega*b+phase)) / (omega*(b-a))
        return x, 0. if projection else y
    old, new = mean(0, 18), mean(18, 36)
    ideal = math.hypot(new[0]-old[0], new[1]-old[1])
    assert abs(event.score_m - ideal) <= 2 * .001919089745 + 1e-10
    assert all(not result.full for result in results if result.stamp_ns < 36_000_000_000)


@pytest.mark.parametrize('period', [3., 12.2819299136, 24.])
@pytest.mark.parametrize('heading', [0., .73, math.pi / 2])
def test_translated_circle_is_not_a_settled_positive(period, heading):
    def path(t):
        angle = 2 * math.pi * t / period
        return (.02*t*math.cos(heading)+.35*math.cos(angle),
                .02*t*math.sin(heading)+.35*math.sin(angle))
    results = _run(selected(), path, _times(72, rate=10))
    assert not _events(results)
    assert all(r.score_m >= .205880 for r in results if r.full)


@pytest.mark.parametrize('projection', [False, True])
def test_large_loop_or_fore_aft_is_rejected_by_full_trajectory_radius(projection):
    def path(t):
        return math.cos(2*math.pi*t/24), 0. if projection else math.sin(2*math.pi*t/24)
    results = _run(selected(), path, _times(48, rate=10))
    assert not _events(results)
    assert all(r.radius_m > .5 for r in results if r.full)


def test_unequal_samples_and_interpolated_windows_use_time_means():
    # Linear trajectory gives exact block means at t=9 and t=27; no source
    # observation lies on the 6s boundaries of this deliberately coarse mesh.
    times = [i*.37 for i in range(99)]
    result = next(r for r in _run(selected(max_radius_m=10),
        lambda t: (.02*t, -.01*t), times) if r.full)
    assert result.score_m == pytest.approx(18*math.hypot(.02, -.01), abs=1e-12)
    assert result.mean_xy == pytest.approx((.36, -.18), abs=1e-12)
    assert result.end_ns == 36_000_000_000
    assert result.sample_count == 98
    assert result.max_source_gap_ns == 370_000_000


def test_strict_score_and_inclusive_radius_edges():
    result = _run(selected(window_seconds=1, epsilon_m=3, max_radius_m=3),
                  lambda t: (t, 0.), _times(6, rate=4))[-1]
    assert result.score_m == 3 and result.radius_m == 3
    assert not result.eligible
    result = _run(selected(window_seconds=1, epsilon_m=3.01, max_radius_m=3),
                  lambda t: (t, 0.), _times(6, rate=4))[-1]
    assert result.confirmed_event


@pytest.mark.parametrize('fault', ['gap', 'rollback', 'frame', 'nonfinite'])
def test_new_mode_fault_resets_history_without_rearming_confirmed_epoch(fault):
    detector = selected()
    assert len(_events(_run(detector, lambda t: (0., 0.), _times(36, rate=10)))) == 1
    if fault == 'gap':
        detector.update(37_000_000_000, (0., 0.), 'odom')
    elif fault == 'rollback':
        detector.update(0, (0., 0.), 'odom')
    elif fault == 'frame':
        detector.update(36_100_000_000, (0., 0.), 'map')
    else:
        detector.update(36_100_000_000, (math.nan, 0.), 'odom')
    assert not _events(_run(detector, lambda t: (0., 0.), _times(36, rate=10)))
    detector.start_epoch('new-search')
    assert len(_events(_run(detector, lambda t: (0., 0.), _times(36, rate=10)))) == 1


def test_typed_score_mode_and_support_are_independently_checked():
    message = valid_centroid_diagnostic()
    message.metric_mode = CENTROID_TWO_BLOCK_V2
    message.centroid_x_m = [0., .03, 0., 0., .03, 0.]
    message.centroid_y_m = [0., 0., 0., .04, .04, .04]
    message.displacement_m = [.03, .03, .04, .03, .03]
    message.center_x_m, message.center_y_m = .01, .02
    message.score_m = .04
    assert not centroid_diagnostic_errors([message], expected_metric_mode=CENTROID_TWO_BLOCK_V2)
    assert centroid_diagnostic_errors([message], expected_metric_mode=CENTROID_WINDOWS_V2)
    switched = deepcopy(message)
    switched.metric_mode = CENTROID_WINDOWS_V2
    assert centroid_diagnostic_errors([switched])
    wrong_score = deepcopy(message)
    wrong_score.score_m = sum(message.displacement_m)
    assert centroid_diagnostic_errors([wrong_score])
    bad_support = deepcopy(message)
    bad_support.displacement_m[0] = .001
    assert centroid_diagnostic_errors([bad_support])
