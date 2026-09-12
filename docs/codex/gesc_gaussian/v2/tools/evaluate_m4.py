#!/usr/bin/env python3
"""Finite staged M4 science through the existing bag and numerical owners.

Invoke only through the prospective 120/45/10-second child-job envelopes.
Labels freeze pose-derived intervals before inspecting outcomes. References
consume those retained inputs; summaries never reopen bags or evaluate fields.
"""

import argparse
from bisect import bisect_right
from copy import deepcopy
import math
from pathlib import Path

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import m4_pilot as metrics
from ros_esc.plotting_scripts.bag_reader import load_yaml, read_run_bag, records_for_alias, stamp_nanoseconds
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc_interfaces.msg import AlgorithmEvent

from m4_workflow import check_receipts, read_json, receipt, slot_spec, verify_frozen


NS = 1_000_000_000
RECORDED_ARRIVAL_BINDING = metrics.RECORDED_ARRIVAL_BINDING


def _pairs(bag, alias, *, readiness=False):
    return [(r.bag_timestamp_ns, r.message) for r in records_for_alias(bag, alias)
            if not readiness or r.in_readiness_interval]


def _origin(bag):
    rows = records_for_alias(bag, 'timekeeper')
    values = {float(r.message.start_time) for r in rows}
    if (len(values) != 1 or not all(math.isfinite(v) for v in values)
            or {r.message.mode for r in rows} != {'sim time'}):
        return None
    return round(next(iter(values))*NS)


def _terminal_stamp(bag):
    return min((stamp_nanoseconds(r.message.stamp) for r in records_for_alias(bag, 'algorithm_state')
                if r.in_readiness_interval and r.message.state_valid and r.message.state in (7, 8)),
               default=None)


def _v10(planned):
    """Arrival-family selection; retain the existing helper name for callers."""
    return metrics.is_arrival_experiment_version(planned.get('experiment_version'))


def _confirmation_inputs(bag, planned):
    """Keep actual decision/publication and admitted source support separate."""
    events = _pairs(bag, 'algorithm_events', readiness=True)
    audit, errors, confirmations = [], [], []
    if planned['arm'] in ('B', 'D'):
        alias = 'recurrent_convergence_diagnostics' if _v10(planned) else 'centroid_convergence_diagnostics'
        events, audit, error = runner._centroid_convergence_evaluation_events(
            planned['resolved_scenario'], _pairs(bag, 'algorithm_state', readiness=True), events,
            _pairs(bag, alias, readiness=True), _pairs(bag, 'timekeeper'))
        if error:
            errors.append(error)
        confirmations = [dict(decision_ns=r['diagnostic_publication_stamp_ns'],
                              source_ns=(r['diagnostic_history_end_ns'] if _v10(planned)
                                         else r['diagnostic_source_stamp_ns'])) for r in audit]
    elif planned['arm'] == 'C':
        confirmations = [dict(decision_ns=stamp_nanoseconds(r.message.stamp),
                              source_ns=stamp_nanoseconds(r.message.source_stamp))
                         for r in records_for_alias(bag, 'v2_detector_confirmation')
                         if r.in_readiness_interval and r.message.valid]
    else:
        origin = _origin(bag)
        for _, message in events:
            if message.event_type != AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED:
                continue
            source = runner._message_source_timestamp(message)
            if origin is None or source is None:
                errors.append('legacy confirmation lacks observed source/Timekeeper binding')
                continue
            confirmations.append(dict(decision_ns=stamp_nanoseconds(message.stamp),
                                      source_ns=origin+round(source*NS)))
    return confirmations, events, audit, errors


def _intervention_inputs(bag, metadata, planned, events):
    """Inspect complete typed activation authority; preparation is not a fill."""
    required = {'algorithm_events', 'gaussian_fills', 'algorithm_state'}
    missing = required-set(bag.topics_by_alias)
    if missing:
        return dict(complete=False, stamp_ns=None, errors=['missing aliases: '+','.join(sorted(missing))])
    fills = _pairs(bag, 'gaussian_fills', readiness=True)
    clusters, error = runner._created_fill_clusters(events, fills)
    if error:
        return dict(complete=False, stamp_ns=None, errors=[error])
    active = [stamp_nanoseconds(m.stamp) for _, m in fills if m.active and not m.superseded]
    if planned['arm'] in ('C', 'D'):
        lifecycle, _, _ = analysis._v2_lifecycle_analysis(bag, metadata, planned['resolved_scenario'])
        if lifecycle is None or lifecycle['status'] != 'valid':
            return dict(complete=False, stamp_ns=None,
                        errors=['moving activation authority unavailable'] if lifecycle is None else lifecycle['errors'],
                        lifecycle=lifecycle)
        stamps = [r['committed_at_ns'] for r in lifecycle['audit']['commits']]
        return dict(complete=True, stamp_ns=min(stamps, default=None), errors=[], lifecycle=lifecycle,
                    convention='typed actual committed_at; PREPARED excluded')
    stationary = None
    if planned['arm'] == 'B':
        stationary, _, _ = analysis._stationary_centroid_analysis(bag, metadata)
        if stationary is None or stationary['status'] != 'valid':
            return dict(complete=False, stamp_ns=None,
                        errors=['stationary request/result authority unavailable'] if stationary is None else stationary['errors'],
                        stationary=stationary)
    # Both independent public owners must account for the complete observed map.
    created = {r['fill_id'] for r in clusters['created']}
    active_ids = {m.fill_id for _, m in fills if m.active and not m.superseded}
    if not active_ids <= created:
        return dict(complete=False, stamp_ns=None, errors=['active fill lacks canonical creation event'])
    stamps = active+[stamp_nanoseconds(r['event'].stamp) for r in clusters['created']]
    return dict(complete=True, stamp_ns=min(stamps, default=None), errors=[], stationary=stationary,
                convention='earliest canonical active fill or FILL_CREATED ROS publication; observable activation proxy')


