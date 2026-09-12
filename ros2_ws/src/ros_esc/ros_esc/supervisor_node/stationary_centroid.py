"""Typed Arm B input adapter within the existing stationary supervisor."""

from copy import deepcopy
from dataclasses import dataclass
import math
import time

from rclpy.clock import Clock, ClockType
from std_msgs.msg import Bool
import ros_esc_interfaces.msg as interface_messages
from ros_esc_interfaces.msg import Timekeeper
from ros_esc.convergence_detector_node.centroid_contract import CENTROID_METRIC_MODES
from ros_esc.stationary_fill_protocol import (
    centroid_configuration_errors, stationary_contract, stationary_diagnostic_errors,
    stationary_diagnostic_origin_errors,
    stationary_request_errors, stationary_request_sha256,
)
from ros_esc.supervisor_node.state_machine import State, candidate_fill_evidence_from_summary
from ros_esc.v2_lifecycle import FRESHNESS_NS, MAX_COMMANDS, hash_payload, message_payload
from ros_esc.v2_stream import relative_stamp_ns, set_time, time_to_ns


@dataclass(frozen=True)
class PendingConfirmation:
    message: object
    receipt_ns: int
    steady_ns: int
    search_entry_ns: int


@dataclass(frozen=True)
class AcceptedConfirmation:
    message: object
    received_ns: int
    accepted_ns: int
    steady_ns: int
    search_entry_ns: int


