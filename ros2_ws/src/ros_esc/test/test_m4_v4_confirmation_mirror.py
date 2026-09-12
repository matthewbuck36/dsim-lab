"""Actual legacy buffer decisions through typed binding and recorded audit.

Generated ROS messages are serialized; one bounded DDS test uses the existing
detector and PDE owners. No bag or Gazebo is started. Synthetic PDE input
isolates publication semantics from field quality.
"""

from copy import deepcopy
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import PdeHistoryEvidence, StampedFloat64MultiArray, Timekeeper

from ros_esc.convergence_detector_node.convergence_detector_node_script import (
    CROSSING_COUNT, QUALIFIED_DWELL, ConvergenceDetector, QualifiedDwellPolicy,
)
from ros_esc.convergence_detector_node.v2_binding import V2DetectorBinding
from ros_esc.experiment_recording.v2_lifecycle_validation import TOPICS, lifecycle_stream_errors
from ros_esc.pde_history_node.v2_evidence import history_sha256
from ros_esc.v2_stream import set_time
from test_v2_epoch_binding import Host, Publisher, context, pose


class DetectorHost(Host):
    buffer_cb = ConvergenceDetector.buffer_cb
    _publish_confirmation = ConvergenceDetector._publish_confirmation
    _reset_detection_state = ConvergenceDetector._reset_detection_state

    def __init__(self, *, moving=True, policy=QUALIFIED_DWELL):
        super().__init__()
        del self.buffer_cb  # Use the actual detector callback, not Host's sink.
        self.continuous_mode='rolling_gesc_v2' if moving else 'stationary_v1'
        self.enable_observability=False
        self.observability_configuration_published=True
        self.search_gate=SimpleNamespace(active=True)
        self.k,self.N,self.th,self.b=3,9,.2,1.
        self.minimum_path_length_m,self.maximum_path_efficiency=.2,.5
        self.min_time_before_trigger=0.
        self.count_start=1
        self.reset_counter_after_event=True
        self.confirmation_policy=policy
        self.confirmation_dwell_sec=6.
        self.qualified_dwell_policy=QualifiedDwellPolicy(6.,.1)
        self._reset_detection_state()
        self.convergence_status_publisher=Publisher()
        self.pub_metric,self.pub_r,self.pub_count=Publisher(),Publisher(),Publisher()
        self.v2_binding=V2DetectorBinding(self) if moving else None

    def get_logger(self):
        return SimpleNamespace(info=lambda *args:None)


def production_messages(*, moving=True, policy=QUALIFIED_DWELL, epochs=1, steps=100):
    node=DetectorHost(moving=moving,policy=policy)
    keeper=Timekeeper(mode='sim time',start_time=0.)
    messages={node.config['timekeeper_topic']:[(0,keeper)],
              TOPICS['v2_search_epoch']:[],TOPICS['v2_pde_history_evidence']:[],
              node.config['pose_topic']:[]}
    if moving:node.v2_binding.binding.set_timekeeper(keeper)
    # Three repeated triangles have equal recent/old means and qualified motion.
    payload=[1.,2.,1.1,2.,1.,2.1]*3
    sequence=0
    for epoch in range(1,epochs+1):
        start=(epoch-1)*20_000_000_000
        messages[node.config['pose_topic']].append((start,pose(start,1.,2.)))
        if not moving:node._reset_detection_state()
        for step in range(steps):
            sequence+=1;node.now_ns=start+1_000_000_000+step*100_000_000
            ctx=context(node,epoch=epoch,sequence=sequence,start=start)
            messages[TOPICS['v2_search_epoch']].append((node.now_ns,ctx))
            h=PdeHistoryEvidence(schema_version=1,run_id=ctx.run_id,
                stream_contract_id=ctx.stream_contract_id,frame_id=ctx.frame_id,
                search_epoch=epoch,context_sequence=sequence,history_sequence=sequence,valid=True)
            h.epoch_started_at=deepcopy(ctx.started_at)
            for field,value in [('stamp',node.now_ns),('input_start',start),
                                ('input_end',node.now_ns),('latest_input_receipt',node.now_ns)]:
                set_time(getattr(h,field),value)
            h.history=StampedFloat64MultiArray(timestamp=node.now_ns*1e-9,data=payload)
            h.history_sha256=history_sha256(h)
            messages[TOPICS['v2_pde_history_evidence']].append((node.now_ns,deepcopy(h)))
            messages[node.config['pose_topic']].append((node.now_ns,pose(node.now_ns,1.,2.)))
            if moving:
                node.v2_binding.binding.receive_context(ctx)
                node.v2_binding.receive_history(h)
            else:node.buffer_cb(h.history)
    messages[TOPICS['convergence_status']]=list(enumerate(node.convergence_status_publisher.messages))
    messages['/convergence_event']=list(enumerate(node.pub.messages))
    messages[TOPICS['v2_detector_confirmation']]=list(enumerate(
        node.v2_binding.publisher.messages if moving else []))
    identity={'run_id':'epoch-test','stream_config':node.config}
    return node,messages,identity