def _error_counts(bag, planned, events, outcomes):
    """Use existing evaluator associations, retaining unmatched attribution."""
    required = {'algorithm_events', 'gaussian_fills', 'algorithm_state'}
    if not required <= set(bag.topics_by_alias) or bag.readiness_start_ns is None or outcomes.get('outcome_error'):
        return dict(wrong_fills=None, wrong_goals=None, attribution_errors=['complete event/state/fill attribution unavailable'])
    clusters, error = runner._created_fill_clusters(events, _pairs(bag, 'gaussian_fills', readiness=True))
    if error:
        return dict(wrong_fills=None, wrong_goals=None, attribution_errors=[error])
    stage = outcomes.get('local_recovery_stage') or {}
    assigned = {r['cluster_id'] for r in stage.get('assignments', [])}
    created = clusters['created_cluster_ids']
    # A failed episode/association is not evidence that its fill was wrong.
    wrong_fills = 0 if not created or (created <= assigned and outcomes.get('fill_cardinality_passed') is True) else None
    goal_events = [(s, m) for s, m in events if m.event_type == AlgorithmEvent.EVENT_GOAL_REACHED]
    goal_states = [m for _, m in _pairs(bag, 'algorithm_state', readiness=True) if m.state_valid and m.state == 7]
    wrong_goals, unknown, audits = 0, bool(goal_states) and not goal_events, []
    for event in goal_events:
        passed, evidence, error = runner._ranked_goal_evidence(planned['resolved_scenario'], [event], stage)
        audits.append(dict(passed=passed, evidence=evidence, error=error))
        if error or passed is None or not stage.get('stage_a_completion_stamp'):
            unknown = True
        elif passed is True and (outcomes.get('post_recovery_global_proximity_passed') is not True
                                or outcomes.get('simulation_ground_truth') != 'passed'):
            unknown = True  # Internal ranking alone cannot establish the externally correct terminal region.
        elif passed is not True:
            # Missing/malformed evidence is explicitly not an observed wrong decision.
            unknown = True
    return dict(wrong_fills=wrong_fills, wrong_goals=None if unknown else wrong_goals,
                attribution_errors=[], fill_created_cluster_ids=sorted(created),
                fill_assigned_cluster_ids=sorted(assigned), goal_event_count=len(goal_events),
                goal_attribution=audits,
                scope='existing staged geometry/cardinality and counted-candidate ranking; unmatched attribution unavailable')


def _motion_metrics(bag, planned, intervention=None):
    """Report acquisition-phase commands separately from safety/goal stops."""
    if planned['arm'] not in ('C', 'D'):
        return dict(mandatory_stopped_acquisitions=None, status='NOT_APPLICABLE')
    if _v10(planned):
        if planned.get('experiment_version') == metrics.V14_EXPERIMENT_VERSION:
            return _v10_motion_metrics(bag, planned, intervention or {},
                                       pairing_basis='full_publication_order_v1')
        return _v10_motion_metrics(bag, planned, intervention or {})
    states = [r for r in records_for_alias(bag, 'algorithm_state') if r.in_readiness_interval]
    stamps = [r.bag_timestamp_ns for r in states]
    sampled, zero, suppressed, unknown = 0, 0, 0, 0
    coverage = set()
    for record in records_for_alias(bag, 'control_diagnostics'):
        if not record.in_readiness_interval:
            continue
        index = bisect_right(stamps, record.bag_timestamp_ns)-1
        if index < 0:
            unknown += 1
            continue
        state = states[index].message
        if not state.state_valid or record.bag_timestamp_ns-stamps[index] > 500_000_000:
            unknown += 1
            continue
        if state.state not in (1, 2, 3) or (state.state == 3 and state.previous_state != 2):
            continue  # Redesign/escape, safety and final stops have other owners.
        coverage.add(index)
        message = record.message
        values = list(message.final_command)+list(message.gesc_command_unsaturated)+list(message.combined_command_unsaturated)
        if (not message.final_command_valid or not message.gesc_command_unsaturated_valid
                or not message.combined_command_unsaturated_valid or not all(map(math.isfinite, values))):
            unknown += 1
            continue
        sampled += 1
        if all(v == 0. for v in message.final_command):
            zero += 1
            # Could be readiness/freshness or other safety authorization loss.
            # Without a typed stop reason this cannot establish a mandatory dwell.
            if any(v != 0. for v in message.gesc_command_unsaturated):
                suppressed += 1
    required = {i for i, r in enumerate(states) if r.message.state_valid and
                (r.message.state in (1, 2) or (r.message.state == 3 and r.message.previous_state == 2))}
    missing = len(required-coverage)
    known = bool(states) and bool(records_for_alias(bag, 'control_diagnostics')) and not unknown and not zero and not missing
    return dict(mandatory_stopped_acquisitions=0 if known else None,
                status='OBSERVED_NO_MANDATORY_STOP' if known else 'EVIDENCE_UNAVAILABLE',
                acquisition_command_samples=sampled, zero_command_samples=zero,
                potentially_suppressed_command_samples=suppressed, unknown_samples=unknown,
                uncovered_acquisition_state_samples=missing,
                scope='recorded SEARCH/verification/design commands; all-zero output lacks a typed reason and remains unavailable; safety/goal and redesign stops are separate')


