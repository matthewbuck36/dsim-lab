"""Independent affine-field equations and numerical/support boundaries."""
import hashlib
import inspect
import json
import math

import numpy as np
import pytest

from ros_esc.filter_node import harmonic_gesc as owner


OMEGA = math.tau/3.
TRANSFER = 1j*OMEGA/(1+1j*OMEGA)
M = np.zeros((2, 6))
M[:, :2] = -np.array([[TRANSFER.real, TRANSFER.imag],
                       [-TRANSFER.imag, TRANSFER.real]])/.18
CENTER = np.array([.03, -.02])


def samples(*, duration=14., noise=False, zero=False, circle=False):
    t = np.arange(round(duration*30)+1)/30.
    phase = .31+OMEGA*t+.07*np.sin(.31*t)
    if circle:
        dx, dy = .1*np.cos(.27*t), .1*np.sin(.27*t)
    else:
        dx = .085*np.cos(.47*t)+.03*np.cos(1.13*t)
        dy = .075*np.sin(.39*t)+.025*np.sin(.91*t)
    xy = CENTER+np.column_stack((dx, dy))
    beta = np.array([0., 0., .007, -.004, .003, .002])
    beta[:2] = np.linalg.solve(M[:, :2], [0., 0.] if zero else [.01, -.02])
    jacobian = np.array([[-.8, .12], [-.09, -1.2]])
    gradients = np.array([[0., 0., .004, -.003, .001, .002],
                          [0., 0., -.002, .005, .003, -.001]])
    for axis in range(2):
        gradients[axis, :2] = .15*np.linalg.solve(M[:, :2], jacobian[:, axis])
    raw = -1.+.002*t+.1*dx-.2*dy+.3*dx*dx+.15*dx*dy-.4*dy*dy
    for k in (1, 2, 3):
        for j, wave in ((2*k-2, np.cos(k*phase)), (2*k-1, np.sin(k*phase))):
            raw += (beta[j]+gradients[0, j]*dx/.15+gradients[1, j]*dy/.15)*wave
    if noise:
        raw += .006*np.sin(9.37*t)+.003*np.cos(13.71*t)
    return np.column_stack((t, xy, phase, raw)), beta, gradients


def fit(data, mapping=M, center=CENTER):
    return owner.fit_affine_gesc_field(data, center, output_map=mapping)


@pytest.mark.parametrize('general_map', [False, True])
def test_exact_field_mapping_sign_axis_order_and_physical_metres(general_map):
    data, beta, gradients = samples()
    mapping = M.copy()
    if general_map:
        mapping[:, 2:] = [[.2, -.5, .3, .1], [.4, .2, -.1, .6]]
    result = fit(data, mapping)
    assert result['valid'], result
    expected_b = np.column_stack([mapping@g/.15 for g in gradients])
    expected = np.r_[mapping@beta, expected_b.ravel()]
    np.testing.assert_allclose(result['field_vector'], expected, atol=2e-8)
    _, _, _, design = owner._spatial_design(data, CENTER, data[-1, 0])
    np.testing.assert_allclose(design@result['coefficients'], data[:, 4], atol=2e-9)
    assert len(result['coefficients']) == 25
    assert result['regularization'] == 0.
    assert result['source_start_sec'] == 0. and result['source_end_sec'] == 14.
    assert result['sample_count'] == len(data)


def test_zero_anchor_h1_does_not_discard_restoring_jacobian():
    data, _, _ = samples(zero=True)
    result = fit(data)
    assert result['valid'], result
    np.testing.assert_allclose(result['field_vector'][:2], 0., atol=2e-8)
    np.testing.assert_allclose(result['field_vector'][2:], [-.8, .12, -.09, -1.2], atol=2e-8)


def test_spatial_dc_nuisance_null_does_not_discard_estimable_field():
    data, _, _ = samples(circle=True)
    result = fit(data)
    assert result['valid'], result
    assert result['rank'] < 25  # dx^2+dy^2 is a constant on this circle.
    assert result['output_null_ratio'] <= 1e-8
    np.testing.assert_allclose(result['field_vector'], [.01, -.02, -.8, .12, -.09, -1.2], atol=2e-7)


@pytest.mark.parametrize('geometry', ['constant', 'phase_locked'])
def test_identifiable_anchor_direction_does_not_rescue_unidentified_field(geometry):
    data, _, _ = samples()
    if geometry == 'constant':
        data[:, 1:3] = CENTER
    else:
        data[:, 1] = CENTER[0]+.08*np.cos(data[:, 3])
        data[:, 2] = CENTER[1]+.08*np.sin(data[:, 3])
    result = fit(data)
    assert not result['valid'], result
    assert result['reason'] == 'affine_field_not_estimable'
    assert not result['output_estimable']
    assert result['field_vector'] is None


def test_full_and_caller_selected_halves_share_anchor_without_internal_splitting():
    data, _, _ = samples(duration=28.)
    middle = len(data)//2
    results = [fit(s) for s in (data, data[:middle], data[middle:])]
    for result in results:
        assert result['valid'], result
        assert result['center_xy'] == CENTER.tolist() and result['output_map'] == M.tolist()
        np.testing.assert_allclose(result['field_vector'], [.01, -.02, -.8, .12, -.09, -1.2], atol=2e-7)
    assert results[1]['source_end_sec'] < results[2]['source_start_sec']
    assert results[1]['sample_count']+results[2]['sample_count'] == results[0]['sample_count']


