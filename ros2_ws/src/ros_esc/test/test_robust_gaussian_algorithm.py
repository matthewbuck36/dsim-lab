"""Deterministic ROS-independent tests for the Phase 03 Gaussian algorithm."""

from dataclasses import replace
import math

import numpy as np
import pytest

from ros_esc.gaussian_fill_node.basin_estimator import (
    BasinEstimate,
    BasinSample,
    CostSnapshot,
    EstimatorConfig,
    PoseSnapshot,
    QuadraticFit,
    clip_covariance,
    estimate_basin,
    fit_local_quadratic,
    freeze_sample_window,
    normalized_kernel_weights,
    synchronize_samples,
    weighted_covariance,
)
from ros_esc.gaussian_fill_node.fill_designer import (
    FillDesignConfig,
    design_fill,
    gaussian_gradient,
    gaussian_value,
    initial_fill_geometry,
    residual_minima_count,
)
from ros_esc.gaussian_fill_node.fill_registry import (
    FillRegistry,
    RegistryConfig,
    active_fill_value,
    associate_candidate,
    retain_cluster_samples,
)


def sample(stamp, x, y, cost, state=1):
    """Build one valid estimator sample."""

    return BasinSample(
        stamp_sec=float(stamp),
        x=float(x),
        y=float(y),
        yaw=0.0,
        raw_sensor_value=float("nan"),
        raw_sensor_valid=False,
        raw_cost=float(cost),
        source_score=0.2,
        source_score_valid=True,
        algorithm_state=state,
    )


def quadratic_fit(hessian=None, gradient=None, valid=True):
    """Build a deterministic quadratic fit fixture."""

    hessian = np.eye(2) * 0.1 if hessian is None else np.asarray(hessian, dtype=float)
    gradient = np.zeros(2) if gradient is None else np.asarray(gradient, dtype=float)
    values, vectors = np.linalg.eigh(hessian)
    positive = vectors @ np.diag(np.maximum(values, 0.0)) @ vectors.T
    return QuadraticFit(
        intercept=0.0,
        gradient=gradient,
        hessian=hessian,
        positive_hessian=positive,
        residual_rms=0.0,
        condition_number=1.0,
        rank=6,
        valid=valid,
        predictor_valid=True,
    )


def estimate_fixture(
    covariance=None,
    hessian=None,
    depth=0.02,
    sample_count=40,
):
    """Build a fill-designer estimate fixture."""

    covariance = (
        np.eye(2) * 0.091
        if covariance is None
        else np.asarray(covariance, dtype=float)
    )
    samples = tuple(
        sample(index * 0.1, math.cos(index), math.sin(index), 0.1)
        for index in range(sample_count)
    )
    return BasinEstimate(
        center=np.zeros(2),
        weights=np.full(sample_count, 1.0 / sample_count),
        sample_covariance=covariance,
        quadratic=quadratic_fit(hessian=hessian),
        center_cost=0.0,
        shoulder_cost=depth,
        depth=depth,
        shoulder_fallback=False,
        sample_count=sample_count,
        angular_coverage=1.0,
        spatial_coverage=1.0,
        samples=samples,
    )


def version_values(center, amplitude, sigma, source_timestamp=1.0):
    """Build registry commit values."""

    covariance = np.eye(2) * sigma ** 2
    return {
        "source_timestamp": source_timestamp,
        "center": np.asarray(center, dtype=float),
        "amplitude": amplitude,
        "covariance": covariance,
        "sigma_major": sigma,
        "sigma_minor": sigma,
        "orientation": 0.0,
        "support_radius": 3.0 * sigma,
        "exit_radius": 2.5 * sigma,
        "confidence": 0.8,
        "sample_count": 40,
        "fit_residual": 0.01,
        "fit_condition_number": 10.0,
        "fit_condition_number_valid": True,
        "design_escalations": 0,
    }


def test_synchronization_is_closest_one_to_one_with_cost_stamp():
    poses = [PoseSnapshot(1.00, 1, 2, 0), PoseSnapshot(1.10, 3, 4, 0)]
    costs = [
        CostSnapshot(1.03, math.nan, False, -1, 0.2, True, 1, True),
        CostSnapshot(1.18, math.nan, False, -2, 0.3, True, 1, True),
    ]
    synchronized, unmatched = synchronize_samples(poses, costs, 0.05)
    assert len(synchronized) == 1
    assert synchronized[0].stamp_sec == 1.03
    assert (synchronized[0].x, synchronized[0].y) == (1.0, 2.0)
    assert unmatched == 2


def test_kernel_weights_sum_to_one_and_prefer_lower_cost():
    weights = normalized_kernel_weights(
        np.array([[-1.0, 0.0], [1.0, 0.0]]),
        np.zeros(2),
        np.array([0.0, 0.05]),
        0.25,
        0.05,
    )
    assert np.sum(weights) == pytest.approx(1.0, abs=1e-15)
    assert weights == pytest.approx([0.7310585786, 0.2689414214])
    assert weights[0] > weights[1]


