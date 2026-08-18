"""Pure robust sample synchronization and basin estimation helpers."""

from bisect import bisect_left
from dataclasses import dataclass
import math
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class PoseSnapshot:
    """One stamped planar pose awaiting cost synchronization."""

    stamp_sec: float
    x: float
    y: float
    yaw: float
    valid: bool = True


@dataclass(frozen=True)
class CostSnapshot:
    """One stamped source-cost sample awaiting pose synchronization."""

    stamp_sec: float
    raw_sensor_value: float
    raw_sensor_valid: bool
    raw_cost: float
    source_score: float
    source_score_valid: bool
    algorithm_state: int
    algorithm_state_valid: bool


@dataclass(frozen=True)
class BasinSample:
    """One immutable synchronized estimator sample."""

    stamp_sec: float
    x: float
    y: float
    yaw: float
    raw_sensor_value: float
    raw_sensor_valid: bool
    raw_cost: float
    source_score: float
    source_score_valid: bool
    algorithm_state: int


@dataclass(frozen=True)
class EstimatorConfig:
    """Configuration for robust sample filtering and basin estimation."""

    sample_sync_tolerance_sec: float = 0.05
    maximum_position_speed_mps: float = 0.20
    outlier_mad_threshold: float = 3.5
    position_increment_mad_floor_m: float = 1e-4
    estimation_window_sec: float = 8.0
    minimum_valid_samples: int = 40
    maximum_sample_age_sec: float = 12.0
    mean_shift_iterations: int = 5
    center_tolerance_m: float = 0.005
    position_kernel_bandwidth_m: float = 0.25
    cost_temperature_normalized: float = 0.05
    covariance_eigenvalue_min_m2: float = 0.0025
    covariance_eigenvalue_max_m2: float = 0.25
    quadratic_ridge_lambda: float = 1e-6
    quadratic_condition_number_max: float = 1e8
    center_cost_percentile: float = 10.0
    shoulder_cost_percentile: float = 80.0
    inner_mahalanobis_radius: float = 1.0
    minimum_basin_depth: float = 0.02

    def __post_init__(self):
        positive = (
            self.sample_sync_tolerance_sec,
            self.maximum_position_speed_mps,
            self.estimation_window_sec,
            self.maximum_sample_age_sec,
            self.position_kernel_bandwidth_m,
            self.cost_temperature_normalized,
            self.covariance_eigenvalue_min_m2,
            self.covariance_eigenvalue_max_m2,
            self.quadratic_condition_number_max,
            self.minimum_basin_depth,
        )
        if not all(math.isfinite(value) and value > 0.0 for value in positive):
            raise ValueError("estimator scales and limits must be finite and positive")
        if self.covariance_eigenvalue_max_m2 < self.covariance_eigenvalue_min_m2:
            raise ValueError("maximum covariance eigenvalue must not be below minimum")
        if self.minimum_valid_samples < 1 or self.mean_shift_iterations < 1:
            raise ValueError("sample and iteration counts must be positive")
        if not math.isfinite(self.outlier_mad_threshold) or self.outlier_mad_threshold <= 0:
            raise ValueError("outlier MAD threshold must be finite and positive")
        if (
            not math.isfinite(self.position_increment_mad_floor_m)
            or self.position_increment_mad_floor_m < 0.0
        ):
            raise ValueError(
                "position increment MAD floor must be finite and nonnegative"
            )


@dataclass(frozen=True)
class FilteredWindow:
    """Frozen inlier samples and finite rejection accounting."""

    samples: Tuple[BasinSample, ...]
    input_count: int
    rejected: Dict[str, int]

    @property
    def valid_count(self):
        return len(self.samples)


@dataclass(frozen=True)
class QuadraticFit:
    """Weighted local quadratic model and its validation diagnostics."""

    intercept: float
    gradient: np.ndarray
    hessian: np.ndarray
    positive_hessian: np.ndarray
    residual_rms: float
    condition_number: float
    rank: int
    valid: bool
    predictor_valid: bool


@dataclass(frozen=True)
class BasinEstimate:
    """Complete robust basin estimate consumed by the fill designer."""

    center: np.ndarray
    weights: np.ndarray
    sample_covariance: np.ndarray
    quadratic: QuadraticFit
    center_cost: float
    shoulder_cost: float
    depth: float
    shoulder_fallback: bool
    sample_count: int
    angular_coverage: float
    spatial_coverage: float
    samples: Tuple[BasinSample, ...]


