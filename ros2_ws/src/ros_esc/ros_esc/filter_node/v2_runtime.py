"""ROS adapter for synchronized rolling GESC in the existing custom filter."""

from collections import OrderedDict
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    AlgorithmState, GescDirectionDiagnostics, GescDirectionPolicyDiagnostics, ObjectiveCostSample,
    SourceSampleProvenance, StampedFloat64MultiArray,
    SynchronizedObservation as ObservationMessage,
)
from ros_esc.v2_stream import (
    canonical_json, relative_stamp_ns, set_time, stream_contract_id,
    time_to_ns, validate_mode_identity,
)
from ros_esc.v2_direction_policy import (
    THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY, POLICY_SCHEMA_VERSION, POLICY_DIAGNOSTICS_TOPIC,
    policy_descriptor, policy_config_sha256, validate_policy,
)
from ros_esc.filter_node.rolling_gesc import (
    AugmentedCost, DemodulatedSample, EncoderSample, ObjectiveIdentity,
    PoseSample, Provenance, RawCost, RollingGesc, RollingGescConfig, SourceSynchronizer,
    StreamIdentity, publication_time_tolerance_ns, wrap_angle,
)


def _time(value):
    return set_time(Time(), 0 if value is None else int(value))


def _number(value):
    return math.nan if value is None else float(value)


def _vector(value):
    return [math.nan, math.nan] if value is None else [float(v) for v in value]


def policy_diagnostic_message(direction, result, policy):
    """Detach a policy receipt from one exact direction publication; no clock read."""
    descriptor = policy_descriptor(policy)
    companion = GescDirectionPolicyDiagnostics()
    companion.policy_schema_version = POLICY_SCHEMA_VERSION
    companion.source_schema_version = direction.schema_version
    for name in ("stamp", "time_origin", "run_id", "stream_contract_id", "frame_id",
                 "diagnostic_sequence", "reset_sequence", "reset_reason",
                 "objective_revision", "objective_sha256", "registry_digest", "affine_revision",
                 "output_units", "rolling_start", "rolling_end", "mean_magnitude",
                 "mean_full", "coverage_valid", "output_valid", "fallback_used", "blend_allowed",
                 "fallback_reason"):
        setattr(companion, name, deepcopy(getattr(direction, name)))
    for name in ("source_sequence", "observation_id", "source_stamp", "cost_source_stamp"):
        setattr(companion, name, deepcopy(getattr(direction.observation, name)))
    companion.direction_policy = policy
    companion.policy_config_sha256 = policy_config_sha256(policy)
    companion.configured_mean_weight = descriptor["configured_mean_weight"]
    companion.actual_blend_weight = direction.blend_weight
    companion.selected_policy_qualified = direction.qualified
    for name in ("norm_denominator", "norm_error", "coherence", "coherence_lower", "coherence_upper"):
        setattr(companion, name, _number(getattr(result, name)))
    for name in ("norm_new_evaluations", "norm_window_evaluations", "warmup_valid", "coherence_available"):
        setattr(companion, name, getattr(result, name))
    companion.coherence_threshold = _number(descriptor.get("coherence_threshold"))
    margin = None
    if "mean_absolute_margin" in descriptor and result.mean_magnitude is not None:
        margin = math.sqrt(2.)*(descriptor["mean_absolute_margin"]
                               + descriptor["mean_relative_margin"]*result.mean_magnitude)
    companion.numerator_margin = _number(margin)
    companion.numerical_reason = result.coherence_reason
    return companion