def _v10_motion_metrics(bag, planned, intervention, *, pairing_basis=None):
    """Project typed evidence into the fixed motion rule.

    The opt-in pairs complete publication streams before readiness selection.
    It inherits publication order from the single controller publisher; exact
    vectors and bounded receipts do not supply a shared sequence to Twist.
    Historical callers retain independent readiness selection and its verdicts.
    """
    if pairing_basis not in (None, 'full_publication_order_v1'):
        raise ValueError('unsupported command pairing basis')
    full_pairing = pairing_basis == 'full_publication_order_v1'
    states = [dict(bag_ns=r.bag_timestamp_ns, stamp_ns=stamp_nanoseconds(r.message.stamp),
        state=r.message.state, previous_state=r.message.previous_state,
        valid=bool(r.message.state_valid)) for r in records_for_alias(bag, 'algorithm_state')
        if r.in_readiness_interval]
    # Include the first later public state to close a stopped/aborted segment.
    later = next((r for r in records_for_alias(bag, 'algorithm_state')
        if states and r.bag_timestamp_ns > states[-1]['bag_ns']), None)
    if later is not None:
        states.append(dict(bag_ns=later.bag_timestamp_ns, stamp_ns=stamp_nanoseconds(later.message.stamp),
            state=later.message.state, previous_state=later.message.previous_state,
            valid=bool(later.message.state_valid)))
    guidance = [dict(stamp_ns=stamp_nanoseconds(r.message.stamp), valid=True,
        proposal_valid=bool(r.message.valid),
        proposal_nonzero=bool(r.message.linear_x_mps or r.message.angular_z_radps),
        reason=r.message.reason) for r in records_for_alias(bag, 'v2_verification_guidance')]
    full_diagnostics = records_for_alias(bag, 'control_diagnostics')
    full_actual = records_for_alias(bag, 'command_final')
    start, end = bag.readiness_start_ns, bag.readiness_end_ns
    bounds_valid = type(start) is int and type(end) is int and 0 <= start < end
    membership_valid = bounds_valid and all(
        r.in_readiness_interval == (start <= r.bag_timestamp_ns <= end)
        for r in full_diagnostics + full_actual)
    # Preserve original within-interval counts even when full pairs are selected.
    diagnostics = [r for r in full_diagnostics if r.in_readiness_interval]
    actual = [r for r in full_actual if r.in_readiness_interval]
    def interval_counts(records):
        return dict(full=len(records), within=sum(r.in_readiness_interval for r in records),
            pre=sum(r.bag_timestamp_ns < start for r in records) if bounds_valid else None,
            post=sum(r.bag_timestamp_ns > end for r in records) if bounds_valid else None)
    pair_diagnostics = full_diagnostics if full_pairing else diagnostics
    pair_actual = full_actual if full_pairing else actual
    pairing = bool(membership_valid and pair_diagnostics
                   and len(pair_diagnostics) == len(pair_actual))
    receipt_order_valid = all(a.bag_timestamp_ns <= b.bag_timestamp_ns
        for rows in (pair_diagnostics, pair_actual) for a, b in zip(rows, rows[1:]))
    commands, pairing_errors, paired_stamps, excluded_boundary = [], [], [], []
    invalid_stamp_indices = []
    for index, (diagnostic, command) in enumerate(zip(pair_diagnostics, pair_actual)):
        m, twist = diagnostic.message, command.message
        vector = [twist.linear.x, twist.linear.y, twist.linear.z,
                  twist.angular.x, twist.angular.y, twist.angular.z]
        valid = bool(m.final_command_valid and all(math.isfinite(v) for v in vector)
                     and list(m.final_command) == vector
                     and abs(diagnostic.bag_timestamp_ns-command.bag_timestamp_ns) <= 500_000_000)
        if full_pairing and not (type(m.stamp.sec) is int and m.stamp.sec >= 0
                and type(m.stamp.nanosec) is int and 0 <= m.stamp.nanosec < NS):
            invalid_stamp_indices.append(index)
            valid = False
        if not valid:
            pairing_errors.append(index)
        stamp_ns = stamp_nanoseconds(m.stamp)
        paired_stamps.append(stamp_ns)
        zero = all(v == 0. for v in vector)
        both_ready = diagnostic.in_readiness_interval and command.in_readiness_interval
        if full_pairing and diagnostic.in_readiness_interval != command.in_readiness_interval:
            excluded_boundary.append(dict(index=index, command_bag_ns=command.bag_timestamp_ns,
                diagnostic_bag_ns=diagnostic.bag_timestamp_ns,
                command_in_readiness=command.in_readiness_interval,
                diagnostic_in_readiness=diagnostic.in_readiness_interval,
                stamp_ns=stamp_ns, zero=zero))
        if not full_pairing or both_ready:
            commands.append(dict(bag_ns=command.bag_timestamp_ns,
                diagnostic_bag_ns=diagnostic.bag_timestamp_ns, stamp_ns=stamp_ns,
                valid=valid, zero=zero))
    pairing = pairing and not pairing_errors and all(a <= b
        for a, b in zip(paired_stamps, paired_stamps[1:]))
    if full_pairing:
        pairing = pairing and receipt_order_valid
    pose_topic = planned['resolved_scenario']['algorithm']['launch_overrides'].get('algorithm_pose_topic',
        '/gesc_gaussian/simulation/pose_delayed' if planned['condition'] == 'delay' else '/odom')
    alias = next((a for a,e in bag.topics_by_alias.items() if e['topic'] == pose_topic), None)
    poses = []
    for record in records_for_alias(bag, alias) if alias is not None else []:
        m = record.message
        values = [m.pose.pose.position.x, m.pose.pose.position.y,
                  m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z]
        finite = all(math.isfinite(v) for v in values)
        poses.append(dict(stamp_ns=stamp_nanoseconds(m.header.stamp), valid=finite,
            x=values[0], y=values[1], moving=bool(finite and
                (math.hypot(values[2], values[3]) >= .001 or abs(values[4]) >= .001))))
    result = metrics.continuous_acquisition_metrics(states, guidance, commands, poses,
        authority_complete=intervention.get('complete') is True,
        command_pairing_complete=pairing)
    result.update(command_pairing_errors=pairing_errors, diagnostic_count=len(diagnostics),
                  actual_command_count=len(actual), selected_pose_topic=pose_topic,
                  command_pairing_scope='recorded_readiness_interval_v1',
                  command_pairing_readiness_bounds=dict(start_ns=start, end_ns=end,
                      valid=bounds_valid, membership_valid=bool(membership_valid)),
                  command_pairing_input_counts=dict(control_diagnostics=interval_counts(full_diagnostics),
                      command_final=interval_counts(full_actual)))
    if full_pairing:
        result.update(command_pairing_scope=pairing_basis,
            command_pairing_full_counts=dict(control_diagnostics=len(full_diagnostics),
                command_final=len(full_actual)),
            command_pairing_admitted_pair_count=len(commands),
            command_pairing_excluded_boundary_pairs=excluded_boundary,
            command_pairing_receipt_order_valid=receipt_order_valid,
            command_pairing_invalid_stamp_indices=invalid_stamp_indices)
    return result


