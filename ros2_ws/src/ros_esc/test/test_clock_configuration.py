"""Regression tests for shared simulation/physical clock initialization."""

import sys
import time

import pytest
import rclpy
from rcl_interfaces.srv import SetParameters
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

from ros_esc.convergence_detector_node.convergence_detector_node_script import (
    ConvergenceDetector,
)
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from ros_esc.modified_cost_node.modified_cost_script import ModifiedCost2D
from ros_esc.pde_cost_history_node.pde_cost_history_script import (
    PDECostHistory,
)
from ros_esc.pde_history_node.pde_history_script import PDEHistory


OWNER_NAMES = (
    "modified_cost",
    "pde_history",
    "pde_cost_history",
    "convergence_detector",
    "gaussian_fill",
)


def _make_owner(owner_name):
    if owner_name == "modified_cost":
        return ModifiedCost2D()
    if owner_name == "pde_history":
        return PDEHistory(
            parameter_overrides=[Parameter("n_buffer", value=8)]
        )
    if owner_name == "pde_cost_history":
        return PDECostHistory(
            parameter_overrides=[Parameter("n_buffer", value=8)]
        )
    if owner_name == "convergence_detector":
        return ConvergenceDetector()
    if owner_name == "gaussian_fill":
        return GaussianFill()
    raise AssertionError(owner_name)


@pytest.mark.parametrize("owner_name", OWNER_NAMES)
@pytest.mark.parametrize(
    ("ros_args", "expected", "explicit"),
    (
        pytest.param([], True, False, id="legacy-default"),
        pytest.param(
            ["--ros-args", "-p", "use_sim_time:=false"],
            False,
            True,
            id="physical-false",
        ),
        pytest.param(
            ["--ros-args", "-p", "use_sim_time:=true"],
            True,
            True,
            id="explicit-simulation-true",
        ),
    ),
)
def test_shared_owner_preserves_startup_clock_selection(
    monkeypatch,
    owner_name,
    ros_args,
    expected,
    explicit,
):
    """All five owners retain explicit clocks and the historical default."""

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "clock_configuration_test",
            "/clock_test/input",
            "/clock_test/fill",
            "/clock_test/output",
        ],
    )
    rclpy.init(args=ros_args)
    node = None
    try:
        node = _make_owner(owner_name)
        assert node.get_parameter("use_sim_time").value is expected
        assert node._time_source.ros_time_is_active is expected
        assert (node._time_source._clock_sub is None) is (not expected)
        assert ("use_sim_time" in node._parameter_overrides) is explicit
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


def test_gaussian_fill_physical_clock_survives_parameter_enforcement(
    monkeypatch,
):
    """Repeated physical enforcement causes no live /clock destruction."""

    monkeypatch.setattr(sys, "argv", ["gaussian_fill_node"])
    rclpy.init(
        args=["--ros-args", "-p", "use_sim_time:=false"]
    )
    gaussian = GaussianFill()
    client_node = Node("clock_parameter_enforcement_client")
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(gaussian)
    executor.add_node(client_node)
    client = client_node.create_client(
        SetParameters,
        "/gaussian_fill/set_parameters",
    )
    try:
        assert gaussian.get_parameter("use_sim_time").value is False
        assert gaussian._time_source._clock_sub is None
        assert client.wait_for_service(timeout_sec=2.0)

        for _ in range(3):
            request = SetParameters.Request()
            request.parameters = [
                Parameter("use_sim_time", value=False).to_parameter_msg()
            ]
            future = client.call_async(request)
            deadline = time.monotonic() + 2.0
            while not future.done() and time.monotonic() < deadline:
                executor.spin_once(timeout_sec=0.05)
            assert future.done()
            assert future.result().results[0].successful

        for _ in range(20):
            executor.spin_once(timeout_sec=0.01)
        assert gaussian._time_source._clock_sub is None
    finally:
        executor.remove_node(client_node)
        executor.remove_node(gaussian)
        executor.shutdown(timeout_sec=1.0)
        client_node.destroy_node()
        gaussian.destroy_node()
        rclpy.shutdown()
