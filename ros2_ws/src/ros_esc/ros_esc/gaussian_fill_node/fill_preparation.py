"""Bounded pure preparation using the existing estimator, designer and registry."""

from dataclasses import dataclass
import math

import numpy as np

from ros_esc.gaussian_fill_node.basin_estimator import (
    BasinSample, EstimatorConfig, estimate_basin, freeze_sample_window,
)
from ros_esc.gaussian_fill_node.fill_designer import (
    FillDesignConfig, candidate_amplitude_floor, design_fill, initial_fill_geometry,
)
from ros_esc.gaussian_fill_node.fill_registry import (
    RegistryConfig, RegistrySnapshot, associate_candidate,
)


@dataclass(frozen=True)
class PreparationInput:
    samples: tuple[BasinSample, ...]
    registry: RegistrySnapshot
    estimator: EstimatorConfig
    designer: FillDesignConfig
    association: RegistryConfig
    source_timestamp: float
    candidate_lower: float
    amplitude_scale: float
    candidate_informed: bool
    maximum_fills: int
    target: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class PreparedProposal:
    """No allocated identity, mutable array, ROS handle or registry reference."""

    version_values: tuple
    samples: tuple[BasinSample, ...]
    cluster_id: int | None
    exact_target: tuple[int, int, int] | None
    registry_generation: int
    input_count: int
    rejection_counts: tuple


def sample_payload(sample):
    """Comparable support identity, with unavailable optional values explicit."""
    return tuple((name, value if not isinstance(value, float) or math.isfinite(value) else None)
                 for name, value in vars(sample).items())


def validate_samples(samples, maximum=4000):
    samples = tuple(samples)
    if not samples or len(samples) > maximum:
        raise ValueError("snapshot sample capacity")
    last = None
    for sample in samples:
        if (not all(math.isfinite(float(v)) for v in
                    (sample.stamp_sec, sample.x, sample.y, sample.yaw, sample.raw_cost))
                or sample.algorithm_state <= 0 or (last is not None and sample.stamp_sec <= last)):
            raise ValueError("invalid or conflicting snapshot sample order")
        last = sample.stamp_sec
    return samples


def combine_samples(old, new, maximum):
    """Merge two validated streams without overwriting conflicts or decimation."""
    old, new = validate_samples(old, maximum), validate_samples(new, maximum)
    by_stamp = {sample.stamp_sec: sample for sample in old}
    for sample in new:
        previous = by_stamp.get(sample.stamp_sec)
        if previous is not None and sample_payload(previous) != sample_payload(sample):
            raise ValueError("retained/current support conflict")
        by_stamp[sample.stamp_sec] = sample
    if len(by_stamp) > maximum:
        raise ValueError("merged support capacity")
    return tuple(by_stamp[stamp] for stamp in sorted(by_stamp))


def compute_fill_proposal(inp: PreparationInput) -> PreparedProposal:
    """Calculate one finite proposal. A caller may discard its eventual result."""
    maximum = min(4000, inp.association.maximum_cluster_samples)
    source = validate_samples(inp.samples, maximum)
    target_cluster = None
    if inp.target is not None:
        target_cluster = next((cluster for cluster in inp.registry.clusters
                               if (cluster.active_fill.fill_id, cluster.active_fill.cluster_id,
                                   cluster.active_fill.revision) == inp.target), None)
        if target_cluster is None:
            raise ValueError("exact redesign target is not active")
    # Keep the existing speed/MAD rules, but select the frozen support bounds;
    # a new request-ending eight-second window must not replace these cycles.
    window = freeze_sample_window(source, source[-1].stamp_sec, inp.estimator,
                                  snapshot_bounds=(source[0].stamp_sec, source[-1].stamp_sec))
    if window.valid_count < inp.estimator.minimum_valid_samples:
        raise ValueError("insufficient valid immutable support")
    floor = (candidate_amplitude_floor(inp.candidate_lower, inp.amplitude_scale,
                                      inp.designer.amplitude_max).applied
             if inp.candidate_informed else 0.)
    estimate = estimate_basin(window.samples, inp.estimator)
    geometry = initial_fill_geometry(estimate, inp.designer, minimum_amplitude=floor)
    if target_cluster is None:
        association = associate_candidate(estimate.center, geometry.sigma_major,
                                          inp.registry.clusters, inp.association)
        cluster = (next(c for c in inp.registry.clusters
                        if c.active_fill.cluster_id == association.cluster_id)
                   if association.merge else None)
    else:
        cluster = target_cluster
        distance = float(np.linalg.norm(estimate.center-cluster.active_fill.center))
        radius = inp.association.merge_radius_scale * max(geometry.sigma_major,
                                                         cluster.active_fill.sigma_major)
        if distance > radius:
            raise ValueError("redesign estimate outside target overlap")
    if cluster is None and inp.maximum_fills > 0 and len(inp.registry.clusters) >= inp.maximum_fills:
        raise ValueError("maximum active fill count")
    samples = window.samples
    if cluster is not None:
        samples = combine_samples(cluster.samples, samples, maximum)
        estimate = estimate_basin(samples, inp.estimator)
    design = design_fill(estimate, inp.designer,
                         minimum_valid_samples=inp.estimator.minimum_valid_samples,
                         condition_limit=inp.estimator.quadratic_condition_number_max,
                         minimum_amplitude=floor)
    if not design.success:
        raise ValueError("residual fitted minimum after bounded escalation")
    geom, quadratic = design.geometry, estimate.quadratic
    values = dict(
        source_timestamp=float(inp.source_timestamp), center=tuple(float(v) for v in geom.center),
        amplitude=float(geom.amplitude), covariance=tuple(tuple(float(v) for v in row) for row in geom.covariance),
        sigma_major=float(geom.sigma_major), sigma_minor=float(geom.sigma_minor),
        orientation=float(geom.orientation), support_radius=float(geom.support_radius),
        exit_radius=float(geom.exit_radius), confidence=float(design.confidence),
        sample_count=int(estimate.sample_count), fit_residual=float(quadratic.residual_rms),
        fit_condition_number=float(quadratic.condition_number),
        fit_condition_number_valid=math.isfinite(quadratic.condition_number),
        design_escalations=int(design.design_escalations),
    )
    target = None if cluster is None else (cluster.active_fill.fill_id,
                                           cluster.active_fill.cluster_id, cluster.active_fill.revision)
    return PreparedProposal(tuple(values.items()), tuple(samples),
                            None if cluster is None else cluster.active_fill.cluster_id,
                            target, inp.registry.generation, len(source), tuple(sorted(window.rejected.items())))
