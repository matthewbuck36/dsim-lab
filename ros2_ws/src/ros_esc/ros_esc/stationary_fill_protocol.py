"""Arm B request identity and static evidence; live authority stays in nodes."""

import math

from ros_esc.convergence_detector_node.centroid_contract import (
    CENTROID_METRIC_MODES, centroid_diagnostic_errors,
)
from ros_esc.convergence_detector_node.recurrent_contract import (
    RECURRENT_GEOMETRY_V3, RECURRENT_TOPIC, recurrent_diagnostic_errors,
)
from ros_esc.supervisor_node.state_machine import CandidateFillEvidence, ROBUST_PROFILE
from ros_esc.v2_lifecycle import FRESHNESS_NS, hash_payload, message_payload
from ros_esc.v2_stream import time_to_ns


STATIONARY_FILL_REQUEST_TOPIC = '/gesc_gaussian/v2/stationary_fill_requests'
STATIONARY_RECURRENT_FILL_REQUEST_TOPIC = '/gesc_gaussian/v2/stationary_recurrent_fill_requests'


def stationary_contract(metric_mode):
    """Return selected wire names without importing generated ROS messages."""
    if metric_mode == RECURRENT_GEOMETRY_V3:
        return dict(
            request_type='ros_esc_interfaces/msg/StationaryRecurrentFillRequest',
            request_topic=STATIONARY_RECURRENT_FILL_REQUEST_TOPIC,
            request_topic_parameter='stationary_recurrent_fill_request_topic',
            request_alias='stationary_recurrent_fill_requests',
            diagnostics_type='ros_esc_interfaces/msg/RecurrentConvergenceDiagnostics',
            diagnostics_topic=RECURRENT_TOPIC,
            diagnostics_topic_parameter='recurrent_diagnostics_topic',
            diagnostics_alias='recurrent_convergence_diagnostics')
    if metric_mode not in CENTROID_METRIC_MODES:
        raise ValueError('unsupported stationary detector metric mode')
    return dict(
        request_type='ros_esc_interfaces/msg/StationaryFillRequest',
        request_topic=STATIONARY_FILL_REQUEST_TOPIC,
        request_topic_parameter='stationary_fill_request_topic',
        request_alias='stationary_fill_requests',
        diagnostics_type='ros_esc_interfaces/msg/CentroidConvergenceDiagnostics',
        diagnostics_topic='/gesc_gaussian/v2/convergence_diagnostics',
        diagnostics_topic_parameter='convergence_diagnostics_topic',
        diagnostics_alias='centroid_convergence_diagnostics')


def stationary_diagnostic_errors(
    messages, expected_source_pose_topic=None, supervisor_run_ids=None,
    maximum_source_gap_sec=None, allow_clock_admission=False,
    expected_frame_id=None, pose_freshness_sec=.5, expected_metric_mode=None,
):
    """Check the configured diagnostic contract; missing selection stays legacy."""
    try:
        contract = stationary_contract(expected_metric_mode or CENTROID_METRIC_MODES[0])
        messages = list(messages)
        expected_type = contract['diagnostics_type'].rsplit('/', 1)[1]
        if any(type(message).__name__ != expected_type for message in messages):
            return ['stationary diagnostic type differs from selected contract']
        checker = (recurrent_diagnostic_errors if expected_metric_mode == RECURRENT_GEOMETRY_V3
                   else centroid_diagnostic_errors)
        return checker(
            messages, expected_source_pose_topic=expected_source_pose_topic,
            supervisor_run_ids=supervisor_run_ids,
            maximum_source_gap_sec=maximum_source_gap_sec,
            allow_clock_admission=allow_clock_admission,
            expected_frame_id=expected_frame_id, pose_freshness_sec=pose_freshness_sec,
            expected_metric_mode=expected_metric_mode)
    except (AttributeError, TypeError, ValueError, OverflowError) as error:
        return ['stationary diagnostic malformed: ' + str(error)]


def stationary_diagnostic_origin_errors(message, origin_ns, expected_metric_mode=None):
    """Bind every accepted support interval to the original Timekeeper origin."""
    try:
        stationary_contract(expected_metric_mode or CENTROID_METRIC_MODES[0])
        fields = ('history_start', 'persistence_start') if (
            expected_metric_mode == RECURRENT_GEOMETRY_V3) else ('history_start',)
        return ['stationary confirmation ' + name + ' precedes time origin'
                for name in fields if time_to_ns(getattr(message, name)) < origin_ns]
    except (AttributeError, TypeError, ValueError, OverflowError) as error:
        return ['stationary confirmation origin malformed: ' + str(error)]


def centroid_configuration_errors(confirmation, window_sec, epsilon_m, radius_m,
                                  expected_metric_mode=None):
    if expected_metric_mode is not None and (
            expected_metric_mode not in CENTROID_METRIC_MODES
            or confirmation.metric_mode != expected_metric_mode):
        return ['centroid metric mode differs from selection']
    pairs = ((confirmation.window_duration_sec, window_sec),
             (confirmation.epsilon_m, epsilon_m), (confirmation.maximum_radius_m, radius_m))
    if any(not math.isfinite(value) or not math.isfinite(expected) or expected <= 0
           or not math.isclose(value, expected, rel_tol=1e-12, abs_tol=1e-12)
           for value, expected in pairs):
        return ['centroid configuration differs from selection']
    return []