def test_kernel_weights_remain_finite_at_extreme_distance():
    weights = normalized_kernel_weights(
        np.array([[0.0, 0.0], [1000.0, 0.0]]),
        np.zeros(2),
        np.zeros(2),
        0.25,
        0.05,
    )
    assert np.all(np.isfinite(weights))
    assert np.sum(weights) == 1.0
    assert weights == pytest.approx([1.0, 0.0])


def test_center_estimate_is_stable_under_distant_high_cost_outlier():
    samples = [
        sample(0.0, 0.9, 2.0, 0.0),
        sample(0.1, 1.1, 2.0, 0.0),
        sample(0.2, 1.0, 1.9, 0.0),
        sample(0.3, 1.0, 2.1, 0.0),
        sample(0.4, 10.0, -9.0, 50.0),
    ]
    estimate = estimate_basin(
        samples,
        EstimatorConfig(minimum_valid_samples=4, center_tolerance_m=1e-12),
    )
    assert estimate.center == pytest.approx([1.0, 2.0], abs=1e-6)


def test_covariance_is_symmetric_positive_semidefinite_and_clipped():
    positions = np.array([[0.1, 0], [-0.1, 0], [0, 0.2], [0, -0.2]])
    covariance = weighted_covariance(positions, np.zeros(2), np.full(4, 0.25))
    assert covariance == pytest.approx(np.diag([0.005, 0.020]))
    clipped = clip_covariance(np.array([[2.0, 0.2], [0.1, -1.0]]), 0.0025, 0.25)
    assert clipped == pytest.approx(clipped.T)
    assert np.linalg.eigvalsh(clipped) == pytest.approx([0.0025, 0.25])


def test_initial_width_calculation_and_clipping_are_exact():
    estimate = estimate_fixture(covariance=np.diag([0.0025, 0.25]))
    geometry = initial_fill_geometry(estimate, FillDesignConfig())
    assert np.linalg.eigvalsh(geometry.covariance) == pytest.approx(
        [0.02875, 0.6475]
    )
    assert geometry.sigma_minor == pytest.approx(0.1695582496)
    assert geometry.sigma_major == pytest.approx(0.8046738470)


def test_quadratic_recovery_is_deterministic():
    positions = np.array([(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1)])
    costs = np.array(
        [2 + 3 * x - 2 * y + 2 * x ** 2 + x * y + y ** 2 for x, y in positions]
    )
    fit = fit_local_quadratic(
        positions,
        costs,
        np.zeros(2),
        np.full(9, 1.0 / 9.0),
        EstimatorConfig(minimum_valid_samples=1, quadratic_ridge_lambda=0.0),
    )
    assert fit.intercept == pytest.approx(2.0, abs=1e-12)
    assert fit.gradient == pytest.approx([3.0, -2.0], abs=1e-12)
    np.testing.assert_allclose(
        fit.hessian, np.array([[4.0, 1.0], [1.0, 2.0]]), atol=1e-12
    )
    assert fit.residual_rms < 1e-12
    assert np.linalg.eigvalsh(fit.hessian) == pytest.approx(
        [3.0 - math.sqrt(2.0), 3.0 + math.sqrt(2.0)]
    )


def test_amplitude_scales_with_width_and_curvature():
    narrow = estimate_fixture(covariance=np.diag([0.01, 0.02]), hessian=np.diag([4, 2]))
    wide = replace(narrow, sample_covariance=np.diag([0.04, 0.08]))
    config = FillDesignConfig(amplitude_min=0.01, amplitude_max=10.0)
    narrow_fill = initial_fill_geometry(narrow, config)
    wide_fill = initial_fill_geometry(wide, config)
    assert wide_fill.amplitude_curvature > narrow_fill.amplitude_curvature
    assert wide_fill.amplitude > narrow_fill.amplitude


def test_current_narrow_fill_can_leave_a_residual_minimum():
    estimate = estimate_fixture(covariance=np.eye(2) * 0.091, hessian=np.eye(2) * 0.1)
    geometry = initial_fill_geometry(
        estimate,
        FillDesignConfig(amplitude_min=0.1, amplitude_max=10.0),
    )
    assert geometry.sigma_major == pytest.approx(0.5)
    assert geometry.amplitude == pytest.approx(0.1)
    assert residual_minima_count(estimate, geometry, FillDesignConfig()) > 0


def test_robust_design_removes_fitted_interior_minimum_by_escalation():
    estimate = estimate_fixture(covariance=np.eye(2) * 0.091, hessian=np.eye(2) * 0.1)
    config = FillDesignConfig(amplitude_min=0.1, amplitude_max=10.0, sigma_ceiling_m=2.0)
    design = design_fill(estimate, config)
    assert design.success is True
    assert design.residual_minima_count == 0
    assert design.design_escalations > 0
    assert design.geometry.amplitude > 0.1
    assert design.geometry.sigma_major > 0.5


