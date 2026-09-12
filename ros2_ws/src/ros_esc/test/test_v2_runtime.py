"""Cross-topic joins and existing-owner composition, using actual ROS messages."""

from copy import deepcopy
from itertools import permutations
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from ros_esc.config_parsing import parse_filter_config
from ros_esc.filter_node.v2_runtime import RollingFilterAdapter
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.modified_cost_node.v2_objective import (
    V2ObjectiveComposer, canonical_json, digest, objective_configuration,
)
from ros_esc.v2_stream import SUPPORTED_GEOMETRY, set_time, stream_contract_id
from ros_esc_interfaces.msg import (
    AlgorithmState, CostBreakdown, ObjectiveCostSample, SourceSampleProvenance,
    StampedFloat64MultiArray, Timekeeper,
)


FILTER = Path(__file__).parents[1] / "ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
CONFIG = dict(schema_version=1, raw_cost_topic="/test/raw", source_cost_topic="/test/source",
              augmented_cost_topic="/test/augmented", objective_cost_topic="/test/objective",
              provenance_topic="/test/provenance", pose_topic="/test/pose",
              encoder_topic="/test/encoder", timekeeper_topic="/test/timekeeper",
              frame_id="odom", selected_channel=0, sensor_geometry_config_sha256="a"*64,
              sensor_geometry=SUPPORTED_GEOMETRY)


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(deepcopy(msg))


class FakeNode:
    def __init__(self):
        self.now_ns = 0
        self.publishers = {}
        self.params = {"v2_run_id": "test-v2", "v2_stream_config_json": canonical_json(CONFIG)}

    def create_publisher(self, kind, topic, qos):
        publisher = Publisher()
        self.publishers[topic] = publisher
        return publisher

    def create_subscription(self, *args):
        return args

    def create_timer(self, *args):
        return args

    def get_clock(self):
        return SimpleNamespace(now=lambda: SimpleNamespace(
            nanoseconds=self.now_ns, to_msg=lambda: set_time(Time(), self.now_ns)))

    def get_parameter(self, name):
        return SimpleNamespace(value=self.params[name])

    def resolve_topic_name(self, name):
        return name


def make_state(now, state=AlgorithmState.STATE_SEARCH):
    msg = AlgorithmState()
    set_time(msg.stamp, now)
    msg.state = state
    msg.state_valid = msg.weights_valid = msg.run_id_valid = True
    msg.run_id = "test-v2"
    msg.sensor_weight, msg.gaussian_weight = 1., 1.
    return msg


def make_filter():
    node = FakeNode()
    node.algorithm_profile, node.combine_data, node.enable_observability = "robust_gaussian_v1", True, True
    node.custom_filter, node.z_vec = parse_filter_config(json.loads(FILTER.read_text()), [])
    node.filter_publisher = Publisher()
    node.instantaneous_receipts = []
    node.publish_gesc_diagnostics = lambda *args, **kw: node.instantaneous_receipts.append(deepcopy((args, kw)))
    args = SimpleNamespace(v2_run_id="test-v2", continuous_search_mode="rolling_gesc_v2",
                           v2_stream_config_json=canonical_json(CONFIG), use_sim_time=True,
                           json_config=str(FILTER), inp_value_topic=CONFIG["augmented_cost_topic"],
                           inp_encoder_topic=CONFIG["encoder_topic"], inp_timekeeping_topic=CONFIG["timekeeper_topic"],
                           v2_direction_diagnostics_topic="/test/direction", algorithm_state_topic="/test/state")
    adapter = RollingFilterAdapter(node, args)
    adapter.set_timekeeper(Timekeeper(mode="sim time", start_time=0.))
    return node, adapter


def make_composer():
    class ComposerNode(FakeNode):
        _apply_cost = ModifiedCost2D._apply_cost
        _bias_components_at_xy = ModifiedCost2D._bias_components_at_xy
        _gaussian_bias_at_xy = ModifiedCost2D._gaussian_bias_at_xy
        _affine_bias_at_xy = ModifiedCost2D._affine_bias_at_xy

        def _now_sec(self):
            return self.now_ns*1e-9

    node = ComposerNode()
    node.xy = None
    node.sensor_xy = np.array([[99., 99.]])  # Must not replace observed sample geometry.
    node.robust_profile, node.bias_all, node.enable_observability = True, True, False
    node.robust_terms = {1: dict(fill_id=1, cluster_id=1, revision=1, amplitude=2.,
                               center=np.array([0., 0.]), covariance=np.eye(2), inverse=np.eye(2))}
    node.robust_affine_terms = {}
    node.enable_affine_bias = True
    node.affine_decay_rate, node.affine_max_age, node.affine_min_norm = .0000005, 30., 1e-4
    node.algorithm_state = make_state(0)
    node.pub = Publisher()
    node.v2_composer = V2ObjectiveComposer(node)
    node.v2_composer.set_timekeeper(Timekeeper(mode="sim time", start_time=0.))
    return node, node.v2_composer


