"""Pure immutable revision-aware Gaussian fill registry."""

from dataclasses import dataclass, replace
import math
from typing import Dict, Iterable, Optional, Sequence, Tuple

import numpy as np

from ros_esc.gaussian_fill_node.basin_estimator import BasinSample


@dataclass(frozen=True)
class RegistryConfig:
    """Soft-association and retained-sample limits."""

    merge_bandwidth_m: float = 0.50
    merge_radius_scale: float = 2.0
    minimum_merge_probability: float = 0.60
    maximum_cluster_samples: int = 4000

    def __post_init__(self):
        if not math.isfinite(self.merge_bandwidth_m) or self.merge_bandwidth_m <= 0:
            raise ValueError("merge bandwidth must be finite and positive")
        if not math.isfinite(self.merge_radius_scale) or self.merge_radius_scale <= 0:
            raise ValueError("merge radius scale must be finite and positive")
        if not 0.0 <= self.minimum_merge_probability <= 1.0:
            raise ValueError("minimum merge probability must be in [0, 1]")
        if self.maximum_cluster_samples < 1:
            raise ValueError("maximum cluster samples must be positive")


@dataclass(frozen=True)
class FillVersion:
    """One frozen publishable fill lifecycle record."""

    fill_id: int
    cluster_id: int
    revision: int
    source_timestamp: float
    center: np.ndarray
    amplitude: float
    covariance: np.ndarray
    sigma_major: float
    sigma_minor: float
    orientation: float
    support_radius: float
    exit_radius: float
    confidence: float
    sample_count: int
    fit_residual: float
    fit_condition_number: float
    fit_condition_number_valid: bool
    design_escalations: int
    active: bool = True
    superseded: bool = False

    def __post_init__(self):
        center = np.array(self.center, dtype=np.float64, copy=True)
        covariance = np.array(self.covariance, dtype=np.float64, copy=True)
        center.setflags(write=False)
        covariance.setflags(write=False)
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "covariance", covariance)


@dataclass(frozen=True)
class ClusterRecord:
    """One active cluster plus retained sufficient sample history."""

    active_fill: FillVersion
    samples: Tuple[BasinSample, ...]


@dataclass(frozen=True)
class Association:
    """Best soft association and the mandatory hard-overlap outcome."""

    cluster_id: Optional[int]
    probability: float
    distance_m: float
    hard_radius_m: float
    merge: bool


@dataclass(frozen=True)
class RegistrySnapshot:
    """Detached, immutable inputs for a preparation worker."""

    generation: int
    next_id: int
    clusters: Tuple[ClusterRecord, ...]


@dataclass(frozen=True)
class RegistryCommitPlan:
    """Preconstructed state; staging consumes no identity or generation."""

    generation: int
    next_id: int
    clusters: Tuple[ClusterRecord, ...]
    history: Tuple[FillVersion, ...]
    superseded: Optional[FillVersion]
    active: FillVersion


def association_probabilities(candidate_center, clusters, bandwidth_m):
    """Return stable softmax association probabilities ordered by cluster ID."""

    ordered = sorted(clusters, key=lambda cluster: cluster.active_fill.cluster_id)
    if not ordered:
        return tuple(), np.empty(0, dtype=np.float64)
    candidate = np.asarray(candidate_center, dtype=np.float64)
    distances_squared = np.array(
        [
            float(np.sum((candidate - cluster.active_fill.center) ** 2))
            for cluster in ordered
        ],
        dtype=np.float64,
    )
    log_scores = -distances_squared / (2.0 * float(bandwidth_m) ** 2)
    maximum = float(np.max(log_scores))
    shifted = np.exp(log_scores - maximum)
    probabilities = shifted / float(np.sum(shifted))
    return tuple(ordered), probabilities


