"""Deterministic checks of the unwired R14 fit, using analytic raw signals.

These examples test the mathematical contract, not noise calibration or the
independent synthetic study's acceptance criteria. No ROS/model is needed.
"""
import json
import math

import numpy as np
import pytest

from ros_esc.filter_node.harmonic_gesc import fit_profile


COEFFICIENTS = np.array([0.030, -0.020, 0.012, 0.007, -0.006, 0.004])


def analytic_samples(*, moving=False):
    """Independent declared equation: three sensor turns in nine seconds."""
    t = np.arange(180, dtype=float) / 20.0
    theta = math.tau * t / 3.0
    x = 0.06 * np.sin(math.tau * t / 9.0) if moving else np.zeros_like(t)
    y = 0.05 * np.cos(math.tau * t / 9.0) if moving else np.zeros_like(t)
    raw = -2.0 + 0.007 * ((t - 9.0) / 3.0)
    for harmonic in (1, 2, 3):
        raw += (COEFFICIENTS[2 * harmonic - 2] * np.cos(harmonic * theta)
                + COEFFICIENTS[2 * harmonic - 1] * np.sin(harmonic * theta))
    if moving:
        raw += 0.023 * x / 0.15 - 0.017 * y / 0.15
        raw += (x / 0.15) * (0.009 * np.cos(theta) - 0.004 * np.sin(theta))
        raw += (y / 0.15) * (-0.003 * np.cos(theta) + 0.006 * np.sin(theta))
    cycle = np.arange(len(t)) // 60
    return np.column_stack((t, x, y, theta, raw, cycle))


def fitted(samples):
    return fit_profile(samples, center_xy=(0.0, 0.0), center_time=9.0)


@pytest.mark.parametrize('moving', [False, True])
def test_exact_raw_harmonics_recovered_with_declared_nuisance(moving):
    result = fitted(analytic_samples(moving=moving))
    assert result['valid'], result
    np.testing.assert_allclose(result['coefficients'], COEFFICIENTS, atol=1e-10, rtol=1e-9)
    assert len(result['cv_gains']) == 3
    np.testing.assert_allclose(result['cv_gains'], [1.0, 1.0, 1.0], atol=1e-10)
    assert result['cv_gain'] == pytest.approx(min(result['cv_gains']))


def test_coordinate_and_time_origin_translation_preserves_same_target_fit():
    samples = analytic_samples(moving=True)
    original = fitted(samples)
    shifted = samples.copy()
    shifted[:, 0] += 10000.0
    shifted[:, 1] += 1000.0
    shifted[:, 2] -= 2000.0
    result = fit_profile(shifted, center_xy=(1000.0, -2000.0), center_time=10009.0)
    assert original['valid'] and result['valid'], (original, result)
    np.testing.assert_allclose(result['coefficients'], original['coefficients'], atol=1e-9, rtol=1e-8)
    np.testing.assert_allclose(result['cv_gains'], original['cv_gains'], atol=1e-9)


def test_raw_cost_sign_is_preserved_and_dc_offset_is_a_nuisance():
    samples = analytic_samples()
    flipped = samples.copy()
    flipped[:, 4] *= -1.0
    shifted = samples.copy()
    shifted[:, 4] += 17.0
    negative = fitted(flipped)
    dc_shifted = fitted(shifted)
    assert negative['valid'] and dc_shifted['valid'], (negative, dc_shifted)
    np.testing.assert_allclose(negative['coefficients'], -COEFFICIENTS, atol=1e-10)
    np.testing.assert_allclose(dc_shifted['coefficients'], COEFFICIENTS, atol=1e-10)


@pytest.mark.parametrize('perturbation', [0.0, 1e-5])
def test_phase_position_confounding_is_unavailable(perturbation):
    samples = analytic_samples()
    theta, t = samples[:, 3], samples[:, 0]
    samples[:, 1] = 0.12 * np.cos(theta) + perturbation * np.sin(t / 7.0)
    samples[:, 2] = 0.12 * np.sin(theta) + perturbation * np.cos(t / 8.0)
    result = fitted(samples)
    assert result['valid'] is False, result
    assert result['reason']


def test_cycle_labels_cannot_hide_two_revolutions_per_cycle():
    samples = analytic_samples()
    samples[:, 3] *= 2.0
    theta = samples[:, 3]
    samples[:, 4] = -2.0
    for harmonic in (1, 2, 3):
        samples[:, 4] += (COEFFICIENTS[2 * harmonic - 2] * np.cos(harmonic * theta)
                         + COEFFICIENTS[2 * harmonic - 1] * np.sin(harmonic * theta))
    result = fitted(samples)
    assert result['valid'] is False, result
    assert result['reason']


def test_finite_input_overflow_is_unavailable_and_json_safe():
    samples = analytic_samples()
    samples[:, 4] = np.where(np.arange(len(samples)) % 2 == 0, 1e308, -1e308)
    assert np.isfinite(samples).all()
    with np.errstate(over='ignore', invalid='ignore'):
        result = fitted(samples)
    assert result['valid'] is False, result
    assert result['reason']
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('column', range(6))
def test_nonfinite_input_is_unavailable(column):
    samples = analytic_samples()
    samples[75, column] = np.nan
    result = fitted(samples)
    assert result['valid'] is False, result
    assert result['reason']


@pytest.mark.parametrize('defect', [
    'empty', 'wrong_shape', 'missing_cycle', 'missing_sector',
    'fractional_cycle', 'duplicate_time', 'source_gap', 'phase_jump',
    'too_long', 'outside_target_excursion',
])
def test_missing_or_invalid_support_is_unavailable(defect):
    samples = analytic_samples()
    if defect == 'empty':
        samples = samples[:0]
    elif defect == 'wrong_shape':
        samples = samples[:, :5]
    elif defect == 'missing_cycle':
        samples = samples[samples[:, 5] != 1]
    elif defect == 'missing_sector':
        samples = samples[~((samples[:, 5] == 1)
                            & ((samples[:, 3] % math.tau) < math.tau / 12))]
    elif defect == 'fractional_cycle':
        samples[75, 5] = 1.25
    elif defect == 'duplicate_time':
        samples[75, 0] = samples[74, 0]
    elif defect == 'source_gap':
        samples[75:, 0] += 0.6
    elif defect == 'phase_jump':
        samples[75:, 3] += math.pi
    elif defect == 'too_long':
        samples[:, 0] *= 2.0
    elif defect == 'outside_target_excursion':
        samples[:, 1] = 0.6
    result = fitted(samples)
    assert result['valid'] is False, (defect, result)
    assert result['reason']