def test_full_cross_covariance_matches_independent_influence_and_finite_difference():
    data, _, _ = samples(noise=True)
    result = fit(data)
    assert result['valid'], result
    _, _, _, design = owner._spatial_design(data, CENTER, data[-1, 0])
    solution = owner._spatial_solve(design, data[:, 4], 0.)
    f = solution['influence']
    influence = np.vstack((M@f[7:13],
        (M@f[13:19]/.15)[0], (M@f[19:25]/.15)[0],
        (M@f[13:19]/.15)[1], (M@f[19:25]/.15)[1]))
    adjusted = influence*solution['residual']/(1-solution['leverage'])
    kernel = np.maximum(0., 1-np.abs(data[:, 0, None]-data[None, :, 0]))
    expected = adjusted@kernel@adjusted.T
    np.testing.assert_allclose(result['field_covariance'], expected, atol=1e-13)
    assert np.linalg.norm(expected[:2, 2:]) > 1e-12
    assert np.linalg.eigvalsh(result['field_covariance']).min() >= -1e-12
    for i in (0, 97, len(data)-1):
        upper, lower = data.copy(), data.copy()
        upper[i, 4] += 1e-6; lower[i, 4] -= 1e-6
        high, low = fit(upper), fit(lower)
        assert high['valid'] and low['valid']
        derivative = (np.array(high['field_vector'])-low['field_vector'])/2e-6
        np.testing.assert_allclose(derivative, influence[:, i], atol=2e-6, rtol=2e-5)


def test_cost_scale_dc_and_source_coordinate_offsets_preserve_field():
    data, _, _ = samples(noise=True)
    original = fit(data)
    changed = data.copy()
    changed[:, 4] = -3*changed[:, 4]+17.
    changed[:, 0] += 10000.
    changed[:, 1:3] += [2., -3.]
    result = fit(changed, center=CENTER+[2., -3.])
    assert original['valid'] and result['valid']
    np.testing.assert_allclose(result['field_vector'], -3*np.array(original['field_vector']), atol=2e-7)
    np.testing.assert_allclose(result['field_covariance'], 9*np.array(original['field_covariance']), atol=1e-10)


def test_world_rotation_rotates_vector_and_both_jacobian_axes():
    data, _, _ = samples(noise=True)
    original = fit(data)
    angle = .61
    rotation = np.array([[math.cos(angle), -math.sin(angle)],
                         [math.sin(angle), math.cos(angle)]])
    rotated = data.copy()
    rotated[:, 1:3] = data[:, 1:3]@rotation.T
    rotated[:, 3] += angle
    result = fit(rotated, center=rotation@CENTER)
    assert original['valid'] and result['valid']
    vector = np.array(original['field_vector'])
    expected = np.r_[rotation@vector[:2], (rotation@vector[2:].reshape(2, 2)@rotation.T).ravel()]
    np.testing.assert_allclose(result['field_vector'], expected, atol=2e-7)


@pytest.mark.parametrize('defect', ['shape', 'few', 'many', 'nonfinite', 'order',
                                  'gap', 'duration', 'excursion', 'phase_reverse',
                                  'few_rotations', 'sectors'])
def test_support_rejections_preserve_json_safe_unavailability(defect):
    data, _, _ = samples(duration=31. if defect == 'duration' else 14.)
    if defect == 'shape': data = data[:, :4]
    elif defect == 'few': data = data[:47]
    elif defect == 'many': data = np.tile(data, (3, 1))
    elif defect == 'nonfinite': data[7, 4] = np.nan
    elif defect == 'order': data[10, 0] = data[9, 0]
    elif defect == 'gap': data[100:, 0] += .11
    elif defect == 'excursion': data[40, 1] = CENTER[0]+.3
    elif defect == 'phase_reverse': data[50, 3] -= .2
    elif defect == 'few_rotations': data[:, 3] *= .2
    elif defect == 'sectors': data[:, 3] = np.floor(data[:, 0]/3)*math.tau+.1
    result = fit(data)
    assert not result['valid'], result
    assert result['field_vector'] is None and result['field_covariance'] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('mapping', [np.zeros((2, 6)), np.ones((6, 2)), np.full((2, 6), np.nan)])
def test_output_map_validation(mapping):
    data, _, _ = samples()
    result = fit(data, mapping)
    assert not result['valid'] and result['reason'] == 'invalid_output_map'


def test_constant_finite_cost_and_overflow_are_distinguished():
    data, _, _ = samples()
    data[:, 4] = -1.
    result = fit(data)
    assert result['valid'], result
    np.testing.assert_allclose(result['field_vector'], 0., atol=1e-12)
    data[:, 4] = 1e308
    with np.errstate(over='ignore', invalid='ignore'):
        result = fit(data)
    assert not result['valid'] and result['reason'] == 'nonfinite_fit'
    json.dumps(result, allow_nan=False)


def test_previous_entrypoints_remain_exact_source_prefix():
    prefix = inspect.getsource(owner).split('\n\ndef fit_affine_gesc_field(', 1)[0]
    assert hashlib.sha256(prefix.encode()).hexdigest() == (
        '449f4403edef7867b11a22f1715d346158f5ff8d719ec949fde084ac18604b1a')
