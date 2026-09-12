"""Existing detector admits standalone stationary recurrent source/state authority."""
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE,recurrent_diagnostic_errors
from ros_esc.v2_stream import time_to_ns
from test_m4_v6_centroid_heartbeat_transport import Transport,SEARCH,VERIFY


def test_stationary_recurrent_publishes_once_without_moving_epoch_pipeline():
    t=Transport(RECURRENT_MODE,False,False)
    try:
        assert t.node.v2_binding is None and t.node.sub is None
        assert t.node.centroid_invalid_status_heartbeat_enabled
        for i in range(361):
            t.clock(1_000_000_000+i*100_000_000)
            t.context(SEARCH,epoch=1 if i==0 else None)
            t.pose()
        confirmed=[msg for _,msg in t.rows['diagnostic'] if msg.confirmed]
        assert len(confirmed)==1
        diagnostic=confirmed[0]
        assert diagnostic.branch=='static'
        assert time_to_ns(diagnostic.epoch_started_at)==1_000_000_000
        assert time_to_ns(diagnostic.history_end)==31_000_000_000
        assert time_to_ns(diagnostic.persistence_start)==1_000_000_000
        assert t.rows['confirmation']==[]
        before=len(t.rows['diagnostic'])
        for _ in range(5):
            t.clock(t.now_ns+100_000_000);t.context(VERIFY);t.settle(.12,refresh_ready=True)
        outside=[msg for _,msg in t.rows['diagnostic'][before:] if msg.reset_reason=='outside_search']
        assert outside and all(not msg.confirmed and not msg.history_valid for msg in outside)
        assert recurrent_diagnostic_errors([msg for _,msg in t.rows['diagnostic']],
            expected_metric_mode=RECURRENT_MODE,allow_clock_admission=True)==[]
        assert t.rows['confirmation']==[]
    finally:t.close()
