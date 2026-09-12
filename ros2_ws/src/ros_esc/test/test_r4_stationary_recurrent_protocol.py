"""Distinct stationary wire and immutable recurrent support/admission contract."""
from copy import deepcopy
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics, StationaryRecurrentFillRequest
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, recurrent_diagnostic_errors
from ros_esc.stationary_fill_protocol import (
    stationary_contract, stationary_diagnostic_errors, stationary_diagnostic_origin_errors,
    stationary_request_errors, stationary_request_sha256, stationary_centroid_selected,
)
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc.v2_lifecycle import message_payload
from test_q1_launch_frontend import parsed_launch  # noqa: F401

ORIGIN_NS = 10**12
RUN = 'r4-stationary-recurrent'
POSE = '/selected/odom'


def confirmation(branch='circle'):
    """Independent valid wire values; no detector fit is used to bless them."""
    width = 36. if branch == 'oscillation' else 30.
    count = 1 if branch == 'static' else 3
    limit = .005 if branch == 'static' else .006
    drift = 0. if branch == 'circle' else .001
    msg = RecurrentConvergenceDiagnostics(
        run_id=RUN, frame_id='odom', source_pose_topic=POSE, metric_mode=RECURRENT_MODE,
        search_epoch=1, confirmation_sequence=1, reset_sequence=1,
        branch=branch, support_duration_sec=width, evaluation_interval_sec=6.,
        persistence_count=count, persistence_required=count, score_scale_sec=12.,
        score_threshold_m=12.*limit, score_m=12.*drift, drift_m_s=drift,
        maximum_drift_m_s=limit, center_x_m=1., center_y_m=2.,
        confinement_radius_m=.02 if branch=='static' else .25, maximum_radius_m=.5,
        represented_duration_sec=width, maximum_source_gap_sec=.1,
        sample_count=round(width*10)+1, fit_residual_rms_m=.005,
        radius_difference_m=math.nan, period_sec=math.nan, amplitude_m=math.nan,
        perpendicular_rms_m=math.nan, axis_variance_ratio=math.nan,
        design_condition=math.nan, fit_rejection_reason='model_pass',
        source_valid=True, history_valid=True, metric_valid=True,
        confinement_valid=True, eligible=True, confirmed=True)
    for name,offset in (
        ('epoch_started_at',0), ('history_start',round((60.-width)*1e9)),
        ('history_end',60_000_000_000), ('source_stamp',60_009_000_000),
        ('receipt_stamp',60_000_000_000), ('stamp',60_100_000_000),
        ('persistence_start',round((60.-width-(count-1)*6.)*1e9)),
    ):set_time(getattr(msg,name),ORIGIN_NS+offset)
    if branch == 'circle':
        msg.arc_center_x_m=[1.,1.];msg.arc_center_y_m=[2.,2.]
        msg.arc_radius_m=[.25,.25];msg.arc_radial_rms_m=[.005,.005]
        msg.arc_net_angle_rad=[1.5,1.5];msg.radius_difference_m=0.
    elif branch == 'oscillation':
        msg.period_sec=24.;msg.amplitude_m=.2;msg.perpendicular_rms_m=.002
        msg.axis_variance_ratio=.005;msg.design_condition=8.
    return msg


def rehash(message):
    message.request_sha256=stationary_request_sha256(message)
    return message


def request(branch='circle', *, informed=False, redesign=False):
    msg=StationaryRecurrentFillRequest(schema_version=1,request_sequence=1,
        operation=2 if redesign else 1,confirmation=confirmation(branch),source_timestamp=70.)
    for name,offset in (('time_origin',0),('confirmation_received_at',60_100_000_000),
                        ('confirmation_accepted_at',60_200_000_000),
                        ('stamp',70_000_000_000),('expires_at',75_000_000_000)):
        set_time(getattr(msg,name),ORIGIN_NS+offset)
    if redesign:msg.target_fill_id,msg.target_cluster_id,msg.target_revision=7,3,2
    if informed:
        msg.candidate_evidence_valid=True;msg.candidate_cost_estimate=-1.
        msg.candidate_cost_mad=.1;msg.candidate_cost_uncertainty=.3
        msg.candidate_cost_lower=-1.3;msg.candidate_rotation_count=3
    return rehash(msg)


