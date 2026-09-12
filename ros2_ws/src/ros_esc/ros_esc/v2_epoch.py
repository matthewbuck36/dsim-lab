"""Authoritative supervisor epoch binding for existing observation owners."""

import copy

from ros_esc.v2_lifecycle import (
    FRESHNESS_NS, SEARCH_EPOCH_TOPIC, message_payload,
)
from ros_esc.v2_stream import relative_stamp_ns, stream_contract_id, time_to_ns, validate_mode_identity
from ros_esc_interfaces.msg import AlgorithmState, SearchEpochContext, Timekeeper


def declare_epoch_parameters(node):
    for name, default in (('continuous_search_mode', 'stationary_v1'),
                          ('v2_run_id', ''), ('v2_stream_config_json', '')):
        node.declare_parameter(name, default)


class EpochBinding:
    """Receive identity and heartbeat without treating elapsed time as an epoch."""

    def __init__(self, node, on_boundary):
        self.node = node
        self.run_id = str(node.get_parameter('v2_run_id').value)
        self.config = validate_mode_identity(
            str(node.get_parameter('continuous_search_mode').value),
            node.algorithm_profile, self.run_id,
            node.get_parameter('v2_stream_config_json').value,
            simulation=bool(node.get_parameter('use_sim_time').value))
        self.on_boundary = on_boundary
        self.origin_ns = None
        self.contract_id = None
        self.origin_fault = False
        self.context = None
        self.receipt_ns = None
        self.last_now_ns = None
        self.last_epoch = 0
        self.last_sequence = 0
        self.last_payload = None
        self.epoch_start_ns = None
        self.subscriptions = [
            node.create_subscription(Timekeeper, self.config['timekeeper_topic'],
                                     self.set_timekeeper, 10),
            node.create_subscription(SearchEpochContext, SEARCH_EPOCH_TOPIC,
                                     self.receive_context, 10),
        ]

    def now(self):
        now = self.node.get_clock().now().nanoseconds
        if self.last_now_ns is not None and now < self.last_now_ns:
            self.context = None
            self.on_boundary('clock_rollback')
        self.last_now_ns = now
        return now

    def invalidate(self, reason):
        self.context = None
        self.on_boundary(reason)

    def set_timekeeper(self, msg):
        try:
            if msg.mode != 'sim time' or msg.start_time < 0:
                raise ValueError('invalid simulation time origin')
            origin = relative_stamp_ns(0, msg.start_time)
            contract_id = stream_contract_id(self.config, origin)
        except (AttributeError, TypeError, ValueError, OverflowError):
            self.origin_fault = True
            self.invalidate('invalid_time_origin')
            return
        if self.origin_ns is not None and origin != self.origin_ns:
            self.origin_fault = True
            self.invalidate('changed_time_origin')
            return
        # An invalid/changed origin is terminal for this owner instance. A later
        # packet cannot replace its first valid origin or rehabilitate the stream.
        if not self.origin_fault:
            self.origin_ns = origin
            self.contract_id = contract_id

    def receive_context(self, msg):
        receipt = self.now()
        try:
            stamp, start = time_to_ns(msg.stamp), time_to_ns(msg.started_at)
            if (self.origin_fault or self.origin_ns is None
                    or msg.schema_version != 1 or msg.run_id != self.run_id
                    or msg.stream_contract_id != self.contract_id
                    or time_to_ns(msg.time_origin) != self.origin_ns
                    or msg.frame_id != self.config['frame_id']
                    or not msg.valid or not 1 <= msg.algorithm_state <= 8
                    or msg.search_epoch <= 0 or start < self.origin_ns
                    or start > stamp or abs(receipt - stamp) > FRESHNESS_NS):
                raise ValueError('invalid_epoch_context')
            payload = message_payload(msg)
            if msg.context_sequence < self.last_sequence or msg.search_epoch < self.last_epoch:
                raise ValueError('regressed_epoch_context')
            if msg.context_sequence == self.last_sequence:
                if payload != self.last_payload:
                    raise ValueError('conflicting_epoch_context')
                return  # Original receipt age is never refreshed.
            if msg.search_epoch == self.last_epoch and start != self.epoch_start_ns:
                raise ValueError('changed_epoch_start')
            boundary = msg.search_epoch != self.last_epoch
            previous_state = self.context.algorithm_state if self.context else None
            self.context = copy.deepcopy(msg)
            self.receipt_ns = receipt
            self.last_sequence = int(msg.context_sequence)
            self.last_payload = payload
            self.last_epoch = int(msg.search_epoch)
            self.epoch_start_ns = start
            if boundary:
                self.on_boundary('new_search_epoch')
            elif previous_state != msg.algorithm_state and msg.algorithm_state != AlgorithmState.STATE_SEARCH:
                self.on_boundary('outside_search')
        except (TypeError, ValueError, OverflowError):
            self.invalidate('invalid_epoch_context')

    def ready(self, now_ns=None):
        now = self.now() if now_ns is None else now_ns
        context = self.context
        return bool(not self.origin_fault and context is not None
                    and context.algorithm_state == AlgorithmState.STATE_SEARCH
                    and 0 <= now - time_to_ns(context.stamp) <= FRESHNESS_NS
                    and self.receipt_ns is not None
                    and 0 <= now - self.receipt_ns <= FRESHNESS_NS)
