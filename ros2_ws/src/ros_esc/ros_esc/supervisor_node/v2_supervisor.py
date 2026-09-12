"""Typed moving-verification adapter owned by the existing supervisor node.

Registry facts are accounted independently of the motion state. An immutable
accepted result may arrive after cancellation; it cannot re-enter escape.
"""
from copy import deepcopy
from dataclasses import dataclass, replace
import json
import math
import time

from builtin_interfaces.msg import Time
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import (CandidateSnapshot, DetectorConfirmation,
    FillCommand, FillResult, GescDirectionDiagnostics, ObjectiveCostSample,
    SearchEpochContext, SourceSampleProvenance, Timekeeper)
from ros_esc.v2_lifecycle import (DETECTOR_CONFIRMATION_TOPIC, FILL_COMMAND_TOPIC,
    FILL_RESULT_TOPIC, SEARCH_EPOCH_TOPIC, FRESHNESS_NS, MAX_COMMANDS,
    clone_ros_message, copy_envelope, envelope_identity, fill_registry_digest, hash_payload,
    message_payload, observation_payload, result_sha256, snapshot_sha256)
from ros_esc.v2_stream import relative_stamp_ns, set_time, stream_contract_id, time_to_ns
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence
from ros_esc.supervisor_node.state_machine import COUNTED_CANDIDATES, State
from ros_esc.convergence_detector_node.centroid_contract import CENTROID_METRIC_MODES
from ros_esc.supervisor_node.centered_verification import (
    ADMISSION_DETAIL, ADMISSION_EVENT, ADMISSION_RADIUS_M, APPROACH_NS,
    CENTERED_MODE, COLLECTION_NS, GUIDANCE_TOPIC, LEGACY_MODE, MODES, TOTAL_NS,
    tracking_command, tracking_controller)


def stamp(ns):
    return set_time(Time(), int(ns))


@dataclass
class Candidate:
    candidate_id: int
    confirmation: object
    accepted_ns: int
    deadline_ns: int
    snapshot: object = None
    evidence: object = None
    cancelled: bool = False
    reason: str = ''
    last_evidence_detail: str = ''
    collection_admitted_ns: object = None
    recurrent_diagnostic: object = None
    nomination_sha256: str = ''


@dataclass
class Preparation:
    command: object
    candidate: Candidate
    sequences: dict
    prepared: object = None
    activated: object = None
    cancelled: bool = False
    terminal: bool = False


