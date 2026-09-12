#!/usr/bin/env python3

"""Offline run-completeness validator for unified GESC/Gaussian recordings."""

import argparse
import hashlib
from bisect import bisect_right
import json
import math
from pathlib import Path
import sys

from rclpy.serialization import deserialize_message
import rosbag2_py
from rosidl_runtime_py.utilities import get_message
import yaml

from .record_run import (
    DEFAULT_TIMESTAMP_ORDERING,
    MULTI_PUBLISHER_TIMESTAMP_ORDERING,
    REQUIRED_METADATA,
    VALID_PROFILES_BY_MODE,
    atomic_json,
    expected_publisher_error,
    preauthorization_lifecycle_errors,
    require_selected_algorithm_topics,
    stationary_centroid_config_from_target,
    topic_evidence_contract_errors,
    v2_identity_from_metadata,
    v2_message_identity_error,
    v2_policy_identity_error,
)
from ros_esc.v2_stream import canonical_json, relative_stamp_ns, time_to_ns
from ros_esc.filter_node.rolling_gesc import publication_time_tolerance_ns
from .v2_lifecycle_validation import lifecycle_stream_errors
from .v2_direction_policy_validation import index_policy_companions, direction_policy_pair_errors
from ros_esc.convergence_detector_node.centroid_contract import (
    CENTROID_METRIC_MODES, centroid_diagnostic_errors,
)
from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC, validate_policy_metadata,
)


FORBIDDEN_CONSOLE_MARKERS = (
    "traceback (most recent call last)",
    "rclerror",
    "publisher's context is invalid",
    "failed to terminate",
)
MOTION_COVERAGE_ALIASES = {
    "source_cost",
    "cost_breakdown",
    "gesc_diagnostics",
    "control_diagnostics",
    "algorithm_state",
    "pose",
    "command_final",
    "command_array_final",
}
FILL_EVENT_TYPES = {20, 22, 23}
FILL_OWNER_EVENT_TYPES = set(range(20, 27))


def _stamp_nanoseconds(stamp):
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


def _message_stamp_nanoseconds(message):
    """Return a typed absolute ROS stamp, excluding legacy float timestamps."""

    if hasattr(message, "stamp"):
        return _stamp_nanoseconds(message.stamp)
    if hasattr(message, "header") and hasattr(message.header, "stamp"):
        return _stamp_nanoseconds(message.header.stamp)
    return None


def timestamp_regressions(values, tolerance_nanoseconds):
    """Return ordered pairs that regress beyond the configured tolerance."""

    regressions = []
    previous = None
    for current in values:
        if previous is not None and current + tolerance_nanoseconds < previous:
            regressions.append({"previous": previous, "current": current})
        previous = current
    return regressions


def centroid_stream_errors(
    diagnostic_records, clock_records, interval_start_ns, interval_end_ns,
    maximum_gap_sec, *, diagnostic_kind='centroid',
):
    """Check selected diagnostic coverage using simulated publication time.

    Bag ordering locates the clock at readiness boundaries. Neither endpoints
    nor internal gaps are compared in wall time, so real-time factor does not
    change this evidence gate. Invalid-history diagnostics still count as
    observations of the detector's state.
    """
    if (interval_start_ns is None or interval_end_ns is None
            or interval_end_ns < interval_start_ns):
        return [f'{diagnostic_kind} diagnostic readiness interval is unavailable']
    scaled_gap = maximum_gap_sec * 1e9
    if not math.isfinite(scaled_gap) or scaled_gap < 1:
        return [f'{diagnostic_kind} diagnostic coverage gap allowance is invalid']
    gap_ns = round(scaled_gap)
    clocks = sorted(
        (bag_stamp, _stamp_nanoseconds(message.clock))
        for bag_stamp, message in clock_records if message is not None
    )
    clock_bag_stamps = [stamp for stamp, _ in clocks]
    start_index = bisect_right(clock_bag_stamps, interval_start_ns) - 1
    end_index = bisect_right(clock_bag_stamps, interval_end_ns) - 1
    if start_index < 0 or end_index < 0:
        return [f'{diagnostic_kind} diagnostic coverage lacks a readiness boundary clock']
    start = clocks[start_index][1]
    end = clocks[end_index][1]
    if start > end:
        return [f'{diagnostic_kind} diagnostic simulated readiness time regressed']
    publications = sorted({
        _stamp_nanoseconds(message.stamp)
        for bag_stamp, message in diagnostic_records
        if message is not None and interval_start_ns <= bag_stamp <= interval_end_ns
    })
    if not any(start - gap_ns <= stamp <= end + gap_ns for stamp in publications):
        return [f'{diagnostic_kind} diagnostics do not cover the authorized interval']
    covered = [start, *(stamp for stamp in publications if start <= stamp <= end), end]
    if any(current - previous > gap_ns for previous, current in zip(covered, covered[1:])):
        return [f'{diagnostic_kind} diagnostics have a simulated publication coverage gap']
    return []


