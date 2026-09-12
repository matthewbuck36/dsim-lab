"""Atomic combined-fill activation in the existing modified-cost owner."""

from copy import deepcopy
from dataclasses import dataclass
import math
import numpy as np

from ros_esc_interfaces.msg import FillResult
from ros_esc.v2_lifecycle import (
    MAX_COMMANDS, PROTOCOL_VERSION, FILL_RESULT_TOPIC, FRESHNESS_NS,
    fill_registry_digest, hash_payload,
    message_payload, result_sha256,
)
from ros_esc.v2_stream import time_to_ns


def commit_identity(result):
    """Retries can change their command/response envelope, never the commit."""
    return hash_payload(message_payload(result, exclude=(
        'stamp', 'committed_sha256', 'result', 'command_sequence')))


def fill_term(fill):
    values = (fill.center_x, fill.center_y, fill.amplitude, fill.covariance_xx,
              fill.covariance_xy, fill.covariance_yy, fill.sigma_major,
              fill.sigma_minor, fill.support_radius, fill.exit_radius)
    if (min(fill.fill_id, fill.cluster_id, fill.revision) <= 0
            or not fill.active or fill.superseded
            or not all(math.isfinite(v) for v in values)
            or not all((fill.covariance_valid, fill.principal_widths_valid,
                        fill.support_radius_valid, fill.exit_radius_valid))
            or fill.amplitude < 0 or min(values[6:]) <= 0):
        raise ValueError('invalid active fill geometry')
    covariance = np.array([[fill.covariance_xx, fill.covariance_xy],
                           [fill.covariance_xy, fill.covariance_yy]])
    if np.min(np.linalg.eigvalsh(covariance)) <= 0:
        raise ValueError('nonpositive fill covariance')
    inverse = np.linalg.inv(covariance)
    if not np.all(np.isfinite(inverse)):
        raise ValueError('invalid fill covariance inverse')
    return dict(fill_id=int(fill.fill_id), cluster_id=int(fill.cluster_id),
                revision=int(fill.revision), amplitude=float(fill.amplitude),
                center=np.array([fill.center_x, fill.center_y]), covariance=covariance,
                inverse=inverse, sigma_major=float(fill.sigma_major))


@dataclass(frozen=True)
class PendingActivation:
    result: FillResult
    identity: str
    receipt_ns: int


