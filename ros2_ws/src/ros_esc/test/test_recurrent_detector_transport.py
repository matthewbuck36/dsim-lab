"""Real selected rolling detector and new diagnostic wire over local DDS."""
import math

from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, recurrent_diagnostic_errors
from test_m4_v6_centroid_heartbeat_transport import Transport, SEARCH, VERIFY
from ros_esc.v2_stream import time_to_ns


def test_recurrent_generated_diagnostic_epoch_confirmation_and_status_heartbeat():
    t = Transport(RECURRENT_MODE, True, False)
    try:
        assert t.node.get_parameter('centroid_invalid_status_heartbeat_enabled').value is False
        assert t.node.centroid_invalid_status_heartbeat_enabled
        for i in range(541):
            t.clock(1_000_000_000 + i * 100_000_000)
            t.context(SEARCH, epoch=1 if i == 0 else None)
            # Real selected-pose subscription and untouched core, fixed circle.
            from nav_msgs.msg import Odometry
            from ros_esc.v2_stream import set_time
            pose = Odometry(); set_time(pose.header.stamp, t.now_ns)
            pose.header.frame_id = 'odom'; pose.pose.pose.orientation.w = 1.
            angle = 2 * math.pi * i / 600
            pose.pose.pose.position.x = .25 * math.cos(angle)
            pose.pose.pose.position.y = .25 * math.sin(angle)
            t.pubs['pose'].publish(pose)
            t.until(lambda: any(m.source_valid and time_to_ns(m.source_stamp) == t.now_ns
                               for _, m in t.rows['diagnostic'][-8:]))
        t.until(lambda: len(t.rows['confirmation']) == 1)
        confirmed = [m for _, m in t.rows['diagnostic'] if m.confirmed]
        assert len(confirmed) == 1
        diag = confirmed[0]; confirmation = t.rows['confirmation'][0][1]
        assert diag.branch == 'circle' and diag.persistence_count == 3
        assert time_to_ns(diag.history_end) == 43_000_000_000
        assert confirmation.metric_mode == RECURRENT_MODE
        assert confirmation.history_kind == 'recurrent_geometry'
        assert confirmation.source_stamp_kind == 'pose_input'
        assert confirmation.history_start == diag.history_start and confirmation.history_end == diag.history_end
        assert confirmation.source_stamp == diag.history_end
        assert confirmation.convergence_score_m == diag.score_m
        assert confirmation.convergence_score_valid and not confirmation.legacy_r_mean_valid
        assert not confirmation.legacy_snapshot
        assert serialize_message(deserialize_message(serialize_message(diag), RecurrentConvergenceDiagnostics)) == serialize_message(diag)
        assert recurrent_diagnostic_errors([m for _, m in t.rows['diagnostic']], allow_clock_admission=True) == []
        before = len(t.rows['diagnostic'])
        for _ in range(5):
            t.clock(t.now_ns + 100_000_000); t.context(VERIFY); t.settle(.12, refresh_ready=True)
        outside = [m for _, m in t.rows['diagnostic'][before:] if m.reset_reason == 'outside_search']
        assert outside and all(not m.confirmed and not m.history_valid for m in outside)
        assert len(t.rows['confirmation']) == 1
    finally:
        t.close()
