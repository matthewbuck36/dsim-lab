"""Pure adaptive anisotropic Gaussian fill design and validation helpers."""

from dataclasses import dataclass, replace
import math
from typing import Tuple

import numpy as np

from ros_esc.gaussian_fill_node.basin_estimator import BasinEstimate


@dataclass(frozen=True)
class FillDesignConfig:
    """Configuration for width, amplitude, grid validation, and confidence."""

    covariance_scale: float = 2.5
    sigma_floor_m: float = 0.15
    sigma_ceiling_m: float = 1.25
    amplitude_depth_scale: float = 1.5
    amplitude_curvature_scale: float = 1.2
    amplitude_min: float = 0.10
    amplitude_max: float = 3.00
    validation_grid_points_per_axis: int = 41
    validation_support_sigma: float = 3.0
    maximum_design_escalations: int = 5
    amplitude_escalation_factor: float = 1.5
    width_escalation_factor: float = 1.25
    grid_minimum_tolerance: float = 1e-9
    support_sigma: float = 3.0
    exit_sigma: float = 2.5
    low_confidence_threshold: float = 0.60

    def __post_init__(self):
        positive = (
            self.covariance_scale,
            self.sigma_floor_m,
            self.sigma_ceiling_m,
            self.amplitude_depth_scale,
            self.amplitude_curvature_scale,
            self.amplitude_min,
            self.amplitude_max,
            self.validation_support_sigma,
            self.amplitude_escalation_factor,
            self.width_escalation_factor,
            self.support_sigma,
            self.exit_sigma,
        )
        if not all(math.isfinite(value) and value > 0.0 for value in positive):
            raise ValueError("fill design scales and limits must be finite and positive")
        if self.sigma_ceiling_m < self.sigma_floor_m:
            raise ValueError("sigma ceiling must not be below sigma floor")
        if self.amplitude_max < self.amplitude_min:
            raise ValueError("amplitude maximum must not be below minimum")
        if self.validation_grid_points_per_axis < 3:
            raise ValueError("validation grid must have at least three points per axis")
        if self.maximum_design_escalations < 0:
            raise ValueError("maximum design escalations must be nonnegative")


@dataclass(frozen=True)
class FillGeometry:
    """One fill geometry/amplitude proposal."""

    center: np.ndarray
    covariance: np.ndarray
    amplitude: float
    sigma_major: float
    sigma_minor: float
    orientation: float
    support_radius: float
    exit_radius: float
    amplitude_depth: float
    amplitude_curvature: float


@dataclass(frozen=True)
class FillDesign:
    """Validated fill result plus all bounded-escalation diagnostics."""

    geometry: FillGeometry
    success: bool
    residual_minima_count: int
    design_escalations: int
    amplitude_steps: int
    width_steps: int
    confidence: float
    confidence_components: Tuple[float, ...]
    amplitude_at_cap: bool
    width_at_cap: bool
    escalation_limit_reached: bool


def _canonical_orientation(eigenvalues, eigenvectors):
    if math.isclose(
        float(eigenvalues[0]),
        float(eigenvalues[1]),
        rel_tol=1e-9,
        abs_tol=1e-12,
    ):
        return 0.0
    vector = eigenvectors[:, int(np.argmax(eigenvalues))]
    angle = math.atan2(float(vector[1]), float(vector[0]))
    return (angle + math.pi / 2.0) % math.pi - math.pi / 2.0