def wire_audit(messages,identity):
    roundtripped={topic:[(stamp,deserialize_message(serialize_message(msg),type(msg)))
                        for stamp,msg in records] for topic,records in messages.items()}
    return lifecycle_stream_errors(roundtripped,identity,metric_mode='pde_mean_v1')


def test_actual_buffer_dwell_confirmation_has_exact_canonical_mirror():
    node,messages,identity=production_messages()
    assert len(node.pub.messages)==1
    assert len(node.v2_binding.publisher.messages)==1
    errors,metrics=wire_audit(messages,identity)
    event=node.pub.messages[0];typed=node.v2_binding.publisher.messages[0]
    status=[msg for msg in node.convergence_status_publisher.messages if msg.timestamp==event.timestamp]
    evidence=os.environ.get('M4_MIRROR_EVIDENCE')
    if evidence:
        with Path(evidence).open('x') as stream:
            json.dump(dict(errors=errors,metrics=metrics,event=list(event.data),
                status=[list(msg.data) for msg in status],typed=list(typed.legacy_snapshot),
                source_timestamp=event.timestamp,status_count=len(node.convergence_status_publisher.messages)),stream,indent=2)
    assert errors==[],errors
    assert len(status)==1
    assert list(status[0].data)==list(event.data)==list(typed.legacy_snapshot)
    assert status[0].data[-1]==0.
    assert metrics['counts']['confirmations']==1
    assert metrics['counts']['candidate_snapshots']==0
    assert metrics['counts']['commands']==0


@pytest.mark.parametrize('policy',[QUALIFIED_DWELL,CROSSING_COUNT])
def test_each_authoritative_epoch_has_one_exact_confirmation_without_losing_status(policy):
    node,messages,identity=production_messages(policy=policy,epochs=2)
    errors,metrics=wire_audit(messages,identity)
    assert errors==[],errors
    assert [m.search_epoch for m in node.v2_binding.publisher.messages]==[1,2]
    assert metrics['counts']['candidate_snapshots']==0
    statuses=node.convergence_status_publisher.messages
    # Startup/invalid callbacks remain silent. Every computed metric has exactly
    # one status, including crossing_count's no-previous-metric/noncrossing paths.
    assert [m.timestamp for m in statuses]==[m.timestamp for m in node.pub_metric.messages]
    assert len({m.timestamp for m in statuses})==len(statuses)
    assert all(m.header=='CONVERGENCE_STATUS' and len(m.data)==8 for m in statuses)
    for event,typed in zip(node.pub.messages,node.v2_binding.publisher.messages):
        status=next(m for m in statuses if m.timestamp==event.timestamp)
        assert list(status.data)==list(event.data)==list(typed.legacy_snapshot)
        assert status.data[-1]==0.
    assert any(m.data[-1]==1. for m in statuses)


