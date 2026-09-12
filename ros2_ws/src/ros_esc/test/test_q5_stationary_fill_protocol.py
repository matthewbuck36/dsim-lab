"""Independent typed stationary-request contracts, using existing centroid wire."""
from copy import deepcopy

import pytest
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.v2_stream import set_time, time_to_ns
from test_v2_detector_contract import valid_centroid_diagnostic


ORIGIN_NS = 1_000_000_000_000
RUN = 'arm-b-fixture'
POSE = '/selected/odom'


def confirmation():
    message = valid_centroid_diagnostic()
    message.run_id, message.source_pose_topic = RUN, POSE
    for name in ('stamp', 'receipt_stamp', 'source_stamp', 'history_start', 'history_end'):
        field = getattr(message, name)
        set_time(field, time_to_ns(field)+ORIGIN_NS)
    for field in [*message.window_start, *message.window_end]:
        set_time(field, time_to_ns(field)+ORIGIN_NS)
    set_time(message.epoch_started_at, ORIGIN_NS)
    return message


def request(*, informed=False, redesign=False):
    from ros_esc_interfaces.msg import StationaryFillRequest
    from ros_esc.stationary_fill_protocol import stationary_request_sha256
    msg = StationaryFillRequest()
    msg.schema_version = 1
    msg.request_sequence = 1
    msg.operation = StationaryFillRequest.TARGETED_REDESIGN if redesign else StationaryFillRequest.CREATE
    msg.confirmation = confirmation()
    set_time(msg.time_origin, ORIGIN_NS)
    set_time(msg.confirmation_received_at, ORIGIN_NS+19_000_000_000)
    set_time(msg.confirmation_accepted_at, ORIGIN_NS+19_100_000_000)
    set_time(msg.stamp, ORIGIN_NS+25_000_000_000)
    set_time(msg.expires_at, ORIGIN_NS+30_000_000_000)
    msg.source_timestamp = 25.
    if redesign:
        msg.target_fill_id, msg.target_cluster_id, msg.target_revision = 7, 3, 2
    if informed:
        msg.candidate_evidence_valid = True
        msg.candidate_cost_estimate, msg.candidate_cost_mad = -1., .1
        msg.candidate_cost_uncertainty, msg.candidate_cost_lower = .3, -1.3
        msg.candidate_rotation_count = 3
    msg.request_sha256 = stationary_request_sha256(msg)
    return msg


def errors(message, **kwargs):
    from ros_esc.stationary_fill_protocol import stationary_request_errors
    expected = dict(expected_run_id=RUN, expected_frame_id='odom',
                    expected_pose_topic=POSE, origin_ns=ORIGIN_NS)
    expected.update(kwargs)
    return stationary_request_errors(message, **expected)


def rehash(message):
    from ros_esc.stationary_fill_protocol import stationary_request_sha256
    message.request_sha256 = stationary_request_sha256(message)
    return message


@pytest.mark.parametrize('informed,redesign', [(False, False), (True, False), (False, True)])
def test_valid_original_confirmation_survives_verification_age_and_nonzero_origin(informed, redesign):
    from ros_esc.stationary_fill_protocol import stationary_candidate_evidence
    msg = request(informed=informed, redesign=redesign)
    assert time_to_ns(msg.stamp)-time_to_ns(msg.confirmation.stamp) == 6_000_000_000
    assert errors(msg) == []
    restored = deserialize_message(serialize_message(msg), type(msg))
    assert restored == msg and errors(restored) == []
    assert restored.source_timestamp == 25.
    assert time_to_ns(restored.confirmation.source_stamp) == ORIGIN_NS+19_000_000_000
    evidence = stationary_candidate_evidence(restored)
    if informed:
        assert evidence.valid
        assert (evidence.estimate, evidence.mad, evidence.uncertainty,
                evidence.lower, evidence.rotation_count) == (-1., .1, .3, -1.3, 3)
    else:
        assert evidence is None


@pytest.mark.parametrize('field,value', [
    ('schema_version', 2), ('request_sequence', 0), ('operation', 99),
    ('target_fill_id', 1), ('target_cluster_id', 1), ('target_revision', 1),
    ('source_timestamp', 1_025.), ('source_timestamp', -1.),
])
def test_static_envelope_values_cannot_be_repaired_by_self_consistent_hash(field, value):
    msg = request()
    setattr(msg, field, value)
    assert errors(rehash(msg))


@pytest.mark.parametrize('field', ['target_fill_id', 'target_cluster_id', 'target_revision'])
def test_targeted_redesign_requires_each_explicit_target_identity(field):
    msg = request(redesign=True)
    setattr(msg, field, 0)
    assert errors(rehash(msg))


def test_targeted_redesign_never_introduces_candidate_amplitude_floor():
    msg = request(informed=True, redesign=True)
    assert errors(msg)


@pytest.mark.parametrize('field,value', [
    ('candidate_cost_mad', -.1), ('candidate_cost_uncertainty', -.1),
    ('candidate_cost_lower', -1.2), ('candidate_cost_lower', .1),
    ('candidate_rotation_count', 1),
])
def test_candidate_evidence_retains_existing_sign_interval_and_rotation_contract(field, value):
    msg = request(informed=True)
    setattr(msg, field, value)
    assert errors(rehash(msg))


