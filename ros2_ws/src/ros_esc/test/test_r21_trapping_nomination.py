"""Independent typed SEARCH certificate joins; no detector math is rerun."""
from copy import deepcopy
import pytest
from ros_esc_interfaces.msg import DetectorConfirmation
from ros_esc.convergence_detector_node.recurrent_contract import recurrent_nomination_errors
from ros_esc.v2_stream import set_time, time_to_ns
from test_r4_stationary_recurrent_protocol import confirmation as diagnostic_fixture, ORIGIN_NS, POSE


def nomination(branch='circle', *, origin_ns=ORIGIN_NS):
    diagnostic = diagnostic_fixture(branch)
    for name in ('stamp', 'receipt_stamp', 'source_stamp', 'epoch_started_at',
                 'history_start', 'history_end', 'persistence_start'):
        value = time_to_ns(getattr(diagnostic, name)) - ORIGIN_NS + origin_ns
        set_time(getattr(diagnostic, name), value)
    diagnostic.search_epoch = 2  # detector-local counter, deliberately different
    confirmation = DetectorConfirmation(schema_version=1, run_id=diagnostic.run_id,
        stream_contract_id='a'*64, frame_id=diagnostic.frame_id, search_epoch=5,
        context_sequence=7, detector_local_epoch=2, confirmation_sequence=1,
        metric_mode='recurrent_geometry_v3', history_kind='recurrent_geometry',
        source_stamp_kind='pose_input', valid=True, convergence_score_valid=True,
        convergence_score_m=diagnostic.score_m,
        center_x_m=diagnostic.center_x_m, center_y_m=diagnostic.center_y_m)
    confirmation.time_origin = deepcopy(diagnostic.epoch_started_at)
    for name in ('stamp', 'epoch_started_at', 'history_start', 'history_end'):
        setattr(confirmation, name, deepcopy(getattr(diagnostic, name)))
    confirmation.source_stamp = deepcopy(diagnostic.history_end)
    return confirmation, diagnostic


def errors(pair):
    return recurrent_nomination_errors(*pair, expected_source_pose_topic=POSE,
                                      epoch_start_ns=ORIGIN_NS)


@pytest.mark.parametrize('branch', ['static', 'circle', 'oscillation'])
def test_complete_original_branch_proof_and_distinct_epoch_counters(branch):
    pair = nomination(branch)
    assert errors(pair) == []
    assert pair[0].search_epoch != pair[1].search_epoch
    assert time_to_ns(pair[1].source_stamp) > time_to_ns(pair[0].source_stamp)


@pytest.mark.parametrize('side,field,value', [
    (0, 'schema_version', 2), (0, 'metric_mode', 'pde_mean_v1'),
    (0, 'history_kind', 'centroid_windows'), (0, 'source_stamp_kind', 'receipt'),
    (0, 'valid', False), (0, 'context_sequence', 0), (0, 'detector_local_epoch', 9),
    (0, 'legacy_r_mean_valid', True), (0, 'confirmation_sequence', 2),
    (0, 'stream_contract_id', ''), (0, 'center_x_m', 1.01),
    (1, 'run_id', 'other'), (1, 'frame_id', 'map'), (1, 'source_pose_topic', '/wrong'),
    (1, 'confirmed', False), (1, 'eligible', False), (1, 'history_valid', False),
    (1, 'persistence_count', 2), (1, 'maximum_source_gap_sec', .51),
    (1, 'drift_m_s', .007), (1, 'score_m', .001),
])
def test_typed_method_name_cannot_substitute_for_original_authority(side, field, value):
    pair = nomination()
    setattr(pair[side], field, value)
    assert errors(pair)


@pytest.mark.parametrize('side,field,offset', [
    (0, 'source_stamp', 1), (0, 'history_start', -1),
    (0, 'stamp', 500_000_001), (1, 'persistence_start', -1),
    (1, 'epoch_started_at', 1), (1, 'receipt_stamp', -1_000_000_000),
])
def test_history_and_original_time_bounds_are_not_rebased(side, field, offset):
    pair = nomination()
    target = getattr(pair[side], field)
    set_time(target, time_to_ns(target)+offset)
    assert errors(pair)


def test_pre_epoch_persistence_and_malformed_messages_reject():
    pair = nomination()
    assert recurrent_nomination_errors(*pair, expected_source_pose_topic=POSE,
                                      epoch_start_ns=ORIGIN_NS+1)
    assert recurrent_nomination_errors(None, None, expected_source_pose_topic=POSE)