class MovingSupervisor:
    def __init__(self, node, config, radius, epsilon):
        if not all(math.isfinite(v) and v > 0 for v in (radius, epsilon)):
            raise ValueError('rolling_gesc_v2 requires explicit positive finite v2_candidate_radius_m and v2_candidate_epsilon_m')
        if node.machine.config.extremum_classification_mode != COUNTED_CANDIDATES:
            raise ValueError('moving verification requires counted_candidates')
        self.node, self.config = node, config
        self.verification_mode = (str(node.get_parameter('v2_verification_motion_mode').value)
                                  if hasattr(node, 'get_parameter') else LEGACY_MODE)
        if self.verification_mode not in MODES:
            raise ValueError('unsupported v2_verification_motion_mode')
        self.centered = self.verification_mode == CENTERED_MODE
        self.tracking_control = None
        self.guidance_publisher = None
        self.guidance_sequence = 0
        if self.centered:
            from ros_esc_interfaces.msg import VerificationGuidance
            self.tracking_control = tracking_controller(str(node.get_parameter(
                'v2_verification_controller_config_filepath').value))
            self.guidance_publisher = node.create_publisher(VerificationGuidance, GUIDANCE_TOPIC, 20)
        self.metric_mode = (str(node.get_parameter('convergence_metric_mode').value)
                            if hasattr(node, 'get_parameter') else None)
        if self.metric_mode is not None and self.metric_mode not in (
                'pde_mean_v1', *CENTROID_METRIC_MODES, 'recurrent_geometry_v3'):
            raise ValueError('unsupported convergence_metric_mode')
        self.evidence_policy = getattr(node.machine.config, 'verification_evidence_policy',
                                       'angular_profiles_v1')
        if self.evidence_policy not in ('angular_profiles_v1', 'recurrent_trapping_v1'):
            raise ValueError('unsupported v2_verification_evidence_policy')
        self.recurrent_trapping = self.evidence_policy == 'recurrent_trapping_v1'
        if self.recurrent_trapping and (not self.centered or self.metric_mode != 'recurrent_geometry_v3'):
            raise ValueError('recurrent trapping requires recurrent geometry and centered moving verification')
        self.radius, self.epsilon = radius, epsilon
        self.origin = None
        self.contract = None
        self.epoch = 1
        self.started = self.now()
        self.context_sequence = 0
        self.contexts = {}
        self.pending_nominations = {}
        self.nomination_tombstones = set()
        self.nomination_fault = False
        self.nomination_not_before_ns = self.started
        self.raw = MovingRawEvidence()
        self.raw.start_epoch(self.epoch, self.started)
        self.candidate = None
        self.candidate_sequence = 0
        self.command_sequence = 0
        self.preparation_sequence = 0
        self.preparations = {}
        self.current_preparation = None
        self.accepted_epoch = None
        self.pose = None
        self.pose_fingerprint = None
        self.pending_poses = []
        self.pose_tombstones = set()
        self.pose_capacity_exhausted = False
        self.pose_keys = {}
        self.ready_required = bool(node.get_parameter("recording_ready_required").value) if hasattr(node, "get_parameter") else bool(getattr(node, "recording_ready_required", False))
        self.ready_stale_ns = round(float(node.get_parameter("recording_ready_stale_sec").value) * 1e9) if hasattr(node, "get_parameter") else FRESHNESS_NS
        if self.ready_stale_ns <= 0:
            raise ValueError("recording_ready_stale_sec must be positive")
        self.recording_ready = False
        self.ready_receipt = None
        self.first_filter_metadata = {}
        self.objective_ack = None
        self.direction_ack = None
        self.generation = 0
        self.registry_digest = fill_registry_digest([])
        self.active_fills = {}
        self.commit_keys = {}
        self.fill_candidates = {}
        self.published_snapshots = {}
        self.search_weights = (1., 1., 0.)
        self.origin_fault = False
        self.last_reason = ''
        self.epoch_publisher = node.create_publisher(SearchEpochContext, SEARCH_EPOCH_TOPIC, 10)
        if self.recurrent_trapping:
            from ros_esc_interfaces.msg import RecurrentCandidateSnapshot, RecurrentFillCommand
            from ros_esc.v2_lifecycle import RECURRENT_CANDIDATE_SNAPSHOT_TOPIC, RECURRENT_FILL_COMMAND_TOPIC
            self.command_publisher = node.create_publisher(RecurrentFillCommand, RECURRENT_FILL_COMMAND_TOPIC, 10)
            self.snapshot_publisher = node.create_publisher(RecurrentCandidateSnapshot, RECURRENT_CANDIDATE_SNAPSHOT_TOPIC, 10)
        else:
            self.command_publisher = node.create_publisher(FillCommand, FILL_COMMAND_TOPIC, 10)
            self.snapshot_publisher = node.create_publisher(CandidateSnapshot, "/gesc_gaussian/v2/candidate_snapshots", 10)
        self.subscriptions = [
            node.create_subscription(Bool, node.get_parameter("recording_ready_topic").value if hasattr(node, "get_parameter") else "/gesc_gaussian/recording_ready", self.readiness, 10),
            node.create_subscription(Timekeeper, config['timekeeper_topic'], self.timekeeper, 10),
            node.create_subscription(DetectorConfirmation, DETECTOR_CONFIRMATION_TOPIC, self.confirmation, 10),
            node.create_subscription(GescDirectionDiagnostics, node.get_parameter('v2_direction_diagnostics_topic').value if hasattr(node, 'get_parameter') else '/gesc_gaussian/v2/direction_diagnostics', self.direction, 100),
            node.create_subscription(ObjectiveCostSample, config['objective_cost_topic'], self.objective, 100),
            node.create_subscription(SourceSampleProvenance, config['provenance_topic'], self.provenance, 100),
            node.create_subscription(FillResult, FILL_RESULT_TOPIC, self.result, 10),
        ]
        if self.recurrent_trapping:
            from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
            from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_TOPIC
            self.subscriptions.append(node.create_subscription(
                RecurrentConvergenceDiagnostics, RECURRENT_TOPIC, self.recurrent_diagnostic, 20))

    def now(self):
        return int(self.node.get_clock().now().nanoseconds)

    def fresh(self, source, receipt, *, steady=None):
        now = self.now()
        return (0 <= now - source <= FRESHNESS_NS and 0 <= now - receipt <= FRESHNESS_NS
                and (steady is None or 0 <= time.monotonic_ns() - steady <= FRESHNESS_NS))

    def ready(self):
        return bool(not self.ready_required or (self.recording_ready and self.ready_receipt is not None
                    and 0 <= time.monotonic_ns() - self.ready_receipt <= self.ready_stale_ns))

    def readiness(self, msg):
        if not self.ready_required:
            return
        was_ready = self.ready()
        self.recording_ready = bool(msg.data)
        self.ready_receipt = time.monotonic_ns()
        if not self.recording_ready:
            self.cancel("recording_not_ready")
            self.raw.reset("recording_not_ready")
            self._reset_nomination_wait()
        elif not was_ready:
            self.raw.reset("recording_readiness_started")
            self._reset_nomination_wait()

    def identity(self, msg, *, lifecycle=False):
        try:
            return (self.origin is not None and not self.origin_fault
                    and msg.schema_version == (1 if lifecycle else self.config['schema_version'])
                    and msg.run_id == self.node.run_id and msg.stream_contract_id == self.contract
                    and time_to_ns(msg.time_origin) == self.origin and msg.frame_id == self.config['frame_id'])
        except (ValueError, TypeError):
            return False

    def timekeeper(self, msg):
        if self.origin_fault:
            return
        try:
            if msg.mode != 'sim time':
                raise ValueError('invalid timekeeping mode')
            value = relative_stamp_ns(0, msg.start_time)
            contract = stream_contract_id(self.config, value)
            if self.origin is not None and self.origin != value:
                raise ValueError('changed time origin')
        except (ValueError, TypeError, OverflowError):
            self.origin_fault = True
            self.cancel('changed_or_invalid_time_origin')
            self.raw.reset('changed_or_invalid_time_origin')
            return
        if self.origin is None:
            self.origin = value
            self.contract = contract
            if self.started < value:
                self.started = value
                self.raw.epoch = None  # no valid context was published yet
                self.raw.start_epoch(self.epoch, self.started)
                self.contexts.clear()

    def publish_context(self):
        self.context_sequence += 1
        msg = SearchEpochContext()
        msg.schema_version = 1
        msg.stamp = stamp(self.now())
        msg.time_origin = stamp(self.origin or 0)
        msg.run_id = self.node.run_id
        msg.stream_contract_id = self.contract or ''
        msg.frame_id = self.config['frame_id']
        msg.search_epoch = self.epoch
        msg.context_sequence = self.context_sequence
        msg.started_at = stamp(self.started)
        msg.algorithm_state = int(self.node.machine.state)
        msg.valid = (self.origin is not None and not self.origin_fault and self.ready()
                     and self.now() >= self.started)
        self.contexts[self.context_sequence] = (self.now(), msg.algorithm_state, msg.valid)
        self.contexts = {k: v for k, v in self.contexts.items() if self.now() - v[0] <= FRESHNESS_NS}
        self.epoch_publisher.publish(msg)

    def add_pose(self, msg):
        now, steady = self.now(), time.monotonic_ns()
        try:
            source = time_to_ns(msg.header.stamp)
            xy = (float(msg.pose.pose.position.x), float(msg.pose.pose.position.y))
            fingerprint = hash_payload(message_payload(msg.pose))
            if msg.header.frame_id != self.config['frame_id'] or not all(math.isfinite(v) for v in xy):
                self.cancel('invalid_selected_pose')
                return False
            if self.pose_capacity_exhausted or source in self.pose_tombstones:
                return False
            if source in self.pose_keys and self.pose_keys[source] == fingerprint:
                return False
            latest_source = self.pending_poses[-1][0] if self.pending_poses else (self.pose[0] if self.pose is not None else None)
            latest_fingerprint = self.pending_poses[-1][5] if self.pending_poses else self.pose_fingerprint
            if latest_source is not None and source <= latest_source:
                if source == latest_source and fingerprint == latest_fingerprint:
                    return False
                self.cancel('conflicting_or_regressed_pose')
                if len(self.pose_tombstones) >= 4096:
                    self.pose_capacity_exhausted = True
                else:
                    self.pose_tombstones.add(source)
                self.pending_poses.clear()
                self.pose = None
                return False
            self.pose_keys = {key: value for key, value in self.pose_keys.items() if key >= source - FRESHNESS_NS}
            if len(self.pose_keys) >= 20000:
                self.pose_capacity_exhausted = True
                self.cancel('pose_identity_capacity')
                return False
            self.pose_keys[source] = fingerprint
            if source > now:
                if source - now > FRESHNESS_NS or len(self.pending_poses) >= 1024:
                    self.cancel('future_pose_capacity_or_horizon')
                    return False
                self.pending_poses.append((source, xy, now, steady, deepcopy(msg), fingerprint))
                return False
            if not self.fresh(source, now, steady=steady):
                return False
            self._admit_pose((source, xy, now, steady, msg, fingerprint))
            return True
        except (ValueError, OverflowError):
            self.cancel('invalid_selected_pose')
            return False

    def _admit_pose(self, item):
        self.pose = item[:4]
        self.pose_fingerprint = item[5]
        if self.candidate is not None and math.dist(item[1], self.center(self.candidate)) > self.radius:
            self.cancel('candidate_departure')

    def drain_poses(self):
        now, steady = self.now(), time.monotonic_ns()
        while self.pending_poses:
            item = self.pending_poses[0]
            if now - item[2] > FRESHNESS_NS or steady - item[3] > FRESHNESS_NS:
                self.pending_poses.pop(0)
                continue
            if item[0] > now:
                break
            self.pending_poses.pop(0)
            if item[0] not in self.pose_tombstones and self.fresh(item[0], item[2], steady=item[3]):
                self._admit_pose(item)
                # Existing geometry owner receives the covered observation with
                # the original callback receipt, not a fabricated new receipt.
                if hasattr(self.node, 'pose_callback'):
                    self.node.pose_callback(item[4], v2_admitted=True, receipt_ns=item[2])

    @staticmethod
    def center(candidate):
        return (candidate.confirmation.center_x_m, candidate.confirmation.center_y_m)

    def pose_inside(self, candidate):
        return bool(self.pose is not None and self.fresh(self.pose[0], self.pose[2], steady=self.pose[3])
                    and math.dist(self.pose[1], self.center(candidate)) <= self.radius)

    def confirmation(self, msg):
        if self.recurrent_trapping:
            self._receive_nomination('confirmation', msg)
            return
        self._accept_confirmation(msg)

    def _accept_confirmation(self, msg, diagnostic=None):
        # Reject before allocating a candidate or consuming its SEARCH epoch.
        # Direction/raw evidence and state/epoch heartbeats remain observable.
        if self.node.machine.config.qualification_observation_only:
            return
        now = self.now()
        try:
            context = self.contexts.get(int(msg.context_sequence))
            source, lo, hi = (time_to_ns(getattr(msg, key)) for key in ('source_stamp', 'history_start', 'history_end'))
            valid = (self.ready() and self.identity(msg, lifecycle=True) and msg.valid
                     and self.node.machine.state == State.SEARCH and msg.search_epoch == self.epoch
                     and self.accepted_epoch != self.epoch and context is not None
                     and context[1] == int(State.SEARCH) and context[2]
                     and self.fresh(context[0], context[0]) and self.fresh(time_to_ns(msg.stamp), now)
                     and self.fresh(source, now) and time_to_ns(msg.epoch_started_at) == self.started
                     and self.started <= lo <= hi <= source <= time_to_ns(msg.stamp)
                     and msg.confirmation_sequence > 0
                     and (self.metric_mode is None or msg.metric_mode == self.metric_mode)
                     and all(math.isfinite(v) for v in (msg.center_x_m, msg.center_y_m)))
            if msg.metric_mode == 'pde_mean_v1':
                valid = valid and msg.history_kind == 'pde_input_support' and msg.source_stamp_kind == 'pose_input' and len(msg.legacy_snapshot) == 8 and all(math.isfinite(v) for v in msg.legacy_snapshot) and msg.legacy_r_mean_valid and math.isfinite(msg.legacy_r_mean_m2) and msg.legacy_r_mean_m2 >= 0 and msg.legacy_r_mean_m2 == msg.legacy_snapshot[1] and (msg.center_x_m, msg.center_y_m) == tuple(msg.legacy_snapshot[3:5])
            elif msg.metric_mode in CENTROID_METRIC_MODES:
                valid = valid and msg.history_kind == 'centroid_windows' and msg.source_stamp_kind == 'pose_input' and msg.convergence_score_valid and math.isfinite(msg.convergence_score_m) and msg.convergence_score_m >= 0
            elif msg.metric_mode == 'recurrent_geometry_v3':
                valid = (valid and msg.history_kind == 'recurrent_geometry'
                         and msg.source_stamp_kind == 'pose_input' and msg.convergence_score_valid
                         and math.isfinite(msg.convergence_score_m) and msg.convergence_score_m >= 0
                         and not msg.legacy_r_mean_valid and len(msg.legacy_snapshot) == 0)
            else:
                valid = False
            if not valid:
                return
            if self.candidate_sequence >= MAX_COMMANDS:
                self.last_reason = 'candidate_capacity'
                return
            candidate = Candidate(self.candidate_sequence + 1, deepcopy(msg), now,
                                  now + (APPROACH_NS if self.centered else COLLECTION_NS))
            if not self.pose_inside(candidate):
                return
            if self.recurrent_trapping:
                if diagnostic is None:
                    return
                candidate.recurrent_diagnostic = deepcopy(diagnostic)
                candidate.nomination_sha256 = self._nomination_hash(candidate)
            self.candidate_sequence += 1
            self.candidate = candidate
            self.accepted_epoch = self.epoch
        except (ValueError, TypeError, OverflowError):
            return

    def _reset_nomination_wait(self):
        self.pending_nominations.clear()
        # A readiness interruption cannot authenticate support collected before
        # admission resumes, even when the supervisor SEARCH epoch is unchanged.
        self.nomination_not_before_ns = self.now()

    def _expire_nominations(self):
        for key, pair in tuple(self.pending_nominations.items()):
            if any(not self.fresh(time_to_ns(item[1].stamp), item[2], steady=item[3])
                   for item in pair.values()):
                del self.pending_nominations[key]
                self.nomination_tombstones.add(key)
        if len(self.nomination_tombstones) >= 8:
            self.nomination_fault = True
            self.pending_nominations.clear()

    def recurrent_diagnostic(self, msg):
        if self.recurrent_trapping and msg.confirmed:
            self._receive_nomination('diagnostic', msg)

    def _receive_nomination(self, kind, msg):
        """Bounded two-topic join; original receipts never refresh on duplicates."""
        from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
        candidate = self.candidate
        if candidate is not None and candidate.recurrent_diagnostic is not None:
            original = candidate.confirmation if kind == 'confirmation' else candidate.recurrent_diagnostic
            if (msg.run_id == original.run_id and msg.confirmation_sequence == original.confirmation_sequence
                    and msg.search_epoch == original.search_epoch
                    and hash_payload(message_payload(msg)) != hash_payload(message_payload(original))):
                self.nomination_fault = True
                self.cancel('conflicting_recurrent_nomination')
            return
        if (self.node.machine.config.qualification_observation_only
                or self.node.machine.state != State.SEARCH or not self.ready()
                or self.nomination_fault or self.accepted_epoch == self.epoch):
            return
        now, steady = self.now(), time.monotonic_ns()
        try:
            self._expire_nominations()
            key = int(msg.confirmation_sequence)
            if key <= 0 or key in self.nomination_tombstones or self.nomination_fault:
                return
            if (msg.run_id != self.node.run_id or msg.frame_id != self.config['frame_id']
                    or msg.metric_mode != 'recurrent_geometry_v3'
                    or not self.fresh(time_to_ns(msg.stamp), now)
                    or time_to_ns(msg.epoch_started_at) != self.started):
                return
            if kind == 'confirmation' and (not self.identity(msg, lifecycle=True)
                                           or msg.search_epoch != self.epoch):
                return
            fingerprint = hash_payload(message_payload(msg))
            pair = self.pending_nominations.get(key)
            if pair is None:
                if len(self.pending_nominations) + len(self.nomination_tombstones) >= 8:
                    self.nomination_fault = True
                    self.pending_nominations.clear()
                    return
                pair = self.pending_nominations[key] = {}
            previous = pair.get(kind)
            if previous is not None:
                if previous[0] != fingerprint:
                    self.nomination_fault = True
                    self.pending_nominations.clear()
                    self.last_reason = 'conflicting_recurrent_nomination'
                return
            pair[kind] = (fingerprint, deepcopy(msg), now, steady)
            if len(pair) != 2:
                return
            confirmation, diagnostic = pair['confirmation'][1], pair['diagnostic'][1]
            errors = recurrent_nomination_errors(confirmation, diagnostic,
                expected_source_pose_topic=self.config['pose_topic'], epoch_start_ns=self.started)
            if (time_to_ns(diagnostic.persistence_start) < self.nomination_not_before_ns
                    or errors):
                self.nomination_tombstones.add(key)
                del self.pending_nominations[key]
                self.last_reason = 'invalid_recurrent_nomination'
                return
            self._accept_confirmation(confirmation, diagnostic)
            if self.candidate is not None and self.accepted_epoch == self.epoch:
                self.pending_nominations.clear()
        except (AttributeError, ValueError, TypeError, OverflowError):
            return

    @staticmethod
    def _nomination_hash(candidate):
        return hash_payload({'confirmation': message_payload(candidate.confirmation),
                             'diagnostic': message_payload(candidate.recurrent_diagnostic)})

    def _candidate_nomination_valid(self, candidate):
        from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
        return bool(candidate is not None and not candidate.cancelled and self.ready()
            and candidate.confirmation.search_epoch == self.epoch
            and candidate.nomination_sha256
            and candidate.nomination_sha256 == self._nomination_hash(candidate)
            and not recurrent_nomination_errors(candidate.confirmation, candidate.recurrent_diagnostic,
                expected_source_pose_topic=self.config['pose_topic'], epoch_start_ns=self.started))

    def _snapshot_wrapper(self, candidate, snapshot):
        from ros_esc_interfaces.msg import RecurrentCandidateSnapshot
        from ros_esc.v2_lifecycle import clone_recurrent_snapshot
        wrapper = RecurrentCandidateSnapshot()
        wrapper.schema_version, wrapper.policy_id = 1, self.evidence_policy
        wrapper.snapshot = snapshot
        wrapper.confirmation = candidate.confirmation
        wrapper.diagnostic = candidate.recurrent_diagnostic
        return clone_recurrent_snapshot(wrapper)

    def direction(self, msg):
        now = self.now()
        try:
            if not self.identity(msg) or not self.fresh(time_to_ns(msg.stamp), now):
                return
            if msg.algorithm_state_valid and msg.algorithm_state == int(self.node.machine.state):
                self.direction_ack = (msg.registry_digest, time_to_ns(msg.stamp), now, time.monotonic_ns())
            obs = msg.observation
            if (not self.identity(obs) or not msg.algorithm_state_valid
                    or msg.algorithm_state not in (1, 2, 3, 4, 5)
                    or not obs.synchronized_valid or not obs.raw_cost_valid
                    or not obs.sensor_transform_observed
                    or not self.fresh(time_to_ns(obs.source_stamp), now)
                    or not self.fresh(time_to_ns(obs.admission_stamp), now)):
                return
            key = time_to_ns(obs.source_stamp)
            fingerprint = hash_payload(observation_payload(obs))
            self.first_filter_metadata = {k: v for k, v in self.first_filter_metadata.items()
                                          if k >= now - 1_000_000_000}
            previous = self.first_filter_metadata.get(key)
            if previous is not None and previous[0] != fingerprint:
                self.raw.revoke(key)
                self.cancel('conflicting_filter_observation')
                return
            if previous is None:
                if len(self.first_filter_metadata) >= 20000:
                    self.cancel('filter_metadata_capacity')
                    return
                previous = (fingerprint, int(msg.algorithm_state), time_to_ns(msg.stamp))
                self.first_filter_metadata[key] = previous
            if not self.ready():
                return
            before = self.raw.reset_sequence
            self.raw.add(obs, previous[1], previous[2])
            if self.raw.reset_sequence != before and self.raw.reason in ('conflicting_observation', 'source_regression', 'invalid_or_overflow'):
                self.cancel(self.raw.reason)
        except (ValueError, TypeError, OverflowError):
            self.cancel('invalid_direction_observation')

    def objective(self, msg):
        now = self.now()
        try:
            if self.identity(msg) and msg.valid and self.fresh(time_to_ns(msg.stamp), now):
                self.objective_ack = (msg.registry_digest, time_to_ns(msg.stamp), now, time.monotonic_ns())
        except ValueError:
            return

    def provenance(self, msg):
        if not self.identity(msg) or (msg.model_input_stamp_valid and msg.sensor_transform_valid):
            return
        try:
            key = time_to_ns(msg.model_input_stamp)
            affected = self.raw.revoke(key)
            frozen = (self.candidate is not None and self.candidate.snapshot is not None
                      and any(time_to_ns(o.source_stamp) == key for o in self.candidate.snapshot.observations))
            if affected or frozen:
                self.cancel('source_revoked')
        except ValueError:
            return

    def snapshot(self, candidate, evidence, revision=1):
        trapping = getattr(self, 'recurrent_trapping', False)
        msg = CandidateSnapshot()
        copy_envelope(msg, candidate.confirmation)
        msg.stamp = stamp(self.now())
        msg.candidate_id = candidate.candidate_id
        msg.objective_revision = evidence.records[-1].observation.objective_revision
        msg.detector_confirmation_sequence = candidate.confirmation.confirmation_sequence
        msg.snapshot_revision = revision
        msg.metric_mode = candidate.confirmation.metric_mode
        msg.confirmation_stamp = deepcopy(candidate.confirmation.source_stamp)
        msg.accepted_at = stamp(candidate.accepted_ns)
        msg.evidence_start = stamp(evidence.cycles[0].start_ns)
        msg.evidence_end = stamp(evidence.cycles[-1].end_ns)
        msg.center_x_m, msg.center_y_m = self.center(candidate)
        msg.neighborhood_radius_m, msg.centroid_tolerance_m = self.radius, self.epsilon
        for key in ('convergence_score_m', 'convergence_score_valid', 'legacy_r_mean_m2', 'legacy_r_mean_valid'):
            setattr(msg, key, getattr(candidate.confirmation, key))
        summary = evidence.summary
        for key in ('estimate', 'mad', 'uncertainty', 'lower', 'upper'):
            setattr(msg, 'candidate_cost_' + key, float(getattr(summary, key)))
        msg.information_amplitude = evidence.amplitude
        msg.information_disagreement = evidence.disagreement
        msg.information_floor = evidence.information_floor
        msg.informative = evidence.informative
        msg.completed_revolutions = 3
        msg.pretrigger_revolutions = summary.pretrigger_rotation_count
        msg.verification_revolutions = summary.verification_rotation_count
        msg.revolution_start = [stamp(c.start_ns) for c in evidence.cycles]
        msg.revolution_end = [stamp(c.end_ns) for c in evidence.cycles]
        msg.revolution_sample_start = [v[0] for v in evidence.sample_ranges]
        msg.revolution_sample_end = [v[1] for v in evidence.sample_ranges]
        # Borrow references only inside this synchronous local assembly. One
        # complete wire clone detaches them before hashing, retention or publish.
        msg.observations = [r.observation for r in evidence.records]
        msg.observation_filter_state = [r.filter_state for r in evidence.records]
        msg.observation_filter_stamp = [stamp(r.filter_stamp_ns) for r in evidence.records]
        msg = clone_ros_message(msg)
        if trapping:
            from ros_esc.v2_lifecycle import recurrent_snapshot_sha256
            if not self._candidate_nomination_valid(candidate):
                raise ValueError('candidate recurrent nomination changed or lost authority')
            msg.evidence_sha256 = recurrent_snapshot_sha256(msg, self._snapshot_wrapper(candidate, msg))
        else:
            msg.evidence_sha256 = snapshot_sha256(msg)
        identity = (msg.candidate_id, msg.snapshot_revision)
        previous = self.published_snapshots.get(identity)
        if previous is not None and previous != msg.evidence_sha256:
            raise ValueError("candidate snapshot identity reused with different evidence")
        if previous is None:
            self.published_snapshots[identity] = msg.evidence_sha256
            self.snapshot_publisher.publish(self._snapshot_wrapper(candidate, msg)
                if trapping else clone_ros_message(msg))
        return msg

    def _evaluate(self, candidate):
        if self.recurrent_trapping and not self._candidate_nomination_valid(candidate):
            from ros_esc.supervisor_node.moving_evidence import MovingEvidence
            return MovingEvidence(reason='recurrent_nomination_unavailable')
        return self.raw.evaluate(self.center(candidate), self.radius, self.epsilon,
                                 time_to_ns(candidate.confirmation.source_stamp),
                                 mad_scale=self.node.machine.config.candidate_cost_mad_scale,
                                 evidence_policy=self.evidence_policy)

    def _admit_collection(self, candidate):
        """Freeze one observed admission; later re-entry never renews its clock."""
        now = self.now()
        if (not self.centered or candidate.collection_admitted_ns is not None
                or now > candidate.accepted_ns + APPROACH_NS
                or not self.pose_inside(candidate)
                or math.dist(self.pose[1], self.center(candidate)) > ADMISSION_RADIUS_M):
            return
        from ros_esc_interfaces.msg import AlgorithmEvent
        candidate.collection_admitted_ns = now
        candidate.deadline_ns = min(now + COLLECTION_NS, candidate.accepted_ns + TOTAL_NS)
        event = AlgorithmEvent()
        event.stamp = stamp(now)
        event.event_type = ADMISSION_EVENT
        event.state, event.state_name, event.state_valid = int(State.VERIFY_EXTREMUM), 'VERIFY_EXTREMUM', True
        event.detail = ADMISSION_DETAIL
        event.value_names = ['candidate_id', 'search_epoch']
        event.values = [float(candidate.candidate_id), float(self.epoch)]
        self.node.event_publisher.publish(event)

    def _centered_handoff_avoidances(self, candidate, now_ns):
        """Exclude only this DESIGN's authenticated fill during its ACK handoff.

        The committed mathematical fill is the object of the pending escape,
        not a new obstacle to its own centered proposal. Registry accounting and
        the original preparation lease must still agree in both local mirrors.
        Any mismatch retains every avoidance; ACK/state ownership is unchanged.
        """
        full = self.node._active_fill_avoidances()
        prep = self.current_preparation
        try:
            if (not self.centered or self.verification_mode != CENTERED_MODE
                    or self.node.machine.state != State.DESIGN_OR_MERGE_FILL
                    or self.node.machine.design_returns_to_assist
                    or candidate is None or candidate is not self.candidate or candidate.cancelled
                    or prep is None or prep.candidate is not candidate or prep.cancelled
                    or self.preparations.get(prep.command.preparation_id) is not prep
                    or prep.command.redesign or prep.command.return_state != int(State.ESCAPE_REPULSE)
                    or not self.ready() or not self.pose_inside(candidate)):
                return full
            activated, prepared, command = prep.activated, prep.prepared, prep.command
            if (activated is None or prepared is None
                    or activated.result not in (FillResult.ACTIVATED, FillResult.ALREADY_ACTIVATED)
                    or prepared.result != FillResult.PREPARED
                    or activated.preparation_id != command.preparation_id
                    or prepared.preparation_id != command.preparation_id
                    or not (activated.candidate_id == command.candidate_id == candidate.candidate_id)
                    or activated.search_epoch != self.epoch
                    or envelope_identity(activated) != envelope_identity(command)
                    or activated.evidence_sha256 != command.evidence_sha256
                    or not activated.prepared_sha256
                    or activated.prepared_sha256 != prepared.prepared_sha256
                    or activated.return_state != command.return_state
                    or not activated.committed_sha256
                    or result_sha256(activated) != activated.committed_sha256):
                return full
            sent = prep.sequences.get(activated.command_sequence)
            expires = time_to_ns(command.expires_at)
            if (sent is None or sent.operation != FillCommand.ACTIVATE
                    or time_to_ns(activated.expires_at) != expires
                    or time_to_ns(prepared.expires_at) != expires
                    or not time_to_ns(activated.committed_at) <= now_ns < expires
                    or activated.expected_registry_generation != command.expected_registry_generation
                    or activated.registry_generation != command.expected_registry_generation + 1
                    or activated.registry_generation != self.generation
                    or activated.registry_digest_after != self.registry_digest
                    or self.commit_keys.get(self.generation) != self.commit_key(activated)
                    or fill_registry_digest(self.active_fills.values()) != self.registry_digest):
                return full
            fill = activated.fill
            active = self.active_fills.get(fill.cluster_id)
            record = self.node.active_fill_records.get(fill.cluster_id)
            if (active is None or record is None or not self.valid_fill(fill)
                    or message_payload(active) != message_payload(fill)
                    or record['fill_id'] != fill.fill_id or record['revision'] != fill.revision
                    or tuple(record['center']) != (fill.center_x, fill.center_y)
                    or record['support_radius'] != fill.support_radius
                    or record['exit_radius'] != fill.exit_radius):
                return full
            matching = [i for i, avoidance in enumerate(full)
                if (avoidance.fill_id == fill.fill_id and avoidance.cluster_id == fill.cluster_id
                    and (avoidance.center_x, avoidance.center_y) == (fill.center_x, fill.center_y)
                    and avoidance.radius == fill.support_radius + self.node.fill_avoidance_margin_m)]
            if len(matching) != 1:
                return full
            return tuple(avoidance for i, avoidance in enumerate(full) if i != matching[0])
        except (AttributeError, KeyError, ValueError, TypeError, OverflowError):
            return full

    def publish_guidance(self, state):
        """Publish only a same-state proposal; old states cannot borrow a Twist."""
        if not self.centered:
            return
        from ros_esc_interfaces.msg import VerificationGuidance
        from ros_esc.supervisor_node.escape_recenter import command_sweep_is_safe
        message = VerificationGuidance()
        self.guidance_sequence += 1
        message.schema_version = 2
        message.publication_sequence = self.guidance_sequence
        message.state_sha256 = hash_payload(message_payload(state))
        message.stamp = deepcopy(state.stamp)
        message.state_stamp = deepcopy(state.stamp)
        message.run_id, message.stream_contract_id = self.node.run_id, self.contract or ''
        message.frame_id, message.mode = self.config['frame_id'], self.verification_mode
        message.search_epoch, message.algorithm_state = self.epoch, int(state.state)
        candidate = self.candidate
        selected = (state.state == int(State.VERIFY_EXTREMUM)
                    or (state.state == int(State.DESIGN_OR_MERGE_FILL)
                        and not self.node.machine.design_returns_to_assist))
        message.reason = 'outside_centered_collection'
        if selected and candidate is not None:
            message.candidate_id = candidate.candidate_id
            message.accepted_at = stamp(candidate.accepted_ns)
            message.collection_started = candidate.collection_admitted_ns is not None
            message.collection_admitted_at = stamp(candidate.collection_admitted_ns or 0)
            message.verification_expires_at = stamp(candidate.deadline_ns)
            message.center_x_m, message.center_y_m = self.center(candidate)
            deadline = candidate.deadline_ns
            if state.state == int(State.DESIGN_OR_MERGE_FILL) and self.current_preparation is not None:
                deadline = time_to_ns(self.current_preparation.command.expires_at)
            message.command_expires_at = stamp(deadline)
            pose = self.node.latest_pose
            if state.state == int(State.DESIGN_OR_MERGE_FILL) and self.current_preparation is None:
                message.reason = 'centered_preparation_pending'
            elif (candidate.cancelled or not self.ready() or not self.pose_inside(candidate)
                    or self.now() >= deadline or pose is None
                    or abs(pose.stamp_sec*1e9-self.pose[0]) > 1.):
                message.reason = candidate.reason or 'centered_candidate_or_pose_unavailable'
            else:
                try:
                    command = tracking_command(self.tracking_control, self.center(candidate),
                        pose.position, pose.yaw, (self.now()-candidate.accepted_ns)*1e-9,
                        approach=(state.state == int(State.VERIFY_EXTREMUM)
                                  and candidate.collection_admitted_ns is None))
                    linear, angular = float(command[0]), float(command[5])
                    sweep_yaw = pose.yaw + (math.pi if linear < 0 else 0.)
                    handoff_design = (state.state == int(State.DESIGN_OR_MERGE_FILL)
                        and state.previous_state_valid
                        and state.previous_state == int(State.VERIFY_EXTREMUM))
                    avoidances = (self._centered_handoff_avoidances(candidate, self.now())
                        if handoff_design else self.node._active_fill_avoidances())
                    safe = command_sweep_is_safe(pose.position, sweep_yaw, abs(linear),
                        self.node.supervisor_command_stale_sec, avoidances,
                        self.node.bounds, allow_inward_from_margin=True,
                        boundary_trigger_clearance_m=self.node.boundary_recovery_trigger_clearance_m)
                except (ValueError, TypeError, OverflowError, ArithmeticError):
                    safe = False
                if safe:
                    message.pose_stamp = stamp(self.pose[0])
                    message.linear_x_mps, message.angular_z_radps = linear, angular
                    message.valid, message.reason = True, 'centered_tracking'
                else:
                    self.cancel('centered_command_sweep_unsafe')
                    message.reason = 'centered_command_sweep_unsafe'
        self.guidance_publisher.publish(message)

    def inputs(self, inputs):
        self.drain_poses()
        if not self.ready():
            self.cancel("recording_not_ready")
            self._reset_nomination_wait()
        if self.recurrent_trapping:
            self._expire_nominations()
        candidate = self.candidate
        state = self.node.machine.state
        if self.origin_fault:
            return replace(inputs, controller_fault=True)
        kwargs = dict(convergence=False, convergence_confirmed=False, candidate_cost_observed=False,
                      candidate_cost_valid=True, candidate_cost_ready=False, candidate_cost_summary=None,
                      candidate_informative=False, candidate_verification_passed=False,
                      candidate_associated_with_fill=False,
                      fill_result=None, fill_source_timestamp=None, fill_id=None,
                      active_fill_count=len(self.active_fills))
        if state == State.SEARCH and candidate is not None and not candidate.cancelled:
            kwargs['convergence_confirmed'] = (self.pose_inside(candidate)
                and (not self.recurrent_trapping or self._candidate_nomination_valid(candidate)))
        if state in (State.VERIFY_EXTREMUM, State.DESIGN_OR_MERGE_FILL) and candidate is not None:
            if not self.pose_inside(candidate):
                self.cancel('candidate_pose_unavailable_or_departed')
            kwargs['moving_candidate_cancelled'] = candidate.cancelled
        if state == State.VERIFY_EXTREMUM and candidate is not None and not candidate.cancelled:
            self._admit_collection(candidate)
            if self.now() >= candidate.deadline_ns:
                self.cancel('centered_approach_deadline' if self.centered and
                            candidate.collection_admitted_ns is None else 'verification_deadline')
                kwargs['moving_candidate_cancelled'] = True
            else:
                kwargs["candidate_associated_with_fill"] = any(
                    math.dist(self.center(candidate), (f.center_x, f.center_y)) <= max(f.support_radius, f.exit_radius)
                    for f in self.active_fills.values())
                evidence = self._evaluate(candidate)
                if self.centered and candidate.collection_admitted_ns is None:
                    candidate.last_evidence_detail = 'approaching_frozen_center'
                    return replace(inputs, **kwargs)
                self.last_reason = evidence.reason
                candidate.last_evidence_detail = evidence.reason + ' ' + json.dumps(
                    dict(evidence.diagnostics), sort_keys=True, separators=(',', ':'))
                kwargs.update(candidate_cost_observed=bool(self.raw.records), candidate_cost_ready=evidence.ready,
                              candidate_cost_summary=evidence.summary, candidate_informative=evidence.informative)
                if self.recurrent_trapping:
                    kwargs['candidate_verification_passed'] = bool(
                        evidence.ready and self._candidate_nomination_valid(candidate))
                if evidence.ready:
                    candidate.evidence = evidence
                    if candidate.snapshot is None:
                        candidate.snapshot = self.snapshot(candidate, evidence)
        prep = self.current_preparation
        if state == State.DESIGN_OR_MERGE_FILL and prep is not None:
            if prep.terminal and prep.activated is None:
                kwargs['fill_result'] = 'rejected'
            if prep.activated is not None and not prep.cancelled and candidate is prep.candidate:
                acks = (self.objective_ack, self.direction_ack)
                if all(a is not None and a[0] == prep.activated.registry_digest_after
                       and self.fresh(a[1], a[2], steady=a[3])
                       and a[1] >= time_to_ns(prep.activated.committed_at) for a in acks):
                    kwargs.update(fill_result='success', fill_id=int(prep.activated.fill.fill_id))
            if self.now() >= time_to_ns(prep.command.expires_at) and prep.activated is None:
                self.cancel('preparation_deadline')
                kwargs['moving_candidate_cancelled'] = True
        if state == State.DESIGN_OR_MERGE_FILL and self.node.machine.design_returns_to_assist:
            progress = self.node.escape_tracker.latest if self.node.escape_tracker is not None else None
            kwargs['stable_exit'] = bool(progress is not None and progress.stable_exit)
        if candidate is not None and candidate.cancelled:
            kwargs['moving_candidate_reason'] = candidate.reason
            if candidate.last_evidence_detail:
                kwargs['moving_candidate_reason'] += '; last_evidence=' + candidate.last_evidence_detail
        return replace(inputs, **kwargs)

    def on_transition(self, transition):
        if transition.previous == State.SEARCH:
            self.pending_nominations.clear()
        if transition.current == State.SEARCH:
            self.cancel('search_reentry')
            self.epoch += 1
            self.started = self.now()
            self.raw.start_epoch(self.epoch, self.started)
            self.candidate = None
            self.current_preparation = None
            self.contexts.clear()
            self.pending_nominations.clear()
            self.nomination_tombstones.clear()
            self.nomination_fault = False
            self.nomination_not_before_ns = self.started
            self.pose_tombstones.clear()
            self.pose_capacity_exhausted = False
        elif transition.current == State.DESIGN_OR_MERGE_FILL:
            self.node._publish_state_and_command(self.now() * 1e-9)
            self.begin_preparation(redesign=transition.previous == State.ESCAPE_REPULSE)
        elif transition.previous == State.DESIGN_OR_MERGE_FILL:
            if transition.current not in (State.ESCAPE_REPULSE, State.ESCAPE_ASSIST):
                self.cancel('design_state_exited')
            elif self.current_preparation is not None and self.current_preparation.activated is None:
                self.cancel('redesign_abandoned')
        if transition.current in (State.GOAL_HOLD, State.FAILSAFE, State.RECENTER):
            self.cancel('motion_authorization_ended')

    def begin_preparation(self, *, redesign):
        candidate = self.candidate
        target = None
        if redesign:
            fill_id = self.node.machine.active_escape_fill_id
            previous = self.fill_candidates.get(fill_id)
            target = next((f for f in self.active_fills.values() if f.fill_id == fill_id), None)
            if previous is None or target is None:
                self.cancel('redesign_target_unavailable')
                return
            candidate = Candidate(previous.candidate_id, deepcopy(previous.confirmation), previous.accepted_ns,
                                  previous.deadline_ns)
            candidate.recurrent_diagnostic = deepcopy(previous.recurrent_diagnostic)
            candidate.nomination_sha256 = previous.nomination_sha256
            self.candidate = candidate
            evidence = self._evaluate(candidate)
            if not evidence.ready:
                self.cancel('redesign_evidence_unavailable')
                return
            candidate.evidence = evidence
            candidate.snapshot = self.snapshot(candidate, evidence, previous.snapshot.snapshot_revision + 1)
        if candidate is None or candidate.snapshot is None or not self.ready() or not self.pose_inside(candidate):
            self.cancel('preparation_candidate_unavailable')
            return
        if self.command_sequence >= MAX_COMMANDS:
            self.cancel('command_capacity')
            return
        self.preparation_sequence += 1
        cmd = FillCommand()
        copy_envelope(cmd, candidate.snapshot)
        cmd.stamp = stamp(self.now())
        cmd.operation = FillCommand.PREPARE
        cmd.candidate_id = candidate.candidate_id
        cmd.objective_revision = candidate.snapshot.objective_revision
        cmd.preparation_id = self.preparation_sequence
        cmd.expected_registry_generation = self.generation
        deadline = self.now() + round(self.node.machine.config.fill_design_timeout_sec * 1e9)
        if redesign:
            deadline = min(deadline, round((self.node.machine.escape_started_sec + self.node.machine.config.escape_max_sec) * 1e9))
            cmd.target_fill_id, cmd.target_cluster_id, cmd.target_revision = target.fill_id, target.cluster_id, target.revision
        cmd.expires_at = stamp(deadline)
        cmd.evidence_sha256 = candidate.snapshot.evidence_sha256
        cmd.snapshot = clone_ros_message(candidate.snapshot)
        cmd.redesign = redesign
        cmd.return_state = int(State.ESCAPE_ASSIST if redesign else State.ESCAPE_REPULSE)
        prep = Preparation(cmd, candidate, {})
        self.preparations[cmd.preparation_id] = prep
        self.current_preparation = prep
        self._send(prep, FillCommand.PREPARE)

    def _send(self, prep, operation, reason=''):
        if self.command_sequence >= MAX_COMMANDS:
            prep.terminal = True
            self.last_reason = 'command_capacity'
            return
        self.command_sequence += 1
        cmd = clone_ros_message(prep.command)
        cmd.stamp = stamp(self.now())
        cmd.command_sequence = self.command_sequence
        cmd.operation = operation
        cmd.reason = reason
        if prep.prepared is not None:
            cmd.prepared_sha256 = prep.prepared.prepared_sha256
        prep.sequences[cmd.command_sequence] = cmd
        if self.recurrent_trapping:
            from ros_esc_interfaces.msg import RecurrentFillCommand
            from ros_esc.v2_lifecycle import clone_recurrent_command
            wrapper = RecurrentFillCommand()
            wrapper.schema_version, wrapper.policy_id = 1, self.evidence_policy
            wrapper.command = cmd
            wrapper.confirmation = prep.candidate.confirmation
            wrapper.diagnostic = prep.candidate.recurrent_diagnostic
            self.command_publisher.publish(clone_recurrent_command(wrapper))
        else:
            self.command_publisher.publish(cmd)

    def cancel(self, reason):
        self.last_reason = reason
        if self.candidate is not None:
            self.candidate.cancelled = True
            self.candidate.reason = reason
        prep = self.current_preparation
        if prep is not None and not prep.cancelled:
            prep.cancelled = True
            self._send(prep, FillCommand.CANCEL, reason)

    @staticmethod
    def commit_key(msg):
        return hash_payload({'generation': msg.registry_generation,
            'before': msg.registry_digest_before, 'after': msg.registry_digest_after,
            'committed_at': time_to_ns(msg.committed_at),
            'fill': message_payload(msg.fill), 'has_superseded_fill': msg.has_superseded_fill,
            'superseded_fill': message_payload(msg.superseded_fill) if msg.has_superseded_fill else None})

    @staticmethod
    def valid_fill(fill):
        values = (fill.center_x, fill.center_y, fill.amplitude, fill.covariance_xx,
                  fill.covariance_xy, fill.covariance_yy, fill.sigma_major,
                  fill.sigma_minor, fill.support_radius, fill.exit_radius)
        return bool(fill.active and not fill.superseded and fill.source_timestamp_valid
                    and math.isfinite(fill.source_timestamp) and fill.covariance_valid
                    and fill.principal_widths_valid and fill.support_radius_valid and fill.exit_radius_valid
                    and all(math.isfinite(v) for v in values) and fill.amplitude >= 0
                    and min(fill.sigma_major, fill.sigma_minor, fill.support_radius,
                            fill.exit_radius, fill.covariance_xx, fill.covariance_yy) > 0
                    and fill.covariance_xx * fill.covariance_yy > fill.covariance_xy ** 2)

    def result(self, msg):
        try:
            if not self.identity(msg, lifecycle=True):
                return
            prep = self.preparations.get(msg.preparation_id)
            if prep is None:
                return
            sent = prep.sequences.get(msg.command_sequence)
            if sent is None:
                return
            if (envelope_identity(msg) != envelope_identity(prep.command)
                    or msg.candidate_id != prep.command.candidate_id
                    or msg.objective_revision != prep.command.objective_revision
                    or msg.expected_registry_generation != prep.command.expected_registry_generation
                    or msg.evidence_sha256 != prep.command.evidence_sha256
                    or time_to_ns(msg.expires_at) != time_to_ns(prep.command.expires_at)
                    or msg.return_state != prep.command.return_state):
                return
            if msg.result == FillResult.PREPARED:
                if (sent.operation != FillCommand.PREPARE or prep.prepared is not None or prep.cancelled
                        or not msg.prepared_sha256 or self.current_preparation is not prep
                        or self.node.machine.state != State.DESIGN_OR_MERGE_FILL
                        or not self.ready() or self.now() >= time_to_ns(msg.expires_at) or not self.pose_inside(prep.candidate)
                        or msg.registry_generation != self.generation):
                    return
                prep.prepared = deepcopy(msg)
                self._send(prep, FillCommand.ACTIVATE)
                return
            if msg.result in (FillResult.ACTIVATED, FillResult.ALREADY_ACTIVATED):
                if sent.operation not in (FillCommand.ACTIVATE, FillCommand.CANCEL):
                    return
                if (not msg.committed_sha256 or result_sha256(msg) != msg.committed_sha256
                        or prep.prepared is None or msg.prepared_sha256 != prep.prepared.prepared_sha256):
                    return
                key = self.commit_key(msg)
                if msg.registry_generation in self.commit_keys:
                    if self.commit_keys[msg.registry_generation] != key:
                        self.node.graph_fault = 'conflicting typed committed registry generation'
                    return
                if (msg.registry_generation != self.generation + 1
                        or msg.registry_digest_before != self.registry_digest
                        or msg.expected_registry_generation != self.generation
                        or not (time_to_ns(msg.prepared_at) <= time_to_ns(msg.committed_at)
                                < time_to_ns(msg.expires_at))):
                    self.node.graph_fault = 'typed fill registry chain mismatch'
                    return
                fills = dict(self.active_fills)
                fill = msg.fill
                if not self.valid_fill(fill) or fill.frame_id != self.config["frame_id"] or min(fill.fill_id, fill.cluster_id, fill.revision) <= 0:
                    return
                if msg.has_superseded_fill:
                    old = fills.get(fill.cluster_id)
                    if (not prep.command.redesign or old is None
                            or old.fill_id != prep.command.target_fill_id
                            or old.revision != prep.command.target_revision
                            or msg.superseded_fill.fill_id != old.fill_id
                            or fill.revision != old.revision + 1):
                        return
                elif prep.command.redesign or fill.cluster_id in fills:
                    return
                fills[fill.cluster_id] = deepcopy(fill)
                if fill_registry_digest(fills.values()) != msg.registry_digest_after:
                    return
                machine = self.node.machine
                if not prep.command.redesign:
                    if len(fills) != len(machine.filled_candidate_costs) + 1 or len(fills) > machine.config.known_source_count - 1:
                        self.node.graph_fault = 'typed fill counted-candidate ledger mismatch'
                        return
                    machine.filled_candidate_costs.append(prep.candidate.evidence.summary)
                machine.active_fill_count = len(fills)
                if self.candidate is prep.candidate:
                    machine.pending_candidate_cost = None
                self.active_fills = fills
                self.generation = int(msg.registry_generation)
                self.registry_digest = msg.registry_digest_after
                self.commit_keys[self.generation] = key
                self.fill_candidates[fill.fill_id] = prep.candidate
                self.node.fill_callback(fill, authoritative=True)
                prep.activated = deepcopy(msg)
                prep.terminal = True
                return
            if msg.result in (FillResult.CANCELLED, FillResult.EXPIRED, FillResult.REJECTED):
                prep.terminal = True
                if self.current_preparation is prep:
                    self.last_reason = msg.reason
        except (ValueError, TypeError, OverflowError, AttributeError):
            self.last_reason = 'invalid_fill_result'