def _arrival_metrics(acquired, planned, bag, origin, *, binding_method=None):
    """Bind the existing retained arrival decision to its exact measured pose."""
    if binding_method not in (None, RECORDED_ARRIVAL_BINDING):
        raise ValueError('unsupported arrival binding method')
    outcome = acquired['runner_result'].get('outcomes', {})
    passed = outcome.get('post_recovery_global_proximity_passed')
    evidence = outcome.get('post_recovery_global_proximity') or {}
    live = acquired['runner_result'].get('record_process', {}).get('global_proximity_sample_live') or {}
    selected = planned['resolved_scenario']['success'].get('criterion') == 'post_recovery_arrival_v1'
    result = dict(arrival_criterion=planned['resolved_scenario']['success'].get('criterion'), arrival_passed=passed,
        time_to_arrival_sec=None, arrival_ros_stamp_ns=None, arrival_bag_stamp_ns=None,
        arrival_distance_m=evidence.get('distance_m'), arrival_evidence=deepcopy(evidence),
        arrival_live_evidence=deepcopy(live), arrival_measurement_complete=False,
        time_to_arrival_scope='Exact retained evaluator pose ROS stamp minus original Timekeeper origin; optional GOAL_HOLD separate.')
    if binding_method == RECORDED_ARRIVAL_BINDING:
        return _recorded_arrival_binding(result, acquired, planned, bag, origin)
    if not selected or type(passed) is not bool or outcome.get('outcome_error'):
        return result
    if not passed:
        result['arrival_measurement_complete'] = True  # Observed failure/censor, not a fabricated time.
        return result
    matches = [r for r in records_for_alias(bag, 'pose') if r.in_readiness_interval
               and r.bag_timestamp_ns == evidence.get('sample_bag_stamp')]
    if len(matches) != 1 or origin is None:
        return result
    record = matches[0]; message = record.message
    stamp = stamp_nanoseconds(message.header.stamp)
    position = {'x_m': message.pose.pose.position.x, 'y_m': message.pose.pose.position.y}
    complete = (stamp is not None and stamp >= origin and evidence.get('position') == position
        and live.get('position') == position and live.get('interpolation_used') is False
        and evidence.get('interpolation_used') is False and evidence.get('proximity_radius_m') == .5
        and live.get('proximity_radius_m') == .5 and metrics._finite(evidence.get('distance_m'))
        and 0 <= evidence['distance_m'] <= .5 and live.get('distance_m') == evidence['distance_m']
        and metrics._finite(live.get('sample_sim_sec')) and abs(round(live['sample_sim_sec']*NS)-stamp) <= 1)
    if complete:
        result.update(arrival_measurement_complete=True, time_to_arrival_sec=(stamp-origin)/NS,
            arrival_ros_stamp_ns=stamp, arrival_bag_stamp_ns=record.bag_timestamp_ns)
    return result


