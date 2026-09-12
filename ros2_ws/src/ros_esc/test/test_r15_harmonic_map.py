"""Analytical and existing-quadrature checks; no bags or field-model queries."""

from copy import deepcopy
import json
import math

import numpy as np
import pytest

from ros_esc.plotting_scripts import v2_direction_reference as reference
from test_v2_direction_reference import _binding
from test_v2_observed_phase_reference import _cycle, _observations, _variable


def profile(beta, theta):
    return sum(beta[2*(k-1)]*math.cos(k*theta)
               + beta[2*(k-1)+1]*math.sin(k*theta) for k in range(1, 4))


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('phase_origin', [0., .37])
def test_uniform_map_matches_independent_signed_washout(sign, phase_origin):
    cycle = _cycle(_observations(sign=sign, yaw=phase_origin))
    original = deepcopy(cycle)
    result = reference.observed_phase_harmonic_map(cycle=cycle)
    assert result['qualified'], result
    omega = sign*math.tau/3
    # Independently derived continuous high-pass transfer: i*w/(1+i*w).
    real = omega**2/(1+omega**2)
    imag = omega/(1+omega**2)
    expected = np.zeros((2, 6))
    expected[:, :2] = -np.asarray([[real, imag], [-imag, real]])/.18
    assert np.asarray(result['matrix']) == pytest.approx(expected, abs=3e-10)
    errors = np.asarray(result['estimated_matrix_error'])
    assert errors.shape == (2, 6) and np.isfinite(errors).all()
    assert np.all(errors >= 0) and np.max(errors) < 1e-6
    assert np.all(np.abs(np.asarray(result['matrix'])-expected) <= errors+1e-13)
    assert result['audit']['objective_evaluations'] == 0
    assert cycle == original
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('sign,dwell', [(1, False), (-1, False), (1, True), (-1, True)])
def test_variable_phase_map_matches_existing_quadrature_for_all_harmonics(sign, dwell):
    cycle = _cycle(_variable(sign=sign, dwell=dwell, yaw=.2))
    assert cycle['qualified'] and not cycle['constant_rate_qualified']
    result = reference.observed_phase_harmonic_map(cycle=cycle)
    assert result['qualified'], result
    matrix = np.asarray(result['matrix'])
    # A pure higher harmonic is informative under this nonuniform phase;
    # two independent mixed vectors exercise all six signed columns.
    for beta in (np.array([0., 0., 1., 0., 0., 0.]),
                 np.array([.7, -.4, .3, .2, -.1, .15]),
                 np.array([-.2, .6, -.5, .1, .4, -.3])):
        expected = reference.observed_phase_reference(
            lambda theta: 2+profile(beta, theta), cycle=cycle, xy=[0., 0.], sources=[])
        assert expected['qualified'] and expected['informative']
        actual = matrix@beta
        assert actual == pytest.approx(expected['world_vector'], abs=3e-9)
        bound = (np.linalg.norm(np.asarray(result['estimated_matrix_error'])@np.abs(beta))
                 + expected['estimated_vector_error'])
        assert np.linalg.norm(actual-expected['world_vector']) <= bound+1e-12
    assert np.linalg.norm(matrix[:, 2]) > .01


def test_known_frozen_augmented_terms_need_one_separate_response():
    cycle = _cycle(_variable(dwell=True, yaw=.31))
    beta = np.array([.03, -.02, .01, .007, -.006, .004])
    weights = [.6, .7, .8]
    arguments = dict(base_xy=[.2, -.1], binding=_binding(), weights=weights,
        gaussian_fills=[{'center': [.5, -.2], 'covariance': [[.3, .02], [.02, .2]],
                         'amplitude': .4}],
        affine_terms=[{'anchor': [-.3, .4], 'vector': [.2, -.1]}])
    known = reference.augmented_objective(lambda x, y, theta: 0., **arguments)
    full = reference.augmented_objective(lambda x, y, theta: -2+profile(beta, theta),
                                         **arguments)
    known_response = reference.observed_phase_reference(
        known, cycle=cycle, xy=arguments['base_xy'], sources=[])
    full_response = reference.observed_phase_reference(
        full, cycle=cycle, xy=arguments['base_xy'], sources=[])
    mapped = reference.observed_phase_harmonic_map(cycle=cycle)
    assert mapped['qualified'] and known_response['qualified'] and full_response['qualified']
    actual = weights[0]*np.asarray(mapped['matrix'])@beta+known_response['world_vector']
    assert actual == pytest.approx(full_response['world_vector'], abs=3e-9)


def test_tiny_source_segment_and_zero_rate_limit_without_quadrature(monkeypatch):
    times = np.sort(np.r_[np.linspace(0., 3., 121), 1e-9])
    cycle = _cycle(_observations(times=times))
    def forbidden(*args, **kwargs):
        pytest.fail('the analytic map must not invoke objective quadrature')
    monkeypatch.setattr(reference, 'quad', forbidden)
    result = reference.observed_phase_harmonic_map(cycle=cycle)
    assert result['qualified'], result
    assert np.isfinite(result['matrix']).all()
    # Initial dwell explicitly exercises omega=0, not just small time steps.
    assert reference.observed_phase_harmonic_map(cycle=_cycle(_variable(dwell=True)))['qualified']


@pytest.mark.parametrize('fault', ['unqualified', 'missing_waveform', 'count', 'phase_nan'])
def test_original_support_and_waveform_guards_remain_required(fault):
    cycle = _cycle()
    if fault == 'unqualified':
        cycle['qualified'] = False
    elif fault == 'missing_waveform':
        del cycle['waveform']
    elif fault == 'count':
        cycle['actual_observation_count'] += 1
    else:
        cycle['waveform']['unwrapped_world_phase_rad'][4] = math.nan
    result = reference.observed_phase_harmonic_map(cycle=cycle)
    assert not result['qualified'] and result['matrix'] is None and result['reason']
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('fault', ['dc_leak', 'nonfinite', 'error_ceiling'])
def test_kernel_and_floating_error_failures_do_not_publish_a_map(monkeypatch, fault):
    original = reference._observed_adjoint
    def altered(times, phases):
        kernel, audit = original(times, phases)
        if fault == 'error_ceiling':
            audit['estimated_kernel_roundoff'] = .001
        def evaluate(t):
            theta, value = kernel(t)
            if fault == 'dc_leak':
                value += .01
            elif fault == 'nonfinite':
                value = complex(math.nan, 0.)
            return theta, value
        return evaluate, audit
    monkeypatch.setattr(reference, '_observed_adjoint', altered)
    result = reference.observed_phase_harmonic_map(cycle=_cycle())
    assert not result['qualified'] and result['matrix'] is None and result['reason']
    json.dumps(result, allow_nan=False)
