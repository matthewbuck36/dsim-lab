"""R17 algebra and boundary checks; no empirical acceptance is inferred here."""
import ast
import hashlib
import inspect
import json
import math

import numpy as np
import pytest

from ros_esc.filter_node import harmonic_gesc as owner


BETA = np.array([.03, -.02, .009, .006, -.004, .003])
INTERACTIONS = np.array([[.011, -.007, .005, .008, -.003, .006],
                         [-.006, .009, .004, -.005, .007, -.002]])
MAP = np.array([[1., -.3, .4, 0., -.2, .1],
                [.2, .8, 0., -.5, .3, -.4]])


def samples(*, noise=False):
    """Independent raw equations with a known profile at the origin."""
    t = np.arange(216)/24.
    phase = .27+math.tau*t/3.
    x = .045*np.sin(.73*t)+.025*np.cos(4.37*t)
    y = .04*np.cos(.91*t)+.03*np.sin(3.17*t)
    raw = -1.+.004*t+.2*x-.1*y+.5*x*x-.4*x*y+.3*y*y
    for k in (1, 2, 3):
        for j, wave in ((2*k-2, np.cos(k*phase)), (2*k-1, np.sin(k*phase))):
            raw += (BETA[j]+x/.15*INTERACTIONS[0, j]
                    +y/.15*INTERACTIONS[1, j])*wave
    if noise:
        raw += .003*np.sin(9.37*t)+.002*np.cos(13.91*t)
    return np.column_stack((t, x, y, phase, raw, np.arange(216)//72))


def fit(data=None, *, regularization=.001, output_map=None):
    return owner.fit_spatial_profile(samples() if data is None else data,
                                     center_xy=[0., 0.], center_time=4.5,
                                     regularization=regularization,
                                     output_map=output_map)


@pytest.mark.parametrize('output_map', [None, MAP])
def test_zero_penalty_limit_recovers_all_interactions_and_requested_output(output_map):
    result = fit(regularization=0., output_map=output_map)
    assert result['valid'], result
    assert result['output_estimable']
    np.testing.assert_allclose(result['coefficients'], BETA, atol=2e-8)
    np.testing.assert_allclose(np.array(result['interaction_coefficients']).reshape(2, 6),
                               INTERACTIONS, atol=2e-8)
    expected = (np.eye(2, 6) if output_map is None else output_map)@BETA
    np.testing.assert_allclose(result['raw_output'], expected, atol=2e-8)
    assert result['latest_predictive_gain'] == pytest.approx(1., abs=1e-7)


def test_augmented_system_matches_independent_mean_sse_ridge_solution():
    data = samples(noise=True)
    t, x, y, phase, raw, _ = data.T
    h = np.column_stack([f(k*phase) for k in (1, 2, 3) for f in (np.cos, np.sin)])
    dx, dy = x/.15, y/.15
    z = np.column_stack((np.ones(len(t)), (t-4.5)/3., dx, dy, dx*dx, dx*dy, dy*dy))
    design = np.column_stack((z, h, dx[:, None]*h, dy[:, None]*h))
    penalty = np.zeros((12, 25))
    penalty[:, 13:] = np.sqrt(len(t)*.001)*np.eye(12)
    expected = np.linalg.lstsq(np.vstack((design, penalty)),
                               np.r_[raw-raw.mean(), np.zeros(12)], rcond=1e-10)[0]
    result = fit(data, output_map=MAP)
    assert result['valid'], result
    np.testing.assert_allclose(result['coefficients'], expected[7:13], atol=2e-9)
    np.testing.assert_allclose(result['raw_output'], MAP@expected[7:13], atol=2e-9)


def test_nuisance_only_null_space_is_allowed():
    data = samples()
    data[:, 1:3] = 0.
    data[:, 4] = -1.+.03*np.cos(data[:, 3])-.02*np.sin(data[:, 3])
    result = fit(data)
    assert result['valid'], result
    assert result['rank'] == 8
    assert result['output_null_ratio'] <= 1e-8
    np.testing.assert_allclose(result['raw_output'], BETA[:2], atol=1e-10)


@pytest.mark.parametrize('regularization', [0., .0001, .001, .01])
def test_ridge_does_not_rescue_output_confounded_with_spatial_null(regularization):
    data = samples()
    phase = data[:, 3]
    data[:, 1] = .03*np.cos(phase/2.)
    data[:, 2] = .03*np.sin(phase/2.)
    data[:, 4] = -1.+20*(data[:, 1]**2-data[:, 2]**2)
    result = fit(data, regularization=regularization)
    assert not result['valid'], result
    assert result['reason'] == 'output_phase_motion_confounded'
    assert not result['output_estimable']
    assert result['output_null_ratio'] > 1e-8
    assert result['raw_output'] is None


def test_estimable_linear_combination_survives_other_harmonic_ambiguity():
    data = samples()
    phase = data[:, 3]
    data[:, 1] = .03*np.cos(phase)
    data[:, 2] = 0.
    data[:, 4] = -1.+.03*np.sin(phase)+.01*np.sin(3*phase)
    requested = np.zeros((2, 6))
    requested[0, [1, 5]] = [1., -1.]
    requested[1] = 2*requested[0]
    result = fit(data, output_map=requested)
    assert result['valid'], result
    np.testing.assert_allclose(result['raw_output'], [.02, .04], atol=2e-9)
    assert not fit(data)['valid']  # H1 alone is not identified by these rows.


def test_missing_latest_fit_is_diagnostic_and_does_not_discard_full_fit():
    data = samples()
    early = data[:, 5] < 2
    phase = data[early, 3]
    data[early, 1] = .03*np.cos(phase)
    data[early, 2] = .03*np.sin(phase)
    result = fit(data)
    assert result['valid'], result
    assert result['latest_predictive_gain'] is None
    assert result['latest_predictive_reason'] == 'output_phase_motion_confounded'


def test_latest_loss_is_retained_without_a_predictive_admission_gate():
    data = samples()
    data[:, 1:3] = 0.
    data[:, 4] = -1.+.03*np.cos(data[:, 3])
    data[data[:, 5] == 2, 4] = -1.
    result = fit(data)
    assert result['valid'], result
    assert result['latest_predictive_gain'] < 0.


def test_actual_coefficient_influence_matches_raw_cost_finite_differences():
    data = samples(noise=True)
    _, _, _, design = owner._spatial_design(data, np.array([0., 0.]), 4.5)
    solved = owner._spatial_solve(design, data[:, 4], .001)
    for index in (0, 51, 127, 215):
        high, low = data.copy(), data.copy()
        high[index, 4] += 1e-6
        low[index, 4] -= 1e-6
        upper, lower = fit(high), fit(low)
        assert upper['valid'] and lower['valid']
        derivative = (np.array(upper['coefficients'])-lower['coefficients'])/2e-6
        np.testing.assert_allclose(derivative, solved['influence'][7:13, index],
                                   atol=2e-7, rtol=2e-6)


def test_covariance_is_psd_and_uses_actual_hac_influence():
    data = samples(noise=True)
    result = fit(data, output_map=MAP)
    assert result['valid'], result
    _, _, _, design = owner._spatial_design(data, np.array([0., 0.]), 4.5)
    solved = owner._spatial_solve(design, data[:, 4], .001)
    a = solved['influence'][7:13]*solved['residual']/(1-solved['leverage'])
    kernel = np.maximum(0., 1-np.abs(data[:, 0, None]-data[None, :, 0]))
    expected = a@kernel@a.T
    np.testing.assert_allclose(result['covariance_hac'], expected, atol=1e-15)
    np.testing.assert_allclose(result['output_covariance_hac'], MAP@expected@MAP.T, atol=1e-15)
    assert np.linalg.eigvalsh(result['covariance_hac']).min() >= -1e-15
    assert np.linalg.eigvalsh(result['output_covariance_hac']).min() >= -1e-15


def test_cost_sign_scale_and_dc_origin_preserve_equivariance():
    data = samples(noise=True)
    base = fit(data, output_map=MAP)
    changed = data.copy()
    changed[:, 4] = -7*data[:, 4]+13.
    scaled = fit(changed, output_map=MAP)
    assert base['valid'] and scaled['valid']
    np.testing.assert_allclose(scaled['coefficients'], -7*np.array(base['coefficients']), atol=2e-8)
    np.testing.assert_allclose(scaled['output_covariance_hac'],
                               49*np.array(base['output_covariance_hac']), atol=2e-10)
    assert scaled['signal_score'] == pytest.approx(base['signal_score'], rel=2e-6)
    shifted = data.copy()
    shifted[:, 0] += 10000.
    shifted[:, 1:3] += [3., -5.]
    result = owner.fit_spatial_profile(shifted, [3., -5.], 10004.5,
                                      regularization=.001, output_map=MAP)
    assert result['valid'], result
    np.testing.assert_allclose(result['coefficients'], base['coefficients'], atol=2e-8)


def test_output_coordinate_rotation_and_scale_propagate_score_and_covariance():
    data = samples(noise=True)
    base = fit(data, output_map=MAP)
    angle = .63
    rotation = np.array([[math.cos(angle), -math.sin(angle)],
                         [math.sin(angle), math.cos(angle)]])
    transformed = fit(data, output_map=3*rotation@MAP)
    assert base['valid'] and transformed['valid']
    np.testing.assert_allclose(transformed['raw_output'], 3*rotation@base['raw_output'], atol=1e-12)
    np.testing.assert_allclose(transformed['output_covariance_hac'],
                               9*rotation@base['output_covariance_hac']@rotation.T, atol=1e-12)
    assert transformed['signal_score'] == pytest.approx(base['signal_score'], rel=1e-8)


def test_world_rotation_preserves_isotropic_interaction_penalty():
    data = samples(noise=True)
    base = fit(data)
    angle = .72
    rotation = np.array([[math.cos(angle), -math.sin(angle)],
                         [math.sin(angle), math.cos(angle)]])
    rotated = data.copy()
    rotated[:, 1:3] = data[:, 1:3]@rotation.T
    rotated[:, 3] += angle
    result = fit(rotated)
    transform = np.zeros((6, 6))
    for k in (1, 2, 3):
        c, s = math.cos(k*angle), math.sin(k*angle)
        transform[2*k-2:2*k, 2*k-2:2*k] = [[c, -s], [s, c]]
    assert base['valid'] and result['valid']
    np.testing.assert_allclose(result['coefficients'], transform@base['coefficients'], atol=2e-9)
    np.testing.assert_allclose(result['output_covariance_hac'],
                               rotation@base['output_covariance_hac']@rotation.T, atol=1e-12)
    assert result['signal_score'] == pytest.approx(base['signal_score'], rel=2e-7)


@pytest.mark.parametrize('regularization', [-1., float('nan'), float('inf'), True, [.001]])
def test_invalid_regularization_is_unavailable_and_json_safe(regularization):
    result = fit(regularization=regularization)
    assert not result['valid']
    assert result['reason'] == 'invalid_regularization'
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('output_map', [np.zeros((2, 6)), np.ones((6, 2)),
                                      np.full((2, 6), np.nan), np.full((2, 6), np.inf)])
def test_invalid_output_maps_are_unavailable_and_json_safe(output_map):
    result = fit(output_map=output_map)
    assert not result['valid']
    assert result['reason'] == 'invalid_output_map'
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('defect', ['nonfinite', 'gap', 'excursion', 'cycle', 'reverse'])
def test_original_support_failures_are_preserved(defect):
    data = samples()
    if defect == 'nonfinite':
        data[30, 4] = np.nan
    elif defect == 'gap':
        data[90:, 0] += .6
    elif defect == 'excursion':
        data[20, 1] = .6
    elif defect == 'cycle':
        data[:, 5] = 0.
    else:
        data[50, 3] -= .4
    result = fit(data)
    assert not result['valid']
    json.dumps(result, allow_nan=False)


def test_finite_overflow_is_an_unavailable_json_safe_result():
    data = samples()
    data[:, 4] = 1e308
    with np.errstate(over='ignore', invalid='ignore'):
        result = fit(data)
    assert not result['valid'], result
    assert result['reason'] == 'nonfinite_fit'
    json.dumps(result, allow_nan=False)


def test_legacy_owners_are_byte_unchanged_from_r16_source_boundary():
    source = inspect.getsource(owner)
    # All pre-existing definitions precede the additive R17 implementation.
    original = source.split('\n\ndef _spatial_design(', 1)[0]
    assert hashlib.sha256(original.encode()).hexdigest() == (
        '20f7f10272f6fa41a84be7991c0ecd3e3e33daa97db0854f720fce56e60c29ea')
    tree = ast.parse(source)
    assert sum(isinstance(node, ast.FunctionDef) and node.name == 'fit_profile'
               for node in tree.body) == 1
