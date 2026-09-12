"""Epoch-bound identity wrapper; the existing PDE owner retains its arithmetic."""

import copy
import math
from collections import OrderedDict, deque

from ros_esc.v2_epoch import EpochBinding
from ros_esc.v2_lifecycle import FRESHNESS_NS, copy_envelope, hash_payload, message_payload
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc_interfaces.msg import PdeHistoryEvidence


PDE_EVIDENCE_TOPIC = '/gesc_gaussian/v2/pde_history_evidence'


def history_sha256(message):
    return hash_payload(message_payload(message, exclude=('stamp', 'history_sha256')))


class V2PdeEvidence:
    def __init__(self, node):
        self.node = node
        self.pending = deque()
        self.seen = OrderedDict()
        self.first_source = None
        self.latest_source = None
        self.latest_receipt = None
        self.last_queued_source = None
        self.sequence = 0
        self.binding = EpochBinding(node, self.reset)
        if node.resolve_topic_name('/odom') != self.binding.config['pose_topic']:
            raise ValueError('PDE pose topic differs from V2 stream contract')
        self.publisher = node.create_publisher(PdeHistoryEvidence, PDE_EVIDENCE_TOPIC, 10)
        self.timer = node.create_timer(0.02, self.poll)

    def reset(self, reason):
        # A gap/conflict must revoke detector persistence immediately. Merely
        # suppressing the next history would let an old dwell span that fault.
        context = getattr(getattr(self, 'binding', None), 'context', None)
        if self.first_source is not None and context is not None:
            invalid = PdeHistoryEvidence()
            copy_envelope(invalid, context)
            set_time(invalid.stamp, self.node.get_clock().now().nanoseconds)
            invalid.context_sequence = context.context_sequence
            self.sequence += 1
            invalid.history_sequence = self.sequence
            invalid.epoch_started_at = copy.deepcopy(context.started_at)
            set_time(invalid.input_start, self.first_source)
            set_time(invalid.input_end, self.latest_source)
            set_time(invalid.latest_input_receipt, self.latest_receipt)
            invalid.history.header = 'V2_INVALID: ' + str(reason)
            invalid.valid = False
            invalid.history_sha256 = history_sha256(invalid)
            self.publisher.publish(invalid)
        self.pending.clear()
        self.first_source = self.latest_source = self.latest_receipt = None
        self.last_queued_source = None
        self.node.search_epoch_reset_pending = True
        self.node.last_stamp = None

    def receive_pose(self, message):
        receipt = self.binding.now()
        try:
            source = time_to_ns(message.header.stamp)
            context = self.binding.context
            xy = (float(message.pose.pose.position.x), float(message.pose.pose.position.y))
            if (context is None or context.algorithm_state != 1
                    or message.header.frame_id != self.binding.config['frame_id']
                    or not all(math.isfinite(value) for value in xy)
                    or source < time_to_ns(context.started_at)
                    or abs(receipt - source) > FRESHNESS_NS):
                raise ValueError('invalid_pose')
            key = (int(context.search_epoch), source)
            payload = (str(message.header.frame_id), xy)
            if key in self.seen:
                if self.seen[key] != payload:
                    self.seen[key] = None
                    raise ValueError('conflicting_pose')
                return
            self.seen[key] = payload
            while len(self.seen) > 4096:
                self.seen.popitem(last=False)
            if self.last_queued_source is not None and source <= self.last_queued_source:
                raise ValueError('regressed_pose')
            self.last_queued_source = source
            if len(self.pending) >= 1024:
                raise ValueError('pose_capacity')
            self.pending.append((source, receipt, copy.deepcopy(message)))
            self.poll()
        except (TypeError, ValueError, OverflowError):
            self.reset('invalid_pose')

    def poll(self):
        now = self.binding.now()
        if not self.binding.ready(now):
            # A future heartbeat can wait for clock coverage, but cannot update
            # numerical state. Expiration never substitutes fresh receipt times.
            while self.pending and now - self.pending[0][1] > FRESHNESS_NS:
                self.reset('stale_epoch_or_pose')
            return
        while self.pending:
            source, receipt, message = self.pending[0]
            if now < source:
                return
            self.pending.popleft()
            if not (0 <= now - receipt <= FRESHNESS_NS
                    and now - source <= FRESHNESS_NS):
                self.reset('stale_pose')
                return
            if self.latest_source is not None and source - self.latest_source > FRESHNESS_NS:
                self.reset('pose_gap')
            if self.first_source is None:
                self.first_source = source
            self.latest_source, self.latest_receipt = source, receipt
            self.node._legacy_pose_cb(message)

    def publish(self, history):
        now = self.binding.now()
        if (not self.binding.ready(now) or self.first_source is None
                or self.latest_source is None or self.latest_receipt is None):
            return
        if max(now - self.latest_source, now - self.latest_receipt) > FRESHNESS_NS:
            self.reset('stale_publication')
            return
        result = PdeHistoryEvidence()
        copy_envelope(result, self.binding.context)
        set_time(result.stamp, now)
        result.context_sequence = self.binding.context.context_sequence
        self.sequence += 1
        result.history_sequence = self.sequence
        result.epoch_started_at = copy.deepcopy(self.binding.context.started_at)
        set_time(result.input_start, self.first_source)
        set_time(result.input_end, self.latest_source)
        set_time(result.latest_input_receipt, self.latest_receipt)
        result.history = copy.deepcopy(history)
        result.valid = True
        result.history_sha256 = history_sha256(result)
        self.publisher.publish(result)