def _recorded_arrival_binding(result, acquired, planned, bag, origin):
    """Opt-in evaluator /odom binding; independent live evidence is descriptive.

    The original runner selects the first recorded qualifying pose independently
    of its live subscriber. Only that exact recorded pose supplies measured time.
    This method is never selected implicitly from an experiment version.
    """
    result.update(arrival_binding_method=RECORDED_ARRIVAL_BINDING,
                  arrival_binding_error=None, arrival_live_measurement_complete=False)

    def reject(reason):
        result['arrival_binding_error'] = reason
        return result

    def integer(value):
        return type(value) is int and value >= 0

    def finite(value):
        return type(value) in (int, float) and math.isfinite(value)

    outcome = acquired['runner_result'].get('outcomes', {})
    if (result['arrival_criterion'] != 'post_recovery_arrival_v1'
            or type(result['arrival_passed']) is not bool or outcome.get('outcome_error')):
        return reject('unsupported_arrival_outcome')
    if not result['arrival_passed']:
        result['arrival_measurement_complete'] = True
        return result  # Valid observed failure/censoring still has no arrival time.
    required = ('local_recovery_stage_passed', 'fill_cardinality_passed',
                'escape_command_ownership_passed', 'required_events_passed',
                'required_event_sequence_passed', 'forbidden_states_absent',
                'forbidden_events_absent')
    if any(outcome.get(key) is not True for key in required):
        return reject('successful_recovery_evidence_unavailable')
    try:
        scenario = planned['resolved_scenario']
        success = scenario['success']; stage = success['staged_recovery']
        goal = success['ground_truth']; evidence = result['arrival_evidence']
        sources = [source for source in scenario['sources'] if source['id'] == stage['global_source_id']]
        if (len(sources) != 1 or goal['global_source_id'] != stage['global_source_id']
                or goal['method'] != 'declared_global_proximity'
                or stage['global_proximity_radius_m'] != .5 or goal['proximity_radius_m'] != .5):
            return reject('goal_region_association_invalid')
        point = {'x_m': sources[0]['x_m'], 'y_m': sources[0]['y_m']}
        if (not all(finite(v) for v in point.values())
                or sources[0].get('evaluation_role') != 'goal'
                or evidence['global_source_id'] != stage['global_source_id']
                or evidence['global_point'] != point):
            return reject('goal_region_association_invalid')
        start, end = bag.readiness_start_ns, bag.readiness_end_ns
        completion = outcome['local_recovery_stage']['stage_a_completion_stamp']
        wanted = evidence['sample_bag_stamp']
        if (not all(integer(v) for v in (origin, start, end, completion, wanted))
                or start >= end or not start <= completion < wanted <= end):
            return reject('recorded_arrival_time_bounds_invalid')
        # The evaluator always observes /odom, independently of any delayed
        # algorithm pose stream selected for a detector or moving controller.
        if bag.topics_by_alias.get('pose', {}).get('topic') != '/odom':
            return reject('recorded_arrival_pose_alias_invalid')
        matches = [r for r in records_for_alias(bag, 'pose') if r.bag_timestamp_ns == wanted]
        if len(matches) != 1 or matches[0].in_readiness_interval is not True:
            return reject('recorded_arrival_pose_not_unique_or_ready')
        record = matches[0]; message = record.message; header = message.header
        if (record.topic != '/odom' or record.type_name != 'nav_msgs/msg/Odometry'
                or header.frame_id != 'odom'):
            return reject('recorded_arrival_pose_frame_or_topic_invalid')
        sec, nsec = header.stamp.sec, header.stamp.nanosec
        if not integer(sec) or not integer(nsec) or nsec >= NS:
            return reject('recorded_arrival_source_stamp_invalid')
        stamp = sec*NS+nsec
        if stamp <= origin or record.ros_timestamp_ns != stamp:
            return reject('recorded_arrival_source_stamp_invalid')
        position = {'x_m': message.pose.pose.position.x, 'y_m': message.pose.pose.position.y}

        def valid_sample(sample, xy):
            if (not isinstance(xy, dict) or set(xy) != {'x_m', 'y_m'}
                    or not all(finite(v) for v in xy.values())
                    or sample.get('position') != xy or sample.get('interpolation_used') is not False
                    or sample.get('proximity_radius_m') != .5 or not finite(sample.get('distance_m'))):
                return False
            distance = math.hypot(xy['x_m']-point['x_m'], xy['y_m']-point['y_m'])
            return (0 <= sample['distance_m'] <= .5 and distance <= .5
                    and math.isclose(sample['distance_m'], distance, rel_tol=0., abs_tol=1e-12))

        if not valid_sample(evidence, position):
            return reject('recorded_arrival_pose_or_distance_invalid')
        live = result['arrival_live_evidence']; live_time = live.get('sample_sim_sec')
        if (not valid_sample(live, live.get('position')) or not finite(live_time)
                or live_time < 0 or round(live_time*NS) <= origin
                or acquired['runner_result'].get('record_process', {}).get('global_proximity_observed_live') is not True
                or live.get('controller_ranked_goal_required') is not False):
            return reject('independent_live_arrival_invalid')
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
        return reject('recorded_arrival_evidence_malformed')
    result.update(arrival_measurement_complete=True, arrival_live_measurement_complete=True,
                  time_to_arrival_sec=(stamp-origin)/NS, arrival_ros_stamp_ns=stamp,
                  arrival_bag_stamp_ns=record.bag_timestamp_ns)
    return result


