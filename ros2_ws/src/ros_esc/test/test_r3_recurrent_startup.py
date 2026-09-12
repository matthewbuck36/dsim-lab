"""Actual failed-launch parameter receipts must reach the selected moving owners."""
import json
from pathlib import Path

import pytest
import rclpy
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.stationary_fill_protocol import stationary_centroid_selected

FIXTURE = Path(__file__).with_name('fixtures')/'r3_recurrent_startup_parameters.json'
RECORDED = json.loads(FIXTURE.read_text())['ros_arguments']
OWNERS = {'gaussian_fill_node':GaussianFill, 'supervisor_node':SupervisorNode}


@pytest.mark.parametrize('name', list(OWNERS))
def test_actual_constructor_with_recorded_recurrent_parameters_selects_moving(name, monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID','203')
    monkeypatch.setenv('ROS_LOCALHOST_ONLY','1')
    rclpy.init(args=RECORDED[name])
    node = None
    try:
        node = OWNERS[name]()
        assert node.get_parameter('use_sim_time').value is True
        assert node.get_parameter('convergence_metric_mode').value == 'recurrent_geometry_v3'
        assert node.get_parameter('continuous_search_mode').value == 'rolling_gesc_v2'
        assert node.get_parameter('algorithm_profile').value == 'robust_gaussian_v1'
        if name == 'gaussian_fill_node':
            assert node.v2_fill is not None and not node.stationary_centroid_enabled
            assert node.stationary_fill is None
        else:
            assert node.moving_v2 is not None and node.stationary_centroid is None
            assert node.moving_v2.centered
            assert node.machine.config.verification_max_sec == 20.
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()


@pytest.mark.parametrize('name', list(OWNERS))
@pytest.mark.parametrize('override', ['use_sim_time:=False','algorithm_profile:=legacy'])
def test_actual_recorded_owners_reject_incompatible_recurrent_selection(name, override, monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID','203')
    monkeypatch.setenv('ROS_LOCALHOST_ONLY','1')
    rclpy.init(args=RECORDED[name]+['-p',override])
    node = None
    try:
        with pytest.raises(ValueError):
            node = OWNERS[name]()
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()


@pytest.mark.parametrize('mode,profile,sim', [
    ('stationary_v1','robust_gaussian_v1',False),
    ('rolling_gesc_v2','robust_gaussian_v1',False),
    ('rolling_gesc_v2','legacy',True),
    ('rolling_gesc_v2','robust_gaussian_v1',1),
    ('unknown','robust_gaussian_v1',True),
])
def test_recurrent_shared_selector_rejects_incompatible_mode_profile_or_clock(mode,profile,sim):
    with pytest.raises(ValueError):
        stationary_centroid_selected('recurrent_geometry_v3',mode,profile,sim)


def test_recurrent_moving_selection_does_not_enable_stationary_adapter():
    assert stationary_centroid_selected('recurrent_geometry_v3','rolling_gesc_v2',
                                        'robust_gaussian_v1',True) is False