def messages(source_ns=1_000_000_000, cost=-1., theta=.4, xy=(.18, 0.)):
    publication_ns = source_ns+5_000_000
    key = publication_ns*1e-9
    raw = StampedFloat64MultiArray(timestamp=key, data=[cost])
    augmented = deepcopy(raw)
    prov = SourceSampleProvenance()
    prov.schema_version = 1
    prov.run_id, prov.stream_contract_id, prov.frame_id = "test-v2", stream_contract_id(CONFIG, 0), "odom"
    prov.source_sequence = source_ns+1
    set_time(prov.model_input_stamp, source_ns)
    set_time(prov.cost_publication_stamp, publication_ns)
    prov.legacy_cost_source_timestamp_sec = key
    prov.channel_count = 1
    prov.sensor_x_m, prov.sensor_y_m, prov.sensor_world_phase_rad = [xy[0]], [xy[1]], [theta]
    prov.model_input_stamp_valid = prov.sensor_transform_valid = True
    config = dict(schema_version=1, weights=[1., 1., 0.], bias_all_channels=True,
                  fills=[], affine=[], affine_enabled=True, affine_decay_rate=.0000005,
                  affine_max_age=30., affine_min_norm=1e-4)
    obj = ObjectiveCostSample()
    for name in ("schema_version", "run_id", "stream_contract_id", "frame_id", "time_origin",
                 "source_sequence", "model_input_stamp", "legacy_cost_source_timestamp_sec", "channel_count",
                 "sensor_x_m", "sensor_y_m"):
        setattr(obj, name, deepcopy(getattr(prov, name)))
    set_time(obj.composition_stamp, publication_ns+1_000_000)
    obj.objective_revision, obj.objective_config_json, obj.objective_sha256 = 1, canonical_json(config), digest(config)
    obj.registry_digest = digest([])
    obj.sensor_weight, obj.gaussian_weight = 1., 1.
    obj.raw_cost, obj.gaussian_cost, obj.affine_cost, obj.augmented_cost = [cost], [0.], [0.], [cost]
    obj.valid = True
    return dict(raw=raw, augmented=augmented, provenance=prov, objective=obj)


def support(node, adapter, source_ns, yaw=.2, theta=.4, state=AlgorithmState.STATE_SEARCH):
    node.now_ns = source_ns+20_000_000
    adapter.add_state(make_state(node.now_ns, state))
    for stamp in (source_ns-10_000_000, source_ns+10_000_000):
        pose = Odometry()
        pose.header.frame_id = "odom"
        set_time(pose.header.stamp, stamp)
        pose.pose.pose.orientation.z, pose.pose.pose.orientation.w = math.sin(yaw/2), math.cos(yaw/2)
        adapter.add_pose(pose)
        adapter.add_encoder(StampedFloat64MultiArray(timestamp=stamp*1e-9, data=[theta-yaw]))


@pytest.mark.parametrize("order", list(permutations(("raw", "augmented", "provenance", "objective"))))
def test_all_cost_topic_arrival_orders_require_actual_raw_and_preserve_filter(order):
    node, adapter = make_filter()
    support(node, adapter, 1_000_000_000)
    bundle = messages()
    for index, name in enumerate(order):
        getattr(adapter, "add_"+name)(bundle[name])
        if index < 3:
            assert not node.filter_publisher.messages
    assert len(node.filter_publisher.messages) == 1
    assert node.filter_publisher.messages[-1].data == pytest.approx(
        [2/.18*math.cos(.2), 2/.18*math.sin(.2)])
    diag = adapter.publisher.messages[-1]
    assert diag.observation.sensor_phase_rad == pytest.approx(.2)
    assert diag.observation.demodulation_phase_reconstructed
    assert diag.observation.source_stamp.sec == 1
    assert diag.output_valid and not diag.qualified and diag.fallback_used
    assert node.z_vec == pytest.approx([0.])  # First dt is zero, not time since origin.
    for name in order:
        getattr(adapter, "add_"+name)(bundle[name])
    assert len(node.filter_publisher.messages) == 1


def test_stale_inputs_never_refresh_filter_heartbeat_and_origin_change_latches():
    node, adapter = make_filter()
    support(node, adapter, 1_000_000_000)
    for name, msg in messages().items():
        getattr(adapter, "add_"+name)(msg)
    count = len(node.filter_publisher.messages)
    node.now_ns += 600_000_000
    adapter.poll()
    assert len(node.filter_publisher.messages) == count
    assert not adapter.publisher.messages[-1].output_valid
    adapter.set_timekeeper(Timekeeper(mode="sim time", start_time=2.))
    assert adapter.origin_fault
    adapter.poll()
    assert len(node.filter_publisher.messages) == count


def test_filter_work_cannot_publish_after_source_expires():
    node, adapter = make_filter()
    support(node, adapter, 1_000_000_000)
    old = node.custom_filter.filter_output

    def delayed(*args):
        answer = old(*args)
        node.now_ns += 600_000_000
        return answer

    node.custom_filter.filter_output = delayed
    for name, msg in messages().items():
        getattr(adapter, "add_"+name)(msg)
    assert not node.filter_publisher.messages
    assert not adapter.publisher.messages[-1].output_valid