def errors(message, **kwargs):
    options=dict(expected_run_id=RUN,expected_frame_id='odom',expected_pose_topic=POSE,
                 origin_ns=ORIGIN_NS,expected_metric_mode=RECURRENT_MODE)
    options.update(kwargs)
    return stationary_request_errors(message,**options)


@pytest.mark.parametrize('branch',['static','circle','oscillation'])
@pytest.mark.parametrize('informed,redesign',[(False,False),(True,False),(False,True)])
def test_distinct_request_preserves_full_support_and_original_admission(branch,informed,redesign):
    msg=request(branch,informed=informed,redesign=redesign)
    assert errors(msg)==[]
    restored=deserialize_message(serialize_message(msg),StationaryRecurrentFillRequest)
    assert message_payload(restored)==message_payload(msg) and errors(restored)==[]
    assert restored.request_sha256==msg.request_sha256
    assert time_to_ns(restored.confirmation.source_stamp)-time_to_ns(restored.confirmation.history_end)==9_000_000
    assert time_to_ns(restored.stamp)-time_to_ns(restored.confirmation.stamp)>9_000_000_000
    assert restored.confirmation.persistence_start==msg.confirmation.persistence_start
    assert restored.source_timestamp==70.  # Request correlation, not model endpoint.


@pytest.mark.parametrize('mode',[None,'centroid_windows_v2','centroid_two_block_v2','unknown'])
def test_recurrent_request_requires_explicit_matching_selection(mode):
    assert errors(request(),expected_metric_mode=mode)


def test_old_wire_cannot_claim_recurrent_by_changing_only_metric_name():
    from test_q5_stationary_fill_protocol import request as old_request
    msg=old_request();msg.confirmation.metric_mode=RECURRENT_MODE
    assert any('type differs' in error for error in errors(rehash(msg)))


@pytest.mark.parametrize('field,value',[
    ('score_m',.001),('score_scale_sec',1.),('maximum_drift_m_s',.02),
    ('confinement_radius_m',.51),('persistence_count',2),('sample_count',3),
    ('arc_net_angle_rad',[1.,1.]),('arc_radial_rms_m',[.03,.03]),
    ('arc_radius_m',[.6,.6]),('center_x_m',1.2),
])
def test_rehashed_recurrent_claims_still_must_satisfy_fixed_branch_contract(field,value):
    msg=request();setattr(msg.confirmation,field,value)
    assert errors(rehash(msg))


def test_hash_covers_nested_persistence_even_before_semantic_validation():
    msg=request();set_time(msg.confirmation.persistence_start,ORIGIN_NS+19_000_000_000)
    assert 'stationary request hash mismatch' in errors(msg)


def test_persistence_before_timekeeper_rejects_even_with_valid_later_model_history():
    msg=request()
    for field in ('epoch_started_at','history_start','history_end','source_stamp',
                  'receipt_stamp','stamp','persistence_start'):
        value=getattr(msg.confirmation,field);set_time(value,time_to_ns(value)-19_000_000_000)
    for field in ('confirmation_received_at','confirmation_accepted_at'):
        value=getattr(msg,field);set_time(value,time_to_ns(value)-19_000_000_000)
    assert recurrent_diagnostic_errors([msg.confirmation],allow_clock_admission=True)==[]
    assert time_to_ns(msg.confirmation.history_start)>ORIGIN_NS
    expected=['stationary confirmation persistence_start precedes time origin']
    assert stationary_diagnostic_origin_errors(msg.confirmation,ORIGIN_NS,RECURRENT_MODE)==expected
    assert any(expected[0]==error for error in errors(rehash(msg)))


def test_request_cannot_refresh_its_original_subscriber_admission():
    msg=request();set_time(msg.confirmation_accepted_at,ORIGIN_NS+61_000_000_000)
    assert 'stationary confirmation original receipt/admission invalid' in errors(rehash(msg))


def test_redesign_cannot_introduce_candidate_evidence():
    assert errors(request(informed=True,redesign=True))