def stationary_centroid_selected(metric_mode, continuous_search_mode, algorithm_profile, use_sim_time):
    # Historical API name; both explicit positional contracts use these owners.
    if metric_mode == RECURRENT_GEOMETRY_V3:
        if (continuous_search_mode not in ('stationary_v1', 'rolling_gesc_v2')
                or algorithm_profile != ROBUST_PROFILE or use_sim_time is not True):
            raise ValueError('recurrent geometry requires selected robust simulation')
        return continuous_search_mode == 'stationary_v1'
    if metric_mode not in ('pde_mean_v1', *CENTROID_METRIC_MODES):
        raise ValueError('unsupported convergence_metric_mode')
    if continuous_search_mode not in ('stationary_v1', 'rolling_gesc_v2'):
        raise ValueError('unsupported continuous_search_mode')
    selected = metric_mode in CENTROID_METRIC_MODES and continuous_search_mode == 'stationary_v1'
    if selected and (algorithm_profile != ROBUST_PROFILE or use_sim_time is not True):
        raise ValueError('stationary centroid adapter requires robust simulation')
    return selected


def stationary_request_sha256(message):
    return hash_payload(message_payload(message, exclude=('request_sha256',)))


def stationary_candidate_evidence(message):
    if message.operation not in (message.CREATE, message.TARGETED_REDESIGN):
        raise ValueError('invalid stationary operation')
    if message.operation == message.TARGETED_REDESIGN and message.candidate_evidence_valid:
        raise ValueError('stationary redesign must not add candidate amplitude evidence')
    if not message.candidate_evidence_valid:
        return None
    evidence = CandidateFillEvidence(
        estimate=float(message.candidate_cost_estimate), mad=float(message.candidate_cost_mad),
        uncertainty=float(message.candidate_cost_uncertainty), lower=float(message.candidate_cost_lower),
        rotation_count=int(message.candidate_rotation_count))
    if not evidence.valid:
        raise ValueError('invalid stationary candidate evidence')
    return evidence


def stationary_request_errors(message, expected_run_id=None, expected_frame_id=None,
                              expected_pose_topic=None, origin_ns=None,
                              maximum_source_gap_sec=0.5, pose_freshness_sec=0.5,
                              expected_metric_mode=None):
    """Validate immutable claims without expiring accepted historical support."""
    errors = []
    try:
        contract = stationary_contract(expected_metric_mode or CENTROID_METRIC_MODES[0])
        if type(message).__name__ != contract['request_type'].rsplit('/', 1)[1]:
            errors.append('stationary request type differs from selected contract')
        if message.schema_version != 1 or message.request_sequence <= 0:
            errors.append('stationary request schema or sequence invalid')
        if message.request_sha256 != stationary_request_sha256(message):
            errors.append('stationary request hash mismatch')
        origin = time_to_ns(message.time_origin)
        publication, deadline = time_to_ns(message.stamp), time_to_ns(message.expires_at)
        received = time_to_ns(message.confirmation_received_at)
        accepted = time_to_ns(message.confirmation_accepted_at)
        confirmation = message.confirmation
        diagnostic_stamp = time_to_ns(confirmation.stamp)
        if origin_ns is not None and origin != origin_ns:
            errors.append('stationary request time origin mismatch')
        if not origin <= publication < deadline:
            errors.append('stationary request publication/deadline invalid')
        correlation = (publication - origin) * 1e-9
        if (not math.isfinite(message.source_timestamp)
                or message.source_timestamp != correlation):
            errors.append('stationary request correlation differs from publication minus origin')
        # The B subscriber's fixed 500 ms admission lease is distinct from
        # the selected detector's configurable source-pose freshness below.
        if not (0 <= received <= accepted <= publication
                and diagnostic_stamp <= accepted
                and accepted - received <= FRESHNESS_NS
                and accepted - diagnostic_stamp <= FRESHNESS_NS):
            errors.append('stationary confirmation original receipt/admission invalid')
        errors.extend(stationary_diagnostic_origin_errors(
            confirmation, origin, expected_metric_mode))
        if not (confirmation.confirmed and confirmation.eligible and confirmation.source_valid
                and confirmation.history_valid and confirmation.metric_valid and confirmation.confinement_valid):
            errors.append('stationary request requires a complete confirmed diagnostic')
        errors.extend(stationary_diagnostic_errors(
            [confirmation], expected_source_pose_topic=expected_pose_topic,
            supervisor_run_ids=None if expected_run_id is None else {expected_run_id},
            maximum_source_gap_sec=maximum_source_gap_sec, allow_clock_admission=True,
            expected_frame_id=expected_frame_id, pose_freshness_sec=pose_freshness_sec,
            expected_metric_mode=expected_metric_mode))
        targets = (message.target_fill_id, message.target_cluster_id, message.target_revision)
        if message.operation == message.CREATE:
            if any(targets):
                errors.append('stationary CREATE carries a redesign target')
        elif message.operation == message.TARGETED_REDESIGN:
            if min(targets) <= 0:
                errors.append('stationary redesign target invalid')
        else:
            errors.append('stationary request operation invalid')
        stationary_candidate_evidence(message)
    except (AttributeError, TypeError, ValueError, OverflowError) as error:
        errors.append('stationary request malformed: ' + str(error))
    return errors
