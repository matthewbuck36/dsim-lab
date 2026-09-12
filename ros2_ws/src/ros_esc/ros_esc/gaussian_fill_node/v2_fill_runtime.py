"""Serialized moving-fill lifecycle inside the existing Gaussian node."""

from bisect import bisect_left
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict, dataclass
import math
import time

import numpy as np
from rclpy.clock import Clock, ClockType
from ros_esc_interfaces.msg import FillCommand, FillResult, GaussianFill, SearchEpochContext, Timekeeper, CandidateSnapshot, AlgorithmEvent

from ros_esc.gaussian_fill_node.basin_estimator import BasinSample
from ros_esc.gaussian_fill_node.fill_preparation import (
    PreparationInput, compute_fill_proposal, sample_payload, validate_samples,
)
from ros_esc.gaussian_fill_node.fill_registry import FillVersion
from ros_esc.v2_lifecycle import (
    FRESHNESS_NS, MAX_COMMANDS, PROTOCOL_VERSION, FILL_COMMAND_TOPIC, FILL_RESULT_TOPIC, SEARCH_EPOCH_TOPIC, copy_envelope, envelope_identity,
    clone_ros_message, fill_registry_digest, hash_payload, message_payload, result_sha256, snapshot_sha256,
    ANGULAR_PROFILES_POLICY, RECURRENT_TRAPPING_POLICY, RECURRENT_FILL_COMMAND_TOPIC,
    validate_verification_evidence_policy, recurrent_proof_payload, recurrent_snapshot_sha256,
)
from ros_esc.v2_stream import relative_stamp_ns, set_time, stream_contract_id, time_to_ns, validate_mode_identity


def version_message(version, stamp_ns, frame):
    """Complete legacy mirror, created without publishing or allocating IDs."""
    msg = GaussianFill()
    set_time(msg.stamp, stamp_ns)
    msg.source_timestamp, msg.source_timestamp_valid = float(version.source_timestamp), True
    msg.frame_id = frame
    for name in ("fill_id", "cluster_id", "revision", "amplitude", "sigma_major", "sigma_minor",
                 "orientation", "support_radius", "exit_radius", "confidence", "sample_count",
                 "fit_residual", "fit_condition_number", "design_escalations", "active", "superseded"):
        setattr(msg, name, getattr(version, name))
    msg.center_x, msg.center_y = (float(v) for v in version.center)
    msg.covariance_xx = float(version.covariance[0, 0])
    msg.covariance_xy = float(version.covariance[0, 1])
    msg.covariance_yy = float(version.covariance[1, 1])
    for name in ("covariance_valid", "principal_widths_valid", "support_radius_valid", "exit_radius_valid",
                 "confidence_valid", "sample_count_valid", "fit_residual_valid", "design_escalations_valid"):
        setattr(msg, name, True)
    msg.fit_condition_number_valid = version.fit_condition_number_valid
    return msg


@dataclass
class PendingPreparation:
    command: object
    status: int = 0
    proposal: object = None
    prepared_hash: str = ""
    prepared_at_ns: int = 0
    active_result: object = None
    wall_expires_ns: int = 0
    proof_payload: object = None