@pytest.mark.parametrize('field',['target_fill_id','target_cluster_id','target_revision'])
def test_redesign_binds_every_target_identifier(field):
    msg=request(redesign=True);setattr(msg,field,0)
    assert errors(rehash(msg))


def test_dispatcher_rejects_wrong_diagnostic_type_and_malformed_input():
    from test_q5_stationary_fill_protocol import confirmation as old_confirmation
    assert stationary_diagnostic_errors([old_confirmation()],expected_metric_mode=RECURRENT_MODE)
    assert stationary_diagnostic_errors([confirmation()],expected_metric_mode='centroid_windows_v2')
    assert stationary_diagnostic_errors([None],expected_metric_mode=RECURRENT_MODE)
    assert stationary_diagnostic_errors([],expected_metric_mode='unknown')


def test_selected_contract_names_and_default_legacy_route_remain_distinct():
    new=stationary_contract(RECURRENT_MODE);old=stationary_contract('centroid_windows_v2')
    assert new['request_type'].endswith('/StationaryRecurrentFillRequest')
    assert new['diagnostics_type'].endswith('/RecurrentConvergenceDiagnostics')
    assert new['request_topic']=='/gesc_gaussian/v2/stationary_recurrent_fill_requests'
    assert old['request_topic']=='/gesc_gaussian/v2/stationary_fill_requests'
    assert stationary_centroid_selected(RECURRENT_MODE,'stationary_v1','robust_gaussian_v1',True)
    assert not stationary_centroid_selected(RECURRENT_MODE,'rolling_gesc_v2','robust_gaussian_v1',True)
    for sim in (False,1):
        with pytest.raises(ValueError):stationary_centroid_selected(RECURRENT_MODE,'stationary_v1','robust_gaussian_v1',sim)


def test_shared_protocol_import_does_not_require_ros_runtime():
    package=Path(__file__).resolve().parents[1]
    program=('import sys; sys.path.insert(0,'+repr(str(package))+'); '
             'import ros_esc.stationary_fill_protocol; '
             'assert "rclpy" not in sys.modules; assert "ros_esc_interfaces" not in sys.modules')
    subprocess.run([sys.executable,'-I','-c',program],check=True,timeout=10)


def test_launch_forwards_both_selected_stationary_wires_to_existing_consumers():
    path=Path(__file__).resolve().parents[2]/'turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    tree=ET.parse(path);args={row.attrib['name']:row.attrib.get('default') for row in tree.findall('arg')}
    contract=stationary_contract(RECURRENT_MODE)
    assert args[contract['request_topic_parameter']]==contract['request_topic']
    commands=[row.attrib.get('cmd','') for row in tree.iter('executable')]
    for name in ('supervisor_node','gaussian_fill_node'):
        command=next(value for value in commands if 'ros2 run ros_esc '+name in value)
        assert '-p stationary_recurrent_fill_request_topic:=$(var stationary_recurrent_fill_request_topic)' in command
        assert '-p stationary_fill_request_topic:=$(var stationary_fill_request_topic)' in command
    supervisor=next(value for value in commands if 'ros2 run ros_esc supervisor_node' in value)
    assert '-p recurrent_diagnostics_topic:=$(var recurrent_diagnostics_topic)' in supervisor


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('pose', ['/r4/selected', '/gesc_gaussian/simulation/pose_delayed'])
def test_actual_launch_routes_selected_recurrent_stationary_pose(parsed_launch, mode, pose):
    from test_q7_launch_selection import parameters

    _, selected = parameters(parsed_launch, dict(
        algorithm_profile='robust_gaussian_v1', convergence_metric_mode=RECURRENT_MODE,
        continuous_search_mode=mode, algorithm_pose_topic=pose,
        gaussian_fill_pose_topic='/r4/legacy_fill'))
    assert selected['convergence_detector_node']['pose_topic'] == pose
    assert selected['supervisor_node']['pose_topic'] == pose
    assert selected['gaussian_fill_node']['pose_topic'] == (
        pose if mode == 'stationary_v1' else '/r4/legacy_fill')