class StationaryCentroidAdapter:
    def __init__(self, node):
        self.node = node
        self.metric_mode = node._string('convergence_metric_mode')
        self.contract = stationary_contract(self.metric_mode)
        self.request_type = getattr(interface_messages, self.contract['request_type'].rsplit('/', 1)[-1])
        self.diagnostics_type = getattr(interface_messages, self.contract['diagnostics_type'].rsplit('/', 1)[-1])
        self.pose_topic = node.resolve_topic_name(node._string('pose_topic'))
        self.frame_id = 'odom'  # Inherited stationary fill/result frame contract.
        self.maximum_gap_sec = node._positive_float('centroid_maximum_gap_sec')
        self.pose_freshness_sec = node._positive_float('centroid_pose_stale_sec')
        self.configuration = (tuple(node._positive_float(name) for name in (
            'centroid_window_sec', 'centroid_epsilon_m', 'centroid_maximum_radius_m'))
            if self.metric_mode in CENTROID_METRIC_MODES else None)
        request_topic = node.resolve_topic_name(node._string(self.contract['request_topic_parameter']))
        if request_topic != self.contract['request_topic']:
            raise ValueError('stationary fill request topic differs from fixed contract')
        timekeeper_topic = node._string('timekeeper_topic')
        if not timekeeper_topic.strip():
            raise ValueError('stationary centroid requires selected timekeeper_topic')
        self.ready_required = bool(node.get_parameter('recording_ready_required').value)
        self.ready_stale_ns = round(node._positive_float('recording_ready_stale_sec') * 1e9)
        self.recording_ready = False
        self.ready_receipt_ns = None
        self.origin_ns = None
        self.origin_fault = False
        self.pending_confirmation = None
        self.accepted = None
        self.trigger_pending = False
        self.pending_design = None
        self.request_sequence = 0
        self.requests = {}
        self.confirmations = {}
        self.last_detector_epoch = 0
        self.last_confirmation_sequence = 0
        self.accepted_search_entry = None
        self.last_now_ns = None
        self.last_reason = ''
        self.request_publisher = node.create_publisher(self.request_type, request_topic, 10)
        self.subscriptions = [
            node.create_subscription(self.diagnostics_type,
                node._string(self.contract['diagnostics_topic_parameter']), self.confirmation, 10),
            node.create_subscription(Timekeeper, timekeeper_topic, self.timekeeper, 10),
        ]
        if self.ready_required:
            self.subscriptions.append(node.create_subscription(
                Bool, node._string('recording_ready_topic'), self.readiness, 10))
        self.timer = node.create_timer(.05, self.poll, clock=Clock(clock_type=ClockType.STEADY_TIME))

    def now(self):
        return self.node.get_clock().now().nanoseconds

    def search_entry(self):
        return round(self.node.machine.state_entered_sec * 1e9)

    def ready(self):
        return bool(not self.ready_required or (
            self.recording_ready and self.ready_receipt_ns is not None
            and 0 <= time.monotonic_ns() - self.ready_receipt_ns <= self.ready_stale_ns))

    def _drop_pending(self, reason):
        self.last_reason = str(reason)
        self.pending_confirmation = None
        self.trigger_pending = False
        self.node.pending_convergence_confirmation_receipt_sec = None

    def _fail(self, reason):
        self._drop_pending(reason)
        self.pending_design = None
        now_sec = self.now() * 1e-9
        self.node._force_failsafe(now_sec, str(reason))
        self.node._publish_state_and_command(now_sec)

    def timekeeper(self, message):
        try:
            if message.mode != 'sim time':
                raise ValueError('stationary Timekeeper mode invalid')
            origin = relative_stamp_ns(0, message.start_time)
            if self.origin_fault or (self.origin_ns is not None and self.origin_ns != origin):
                raise ValueError('stationary Timekeeper origin changed')
            self.origin_ns = origin
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            self.origin_fault = True
            self._fail(str(error))
            return
        self.poll()

    def readiness(self, message):
        self.recording_ready = bool(message.data)
        self.ready_receipt_ns = time.monotonic_ns()
        if not self.recording_ready:
            self._drop_pending('recording not ready')
            if self.accepted is not None and self.node.machine.state != State.SEARCH:
                self._fail('recording authorization revoked')

    def confirmation(self, message):
        received, steady = self.now(), time.monotonic_ns()
        if not isinstance(message, self.diagnostics_type):
            self.last_reason = 'wrong selected stationary diagnostic type'
            return
        if not message.confirmed:
            return
        try:
            fingerprint = hash_payload(message_payload(message))
            errors = stationary_diagnostic_errors(
                [message], expected_source_pose_topic=self.pose_topic,
                supervisor_run_ids={self.node.run_id}, maximum_source_gap_sec=self.maximum_gap_sec,
                allow_clock_admission=True, expected_frame_id=self.frame_id,
                pose_freshness_sec=self.pose_freshness_sec,
                expected_metric_mode=self.metric_mode)
            if self.configuration is not None:
                errors += centroid_configuration_errors(message, *self.configuration,
                    expected_metric_mode=self.metric_mode)
            if errors or not (message.eligible and message.history_valid and message.metric_valid
                              and message.source_valid and message.confinement_valid):
                raise ValueError('; '.join(errors) or 'centroid confirmation lacks full support')
            key = (int(message.search_epoch), int(message.confirmation_sequence))
            if key in self.confirmations:
                if self.confirmations[key] != fingerprint:
                    if self.pending_confirmation is not None:
                        self._drop_pending('conflicting centroid confirmation')
                    raise ValueError('conflicting centroid confirmation')
                return  # Exact repetition cannot refresh or resurrect evidence.
            if len(self.confirmations) >= MAX_COMMANDS:
                raise ValueError('stationary confirmation capacity exceeded')
            self.confirmations[key] = fingerprint
            if (self.node.machine.state != State.SEARCH or not self.ready() or self.origin_fault
                    or key[0] <= self.last_detector_epoch or key[1] <= self.last_confirmation_sequence
                    or self.accepted_search_entry == self.search_entry()):
                raise ValueError('centroid confirmation lacks current SEARCH authority')
            publication = time_to_ns(message.stamp)
            if abs(publication - received) > FRESHNESS_NS:
                raise ValueError('centroid confirmation publication stale or excessively future')
            # The detector counter is local; bind its source entry to the actual
            # supervisor SEARCH entry, allowing only float-to-ns representation.
            if abs(time_to_ns(message.epoch_started_at) - self.search_entry()) > 1000:
                raise ValueError('centroid confirmation SEARCH entry mismatch')
            if self.pending_confirmation is not None:
                raise ValueError('stationary confirmation already pending')
            self.pending_confirmation = PendingConfirmation(
                deepcopy(message), received, steady, self.search_entry())
            self.poll()
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            self.last_reason = str(error)

    def confirmation_ready(self, now_ns):
        accepted = self.accepted
        return bool(self.trigger_pending and accepted is not None and self.ready()
                    and not self.origin_fault and self.origin_ns is not None
                    and self.node.machine.state == State.SEARCH
                    and accepted.search_entry_ns == self.search_entry()
                    and 0 <= now_ns - accepted.received_ns <= FRESHNESS_NS
                    and 0 <= now_ns - time_to_ns(accepted.message.stamp) <= FRESHNESS_NS
                    and 0 <= time.monotonic_ns() - accepted.steady_ns <= FRESHNESS_NS)

    def candidate_center(self):
        if self.accepted is None:
            return None
        return (self.accepted.message.center_x_m, self.accepted.message.center_y_m)

    def poll(self):
        now, steady = self.now(), time.monotonic_ns()
        previous, self.last_now_ns = self.last_now_ns, now
        if now < 0 or (previous is not None and now < previous):
            self._fail('stationary supervisor clock moved backward')
            return
        if self.node.stop_requested or self.node.controller_fault:
            self._fail('stationary supervisor stop or controller fault')
            return
        if self.origin_fault:
            return
        if not self.ready():
            self._drop_pending('recording not ready')
            if self.accepted is not None and self.node.machine.state not in (State.SEARCH, State.FAILSAFE):
                self._fail('recording authorization expired')
            return
        pending = self.pending_confirmation
        if pending is not None:
            publication = time_to_ns(pending.message.stamp)
            if (self.node.machine.state != State.SEARCH or pending.search_entry_ns != self.search_entry()
                    or not 0 <= now - pending.receipt_ns <= FRESHNESS_NS
                    or not 0 <= steady - pending.steady_ns <= FRESHNESS_NS):
                self._drop_pending('centroid confirmation original admission lease expired or revoked')
            elif publication <= now and self.origin_ns is not None:
                if (now - publication > FRESHNESS_NS
                        or stationary_diagnostic_origin_errors(pending.message, self.origin_ns,
                            expected_metric_mode=self.metric_mode)
                        or not self.node.latest_pose_valid
                        or self.node.latest_pose_frame_id != self.frame_id):
                    self._drop_pending('centroid confirmation origin or selected pose invalid')
                else:
                    self.accepted = AcceptedConfirmation(pending.message, pending.receipt_ns,
                        now, pending.steady_ns, pending.search_entry_ns)
                    self.last_detector_epoch = int(pending.message.search_epoch)
                    self.last_confirmation_sequence = int(pending.message.confirmation_sequence)
                    self.accepted_search_entry = pending.search_entry_ns
                    self.pending_confirmation = None
                    self.trigger_pending = True
                    self.node.pending_convergence_confirmation_receipt_sec = pending.receipt_ns * 1e-9
                    self.last_reason = ''
        if self.trigger_pending and not self.confirmation_ready(now):
            self._drop_pending('centroid confirmation original admission lease expired')
        if self.pending_design is not None:
            self._dispatch(now)

    def on_transition(self, transition):
        if transition.current == State.SEARCH:
            self._drop_pending('new SEARCH entry')
            self.accepted = None
            self.pending_design = None
        elif transition.current == State.VERIFY_EXTREMUM:
            self.trigger_pending = False
            self.pending_confirmation = None
        elif transition.current == State.DESIGN_OR_MERGE_FILL:
            self.trigger_pending = False
            deadline = self.search_entry() + round(self.node.machine.config.fill_design_timeout_sec * 1e9)
            self.pending_design = (deadline, bool(self.node.machine.design_returns_to_assist))
            # Publish the actual stopped state before the cross-topic request.
            self.node._publish_state_and_command(self.now() * 1e-9)
            self._dispatch(self.now())
        elif transition.current in (State.GOAL_HOLD, State.FAILSAFE):
            self._drop_pending('stationary authority terminated')
            self.pending_design = None

    def _dispatch(self, now_ns):
        if self.pending_design is None:
            return
        deadline, redesign = self.pending_design
        if self.node.machine.state != State.DESIGN_OR_MERGE_FILL:
            self.pending_design = None
            return
        if now_ns >= deadline:
            self._fail('fill design timeout while awaiting stationary request clock')
            return
        if self.accepted is None or self.origin_ns is None or self.origin_fault or not self.ready():
            self._fail('stationary fill request has no accepted candidate authority')
            return
        correlation = (now_ns - self.origin_ns) * 1e-9
        if any(math.isclose(correlation, old.source_timestamp, rel_tol=0., abs_tol=1e-9)
               for old in self.requests.values()):
            return  # Wait for a genuine clock tick within the original deadline.
        if len(self.requests) >= MAX_COMMANDS:
            self._fail('stationary fill request capacity exceeded')
            return
        request = self.request_type()
        request.schema_version, request.request_sequence = 1, self.request_sequence + 1
        set_time(request.stamp, now_ns)
        set_time(request.time_origin, self.origin_ns)
        set_time(request.expires_at, deadline)
        set_time(request.confirmation_received_at, self.accepted.received_ns)
        set_time(request.confirmation_accepted_at, self.accepted.accepted_ns)
        request.confirmation = deepcopy(self.accepted.message)
        request.source_timestamp = correlation
        request.operation = request.TARGETED_REDESIGN if redesign else request.CREATE
        if redesign:
            target = self.node.machine.active_escape_fill_id
            match = next(((cluster, record) for cluster, record in self.node.active_fill_records.items()
                          if record['fill_id'] == target), None)
            if match is None:
                self._fail('stationary redesign has no exact active fill')
                return
            request.target_cluster_id, record = match
            request.target_fill_id, request.target_revision = record['fill_id'], record['revision']
        elif self.node.machine.config.candidate_informed_fill_enabled:
            evidence = candidate_fill_evidence_from_summary(self.node.machine.pending_candidate_cost)
            request.candidate_evidence_valid = True
            request.candidate_cost_estimate, request.candidate_cost_mad = evidence.estimate, evidence.mad
            request.candidate_cost_uncertainty, request.candidate_cost_lower = evidence.uncertainty, evidence.lower
            request.candidate_rotation_count = evidence.rotation_count
        request.request_sha256 = stationary_request_sha256(request)
        errors = stationary_request_errors(request, self.node.run_id, self.frame_id, self.pose_topic,
            self.origin_ns, self.maximum_gap_sec, self.pose_freshness_sec,
            expected_metric_mode=self.metric_mode)
        if errors:
            self._fail('; '.join(errors))
            return
        self.requests[request.request_sequence] = deepcopy(request)
        self.request_sequence = request.request_sequence
        self.pending_design = None
        self.node.machine.register_fill_request(request.source_timestamp)
        self.request_publisher.publish(request)

    def result_known(self, source_timestamp):
        return bool(math.isfinite(source_timestamp) and any(
            math.isclose(source_timestamp, request.source_timestamp, rel_tol=0., abs_tol=1e-9)
            for request in self.requests.values()))