def v2_stream_contract_errors(messages, identity, direction_topic='/gesc_gaussian/v2/direction_diagnostics'):
    """Audit typed claims and exact source joins; this is not behavioral validation.

    Message receipts are bag observations, not a reconstruction of DDS callback
    scheduling. Invalid startup directions may be unbound until first origin.
    """
    errors = []
    config = identity['stream_config']
    if identity.get('direction_policy') is not None:
        try:
            validate_policy_metadata(identity['direction_policy'])
        except ValueError as exc:
            return ['V2 direction policy metadata: ' + str(exc)]
    def rows(topic):
        return [message for _, message in messages.get(topic, [])]
    origins = []
    for message in rows(config['timekeeper_topic']):
        try:
            if message is None or message.mode != 'sim time':
                raise ValueError('invalid simulation Timekeeper')
            origins.append(relative_stamp_ns(0, message.start_time))
        except (ValueError, TypeError, OverflowError):
            errors.append('V2 Timekeeper is invalid')
    if not origins or len(set(origins)) != 1:
        errors.append('V2 lacks one immutable recorded Timekeeper origin')
        return errors
    origin = origins[0]
    moving_policy = identity.get('direction_policy', {}).get('policy_name') == MOVING_CYCLE_POLICY
    companions = {}
    if moving_policy:
        companions, policy_errors = index_policy_companions(messages.get(POLICY_DIAGNOSTICS_TOPIC, []))
        errors.extend(policy_errors)
        if not companions:
            errors.append('V2 moving direction policy lacks recorded companion diagnostics')
        for companion in companions.values():
            unbound = (not companion.stream_contract_id and not companion.output_valid
                       and not companion.selected_policy_qualified and companion.observation_id == 0)
            error = v2_policy_identity_error(companion, identity, origin, allow_unbound=unbound)
            if error:
                errors.append(error)
        direction_keys = {(int(message.diagnostic_sequence), time_to_ns(message.stamp))
                          for message in rows(direction_topic) if message is not None}
        if companions.keys() - direction_keys:
            errors.append('V2 policy companion lacks its original direction publication')
    def envelope(message, allow_unbound=False):
        error = v2_message_identity_error(message, identity, origin, allow_unbound=allow_unbound)
        if error:
            errors.append(error)
        return error is None
    def finite(values):
        return all(math.isfinite(float(value)) for value in values)
    def close(left, right):
        return math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
    def index_legacy(topic):
        indexed = {}
        for message in rows(topic):
            if message is None or not math.isfinite(message.timestamp):
                continue
            key = float(message.timestamp)
            if key in indexed and indexed[key] != message:
                errors.append('V2 conflicting legacy duplicate: ' + topic)
            indexed[key] = message
        return indexed
    raw = index_legacy(config['raw_cost_topic'])
    augmented = index_legacy(config['augmented_cost_topic'])
    def support_records(topic, pose):
        indexed = {}
        for message in rows(topic):
            try:
                if pose:
                    stamp = time_to_ns(message.header.stamp)
                    p, q = message.pose.pose.position, message.pose.pose.orientation
                    if not finite((p.x, p.y, q.x, q.y, q.z, q.w)) or abs(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w-1) > 1e-3:
                        continue
                    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
                    value = (p.x, p.y, yaw, message.header.frame_id)
                else:
                    stamp = relative_stamp_ns(origin, message.timestamp)
                    if len(message.data) != 1 or not finite(message.data):
                        continue
                    value = tuple(message.data)
                if stamp in indexed and indexed[stamp] != value:
                    indexed[stamp] = None
                else:
                    indexed[stamp] = value
            except (ValueError, AttributeError, TypeError, OverflowError):
                continue
        return indexed
    pose_records = support_records(config['pose_topic'], True)
    encoder_records = support_records(config['encoder_topic'], False)
    def angle_delta(left, right):
        value = math.remainder(math.remainder(right,2*math.pi)-math.remainder(left,2*math.pi),2*math.pi)
        if abs(value) == math.pi:
            raise ValueError('ambiguous pi support interpolation')
        return value
    provenance = {}
    previous_sequence = 0
    for message in rows(config['provenance_topic']):
        if not envelope(message):
            continue
        try:
            key = float(message.legacy_cost_source_timestamp_sec)
            if not math.isfinite(key) or key < 0 or message.source_sequence <= 0:
                raise ValueError('invalid exact key or source sequence')
            if key in provenance and provenance[key] != message:
                raise ValueError('conflicting provenance duplicate')
            if key not in provenance and message.source_sequence <= previous_sequence:
                raise ValueError('source sequence did not increase')
            previous_sequence = max(previous_sequence, message.source_sequence)
            provenance[key] = message
            if message.model_input_stamp_valid:
                if not origin <= time_to_ns(message.model_input_stamp) <= time_to_ns(message.cost_publication_stamp) <= time_to_ns(message.stamp):
                    raise ValueError('model/publication source times disagree')
                if config.get('cost_key_basis') == 'model_input_time':
                    model_stamp = time_to_ns(message.model_input_stamp)
                    if abs(relative_stamp_ns(origin, key)-model_stamp) > publication_time_tolerance_ns(origin, key, model_stamp):
                        raise ValueError('acquisition key differs from model source time')
            if message.sensor_transform_valid:
                if (message.channel_count != 1 or any(len(values) != 1 for values in (message.sensor_x_m, message.sensor_y_m, message.sensor_world_phase_rad))
                        or not finite((*message.sensor_x_m, *message.sensor_y_m, *message.sensor_world_phase_rad))):
                    raise ValueError('valid transform claim lacks one finite observed channel')
        except (ValueError, TypeError, OverflowError) as exc:
            errors.append('V2 provenance: ' + str(exc))
    objectives = {}
    previous_revision, previous_digest = 0, None
    for message in rows(config['objective_cost_topic']):
        if not envelope(message):
            continue
        if not message.valid:
            continue
        try:
            key = float(message.legacy_cost_source_timestamp_sec)
            source = provenance.get(key)
            legacy_raw, legacy_augmented = raw.get(key), augmented.get(key)
            if source is None or legacy_raw is None or legacy_augmented is None:
                raise ValueError('atomic cost lacks selected raw/augmented/provenance join')
            if (not source.model_input_stamp_valid or not source.sensor_transform_valid
                    or source.source_sequence != message.source_sequence
                    or time_to_ns(source.model_input_stamp) != time_to_ns(message.model_input_stamp)
                    or list(source.sensor_x_m) != list(message.sensor_x_m)
                    or list(source.sensor_y_m) != list(message.sensor_y_m)):
                raise ValueError('objective cost differs from evaluated source geometry/time')
            if not time_to_ns(message.model_input_stamp) <= time_to_ns(message.composition_stamp) <= time_to_ns(message.stamp):
                raise ValueError('objective composition times disagree')
            arrays = (message.raw_cost, message.gaussian_cost, message.affine_cost, message.augmented_cost)
            weights = (message.sensor_weight, message.gaussian_weight, message.affine_weight)
            if message.channel_count != 1 or any(len(values) != 1 for values in arrays) or not finite((*weights, *(value for values in arrays for value in values))):
                raise ValueError('valid objective lacks one finite cost channel/weights')
            if list(message.raw_cost) != list(legacy_raw.data) or list(message.augmented_cost) != list(legacy_augmented.data):
                raise ValueError('atomic objective differs from legacy exact-key values')
            if not close(message.augmented_cost[0], sum(weight * values[0] for weight, values in zip(weights, arrays[:3]))):
                raise ValueError('augmented value differs from declared weighted composition')
            objective = json.loads(message.objective_config_json)
            digest = hashlib.sha256(canonical_json(objective).encode()).hexdigest()
            registry = hashlib.sha256(canonical_json(objective['fills']).encode()).hexdigest()
            if (digest != message.objective_sha256 or registry != message.registry_digest
                    or list(weights) != objective['weights'] or message.objective_revision <= 0):
                raise ValueError('objective law/digest/weights/revision inconsistent')
            if (message.objective_revision < previous_revision
                    or (previous_digest is not None and (message.objective_sha256 != previous_digest) != (message.objective_revision > previous_revision))):
                raise ValueError('objective revision does not match law changes')
            previous_revision, previous_digest = message.objective_revision, message.objective_sha256
            if key in objectives and objectives[key] != message:
                raise ValueError('conflicting atomic objective duplicate')
            objectives[key] = message
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            errors.append('V2 objective: ' + str(exc))
    previous_diagnostic = 0
    for message in rows(direction_topic):
        if message is None:
            errors.append('V2 undecodable direction diagnostic')
            continue
        unbound = not message.stream_contract_id and not message.output_valid and not message.qualified and not message.observation.synchronized_valid
        if not envelope(message, allow_unbound=unbound):
            continue
        try:
            if message.diagnostic_sequence <= previous_diagnostic:
                raise ValueError('diagnostic sequence did not increase')
            previous_diagnostic = message.diagnostic_sequence
            if moving_policy:
                companion = companions.get((int(message.diagnostic_sequence), time_to_ns(message.stamp)))
                errors.extend(direction_policy_pair_errors(message, companion))
            observation = message.observation
            if message.output_valid and not observation.synchronized_valid:
                raise ValueError('valid output lacks a synchronized observation')
            if observation.synchronized_valid:
                if not envelope(observation):
                    continue
                key = float(observation.legacy_cost_source_timestamp_sec)
                source, objective = provenance.get(key), objectives.get(key)
                if source is None or objective is None:
                    raise ValueError('synchronized observation lacks selected provenance/objective')
                if (observation.source_sequence != source.source_sequence
                        or time_to_ns(observation.source_stamp) != time_to_ns(source.model_input_stamp)
                        or time_to_ns(observation.cost_source_stamp) != time_to_ns(source.cost_publication_stamp)
                        or observation.objective_revision != objective.objective_revision
                        or observation.channel_index != 0
                        or not observation.sensor_transform_observed
                        or not observation.demodulation_phase_reconstructed
                        or not observation.raw_cost_valid or not observation.augmented_cost_valid
                        or observation.raw_cost != objective.raw_cost[0]
                        or observation.augmented_cost != objective.augmented_cost[0]
                        or observation.sensor_x_m != source.sensor_x_m[0]
                        or observation.sensor_y_m != source.sensor_y_m[0]
                        or observation.sensor_world_phase_rad != source.sensor_world_phase_rad[0]):
                    raise ValueError('synchronized observation differs from admitted source/objective')
                source_ns = time_to_ns(observation.source_stamp)
                for left, right in ((observation.pose_left_stamp, observation.pose_right_stamp), (observation.encoder_left_stamp, observation.encoder_right_stamp)):
                    left_ns, right_ns = time_to_ns(left), time_to_ns(right)
                    if not left_ns <= source_ns <= right_ns or max(source_ns-left_ns, right_ns-source_ns) > 50_000_000:
                        raise ValueError('observation lacks bounded source-time brackets')
                pl_ns, pr_ns = time_to_ns(observation.pose_left_stamp), time_to_ns(observation.pose_right_stamp)
                el_ns, er_ns = time_to_ns(observation.encoder_left_stamp), time_to_ns(observation.encoder_right_stamp)
                pl, pr = pose_records.get(pl_ns), pose_records.get(pr_ns)
                el, er = encoder_records.get(el_ns), encoder_records.get(er_ns)
                if any(value is None for value in (pl, pr, el, er)):
                    raise ValueError('claimed brackets lack unambiguous recorded selected inputs')
                if pl[3] != config['frame_id'] or pr[3] != config['frame_id']:
                    raise ValueError('recorded pose bracket frame mismatch')
                pf = 0. if pr_ns == pl_ns else (source_ns-pl_ns)/(pr_ns-pl_ns)
                ef = 0. if er_ns == el_ns else (source_ns-el_ns)/(er_ns-el_ns)
                expected_xy = [pl[i]+pf*(pr[i]-pl[i]) for i in range(2)]
                yaw = pl[2]+pf*angle_delta(pl[2],pr[2])
                phase = el[0]+ef*angle_delta(el[0],er[0])
                if (not all(close(a,b) for a,b in zip(expected_xy,(observation.base_x_m,observation.base_y_m)))
                        or not close(angle_delta(yaw,observation.base_yaw_rad),0)
                        or not close(angle_delta(phase,observation.encoder_phase_rad),0)):
                    raise ValueError('observed pose/encoder interpolation differs from selected records')
                if not close(observation.sync_error_sec, max(source_ns-pl_ns,pr_ns-source_ns,source_ns-el_ns,er_ns-source_ns)*1e-9):
                    raise ValueError('reported synchronization error differs from brackets')
                demod = math.remainder(observation.sensor_world_phase_rad-observation.base_yaw_rad,2*math.pi)
                disagreement = math.remainder(demod-observation.encoder_phase_rad,2*math.pi)
                if (not close(angle_delta(demod,observation.sensor_phase_rad),0)
                        or not close(angle_delta(disagreement,observation.phase_disagreement_rad),0)):
                    raise ValueError('reconstructed body/encoder phase differs from observed world orientation')
                receipt, observation_stamp = time_to_ns(observation.receipt_stamp), time_to_ns(observation.stamp)
                if config.get('cost_key_basis') == 'model_input_time':
                    admission = time_to_ns(observation.admission_stamp)
                    if not (0 <= receipt <= admission <= observation_stamp
                            and origin <= source_ns <= admission
                            and max(source_ns, pl_ns, pr_ns, el_ns, er_ns,
                                    time_to_ns(observation.cost_source_stamp)) <= admission):
                        raise ValueError('observation admission precedes clock coverage or receipt')
                elif not source_ns <= receipt <= observation_stamp:
                    raise ValueError('observation receipt/source times disagree')
                oldest = time_to_ns(observation.oldest_receipt_stamp)
                receipt_floor = 0 if config.get('cost_key_basis') == 'model_input_time' else origin
                if not receipt_floor <= oldest <= time_to_ns(observation.receipt_stamp):
                    raise ValueError('observation oldest input receipt is invalid')
                if message.output_valid and not 0 <= time_to_ns(message.stamp) - oldest <= 500_000_000:
                    raise ValueError('valid output uses stale input receipt')
            if not moving_policy and message.qualified and not (message.mean_full and message.coverage_valid and message.cycles_valid):
                raise ValueError('qualified direction lacks full coverage and stable cycles')
            if message.coverage_valid and (len(message.sector_counts) != 12 or min(message.sector_counts) < 2):
                raise ValueError('coverage claim lacks two actual observations per sector')
            if message.qualified and not moving_policy:
                if (len(message.cycle_mean_world_x) != 3 or len(message.cycle_mean_world_y) != 3
                        or len(message.cycle_coverage_valid) != 3 or not all(message.cycle_coverage_valid)
                        or len(message.cycle_sector_counts) != 36 or min(message.cycle_sector_counts) < 2
                        or not finite((message.max_pair_angle_rad, message.cycle_variability, message.magnitude_floor, message.mean_magnitude))
                        or not 0 <= message.max_pair_angle_rad <= math.pi/6 + 1e-9
                        or message.cycle_variability < 0
                        or not close(message.magnitude_floor, max(1e-6, 3*message.cycle_variability))
                        or message.mean_magnitude <= message.magnitude_floor):
                    raise ValueError('qualified direction violates declared three-cycle gates')
                vectors = list(zip(message.cycle_mean_world_x, message.cycle_mean_world_y))
                if not finite(value for vector in vectors for value in vector):
                    raise ValueError('qualified cycle means are not finite')
                center = [sum(vector[i] for vector in vectors)/3 for i in range(2)]
                variability = math.sqrt(sum(sum((vector[i]-center[i])**2 for i in range(2)) for vector in vectors)/3)
                floor = max(1e-6, 3*variability)
                norms = [math.hypot(*vector) for vector in vectors]
                if (any(norm <= floor for norm in norms)
                        or len(message.mean_world) != 2 or not finite(message.mean_world)
                        or math.hypot(*message.mean_world) <= floor
                        or not close(variability,message.cycle_variability)
                        or not close(math.hypot(*message.mean_world),message.mean_magnitude)):
                    raise ValueError('qualified means violate recomputed variability/magnitude floor')
                angles = [math.acos(max(-1.,min(1.,sum(a*b for a,b in zip(vectors[i],vectors[j]))/(norms[i]*norms[j]))))
                          for i,j in ((0,1),(0,2),(1,2))]
                if max(angles) > math.pi/6+1e-9 or not close(max(angles),message.max_pair_angle_rad):
                    raise ValueError('qualified means violate recomputed pairwise angle')
            if message.output_valid:
                if any(len(values) != 2 or not finite(values) for values in (message.instant_body, message.instant_world, message.output_body)):
                    raise ValueError('valid output lacks finite planar vectors')
                cosine, sine = math.cos(observation.base_yaw_rad), math.sin(observation.base_yaw_rad)
                instant_world = [cosine*message.instant_body[0]-sine*message.instant_body[1],
                                 sine*message.instant_body[0]+cosine*message.instant_body[1]]
                if not all(close(a,b) for a,b in zip(instant_world,message.instant_world)):
                    raise ValueError('instantaneous world vector differs from observed-body rotation')
                if message.blend_weight not in (0., .75 if moving_policy else .5) or (message.blend_weight and not (message.qualified and message.blend_allowed and message.algorithm_state_valid)):
                    raise ValueError('blend applied without qualification/state permission')
                if not finite((message.output_yaw_rad, message.output_magnitude)):
                    raise ValueError('valid output lacks current frame/norm')
                publication_ns = time_to_ns(message.stamp)
                output_pose_ns = time_to_ns(message.output_pose_stamp)
                if not (0 <= publication_ns-time_to_ns(observation.source_stamp) <= 500_000_000
                        and 0 <= publication_ns-output_pose_ns <= 500_000_000):
                    raise ValueError('valid output uses stale source or current pose')
                output_pose = pose_records.get(output_pose_ns)
                if output_pose is None or output_pose[3] != config['frame_id'] or not close(angle_delta(output_pose[2],message.output_yaw_rad),0):
                    raise ValueError('output frame does not match a recorded selected current pose')
                blend = message.blend_weight
                if blend and (len(message.mean_world) != 2 or not finite(message.mean_world)):
                    raise ValueError('blend lacks finite rolling mean')
                world = [(1-blend)*message.instant_world[i] + (blend*message.mean_world[i] if blend else 0) for i in range(2)]
                c, s = math.cos(message.output_yaw_rad), math.sin(message.output_yaw_rad)
                expected = [c*world[0]+s*world[1], -s*world[0]+c*world[1]]
                if not all(close(a,b) for a,b in zip(expected,message.output_body)) or not close(math.hypot(*message.output_body), message.output_magnitude):
                    raise ValueError('output is inconsistent with world blend/current-body rotation')
        except (ValueError, TypeError, IndexError, OverflowError) as exc:
            errors.append('V2 direction: ' + str(exc))
    return errors