def associate_candidate(
    candidate_center,
    candidate_sigma_major,
    clusters,
    config,
):
    """Apply stable soft association followed by the required hard overlap gate."""

    ordered, probabilities = association_probabilities(
        candidate_center, clusters, config.merge_bandwidth_m
    )
    if not ordered:
        return Association(None, 0.0, float("nan"), float("nan"), False)
    best_index = int(np.argmax(probabilities))
    cluster = ordered[best_index]
    distance = float(
        np.linalg.norm(
            np.asarray(candidate_center, dtype=np.float64)
            - cluster.active_fill.center
        )
    )
    hard_radius = config.merge_radius_scale * max(
        float(candidate_sigma_major), cluster.active_fill.sigma_major
    )
    probability = float(probabilities[best_index])
    return Association(
        cluster_id=cluster.active_fill.cluster_id,
        probability=probability,
        distance_m=distance,
        hard_radius_m=hard_radius,
        merge=bool(
            probability >= config.minimum_merge_probability
            and distance <= hard_radius
        ),
    )


def retain_cluster_samples(samples: Iterable[BasinSample], maximum):
    """De-duplicate stamps and retain deterministic evenly spaced history."""

    by_stamp = {}
    for sample in samples:
        by_stamp[float(sample.stamp_sec)] = sample
    ordered = tuple(by_stamp[stamp] for stamp in sorted(by_stamp))
    if len(ordered) <= maximum:
        return ordered
    indices = np.linspace(0, len(ordered) - 1, int(maximum))
    indices = np.rint(indices).astype(int)
    return tuple(ordered[int(index)] for index in indices)


