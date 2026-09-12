"""Opt-in atomic objective receipts inside the existing modified-cost owner."""

from collections import OrderedDict
from copy import deepcopy
import hashlib
import json
import math

from ros_esc_interfaces.msg import (
    ObjectiveCostSample, SourceSampleProvenance, StampedFloat64MultiArray,
    Timekeeper,
)
from ros_esc.v2_stream import (
    relative_stamp_ns, set_time, stream_contract_id, time_to_ns,
    validate_stream_config,
)
from ros_esc.filter_node.rolling_gesc import publication_time_tolerance_ns


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def objective_configuration(node):
    """Capture the exact active law, excluding its continuously advancing time."""
    state = node.algorithm_state
    fills = []
    for key, term in sorted(node.robust_terms.items()):
        fills.append({
            "fill_id": int(key), "cluster_id": int(term["cluster_id"]),
            "revision": int(term["revision"]),
            "amplitude": float(term["amplitude"]),
            "center": [float(v) for v in term["center"]],
            "covariance": [[float(v) for v in row] for row in term["covariance"]],
        })
    affine = []
    for key, term in sorted(node.robust_affine_terms.items()):
        affine.append({
            "cluster_id": int(key), "fill_id": int(term["fill_id"]),
            "direction_revision": int(term["direction_revision"]),
            "anchor": [float(v) for v in term["anchor"]],
            "b0": [float(v) for v in term["b0"]], "t0_sec": float(term["t0"]),
        })
    return {
        "schema_version": 1,
        "weights": [float(state.sensor_weight), float(state.gaussian_weight),
                    float(state.affine_weight)],
        "bias_all_channels": bool(node.bias_all), "fills": fills,
        "affine": affine, "affine_enabled": bool(node.enable_affine_bias),
        "affine_decay_rate": float(node.affine_decay_rate),
        "affine_max_age": float(node.affine_max_age),
        "affine_min_norm": float(node.affine_min_norm),
    }


