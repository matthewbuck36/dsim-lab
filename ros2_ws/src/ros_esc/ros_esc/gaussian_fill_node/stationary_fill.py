"""Arm B live request admission around the existing synchronous robust fit."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
import math
import threading
import time

from rclpy.clock import Clock, ClockType
from std_msgs.msg import Bool
import ros_esc_interfaces.msg as interface_messages
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState, Timekeeper
from ros_esc.convergence_detector_node.centroid_contract import CENTROID_METRIC_MODES
from ros_esc.controller_node.clock_admission import ClockAdmission
from ros_esc.gaussian_fill_node.gaussian_fill_script import StationaryAuthorityError
from ros_esc.stationary_fill_protocol import (
    centroid_configuration_errors, stationary_contract,
    stationary_candidate_evidence, stationary_request_errors,
)
from ros_esc.v2_lifecycle import FRESHNESS_NS, MAX_COMMANDS, hash_payload, message_payload
from ros_esc.v2_stream import time_to_ns


@dataclass
class StationaryRequest:
    message: object
    receipt_ns: int
    steady_ns: int
    pose_snapshots: tuple
    cost_snapshots: tuple
    generation: int
    started_wall_sec: float
    status: str = 'pending'
    registry_generation: object = None
    publications: list = field(default_factory=list)


class StationaryFillAdapter:
    """Authority updates can run during fit; only the fill group executes it."""

    def __init__(self, node):
        self.node = node
        self.metric_mode = str(node.get_parameter('convergence_metric_mode').value)
        self.contract = stationary_contract(self.metric_mode)
        self.request_type = getattr(interface_messages, self.contract['request_type'].rsplit('/', 1)[-1])
        self.lock = threading.RLock()
        self.clock_admission = ClockAdmission()
        self.origin_ns = None
        self.origin_fault = False
        self.run_id = None
        self.state = None
        self.generation = 0
        self.last_now_ns = None
        self.last_reason = ''
        self.requests = {}
        self.last_sequence = 0
        self.pending = None
        self.current = None
        self.closed = False
        self.recording_required = bool(node.get_parameter('recording_ready_required').value)
        self.recording_ready = False
        self.recording_receipt_ns = None
        self.recording_limit_ns = self._limit('recording_ready_stale_sec')
        self.state_limit_ns = self._limit('centroid_state_stale_sec')
        self.timeout_ns = self._limit('fill_design_timeout_sec')
        self.pose_freshness_sec = node.get_parameter('centroid_pose_stale_sec').value
        self.maximum_gap_sec = node.get_parameter('centroid_maximum_gap_sec').value
        self._limit('centroid_pose_stale_sec')
        self._limit('centroid_maximum_gap_sec')
        self.metric_parameters = None
        if self.metric_mode in CENTROID_METRIC_MODES:
            self._limit('centroid_window_sec')
            self.metric_parameters = tuple(float(node.get_parameter(name).value) for name in (
                'centroid_window_sec', 'centroid_epsilon_m', 'centroid_maximum_radius_m'))
            if not all(math.isfinite(value) and value > 0 for value in self.metric_parameters):
                raise ValueError('invalid stationary centroid metric parameters')
        selected = node.resolve_topic_name(str(node.get_parameter(self.contract['request_topic_parameter']).value))
        if selected != self.contract['request_topic']:
            raise ValueError('stationary fill request topic differs from contract')
        self.subscription = node.create_subscription(
            self.request_type, selected, self.request_cb, 10,
            callback_group=node.fill_request_callback_group)
        self.time_subscription = node.create_subscription(
            Timekeeper, str(node.get_parameter('timekeeper_topic').value), self.set_timekeeper, 10,
            callback_group=node.stationary_authority_callback_group)
        self.ready_subscription = node.create_subscription(
            Bool, str(node.get_parameter('recording_ready_topic').value), self.ready_cb, 10,
            callback_group=node.stationary_authority_callback_group)
        self.timer = node.create_timer(
            .02, self.poll, callback_group=node.fill_request_callback_group,
            clock=Clock(clock_type=ClockType.STEADY_TIME))

    def _limit(self, name):
        value = self.node.get_parameter(name).value
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value * 1e9) or round(value * 1e9) <= 0):
            raise ValueError(name + ' must be finite positive seconds')
        return round(value * 1e9)

    def now(self):
        return self.node.get_clock().now().nanoseconds

    @staticmethod
    def steady():
        return time.monotonic_ns()

    def _revoke(self, reason):
        self.generation += 1
        self.state = None
        self.node.latest_algorithm_state = None
        self.clock_admission.discard('state')
        self.last_reason = reason

    def _clock(self, now):
        if self.last_now_ns is not None and now < self.last_now_ns:
            self.clock_admission.clear()
            self._revoke('stationary ROS clock rollback')
        self.last_now_ns = now

    def set_timekeeper(self, message):
        with self.lock:
            try:
                value = float(message.start_time) * 1e9
                if message.mode != 'sim time' or not math.isfinite(value) or value < 0:
                    raise ValueError('invalid stationary time origin')
                origin = round(value)
                if self.origin_ns is not None and origin != self.origin_ns:
                    raise ValueError('stationary time origin changed')
                self.origin_ns = origin
            except (TypeError, ValueError, OverflowError) as exc:
                self.origin_fault = True
                self._revoke(str(exc))

    def ready_cb(self, message):
        with self.lock:
            self.recording_ready = bool(message.data)
            self.recording_receipt_ns = self.steady()
            if self.recording_required and not self.recording_ready:
                self._revoke('stationary recording authorization revoked')

    def _ready(self, steady):
        return not self.recording_required or (
            self.recording_ready and self.recording_receipt_ns is not None
            and 0 <= steady - self.recording_receipt_ns <= self.recording_limit_ns)

    def state_cb(self, message):
        receipt, steady = self.now(), self.steady()
        with self.lock:
            self._clock(receipt)
            try:
                source = time_to_ns(message.stamp)
                if (not message.state_valid or not message.run_id_valid or not message.run_id
                        or message.algorithm_profile != 'robust_gaussian_v1'
                        or not 1 <= message.state <= 8):
                    raise ValueError('invalid stationary AlgorithmState')
                if self.run_id is not None and self.run_id != message.run_id:
                    raise ValueError('stationary supervisor run changed')
                self.clock_admission.receive(
                    'state', source, receipt, steady, message,
                    limit_ns=self.state_limit_ns, fingerprint=hash_payload(message_payload(message)))
                if self.run_id is None:
                    self.run_id = message.run_id
                # A later stopping transition fences work immediately, even
                # while its publication is awaiting this subscriber's clock.
                work = self.current or self.pending
                predecessor = None if work is None else (
                    AlgorithmState.STATE_VERIFY_EXTREMUM if work.message.operation == work.message.CREATE
                    else AlgorithmState.STATE_ESCAPE_REPULSE)
                awaiting_design = (self.current is None and work is not None
                                   and message.state == predecessor
                                   and source <= time_to_ns(work.message.stamp))
                if (work is not None and message.state != AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
                        and source >= time_to_ns(work.message.stamp) and not awaiting_design):
                    self._revoke('stationary request authority left DESIGN')
                self._refresh(receipt, steady)
            except (TypeError, ValueError, OverflowError) as exc:
                self._revoke(str(exc))

    def _refresh(self, now, steady):
        self._clock(now)
        if (self.recording_required and self.recording_ready
                and not self._ready(steady)):
            self.recording_ready = False
            self._revoke('stationary recording authorization stale')
        try:
            for item in self.clock_admission.covered('state', now, steady, limit_ns=self.state_limit_ns):
                self.state = item
                self.node.latest_algorithm_state = item.message
            if self.state is not None and not (
                    0 <= now - self.state.source_ns <= self.state_limit_ns
                    and 0 <= now - self.state.receipt_ns <= self.state_limit_ns
                    and 0 <= steady - self.state.steady_ns <= self.state_limit_ns):
                self._revoke('stationary AlgorithmState stale')
        except ValueError as exc:
            self._revoke(str(exc))

    def _errors(self, message):
        errors = stationary_request_errors(
            message, expected_run_id=self.run_id, expected_frame_id='odom',
            expected_pose_topic=str(self.node.get_parameter('pose_topic').value),
            origin_ns=self.origin_ns, maximum_source_gap_sec=self.maximum_gap_sec,
            pose_freshness_sec=self.pose_freshness_sec, expected_metric_mode=self.metric_mode)
        if self.metric_parameters is not None:
            errors.extend(centroid_configuration_errors(message.confirmation, *self.metric_parameters,
                expected_metric_mode=self.metric_mode))
        return errors

    def request_cb(self, message):
        # This callback belongs to the original fill group. A future message
        # cannot acquire samples that were not present at its first receipt.
        receipt, steady = self.now(), self.steady()
        poses, costs = tuple(self.node.pose_snapshots), tuple(self.node.cost_snapshots)
        started = time.monotonic()
        if not isinstance(message, self.request_type):
            self.last_reason = 'malformed stationary request type'
            return
        replay = ()
        reject = None
        with self.lock:
            self._refresh(receipt, steady)
            errors = self._errors(message)
            if errors or self.closed or self.origin_fault:
                self.last_reason = '; '.join(errors) or 'stationary adapter fenced'
                return
            sequence = int(message.request_sequence)
            previous = self.requests.get(sequence)
            if previous is not None:
                if previous.message.request_sha256 != message.request_sha256:
                    self.last_reason = 'conflicting stationary request sequence'
                    if previous.status in ('pending', 'running'):
                        self._revoke(self.last_reason)
                    return
                replay = tuple(previous.publications) if previous.status == 'complete' else ()
            else:
                if sequence <= self.last_sequence or len(self.requests) >= MAX_COMMANDS:
                    self.last_reason = 'stationary request order or capacity'
                    return
                if any(abs(entry.message.source_timestamp - message.source_timestamp) <= 1e-9
                       for entry in self.requests.values()):
                    self.last_reason = 'stationary request correlation collision'
                    return
                entry = StationaryRequest(deepcopy(message), receipt, steady, poses, costs,
                                          self.generation, started)
                self.requests[sequence] = entry
                self.last_sequence = sequence
                source = time_to_ns(message.stamp)
                if abs(receipt - source) > FRESHNESS_NS:
                    reject = (entry, 'stationary request stale or excessively future')
                elif self.pending is not None or self.current is not None:
                    reject = (entry, 'stationary request already in flight')
                else:
                    self.pending = entry
        for publisher, response in replay:
            publisher.publish(deepcopy(response))
        if reject is not None:
            self._reject(*reject)
        self.poll()

    def _live(self, entry, now, steady, *, running=False):
        if self.closed or self.origin_fault or entry.generation != self.generation:
            raise StationaryAuthorityError('stationary request authority revoked')
        message = entry.message
        if now >= time_to_ns(message.expires_at):
            raise StationaryAuthorityError('stationary DESIGN deadline expired')
        if not running and not (0 <= now - entry.receipt_ns <= FRESHNESS_NS
                                and 0 <= steady - entry.steady_ns <= FRESHNESS_NS):
            raise StationaryAuthorityError('stationary original request receipt expired')
        if self.origin_ns is None or self.state is None:
            return False
        if not self._ready(steady):
            return False
        errors = self._errors(message)
        if errors:
            raise StationaryAuthorityError('; '.join(errors))
        source = time_to_ns(message.stamp)
        if source > now:
            return False
        if not running and now - source > FRESHNESS_NS:
            raise StationaryAuthorityError('stationary request publication stale before admission')
        state = self.state.message
        expected_previous = (AlgorithmState.STATE_VERIFY_EXTREMUM
                             if message.operation == message.CREATE else AlgorithmState.STATE_ESCAPE_REPULSE)
        if state.state != AlgorithmState.STATE_DESIGN_OR_MERGE_FILL:
            if not running and state.state == expected_previous and self.state.source_ns <= source:
                return False  # Matching DESIGN can follow the request on DDS.
            raise StationaryAuthorityError('stationary request outside DESIGN')
        if (not state.previous_state_valid or state.previous_state != expected_previous
                or not state.state_elapsed_valid or not math.isfinite(state.state_elapsed_sec)
                or state.state_elapsed_sec < 0):
            raise StationaryAuthorityError('stationary DESIGN entry lacks matching authority')
        began = self.state.source_ns - round(state.state_elapsed_sec * 1e9)
        if (began > source or abs(time_to_ns(message.expires_at) - (began + self.timeout_ns)) > 1):
            raise StationaryAuthorityError('stationary request deadline differs from DESIGN entry')
        if message.operation == message.TARGETED_REDESIGN:
            cluster = self.node.fill_registry.active_cluster_for_fill(message.target_fill_id)
            active = None if cluster is None else cluster.active_fill
            if active is None or (active.fill_id, active.cluster_id, active.revision) != (
                    message.target_fill_id, message.target_cluster_id, message.target_revision):
                raise StationaryAuthorityError('stationary redesign target changed')
        return True

    def _reject(self, entry, reason):
        self.last_reason = reason
        previous = self.current
        self.current = entry
        try:
            self.node._publish_event(AlgorithmEvent.EVENT_FILL_REJECTED, reason,
                                     entry.message.source_timestamp, [], [], reason_code=36)
        finally:
            entry.status = 'complete'
            self.current = previous
            if self.pending is entry:
                self.pending = None
            entry.pose_snapshots = entry.cost_snapshots = ()

    def poll(self):
        with self.lock:
            now, steady = self.now(), self.steady()
            self._refresh(now, steady)
            entry = self.pending
            if entry is None or self.current is not None:
                return
            try:
                if not self._live(entry, now, steady):
                    return
                entry.status = 'running'
                entry.registry_generation = self.node.fill_registry.generation
                self.pending, self.current = None, entry
            except StationaryAuthorityError as exc:
                failure = str(exc)
            else:
                failure = None
        if failure is not None:
            self._reject(entry, failure)
            return
        from ros_esc.gaussian_fill_node.gaussian_fill_script import RobustRequestContext
        message = entry.message
        context = RobustRequestContext(
            message.source_timestamp,
            message.target_fill_id if message.operation == message.TARGETED_REDESIGN else None,
            entry.receipt_ns * 1e-9, entry.pose_snapshots, entry.cost_snapshots,
            entry.started_wall_sec, candidate_evidence=stationary_candidate_evidence(message),
            authority=entry)
        self.node.current_event_timestamp = message.source_timestamp
        try:
            if (self.node.enable_observability
                    and not self.node.observability_configuration_published):
                self.node._publish_configuration_event()
                self.node.observability_configuration_published = True
            if self.node.escape_policy == 'none':
                self.node._publish_rejection(13, 'fill policy is disabled')
            elif self.node.max_fills == 0:
                self.node._publish_rejection(14, 'maximum fill count is zero')
            else:
                self.node._execute_robust_request(context)
        finally:
            with self.lock:
                entry.status = 'complete'
                entry.pose_snapshots = entry.cost_snapshots = ()
                self.current = None

    @contextmanager
    def commit_guard(self, entry):
        with self.lock:
            now, steady = self.now(), self.steady()
            self._refresh(now, steady)
            if (self.current is not entry or not self._live(entry, now, steady, running=True)
                    or entry.registry_generation != self.node.fill_registry.generation):
                raise StationaryAuthorityError('stationary live authority unavailable before commit')
            yield

    def cache_publication(self, publisher, message):
        if (self.current is not None
                and not (isinstance(message, AlgorithmEvent) and not message.source_timestamp_valid)):
            self.current.publications.append((publisher, deepcopy(message)))

    def close(self):
        with self.lock:
            self.closed = True
            self._revoke('stationary fill node closed')
