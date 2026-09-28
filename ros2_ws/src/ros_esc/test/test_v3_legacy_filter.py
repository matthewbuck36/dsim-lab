"""Original filter mathematics, bounded failure handling, and source-age semantics."""
from copy import deepcopy
import json
from pathlib import Path
from types import MethodType, SimpleNamespace as NS

import numpy as np
import pytest

pytest.importorskip("rclpy")
pytest.importorskip("ros_esc_interfaces.msg")
from ros_esc_interfaces.msg import StampedFloat64MultiArray
from ros_esc.config_parsing import parse_filter_config
from ros_esc.filter_node.filter_node_script import (
    CustomFilter, advance_filter_state, parse_filter_arguments, MAX_REFINEMENT_EVALUATIONS,
)
from ros_esc.profiles import available_profiles, resolve_profile


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


def harness(custom_filter, initial):
    warnings = []
    node = NS(custom_filter=custom_filter, initial_state=np.asarray(initial, dtype=float),
              z_vec=np.asarray(initial, dtype=float), prev_time=0.0, last_input_stamp=None,
              start_time=100.0, encoder_value=None, encoder_timestamp=None, combine_data=False,
              filter_publisher=Publisher(), now=100.1, warnings=warnings)
    node.get_clock = lambda: NS(now=lambda: NS(nanoseconds=int(node.now * 1e9)))
    node.get_logger = lambda: NS(warning=warnings.append)
    node.get_parameter = lambda key: NS(value=True)
    for name in ("_fresh", "_reset"):
        setattr(node, name, MethodType(getattr(CustomFilter, name), node))
    return node


def sample(stamp, data=(1.0,)):
    msg = StampedFloat64MultiArray()
    msg.timestamp = float(stamp)
    msg.data = [float(value) for value in data]
    return msg


@pytest.mark.parametrize("profile", available_profiles())
def test_valid_original_filter_trace_retains_pre_step_euler_output(profile):
    config = json.loads(Path(resolve_profile(profile)["config_paths"]["filter"]).read_text())
    actual, initial = parse_filter_config(deepcopy(config), [])
    reference, expected_state = parse_filter_config(deepcopy(config), [])
    expected_state = np.asarray(expected_state)
    node = harness(actual, initial)
    node.combine_data = True
    previous = 0.0
    for stamp in (0.01, 0.02, 0.03):
        node.now = 100 + stamp
        CustomFilter.encoder_value_callback(node, sample(stamp, (.3,)))
        values = np.array([-.5, .3])
        expected_output = reference.filter_output(expected_state, values, stamp)
        expected_state = expected_state + (stamp - previous) * reference.differential_equation(stamp, expected_state, values)
        assert reference.valid_state(expected_state)
        CustomFilter.input_value_callback(node, sample(stamp, (-.5,)))
        np.testing.assert_allclose(node.filter_publisher.messages[-1].data, expected_output)
        np.testing.assert_allclose(node.z_vec, expected_state)
        assert node.filter_publisher.messages[-1].timestamp == stamp
        previous = stamp


def test_refinement_has_at_most_64_total_derivative_evaluations():
    calls = []
    def derivative(*args):
        calls.append(args[0])
        return np.array([1.0])
    bad = NS(valid_state=lambda state: False, differential_equation=derivative)
    first = derivative(.1, np.zeros(1), np.ones(1))
    with pytest.raises(ValueError, match="64-evaluation budget"):
        advance_filter_state(bad, 0, .1, np.ones(1), np.zeros(1), first)
    assert len(calls) <= MAX_REFINEMENT_EVALUATIONS == 64
    assert len(calls) == 55  # next full original-order attempt needs eleven evaluations


def test_original_first_successful_refinement_order_is_preserved():
    calls = []
    def derivative(time, state, inputs):
        calls.append(time)
        return -10 * np.asarray(state)
    stable = NS(valid_state=lambda state: bool((state > 0).all()), differential_equation=derivative)
    state = np.ones(1)
    result = advance_filter_state(stable, 0, .15, np.ones(1), state, derivative(.15, state, None))
    np.testing.assert_allclose(result, [.0625])  # two Euler substeps, each factor .25
    np.testing.assert_allclose(calls, [.15, .15, .225])


def test_bad_state_drops_sample_resets_and_recovers_without_duplicate_publish():
    valid = [False]
    custom = NS(filter_output=lambda state, inputs, time: inputs[:1],
                differential_equation=lambda *args: np.array([1.0]),
                valid_state=lambda state: valid[0])
    node = harness(custom, [0])
    CustomFilter.input_value_callback(node, sample(.1))
    assert not node.filter_publisher.messages and node.warnings
    np.testing.assert_allclose(node.z_vec, [0])
    valid[0] = True
    node.now = 100.2
    CustomFilter.input_value_callback(node, sample(.2))
    assert len(node.filter_publisher.messages) == 1
    CustomFilter.input_value_callback(node, sample(.2))
    CustomFilter.input_value_callback(node, sample(.19))
    assert len(node.filter_publisher.messages) == 1


def test_stale_and_nonfinite_inputs_do_not_renew_and_long_gap_resets():
    custom = NS(filter_output=lambda state, inputs, time: state.copy(),
                differential_equation=lambda *args: np.ones(1), valid_state=lambda state: True)
    node = harness(custom, [2])
    node.combine_data = True
    CustomFilter.encoder_value_callback(node, sample(.1))
    CustomFilter.input_value_callback(node, sample(.1))
    assert len(node.filter_publisher.messages) == 1
    node.now = 102.0
    CustomFilter.input_value_callback(node, sample(2.0))  # stale encoder
    CustomFilter.encoder_value_callback(node, sample(2.0))
    CustomFilter.input_value_callback(node, sample(2.0, (float("nan"),)))
    assert node.last_input_stamp == .1
    CustomFilter.input_value_callback(node, sample(2.0))
    assert node.filter_publisher.messages[-1].data[0] == 2  # baseline after the gap
    np.testing.assert_allclose(node.z_vec, [2])
    assert len(node.filter_publisher.messages) == 2


def test_strict_clock_cli_preserves_original_append_encoder_alias():
    args = parse_filter_arguments(["/cost", "/encoder", "/time", "/filter", "--filter_file", "filter.json",
                                   "--append_encoder_data", "True", "--use-sim-time", "False"])
    assert args.combine_enc_data is True and args.use_sim_time is False
    with pytest.raises(SystemExit):
        parse_filter_arguments(["/cost", "/encoder", "/time", "/filter", "--filter_file", "filter.json",
                                "--use-sim-time", "maybe"])
