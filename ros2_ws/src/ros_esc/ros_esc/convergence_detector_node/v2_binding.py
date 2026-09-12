"""Typed confirmation binding for both unchanged detector decision methods."""

import copy
import math
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_HISTORY_KIND
import time
from collections import OrderedDict, deque

from rclpy.clock import Clock, ClockType

from ros_esc.pde_history_node.v2_evidence import PDE_EVIDENCE_TOPIC, history_sha256
from ros_esc.v2_epoch import EpochBinding
from ros_esc.v2_lifecycle import (
    DETECTOR_CONFIRMATION_TOPIC, FRESHNESS_NS, copy_envelope,
)
from ros_esc.v2_stream import relative_stamp_ns, set_time, time_to_ns
from ros_esc_interfaces.msg import DetectorConfirmation, PdeHistoryEvidence


MAX_PENDING_HISTORIES = 1024
MAX_HISTORY_TOMBSTONES = 4096


class V2DetectorBinding:
    def __init__(self, node):
        self.node = node
        self.sequence = 0
        self.confirmed_epoch = None
        self.last_history_sequence = 0
        self.last_history_digest = None
        self.history = None
        self.history_pending = deque()
        self.history_seen = OrderedDict()
        self.history_frontier = 0
        self.latest_history_receipt = None
        self.pending = deque()
        self.seen = OrderedDict()
        self.pose_frontier = None
        self.latest_pose_steady_ns = None
        self.binding = EpochBinding(node, self.reset)
        if (node.centroid_mode and node.resolve_topic_name(node.centroid_pose_topic)
                != self.binding.config['pose_topic']):
            raise ValueError('centroid pose topic differs from V2 stream contract')
        self.publisher = node.create_publisher(
            DetectorConfirmation, DETECTOR_CONFIRMATION_TOPIC, 10)
        self.subscription = None
        self.pose_timer = None
        self.history_timer = None
        if node.centroid_mode:
            self.pose_timer = node.create_timer(
                0.02, self.poll, clock=Clock(clock_type=ClockType.STEADY_TIME))
        if not node.centroid_mode:
            self.history_timer = node.create_timer(
                0.02, self.poll_history, clock=Clock(clock_type=ClockType.STEADY_TIME))
            self.subscription = node.create_subscription(
                PdeHistoryEvidence, PDE_EVIDENCE_TOPIC, self.receive_history, 10)

    def reset(self, reason, *, preserve_history_pending=False):
        self.history = None
        self.latest_history_receipt = None
        if not preserve_history_pending:
            self.history_pending.clear()
        self.pending.clear()
        self.latest_pose_steady_ns = None
        if reason == 'new_search_epoch':
            self.pose_frontier = None
        self.node._reset_detection_state()
        if self.node.centroid_mode:
            context = self.binding.context
            epoch = context.search_epoch if context is not None else 0
            epoch_args = ({'start_ns': time_to_ns(context.started_at) if context is not None else None}
                          if self.node.metric_mode == RECURRENT_MODE else {})
            self.node.centroid_detector.start_epoch(f'v2-authoritative:{epoch}', **epoch_args)
            # start_epoch is intentionally idempotent within one SEARCH epoch.
            # A source fault still discards all numerical integration support.
            self.node.centroid_detector.invalidate(str(reason))
            self.node.latest_centroid_result = None
            self.node.centroid_pose_source_ns = None
            self.node.centroid_pose_receipt_ns = None
            if context is not None:
                self.node.centroid_epoch_started_ns = time_to_ns(context.started_at)
                self.node.centroid_confirmed_in_epoch = self.confirmed_epoch == epoch

    def receive_pose(self, message):
        """Keep original receipts while source headers await clock coverage."""
        receipt, steady = self.binding.now(), time.monotonic_ns()
        context = self.binding.context
        try:
            source = time_to_ns(message.header.stamp)
            xy = (float(message.pose.pose.position.x), float(message.pose.pose.position.y))
            if (context is None or context.algorithm_state != 1
                    or message.header.frame_id != self.binding.config['frame_id']
                    or not all(math.isfinite(value) for value in xy)
                    or source < time_to_ns(context.started_at)
                    or abs(receipt - source) > FRESHNESS_NS):
                raise ValueError('invalid_selected_pose')
            key = (int(context.search_epoch), source)
            payload = (str(message.header.frame_id), xy)
            if key in self.seen:
                if self.seen[key] != payload:
                    self.seen[key] = None
                    raise ValueError('conflicting_selected_pose')
                self.poll()  # A duplicate never changes either receipt.
                return
            self.seen[key] = payload
            while len(self.seen) > 4096:
                self.seen.popitem(last=False)
            if self.pose_frontier is not None and source <= self.pose_frontier:
                raise ValueError('regressed_selected_pose')
            self.pose_frontier = source
            if len(self.pending) >= 1024:
                raise ValueError('selected_pose_capacity')
            self.pending.append((source, receipt, steady, copy.deepcopy(message)))
            self.poll()
        except (TypeError, ValueError, OverflowError) as error:
            self.reset(str(error))

    def poll(self):
        now, steady = self.binding.now(), time.monotonic_ns()
        if self.latest_pose_steady_ns is not None and (
                steady - self.latest_pose_steady_ns > FRESHNESS_NS):
            self.reset('stale_selected_pose_receipt')
            return
        if self.pending:
            _, receipt, first_steady, _ = self.pending[0]
            if (not 0 <= now - receipt <= FRESHNESS_NS
                    or not 0 <= steady - first_steady <= FRESHNESS_NS):
                self.reset('stale_pending_selected_pose')
                return
        if not self.binding.ready(now):
            return
        while self.pending:
            source, receipt, first_steady, message = self.pending[0]
            if now < source:
                return
            self.pending.popleft()
            if (not 0 <= now - source <= FRESHNESS_NS
                    or not 0 <= now - receipt <= FRESHNESS_NS
                    or not 0 <= steady - first_steady <= FRESHNESS_NS):
                self.reset('stale_selected_pose')
                return
            self.latest_pose_steady_ns = first_steady
            self.node._admitted_pose_cb(message, receipt_ns=receipt)

    def _history_envelope(self, message, now):
        """Validate source claims before they can enter the bounded queue."""
        context = self.binding.context
        if (self.binding.origin_fault or context is None or context.algorithm_state != 1
                or message.schema_version != 1 or message.run_id != context.run_id
                or message.stream_contract_id != context.stream_contract_id
                or time_to_ns(message.time_origin) != self.binding.origin_ns
                or message.frame_id != context.frame_id or message.search_epoch != context.search_epoch
                or message.context_sequence <= 0
                or time_to_ns(message.epoch_started_at) != time_to_ns(context.started_at)
                or message.history_sha256 != history_sha256(message)):
            raise ValueError('history_identity')
        publication = time_to_ns(message.stamp)
        if (message.history_sequence <= 0
                or publication < time_to_ns(context.started_at)
                or abs(now - publication) > FRESHNESS_NS):
            raise ValueError('history_sequence_or_publication')
        if not message.valid:
            if message.history.data or not message.history.header.startswith('V2_INVALID: '):
                raise ValueError('invalid_history_revocation')
        else:
            start, end = time_to_ns(message.input_start), time_to_ns(message.input_end)
            receipt = time_to_ns(message.latest_input_receipt)
            if (not time_to_ns(context.started_at) <= start <= end <= publication
                    or not 0 <= receipt <= publication
                    or max(publication - receipt, publication - end) > FRESHNESS_NS
                    or abs(relative_stamp_ns(0, message.history.timestamp) - publication) > 2
                    or not message.history.data
                    or not all(math.isfinite(value) for value in message.history.data)):
                raise ValueError('history_time_or_values')
        return publication

    def receive_history(self, message):
        """Admit publication time separately from the sender's admitted input."""
        receipt, steady = self.binding.now(), time.monotonic_ns()
        try:
            publication = self._history_envelope(message, receipt)
            sequence, digest = int(message.history_sequence), message.history_sha256
            if sequence in self.history_seen:
                if self.history_seen[sequence] != digest:
                    self.history_seen[sequence] = None
                    raise ValueError('history_conflict')
                self.poll_history()  # No retransmission can refresh either receipt.
                return
            if sequence <= self.history_frontier:
                raise ValueError('history_regression')
            self.history_frontier = sequence
            self.history_seen[sequence] = digest
            while len(self.history_seen) > MAX_HISTORY_TOMBSTONES:
                self.history_seen.popitem(last=False)
            if not message.valid:
                # A known revocation fences earlier evidence immediately, even
                # while its publication awaits clock coverage. It never grants
                # authority; its ordered admission still waits below.
                self.reset('pending_pde_revocation')
            if len(self.history_pending) >= MAX_PENDING_HISTORIES:
                raise ValueError('history_capacity')
            self.history_pending.append((publication, receipt, steady, copy.deepcopy(message)))
            self.poll_history()
        except (TypeError, ValueError, OverflowError):
            self.reset('invalid_pde_evidence')

    def _history_receipt_ready(self, now=None):
        if now is None:
            now = self.binding.now()
        receipt = self.latest_history_receipt
        return bool(self.history is not None and receipt is not None
                    and 0 <= now - receipt[0] <= FRESHNESS_NS
                    and 0 <= time.monotonic_ns() - receipt[1] <= FRESHNESS_NS)

    def poll_history(self):
        now, steady = self.binding.now(), time.monotonic_ns()
        if self.history is not None and not self._history_receipt_ready(now):
            self.reset('stale_history_receipt', preserve_history_pending=True)
        while self.history_pending:
            now, steady = self.binding.now(), time.monotonic_ns()
            if not self.history_pending:  # A detected clock rollback clears it.
                return
            publication, receipt, first_steady, message = self.history_pending[0]
            if (not 0 <= now - receipt <= FRESHNESS_NS
                    or not 0 <= steady - first_steady <= FRESHNESS_NS):
                self.reset('stale_pending_history')
                return
            if (not self.binding.ready(now) or now < publication
                    or message.context_sequence > self.binding.context.context_sequence):
                return
            self.history_pending.popleft()
            try:
                # Revalidate epoch/hash and sender input freshness after waiting.
                self._history_envelope(message, now)
                if message.valid and (now - time_to_ns(message.input_end) > FRESHNESS_NS
                        or now - time_to_ns(message.latest_input_receipt) > FRESHNESS_NS):
                    raise ValueError('stale_history_input')
                if message.history_sequence <= self.last_history_sequence:
                    raise ValueError('history_admission_regression')
                self.last_history_sequence = int(message.history_sequence)
                self.last_history_digest = message.history_sha256
                if not message.valid:
                    self.reset('revoked_pde_evidence', preserve_history_pending=True)
                    continue
                self.latest_history_receipt = (receipt, first_steady)
                self.history = copy.deepcopy(message)
                self.node.buffer_cb(message.history)
            except (TypeError, ValueError, OverflowError):
                self.reset('invalid_pde_evidence')
                return

    def _confirmation(self, start, end, center):
        now = self.binding.now()
        context = self.binding.context
        if (not self.binding.ready(now) or self.confirmed_epoch == context.search_epoch
                or not time_to_ns(context.started_at) <= start <= end <= now
                or now - end > FRESHNESS_NS
                or not all(math.isfinite(float(value)) for value in center)):
            return None
        result = DetectorConfirmation()
        copy_envelope(result, context)
        set_time(result.stamp, now)
        result.context_sequence = context.context_sequence
        result.epoch_started_at = copy.deepcopy(context.started_at)
        set_time(result.source_stamp, end)
        set_time(result.history_start, start)
        set_time(result.history_end, end)
        result.metric_mode = self.node.metric_mode
        result.source_stamp_kind = 'pose_input'
        result.confirmation_sequence = self.sequence + 1
        result.detector_local_epoch = int(getattr(self.node, 'centroid_search_epoch', 0))
        result.center_x_m, result.center_y_m = map(float, center)
        result.valid = True
        return result

    def publish_centroid(self, diagnostic):
        if (diagnostic.frame_id != self.binding.config['frame_id']
                or diagnostic.metric_mode != self.node.metric_mode):
            return False
        result = self._confirmation(time_to_ns(diagnostic.history_start),
                                    time_to_ns(diagnostic.history_end),
                                    (diagnostic.center_x_m, diagnostic.center_y_m))
        if result is None:
            return False
        result.history_kind = (RECURRENT_HISTORY_KIND if self.node.metric_mode == RECURRENT_MODE
                               else 'centroid_windows')
        result.convergence_score_m = float(diagnostic.score_m)
        result.convergence_score_valid = bool(diagnostic.metric_valid)
        if not result.convergence_score_valid or not math.isfinite(result.convergence_score_m):
            return False
        return self._publish(result)

    def centroid_ready(self, *, now_ns=None, steady_ns=None):
        """Use captured clocks for pure status reads; retain old caller behavior."""
        receipt = self.latest_pose_steady_ns
        ready = self.binding.ready() if now_ns is None else self.binding.ready(now_ns)
        return bool(ready and receipt is not None
                    and 0 <= (time.monotonic_ns() if steady_ns is None else steady_ns)
                    - receipt <= FRESHNESS_NS)

    def publish_legacy(self, legacy):
        if self.history is None:
            return False
        result = self._confirmation(time_to_ns(self.history.input_start),
                                    time_to_ns(self.history.input_end), legacy.data[3:5])
        if result is None or not all(math.isfinite(value) for value in legacy.data):
            return False
        result.history_kind = 'pde_input_support'
        result.legacy_r_mean_m2 = float(legacy.data[1])
        result.legacy_r_mean_valid = True
        result.legacy_snapshot = list(legacy.data)
        return self._publish(result)

    def _publish(self, result):
        # Recheck after construction; computation can advance the ROS clock.
        now = self.binding.now()
        if (not self.binding.ready(now)
                or self.binding.context.search_epoch != result.search_epoch
                or now - time_to_ns(result.source_stamp) > FRESHNESS_NS):
            return False
        if result.history_kind in ('centroid_windows', RECURRENT_HISTORY_KIND) and not self.centroid_ready():
            self.reset('stale_selected_pose_receipt')
            return False
        if result.history_kind == 'pde_input_support' and not self._history_receipt_ready(now):
            self.reset('stale_history_receipt')
            return False
        set_time(result.stamp, now)
        self.publisher.publish(result)
        self.sequence = result.confirmation_sequence
        self.confirmed_epoch = result.search_epoch
        return True