def analyze_run_data(acquired, planned, bag, geometry, metadata, *, freeze_labels, experiment_version=metrics.VERSION):
    """One in-memory union read, with a durable independent-label boundary."""
    pose_topic = planned['resolved_scenario']['algorithm']['launch_overrides'].get('algorithm_pose_topic',
        '/gesc_gaussian/simulation/pose_delayed' if planned['condition'] == 'delay' else '/odom')
    labels = metrics.analyze_labels(bag, geometry, pose_topic=pose_topic, maximum_samples=40000, experiment_version=experiment_version)
    label_ref = freeze_labels(labels)  # Must finish before detector/event inspection.
    confirmations, events, confirmation_audit, confirmation_errors = _confirmation_inputs(bag, planned)
    intervention = _intervention_inputs(bag, metadata, planned, events)
    outcomes = acquired['runner_result'].get('outcomes', {})
    error_counts = _error_counts(bag, planned, events, outcomes)
    mandatory = (_motion_metrics(bag, planned, intervention) if _v10(planned)
                 else _motion_metrics(bag, planned))
    normalized = None
    if planned['arm'] in ('C', 'D'):
        observations, qualification = analysis.prepare_m4_direction_inputs(bag, metadata, run_spec=planned,
                                                                         maximum_observations=40000)
        normalized = metrics.normalize_direction_targets(observations, qualification,
            run_id=planned['run_id'], arm=planned['arm'], partition=planned['partition'],
            condition=planned['condition'], exposure_end_ns=labels['exposure_end_ns'],
            terminal_stamp_ns=_terminal_stamp(bag), experiment_version=experiment_version)
        # Complete recorded affine/weighted law can intervene independently of
        # Gaussian commits. Use its actual composition publication timestamp.
        if qualification.get('integrity_errors'):
            intervention.update(complete=False)
            intervention['errors'].append('complete objective law extraction unavailable')
        law_stamps = [r['objective']['composition_stamp_ns'] for r in observations
                      if r.get('objective', {}).get('complete') is True and
                      (r['objective'].get('gaussian_fills') or r['objective'].get('affine_terms')
                       or r['objective'].get('weights', [1., 1., 1.])[0] != 1.)]
        intervention['first_nonempty_recorded_law_ns'] = min(law_stamps, default=None)
        interventions = law_stamps+([intervention['stamp_ns']] if intervention['stamp_ns'] is not None else [])
        intervention['stamp_ns'] = min(interventions, default=None)
    attribution_complete = intervention['complete'] and not confirmation_errors
    latency = metrics.join_first_opportunity(labels, confirmations=confirmations if not confirmation_errors else (),
        intervention_ns=intervention['stamp_ns'], intervention_evidence_complete=attribution_complete)
    origin = _origin(bag)
    goals = [stamp_nanoseconds(m.stamp) for _, m in events if m.event_type == AlgorithmEvent.EVENT_GOAL_REACHED]
    goal_ns = min(goals, default=None)
    time_goal = ((goal_ns-origin)/NS if goal_ns is not None and origin is not None and goal_ns >= origin else None)
    sequence_keys = ('local_recovery_stage_passed', 'fill_cardinality_passed',
                     'post_recovery_global_proximity_passed', 'counted_candidate_ranked_goal_passed')
    if _v10(planned):
        sequence_keys = metrics.ARRIVAL_SEQUENCE_KEYS
    sequence = [outcomes.get(key) for key in sequence_keys]
    required_keys = (metrics.arrival_sequence_required_keys(experiment_version)
                     if _v10(planned) else sequence_keys)
    required_sequence = [outcomes.get(key) for key in required_keys]
    combined = all(required_sequence) if all(type(v) is bool for v in required_sequence) else None
    result = {**acquired, 'labels': label_ref, 'latency': latency,
              'confirmation_audit': confirmation_audit, 'confirmation_errors': confirmation_errors,
              'intervention': intervention, **error_counts,
              'combined_sequence_passed': combined, 'combined_sequence_components': dict(zip(sequence_keys, sequence)),
              'mandatory_stopped_acquisitions': mandatory['mandatory_stopped_acquisitions'],
              'mandatory_stop_evidence': mandatory,
              'time_to_goal_sec': time_goal, 'goal_publication_ns': goal_ns, 'time_origin_ns': origin,
              'time_to_goal_scope': 'actual first GOAL publication minus original Timekeeper origin; missing is unavailable',
              'path_length': analysis._path_length([r for r in records_for_alias(bag, 'pose' if _v10(planned) else 'odometry')
                                                   if r.in_readiness_interval]),
              'direction_analysis_complete': False}
    if normalized is not None:
        result['direction_supplemental'] = normalized['supplemental']
        result['direction_qualification'] = normalized['qualification']
    if metrics.is_integrated_arrival_experiment_version(experiment_version):
        result.update(combined_sequence_required_keys=list(required_keys),
                      combined_sequence_diagnostic_keys=['required_state_path_passed'])
    if _v10(planned):
        if experiment_version in (metrics.V13_EXPERIMENT_VERSION, metrics.V14_EXPERIMENT_VERSION):
            arrival = _arrival_metrics(acquired, planned, bag, origin,
                                       binding_method=RECORDED_ARRIVAL_BINDING)
        else:
            arrival = _arrival_metrics(acquired, planned, bag, origin)
        result.update(arrival)
        result['combined_sequence_components']['arrival_criterion'] = arrival['arrival_criterion']
        result['combined_sequence_components']['arrival_measurement_complete'] = arrival['arrival_measurement_complete']
        if combined is True and not arrival['arrival_measurement_complete']:
            result['combined_sequence_passed'] = None
        result['optional_controller_goal'] = dict(time_to_goal_sec=time_goal, publication_ns=goal_ns,
            ranked_goal_passed=outcomes.get('counted_candidate_ranked_goal_passed'))
        negatives = [r for r in labels.get('labels', []) if r['kind'] == 'negative_directed_progress']
        labeled_events = analysis.classify_v2_detector_events(
            [dict(r, stamp_ns=r['source_ns']) for r in confirmations], labels.get('labels', []))
        result['negative_control_confirmations'] = dict(
            count=sum(r['independent_label'] == 'negative' for r in labeled_events),
            observed_negative_interval_count=len(negatives), events=labeled_events,
            scope='Existing independent classifier at confirmation support endpoint; unknown/ambiguous retained separately.')
        poses = [r for r in labels.get('poses', []) if r.get('readiness_eligible') and type(r.get('stamp_ns')) is int]
        checks = dict(
            acquisition_complete=acquired.get('status') == 'COMPLETE' and acquired.get('integrity_passed') is True,
            position_labels_complete=labels.get('spatial_labels_precede_event_join') is True
                and labels.get('admission_ns') is not None and len(poses) >= 2
                and not any(v for k,v in labels.get('pose_faults', {}).items() if k != 'identical_pose_repeat')
                and all(0 < b['stamp_ns']-a['stamp_ns'] <= 500_000_000 for a,b in zip(poses, poses[1:])),
            confirmation_attribution_complete=not confirmation_errors,
            selected_authority_complete=intervention.get('complete') is True,
            error_attribution_complete=not error_counts.get('attribution_errors')
                and all(type(error_counts.get(name)) is int and error_counts[name] >= 0
                        for name in ('wrong_fills', 'wrong_goals')),
            arrival_measurement_complete=arrival['arrival_measurement_complete'],
            path_length_complete=result['path_length'].get('status') == 'valid',
            motion_measurement_complete=planned['arm'] not in ('C', 'D') or mandatory.get('analysis_complete') is True,
            direction_inputs_complete=normalized is None or (normalized['qualification'].get('qualified') is True
                and not normalized['qualification'].get('integrity_errors')))
        result['scientific_analysis_checks'] = checks
        result['scientific_analysis_complete'] = all(checks.values())
    return result, normalized


def _context(contract_path):
    contract = read_json(contract_path)
    if str(Path(contract_path).resolve()) != contract['contract_path']:
        raise ValueError('M4 contract path differs from frozen identity')
    verify_frozen(contract, verify_geometry_points=False)
    return contract