def algorithm_event_producer_stream(message):
    """Identify the producer of one shared-bus event."""  # noqa: Q000
    event_type = int(message.event_type)
    detail = str(message.detail)
    if event_type in (10, 11):
        return 'convergence_detector'
    if event_type in FILL_OWNER_EVENT_TYPES:
        return 'gaussian_fill'
    if event_type in (3, 12, 30, 40, 41, 50, 51, 60):
        return 'supervisor'
    if event_type == 70:
        reason_code = int(message.reason_code)
        if detail.startswith('controller watchdog:') and reason_code == 1:
            return 'controller'
        if not detail.startswith('controller watchdog:') and reason_code == 0:
            return 'supervisor'
        return None
    if event_type == 2:
        return 'cost_function'
    if event_type != 1:
        return None
    from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE
    if detail in {mode + ' source-time configuration' for mode in (*CENTROID_METRIC_MODES, RECURRENT_MODE)}:
        return 'convergence_detector'
    configuration_prefixes = (
        ('source_mode=', 'cost_function'),
        ('state-driven robust weights', 'modified_cost'),
        ('legacy fixed observational weights', 'modified_cost'),
        ('convergence detector configuration', 'convergence_detector'),
        ('robust Gaussian estimator', 'gaussian_fill'),
        ('Gaussian fill configuration', 'gaussian_fill'),
        ('measured escape', 'supervisor'),
        ('post-recovery ', 'supervisor'),
    )
    return next(
        (
            producer
            for prefix, producer in configuration_prefixes
            if detail.startswith(prefix)
        ),
        None,
    )


