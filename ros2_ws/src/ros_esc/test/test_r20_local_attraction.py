"""Independent mathematical fixtures for the optional raw-field decision."""
from copy import deepcopy

import numpy as np
import pytest

from ros_esc.gaussian_fill_node.basin_estimator import (
    field_standardized_error, verify_local_attraction)


def fixture(jacobian=-np.eye(2), zero=(0., 0.), covariance_scale=1e-6):
    positions = .12*np.array([[1, 0], [1, 1], [0, 1], [-1, 1],
                             [-1, 0], [-1, -1], [0, -1], [1, -1]])
    jacobian = np.asarray(jacobian, dtype=float)
    vector = np.r_[-jacobian@zero, jacobian.ravel()]
    full = dict(valid=True, field_vector=vector.tolist(),
                field_covariance=(covariance_scale*np.eye(6)).tolist(),
                center_xy=[0., 0.], output_map=np.eye(2, 6).tolist(),
                source_start_sec=0., source_end_sec=.07, sample_count=8)
    first, second = deepcopy(full), deepcopy(full)
    first.update(source_end_sec=.03, sample_count=4)
    second.update(source_start_sec=.04, sample_count=4)
    return full, first, second, positions


def decide(values, **kwargs):
    return verify_local_attraction(*values, center=(0., 0.),
                                   error_multiplier=3., change_cutoff=4., **kwargs)


def test_restoring_field_accepts_zero_direction_at_candidate():
    result = decide(fixture())
    assert result['valid'] and result['admitted']
    assert result['zero_displacement'] == [0., 0.]
    assert result['zero_radius'] == pytest.approx(.003/.997)
    assert result['zero_hull_clearance'] == pytest.approx(.12)


@pytest.mark.parametrize('jacobian', [np.zeros((2, 2)), np.diag([-1., 1.]),
                                     np.eye(2), [[-1., 6.], [0., -1.]]])
def test_flat_saddle_repeller_and_noncontractive_nonnormal_reject(jacobian):
    result = decide(fixture(jacobian))
    assert result['valid'] and not result['admitted']
    assert result['reason'] == 'restoring_response_not_established'


def test_constant_slope_does_not_establish_attraction():
    values = fixture(np.zeros((2, 2)))
    for fit in values[:3]:
        fit['field_vector'][0] = .2
    result = decide(values)
    assert result['valid'] and not result['admitted']


@pytest.mark.parametrize('zero,covariance_scale', [((.2, 0.), 1e-6), ((.119, 0.), 1e-6),
                                                ((.12, 0.), 0.)])
def test_outside_uncertain_and_exact_boundary_zero_reject(zero, covariance_scale):
    result = decide(fixture(zero=zero, covariance_scale=covariance_scale))
    assert result['valid'] and not result['admitted']
    assert result['reason'] == 'zero_region_not_inside_observed_support'


def test_halves_with_changed_field_reject_despite_restoring_full_fit():
    values = fixture()
    values[2]['field_vector'][2] = 1.
    result = decide(values)
    assert result['valid'] and not result['admitted']
    assert result['reason'] == 'field_changed_between_halves'


@pytest.mark.parametrize('mutation', ['center', 'map', 'overlap', 'gap', 'count', 'unavailable'])
def test_incompatible_field_composition_is_unavailable(mutation):
    values = fixture()
    if mutation == 'center':
        values[1]['center_xy'][0] = .01
    elif mutation == 'map':
        values[2]['output_map'][0][0] = -1.
    elif mutation == 'overlap':
        values[2]['source_start_sec'] = .02
    elif mutation == 'gap':
        values[1]['source_end_sec'] = -.2
    elif mutation == 'count':
        values[0]['sample_count'] = 9
    else:
        values[1]['valid'] = False
    result = decide(values)
    assert not result['valid'] and not result['admitted']


def test_degenerate_spatial_support_is_unavailable():
    values = list(fixture())
    values[3][:, 1] = 0.
    assert not decide(values)['valid']


@pytest.mark.parametrize('covariance', [np.diag([-1., 1., 1., 1., 1., 1.]),
                                       np.eye(5), np.full((6, 6), np.nan)])
def test_invalid_covariance_is_unavailable(covariance):
    result = field_standardized_error(np.zeros(6), covariance)
    assert not result['valid'] and result['score'] is None


def test_asymmetric_covariance_is_not_silently_repaired():
    covariance = np.eye(6)
    covariance[0, 1] = .1
    assert not field_standardized_error(np.zeros(6), covariance)['valid']


def test_covariance_nullspace_retains_unbounded_error():
    covariance = np.diag([1., 1., 1., 1., 1., 0.])
    assert field_standardized_error(np.zeros(6), covariance)['score'] == 0.
    result = field_standardized_error([0., 0., 0., 0., 0., .001], covariance)
    assert not result['valid'] and result['score'] is None
    assert field_standardized_error(np.zeros(6), np.zeros((6, 6)))['score'] == 0.


def test_joint_error_uses_full_cross_covariance_and_changes_coordinates_correctly():
    factor = np.eye(6)
    factor[0, 4], factor[2, 1] = .8, -.6
    covariance = factor@factor.T
    delta = np.array([.1, -.3, .8, 1., -.5, .2])
    expected = np.linalg.norm(np.linalg.solve(factor, delta))
    result = field_standardized_error(delta, covariance)
    assert result['score'] == pytest.approx(expected)
    transform = np.diag([3., .1, .2, 1.5, .4, 2.])
    transformed = field_standardized_error(transform@delta, transform@covariance@transform.T)
    assert transformed['score'] == pytest.approx(expected)


def test_attraction_decision_translates_and_rotates_with_observed_field():
    values = fixture(np.diag([-1., -2.]), zero=(.02, -.01))
    before = decide(values)
    angle = .713
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    center = np.array([7., -3.])
    transform = np.zeros((6, 6))
    transform[:2, :2] = rotation
    transform[2:, 2:] = np.kron(rotation, rotation)
    for fit in values[:3]:
        fit['center_xy'] = center.tolist()
        fit['field_vector'] = (transform@fit['field_vector']).tolist()
        fit['field_covariance'] = (transform@np.array(fit['field_covariance'])@transform.T).tolist()
        fit['output_map'] = (rotation@fit['output_map']).tolist()
    after = verify_local_attraction(*values[:3], values[3]@rotation.T+center, center,
                                   error_multiplier=3., change_cutoff=4.)
    assert after['admitted'] and before['admitted']
    assert after['zero_displacement'] == pytest.approx(rotation@before['zero_displacement'])
    assert after['zero_radius'] == pytest.approx(before['zero_radius'])
    assert after['zero_hull_clearance'] == pytest.approx(before['zero_hull_clearance'])