@pytest.mark.parametrize('change', [
    'request_hash', 'run', 'frame', 'pose_topic', 'not_confirmed', 'not_eligible',
    'invalid_history', 'incomplete_windows', 'wrong_score', 'wrong_window_end',
    'wrong_displacement', 'source_after_publication', 'source_gap',
    'receipt_after_acceptance', 'accepted_before_publication', 'stale_at_acceptance',
    'origin_after_confirmation', 'request_before_acceptance', 'deadline_before_request',
])
def test_static_confirmation_and_original_admission_integrity(change):
    msg = request()
    diag = msg.confirmation
    if change == 'request_hash': msg.request_sha256 = 'b'*64
    elif change == 'run': diag.run_id = 'other'
    elif change == 'frame': diag.frame_id = 'map'
    elif change == 'pose_topic': diag.source_pose_topic = '/other/odom'
    elif change == 'not_confirmed': diag.confirmed = False
    elif change == 'not_eligible': diag.eligible = False
    elif change == 'invalid_history': diag.history_valid = False
    elif change == 'incomplete_windows': diag.completed_window_count = 5
    elif change == 'wrong_score': diag.score_m = .01
    elif change == 'wrong_window_end': diag.window_end[-1].nanosec += 1
    elif change == 'wrong_displacement': diag.displacement_m[0] = .01
    elif change == 'source_after_publication': diag.source_stamp.nanosec += 1
    elif change == 'source_gap': diag.maximum_source_gap_sec = .6
    elif change == 'receipt_after_acceptance': set_time(msg.confirmation_received_at, time_to_ns(msg.confirmation_accepted_at)+1)
    elif change == 'accepted_before_publication': set_time(msg.confirmation_accepted_at, time_to_ns(diag.stamp)-1)
    elif change == 'stale_at_acceptance': set_time(msg.confirmation_accepted_at, time_to_ns(diag.source_stamp)+500_000_001)
    elif change == 'origin_after_confirmation': set_time(msg.time_origin, time_to_ns(diag.stamp)+1)
    elif change == 'request_before_acceptance': set_time(msg.stamp, time_to_ns(msg.confirmation_accepted_at)-1)
    elif change == 'deadline_before_request': set_time(msg.expires_at, time_to_ns(msg.stamp)-1)
    if change != 'request_hash': rehash(msg)
    assert errors(msg), change


def test_request_hash_covers_immutable_payload_but_not_itself():
    from ros_esc.stationary_fill_protocol import stationary_request_sha256
    msg = request()
    original = msg.request_sha256
    msg.request_sha256 = 'ignored self field'
    assert stationary_request_sha256(msg) == original
    msg.confirmation_received_at.nanosec += 1
    assert stationary_request_sha256(msg) != original
    msg = request()
    msg.confirmation.reset_sequence += 1
    assert stationary_request_sha256(msg) != original


def test_original_confirmation_clock_lead_is_valid_only_after_coverage():
    msg = request()
    set_time(msg.confirmation.receipt_stamp, time_to_ns(msg.confirmation.source_stamp)-100_000_000)
    set_time(msg.confirmation_received_at, time_to_ns(msg.confirmation.stamp)-100_000_000)
    set_time(msg.confirmation_accepted_at, time_to_ns(msg.confirmation.stamp))
    assert errors(rehash(msg)) == []
    set_time(msg.confirmation_accepted_at, time_to_ns(msg.confirmation.stamp)-1)
    assert errors(rehash(msg))


def test_selected_positive_freshness_override_is_explicit():
    msg = request()
    set_time(msg.confirmation.receipt_stamp, time_to_ns(msg.confirmation.source_stamp)-750_000_000)
    set_time(msg.confirmation_accepted_at, time_to_ns(msg.confirmation.stamp))
    rehash(msg)
    assert errors(msg)
    assert errors(msg, pose_freshness_sec=1.) == []


def test_outer_subscriber_lease_is_fixed_even_with_longer_detector_pose_limit():
    msg = request()
    set_time(msg.confirmation_received_at, time_to_ns(msg.confirmation.stamp)-750_000_000)
    set_time(msg.confirmation_accepted_at, time_to_ns(msg.confirmation.stamp))
    assert errors(rehash(msg), pose_freshness_sec=1.)


@pytest.mark.parametrize('metric,mode,selected', [
    ('pde_mean_v1', 'stationary_v1', False),
    ('centroid_windows_v2', 'stationary_v1', True),
    ('pde_mean_v1', 'rolling_gesc_v2', False),
    ('centroid_windows_v2', 'rolling_gesc_v2', False),
])
def test_only_arm_b_selects_new_stationary_adapter(metric, mode, selected):
    from ros_esc.stationary_fill_protocol import stationary_centroid_selected
    assert stationary_centroid_selected(metric, mode, 'robust_gaussian_v1', True) is selected


@pytest.mark.parametrize('profile,sim', [('robust_gaussian_v1', False), ('legacy', True)])
def test_arm_b_cannot_silently_select_physical_or_nonrobust_mode(profile, sim):
    from ros_esc.stationary_fill_protocol import stationary_centroid_selected
    with pytest.raises(ValueError):
        stationary_centroid_selected('centroid_windows_v2', 'stationary_v1', profile, sim)