def synchronize_samples(
    poses: Sequence[PoseSnapshot],
    costs: Sequence[CostSnapshot],
    tolerance_sec: float,
) -> Tuple[Tuple[BasinSample, ...], int]:
    """Pair each cost once with the closest unused pose within tolerance."""

    if not math.isfinite(tolerance_sec) or tolerance_sec < 0.0:
        raise ValueError("synchronization tolerance must be finite and nonnegative")
    active_poses = sorted(
        (float(pose.stamp_sec), index)
        for index, pose in enumerate(poses)
        if math.isfinite(float(pose.stamp_sec))
    )
    invalid_pose_count = len(poses) - len(active_poses)
    synchronized = []
    unmatched = 0
    for cost in costs:
        cost_stamp = float(cost.stamp_sec)
        if not math.isfinite(cost_stamp) or not active_poses:
            unmatched += 1
            continue

        insertion = bisect_left(active_poses, (cost_stamp, -1))
        candidate_positions = []
        if insertion > 0:
            predecessor_stamp = active_poses[insertion - 1][0]
            candidate_positions.append(
                bisect_left(active_poses, (predecessor_stamp, -1))
            )
        if insertion < len(active_poses):
            successor_stamp = active_poses[insertion][0]
            candidate_positions.append(
                bisect_left(active_poses, (successor_stamp, -1))
            )
        selected_position = min(
            candidate_positions,
            key=lambda position: (
                abs(active_poses[position][0] - cost_stamp),
                active_poses[position][0],
                active_poses[position][1],
            ),
        )
        pose_stamp, pose_index = active_poses[selected_position]
        pose = poses[pose_index]
        if abs(pose_stamp - cost_stamp) > tolerance_sec:
            unmatched += 1
            continue
        active_poses.pop(selected_position)
        synchronized.append(
            BasinSample(
                stamp_sec=cost_stamp,
                x=float(pose.x) if pose.valid else float("nan"),
                y=float(pose.y) if pose.valid else float("nan"),
                yaw=float(pose.yaw) if pose.valid else float("nan"),
                raw_sensor_value=float(cost.raw_sensor_value),
                raw_sensor_valid=bool(cost.raw_sensor_valid),
                raw_cost=float(cost.raw_cost),
                source_score=float(cost.source_score),
                source_score_valid=bool(cost.source_score_valid),
                algorithm_state=(
                    int(cost.algorithm_state) if cost.algorithm_state_valid else 0
                ),
            )
        )
    return (
        tuple(synchronized),
        unmatched + len(active_poses) + invalid_pose_count,
    )


def _modified_z_scores(values, scale_floor=0.0):
    values = np.asarray(values, dtype=np.float64)
    scale_floor = float(scale_floor)
    if not math.isfinite(scale_floor) or scale_floor < 0.0:
        raise ValueError(
            "modified z-score scale floor must be finite and nonnegative"
        )
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    scale = max(mad, scale_floor)
    if scale <= np.finfo(np.float64).eps:
        return np.zeros(values.shape, dtype=np.float64)
    return 0.67448975 * np.abs(values - median) / scale


def freeze_sample_window(
    samples: Iterable[BasinSample],
    request_ros_time: float,
    config: EstimatorConfig,
) -> FilteredWindow:
    """Freeze one time-bounded window and reject invalid/jump/MAD samples."""

    request_ros_time = float(request_ros_time)
    if not math.isfinite(request_ros_time):
        raise ValueError("request ROS time must be finite")
    source = tuple(samples)
    rejected = {
        "outside_window": 0,
        "invalid": 0,
        "timestamp": 0,
        "speed_jump": 0,
        "cost_mad": 0,
        "position_increment_mad": 0,
    }
    preliminary = []
    previous_stamp = None
    previous_position = None
    lower = request_ros_time - config.estimation_window_sec
    age_lower = request_ros_time - config.maximum_sample_age_sec
    for sample in source:
        stamp = float(sample.stamp_sec)
        if not math.isfinite(stamp) or stamp < lower or stamp < age_lower or stamp > request_ros_time:
            rejected["outside_window"] += 1
            continue
        finite = np.array(
            [sample.x, sample.y, sample.yaw, sample.raw_cost], dtype=np.float64
        )
        if not np.all(np.isfinite(finite)) or int(sample.algorithm_state) <= 0:
            rejected["invalid"] += 1
            continue
        if previous_stamp is not None and stamp <= previous_stamp:
            rejected["timestamp"] += 1
            continue
        position = np.array([sample.x, sample.y], dtype=np.float64)
        if previous_stamp is not None:
            dt = stamp - previous_stamp
            distance = float(np.linalg.norm(position - previous_position))
            if distance > config.maximum_position_speed_mps * dt + 1e-12:
                rejected["speed_jump"] += 1
                continue
        preliminary.append(sample)
        previous_stamp = stamp
        previous_position = position

    if not preliminary:
        return FilteredWindow(tuple(), len(source), rejected)

    costs = np.array([sample.raw_cost for sample in preliminary], dtype=np.float64)
    cost_outlier = _modified_z_scores(costs) > config.outlier_mad_threshold
    increment_outlier = np.zeros(len(preliminary), dtype=bool)
    if len(preliminary) > 1:
        positions = np.array([[sample.x, sample.y] for sample in preliminary])
        increments = np.linalg.norm(np.diff(positions, axis=0), axis=1)
        # Stationary wheel odometry can alternate by encoder-scale increments
        # while its numeric MAD is near zero. Floor only the MAD denominator;
        # the absolute speed-jump gate above remains unchanged.
        increment_outlier[1:] = (
            _modified_z_scores(
                increments,
                scale_floor=config.position_increment_mad_floor_m,
            )
            > config.outlier_mad_threshold
        )

    kept = []
    for index, sample in enumerate(preliminary):
        if cost_outlier[index]:
            rejected["cost_mad"] += 1
            continue
        if increment_outlier[index]:
            rejected["position_increment_mad"] += 1
            continue
        kept.append(sample)
    return FilteredWindow(tuple(kept), len(source), rejected)