class FillRegistry:
    """Commit-only registry retaining every frozen published revision."""

    def __init__(self, config=None):
        self.config = config or RegistryConfig()
        self._clusters: Dict[int, ClusterRecord] = {}
        self._history = []
        self._next_id = 1
        self._generation = 0

    @property
    def generation(self):
        return self._generation

    def snapshot(self):
        return RegistrySnapshot(self._generation, self._next_id, self.active_clusters)

    @property
    def active_clusters(self):
        return tuple(self._clusters[key] for key in sorted(self._clusters))

    @property
    def history(self):
        return tuple(self._history)

    @property
    def active_count(self):
        return len(self._clusters)

    def cluster(self, cluster_id):
        return self._clusters.get(int(cluster_id))

    def active_cluster_for_fill(self, fill_id):
        """Resolve any known fill version to its cluster's active record."""

        fill_id = int(fill_id)
        for cluster in self._clusters.values():
            if cluster.active_fill.fill_id == fill_id:
                return cluster
        for version in reversed(self._history):
            if version.fill_id == fill_id:
                return self._clusters.get(version.cluster_id)
        return None

    def associate_target(self, fill_id, center, sigma_major):
        """Apply the hard-overlap gate to one explicitly targeted cluster."""

        cluster = self.active_cluster_for_fill(fill_id)
        if cluster is None:
            return None
        candidate = np.asarray(center, dtype=np.float64)
        distance = float(np.linalg.norm(candidate - cluster.active_fill.center))
        hard_radius = self.config.merge_radius_scale * max(
            float(sigma_major), cluster.active_fill.sigma_major
        )
        return Association(
            cluster_id=cluster.active_fill.cluster_id,
            probability=1.0,
            distance_m=distance,
            hard_radius_m=hard_radius,
            merge=bool(distance <= hard_radius),
        )

    def associate(self, center, sigma_major):
        return associate_candidate(
            center,
            sigma_major,
            self.active_clusters,
            self.config,
        )

    def combined_samples(self, cluster_id, samples):
        cluster = self._clusters[int(cluster_id)]
        return retain_cluster_samples(
            tuple(cluster.samples) + tuple(samples),
            self.config.maximum_cluster_samples,
        )

    def commit_new(self, version_values, samples):
        """Atomically commit a new cluster whose fill and cluster IDs match."""

        return self.commit_staged(self.stage_commit(version_values, samples))

    def commit_revision(self, cluster_id, version_values, samples):
        """Atomically supersede one active version and commit its replacement."""

        return self.commit_staged(self.stage_commit(version_values, samples, cluster_id=cluster_id))

    def stage_commit(self, version_values, samples, *, cluster_id=None,
                     expected_generation=None, exact_target=None, strict=False):
        """Construct every potentially failing value before changing the registry.

        Legacy callers keep their existing sample-retention policy. V2 callers
        supply prevalidated support and refuse conflict/decimation instead.
        """
        if expected_generation is not None and expected_generation != self._generation:
            raise ValueError("registry generation changed")
        old = None if cluster_id is None else self._clusters[int(cluster_id)].active_fill
        if exact_target is not None and (old is None or exact_target != (
                old.fill_id, old.cluster_id, old.revision)):
            raise ValueError("active target revision changed")
        identity = self._next_id
        active = FillVersion(fill_id=identity, cluster_id=identity if old is None else old.cluster_id,
                             revision=1 if old is None else old.revision+1, **version_values)
        source = tuple(samples)
        if strict:
            required = [*active.center, active.amplitude, *active.covariance.reshape(-1),
                        active.sigma_major, active.sigma_minor, active.support_radius,
                        active.exit_radius, active.confidence, active.fit_residual]
            if (active.center.shape != (2,) or active.covariance.shape != (2, 2)
                    or not all(math.isfinite(float(v)) for v in required)
                    or active.amplitude < 0 or min(active.sigma_major, active.sigma_minor,
                                                  active.support_radius, active.exit_radius) <= 0
                    or not np.allclose(active.covariance, active.covariance.T, rtol=0, atol=1e-12)
                    or np.min(np.linalg.eigvalsh(active.covariance)) <= 0
                    or (active.fit_condition_number_valid and not math.isfinite(active.fit_condition_number))):
                raise ValueError("invalid prepared fill geometry")
            if not source or len(source) > self.config.maximum_cluster_samples:
                raise ValueError("prepared support capacity")
            stamps = [sample.stamp_sec for sample in source]
            if any(not math.isfinite(stamp) for stamp in stamps) or any(
                    right <= left for left, right in zip(stamps, stamps[1:])):
                raise ValueError("prepared support order or conflict")
            retained = source
        else:
            retained = retain_cluster_samples(source, self.config.maximum_cluster_samples)
        superseded = None if old is None else replace(old, active=False, superseded=True)
        clusters = dict(self._clusters)
        clusters[active.cluster_id] = ClusterRecord(active, retained)
        history = tuple(self._history) + (() if superseded is None else (superseded,)) + (active,)
        return RegistryCommitPlan(self._generation, self._next_id,
                                  tuple(clusters[key] for key in sorted(clusters)), history,
                                  superseded, active)

    def commit_staged(self, plan):
        """Serialized linearization point; stale plans never consume an ID."""
        if plan.generation != self._generation or plan.next_id != self._next_id:
            raise ValueError("staged registry generation changed")
        # Construct containers before mutation as well. No callback or yield is
        # possible inside the owner callback's following assignments.
        clusters = {cluster.active_fill.cluster_id: cluster for cluster in plan.clusters}
        history = list(plan.history)
        self._clusters, self._history = clusters, history
        self._next_id += 1
        self._generation += 1
        return plan.superseded, plan.active


def active_fill_value(point, versions: Sequence[FillVersion]):
    """Evaluate only the newest active version of every cluster."""

    active = {}
    for version in versions:
        current = active.get(version.cluster_id)
        if version.superseded or not version.active:
            if current is not None and current.fill_id == version.fill_id:
                del active[version.cluster_id]
            continue
        if current is None or version.revision > current.revision:
            active[version.cluster_id] = version
    point = np.asarray(point, dtype=np.float64)
    total = 0.0
    for version in active.values():
        delta = point - version.center
        inverse = np.linalg.inv(version.covariance)
        total += version.amplitude * math.exp(-0.5 * float(delta.T @ inverse @ delta))
    return float(total)