def _acquired(contract, planned):
    path = Path(contract['root'])/'acquisition'/f"slot_{planned['slot']}.json"
    acquired = read_json(path)
    if contract['version'] != metrics.VERSION and (
            acquired.get('experiment_version') != contract['version']
            or acquired.get('visible') != planned['visible']):
        raise ValueError('M4 v2 acquisition experiment/visibility differs')
    if (acquired.get('status') != 'COMPLETE' or acquired.get('integrity_passed') is not True
            or any(acquired.get(k) != planned[k] for k in
                   ('slot', 'block', 'run_id', 'case_id', 'seed', 'arm', 'partition', 'geometry', 'condition'))):
        raise ValueError('M4 science input is not its complete reserved acquisition')
    check_receipts(acquired['input_files'])
    return acquired, receipt(path)


def labels_stage(contract, block, *, output_directory=None):
    if type(block) is not int or not 0 <= block <= 3:
        raise ValueError('M4 block outside fixed population')
    directory = (Path(contract['root'])/'analysis'/f'block_{block}'
                 if output_directory is None else Path(output_directory))
    directory.mkdir(parents=True, exist_ok=True)
    atomic_exclusive_json(directory/'labels_stage_started.json', dict(version=metrics.VERSION, **metrics.experiment_fields(contract['version']), block=block))
    rows, inputs = [], []
    for slot in range(block*4+1, block*4+5):
        planned = slot_spec(contract, slot)
        acquired, acquisition_ref = _acquired(contract, planned)
        inputs.append(acquisition_ref)
        run_directory = Path(acquired['run_directory'])
        metadata = load_yaml(run_directory/'metadata.yaml')
        resolved_topics = load_yaml(run_directory/'resolved_topics.yaml')
        check_receipts([planned['geometry_receipt']])
        geometry = read_json(planned['geometry_receipt']['path'])
        scenario = planned['resolved_scenario']
        if load_yaml(run_directory/'resolved_scenario.yaml') != scenario:
            raise ValueError('recorded scenario differs from reserved M4 science input')
        pose_topic = scenario['algorithm']['launch_overrides'].get('algorithm_pose_topic',
            '/gesc_gaussian/simulation/pose_delayed' if planned['condition'] == 'delay' else '/odom')
        stream = runner.build_v2_stream_config(scenario) if planned['arm'] in ('C', 'D') else None
        selection = ({'experiment_version': contract['version'], 'arm': planned['arm']}
                     if metrics.is_arrival_experiment_version(contract['version']) else {})
        aliases = metrics.science_aliases(resolved_topics, pose_topic=pose_topic, stream_config=stream, **selection)
        bag = read_run_bag(run_directory, aliases=aliases)
        def freeze(document):
            path = directory/f'slot_{slot}_labels.json'
            digest = atomic_exclusive_json(path, document)
            return {'path': str(path.resolve()), 'sha256': digest}
        edition = ({'experiment_version': contract['version']} if contract['version'] != metrics.VERSION else {})
        result, normalized = analyze_run_data(acquired, planned, bag, geometry, metadata, freeze_labels=freeze, **edition)
        if normalized is not None:
            path = directory/f'slot_{slot}_normalized.json'
            digest = atomic_exclusive_json(path, normalized)
            result['normalized_inputs'] = {'path': str(path.resolve()), 'sha256': digest}
        result['acquisition_receipt'] = acquisition_ref
        rows.append(result)
        atomic_exclusive_json(directory/f'slot_{slot}_metrics.json', result)
        del bag
    if metrics.is_arrival_experiment_version(contract['version']):
        for row in rows:
            check_receipts([row['acquisition_receipt'], row['labels'], *row['input_files'],
                            *([row['normalized_inputs']] if 'normalized_inputs' in row else [])])
        verify_frozen(contract, verify_geometry_points=False)
    document = dict(version=metrics.VERSION, **metrics.experiment_fields(contract['version']), block=block, complete=True, integrity_passed=True,
                    runs=rows, input_files=inputs, contract=receipt(contract['contract_path']))
    atomic_exclusive_json(directory/'labels.json', document)
    return document


def references_stage(contract, slot):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    planned = slot_spec(contract, slot)
    if planned['arm'] not in ('C', 'D'):
        raise ValueError('M4 reference slots exist only for C/D')
    directory = Path(contract['root'])/'analysis'/f"block_{planned['block']}"
    label_document = read_json(directory/'labels.json')
    if contract['version'] != metrics.VERSION:
        metrics.validate_experiment_document(label_document, contract['version'])
        if (label_document.get('contract') != receipt(contract['contract_path'])
                or label_document.get('block') != planned['block']
                or label_document.get('complete') is not True
                or label_document.get('integrity_passed') is not True):
            raise ValueError('M4 v2 reference label contract/block binding differs')
    row = next(r for r in label_document['runs'] if r['slot'] == slot)
    check_receipts([row['acquisition_receipt'], row['normalized_inputs'], row['labels']])
    normalized = read_json(row['normalized_inputs']['path'])
    if contract['version'] != metrics.VERSION:
        metrics.validate_experiment_document(normalized, contract['version'])
        metrics.validate_experiment_document(read_json(row['labels']['path']), contract['version'])
        for key, expected in (('labels', directory/f'slot_{slot}_labels.json'),
                              ('normalized_inputs', directory/f'slot_{slot}_normalized.json'),
                              ('acquisition_receipt', Path(contract['root'])/'acquisition'/f'slot_{slot}.json')):
            if Path(row[key]['path']).resolve() != expected:
                raise ValueError('M4 v2 reference path differs from reserved experiment input')
    if any(normalized[k] != planned[k] for k in ('run_id', 'arm', 'partition', 'condition')):
        raise ValueError('M4 normalized reference population differs')
    binding = row['binding']
    model_ref = binding['selected_configurations']['cost_function_config_filepath']
    check_receipts([model_ref])
    model, _ = truth._model(planned['resolved_scenario']['sources'], model_ref['path'], binding['binding'])
    incremental = directory/f'slot_{slot}_partial_references'
    incremental.mkdir(exist_ok=False)
    result = metrics.evaluate_direction_targets(normalized,
        raw_owner=lambda x, y, phase: truth.evaluate_raw_cost(model, x, y, phase),
        binding=binding['binding'], sources=planned['resolved_scenario']['sources'],
        on_result=lambda value: atomic_exclusive_json(incremental/f"target_{value['number']}.json", value))
    if len(result.get('rows', [])) != 24 or [r['number'] for r in result['rows']] != list(range(1, 25)):
        raise ValueError('M4 numerical owner did not retain all 24 scheduled targets')
    if metrics.is_arrival_experiment_version(contract['version']):
        check_receipts([row['acquisition_receipt'], row['normalized_inputs'], row['labels'],
                        *row['input_files'], model_ref])
        verify_frozen(contract, verify_geometry_points=False)
    document = {**result, 'slot': slot, 'run_id': planned['run_id'], 'complete': True,
                'integrity_passed': True, 'direction_analysis_complete': True,
                'normalized_inputs': row['normalized_inputs'], 'contract': receipt(contract['contract_path'])}
    atomic_exclusive_json(directory/f'slot_{slot}_references.json', document)
    return document