def geometry_from_covariance(
    center,
    covariance,
    amplitude,
    amplitude_depth,
    amplitude_curvature,
    config,
):
    """Canonicalize principal widths/orientation and derive support radii."""

    covariance = 0.5 * (
        np.asarray(covariance, dtype=np.float64)
        + np.asarray(covariance, dtype=np.float64).T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    widths = np.sqrt(np.maximum(eigenvalues, 0.0))
    sigma_major = float(widths[0])
    sigma_minor = float(widths[1])
    orientation = _canonical_orientation(eigenvalues, eigenvectors)
    return FillGeometry(
        center=np.asarray(center, dtype=np.float64),
        covariance=covariance,
        amplitude=float(amplitude),
        sigma_major=sigma_major,
        sigma_minor=sigma_minor,
        orientation=orientation,
        support_radius=config.support_sigma * sigma_major,
        exit_radius=config.exit_sigma * sigma_major,
        amplitude_depth=float(amplitude_depth),
        amplitude_curvature=float(amplitude_curvature),
    )


def initial_fill_geometry(estimate: BasinEstimate, config: FillDesignConfig):
    """Construct the width-coupled initial fill proposal."""

    sample_covariance = np.asarray(estimate.sample_covariance, dtype=np.float64)
    covariance = (
        config.covariance_scale * sample_covariance
        + config.sigma_floor_m ** 2 * np.eye(2)
    )
    eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    widths = np.clip(
        np.sqrt(np.maximum(eigenvalues, 0.0)),
        config.sigma_floor_m,
        config.sigma_ceiling_m,
    )
    covariance = eigenvectors @ np.diag(widths ** 2) @ eigenvectors.T
    covariance = 0.5 * (covariance + covariance.T)
    amplitude_depth = config.amplitude_depth_scale * estimate.depth
    maximum_curvature = (
        float(np.max(np.linalg.eigvalsh(estimate.quadratic.positive_hessian)))
        if estimate.quadratic.valid
        else 0.0
    )
    amplitude_curvature = (
        config.amplitude_curvature_scale
        * maximum_curvature
        * float(np.max(np.linalg.eigvalsh(covariance)))
    )
    amplitude = float(
        np.clip(
            max(config.amplitude_min, amplitude_depth, amplitude_curvature),
            config.amplitude_min,
            config.amplitude_max,
        )
    )
    return geometry_from_covariance(
        estimate.center,
        covariance,
        amplitude,
        amplitude_depth,
        amplitude_curvature,
        config,
    )


def gaussian_value(point, center, amplitude, covariance):
    """Evaluate a positive anisotropic Gaussian fill."""

    delta = np.asarray(point, dtype=np.float64) - np.asarray(center, dtype=np.float64)
    inverse = np.linalg.inv(np.asarray(covariance, dtype=np.float64))
    exponent = -0.5 * float(delta.T @ inverse @ delta)
    return float(amplitude) * math.exp(exponent)


def gaussian_gradient(point, center, amplitude, covariance):
    """Return the fill gradient; minimization descent points opposite it."""

    delta = np.asarray(point, dtype=np.float64) - np.asarray(center, dtype=np.float64)
    inverse = np.linalg.inv(np.asarray(covariance, dtype=np.float64))
    return -gaussian_value(point, center, amplitude, covariance) * (inverse @ delta)


def quadratic_value(point, estimate):
    """Evaluate the retained fitted local model at an absolute point."""

    delta = np.asarray(point, dtype=np.float64) - estimate.center
    quadratic = estimate.quadratic
    return float(
        quadratic.intercept
        + quadratic.gradient @ delta
        + 0.5 * delta.T @ quadratic.hessian @ delta
    )


def residual_minima_count(estimate, geometry, config):
    """Count 8-neighbor interior minima inside the configured exit support."""

    covariance = geometry.covariance
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    widths = np.sqrt(np.maximum(eigenvalues, 0.0))
    coordinates = np.linspace(
        -config.validation_support_sigma,
        config.validation_support_sigma,
        config.validation_grid_points_per_axis,
    )
    values = np.empty((coordinates.size, coordinates.size), dtype=np.float64)
    mahalanobis = np.empty_like(values)
    for row, first in enumerate(coordinates):
        for column, second in enumerate(coordinates):
            principal_delta = np.array(
                [first * widths[0], second * widths[1]], dtype=np.float64
            )
            point = geometry.center + eigenvectors @ principal_delta
            values[row, column] = quadratic_value(point, estimate) + gaussian_value(
                point,
                geometry.center,
                geometry.amplitude,
                covariance,
            )
            mahalanobis[row, column] = math.hypot(first, second)
    minima = 0
    tolerance = config.grid_minimum_tolerance
    for row in range(1, coordinates.size - 1):
        for column in range(1, coordinates.size - 1):
            if mahalanobis[row, column] > config.exit_sigma:
                continue
            neighborhood = values[row - 1:row + 2, column - 1:column + 2]
            center_value = float(values[row, column])
            neighbors = np.delete(neighborhood.reshape(-1), 4)
            if (
                np.all(center_value <= neighbors + tolerance)
                and np.any(center_value < neighbors - tolerance)
            ):
                minima += 1
    return minima


def confidence_components(estimate, design, minimum_valid_samples, condition_limit):
    """Compute the six specified bounded confidence components."""

    sample_count = min(1.0, estimate.sample_count / (2.0 * minimum_valid_samples))
    coverage = 0.5 * (estimate.angular_coverage + estimate.spatial_coverage)
    condition = estimate.quadratic.condition_number
    if not estimate.quadratic.valid or not math.isfinite(condition):
        fit_condition = 0.0
    else:
        denominator = math.log10(max(float(condition_limit), 1.0000001))
        fit_condition = max(
            0.0,
            1.0 - math.log10(max(condition, 1.0)) / denominator,
        )
    costs = np.array([sample.raw_cost for sample in estimate.samples], dtype=np.float64)
    cost_range = max(
        float(np.percentile(costs, 90.0) - np.percentile(costs, 10.0)),
        estimate.depth,
    )
    fit_residual = max(0.0, 1.0 - estimate.quadratic.residual_rms / cost_range)
    cap_use = 1.0 - np.mean(
        [
            float(design.amplitude_at_cap),
            float(design.width_at_cap),
            float(design.escalation_limit_reached),
        ]
    )
    validation = 1.0 if design.success else 0.0
    return tuple(
        float(np.clip(value, 0.0, 1.0))
        for value in (
            sample_count,
            coverage,
            fit_condition,
            fit_residual,
            cap_use,
            validation,
        )
    )


def design_fill(
    estimate,
    config,
    minimum_valid_samples=40,
    condition_limit=1e8,
):
    """Design, validate, and boundedly escalate one adaptive fill."""

    geometry = initial_fill_geometry(estimate, config)
    residual = residual_minima_count(estimate, geometry, config)
    amplitude_steps = 0
    width_steps = 0
    rounds = 0
    while residual > 0 and rounds < config.maximum_design_escalations:
        rounds += 1
        increased_amplitude = min(
            geometry.amplitude * config.amplitude_escalation_factor,
            config.amplitude_max,
        )
        if increased_amplitude > geometry.amplitude:
            amplitude_steps += 1
        geometry = replace(geometry, amplitude=increased_amplitude)
        residual = residual_minima_count(estimate, geometry, config)
        if residual == 0:
            break

        eigenvalues, eigenvectors = np.linalg.eigh(geometry.covariance)
        widths = np.sqrt(np.maximum(eigenvalues, 0.0))
        expanded = np.minimum(
            widths * config.width_escalation_factor,
            config.sigma_ceiling_m,
        )
        if np.any(expanded > widths):
            width_steps += 1
            covariance = eigenvectors @ np.diag(expanded ** 2) @ eigenvectors.T
            amplitude = min(
                geometry.amplitude * config.width_escalation_factor ** 2,
                config.amplitude_max,
            )
            geometry = geometry_from_covariance(
                geometry.center,
                covariance,
                amplitude,
                geometry.amplitude_depth,
                geometry.amplitude_curvature,
                config,
            )
            residual = residual_minima_count(estimate, geometry, config)

    success = residual == 0
    amplitude_at_cap = math.isclose(
        geometry.amplitude, config.amplitude_max, rel_tol=1e-12, abs_tol=1e-12
    )
    width_at_cap = math.isclose(
        geometry.sigma_major, config.sigma_ceiling_m, rel_tol=1e-12, abs_tol=1e-12
    )
    limit_reached = bool(not success and rounds >= config.maximum_design_escalations)
    provisional = FillDesign(
        geometry=geometry,
        success=success,
        residual_minima_count=residual,
        design_escalations=rounds,
        amplitude_steps=amplitude_steps,
        width_steps=width_steps,
        confidence=0.0,
        confidence_components=tuple(),
        amplitude_at_cap=amplitude_at_cap,
        width_at_cap=width_at_cap,
        escalation_limit_reached=limit_reached,
    )
    components = confidence_components(
        estimate, provisional, minimum_valid_samples, condition_limit
    )
    return replace(
        provisional,
        confidence=float(np.mean(components)),
        confidence_components=components,
    )