class RollingFilterAdapter:
    """No motion publisher; legacy controller consumes valid filter outputs."""

    def __init__(self, node, args):
        self.node = node
        self.run_id = args.v2_run_id
        self.direction_policy = validate_policy(
            getattr(args, "v2_direction_policy", THREE_CYCLE_POLICY),
            continuous_search_mode=args.continuous_search_mode,
            algorithm_profile=node.algorithm_profile, use_sim_time=bool(args.use_sim_time),
        )
        self.config = validate_mode_identity(
            args.continuous_search_mode, node.algorithm_profile, self.run_id,
            args.v2_stream_config_json, simulation=bool(args.use_sim_time),
        )
        # This implementation's transform and two-component demodulation contract
        # is deliberately specific to the selected GESC, not arbitrary filters.
        selected = Path(__file__).parent / "filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
        if (not node.combine_data or not args.json_config
                or json.loads(Path(args.json_config).expanduser().read_text())
                != json.loads(selected.read_text())):
            raise ValueError("rolling GESC requires selected full-rotation filter configuration")
        for actual, key in ((args.inp_value_topic, "augmented_cost_topic"),
                            (args.inp_encoder_topic, "encoder_topic"),
                            (args.inp_timekeeping_topic, "timekeeper_topic")):
            if node.resolve_topic_name(actual) != self.config[key]:
                raise ValueError(f"V2 filter actual topic differs from descriptor: {key}")
        self.sync = SourceSynchronizer()
        self.rolling = RollingGesc(RollingGescConfig(direction_policy=self.direction_policy))
        self.identity = None
        self.origin_fault = False
        self.latest_pose = None
        self.state = None
        self.state_receipt_ns = None
        self.initial_state = np.array(node.z_vec, dtype=float, copy=True)
        self.previous_source_ns = None
        self.pending = OrderedDict()
        self.completed = OrderedDict()
        self.revision_hashes = OrderedDict()
        self.last_metadata = None
        self.diagnostic_sequence = 0
        self.publisher = node.create_publisher(
            GescDirectionDiagnostics, args.v2_direction_diagnostics_topic, 100
        )
        self.policy_publisher = node.create_publisher(
            GescDirectionPolicyDiagnostics, POLICY_DIAGNOSTICS_TOPIC, 100
        )
        self.subscriptions = [
            node.create_subscription(Odometry, self.config["pose_topic"], self.add_pose, 100),
            node.create_subscription(StampedFloat64MultiArray, self.config["raw_cost_topic"], self.add_raw, 100),
            node.create_subscription(SourceSampleProvenance, self.config["provenance_topic"], self.add_provenance, 100),
            node.create_subscription(ObjectiveCostSample, self.config["objective_cost_topic"], self.add_objective, 100),
            node.create_subscription(AlgorithmState, args.algorithm_state_topic, self.add_state, 100),
        ]
        self.timer = node.create_timer(0.05, self.poll)

    def _now(self):
        return self.node.get_clock().now().nanoseconds

    def _fault(self, reason):
        if (reason == "pending_receipt_expired"
                and self.config.get("cost_key_basis") == "model_input_time"):
            self._handle(self.sync.expire_pending(
                reason, extra_keys=tuple(self.pending), now_ns=self._now()))
            return
        self.pending.clear()
        self.rolling.invalidate(reason)
        self.sync.invalidate(reason)
        self.previous_source_ns = None
        self.node.z_vec = self.initial_state.copy()

    def set_timekeeper(self, msg):
        if msg.mode != "sim time" or not math.isfinite(msg.start_time) or msg.start_time < 0:
            self.origin_fault = True
            self._fault("invalid_time_origin")
            return
        origin = round(msg.start_time * 1e9)
        if self.identity is not None and origin != self.identity.time_origin_ns:
            self.origin_fault = True
            self._fault("changed_time_origin_requires_new_run")
            return
        identity = StreamIdentity(self.run_id, stream_contract_id(self.config, origin),
                                  self.config["frame_id"], origin, self.config["selected_channel"],
                                  self.config.get("cost_key_basis", "publication_time"))
        if self.identity != identity:
            self.identity = identity
            self._handle(self.sync.set_context(identity))

    def add_state(self, msg):
        now = self._now()
        try:
            valid = (msg.state_valid and msg.weights_valid and msg.run_id_valid
                     and msg.run_id == self.run_id
                     and -(500_000_000 if self.config.get("cost_key_basis") == "model_input_time" else 0)
                     <= now - time_to_ns(msg.stamp) <= 500_000_000)
        except ValueError:
            valid = False
        self.state = deepcopy(msg) if valid else None
        self.state_receipt_ns = now if valid else None

    def _active(self):
        return self.identity is not None and not self.origin_fault

    def add_pose(self, msg):
        if not self._active():
            return
        try:
            now = self._now()
            p, q = msg.pose.pose.position, msg.pose.pose.orientation
            norm = q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w
            if not math.isfinite(norm) or abs(norm - 1.0) > 1e-3:
                raise ValueError("invalid_pose_quaternion")
            yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
            pose = PoseSample(time_to_ns(msg.header.stamp), (float(p.x), float(p.y)),
                              yaw, now, msg.header.frame_id)
            batch = self.sync.add_pose(pose, now)
            if not batch.faults:
                self.latest_pose = pose
            else:
                self.latest_pose = None
            self._handle(batch)
        except (ValueError, OverflowError):
            self.latest_pose = None
            self._fault("invalid_pose")

    def add_encoder(self, msg):
        if not self._active():
            return
        try:
            if len(msg.data) != 1:
                raise ValueError("encoder_channel_count")
            now = self._now()
            sample = EncoderSample(relative_stamp_ns(self.identity.time_origin_ns, msg.timestamp),
                                   float(msg.data[0]), now)
            self._handle(self.sync.add_encoder(sample, now))
        except (ValueError, OverflowError):
            self._fault("invalid_encoder")

    def _store(self, key, name, msg, receipt_ns):
        if not math.isfinite(key) or key < 0:
            self._fault("invalid_cost_key")
            return False
        if self.sync.is_retired(key):
            fault = self.sync._clock(receipt_ns)
            if fault:
                self._handle(fault)
                return False
            # The expensive typed envelope/objective checks precede _store.
            # Raw/augmented arrays otherwise reach validation only at join.
            if name in ("raw", "augmented") and (
                    len(msg.data) != 1 or not all(math.isfinite(value) for value in msg.data)):
                self._fault("invalid_cost_values")
            if name == "objective":
                arrays = (msg.raw_cost, msg.gaussian_cost, msg.affine_cost,
                          msg.augmented_cost, msg.sensor_x_m, msg.sensor_y_m)
                try:
                    source = time_to_ns(msg.model_input_stamp)
                    composition = time_to_ns(msg.composition_stamp)
                    if (any(len(values) != 1 or not all(math.isfinite(v) for v in values)
                            for values in arrays)
                            or not self.identity.time_origin_ns <= source <= composition
                            or composition > receipt_ns+self.sync.config.freshness_ns
                            or abs(source-self.sync._absolute_key(key)) > publication_time_tolerance_ns(
                                self.identity.time_origin_ns, key, source)):
                        raise ValueError("invalid_retired_objective")
                    expected = (msg.sensor_weight*msg.raw_cost[0]
                                + msg.gaussian_weight*msg.gaussian_cost[0]
                                + msg.affine_weight*msg.affine_cost[0])
                    if not math.isfinite(expected) or not math.isclose(
                            expected, msg.augmented_cost[0], rel_tol=1e-12, abs_tol=1e-12):
                        raise ValueError("objective_arithmetic_mismatch")
                except (ValueError, TypeError, OverflowError):
                    self._fault("invalid_objective")
            return False
        if key in self.completed:
            previous = self.completed[key].get(name)
            if previous is not None and previous != msg:
                self._fault("conflicting_consumed_payload")
            return False
        if self.config.get("cost_key_basis") == "model_input_time":
            try:
                source = self.sync._absolute_key(key)
                uncertainty = publication_time_tolerance_ns(
                    self.identity.time_origin_ns, key, receipt_ns)
                if not -self.sync.config.freshness_ns-uncertainty <= receipt_ns-source <= self.sync.config.freshness_ns+uncertainty:
                    raise ValueError("stale_or_future_cost")
            except (TypeError, ValueError, OverflowError):
                self._fault("invalid_cost_key")
                return False
        record = self.pending.setdefault(key, {"receipt": receipt_ns, "receipts": {}})
        if name in record:
            if record[name] != msg:
                self.completed[key] = record
                self._fault("conflicting_pending_payload")
            return False
        record[name] = deepcopy(msg)
        record['receipts'][name] = receipt_ns
        if len(self.pending) > self.sync.config.max_pending_costs:
            self._fault("pending_capacity")
            return False
        return True

    def add_raw(self, msg):
        receipt = self._now()
        if not self._active():
            return
        key = float(msg.timestamp)
        if self._store(key, "raw", msg, receipt):
            self._handle(self.sync.add_raw_cost(RawCost(key, tuple(msg.data), receipt), self._now()))
            self._join(key)

    def add_augmented(self, msg):
        receipt = self._now()
        if not self._active():
            return
        key = float(msg.timestamp)
        if self._store(key, "augmented", msg, receipt):
            self._join(key)

    def _envelope(self, msg):
        return (msg.schema_version == self.config['schema_version'] and msg.run_id == self.run_id
                and msg.stream_contract_id == self.identity.stream_contract_id
                and msg.frame_id == self.identity.frame_id
                and time_to_ns(msg.time_origin) == self.identity.time_origin_ns)

    def add_provenance(self, msg):
        receipt = self._now()
        if not self._active():
            return
        try:
            key = float(msg.legacy_cost_source_timestamp_sec)
            if (self._envelope(msg) and self.config.get('cost_key_basis') == 'model_input_time'
                    and (not msg.model_input_stamp_valid or not msg.sensor_transform_valid)
                    and math.isfinite(key) and key >= 0):
                # Preserve a source-owner revocation even when its previously
                # valid packet is still in flight on another subscription.
                if self.completed.get(key, {}).get('poisoned'):
                    return
                self.completed[key] = {'poisoned': True}
                while len(self.completed) > 4096:
                    self.completed.popitem(last=False)
                self._handle(self.sync.invalidate_key(key))
                return
            if (not self._envelope(msg) or not msg.model_input_stamp_valid
                    or not msg.sensor_transform_valid or msg.channel_count != 1
                    or any(len(v) != 1 for v in
                           (msg.sensor_x_m, msg.sensor_y_m, msg.sensor_world_phase_rad))):
                raise ValueError("invalid_provenance")
            if self.sync.is_retired(key):
                source = Provenance(key, int(msg.source_sequence), time_to_ns(msg.model_input_stamp),
                                    time_to_ns(msg.cost_publication_stamp),
                                    (float(msg.sensor_x_m[0]), float(msg.sensor_y_m[0])),
                                    float(msg.sensor_world_phase_rad[0]), self.identity, receipt)
                self._handle(self.sync.add_provenance(source, self._now()))
                return
            if self._store(key, "provenance", msg, receipt):
                now = self._now()
                source = Provenance(key, int(msg.source_sequence), time_to_ns(msg.model_input_stamp),
                                    time_to_ns(msg.cost_publication_stamp),
                                    (float(msg.sensor_x_m[0]), float(msg.sensor_y_m[0])),
                                    float(msg.sensor_world_phase_rad[0]), self.identity, receipt)
                self._handle(self.sync.add_provenance(source, now))
                self._join(key)
        except (ValueError, OverflowError):
            self._fault("invalid_provenance")

    def add_objective(self, msg):
        receipt = self._now()
        if not self._active():
            return
        try:
            key = float(msg.legacy_cost_source_timestamp_sec)
            if not self._envelope(msg) or not msg.valid or msg.channel_count != 1:
                raise ValueError("invalid_objective_envelope")
            config = json.loads(msg.objective_config_json)
            actual_hash = hashlib.sha256(canonical_json(config).encode()).hexdigest()
            if (actual_hash != msg.objective_sha256
                    or config["weights"] != [msg.sensor_weight, msg.gaussian_weight, msg.affine_weight]
                    or hashlib.sha256(canonical_json(config["fills"]).encode()).hexdigest() != msg.registry_digest
                    or max((int(v["direction_revision"]) for v in config["affine"]), default=0) != msg.affine_revision
                    or msg.objective_revision <= 0):
                raise ValueError("invalid_objective_hash")
            previous = self.revision_hashes.get(msg.objective_revision)
            if previous is not None and previous != actual_hash:
                raise ValueError("conflicting_objective_revision")
            self.revision_hashes[msg.objective_revision] = actual_hash
            while len(self.revision_hashes) > 4096:
                self.revision_hashes.popitem(last=False)
            if self._store(key, "objective", msg, receipt):
                self._join(key)
        except (ValueError, KeyError, TypeError, OverflowError):
            self._fault("invalid_objective")

    def _join(self, key):
        record = self.pending.get(key)
        if record is None or any(k not in record for k in ("raw", "augmented", "provenance", "objective")):
            return
        raw, augmented, prov, obj = (record[k] for k in ("raw", "augmented", "provenance", "objective"))
        now = self._now()
        try:
            composition_stamp = time_to_ns(obj.composition_stamp)
            if (self.config.get("cost_key_basis") == "model_input_time"
                    and now < composition_stamp <= now + 500_000_000):
                return  # Retain original first receipt while local /clock catches up.
            arrays = (obj.raw_cost, obj.gaussian_cost, obj.affine_cost, obj.augmented_cost,
                      obj.sensor_x_m, obj.sensor_y_m)
            if (any(len(v) != 1 or not all(math.isfinite(x) for x in v) for v in arrays)
                    or list(raw.data) != list(obj.raw_cost)
                    or list(augmented.data) != list(obj.augmented_cost)
                    or obj.source_sequence != prov.source_sequence
                    or obj.model_input_stamp != prov.model_input_stamp
                    or list(obj.sensor_x_m) != list(prov.sensor_x_m)
                    or list(obj.sensor_y_m) != list(prov.sensor_y_m)
                    or not time_to_ns(prov.cost_publication_stamp) <= time_to_ns(obj.composition_stamp) <= now
                    or now - record["receipt"] > 500_000_000):
                raise ValueError("objective_sample_mismatch")
            expected = (obj.sensor_weight*obj.raw_cost[0] + obj.gaussian_weight*obj.gaussian_cost[0]
                        + obj.affine_weight*obj.affine_cost[0])
            if not math.isfinite(expected) or not math.isclose(expected, obj.augmented_cost[0], rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("objective_arithmetic_mismatch")
            self.pending.pop(key, None)
            self.completed[key] = record
            while len(self.completed) > 4096:
                self.completed.popitem(last=False)
            objective = ObjectiveIdentity(int(obj.objective_revision), obj.sensor_weight,
                                          obj.gaussian_weight, obj.affine_weight,
                                          obj.registry_digest, int(obj.affine_revision))
            contribution_receipts = [record['receipts'][name] for name in ('augmented', 'objective')]
            sample = AugmentedCost(key, tuple(augmented.data), objective,
                                   max(contribution_receipts), min(contribution_receipts))
            self._handle(self.sync.add_augmented(sample, now))
        except (ValueError, OverflowError):
            self._fault("objective_sample_mismatch")

    def _handle(self, batch):
        if batch.faults:
            reason = ",".join(f.reason for f in batch.faults)
            if (self.config.get("cost_key_basis") == "model_input_time"
                    and all(f.reason in ("pending_expired", "pending_receipt_expired")
                            for f in batch.faults)):
                self.sync.retire_keys(tuple(self.pending), self._now())
            self.pending.clear()
            self.rolling.invalidate(reason)
            self.previous_source_ns = None
            self.node.z_vec = self.initial_state.copy()
            return
        for obs in batch.observations:
            self._evaluate_filter(obs)

    def _evaluate_filter(self, obs):
        node = self.node
        now = self._now()
        metadata = self.completed.get(obs.legacy_cost_source_timestamp_sec, {}).get("objective")
        if metadata is None:
            self._fault("missing_atomic_objective")
            return
        source = obs.source_stamp_ns
        if self.previous_source_ns is not None and source - self.previous_source_ns > 500_000_000:
            self.rolling.invalidate("source_gap")
            node.z_vec = self.initial_state.copy()
            self.previous_source_ns = None
        dt = 0.0 if self.previous_source_ns is None else (source-self.previous_source_ns)*1e-9
        current = (source-self.identity.time_origin_ns)*1e-9
        inp = np.array([obs.augmented_cost, obs.demodulation_phase_rad], dtype=float)
        before = np.array(node.z_vec, dtype=float, copy=True)
        try:
            with np.errstate(all="raise"):
                output = np.asarray(node.custom_filter.filter_output(before, inp, current), dtype=float).reshape(-1)
                derivative = np.asarray(node.custom_filter.differential_equation(current, before, inp), dtype=float)
                after = before + dt*derivative
            if (not 0 <= dt <= .5 or output.size != 2
                    or not all(np.all(np.isfinite(v)) for v in (output, derivative, after))
                    or not node.custom_filter.valid_state(after)):
                raise ValueError("invalid_filter_numerics")
        except (ValueError, ArithmeticError, FloatingPointError):
            self._fault("invalid_filter_numerics")
            return
        node.z_vec = after
        node.prev_time = current
        self.previous_source_ns = source
        self.last_metadata = metadata
        self.rolling.update(DemodulatedSample(obs, (float(output[0]), float(output[1]))))
        # Numerical work may advance simulated time. Revalidate immediately
        # before publication, never refresh an output approved on an old clock.
        now = self._now()
        result = self._output_result(now)
        if result.output_valid:
            legacy = StampedFloat64MultiArray()
            legacy.header = "Filter Value"
            legacy.timestamp = (now-self.identity.time_origin_ns)*1e-9
            legacy.data = list(result.final_body)
            node.filter_publisher.publish(legacy)
        if node.enable_observability:
            node.publish_gesc_diagnostics(current, inp, output, before, derivative, after,
                                         dither_phase=obs.demodulation_phase_rad)
        self.publish_diagnostics(result)

    def _state_valid(self, now):
        return (self.state is not None and self.state_receipt_ns is not None
                and 0 <= now-self.state_receipt_ns <= 500_000_000
                and 0 <= now-time_to_ns(self.state.stamp) <= 500_000_000)

    def _output_result(self, now):
        if self.identity is not None and self.identity.cost_key_basis == "model_input_time":
            self.latest_pose = self.sync.latest_admitted_pose(now)
        pose = self.latest_pose
        result = self.rolling.evaluate(now, pose.yaw if pose else math.nan,
                                       pose.stamp_ns if pose else 0)
        if (not self._state_valid(now) or pose is None
                or not 0 <= now-pose.receipt_ns <= 500_000_000):
            return replace(result, output_valid=False, final_body=None, final_magnitude=None,
                           actual_blend_weight=0.0, fallback_reason="stale_state_or_pose")
        if self.state.state not in (AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM,
                                    AlgorithmState.STATE_DESIGN_OR_MERGE_FILL) and result.output_valid:
            q = result.instant_world
            # A meaningful mean can authorize a zero instantaneous vector in
            # moving SEARCH, but states retaining the instantaneous objective
            # cannot use that mean to authorize a weak fallback.
            if self.direction_policy == MOVING_CYCLE_POLICY and (
                    q is None or not all(math.isfinite(v) for v in q)
                    or not math.isfinite(math.hypot(*q)) or math.hypot(*q) <= 1e-6):
                return replace(result, output_valid=False, final_body=None, final_magnitude=None,
                               actual_blend_weight=0.0, fallback_used=False,
                               fallback_reason="state_instantaneous_direction_weak")
            c, s = math.cos(pose.yaw), math.sin(pose.yaw)
            body = (c*q[0]+s*q[1], -s*q[0]+c*q[1])
            result = replace(result, final_body=body, final_magnitude=math.hypot(*body),
                             actual_blend_weight=0.0, fallback_used=True,
                             fallback_reason="state_preserves_instantaneous_objective")
        return result

    def poll(self):
        if not self._active():
            self.publish_diagnostics(self.rolling.evaluate(self._now(), math.nan, 0))
            return
        now = self._now()
        for key, record in list(self.pending.items()):
            if now-record["receipt"] > 500_000_000 or now < record["receipt"]:
                self._fault("pending_receipt_expired")
                break
            self._join(key)
        self._handle(self.sync.poll(now))
        self.publish_diagnostics(self._output_result(now))

    def publish_diagnostics(self, result):
        msg = GescDirectionDiagnostics()
        msg.schema_version = self.config['schema_version']
        msg.stamp = self.node.get_clock().now().to_msg()
        msg.run_id = self.run_id
        msg.frame_id = self.config["frame_id"]
        if self.identity is not None:
            msg.time_origin = _time(self.identity.time_origin_ns)
            msg.stream_contract_id = self.identity.stream_contract_id
        self.diagnostic_sequence += 1
        msg.diagnostic_sequence = self.diagnostic_sequence
        msg.reset_sequence, msg.reset_reason = result.reset_sequence, result.reset_reason
        msg.algorithm_state_valid = bool(self._state_valid(self._now()))
        msg.algorithm_state = int(self.state.state) if self.state is not None else 0
        msg.blend_allowed = msg.algorithm_state_valid and msg.algorithm_state in (
            AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM,
            AlgorithmState.STATE_DESIGN_OR_MERGE_FILL)
        obs = result.observation
        if obs is not None:
            wire = ObservationMessage()
            wire.schema_version, wire.stamp = msg.schema_version, msg.stamp
            wire.time_origin, wire.run_id = msg.time_origin, msg.run_id
            wire.stream_contract_id, wire.frame_id = msg.stream_contract_id, msg.frame_id
            for name, value in (("source_stamp", obs.source_stamp_ns), ("cost_source_stamp", obs.cost_source_stamp_ns),
                                ("pose_left_stamp", obs.pose_left_stamp_ns), ("pose_right_stamp", obs.pose_right_stamp_ns),
                                ("encoder_left_stamp", obs.encoder_left_stamp_ns), ("encoder_right_stamp", obs.encoder_right_stamp_ns),
                                ("receipt_stamp", obs.receipt_stamp_ns)):
                setattr(wire, name, _time(value))
            wire.legacy_cost_source_timestamp_sec = obs.legacy_cost_source_timestamp_sec
            wire.oldest_receipt_stamp = _time(
                obs.oldest_receipt_stamp_ns if obs.oldest_receipt_stamp_ns is not None else obs.receipt_stamp_ns)
            wire.admission_stamp = _time(
                obs.admission_stamp_ns if obs.admission_stamp_ns is not None else obs.receipt_stamp_ns)
            wire.base_x_m, wire.base_y_m = obs.base_xy
            wire.base_yaw_rad = obs.base_yaw
            wire.sensor_phase_rad, wire.encoder_phase_rad = obs.demodulation_phase_rad, obs.encoder_phase
            wire.phase_disagreement_rad = wrap_angle(obs.demodulation_phase_rad-obs.encoder_phase)
            wire.demodulation_phase_reconstructed = obs.demodulation_phase_reconstructed
            wire.sensor_world_phase_rad = obs.sensor_world_phase
            wire.sensor_x_m, wire.sensor_y_m = obs.sensor_xy
            wire.raw_cost, wire.augmented_cost = obs.raw_cost, obs.augmented_cost
            wire.sync_error_sec = obs.sync_error_ns*1e-9
            wire.observation_id, wire.source_sequence = obs.observation_id, obs.source_sequence
            wire.objective_revision, wire.channel_index = obs.objective.revision, obs.identity.channel_index
            wire.raw_cost_valid = wire.augmented_cost_valid = wire.synchronized_valid = True
            wire.sensor_transform_observed = obs.sensor_transform_observed
            msg.observation = wire
            msg.objective_revision = obs.objective.revision
            msg.registry_digest, msg.affine_revision = obs.objective.registry_digest, obs.objective.affine_revision
            msg.sensor_weight, msg.gaussian_weight, msg.affine_weight = (
                obs.objective.sensor_weight, obs.objective.gaussian_weight, obs.objective.affine_weight)
            if self.last_metadata is not None:
                msg.objective_sha256 = self.last_metadata.objective_sha256
        msg.objective_kind, msg.output_units = "augmented", "cost_units_per_metre"
        msg.output_pose_stamp, msg.output_yaw_rad = _time(result.output_pose_stamp_ns), _number(result.output_yaw)
        msg.instant_body, msg.instant_world = _vector(result.instant_body), _vector(result.instant_world)
        msg.mean_world, msg.output_body = _vector(result.mean_world), _vector(result.final_body)
        msg.instant_magnitude, msg.mean_magnitude, msg.output_magnitude = (
            _number(result.instantaneous_magnitude), _number(result.mean_magnitude), _number(result.final_magnitude))
        msg.blend_weight = result.actual_blend_weight
        msg.rolling_start, msg.rolling_end = _time(result.rolling_start_ns), _time(result.rolling_end_ns)
        msg.rolling_duration_sec = result.rolling_duration_ns*1e-9
        msg.phase_start_rad, msg.phase_end_rad = _number(result.phase_start), _number(result.phase_end)
        msg.sector_counts, msg.rolling_sample_count = list(result.sector_counts), result.sample_count
        msg.max_sample_gap_sec = result.max_gap_ns*1e-9
        msg.completed_revolutions = result.completed_cycle_count
        msg.cycle_start = [_time(c.start_ns) for c in result.cycles]
        msg.cycle_end = [_time(c.end_ns) for c in result.cycles]
        msg.cycle_mean_world_x = [c.mean_world[0] for c in result.cycles]
        msg.cycle_mean_world_y = [c.mean_world[1] for c in result.cycles]
        msg.cycle_sector_counts = [v for c in result.cycles for v in c.sector_counts]
        msg.cycle_coverage_valid = [c.coverage_valid for c in result.cycles]
        msg.max_pair_angle_rad = _number(result.max_pair_angle_rad)
        msg.cycle_variability = _number(result.cycle_variability)
        msg.magnitude_floor = _number(result.effective_magnitude_floor)
        for name in ("mean_full", "coverage_valid", "cycles_valid", "qualified", "fallback_used", "output_valid"):
            setattr(msg, name, bool(getattr(result, name)))
        msg.fallback_reason = result.fallback_reason
        companion = policy_diagnostic_message(msg, result, self.direction_policy)
        self.publisher.publish(msg)
        self.policy_publisher.publish(companion)