class AtomicFillActivation:
    def __init__(self, node):
        self.node = node
        if node.resolve_topic_name(str(node.get_parameter('v2_fill_result_topic').value)) != FILL_RESULT_TOPIC:
            raise ValueError('moving fill result topic differs from frozen contract')
        self.generation = 0
        self.commits = {}
        self.commit_receipts_ns = {}
        self.commit_stamps_ns = {}
        self.latest_commit_ns = None
        self.active = {}
        self.pending = None
        self.last_fault = ''
        self.fault_count = 0

    def _envelope(self, result):
        composer = self.node.v2_composer
        committed_ns = time_to_ns(result.committed_at)
        if (result.result not in (FillResult.ACTIVATED, FillResult.ALREADY_ACTIVATED)
                    or result.schema_version != PROTOCOL_VERSION or composer.origin_fault
                    or composer.origin_ns is None
                    or result.run_id != composer.run_id or result.stream_contract_id != composer.contract_id
                    or result.frame_id != composer.config['frame_id']
                    or time_to_ns(result.time_origin) != composer.origin_ns
                    or min(result.search_epoch, result.candidate_id, result.preparation_id,
                           result.objective_revision, result.command_sequence) <= 0
                    or result.committed_sha256 != result_sha256(result)
                    or not result.evidence_sha256 or not result.prepared_sha256
                    or not composer.origin_ns <= time_to_ns(result.prepared_at)
                        <= committed_ns <= time_to_ns(result.expires_at)):
            raise ValueError('activation envelope mismatch')
        return commit_identity(result), int(result.registry_generation), committed_ns

    def _stage(self, result, generation):
        """Validate against current state; nothing staged survives clock waiting."""
        if (generation != self.generation+1 or len(self.commits) >= MAX_COMMANDS
                or result.expected_registry_generation != self.generation
                or result.registry_digest_before != fill_registry_digest(self.active.values())):
            raise ValueError('activation generation or prior digest mismatch')
        term = fill_term(result.fill)
        if result.fill.frame_id != result.frame_id or result.fill.fill_id <= self.generation:
            raise ValueError('active fill identity mismatch')
        active, terms = dict(self.active), dict(self.node.robust_terms)
        clusters = dict(self.node.robust_cluster_fill_ids)
        affine = dict(self.node.robust_affine_terms)
        old_id = clusters.get(result.fill.cluster_id)
        if result.has_superseded_fill:
            old = result.superseded_fill
            expected = active.get(old.fill_id)
            ignored = ('stamp', 'active', 'superseded')
            if (expected is None or old.active or not old.superseded or old_id != old.fill_id
                    or old.cluster_id != result.fill.cluster_id or result.fill.revision != old.revision+1
                    or message_payload(old, exclude=ignored) != message_payload(expected, exclude=ignored)):
                raise ValueError('superseded target mismatch')
            del active[old.fill_id]
            del terms[old.fill_id]
            affine.pop(old.cluster_id, None)
        elif old_id is not None or result.fill.revision != 1 or result.fill.cluster_id != result.fill.fill_id:
            raise ValueError('new cluster identity mismatch')
        if result.fill.fill_id in active:
            raise ValueError('active fill identity reused')
        active[result.fill.fill_id] = deepcopy(result.fill)
        terms[result.fill.fill_id] = term
        clusters[result.fill.cluster_id] = result.fill.fill_id
        if result.registry_digest_after != fill_registry_digest(active.values()):
            raise ValueError('activation resulting digest mismatch')
        return active, terms, clusters, affine

    def _apply(self, staged, identity, generation, committed_ns, receipt_ns):
        active, terms, clusters, affine = staged
        commits = dict(self.commits)
        commits[generation] = identity
        receipts, stamps = dict(self.commit_receipts_ns), dict(self.commit_stamps_ns)
        receipts[generation], stamps[generation] = receipt_ns, committed_ns
        latest = committed_ns if self.latest_commit_ns is None else max(self.latest_commit_ns, committed_ns)
        # Every allocation and validation precedes this serialized swap.
        self.node.robust_terms, self.node.robust_cluster_fill_ids = terms, clusters
        self.node.robust_affine_terms = affine
        self.active, self.commits, self.generation = active, commits, generation
        self.commit_receipts_ns, self.commit_stamps_ns = receipts, stamps
        self.latest_commit_ns, self.pending = latest, None
        self.node._sync_robust_affine()
        self.last_fault = ''

    def _fault(self, error):
        self.last_fault = str(error)
        self.fault_count += 1
        self.node.v2_composer._report_fault('fill_activation_' + self.last_fault.replace(' ', '_'))

    def accept(self, result):
        if result.result not in (FillResult.ACTIVATED, FillResult.ALREADY_ACTIVATED):
            return False
        receipt_ns = self.node.get_clock().now().nanoseconds
        try:
            identity, generation, committed_ns = self._envelope(result)
            if generation in self.commits:
                if self.commits[generation] != identity:
                    raise ValueError('conflicting committed generation')
                return True
            if self.pending is not None:
                if (generation != self.pending.result.registry_generation
                        or identity != self.pending.identity):
                    raise ValueError('conflicting pending generation')
                return True  # Never replace its message or first receipt.
            if receipt_ns < 0 or committed_ns - receipt_ns > FRESHNESS_NS:
                raise ValueError('activation commit excessively future')
            staged = self._stage(result, generation)
            if committed_ns > receipt_ns:
                self.pending = PendingActivation(deepcopy(result), identity, receipt_ns)
            else:
                self._apply(staged, identity, generation, committed_ns, receipt_ns)
            self.last_fault = ''
            return True
        except (ValueError, TypeError, KeyError, OverflowError, np.linalg.LinAlgError) as exc:
            self._fault(exc)
            return False

    def poll(self, now_ns):
        """Apply covered durable authority and report whether composition is safe."""
        composer = self.node.v2_composer
        if composer.origin_fault or composer.origin_ns is None or now_ns < 0:
            return False
        pending = self.pending
        if pending is not None:
            try:
                identity, generation, committed_ns = self._envelope(pending.result)
                if identity != pending.identity:
                    raise ValueError('pending activation identity changed')
                if committed_ns <= now_ns:
                    # Intervening affine updates belong to the current state.
                    staged = self._stage(pending.result, generation)
                    self._apply(staged, identity, generation, committed_ns, pending.receipt_ns)
            except (ValueError, TypeError, KeyError, OverflowError, np.linalg.LinAlgError) as exc:
                self._fault(exc)
                return False
        # A rollback does not erase commits, but their law cannot act in its past.
        return self.latest_commit_ns is None or now_ns >= self.latest_commit_ns