def test_residual_minima_trigger_bounded_failure_at_default_caps():
    estimate = estimate_fixture(covariance=np.eye(2) * 0.091, hessian=np.eye(2) * 0.1)
    design = design_fill(estimate, FillDesignConfig())
    assert design.success is False
    assert design.design_escalations == 5
    assert design.geometry.amplitude == 3.0
    assert design.geometry.sigma_major == pytest.approx(1.25)
    assert design.residual_minima_count > 0


def test_nearby_candidate_merges_with_stable_soft_probability():
    registry = FillRegistry()
    registry.commit_new(version_values((0, 0), 1.0, 0.3), [sample(1, 0, 0, 0)])
    registry.commit_new(version_values((1, 0), 1.0, 0.3), [sample(2, 1, 0, 0)])
    association = registry.associate(np.array([0.1, 0.0]), 0.3)
    assert association.cluster_id == 1
    assert association.probability == pytest.approx(0.8320183851)
    assert association.merge is True


def test_distant_and_soft_ambiguous_candidates_do_not_merge():
    registry = FillRegistry()
    registry.commit_new(version_values((0, 0), 1.0, 0.3), [sample(1, 0, 0, 0)])
    distant = registry.associate(np.array([5.0, 0.0]), 0.3)
    assert distant.probability == 1.0
    assert distant.hard_radius_m == pytest.approx(0.6)
    assert distant.merge is False

    clusters = list(registry.active_clusters)
    other = FillRegistry()
    other.commit_new(version_values((1, 0), 1.0, 0.3), [sample(2, 1, 0, 0)])
    clusters.extend(other.active_clusters)
    ambiguous = associate_candidate(
        np.array([0.5, 0.0]), 0.3, clusters, RegistryConfig()
    )
    assert ambiguous.probability == pytest.approx(0.5)
    assert ambiguous.merge is False


def test_superseded_fill_is_frozen_and_not_double_counted():
    registry = FillRegistry()
    _, first = registry.commit_new(
        version_values((0, 0), 1.0, 0.3), [sample(1, 0, 0, 0)]
    )
    old, replacement = registry.commit_revision(
        first.cluster_id,
        version_values((0, 0), 2.0, 0.3, source_timestamp=2.0),
        [sample(1, 0, 0, 0), sample(2, 0.1, 0, 0)],
    )
    assert old.active is False and old.superseded is True
    assert replacement.revision == 2
    assert registry.active_count == 1
    assert len(registry.history) == 3
    assert active_fill_value(np.zeros(2), registry.history) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        old.center[0] = 99.0


def test_fill_gradient_descent_direction_points_outward_for_minimization():
    value = gaussian_value(np.array([1.0, 0.0]), np.zeros(2), 2.0, np.eye(2))
    gradient = gaussian_gradient(
        np.array([1.0, 0.0]), np.zeros(2), 2.0, np.eye(2)
    )
    assert value == pytest.approx(1.2130613194)
    assert gradient == pytest.approx([-1.2130613194, 0.0])
    assert -gradient[0] > 0.0


def test_window_boundaries_timestamp_speed_mad_and_minimum_sample_failure():
    config = EstimatorConfig(
        estimation_window_sec=2.0,
        maximum_sample_age_sec=2.0,
        maximum_position_speed_mps=1.0,
        minimum_valid_samples=3,
    )
    samples = [
        sample(8.0, 0.0, 0.0, 0.0),
        sample(8.5, 0.1, 0.0, 0.1),
        sample(8.5, 0.2, 0.0, 0.1),
        sample(9.0, 5.0, 0.0, 0.2),
        sample(9.5, 0.2, 0.0, 100.0),
        sample(10.0, 0.3, 0.0, 0.2),
    ]
    window = freeze_sample_window(samples, 10.0, config)
    assert window.samples[0].stamp_sec == 8.0
    assert window.samples[-1].stamp_sec == 10.0
    assert window.rejected["timestamp"] == 1
    assert window.rejected["speed_jump"] == 1
    assert window.rejected["cost_mad"] == 1
    with pytest.raises(ValueError, match="minimum valid samples"):
        estimate_basin(window.samples[:2], config)


def test_depth_only_fallback_and_orientation_and_retention_are_deterministic():
    line_samples = tuple(sample(i * 0.1, i * 0.01, 0.0, i * 0.01) for i in range(8))
    estimate = estimate_basin(
        line_samples,
        EstimatorConfig(minimum_valid_samples=4, quadratic_condition_number_max=10.0),
    )
    assert estimate.quadratic.valid is False
    geometry = initial_fill_geometry(estimate, FillDesignConfig())
    assert -math.pi / 2 <= geometry.orientation < math.pi / 2

    many = [sample(index, index, 0, 0) for index in range(10)]
    many.append(sample(5, 999, 0, 0))
    retained = retain_cluster_samples(many, 4)
    assert len(retained) == 4
    assert [entry.stamp_sec for entry in retained] == sorted(
        entry.stamp_sec for entry in retained
    )
    assert next(entry for entry in retained if entry.stamp_sec == 0).x == 0