class MovingFillRuntime:
    """One pure worker; all command, completion and commit decisions stay serialized."""

    def __init__(self, node, *, worker=None, steady_now=None):
        self.node = node
        try:
            self.evidence_policy = node.get_parameter('v2_verification_evidence_policy').value
        except KeyError:  # Original pure-owner fixtures predate the declared parameter.
            self.evidence_policy = ANGULAR_PROFILES_POLICY
        recurrent = self.evidence_policy == RECURRENT_TRAPPING_POLICY
        validate_verification_evidence_policy(self.evidence_policy,
            simulation=bool(node.get_parameter('use_sim_time').value),
            continuous_search_mode=(node.get_parameter('continuous_search_mode').value
                                    if recurrent else 'rolling_gesc_v2'),
            algorithm_profile=node.algorithm_profile,
            metric_mode=node.get_parameter('convergence_metric_mode').value if recurrent else None,
            motion_mode=node.get_parameter('v2_verification_motion_mode').value if recurrent else None)
        command_topic = RECURRENT_FILL_COMMAND_TOPIC if recurrent else FILL_COMMAND_TOPIC
        for parameter, topic in (('v2_fill_command_topic', command_topic),
                                 ('v2_fill_result_topic', FILL_RESULT_TOPIC),
                                 ('v2_search_epoch_topic', SEARCH_EPOCH_TOPIC)):
            if node.resolve_topic_name(str(node.get_parameter(parameter).value)) != topic:
                raise ValueError('moving fill lifecycle topic differs from frozen contract')
        self.run_id = str(node.get_parameter("v2_run_id").value)
        self.config = validate_mode_identity(
            "rolling_gesc_v2", node.algorithm_profile, self.run_id,
            node.get_parameter("v2_stream_config_json").value,
            simulation=bool(node.get_parameter("use_sim_time").value))
        if node.resolve_topic_name(str(node.get_parameter("pose_topic").value)) != self.config["pose_topic"]:
            raise ValueError("fill pose topic differs from V2 stream contract")
        self.origin_ns, self.origin_fault = None, False
        self.state_frontier_ns = None
        self.steady_now = steady_now or time.monotonic_ns
        self.pool = worker or ThreadPoolExecutor(max_workers=1, thread_name_prefix="fill_prepare")
        self.future = self.future_token = None
        self.commands = OrderedDict()
        self.preparations = {}
        self.last_command_sequence = 0
        self.current = None
        self.context = self.context_receipt = self.state = self.state_receipt = None
        self.poses = deque(maxlen=64)
        self.last_pose_stamp = self.last_now = None
        self.closed = False
        group = node.fill_request_callback_group
        self.publisher = node.create_publisher(FillResult, str(node.get_parameter("v2_fill_result_topic").value), 100)
        command_type, command_callback = FillCommand, self.command_cb
        if recurrent:
            from ros_esc_interfaces.msg import RecurrentFillCommand
            command_type, command_callback = RecurrentFillCommand, self.recurrent_command_cb
        self.command_subscription = node.create_subscription(
            command_type, str(node.get_parameter("v2_fill_command_topic").value), command_callback, 100,
            callback_group=group)
        self.context_subscription = node.create_subscription(
            SearchEpochContext, str(node.get_parameter("v2_search_epoch_topic").value), self.context_cb, 100,
            callback_group=group)
        self.timekeeper_subscription = node.create_subscription(
            Timekeeper, self.config['timekeeper_topic'], self.set_timekeeper, 10, callback_group=group)
        self.steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.timer = node.create_timer(.02, self.poll, callback_group=group, clock=self.steady_clock)

    def now(self):
        return self.node.get_clock().now().nanoseconds

    def _receipt(self):
        return self.now(), self.steady_now()

    def _fresh(self, stamp_ns, receipt, now):
        return (receipt is not None and 0 <= now-stamp_ns <= FRESHNESS_NS
                and 0 <= now-receipt[0] <= FRESHNESS_NS
                and 0 <= self.steady_now()-receipt[1] <= FRESHNESS_NS)

    def _same_stream(self, msg):
        try:
            return (not self.origin_fault and self.origin_ns is not None
                    and time_to_ns(msg.time_origin) == self.origin_ns
                    and msg.schema_version == PROTOCOL_VERSION and msg.run_id == self.run_id
                    and msg.frame_id == self.config["frame_id"]
                    and msg.stream_contract_id == stream_contract_id(self.config, time_to_ns(msg.time_origin)))
        except (ValueError, TypeError, OverflowError):
            return False

    def set_timekeeper(self, msg):
        try:
            if msg.mode != 'sim time' or not math.isfinite(msg.start_time) or msg.start_time < 0:
                raise ValueError('invalid time origin')
            origin = relative_stamp_ns(0, msg.start_time)
            if self.origin_ns is not None and origin != self.origin_ns:
                raise ValueError('changed time origin')
            if not self.origin_fault:
                self.origin_ns = origin
        except (ValueError, TypeError, OverflowError):
            self.origin_fault = True
            self._cancel_current('invalid or changed time origin')

    def context_cb(self, msg):
        receipt = self._receipt()
        if not self._same_stream(msg):
            return
        if self.context is not None:
            if msg.context_sequence < self.context.context_sequence:
                return
            if msg.context_sequence == self.context.context_sequence:
                if message_payload(msg, exclude=("stamp",)) == message_payload(self.context, exclude=("stamp",)):
                    return
                self.context = None
                self._cancel_current("conflicting epoch context")
                return
        self.context, self.context_receipt = deepcopy(msg), receipt
        if self.current is not None and (not msg.valid or msg.search_epoch != self.current.command.search_epoch
                or envelope_identity(msg) != envelope_identity(self.current.command)):
            self._cancel_current("epoch context changed")

    def state_cb(self, msg):
        receipt = self._receipt()
        if not msg.run_id_valid or msg.run_id != self.run_id:
            return
        stamp = time_to_ns(msg.stamp)
        if self.state_frontier_ns is not None and stamp < self.state_frontier_ns:
            self.state = None
            self._cancel_current('state source regression')
            return
        if self.state_frontier_ns == stamp:
            # A held clock may cover a legitimate transition, but can never
            # restart the first receipt's wall freshness interval.
            receipt = self.state_receipt
        self.state_frontier_ns = stamp
        self.state, self.state_receipt = deepcopy(msg), receipt
        if not msg.state_valid or msg.state in (msg.STATE_FAILSAFE, msg.STATE_GOAL_HOLD, msg.STATE_SEARCH):
            self._cancel_current("state no longer authorizes candidate")

    def pose_cb(self, msg):
        receipt = self._receipt()
        try:
            p, q = msg.pose.pose.position, msg.pose.pose.orientation
            stamp = time_to_ns(msg.header.stamp)
            values = (float(p.x), float(p.y), float(q.x), float(q.y), float(q.z), float(q.w))
            if (msg.header.frame_id != self.config["frame_id"] or not all(math.isfinite(v) for v in values)
                    or abs(sum(v*v for v in values[2:])-1.) > 1e-3
                    or not -FRESHNESS_NS <= receipt[0]-stamp <= FRESHNESS_NS):
                raise ValueError("invalid selected pose")
            if self.last_pose_stamp is not None and stamp <= self.last_pose_stamp:
                previous = next((pose for pose in self.poses if pose[0] == stamp), None)
                if previous is not None and previous[1] == values:
                    return
                raise ValueError("selected pose conflict or regression")
            self.last_pose_stamp = stamp
            self.poses.append((stamp, values, receipt))
        except (ValueError, TypeError, OverflowError):
            self.poses.clear()
            self._cancel_current("invalid selected pose")

    def _live_error(self, pending, *, activation=False):
        cmd, now = pending.command, self.now()
        if not self._same_stream(cmd):
            return 'invalid or changed time origin'
        if now > time_to_ns(cmd.expires_at) or self.steady_now() > pending.wall_expires_ns:
            return "preparation expired"
        context, state = self.context, self.state
        if (context is None or not context.valid or envelope_identity(context) != envelope_identity(cmd)
                or not self._fresh(time_to_ns(context.stamp), self.context_receipt, now)):
            return "stale or changed epoch context"
        if (state is None or not state.state_valid or not state.weights_valid
                or state.algorithm_profile != "robust_gaussian_v1" or not state.run_id_valid or state.run_id != self.run_id
                or not self._fresh(time_to_ns(state.stamp), self.state_receipt, now)
                or not all(math.isfinite(v) for v in (state.sensor_weight, state.gaussian_weight, state.affine_weight))
                or (state.failsafe_valid and state.failsafe)):
            return "stale or invalid state"
        previous = state.STATE_ESCAPE_REPULSE if cmd.redesign else state.STATE_VERIFY_EXTREMUM
        allowed = {state.STATE_DESIGN_OR_MERGE_FILL} if activation else {previous, state.STATE_DESIGN_OR_MERGE_FILL}
        if state.state not in allowed or (state.state == state.STATE_DESIGN_OR_MERGE_FILL
                and (not state.previous_state_valid or state.previous_state != previous)):
            return "state does not authorize preparation purpose"
        pose = next((entry for entry in reversed(self.poses) if entry[0] <= now), None)
        if pose is None or not self._fresh(pose[0], pose[2], now):
            return "stale selected pose"
        snap = cmd.snapshot
        if math.hypot(pose[1][0]-snap.center_x_m, pose[1][1]-snap.center_y_m) > snap.neighborhood_radius_m+1e-12:
            return "candidate neighborhood departed"
        if self.node.fill_registry.generation != cmd.expected_registry_generation:
            return "registry generation changed"
        return ""

    def _result(self, cmd, outcome, reason="", pending=None):
        msg = copy_envelope(FillResult(), cmd)
        set_time(msg.stamp, self.now())
        for field in ("candidate_id", "objective_revision", "command_sequence", "preparation_id",
                      "expected_registry_generation", "evidence_sha256", "expires_at", "return_state"):
            setattr(msg, field, deepcopy(getattr(cmd, field)))
        msg.result, msg.reason = outcome, reason
        msg.registry_generation = self.node.fill_registry.generation
        msg.prepared_sha256 = cmd.prepared_sha256 if pending is None else pending.prepared_hash
        if pending is not None:
            set_time(msg.prepared_at, pending.prepared_at_ns)
        msg.committed_sha256 = result_sha256(msg)
        return msg

    def _publish(self, result):
        try:
            self.publisher.publish(deepcopy(result))
            return True
        except RuntimeError as exc:
            # Every command outcome is cached before publication. A DDS error
            # neither rolls back a commit nor consumes another ID on retry.
            self.node.get_logger().error(f'fill result publication failed: {exc}')
            return False

    def _save_result(self, sequence, result):
        command_hash, _ = self.commands[sequence]
        self.commands[sequence] = (command_hash, deepcopy(result))
        self._publish(result)

    @staticmethod
    def _release_support(pending):
        # Keep identity/hash/outcome tombstones, not thousands of obsolete wire observations.
        pending.command.snapshot = CandidateSnapshot()
        pending.proposal = None

    def _cancel_current(self, reason):
        pending = self.current
        if pending is None or pending.status in (FillResult.ACTIVATED, FillResult.CANCELLED,
                                                 FillResult.EXPIRED, FillResult.REJECTED):
            return
        pending.status = FillResult.EXPIRED if "expired" in reason else FillResult.CANCELLED
        response = self._result(pending.command, pending.status, reason, pending)
        # A PREPARED response already emitted for PREPARE remains immutable.
        if self.commands[pending.command.command_sequence][1] is None:
            self._save_result(pending.command.command_sequence, response)
        else:
            self._publish(response)
        self.current = None
        self._release_support(pending)
        if self.future_token == pending.command.preparation_id and self.future is not None:
            self.future.cancel()

    def _validate_snapshot_proof(self, snap, proof, cmd):
        from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
        recurrent_proof_payload(proof)
        confirmation, diagnostic = proof.confirmation, proof.diagnostic
        if self.context is None:
            raise ValueError('recurrent proof lacks current epoch context')
        errors = recurrent_nomination_errors(confirmation, diagnostic,
            expected_source_pose_topic=self.config['pose_topic'],
            epoch_start_ns=time_to_ns(self.context.started_at))
        if errors:
            raise ValueError('invalid recurrent nomination: '+ '; '.join(errors))
        if (envelope_identity(confirmation) != envelope_identity(snap)
                or confirmation.confirmation_sequence != snap.detector_confirmation_sequence
                or snap.metric_mode != confirmation.metric_mode
                or time_to_ns(snap.confirmation_stamp) != time_to_ns(confirmation.source_stamp)
                or (snap.center_x_m, snap.center_y_m) != (confirmation.center_x_m, confirmation.center_y_m)
                or snap.convergence_score_valid != confirmation.convergence_score_valid
                or snap.legacy_r_mean_valid != confirmation.legacy_r_mean_valid
                or snap.convergence_score_m != confirmation.convergence_score_m):
            raise ValueError('recurrent nomination differs from frozen snapshot')
        source, publication, accepted, frozen, command_stamp = map(time_to_ns, (
            confirmation.source_stamp, confirmation.stamp, snap.accepted_at, snap.stamp, cmd.stamp))
        if not source <= publication <= accepted <= frozen <= command_stamp <= self.now():
            raise ValueError('recurrent snapshot acceptance/publication chronology')
        if accepted-source > FRESHNESS_NS:
            raise ValueError('recurrent nomination was stale at original acceptance')

    def _input(self, cmd, proof=None):
        snap = cmd.snapshot
        recurrent = self.evidence_policy == RECURRENT_TRAPPING_POLICY
        if recurrent:
            self._validate_snapshot_proof(snap, proof, cmd)
            evidence_hash = recurrent_snapshot_sha256(snap, proof)
        else:
            if proof is not None:
                raise ValueError('recurrent proof supplied to angular policy')
            evidence_hash = snapshot_sha256(snap)
        finite = (snap.center_x_m, snap.center_y_m, snap.neighborhood_radius_m, snap.centroid_tolerance_m,
                  snap.candidate_cost_estimate, snap.candidate_cost_mad, snap.candidate_cost_uncertainty,
                  snap.candidate_cost_lower, snap.candidate_cost_upper, snap.information_amplitude,
                  snap.information_disagreement, snap.information_floor)
        if (envelope_identity(snap) != envelope_identity(cmd) or snap.candidate_id != cmd.candidate_id
                or snap.objective_revision != cmd.objective_revision or snap.snapshot_revision <= 0
                or snap.evidence_sha256 != cmd.evidence_sha256 or evidence_hash != cmd.evidence_sha256
                or not all(math.isfinite(v) for v in finite) or min(snap.neighborhood_radius_m, snap.centroid_tolerance_m) <= 0
                or min(snap.candidate_cost_mad, snap.candidate_cost_uncertainty,
                       snap.information_disagreement) < 0
                or snap.information_floor <= 0
                or (not recurrent and (not snap.informative
                    or snap.information_amplitude <= max(3*snap.information_disagreement, snap.information_floor)))
                or snap.candidate_cost_upper >= -snap.information_floor
                or snap.candidate_cost_lower > snap.candidate_cost_estimate or snap.candidate_cost_estimate > snap.candidate_cost_upper
                or snap.completed_revolutions != 3 or len(snap.observations) > 4000):
            raise ValueError("invalid immutable candidate snapshot")
        lengths = [len(getattr(snap, field)) for field in (
            "revolution_start", "revolution_end", "revolution_sample_start", "revolution_sample_end")]
        if (lengths != [3]*4 or len(snap.observation_filter_state) != len(snap.observations)
                or len(snap.observation_filter_stamp) != len(snap.observations)):
            raise ValueError("snapshot support index lengths")
        lo, hi = time_to_ns(snap.evidence_start), time_to_ns(snap.evidence_end)
        if self.context is None or lo < time_to_ns(self.context.started_at) or not lo < hi <= self.now():
            raise ValueError("snapshot time bounds")
        last_index = 0
        for start, end, left, right in zip(snap.revolution_start, snap.revolution_end,
                                         snap.revolution_sample_start, snap.revolution_sample_end):
            if not lo <= time_to_ns(start) < time_to_ns(end) <= hi or not last_index <= left < right <= len(snap.observations):
                raise ValueError("snapshot cycle bounds")
            last_index = right
        stamps = [time_to_ns(obs.source_stamp) for obs in snap.observations]
        if not stamps or stamps[0] > lo or stamps[-1] < hi:
            raise ValueError("snapshot boundary brackets missing")
        assigned_indices = set()
        for start, end, left, right in zip(snap.revolution_start, snap.revolution_end,
                                         snap.revolution_sample_start, snap.revolution_sample_end):
            assigned_indices.update(range(left, right))
            assigned = [i for i, stamp in enumerate(stamps)
                        if time_to_ns(start) <= stamp < time_to_ns(end)]
            if assigned != list(range(left, right)):
                raise ValueError("snapshot actual cycle assignment")
        if (len({obs.observation_id for obs in snap.observations}) != len(stamps)
                or len({obs.source_sequence for obs in snap.observations}) != len(stamps)):
            raise ValueError("snapshot duplicate observation identity")
        samples = []
        origin = time_to_ns(cmd.time_origin)
        for index, (obs, state, state_stamp) in enumerate(zip(
                snap.observations, snap.observation_filter_state, snap.observation_filter_stamp)):
            stamp = time_to_ns(obs.source_stamp)
            if (obs.schema_version != 2 or obs.run_id != cmd.run_id or obs.stream_contract_id != cmd.stream_contract_id
                    or obs.frame_id != cmd.frame_id or time_to_ns(obs.time_origin) != origin
                    or not obs.synchronized_valid or not obs.raw_cost_valid or not obs.sensor_transform_observed
                    or obs.observation_id <= 0 or obs.source_sequence <= 0
                    or not time_to_ns(self.context.started_at) <= stamp <= self.now()
                    or state not in (1, 2, 3, 4, 5) or time_to_ns(state_stamp) < time_to_ns(obs.admission_stamp)
                    or time_to_ns(obs.admission_stamp) < max(stamp, time_to_ns(obs.cost_source_stamp),
                        time_to_ns(obs.pose_right_stamp), time_to_ns(obs.encoder_right_stamp), time_to_ns(obs.receipt_stamp))
                    or relative_stamp_ns(origin, obs.legacy_cost_source_timestamp_sec) != stamp
                    or not math.isfinite(obs.sync_error_sec) or not 0 <= obs.sync_error_sec <= .05
                    or (index in assigned_indices and math.hypot(
                        obs.base_x_m-snap.center_x_m, obs.base_y_m-snap.center_y_m)
                        > snap.neighborhood_radius_m+1e-12)):
                raise ValueError("invalid synchronized snapshot observation")
            samples.append(BasinSample(stamp*1e-9, obs.base_x_m, obs.base_y_m, obs.base_yaw_rad,
                                       math.nan, False, obs.raw_cost, math.nan, False, int(state)))
        # Brackets are immutable interpolation evidence, not additional raw fit samples.
        samples = validate_samples(samples, min(4000, self.node.fill_registry.config.maximum_cluster_samples))
        for bound in (*snap.revolution_start, *snap.revolution_end):
            ns = time_to_ns(bound)
            right = bisect_left(stamps, ns)
            if right >= len(samples):
                raise ValueError('unbracketed candidate boundary')
            if stamps[right] == ns:
                x, y = samples[right].x, samples[right].y
            else:
                if right == 0:
                    raise ValueError('unbracketed candidate boundary')
                left = right-1
                fraction = (ns-stamps[left])/(stamps[right]-stamps[left])
                x = (1-fraction)*samples[left].x + fraction*samples[right].x
                y = (1-fraction)*samples[left].y + fraction*samples[right].y
            if math.hypot(x-snap.center_x_m, y-snap.center_y_m) > snap.neighborhood_radius_m+1e-12:
                raise ValueError('candidate boundary neighborhood departed')
        samples = tuple(sample for index, sample in enumerate(samples) if index in assigned_indices)
        if recurrent:
            from ros_esc.supervisor_node.moving_evidence import snapshot_raw_evidence
            evidence = snapshot_raw_evidence(snap, evidence_policy=self.evidence_policy,
                mad_scale=float(self.node.get_parameter('candidate_cost_mad_scale').value))
            if not evidence.ready:
                raise ValueError('invalid recurrent raw snapshot: '+evidence.reason)
        target = (int(cmd.target_fill_id), int(cmd.target_cluster_id), int(cmd.target_revision)) if cmd.redesign else None
        if (cmd.redesign and (min(target) <= 0 or cmd.return_state != 5)) or (not cmd.redesign and (
                any((cmd.target_fill_id, cmd.target_cluster_id, cmd.target_revision)) or cmd.return_state != 4)):
            raise ValueError("invalid preparation target or return state")
        return PreparationInput(samples, self.node.fill_registry.snapshot(), self.node.estimator_config,
                                self.node.design_config, self.node.fill_registry.config,
                                (time_to_ns(snap.confirmation_stamp)-origin)*1e-9, snap.candidate_cost_lower,
                                self.node.candidate_informed_fill_amplitude_scale,
                                self.node.candidate_informed_fill_enabled, self.node.max_fills,
                                target)

    def recurrent_command_cb(self, message):
        """Unwrap the selected self-contained certificate into the one owner."""
        from ros_esc_interfaces.msg import RecurrentFillCommand
        if type(message) is not RecurrentFillCommand:
            return
        self.command_cb(message.command, proof=message)

    def command_cb(self, cmd, proof=None):
        receipt = self._receipt()
        if self.closed or not self._same_stream(cmd):
            return
        sequence = int(cmd.command_sequence)
        try:
            if self.evidence_policy == RECURRENT_TRAPPING_POLICY:
                proof_payload = recurrent_proof_payload(proof)
            elif proof is None:
                proof_payload = None
            else:
                raise ValueError('recurrent proof supplied to angular policy')
        except (ValueError, TypeError, AttributeError) as exc:
            self._publish(self._result(cmd, FillResult.REJECTED, str(exc)))
            return
        payload = message_payload(cmd, exclude=("stamp",))
        fingerprint = hash_payload(payload if proof_payload is None else
                                   dict(command=payload, proof=proof_payload))
        if sequence in self.commands:
            previous, result = self.commands[sequence]
            if fingerprint != previous:
                self._cancel_current("conflicting command sequence")
                self._publish(self._result(cmd, FillResult.REJECTED, "conflicting command sequence"))
            elif result is not None:
                self._publish(result)
            return
        if sequence <= self.last_command_sequence or sequence <= 0 or len(self.commands) >= MAX_COMMANDS:
            self._publish(self._result(cmd, FillResult.REJECTED, "command order or capacity"))
            return
        self.last_command_sequence = sequence
        self.commands[sequence] = (fingerprint, None)
        key = int(cmd.preparation_id)
        pending = self.preparations.get(key)
        created = committed = False
        try:
            if min(cmd.search_epoch, cmd.candidate_id, cmd.objective_revision, key) <= 0:
                raise ValueError("invalid candidate identity")
            if cmd.operation == FillCommand.PREPARE:
                if pending is not None or self.current is not None or (self.future is not None and not self.future.done()):
                    raise ValueError("preparation identity reused or worker busy")
                remaining = time_to_ns(cmd.expires_at)-receipt[0]
                if remaining <= 0:
                    raise ValueError("preparation already expired")
                pending = PendingPreparation(clone_ros_message(cmd), wall_expires_ns=receipt[1]+remaining,
                                             proof_payload=proof_payload)
                self.preparations[key] = pending
                created = True
                err = self._live_error(pending)
                if err:
                    raise ValueError(err)
                inp = self._input(cmd, proof=proof)
                if (hasattr(self.node, 'observability_configuration_published')
                        and not self.node.observability_configuration_published):
                    self.node._publish_configuration_event()
                    self.node.observability_configuration_published = True
                self.current = pending
                self.future_token = key
                self.future = self.pool.submit(compute_fill_proposal, inp)
                return
            if pending is None:
                raise ValueError("unknown preparation")
            original = pending.command
            if proof_payload != pending.proof_payload:
                raise ValueError('preparation recurrent proof changed')
            immutable_fields = ("candidate_id", "objective_revision", "expected_registry_generation", "evidence_sha256",
                                "target_fill_id", "target_cluster_id", "target_revision", "redesign", "return_state")
            if (envelope_identity(cmd) != envelope_identity(original)
                    or any(getattr(cmd, field) != getattr(original, field) for field in immutable_fields)
                    or time_to_ns(cmd.expires_at) != time_to_ns(original.expires_at)):
                raise ValueError("preparation binding changed")
            if cmd.operation not in (FillCommand.ACTIVATE, FillCommand.CANCEL):
                raise ValueError("unknown operation")
            if pending.status == FillResult.ACTIVATED:
                result = deepcopy(pending.active_result)
                result.command_sequence = sequence
                result.result = FillResult.ALREADY_ACTIVATED
                set_time(result.stamp, self.now())
                result.committed_sha256 = result_sha256(result)
                self._save_result(sequence, result)
                return
            if cmd.operation == FillCommand.CANCEL:
                if cmd.prepared_sha256 and cmd.prepared_sha256 != pending.prepared_hash:
                    raise ValueError("cancel prepared hash mismatch")
                if self.current is pending:
                    self._cancel_current("supervisor cancelled preparation")
                if pending.status == 0:
                    pending.status = FillResult.CANCELLED
                self._save_result(sequence, self._result(cmd, pending.status, "preparation terminal", pending))
                return
            if cmd.operation != FillCommand.ACTIVATE or pending.status != FillResult.PREPARED:
                raise ValueError("preparation is not activatable")
            if not cmd.prepared_sha256 or cmd.prepared_sha256 != pending.prepared_hash:
                raise ValueError("prepared hash mismatch")
            err = self._live_error(pending, activation=True)
            if err:
                self._cancel_current(err)
                raise ValueError(err)
            proposal = pending.proposal
            registry = self.node.fill_registry
            plan = registry.stage_commit(dict(proposal.version_values), proposal.samples,
                cluster_id=proposal.cluster_id, exact_target=proposal.exact_target,
                expected_generation=cmd.expected_registry_generation, strict=True)
            now = self.now()
            result = self._result(cmd, FillResult.ACTIVATED, pending=pending)
            result.fill = version_message(plan.active, now, cmd.frame_id)
            result.has_superseded_fill = plan.superseded is not None
            if plan.superseded is not None:
                result.superseded_fill = version_message(plan.superseded, now, cmd.frame_id)
            result.registry_generation = registry.generation+1
            result.registry_digest_before = fill_registry_digest([
                version_message(cluster.active_fill, now, cmd.frame_id) for cluster in registry.active_clusters])
            result.registry_digest_after = fill_registry_digest([
                version_message(cluster.active_fill, now, cmd.frame_id) for cluster in plan.clusters])
            set_time(result.committed_at, now)
            result.committed_sha256 = result_sha256(result)
            # Staging/hashing can take time; final live validation is immediately
            # adjacent to the serialized registry swap, with no await or publish.
            err = self._live_error(pending, activation=True)
            if err:
                self._cancel_current(err)
                raise ValueError(err)
            registry.commit_staged(plan)
            committed = True
            pending.status, pending.active_result = FillResult.ACTIVATED, deepcopy(result)
            self.current = None
            # Commit is authoritative even if a later DDS/mirror publication fails.
            self.commands[sequence] = (fingerprint, deepcopy(result))
            self._publish(result)
            self.node.fill_count, self.node.has_filled = registry.active_count, registry.active_count > 0
            self.node.last_fill_time = plan.active.source_timestamp
            self.node.fill_centers = [np.array(cluster.active_fill.center, copy=True) for cluster in registry.active_clusters]
            for version in (plan.superseded, plan.active):
                if version is not None:
                    self.node._publish_robust_fill(version, frame_id=cmd.frame_id)
            self.node._publish_compatibility_fill(plan.active)
            if hasattr(self.node, '_publish_event'):
                if plan.superseded is not None:
                    self.node._publish_event(AlgorithmEvent.EVENT_FILL_SUPERSEDED,
                        'atomic moving fill supersession', plan.superseded.source_timestamp,
                        ['cluster_id', 'revision', 'superseded_fill_id', 'new_fill_id'],
                        [plan.superseded.cluster_id, plan.superseded.revision,
                         plan.superseded.fill_id, plan.active.fill_id], fill_id=plan.superseded.fill_id)
                self.node._publish_event(
                    AlgorithmEvent.EVENT_FILL_MERGED if plan.superseded is not None else AlgorithmEvent.EVENT_FILL_CREATED,
                    'atomic moving fill activation', plan.active.source_timestamp,
                    ['cluster_id', 'revision', 'registry_generation', 'amplitude_cost_units', 'sample_count'],
                    [plan.active.cluster_id, plan.active.revision, registry.generation,
                     plan.active.amplitude, plan.active.sample_count], fill_id=plan.active.fill_id)
            self._release_support(pending)
            return
        except (ValueError, TypeError, KeyError, OverflowError, RuntimeError, np.linalg.LinAlgError) as exc:
            if committed:
                # The cached commit remains retryable; never turn it into rejection.
                self._release_support(pending)
                self.node.get_logger().error(f"accepted fill publication failed: {exc}")
                return
            if created and pending is not None:
                pending.status = FillResult.REJECTED
                if self.current is pending:
                    self.current = None
            self._save_result(sequence, self._result(cmd, FillResult.REJECTED, str(exc), pending))
            if created and pending is not None:
                self._release_support(pending)

    def poll(self):
        if self.closed:
            return
        now = self.now()
        if self.last_now is not None and now < self.last_now:
            self._cancel_current("ROS clock rollback")
            self.poses.clear()
            self.last_pose_stamp = None
        self.last_now = now
        if self.current is not None:
            err = self._live_error(self.current)
            if err:
                self._cancel_current(err)
        if self.future is None or not self.future.done():
            return
        future, key = self.future, self.future_token
        self.future = self.future_token = None
        pending = self.preparations.get(key)
        if pending is None or self.current is not pending or pending.status != 0:
            return
        try:
            proposal = future.result()
            err = self._live_error(pending)
            if err or proposal.registry_generation != self.node.fill_registry.generation:
                raise ValueError(err or "registry changed during preparation")
            pending.proposal = proposal
            pending.prepared_at_ns = now
            payload = dict(command=message_payload(pending.command, exclude=("stamp", "operation", "command_sequence", "prepared_sha256")),
                           values=message_payload(dict(proposal.version_values)),
                           support=[sample_payload(sample) for sample in proposal.samples],
                           target=proposal.exact_target, generation=proposal.registry_generation,
                           estimator=asdict(self.node.estimator_config), designer=asdict(self.node.design_config),
                           registry=asdict(self.node.fill_registry.config))
            if pending.proof_payload is not None:
                payload['proof'] = pending.proof_payload
            pending.prepared_hash = hash_payload(payload)
            pending.status = FillResult.PREPARED
            response = self._result(pending.command, FillResult.PREPARED, pending=pending)
            preview = FillVersion(fill_id=0, cluster_id=proposal.cluster_id or 0, revision=0,
                                  active=False, **dict(proposal.version_values))
            response.fill = version_message(preview, now, pending.command.frame_id)
            response.committed_sha256 = result_sha256(response)
            self._save_result(pending.command.command_sequence, response)
        except Exception as exc:  # Worker errors become a terminal result; no worker can publish.
            pending.status = FillResult.REJECTED
            self.current = None
            self._save_result(pending.command.command_sequence,
                              self._result(pending.command, FillResult.REJECTED, str(exc), pending))
            self._release_support(pending)

    def close(self):
        self.closed = True
        self._cancel_current("node shutdown")
        self.pool.shutdown(wait=False, cancel_futures=True)