class V2ObjectiveComposer:
    """Bounded join; the parent node retains all cost and registry ownership."""

    freshness_ns = 500_000_000
    maximum_pending = 1024

    def __init__(self, node):
        self.node = node
        self.run_id = str(node.get_parameter("v2_run_id").value).strip()
        if not self.run_id:
            raise ValueError("rolling GESC requires explicit v2_run_id")
        self.config = validate_stream_config(
            node.get_parameter("v2_stream_config_json").value
        )
        self.origin_ns = None
        self.contract_id = None
        self.origin_fault = False
        self.raw = OrderedDict()
        self.selected_raw = OrderedDict()
        self.provenance = OrderedDict()
        self.seen = OrderedDict()
        self.last_model_ns = None
        self.last_now_ns = None
        self.objective_key = None
        self.objective_revision = 0
        self.fault_count = 0
        self.last_fault_reason = ""
        self.publisher = node.create_publisher(
            ObjectiveCostSample, self.config["objective_cost_topic"], 100
        )
        self.provenance_subscription = node.create_subscription(
            SourceSampleProvenance, self.config["provenance_topic"],
            self.add_provenance, 100,
        )
        self.raw_subscription = node.create_subscription(
            StampedFloat64MultiArray, self.config["raw_cost_topic"],
            self.add_selected_raw, 100,
        )
        self.time_subscription = node.create_subscription(
            Timekeeper, self.config["timekeeper_topic"], self.set_timekeeper, 10
        )
        self.timer = node.create_timer(0.05, self.poll)

    def _now(self):
        return self.node.get_clock().now().nanoseconds

    def _clear(self):
        self.raw.clear()
        self.selected_raw.clear()
        self.provenance.clear()
        self.last_model_ns = None

    def _report_fault(self, reason):
        self.fault_count += 1
        self.last_fault_reason = reason
        if hasattr(self.node, "get_logger"):
            self.node.get_logger().warning("V2 objective evidence rejected: " + reason,
                                           throttle_duration_sec=5.0)

    def set_timekeeper(self, msg):
        if msg.mode != "sim time" or not math.isfinite(msg.start_time) or msg.start_time < 0:
            self.origin_fault = True
            self._clear()
            return
        origin = round(msg.start_time * 1e9)
        if self.origin_ns is not None and origin != self.origin_ns:
            self.origin_fault = True
            self._clear()
            return
        self.origin_ns = origin
        self.contract_id = stream_contract_id(self.config, origin)
        self.poll()

    def _remember(self, key):
        self.seen[key] = True
        while len(self.seen) > 4096:
            self.seen.popitem(last=False)

    def _insert(self, collection, key, msg, receipt_ns):
        if key in self.seen:
            return
        if key in collection:
            if collection[key][0] != msg:
                self.raw.pop(key, None)
                self.selected_raw.pop(key, None)
                self.provenance.pop(key, None)
                self._remember(key)
            return
        if len(collection) >= self.maximum_pending:
            self._report_fault("pending_capacity")
            oldest, _ = collection.popitem(last=False)
            self.raw.pop(oldest, None)
            self.selected_raw.pop(oldest, None)
            self.provenance.pop(oldest, None)
            self._remember(oldest)
        collection[key] = (deepcopy(msg), receipt_ns)
        self.poll()

    def add_raw(self, msg):
        receipt = self._now()
        if (not msg.source_timestamp_valid or not msg.raw_cost_valid
                or not math.isfinite(msg.source_timestamp)
                or msg.source_timestamp < 0
                or int(msg.channel_count) != 1 or len(msg.raw_cost) != 1
                or not all(math.isfinite(v) for v in msg.raw_cost)):
            return
        self._insert(self.raw, float(msg.source_timestamp), msg, receipt)

    def add_selected_raw(self, msg):
        receipt = self._now()
        if (not math.isfinite(msg.timestamp) or msg.timestamp < 0
                or len(msg.data) != 1 or not all(math.isfinite(v) for v in msg.data)):
            self._report_fault("invalid_selected_raw")
            return
        self._insert(self.selected_raw, float(msg.timestamp), msg, receipt)

    def add_provenance(self, msg):
        receipt = self._now()
        key = float(msg.legacy_cost_source_timestamp_sec)
        if not math.isfinite(key) or key < 0:
            self._report_fault("invalid_legacy_key")
            return
        if (self.config.get('cost_key_basis') == 'model_input_time'
                and (not msg.model_input_stamp_valid or not msg.sensor_transform_valid)):
            try:
                same_stream = (msg.schema_version == self.config['schema_version']
                               and msg.run_id == self.run_id and msg.stream_contract_id == self.contract_id
                               and msg.frame_id == self.config['frame_id']
                               and time_to_ns(msg.time_origin) == self.origin_ns)
            except (ValueError, OverflowError):
                same_stream = False
            if same_stream:
                self.raw.pop(key, None)
                self.selected_raw.pop(key, None)
                self.provenance.pop(key, None)
                self._remember(key)
                self._report_fault('source_key_invalidated')
                return
        self._insert(self.provenance, key, msg, receipt)

    def _valid_provenance(self, msg, now):
        if (msg.schema_version != self.config['schema_version'] or msg.run_id != self.run_id
                or msg.stream_contract_id != self.contract_id
                or msg.frame_id != self.config["frame_id"]
                or time_to_ns(msg.time_origin) != self.origin_ns
                or not msg.model_input_stamp_valid or not msg.sensor_transform_valid
                or msg.source_sequence <= 0 or int(msg.channel_count) != 1):
            return False
        arrays = (msg.sensor_x_m, msg.sensor_y_m, msg.sensor_world_phase_rad)
        if any(len(a) != 1 or not all(math.isfinite(v) for v in a) for a in arrays):
            return False
        source = time_to_ns(msg.model_input_stamp)
        publication = time_to_ns(msg.cost_publication_stamp)
        key_stamp = source if self.config.get("cost_key_basis") == "model_input_time" else publication
        return (self.origin_ns <= source <= publication <= now
                and abs(key_stamp - relative_stamp_ns(
                    self.origin_ns, msg.legacy_cost_source_timestamp_sec)) <=
                publication_time_tolerance_ns(
                    self.origin_ns, msg.legacy_cost_source_timestamp_sec, key_stamp)
                and now - source <= self.freshness_ns)

    def poll(self):
        now = self._now()
        if self.last_now_ns is not None and now < self.last_now_ns:
            self._clear()
            self._report_fault('clock_rollback')
        self.last_now_ns = now
        if self.origin_ns is None or self.origin_fault:
            return
        activation = getattr(self.node, 'v2_fill_activation', None)
        if activation is not None and not activation.poll(now):
            return
        for collection in (self.raw, self.selected_raw, self.provenance):
            for key, (_, received) in list(collection.items()):
                if now - received > self.freshness_ns or now < received:
                    self.raw.pop(key, None)
                    self.selected_raw.pop(key, None)
                    self.provenance.pop(key, None)
                    self._remember(key)
        state = self.node.algorithm_state
        try:
            state_valid = (state is not None and state.state_valid and state.weights_valid
                and state.run_id_valid and state.run_id == self.run_id
                and all(math.isfinite(v) for v in
                        (state.sensor_weight, state.gaussian_weight, state.affine_weight))
                and 0 <= now - time_to_ns(state.stamp) <= self.freshness_ns)
        except (ValueError, OverflowError):
            state_valid = False
        if not state_valid:
            return
        # Legacy source publication order is monotonic for this single owner.
        # Missing earlier provenance blocks newer raw costs until bounded expiry.
        for key in sorted(self.raw):
            if key not in self.provenance or key not in self.selected_raw:
                break
            if self.config.get("cost_key_basis") == "model_input_time":
                try:
                    publication = time_to_ns(self.provenance[key][0].cost_publication_stamp)
                    if now < publication <= now + self.freshness_ns:
                        break  # Clock coverage is admission, never a replacement receipt.
                except (ValueError, OverflowError):
                    pass  # The existing validation below rejects malformed time.
            raw, raw_receipt = self.raw.pop(key)
            selected, selected_receipt = self.selected_raw.pop(key)
            provenance, provenance_receipt = self.provenance.pop(key)
            self._remember(key)
            try:
                valid = (self._valid_provenance(provenance, now)
                    and now - min(raw_receipt, selected_receipt, provenance_receipt) <= self.freshness_ns
                    and list(selected.data) == list(raw.raw_cost))
            except (ValueError, OverflowError):
                valid = False
            if not valid:
                self._report_fault("invalid_source_provenance")
                continue
            model = time_to_ns(provenance.model_input_stamp)
            if self.last_model_ns is not None and model <= self.last_model_ns:
                continue
            self.last_model_ns = model
            legacy = StampedFloat64MultiArray()
            legacy.header = "Robust Source Cost"
            legacy.timestamp = key
            legacy.data = list(raw.raw_cost)
            self.node._apply_cost(legacy, raw, v2_provenance=provenance)

    def publish_objective(self, provenance, raw, gaussian, affine, augmented, composition_ns):
        configuration = objective_configuration(self.node)
        key = digest(configuration)
        if key != self.objective_key:
            self.objective_revision += 1
            self.objective_key = key
        msg = ObjectiveCostSample()
        msg.schema_version = self.config['schema_version']
        msg.stamp = self.node.get_clock().now().to_msg()
        set_time(msg.time_origin, self.origin_ns)
        msg.run_id, msg.stream_contract_id = self.run_id, self.contract_id
        msg.frame_id = self.config["frame_id"]
        msg.source_sequence = provenance.source_sequence
        msg.model_input_stamp = deepcopy(provenance.model_input_stamp)
        set_time(msg.composition_stamp, composition_ns)
        msg.legacy_cost_source_timestamp_sec = provenance.legacy_cost_source_timestamp_sec
        msg.channel_count = len(raw)
        msg.objective_revision = self.objective_revision
        msg.objective_sha256 = key
        msg.registry_digest = digest(configuration["fills"])
        msg.affine_revision = max(
            (v["direction_revision"] for v in configuration["affine"]), default=0
        )
        msg.objective_config_json = canonical_json(configuration)
        msg.sensor_weight, msg.gaussian_weight, msg.affine_weight = configuration["weights"]
        msg.sensor_x_m, msg.sensor_y_m = list(provenance.sensor_x_m), list(provenance.sensor_y_m)
        msg.raw_cost = [float(v) for v in raw]
        msg.gaussian_cost = [float(v) for v in gaussian]
        msg.affine_cost = [float(v) for v in affine]
        msg.augmented_cost = [float(v) for v in augmented]
        msg.valid = True
        self.publisher.publish(msg)