def algorithm_event_stream_regressions(records, tolerance_nanoseconds):
    """Check AlgorithmEvent stamps independently per producer."""  # noqa: Q000
    streams = {}
    unidentified = []
    for bag_stamp, message in records:
        producer = algorithm_event_producer_stream(message)
        if producer is None:
            unidentified.append({
                'bag_timestamp': int(bag_stamp),
                'event_type': int(message.event_type),
                'detail': str(message.detail),
            })
            continue
        streams.setdefault(producer, []).append(
            (int(bag_stamp), _message_stamp_nanoseconds(message))
        )
    regressions = []
    for producer, values in streams.items():
        previous = None
        for bag_stamp, current in values:
            if current is None:
                continue
            if (
                previous is not None
                and current + tolerance_nanoseconds < previous['stamp']
            ):
                regressions.append({
                    'producer_stream': producer,
                    'previous': previous['stamp'],
                    'current': current,
                    'previous_bag_timestamp': previous['bag_timestamp'],
                    'current_bag_timestamp': bag_stamp,
                })
            previous = {
                'stamp': current,
                'bag_timestamp': bag_stamp,
            }
    return regressions, unidentified


def algorithm_event_emission_lags(event_records, clock_records):
    """Map event receipts to the latest received simulation clock."""  # noqa: Q000
    clocks = sorted(
        (
            int(bag_stamp),
            _stamp_nanoseconds(message.clock),
        )
        for bag_stamp, message in clock_records
        if message is not None
    )
    results = []
    clock_index = 0
    latest_clock = None
    for bag_stamp, message in sorted(event_records, key=lambda item: item[0]):
        while (
            clock_index < len(clocks)
            and clocks[clock_index][0] <= int(bag_stamp)
        ):
            latest_clock = clocks[clock_index][1]
            clock_index += 1
        event_stamp = _message_stamp_nanoseconds(message)
        results.append({
            'bag_timestamp': int(bag_stamp),
            'producer_stream': algorithm_event_producer_stream(message),
            'event_stamp': event_stamp,
            'clock_at_receipt': latest_clock,
            'clock_skew_nanoseconds': (
                None
                if latest_clock is None or event_stamp is None
                else latest_clock - event_stamp
            ),
        })
    return results


def fill_event_source_causality(event_records, request_records):
    """Require exact fill-event correlation to a recorded request."""  # noqa: Q000
    request_sources = [
        float(message.timestamp)
        for _, message in request_records
        if message is not None and math.isfinite(float(message.timestamp))
    ]
    failures = []
    for bag_stamp, message in event_records:
        if message is None:
            continue
        if int(message.event_type) not in FILL_OWNER_EVENT_TYPES:
            continue
        source = float(message.source_timestamp)
        matched = (
            message.source_timestamp_valid
            and math.isfinite(source)
            and source in request_sources
        )
        if not matched:
            failures.append({
                'bag_timestamp': int(bag_stamp),
                'event_type': int(message.event_type),
                'source_timestamp': source if math.isfinite(source) else None,
                'source_timestamp_valid': bool(
                    message.source_timestamp_valid
                ),
            })
    return failures


def timestamps_within_clock(values, clock_minimum, clock_maximum, tolerance_nanoseconds):
    """Check typed stamps against the selected run's simulation clock range."""

    return all(
        clock_minimum - tolerance_nanoseconds
        <= value
        <= clock_maximum + tolerance_nanoseconds
        for value in values
    )


def _twist_values(message):
    return (
        message.linear.x, message.linear.y, message.linear.z,
        message.angular.x, message.angular.y, message.angular.z,
    )


def _command_values(alias, message):
    if alias == "command_final":
        return _twist_values(message)
    if alias == "command_array_final":
        return tuple(message.data)
    if alias == "control_diagnostics":
        return tuple(message.final_command)
    raise ValueError(f"not a command alias: {alias}")


def _is_zero(values, tolerance=1e-9):
    return (
        len(values) == 6
        and all(
            math.isfinite(float(value)) and abs(float(value)) <= tolerance
            for value in values
        )
    )


def _check(report, name, passed, failure=None, detail=None):
    item = {"passed": bool(passed)}
    if detail is not None:
        item["detail"] = detail
    report["checks"][name] = item
    if not passed and failure:
        report["failures"].append(failure)


def _json_compatible(value, path='$', nonfinite_paths=None):
    """Replace nonfinite evidence scalars with null and retain their paths."""
    if nonfinite_paths is None:
        nonfinite_paths = []
    if isinstance(value, dict):
        converted = {}
        for index, (key, item) in enumerate(value.items()):
            converted_key = key
            if isinstance(key, float) and not math.isfinite(key):
                nonfinite_paths.append(f'{path}.<nonfinite-key>')
                converted_key = f'<nonfinite-key-{index}>'
            elif not isinstance(
                key,
                (str, int, float, bool, type(None)),
            ):
                converted_key = str(key)
            converted[converted_key] = _json_compatible(
                item,
                f'{path}.{converted_key}',
                nonfinite_paths,
            )
        return converted
    if isinstance(value, (list, tuple)):
        return [
            _json_compatible(
                item,
                f'{path}[{index}]',
                nonfinite_paths,
            )
            for index, item in enumerate(value)
        ]
    if isinstance(value, float) and not math.isfinite(value):
        nonfinite_paths.append(path)
        return None
    return value


