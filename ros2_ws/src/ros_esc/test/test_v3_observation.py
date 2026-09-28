import math

from ros_esc.gesc_v3.observation import ObservationBuilder
from ros_esc.gesc_v3.records import Pose


def test_observed_support_interpolates_wrapped_phase_and_preserves_unknown_time():
    source = ObservationBuilder('sensor')
    source.add_pose(Pose(1, 0, 0, 0))
    source.add_pose(Pose(1.04, .04, 0, 0))
    source.add_phase(1, 2*math.pi-.1)
    source.add_phase(1.04, .1)
    source.add_cost(1.02, -1, 1.03)
    obs = source.take(1.04)
    assert obs is not None and obs.pose.x == .02
    assert abs(math.sin(obs.phase)) < 1e-12
    assert math.isnan(obs.acquisition_uncertainty)
    assert obs.timestamp_basis == 'receipt'
    assert obs.receipt_stamp == 1.03 and obs.stamp == 1.02
    assert obs.device_sequence is None


def test_lost_support_does_not_poison_next_sample_or_refresh_duplicate():
    source = ObservationBuilder('sensor')
    source.add_pose(Pose(1, 0, 0, 0))
    source.add_phase(1, 0)
    source.add_cost(1.2, -1, 1.2)
    assert source.take(1.3) is None
    assert source.take(1.8) is None
    source.add_pose(Pose(2, .1, 0, 0))
    source.add_phase(2, 1)
    assert source.add_cost(2, -2, 2.01)
    assert not source.add_cost(2, -2, 2.05)
    recovered = source.take(2.05)
    assert recovered.receipt_stamp == 2.01
    assert recovered.sequence == 2
    assert source.take(2.06) is None


def test_frame_conflict_is_integrity_fault_and_nearest_support_reports_age():
    source = ObservationBuilder('sensor')
    source.add_pose(Pose(1, 0, 0, 0))
    source.add_phase(1, 0)
    source.add_cost(1.03, -1, 1.03)
    obs = source.take(1.03)
    assert obs.pose_support_age > .029 and obs.phase_support_age > .029
    assert not source.add_pose(Pose(1.04, 0, 0, 0, 'different'))
    assert source.fault == 'pose_frame_changed'