def normalized_kernel_weights(
    positions,
    center,
    normalized_costs,
    position_bandwidth_m,
    cost_temperature,
):
    """Return log-sum-exp-normalized spatial/cost kernel weights."""

    positions = np.asarray(positions, dtype=np.float64)
    center = np.asarray(center, dtype=np.float64)
    normalized_costs = np.asarray(normalized_costs, dtype=np.float64)
    if positions.ndim != 2 or positions.shape[1] != 2:
        raise ValueError("positions must have shape (N, 2)")
    if normalized_costs.shape != (positions.shape[0],):
        raise ValueError("normalized costs must match positions")
    if positions.shape[0] == 0:
        raise ValueError("at least one position is required")
    log_weights = -np.sum((positions - center) ** 2, axis=1) / (
        2.0 * float(position_bandwidth_m) ** 2
    ) - normalized_costs / float(cost_temperature)
    maximum = float(np.max(log_weights))
    shifted = np.exp(log_weights - maximum)
    total = float(np.sum(shifted))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("kernel weights could not be normalized")
    return shifted / total


def weighted_covariance(positions, center, weights):
    """Compute a symmetric weighted planar covariance."""

    positions = np.asarray(positions, dtype=np.float64)
    center = np.asarray(center, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    delta = positions - center
    covariance = (delta * weights[:, None]).T @ delta
    return 0.5 * (covariance + covariance.T)


def clip_covariance(covariance, minimum, maximum):
    """Clip covariance eigenvalues and reconstruct a symmetric matrix."""

    covariance = 0.5 * (
        np.asarray(covariance, dtype=np.float64)
        + np.asarray(covariance, dtype=np.float64).T
    )
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    eigenvalues = np.clip(eigenvalues, float(minimum), float(maximum))
    clipped = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
    return 0.5 * (clipped + clipped.T)


def weighted_percentile(values, weights, percentile):
    """Return a deterministic weighted percentile using the empirical CDF."""

    values = np.asarray(values, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ordered_values = values[order]
    ordered_weights = weights[order]
    cumulative = np.cumsum(ordered_weights)
    threshold = float(percentile) / 100.0 * float(cumulative[-1])
    index = int(np.searchsorted(cumulative, threshold, side="left"))
    return float(ordered_values[min(index, ordered_values.size - 1)])


def fit_local_quadratic(positions, costs, center, weights, config):
    """Fit the specified regularized local quadratic model."""

    positions = np.asarray(positions, dtype=np.float64)
    costs = np.asarray(costs, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    delta = positions - np.asarray(center, dtype=np.float64)
    design = np.column_stack(
        (
            np.ones(delta.shape[0]),
            delta[:, 0],
            delta[:, 1],
            0.5 * delta[:, 0] ** 2,
            delta[:, 0] * delta[:, 1],
            0.5 * delta[:, 1] ** 2,
        )
    )
    root_weights = np.sqrt(np.maximum(weights, 0.0))
    weighted_design = design * root_weights[:, None]
    weighted_costs = costs * root_weights
    rank = int(np.linalg.matrix_rank(weighted_design))
    try:
        condition = float(np.linalg.cond(weighted_design))
    except np.linalg.LinAlgError:
        condition = float("inf")
    ridge = np.diag([0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    normal = weighted_design.T @ weighted_design + config.quadratic_ridge_lambda * ridge
    rhs = weighted_design.T @ weighted_costs
    try:
        coefficients = np.linalg.solve(normal, rhs)
    except np.linalg.LinAlgError:
        coefficients = np.linalg.pinv(normal) @ rhs
    predictor_valid = bool(np.all(np.isfinite(coefficients)))
    if not predictor_valid:
        coefficients = np.array(
            [weighted_percentile(costs, weights, 10.0), 0, 0, 0, 0, 0],
            dtype=np.float64,
        )
    predicted = design @ coefficients
    residual = float(np.sqrt(np.sum(weights * (predicted - costs) ** 2)))
    hessian = np.array(
        [
            [coefficients[3], coefficients[4]],
            [coefficients[4], coefficients[5]],
        ],
        dtype=np.float64,
    )
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    positive = eigenvectors @ np.diag(np.maximum(eigenvalues, 0.0)) @ eigenvectors.T
    valid = bool(
        predictor_valid
        and rank >= 6
        and math.isfinite(condition)
        and condition <= config.quadratic_condition_number_max
    )
    return QuadraticFit(
        intercept=float(coefficients[0]),
        gradient=np.array(coefficients[1:3], dtype=np.float64),
        hessian=hessian,
        positive_hessian=0.5 * (positive + positive.T),
        residual_rms=residual,
        condition_number=condition,
        rank=rank,
        valid=valid,
        predictor_valid=predictor_valid,
    )


def estimate_basin(samples: Sequence[BasinSample], config: EstimatorConfig):
    """Estimate basin center, covariance, quadratic shape, depth, and coverage."""

    samples = tuple(samples)
    if len(samples) < config.minimum_valid_samples:
        raise ValueError(
            f"minimum valid samples not met: {len(samples)} < {config.minimum_valid_samples}"
        )
    positions = np.array([[sample.x, sample.y] for sample in samples], dtype=np.float64)
    costs = np.array([sample.raw_cost for sample in samples], dtype=np.float64)
    minimum_cost = float(np.min(costs))
    span = max(float(np.percentile(costs, 90.0)) - minimum_cost, 1e-12)
    normalized_costs = np.clip((costs - minimum_cost) / span, 0.0, 1.0)
    center = np.array(positions[int(np.argmin(costs))], dtype=np.float64)
    for _ in range(config.mean_shift_iterations):
        weights = normalized_kernel_weights(
            positions,
            center,
            normalized_costs,
            config.position_kernel_bandwidth_m,
            config.cost_temperature_normalized,
        )
        updated = np.sum(positions * weights[:, None], axis=0)
        shift = float(np.linalg.norm(updated - center))
        center = updated
        if shift < config.center_tolerance_m:
            break
    weights = normalized_kernel_weights(
        positions,
        center,
        normalized_costs,
        config.position_kernel_bandwidth_m,
        config.cost_temperature_normalized,
    )
    covariance = clip_covariance(
        weighted_covariance(positions, center, weights),
        config.covariance_eigenvalue_min_m2,
        config.covariance_eigenvalue_max_m2,
    )
    quadratic = fit_local_quadratic(positions, costs, center, weights, config)
    inverse_covariance = np.linalg.inv(covariance)
    delta = positions - center
    mahalanobis = np.sqrt(
        np.maximum(np.einsum("ni,ij,nj->n", delta, inverse_covariance, delta), 0.0)
    )
    center_cost = weighted_percentile(costs, weights, config.center_cost_percentile)
    outside = costs[mahalanobis > config.inner_mahalanobis_radius]
    shoulder_fallback = outside.size == 0
    shoulder_values = costs if shoulder_fallback else outside
    shoulder_cost = float(np.percentile(shoulder_values, config.shoulder_cost_percentile))
    depth = max(shoulder_cost - center_cost, config.minimum_basin_depth)

    angles = np.arctan2(delta[:, 1], delta[:, 0])
    angular_bins = np.floor((angles + math.pi) / (2.0 * math.pi) * 8.0).astype(int)
    angular_bins = np.clip(angular_bins, 0, 7)
    angular_coverage = len(np.unique(angular_bins)) / 8.0
    sample_sigma_major = math.sqrt(float(np.max(np.linalg.eigvalsh(covariance))))
    spatial_coverage = min(
        1.0, sample_sigma_major / config.position_kernel_bandwidth_m
    )
    return BasinEstimate(
        center=center,
        weights=weights,
        sample_covariance=covariance,
        quadratic=quadratic,
        center_cost=center_cost,
        shoulder_cost=shoulder_cost,
        depth=depth,
        shoulder_fallback=shoulder_fallback,
        sample_count=len(samples),
        angular_coverage=angular_coverage,
        spatial_coverage=spatial_coverage,
        samples=samples,
    )
