"""Robust-only paired PDE-history reset coverage for Phase 08.7 M4.2."""

from nav_msgs.msg import Odometry
import numpy as np
import pytest
import rclpy
from rclpy.parameter import Parameter
from ros_esc.pde_cost_history_node.pde_cost_history_script import (
    PDECostHistory,
)
from ros_esc.pde_history_node.pde_history_script import PDEHistory
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray


class Recorder:
    """Minimal publisher replacement."""

    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


def _state(state, run_id="m4-2"):
    message = AlgorithmState()
    message.state = int(state)
    message.state_valid = True
    message.run_id = run_id
    message.run_id_valid = True
    return message


def _pose(x_value, y_value):
    message = Odometry()
    message.pose.pose.position.x = float(x_value)
    message.pose.pose.position.y = float(y_value)
    return message


def _cost(value):
    message = StampedFloat64MultiArray()
    message.data = [float(value)]
    return message


def _robust_parameters():
    return [
        Parameter("algorithm_profile", value="robust_gaussian_v1"),
        Parameter("robust_search_epoch_reset_enabled", value=True),
        Parameter("n_buffer", value=8),
    ]


def test_paired_robust_histories_reset_once_on_each_search_entry():
    rclpy.init()
    position = PDEHistory(parameter_overrides=_robust_parameters())
    cost = PDECostHistory(parameter_overrides=_robust_parameters())
    position.pub = Recorder()
    cost.pub = Recorder()
    try:
        position.cb(_pose(1.0, 2.0))
        cost.cb(_cost(-1.0))
        assert np.all(position.U == [1.0, 2.0])
        assert np.all(cost.U == -1.0)

        search = _state(AlgorithmState.STATE_SEARCH)
        position.algorithm_state_cb(search)
        cost.algorithm_state_cb(search)
        assert position.search_epoch_reset_pending is True
        assert cost.search_epoch_reset_pending is True

        position.cb(_pose(3.0, 4.0))
        cost.cb(_cost(-2.0))
        assert np.all(position.U == [3.0, 4.0])
        assert np.all(cost.U == -2.0)
        assert position.search_epoch_reset_pending is False
        assert cost.search_epoch_reset_pending is False
        assert len(position.pub.messages) == 1
        assert len(cost.pub.messages) == 2

        position.algorithm_state_cb(search)
        cost.algorithm_state_cb(search)
        assert position.search_epoch_reset_pending is False
        assert cost.search_epoch_reset_pending is False

        recenter = _state(AlgorithmState.STATE_RECENTER)
        position.algorithm_state_cb(recenter)
        cost.algorithm_state_cb(recenter)
        position.algorithm_state_cb(search)
        cost.algorithm_state_cb(search)
        assert position.search_epoch_reset_pending is True
        assert cost.search_epoch_reset_pending is True
    finally:
        position.destroy_node()
        cost.destroy_node()
        rclpy.shutdown()


def test_default_off_history_owner_retains_legacy_behavior():
    rclpy.init()
    position = PDEHistory(
        parameter_overrides=[Parameter("n_buffer", value=8)]
    )
    try:
        position.cb(_pose(1.0, 2.0))
        position.algorithm_state_cb(
            _state(AlgorithmState.STATE_SEARCH)
        )
        assert position.search_epoch_reset_enabled is False
        assert position.search_epoch_reset_pending is False
        assert np.all(position.U == [1.0, 2.0])
    finally:
        position.destroy_node()
        rclpy.shutdown()


def test_paired_reset_waits_for_next_finite_pose_and_cost():
    rclpy.init()
    position = PDEHistory(parameter_overrides=_robust_parameters())
    cost = PDECostHistory(parameter_overrides=_robust_parameters())
    position.pub = Recorder()
    cost.pub = Recorder()
    try:
        search = _state(AlgorithmState.STATE_SEARCH)
        position.algorithm_state_cb(search)
        cost.algorithm_state_cb(search)

        position.cb(_pose(float("nan"), 2.0))
        cost.cb(_cost(float("nan")))
        assert position.search_epoch_reset_pending is True
        assert cost.search_epoch_reset_pending is True
        assert position.pub.messages == []
        assert cost.pub.messages == []

        position.cb(_pose(5.0, 6.0))
        cost.cb(_cost(-3.0))
        assert position.search_epoch_reset_pending is False
        assert cost.search_epoch_reset_pending is False
        assert np.all(position.U == [5.0, 6.0])
        assert np.all(cost.U == -3.0)
        assert len(position.pub.messages) == 1
        assert len(cost.pub.messages) == 1
    finally:
        position.destroy_node()
        cost.destroy_node()
        rclpy.shutdown()


@pytest.mark.parametrize("owner", [PDEHistory, PDECostHistory])
def test_legacy_profile_rejects_enabled_robust_history_reset(owner):
    rclpy.init()
    try:
        with pytest.raises(ValueError, match="requires robust_gaussian_v1"):
            owner(
                parameter_overrides=[
                    Parameter(
                        "robust_search_epoch_reset_enabled", value=True
                    ),
                ]
            )
    finally:
        rclpy.shutdown()