@pytest.mark.parametrize('policy',[QUALIFIED_DWELL,CROSSING_COUNT])
def test_stationary_status_keeps_historical_predecision_counter(policy):
    node,_,_=production_messages(moving=False,policy=policy)
    assert node.pub.messages
    statuses=node.convergence_status_publisher.messages
    assert [m.timestamp for m in statuses]==[m.timestamp for m in node.pub_metric.messages]
    for event in node.pub.messages:
        status=next(m for m in statuses if m.timestamp==event.timestamp)
        assert list(status.data[:-1])==list(event.data[:-1])
        assert status.data[-1]==1. and event.data[-1]==0.


def test_nonconfirming_moving_dwell_keeps_ordinary_canonical_status():
    node,messages,identity=production_messages(steps=30)
    assert not node.pub.messages and not node.v2_binding.publisher.messages
    assert len(node.convergence_status_publisher.messages)==29
    assert all(m.data[-1]==1. for m in node.convergence_status_publisher.messages)
    errors,metrics=wire_audit(messages,identity)
    assert errors==[],errors
    assert metrics['counts']['confirmations']==metrics['counts']['candidate_snapshots']==0


@pytest.mark.parametrize('mutation',['missing','count','center'])
def test_strict_canonical_mirror_rejection_survives_producer_fix(mutation):
    node,messages,identity=production_messages()
    stamp=node.pub.messages[0].timestamp
    if mutation=='missing':
        messages[TOPICS['convergence_status']]=[
            row for row in messages[TOPICS['convergence_status']] if row[1].timestamp!=stamp]
    else:
        target=next(m for _,m in messages[TOPICS['convergence_status']] if m.timestamp==stamp)
        target.data[7 if mutation=='count' else 3]+=1.
    errors,metrics=wire_audit(messages,identity)
    assert errors==['V2 lifecycle confirmation: legacy confirmation snapshot lacks canonical observation mirror']
    assert metrics['counts']['confirmations']==0


def test_actual_dds_pde_detector_status_event_and_typed_confirmation_match(monkeypatch):
    # Extend the existing real-owner transport fixture's driver with observation
    # subscriptions. Its PDE/detector inputs, bounded spin and two epochs remain
    # unchanged; no parallel node implementation or repaired output is used.
    import time
    from nav_msgs.msg import Odometry
    from ros_esc_interfaces.msg import DetectorConfirmation, SearchEpochContext
    from test_v2_stream import descriptor
    import test_v2_epoch_transport as transport
    captured={}
    original=transport.Node
    def driver(*args,**kwargs):
        node=original(*args,**kwargs)
        for topic,kind in [
            (TOPICS['v2_search_epoch'],SearchEpochContext),
            (TOPICS['v2_detector_confirmation'],DetectorConfirmation),
            (TOPICS['v2_pde_history_evidence'],PdeHistoryEvidence),
            (TOPICS['convergence_status'],StampedFloat64MultiArray),
            ('/convergence_event',StampedFloat64MultiArray),
            ('/epoch_transport/pose',Odometry),('/epoch_transport/timekeeper',Timekeeper),
        ]:
            captured[topic]=[]
            node.create_subscription(kind,topic,
                lambda message,selected=topic:captured[selected].append((time.monotonic_ns(),message)),10)
        return node
    monkeypatch.setattr(transport,'Node',driver)
    transport.test_real_owners_preserve_metrics_and_bind_each_authoritative_epoch('pde_mean_v1',0)
    config=descriptor(2)
    config['pose_topic']='/epoch_transport/pose'
    config['timekeeper_topic']='/epoch_transport/timekeeper'
    errors,metrics=wire_audit(captured,{'run_id':'epoch-transport','stream_config':config})
    assert errors==[],errors
    assert metrics['counts']['confirmations']==2
    assert metrics['counts']['candidate_snapshots']==0
    statuses=[m for _,m in captured[TOPICS['convergence_status']]]
    assert len({m.timestamp for m in statuses})==len(statuses)
    for _,confirmation in captured[TOPICS['v2_detector_confirmation']]:
        matches=[s for s in statuses if list(s.data)==list(confirmation.legacy_snapshot)]
        assert len(matches)==1 and matches[0].data[-1]==0.
        assert any(list(e.data)==list(confirmation.legacy_snapshot)
                   for _,e in captured['/convergence_event'])