def summary_stage(contract, block):
    directory = Path(contract['root'])/'analysis'/f'block_{block}'
    path = directory/'labels.json'
    labels = read_json(path)
    metrics.validate_experiment_document(labels, contract['version'])
    if contract['version'] != metrics.VERSION and labels.get('contract') != receipt(contract['contract_path']):
        raise ValueError('M4 v2 summary label contract differs')
    if (labels.get('version') != metrics.VERSION or labels.get('block') != block
            or labels.get('complete') is not True or labels.get('integrity_passed') is not True
            or [r['slot'] for r in labels['runs']] != list(range(block*4+1, block*4+5))):
        raise ValueError('M4 block label result incomplete or mismatched')
    check_receipts([labels['contract'], *labels['input_files']])
    rows, references = deepcopy(labels['runs']), []
    if metrics.is_arrival_experiment_version(contract['version']):
        for row in rows:
            check_receipts([row['acquisition_receipt'], row['labels'], *row['input_files'],
                            *([row['normalized_inputs']] if 'normalized_inputs' in row else [])])
    for row in rows:
        if row['arm'] not in ('C', 'D'):
            continue
        path = directory/f"slot_{row['slot']}_references.json"
        if not path.exists():
            row.update(direction_analysis_complete=False, direction_unavailable_reason='reference_job_no_complete_result')
            continue
        result = read_json(path)
        if contract['version'] != metrics.VERSION:
            metrics.validate_experiment_document(result, contract['version'])
            if result.get('contract') != receipt(contract['contract_path']):
                raise ValueError('M4 v2 summary reference contract differs')
        check_receipts([result['normalized_inputs'], result['contract']])
        if (result.get('slot') != row['slot'] or result.get('run_id') != row['run_id']
                or result.get('complete') is not True or result.get('integrity_passed') is not True
                or result.get('direction_analysis_complete') is not True or len(result['rows']) != 24
                or result['normalized_inputs'] != row['normalized_inputs']):
            raise ValueError('M4 reference result incomplete or mismatched')
        row.update(direction_rows=result['rows'], direction_analysis_complete=True,
                   direction_summary=result['summary'], direction_supplemental=result['supplemental'])
        references.append(receipt(path))
    aggregate = metrics.aggregate_pilot(rows, experiment_version=contract['version'])  # Existing fixed-population validator.
    result = dict(version=metrics.VERSION, **metrics.experiment_fields(contract['version']), block=block, complete=True, integrity_passed=True,
                  runs=rows, labels=receipt(directory/'labels.json'), references=references)
    if metrics.is_arrival_experiment_version(contract['version']):
        checks = dict(four_arm_analysis_complete=len(rows) == 4
            and [r['arm'] for r in rows] == list(metrics.ARMS)
            and all(r.get('scientific_analysis_complete') is True
                    and r.get('scientific_analysis_checks')
                    and all(value is True for value in r['scientific_analysis_checks'].values()) for r in rows),
            both_reference_products_complete=len(references) == 2 and all(
                r.get('direction_analysis_complete') is True
                and metrics.direction_product_complete(r.get('direction_rows', []), r)
                for r in rows if r['arm'] in ('C', 'D')))
        check_receipts([result['labels'], *references, *labels['input_files']])
        verify_frozen(contract, verify_geometry_points=False)
        result.update(scientific_analysis_checks=checks, scientific_analysis_complete=all(checks.values()),
                      contract=receipt(contract['contract_path']))
    if contract['version'] == metrics.V11_EXPERIMENT_VERSION and block == 0:
        result['development_latency_feasibility'] = metrics.development_latency_feasibility(
            rows, experiment_version=contract['version'])
    if metrics.is_integrated_arrival_experiment_version(contract['version']):
        result.update(scientific_scope=aggregate['scientific_scope'],
                      secondary_endpoint=aggregate['secondary_endpoint'])
    atomic_exclusive_json(directory/'result.json', result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='stage', required=True)
    for name in ('labels', 'references', 'summary'):
        child = subparsers.add_parser(name)
        child.add_argument('--contract', required=True)
        child.add_argument('--slot' if name == 'references' else '--block', required=True, type=int)
    args = parser.parse_args(argv)
    contract = _context(args.contract)
    if args.stage == 'references':
        references_stage(contract, args.slot)
    elif args.stage == 'labels':
        labels_stage(contract, args.block)
    else:
        summary_stage(contract, args.block)
    print('M4 '+args.stage+' complete')


if __name__ == '__main__':
    main()