def _load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _read_bag(bag_directory, expected_types, report):
    storage_options = rosbag2_py.StorageOptions(
        uri=str(bag_directory), storage_id="sqlite3"
    )
    converter_options = rosbag2_py.ConverterOptions("", "")
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    bag_types = {
        item.name: item.type for item in reader.get_all_topics_and_types()
    }
    messages = {topic: [] for topic in bag_types}
    classes = {}
    for topic, type_name in bag_types.items():
        try:
            classes[topic] = get_message(type_name)
        except (AttributeError, ModuleNotFoundError, ValueError) as exc:
            if topic in expected_types:
                report["failures"].append(
                    f"cannot load required type {type_name} for {topic}: {exc}"
                )
    while reader.has_next():
        topic, serialized, bag_stamp = reader.read_next()
        message_class = classes.get(topic)
        message = None
        if message_class is not None:
            message = deserialize_message(serialized, message_class)
        messages.setdefault(topic, []).append((int(bag_stamp), message))
    return bag_types, messages


def validate_run_directory(run_directory, write_report=True):
    """Validate a run directory and optionally replace completeness.json."""

    run_directory = Path(run_directory).expanduser().resolve()
    report = {
        "schema_version": 1,
        "run_id": run_directory.name,
        "passed": False,
        "checks": {},
        "topic_counts": {},
        "failures": [],
        "warnings": [],
    }
    metadata_path = run_directory / "metadata.yaml"
    resolved_topics_path = run_directory / "resolved_topics.yaml"
    resolved_parameters_path = run_directory / "resolved_parameters.yaml"
    notes_path = run_directory / "notes.md"
    bag_directory = run_directory / "bag"

    try:
        metadata = _load_yaml(metadata_path)
        metadata_ok = isinstance(metadata, dict)
    except (OSError, yaml.YAMLError) as exc:
        metadata = {}
        metadata_ok = False
        report["failures"].append(f"metadata unreadable: {exc}")
    missing_metadata = [
        name for name in (*REQUIRED_METADATA, "run_id", "git", "recording")
        if name not in metadata
    ]
    _check(
        report, "metadata_complete", metadata_ok and not missing_metadata,
        "metadata is incomplete",
        {"missing": missing_metadata},
    )
    _check(
        report, "notes_present", notes_path.is_file() and notes_path.stat().st_size > 0,
        "notes.md is missing or empty",
    )

    resolved = {}
    try:
        resolved = _load_yaml(resolved_topics_path)
        entries = resolved.get("topics", []) if isinstance(resolved, dict) else []
    except (OSError, yaml.YAMLError) as exc:
        entries = []
        report["failures"].append(f"resolved topics unreadable: {exc}")
    _check(
        report, "resolved_topics_present", bool(entries),
        "resolved_topics.yaml has no topic manifest",
    )
    try:
        entries = require_selected_algorithm_topics(
            entries, metadata.get('mode'), metadata.get('target_argv', [])
        )
    except ValueError as exc:
        report['failures'].append(f'selected algorithm recording contract: {exc}')
    by_topic = {entry["topic"]: entry for entry in entries if isinstance(entry, dict)}
    by_alias = {entry["alias"]: entry for entry in entries if isinstance(entry, dict)}
    expected_types = {topic: entry["type"] for topic, entry in by_topic.items()}
    timestamp_contract_errors = []
    publisher_contract_errors = []
    multi_publisher_timestamp_topics = set()
    multi_publisher_scope = []
    for topic, entry in by_topic.items():
        entry_errors = topic_evidence_contract_errors(entry)
        timestamp_contract_errors.extend(entry_errors)
        publisher_error = None
        if not entry_errors:
            publisher_error = expected_publisher_error(
                entry,
                entry.get('publishers', ()),
            )
            if publisher_error is not None:
                publisher_contract_errors.append(publisher_error)
        if (
            not entry_errors
            and publisher_error is None
            and entry.get(
                'timestamp_ordering',
                DEFAULT_TIMESTAMP_ORDERING,
            ) == MULTI_PUBLISHER_TIMESTAMP_ORDERING
        ):
            multi_publisher_timestamp_topics.add(topic)
            multi_publisher_scope.append({
                'topic': topic,
                'expected_publishers': sorted(
                    entry['expected_publishers']
                ),
                'resolved_publishers': sorted(entry.get('publishers', ())),
            })
    _check(
        report,
        'timestamp_ordering_contract_valid',
        not timestamp_contract_errors,
        'resolved timestamp-ordering contract is invalid',
        timestamp_contract_errors,
    )
    _check(
        report,
        'expected_publishers_match',
        not publisher_contract_errors,
        'resolved publishers do not match the declared owners',
        publisher_contract_errors,
    )
    _check(
        report,
        'multi_publisher_timestamp_scope',
        True,
        detail=multi_publisher_scope,
    )

    try:
        parameters = _load_yaml(resolved_parameters_path)
        parameter_failures = parameters.get("failures", [])
        required_parameter_failures = [
            item for item in parameter_failures
            if item.get("required_topic_publisher") and item.get("parameter_services_exposed", True)
        ]
        parameters_ok = isinstance(parameters, dict) and not required_parameter_failures
    except (OSError, yaml.YAMLError) as exc:
        parameters_ok = False
        required_parameter_failures = [{"error": str(exc)}]
    _check(
        report, "parameters_captured", parameters_ok,
        "required publisher parameter snapshot is incomplete",
        required_parameter_failures,
    )

    try:
        bag_types, messages = _read_bag(bag_directory, expected_types, report)
        bag_readable = True
    except Exception as exc:
        bag_types, messages = {}, {}
        bag_readable = False
        report["failures"].append(f"bag unreadable: {type(exc).__name__}: {exc}")
    _check(report, "bag_readable", bag_readable, "sqlite3 bag is not readable")

    for topic, entry in by_topic.items():
        count = len(messages.get(topic, []))
        report["topic_counts"][topic] = count
        if entry.get("required"):
            exact_type = bag_types.get(topic) == entry["type"]
            minimum = int(entry.get("minimum_messages", 1))
            _check(
                report, f"required_topic:{entry['alias']}",
                exact_type and count >= minimum,
                f"required topic {topic} missing, wrong type, or below {minimum} messages",
                {"expected_type": entry["type"], "actual_type": bag_types.get(topic), "count": count},
            )

    clock_messages = messages.get(by_alias.get("clock", {}).get("topic", ""), [])
    v2_identity = None
    v2_launch_values = dict(str(token).split(':=', 1)
                            for token in metadata.get('target_argv', []) if ':=' in str(token))
    runner_metadata = metadata.get('scenario_runner', {})
    selected_moving_fill = (
        v2_launch_values.get('continuous_search_mode') == 'rolling_gesc_v2'
        or (isinstance(runner_metadata, dict) and runner_metadata.get('v2_identity') is not None))
    moving_fill_causality = None
    try:
        v2_identity = v2_identity_from_metadata(metadata)
        if v2_identity is not None:
            selected_moving_fill = True
            v2_errors = v2_stream_contract_errors(
                messages, v2_identity,
                by_alias.get('v2_direction_diagnostics', {}).get('topic', '/gesc_gaussian/v2/direction_diagnostics'),
            )
            state_topic = by_alias.get('algorithm_state', {}).get('topic')
            if metadata.get('run_id') != v2_identity['run_id'] or any(
                message is not None and message.state_valid and
                (not message.run_id_valid or message.run_id != v2_identity['run_id'])
                for _, message in messages.get(state_topic, [])
            ):
                v2_errors.append('V2 recorder/supervisor shared run identity differs')
            _check(report, 'v2_synchronized_stream_contract', not v2_errors,
                   'V2 typed identity/synchronization/composition claims are inconsistent', v2_errors)
            lifecycle_errors, lifecycle_metrics = lifecycle_stream_errors(
                messages, v2_identity,
                topics={alias: entry.get('topic') for alias, entry in by_alias.items()},
                metric_mode=v2_launch_values.get('convergence_metric_mode', 'pde_mean_v1'),
                candidate_cost_mad_scale=float(v2_launch_values.get('candidate_cost_mad_scale', '3.0')),
                validate_fill_events=True,
                moving_verification_mode=v2_launch_values.get(
                    'v2_verification_motion_mode', 'rolling_neighborhood_v1'),
                verification_evidence_policy=v2_launch_values.get(
                    'v2_verification_evidence_policy', 'angular_profiles_v1'),
            )
            moving_fill_causality = lifecycle_metrics.get('fill_event_source_causality')
            report['v2_lifecycle_metrics'] = lifecycle_metrics
            _check(report, 'v2_lifecycle_contract', not lifecycle_errors,
                   'V2 epoch/candidate/fill lifecycle evidence is inconsistent', lifecycle_errors)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        _check(report, 'v2_synchronized_stream_contract', False, str(exc))
    # None is unselected; an empty list is validated typed authority. A failed
    # selected audit must never fall back to an unrelated legacy request.
    stationary_causality_failures = None
    stationary_contract_name = 'stationary_centroid'
    try:
        stationary_assignments = dict(str(token).split(':=', 1)
            for token in metadata.get('target_argv', []) if ':=' in str(token))
        if stationary_assignments.get('convergence_metric_mode') == 'recurrent_geometry_v3':
            stationary_contract_name = 'stationary_recurrent'
        stationary_config = stationary_centroid_config_from_target(metadata.get('target_argv', []))
        if stationary_config is not None:
            if stationary_config.get('metric_mode') == 'recurrent_geometry_v3':
                stationary_contract_name = 'stationary_recurrent'
            stationary_causality_failures = ['selected stationary authority unavailable']
            from .stationary_centroid_validation import stationary_centroid_stream_errors
            stationary_errors, stationary_audit = stationary_centroid_stream_errors(
                messages, stationary_config,
                topics={alias: entry.get('topic') for alias, entry in by_alias.items()})
            if (not isinstance(stationary_errors, list)
                    or not all(isinstance(error, str) for error in stationary_errors)
                    or not isinstance(stationary_audit, dict)):
                raise ValueError('selected stationary authority result is malformed')
            stationary_causality_failures = list(stationary_errors)
            report[stationary_contract_name + '_audit'] = stationary_audit
            _check(report, stationary_contract_name + '_contract', not stationary_errors,
                   'stationary request/result evidence is inconsistent', stationary_errors)
        else:
            for alias, name in (('stationary_fill_requests', 'stationary_centroid'),
                                ('stationary_recurrent_fill_requests', 'stationary_recurrent')):
                topic = by_alias.get(alias, {}).get('topic', '/gesc_gaussian/v2/' + alias)
                if messages.get(topic):
                    _check(report, name + '_contract', False,
                           'stationary requests were recorded outside selected Arm B')
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        stationary_causality_failures = ['selected stationary authority unavailable: ' + str(exc)]
        _check(report, stationary_contract_name + '_contract', False, str(exc))
    recurrent_entry = by_alias.get('recurrent_convergence_diagnostics', {})
    recurrent_records = messages.get(recurrent_entry.get('topic'), [])
    if recurrent_records:
        from ros_esc.convergence_detector_node.recurrent_contract import recurrent_diagnostic_errors
        recurrent_errors = recurrent_diagnostic_errors(
            [msg for _, msg in recurrent_records],
            expected_metric_mode=recurrent_entry.get('algorithm_metric_mode'),
            expected_source_pose_topic=recurrent_entry.get('algorithm_source_pose_topic'),
            supervisor_run_ids={msg.run_id for _, msg in messages.get(
                by_alias.get('algorithm_state', {}).get('topic'), []) if msg is not None and msg.run_id},
            maximum_source_gap_sec=recurrent_entry.get('algorithm_maximum_source_gap_sec'),
            allow_clock_admission=(recurrent_entry.get('algorithm_clock_admission') ==
                                   'recurrent_original_receipt_v1'),
            expected_frame_id='odom',
            pose_freshness_sec=recurrent_entry.get('algorithm_pose_stale_sec', .5))
        if not recurrent_entry.get('algorithm_required'):
            recurrent_errors.append('recurrent diagnostic recorded outside selected mode')
        _check(report, 'recurrent_diagnostics_consistent', not recurrent_errors,
               'recurrent diagnostics violate their typed contract', recurrent_errors)
    centroid_entry = by_alias.get('centroid_convergence_diagnostics', {})
    centroid_topic = centroid_entry.get('topic')
    centroid_records = messages.get(centroid_topic, [])
    centroid_messages = [msg for _, msg in messages.get(centroid_topic, [])]
    if centroid_messages:
        state_topic = by_alias.get('algorithm_state', {}).get('topic')
        supervisor_runs = {
            message.run_id for _, message in messages.get(state_topic, [])
            if message is not None and message.state_valid
            and message.run_id_valid and message.run_id
        }
        admission_metadata = centroid_entry.get('algorithm_clock_admission')
        selected_centroid_admission = admission_metadata == 'centroid_original_receipt_v1'
        centroid_errors = centroid_diagnostic_errors(
            centroid_messages,
            expected_metric_mode=centroid_entry.get('algorithm_metric_mode'),
            expected_source_pose_topic=centroid_entry.get('algorithm_source_pose_topic'),
            supervisor_run_ids=supervisor_runs,
            maximum_source_gap_sec=centroid_entry.get('algorithm_maximum_source_gap_sec'),
            allow_clock_admission=selected_centroid_admission or v2_identity is not None,
            expected_frame_id=(v2_identity['stream_config']['frame_id']
                               if v2_identity is not None else None),
            pose_freshness_sec=(centroid_entry.get('algorithm_pose_stale_sec')
                                if selected_centroid_admission else 0.5),
        )
        if ('algorithm_clock_admission' in centroid_entry
                and not selected_centroid_admission):
            centroid_errors.append('centroid diagnostic configuration: unknown clock admission policy')
        _check(report, 'centroid_diagnostics_consistent', not centroid_errors,
               'centroid diagnostics violate their typed contract', centroid_errors)
    if metadata.get("mode") == "simulation":
        clock_values = [
            _stamp_nanoseconds(message.clock)
            for _, message in clock_messages if message is not None
        ]
        clock_ok = bool(clock_values) and all(
            current >= previous for previous, current in zip(clock_values, clock_values[1:])
        )
        _check(report, "simulation_clock_monotonic", clock_ok, "simulation /clock regressed or is absent")

    readiness_topic = by_alias.get("recording_ready", {}).get("topic", "")
    early_readiness_records = [
        (stamp, bool(message.data))
        for stamp, message in messages.get(readiness_topic, []) if message is not None
    ]
    first_ready_true = next(
        (stamp for stamp, value in early_readiness_records if value), None
    )
    first_ready_false_after_true = next(
        (
            stamp for stamp, value in early_readiness_records
            if not value and first_ready_true is not None and stamp >= first_ready_true
        ),
        None,
    )
    try:
        tolerance_sec = float(
            resolved.get("validation", {}).get(
                "timestamp_regression_tolerance_sec", 0.05
            )
        )
    except (TypeError, ValueError):
        tolerance_sec = float('nan')
    tolerance_valid = (
        math.isfinite(tolerance_sec)
        and tolerance_sec >= 0.0
    )
    _check(
        report,
        'timestamp_tolerance_valid',
        tolerance_valid,
        'timestamp regression tolerance is invalid',
        {
            'configured_sec': (
                tolerance_sec if math.isfinite(tolerance_sec) else None
            ),
        },
    )
    if not tolerance_valid:
        tolerance_sec = 0.0
    tolerance_nanoseconds = int(tolerance_sec * 1_000_000_000)
    stamp_regressions = []
    typed_stamps_in_interval = []
    event_topic = by_alias.get('algorithm_events', {}).get('topic', '')
    event_interval_records = []
    for topic, topic_messages in messages.items():
        topic_stamps = []
        for bag_stamp, message in topic_messages:
            if message is None:
                continue
            if first_ready_true is not None and bag_stamp < first_ready_true:
                continue
            if first_ready_false_after_true is not None and bag_stamp > first_ready_false_after_true:
                continue
            current = _message_stamp_nanoseconds(message)
            if current is not None:
                typed_stamps_in_interval.append({"topic": topic, "stamp": current})
                if topic == event_topic:
                    event_interval_records.append((bag_stamp, message))
                elif topic not in multi_publisher_timestamp_topics:
                    topic_stamps.append(current)
        if topic != event_topic:
            for regression in timestamp_regressions(
                topic_stamps, tolerance_nanoseconds
            ):
                stamp_regressions.append({'topic': topic, **regression})
    event_regressions, unidentified_events = (
        algorithm_event_stream_regressions(
            event_interval_records,
            tolerance_nanoseconds,
        )
    )
    stamp_regressions.extend(
        {'topic': event_topic, **regression}
        for regression in event_regressions
    )
    _check(
        report,
        'algorithm_event_producer_identified',
        not unidentified_events,
        'one or more AlgorithmEvent producers could not be identified',
        unidentified_events[:20],
    )
    _check(
        report, "typed_timestamps_nonregressing", not stamp_regressions,
        f"typed ROS timestamps regressed by more than {tolerance_sec:.3f} s",
        stamp_regressions[:20],
    )
    if metadata.get("mode") == "simulation" and clock_values:
        clock_minimum = min(clock_values)
        clock_maximum = max(clock_values)
        out_of_clock = [
            item for item in typed_stamps_in_interval
            if not timestamps_within_clock(
                [item["stamp"]], clock_minimum, clock_maximum,
                tolerance_nanoseconds,
            )
        ]
        _check(
            report, "typed_timestamps_within_clock",
            not out_of_clock,
            "typed ROS timestamps fall outside the recorded simulation clock",
            out_of_clock[:20],
        )
        event_lags = algorithm_event_emission_lags(
            event_interval_records,
            clock_messages,
        )
        stale_events = [
            item for item in event_lags
            if item['clock_skew_nanoseconds'] is None
            or abs(item['clock_skew_nanoseconds']) > tolerance_nanoseconds
        ]
        _check(
            report,
            'algorithm_event_emission_fresh',
            not stale_events,
            'AlgorithmEvent emission stamps lead or lag receipt-time '
            'simulation clock',
            stale_events[:20],
        )

    source_entry = by_alias.get("source_cost", {})
    source_messages = messages.get(source_entry.get("topic", ""), [])
    source_semantics_ok = bool(source_messages)
    for _, message in source_messages:
        if message is None:
            source_semantics_ok = False
            continue
        if metadata.get("mode") == "simulation":
            source_semantics_ok &= (
                message.source_mode == message.SOURCE_SIMULATION
                and message.raw_cost_valid
                and message.source_score_valid
                and not message.raw_sensor_valid
            )
        else:
            source_semantics_ok &= (
                message.source_mode == message.SOURCE_PHYSICAL
                and message.raw_sensor_valid
                and message.raw_cost_valid
                and message.source_score_valid
            )
    _check(
        report, "source_cost_semantics", source_semantics_ok,
        "source cost validity/source mode does not match run mode",
    )
    mode = metadata.get("mode")
    profile = metadata.get("algorithm_profile")
    profile_ok = (
        mode in VALID_PROFILES_BY_MODE
        and profile in VALID_PROFILES_BY_MODE[mode]
    )
    _check(
        report, "audited_profile", profile_ok,
        f"algorithm_profile {profile!r} is not audited for mode {mode!r}",
    )

    event_entry = by_alias.get("algorithm_events", {})
    event_messages = messages.get(event_entry.get("topic", ""), [])
    event_lengths_ok = all(
        message is not None and len(message.value_names) == len(message.values)
        for _, message in event_messages
    )
    _check(report, "event_value_pairs", event_lengths_ok, "AlgorithmEvent value_names/values mismatch")
    fill_request_entry = by_alias.get('fill_requests', {})
    if selected_moving_fill:
        source_causality_failures = (
            moving_fill_causality['errors'] if moving_fill_causality is not None
            else [{'error': 'selected moving lifecycle authority unavailable'}])
    elif stationary_causality_failures is not None:
        source_causality_failures = stationary_causality_failures
    elif profile == 'robust_gaussian_v1':
        source_causality_failures = fill_event_source_causality(
            event_messages, messages.get(fill_request_entry.get('topic', ''), []))
    else:
        source_causality_failures = []
    _check(
        report,
        'algorithm_event_source_causality',
        not source_causality_failures,
        'fill-owner AlgorithmEvent source timestamps lack a recorded request',
        (
            source_causality_failures[:20]
            if profile == 'robust_gaussian_v1'
            else {'status': 'not_applicable'}
        ),
    )

    state_entry = by_alias.get("algorithm_state", {})
    state_messages = messages.get(state_entry.get("topic", ""), [])
    fill_required = any(
        message is not None and message.event_type in FILL_EVENT_TYPES
        for _, message in event_messages
    ) or any(
        message is not None and message.active_fill_count_valid and message.active_fill_count > 0
        for _, message in state_messages
    )
    fill_count = len(messages.get(by_alias.get("gaussian_fills", {}).get("topic", ""), []))
    _check(
        report, "fill_lifecycle_conditional", not fill_required or fill_count > 0,
        "fill lifecycle was reported without GaussianFill records",
        {"fill_required": fill_required, "fill_messages": fill_count},
    )

    command_records = {}
    nonzero_times = []
    for alias in ("command_final", "command_array_final", "control_diagnostics"):
        entry = by_alias.get(alias, {})
        records = messages.get(entry.get("topic", ""), [])
        parsed = [
            (stamp, _command_values(alias, message))
            for stamp, message in records if message is not None
        ]
        command_records[alias] = parsed
        nonzero_times.extend(stamp for stamp, values in parsed if not _is_zero(values))

    readiness_entry = by_alias.get("recording_ready", {})
    readiness_records = [
        (stamp, bool(message.data))
        for stamp, message in messages.get(readiness_entry.get("topic", ""), [])
        if message is not None
    ]
    stop_entry = by_alias.get("stop_requested", {})
    stop_times = [
        stamp
        for stamp, message in messages.get(stop_entry.get("topic", ""), [])
        if message is not None and message.data
    ]
    first_stop_true = stop_times[0] if stop_times else None
    preauthorization_boundaries = [
        boundary
        for boundary in (first_ready_true, first_stop_true)
        if boundary is not None
    ]
    preauthorization_boundary = (
        min(preauthorization_boundaries)
        if preauthorization_boundaries
        else None
    )
    pre_ready_nonzero = [
        {'alias': alias, 'bag_timestamp': stamp}
        for alias, records in command_records.items()
        for stamp, values in records
        if (
            not _is_zero(values)
            and (
                preauthorization_boundary is None
                or stamp < preauthorization_boundary
            )
        )
    ]
    recording = (
        metadata.get('recording', {})
        if isinstance(metadata, dict)
        else {}
    )
    metadata_pre_ready_nonzero = (
        recording.get('pre_ready_nonzero_topics', {})
        if isinstance(recording, dict)
        else {}
    )
    _check(
        report,
        'no_motion_before_readiness',
        not pre_ready_nonzero and not metadata_pre_ready_nonzero,
        'nonzero command was recorded before motion readiness',
        {
            'bag_observations': pre_ready_nonzero[:20],
            'coordinator_observations': metadata_pre_ready_nonzero,
        },
    )
    bag_lifecycle_violations = []
    for stamp, message in state_messages:
        if (
            message is None
            or (
                preauthorization_boundary is not None
                and stamp >= preauthorization_boundary
            )
        ):
            continue
        lifecycle_errors = preauthorization_lifecycle_errors(
            message,
            profile,
        )
        if lifecycle_errors:
            bag_lifecycle_violations.append({
                'bag_timestamp': stamp,
                'errors': lifecycle_errors,
            })
    metadata_lifecycle_violations = (
        recording.get('pre_ready_lifecycle_violations', [])
        if isinstance(recording, dict)
        else []
    )
    lifecycle_clean = (
        profile != 'robust_gaussian_v1'
        or (
            not bag_lifecycle_violations
            and not metadata_lifecycle_violations
        )
    )
    _check(
        report,
        'clean_lifecycle_before_readiness',
        lifecycle_clean,
        'robust lifecycle advanced before recording readiness',
        (
            {
                'bag_observations': bag_lifecycle_violations[:20],
                'coordinator_observations': (
                    metadata_lifecycle_violations
                ),
            }
            if profile == 'robust_gaussian_v1'
            else {'status': 'not_applicable'}
        ),
    )
    shutdown_boundary = stop_times[-1] if stop_times else (
        readiness_records[-1][0] if readiness_records else None
    )
    _check(
        report, "final_readiness_false",
        bool(readiness_records) and readiness_records[-1][1] is False,
        "last recording-ready heartbeat is not false",
    )
    final_zero_ok = True
    final_zero_details = {}
    last_nonzero = max(nonzero_times) if nonzero_times else -1
    for alias, records in command_records.items():
        last = records[-1] if records else None
        passed = (
            last is not None and _is_zero(last[1])
            and last[0] >= last_nonzero
            and shutdown_boundary is not None and last[0] >= shutdown_boundary
        )
        final_zero_ok &= passed
        final_zero_details[alias] = {"passed": passed, "last_timestamp": last[0] if last else None}
    _check(
        report, "final_commands_zero", final_zero_ok,
        "one or more final command representations lack post-shutdown zero evidence",
        final_zero_details,
    )

    if nonzero_times:
        interval_start, interval_end = min(nonzero_times), max(nonzero_times)
    else:
        true_times = [stamp for stamp, value in readiness_records if value]
        false_after = [
            stamp for stamp, value in readiness_records
            if not value and true_times and stamp >= true_times[0]
        ]
        interval_start = true_times[0] if true_times else None
        interval_end = false_after[0] if false_after else None
    coverage_failures = []
    if interval_start is None or interval_end is None:
        coverage_failures.append("motion/readiness coverage interval is unavailable")
    else:
        tolerance = 1_000_000_000
        coverage_aliases = MOTION_COVERAGE_ALIASES | {
            alias for alias, entry in by_alias.items()
            if entry.get('algorithm_required') and entry.get('coverage') == 'motion'
        }
        for alias in coverage_aliases:
            entry = by_alias.get(alias)
            if not entry:
                coverage_failures.append(f"{alias}: absent from resolved manifest")
                continue
            if alias == 'recurrent_convergence_diagnostics':
                coverage_failures.extend(centroid_stream_errors(
                    recurrent_records, clock_messages,
                    first_ready_true, first_ready_false_after_true,
                    entry['algorithm_maximum_diagnostic_gap_sec'], diagnostic_kind='recurrent'))
                continue
            if alias == 'centroid_convergence_diagnostics':
                coverage_failures.extend(centroid_stream_errors(
                    centroid_records, clock_messages,
                    first_ready_true, first_ready_false_after_true,
                    entry['algorithm_maximum_diagnostic_gap_sec'],
                ))
                continue
            timestamps = [stamp for stamp, _ in messages.get(entry["topic"], [])]
            if not timestamps or timestamps[0] > interval_start + tolerance or timestamps[-1] < interval_end - tolerance:
                coverage_failures.append(f"{alias}: does not cover interval within 1 second")
    _check(
        report, "motion_interval_coverage", not coverage_failures,
        "required state/cost/pose/command topics do not cover motion interval",
        coverage_failures,
    )

    readiness_metadata_consistent = (
        'readiness_ever_true' not in recording
        or bool(recording.get('readiness_ever_true'))
        == (first_ready_true is not None)
    )
    _check(
        report,
        'readiness_metadata_consistent',
        readiness_metadata_consistent,
        'recording readiness metadata disagrees with the bag',
    )
    process_ok = (
        recording.get("complete") is True
        and recording.get("bag_clean_shutdown") is True
        and recording.get("target_clean_shutdown") is True
        and recording.get("final_zero_observed") is True
        and not recording.get("run_error")
    )
    _check(report, "clean_shutdown_metadata", process_ok, "recording shutdown metadata is incomplete or failed")

    try:
        console_text = (run_directory / "console.log").read_text(
            encoding="utf-8", errors="replace"
        ).lower()
        console_failures = [marker for marker in FORBIDDEN_CONSOLE_MARKERS if marker in console_text]
        shutdown_index = console_text.find(
            "shutdown initiated; readiness false and stop requested"
        )
        for line in console_text.splitlines():
            if "process has died" not in line:
                continue
            line_index = console_text.find(line)
            allowed_gazebo_interrupt = (
                shutdown_index >= 0
                and line_index >= shutdown_index
                and ("gzserver" in line or "gzclient" in line or "gazebo-" in line)
                and "exit code 255" in line
            )
            allowed_controlled_sigint = (
                shutdown_index >= 0
                and line_index >= shutdown_index
                and "exit code -2" in line
            )
            if not (allowed_gazebo_interrupt or allowed_controlled_sigint):
                console_failures.append(line)
    except OSError as exc:
        console_failures = [f"console.log unreadable: {exc}"]
    _check(
        report, "console_clean", not console_failures,
        "console contains a ROS/process failure marker", console_failures,
    )

    nonfinite_paths = []
    report = _json_compatible(
        report,
        nonfinite_paths=nonfinite_paths,
    )
    _check(
        report,
        'strict_json_finite',
        not nonfinite_paths,
        'nonfinite evidence values were normalized to null',
        {'normalized_paths': nonfinite_paths},
    )
    report["passed"] = not report["failures"]
    if write_report:
        atomic_json(run_directory / "completeness.json", report)
    return report


def _parser():
    parser = argparse.ArgumentParser(description="Validate one recorded run directory.")
    parser.add_argument("run_directory")
    return parser


def main(args=None):
    """Console entry point."""

    parsed = _parser().parse_args(args)
    try:
        report = validate_run_directory(parsed.run_directory, write_report=True)
    except Exception as exc:
        print(f"validate_run: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
