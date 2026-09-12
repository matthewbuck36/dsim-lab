"""Finite source/cache arithmetic checks; no recorded inputs or model calls."""

from dataclasses import replace
import hashlib
import importlib.util
import math
from pathlib import Path
import sys
import warnings

import pytest

from ros_esc.filter_node import cycle_coherence as numeric
from ros_esc.filter_node.rolling_gesc import (
    DemodulatedSample, RollingGesc, RollingGescConfig,
)
from ros_esc.v2_direction_policy import MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY
from test_rolling_gesc import feed, ns, observation, times


def moving(**kwargs):
    return RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY, **kwargs))


@pytest.fixture(scope='module')
def oracle():
    path = Path('/home/mattb/Experiments/GESC-Gaussian/v2/qualification/'
                'q1_direction_policy_diagnostic_v1/preflight/policy_math.py')
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        'f3bdfb9c99f852c3f72df5e4c0922d2d5c044f7eb676a54d663ee1653d3e61a1')
    spec = importlib.util.spec_from_file_location('immutable_d3_math_oracle', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('a,b', [
    ((2., 0.), (2., 0.)), ((1., 0.), (4., 0.)),
    ((-2., 0.), (3., 0.)), ((1., 0.), (0., 1.)),
    ((1., 1.), (1.+1e-12, 1.-1e-12)),
    ((1e-15, -2e-15), (-3e-15, 4e-15)),
    ((1e5, 3e5), (-1e5, -3e5)), ((0., 0.), (0., 0.)),
])
def test_segment_agrees_with_immutable_d3_oracle(oracle, a, b):
    actual = numeric.linear_norm_integral(a, b)
    expected = oracle.linear_norm_integral(a, b)
    assert actual == expected


def test_turning_linear_segment_analytic_integral():
    value = numeric.linear_norm_integral((1., 0.), (0., 1.))
    exact = .5 + math.asinh(1.)/(2*math.sqrt(2))
    assert value['available']
    assert value['mean_norm'] == pytest.approx(exact, abs=1e-12)
    assert value['mean_error'] < 1e-12


def test_collinear_crossing_integrates_norm_not_endpoint_norms():
    value = numeric.linear_norm_integral((-2., 0.), (3., 0.))
    assert value['mean_norm'] == pytest.approx(1.3, abs=1e-12)
    assert value['minimum_fraction'] == pytest.approx(.4)
    assert value['mean_norm'] != 2.5


@pytest.mark.parametrize('kwargs', [
    {'max_gap_ns': 600_000_000}, {'absolute_magnitude_floor': 2e-6},
    {'max_samples': 10}, {'freshness_ns': 600_000_000},
    {'variability_multiplier': 2.}, {'max_pair_angle_rad': math.pi},
])
def test_selected_descriptor_cannot_hide_config_drift(kwargs):
    with pytest.raises(ValueError, match='fixed numerical descriptor'):
        moving(**kwargs)
    RollingGescConfig(**kwargs)  # Established core-only custom configuration.


def test_default_path_does_no_norm_work_and_preserves_custom_blend(monkeypatch):
    monkeypatch.setattr(numeric, 'linear_norm_integral', lambda *a, **k: pytest.fail('default norm work'))
    core = RollingGesc(RollingGescConfig(blend_weight=.2))
    feed(core, times(9))
    result = core.evaluate(ns(9), 0., ns(9))
    assert result.qualified and result.actual_blend_weight == .2
    assert result.direction_policy == THREE_CYCLE_POLICY
    assert core._norm_cache is None and result.norm_new_evaluations == 0


def test_three_covered_cycles_are_warmup_and_new_weight_is_fixed():
    core = moving(blend_weight=.1)
    before = feed(core, times(8.975))[-1]
    assert before.mean_full and not before.warmup_valid and not before.qualified
    final = feed(core, [9.])[-1]
    assert final.warmup_valid and final.qualified
    assert final.coherence == pytest.approx(1.)
    assert core.evaluate(ns(9), 0., ns(9)).actual_blend_weight == .75


@pytest.mark.parametrize('direction', [1, -1])
def test_pi_over_four_harmonic_limit_and_yaw_covariance(direction):
    phase = lambda t: direction*math.tau*t/3 + .137
    vector = lambda t: (2*math.cos(phase(t))**2,
                        2*math.cos(phase(t))*math.sin(phase(t)))
    core = moving()
    feed(core, times(9.15, rate=100), vector=vector, phase=phase, yaw=lambda t: .3*t)
    result = core.evaluate(ns(9.15), .72, ns(9.15))
    assert result.qualified and result.coherence == pytest.approx(math.pi/4, abs=2e-4)
    expected = tuple(.25*a+.75*b for a, b in zip(result.instant_world, result.mean_world))
    c, s = math.cos(.72), math.sin(.72)
    assert result.final_body == pytest.approx((c*expected[0]+s*expected[1],
                                              -s*expected[0]+c*expected[1]))


def test_moving_mean_can_qualify_despite_old_control_rejecting():
    vector = lambda t: (math.cos(.16*t), math.sin(.16*t))
    old, new = RollingGesc(), moving()
    feed(old, times(9.1), vector=vector)
    result = feed(new, times(9.1), vector=vector)[-1]
    assert not old._result.qualified
    assert result.qualified and not result.cycles_valid
    assert result.cycle_variability == old._result.cycle_variability
    assert result.effective_magnitude_floor == old._result.effective_magnitude_floor


def test_finite_zero_instant_continuity_and_all_weak_invalid():
    core = moving()
    feed(core, times(9))
    feed(core, [9.025], vector=lambda t: (0., 0.))
    result = core.evaluate(ns(9.025), 0., ns(9.025))
    assert result.qualified and result.output_valid and result.actual_blend_weight == .75
    assert not result.fallback_used and result.final_magnitude > 1.
    weak = moving()
    feed(weak, times(9), vector=lambda t: (1e-7, 0.))
    result = weak.evaluate(ns(9), 0., ns(9))
    assert not result.output_valid and not result.fallback_used
    assert result.final_body is None and result.fallback_reason == 'no_meaningful_direction'


def test_weak_mixture_uses_meaningful_instant_without_fabricating_mean_authority():
    core = moving()
    feed(core, times(9))
    # Exact output-algebra boundary after a qualified source result.
    core._result = replace(core._result, instant_world=(-6., 0.), mean_world=(2., 0.))
    result = core.evaluate(ns(9), 0., ns(9))
    assert result.output_valid and result.fallback_used
    assert result.actual_blend_weight == 0 and result.final_body == (-6., 0.)
    assert result.fallback_reason == 'weak_or_nonfinite_mixture'


@pytest.mark.parametrize('now,pose_time', [(9.6, 9.6), (8.99, 8.99), (9.1, 8.5), (9.1, 9.2)])
def test_selected_policy_cannot_refresh_stale_or_future_input(now, pose_time):
    core = moving()
    feed(core, times(9))
    result = core.evaluate(ns(now), 0., ns(pose_time))
    assert not result.output_valid and result.final_body is None
    assert not result.fallback_used


def test_full_segments_cached_once_timer_duplicate_do_no_work_and_pruning_bounded(monkeypatch):
    original, calls = numeric.linear_norm_integral, []
    def counted(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)
    monkeypatch.setattr(numeric, 'linear_norm_integral', counted)
    core = moving()
    feed(core, times(9))
    before = len(calls)
    # Exact phase boundary: only the newly appended full segment needs work.
    feed(core, [9.025])
    assert len(calls)-before <= 2
    before = len(calls)
    for unused in range(10):
        core.evaluate(ns(9.025), 0., ns(9.025))
    core.update(core._last_sample)
    assert len(calls) == before
    assert len(core._norm_cache.receipts) == len(core._points)-1
    assert len(core._points) < 250
    assert core._result.norm_new_evaluations <= 2048
    assert core._result.norm_window_evaluations <= 20000


def test_irregular_clipped_window_cached_denominator_matches_uncached_oracle(oracle):
    core = moving()
    phase = lambda t: .137 + math.tau*t/3 + .02*math.sin(t)
    vector = lambda t: (1.+.2*math.cos(phase(t)), .1*math.sin(2*phase(t)))
    values = [i*.034 for i in range(280)]
    feed(core, values, vector=vector, phase=phase)
    result = core._result
    assert result.qualified
    start, end = core._crossing(result.phase_start), core._points[-1]
    assert start.observation_id is None
    points = [start]+[p for p in core._points if start.stamp_ns < p.stamp_ns < end.stamp_ns]+[end]
    receipts = [oracle.linear_norm_integral(a.q, b.q) for a,b in zip(points,points[1:])]
    weights = [(b.stamp_ns-a.stamp_ns)/(end.stamp_ns-start.stamp_ns)
               for a,b in zip(points,points[1:])]
    expected = math.fsum(w*r['mean_norm'] for w,r in zip(weights,receipts))
    error = math.fsum(w*r['mean_error'] for w,r in zip(weights,receipts))
    assert result.norm_denominator == expected and result.norm_error == error
    expected_gate = oracle.coherence_interval(result.mean_world, expected, error,
                                             1e-10+1e-8*result.mean_magnitude)
    assert result.coherence_lower == expected_gate['lower']


@pytest.mark.parametrize('fault', ['source_gap', 'phase_reversal', 'objective_changed', 'invalid_sample'])
def test_cache_and_warmup_clear_on_real_history_faults(fault):
    core = moving()
    feed(core, times(9))
    assert core._norm_cache.receipts and core._result.qualified
    if fault == 'source_gap':
        result = feed(core, [10.])[-1]
    elif fault == 'phase_reversal':
        result = feed(core, [9.025], phase=lambda t: -.1)[-1]
    elif fault == 'objective_changed':
        result = feed(core, [9.025], objective=replace(core.objective, revision=2))[-1]
    else:
        result = core.update(None)
    assert result.reset_reason == fault
    assert not core._norm_cache.receipts
    assert not result.qualified and not result.warmup_valid


def test_quadrature_warning_budget_and_exception_fail_closed(monkeypatch):
    budget = numeric.EvaluationBudget(max_calls=3)
    value = numeric.linear_norm_integral((1., 0.), (0., 1.), budget=budget)
    assert not value['available'] and value['reason'] == 'norm_evaluation_budget'
    assert budget.calls == 3
    def warning(*args, **kwargs):
        warnings.warn('numerical warning')
        return (1., 1e-15, {})
    monkeypatch.setattr(numeric, 'quad', warning)
    value = numeric.linear_norm_integral((1., 0.), (1., 0.))
    assert not value['available'] and value['reason'] == 'norm_quadrature_warning'


def test_failed_full_receipt_is_cached_and_does_not_retry_on_publication(monkeypatch):
    core = moving()
    feed(core, times(9))
    def fail(*args, **kwargs):
        raise ValueError('synthetic quadrature failure')
    monkeypatch.setattr(numeric, 'quad', fail)
    result = feed(core, [9.025])[-1]
    assert not result.qualified and result.coherence_reason == 'norm_quadrature_exception'
    failed = tuple(core._norm_cache.receipts.values())[-1]
    assert not failed['available']
    monkeypatch.setattr(numeric, 'quad', lambda *a, **k: pytest.fail('same-input retry'))
    for unused in range(5):
        value = core.evaluate(ns(9.025), 0., ns(9.025))
        assert value.output_valid and value.fallback_used
    assert core.update(core._last_sample) is result


def test_shared_new_work_cap_and_active_window_cap(monkeypatch):
    core = moving()
    feed(core, times(9))
    for receipt in core._norm_cache.receipts.values():
        receipt['evaluations'] = 300
    result = feed(core, [9.025])[-1]
    assert not result.qualified and result.coherence_reason == 'norm_window_evaluation_budget'
    assert core.evaluate(ns(9.025), 0., ns(9.025)).fallback_used
    core = moving()
    feed(core, times(9))
    def exhausting(function, *args, **kwargs):
        for unused in range(2049):
            function(.5)
        pytest.fail('budget did not stop quadrature')
    monkeypatch.setattr(numeric, 'quad', exhausting)
    result = feed(core, [9.025])[-1]
    assert result.norm_new_evaluations == 2048
    assert not result.qualified and result.coherence_reason == 'norm_evaluation_budget'


@pytest.mark.parametrize('denom,error,expected', [
    (1., 2e-10, 'denominator_error_bound'),
    (1e-12, 1e-12, 'denominator_not_resolved_positive'),
    (1., 0., 'coherence_threshold_unresolved'),
])
def test_denominator_error_and_threshold_interval_are_not_relaxed(denom, error, expected):
    result = numeric.coherence_interval((.25, 0.), denom, error, 1e-8)
    assert not result['qualified'] and result['reason'] == expected


def test_dc_transient_and_synchronous_interference_can_pass_not_noise_proof():
    core = moving()
    vector = lambda t: (math.exp(-t)*math.cos(math.tau*t/3),
                        math.exp(-t)*math.sin(math.tau*t/3))
    result = feed(core, times(9), vector=vector)[-1]
    assert result.warmup_valid and result.qualified  # Coherent washout transient limitation.
    correlated = moving()
    assert feed(correlated, times(9), vector=lambda t: (0., 2.))[-1].qualified
    balanced = moving()
    result = feed(balanced, times(9), vector=lambda t: (
        math.cos(math.tau*t/3), math.sin(math.tau*t/3)))[-1]
    assert not result.qualified and result.coherence_reason == 'weak_current_mean'