def test_invalid_support_discards_adapter_half_join_and_later_samples_recover():
    node, adapter = make_filter()
    support(node, adapter, 1_000_000_000)
    adapter.add_raw(messages()["raw"])
    assert adapter.pending
    adapter.add_encoder(StampedFloat64MultiArray(timestamp=1., data=[math.nan]))
    assert not adapter.pending
    support(node, adapter, 1_100_000_000)
    for name, msg in messages(1_100_000_000).items():
        getattr(adapter, "add_"+name)(msg)
    assert len(node.filter_publisher.messages) == 1


def test_composer_malformed_source_time_is_rejected_without_timer_exception():
    node, composer = make_composer()
    node.now_ns = 1_020_000_000
    node.algorithm_state = make_state(node.now_ns)
    bundle = messages()
    bundle["provenance"].model_input_stamp.sec = -1
    composer.add_selected_raw(bundle["raw"])
    composer.add_provenance(bundle["provenance"])
    composer.add_raw(CostBreakdown(source_timestamp=bundle["raw"].timestamp,
                                  source_timestamp_valid=True, raw_cost_valid=True,
                                  channel_count=1, raw_cost=[-1.]))
    assert not node.pub.messages
    assert composer.last_fault_reason == "invalid_source_provenance"


@pytest.mark.parametrize("fault", ["geometry", "raw", "augmented", "objective_hash", "identity"])
def test_inconsistent_atomic_receipts_do_not_publish(fault):
    node, adapter = make_filter()
    support(node, adapter, 1_000_000_000)
    bundle = messages()
    if fault == "geometry":
        bundle["objective"].sensor_x_m = [44.]
    elif fault == "raw":
        bundle["raw"].data = [-2.]
    elif fault == "augmented":
        bundle["augmented"].data = [-2.]
    elif fault == "objective_hash":
        bundle["objective"].objective_sha256 = "b"*64
    else:
        bundle["provenance"].run_id = "other-run"
    for name, msg in bundle.items():
        getattr(adapter, "add_"+name)(msg)
    assert not node.filter_publisher.messages


@pytest.mark.parametrize("provenance_first", [True, False])
def test_composer_uses_exact_observed_geometry_and_atomic_law(provenance_first):
    node, composer = make_composer()
    node.now_ns = 1_020_000_000
    node.algorithm_state = make_state(node.now_ns)
    bundle = messages(xy=(0., 0.))
    composer.add_selected_raw(bundle["raw"])
    raw = CostBreakdown(source_timestamp=bundle["raw"].timestamp, source_timestamp_valid=True,
                        raw_cost_valid=True, channel_count=1, raw_cost=[-1.])
    calls = [(composer.add_raw, raw), (composer.add_provenance, bundle["provenance"])]
    if provenance_first:
        calls.reverse()
    calls[0][0](calls[0][1])
    assert not node.pub.messages
    calls[1][0](calls[1][1])
    assert node.pub.messages[-1].data == pytest.approx([1.])
    receipt = composer.publisher.messages[-1]
    assert receipt.gaussian_cost == pytest.approx([2.])
    assert list(receipt.sensor_x_m) == [0.] and receipt.objective_revision == 1
    assert receipt.objective_sha256 == digest(objective_configuration(node))
    assert receipt.objective_sha256 == digest(json.loads(receipt.objective_config_json))


def test_objective_identity_tracks_law_not_same_weight_state_or_decay_clock():
    node, composer = make_composer()
    node.now_ns = 1_020_000_000
    node.algorithm_state = make_state(node.now_ns)
    config = objective_configuration(node)
    node.now_ns += 1_000_000_000
    node.algorithm_state = make_state(node.now_ns, AlgorithmState.STATE_VERIFY_EXTREMUM)
    assert objective_configuration(node) == config
    node.robust_terms[1]["revision"] += 1
    assert objective_configuration(node) != config


def test_runtime_preserves_averaging_on_same_objective_state_and_disables_escape_blend():
    node, adapter = make_filter()
    for index in range(1, 301):
        stamp = index*50_000_000
        theta = 2*math.pi*(stamp*1e-9)/3
        state = AlgorithmState.STATE_SEARCH if index < 290 else AlgorithmState.STATE_VERIFY_EXTREMUM
        support(node, adapter, stamp, yaw=.2, theta=theta, state=state)
        for name, msg in messages(stamp, cost=math.cos(theta), theta=theta).items():
            getattr(adapter, "add_"+name)(msg)
    diag = adapter.publisher.messages[-1]
    assert diag.qualified and diag.blend_weight == .5
    assert diag.completed_revolutions >= 4
    adapter.add_state(make_state(node.now_ns, AlgorithmState.STATE_ESCAPE_REPULSE))
    adapter.poll()
    escape = adapter.publisher.messages[-1]
    assert escape.output_valid and not escape.blend_allowed
    assert escape.blend_weight == 0.
    assert escape.output_body == pytest.approx([
        math.cos(.2)*escape.instant_world[0]+math.sin(.2)*escape.instant_world[1],
        -math.sin(.2)*escape.instant_world[0]+math.cos(.2)*escape.instant_world[1]])
