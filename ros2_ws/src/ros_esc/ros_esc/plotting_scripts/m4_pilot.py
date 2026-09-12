"""Finite M4 evidence contracts subordinate to the existing bag analyzer.

No acquisition, CLI, model implementation, or state/control ownership lives here.
The caller freezes source/geometry/input receipts and enforces process deadlines.
"""

from bisect import bisect_left
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
import statistics

from ros_esc.scenario_runner.m4_scenario import (
    V11_EXPERIMENT_VERSION, V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION,
    experiment_method_version, is_arrival_experiment_version,
    is_integrated_arrival_experiment_version, is_retained_development_experiment_version,
)

VERSION = 'm4-pilot-v1'
ARRIVAL_VERSION = 'm4-pilot-v10'
ARRIVAL_METHOD = 'recurrent_arrival_v10'
RECORDED_ARRIVAL_BINDING = 'recorded_pose_arrival_v1'
MAX_OBSERVATIONS = 40000
TARGET_OFFSETS_SEC = tuple(15 + 30*k for k in range(24))
NS = 1_000_000_000
CONDITIONS = ('nominal', 'noise', 'delay')
ARMS = ('A', 'B', 'C', 'D')
ARRIVAL_SEQUENCE_KEYS = ('local_recovery_stage_passed', 'fill_cardinality_passed',
    'required_state_path_passed', 'escape_command_ownership_passed',
    'required_events_passed', 'required_event_sequence_passed',
    'forbidden_states_absent', 'forbidden_events_absent',
    'post_recovery_global_proximity_passed')


def arrival_sequence_required_keys(experiment_version):
    """Integrated arrival versions retain only the first-path key as diagnostic."""
    if not is_arrival_experiment_version(experiment_version):
        raise ValueError('arrival sequence requires an explicit arrival experiment')
    return tuple(key for key in ARRIVAL_SEQUENCE_KEYS
                 if not is_integrated_arrival_experiment_version(experiment_version)
                 or key != 'required_state_path_passed')


def experiment_fields(experiment_version=VERSION):
    """Separate the unchanged scientific method from a fresh experiment."""
    from ros_esc.scenario_runner.m4_scenario import experiment_identity
    experiment_identity(experiment_version)
    return ({} if experiment_version == VERSION else
            {'experiment_version': experiment_version,
             'method_version': experiment_method_version(experiment_version)})


def validate_experiment_document(document, experiment_version=VERSION):
    fields = experiment_fields(experiment_version)
    if (document.get('version') != VERSION
            or document.get('experiment_version', VERSION) != experiment_version
            or any(document.get(key) != value for key, value in fields.items())):
        raise ValueError('M4 scientific document belongs to a different experiment/method')
    return experiment_version


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def _ns(value, name, *, optional=False):
    if value is None and optional:
        return value
    if type(value) is not int or value < 0:
        raise ValueError(name + ' must be nonnegative integer nanoseconds')
    return value


def _finite(value):
    return type(value) in (float, int) and math.isfinite(value)


def continuous_acquisition_metrics(states, guidance, commands, poses, *, authority_complete,
                                   command_pairing_complete):
    """V10 source-time acquisition evidence; numerical rules frozen prospectively.

    Inputs are retained projections of the actual typed streams. A command's
    source time belongs to its exactly paired diagnostic; Twist has no header.
    Existing lifecycle validation remains the authority/identity checker.
    """
    gap_ns = 500_000_000
    def coverage(rows, start, end):
        stamps = sorted({r['stamp_ns'] for r in rows if r.get('valid') is True})
        before = [s for s in stamps if s <= start]
        after = [s for s in stamps if s >= end]
        if not before or not after:
            return False
        lo, hi = before[-1], after[0]
        selected = [s for s in stamps if lo <= s <= hi]
        return (start-lo <= gap_ns and hi-end <= gap_ns
                and all(b-a <= gap_ns for a,b in zip(selected, selected[1:])))

    def longest_observed_low_run(rows):
        longest, first = 0, None
        for row in rows:
            if row['moving']:
                first = None
            else:
                first = row['stamp_ns'] if first is None else first
                longest = max(longest, row['stamp_ns']-first)
        return longest

    valid_states = bool(states) and all(r.get('valid') is True for r in states)
    monotone = all(a['stamp_ns'] <= b['stamp_ns'] for a,b in zip(states, states[1:]))
    phases, current = [], None
    for row in states:
        selected = row['state'] == 2 or (row['state'] == 3 and row['previous_state'] == 2)
        key = row['state'] if selected else None
        if current is not None and current['state'] != key:
            current.update(end_ns=row['stamp_ns'], censored=False)
            phases.append(current); current = None
        if selected and current is None:
            current = dict(state=key, start_ns=row['stamp_ns'])
    if current is not None:
        current.update(end_ns=states[-1]['stamp_ns'], censored=True)
        phases.append(current)
    evidence = []
    zeros = []
    successor = None
    for row in reversed(commands):
        if row['zero']:
            zeros.append(dict(bag_timestamp_ns=row['bag_ns'], diagnostic_ros_stamp_ns=row['stamp_ns'],
                next_nonzero_bag_timestamp_ns=None if successor is None else successor['bag_ns'],
                next_nonzero_diagnostic_ros_stamp_ns=None if successor is None else successor['stamp_ns'],
                duration_sec=None if successor is None else max(0, successor['stamp_ns']-row['stamp_ns'])/NS,
                bag_duration_sec=None if successor is None else (successor['bag_ns']-row['bag_ns'])/NS))
        else:
            successor = row
    zeros.reverse()
    for phase in phases:
        start, end = phase['start_ns'], phase['end_ns']
        ps = [r for r in poses if start <= r['stamp_ns'] <= end and r.get('valid') is True]
        cs = [r for r in commands if start <= r['stamp_ns'] < end and r.get('valid') is True]
        gs = [r for r in guidance if start <= r['stamp_ns'] <= end]
        path = sum(math.hypot(b['x']-a['x'], b['y']-a['y']) for a,b in zip(ps, ps[1:]))
        low_ns = longest_observed_low_run(ps)
        zero_rows = [dict(r, acquisition_overlap_duration_sec=max(0,
            min(end, r['next_nonzero_diagnostic_ros_stamp_ns'] or end)
            -max(start, r['diagnostic_ros_stamp_ns']))/NS)
            for r in zeros if r['diagnostic_ros_stamp_ns'] < end
            and (r['next_nonzero_diagnostic_ros_stamp_ns'] or end) > start]
        zero_ns = max((min(end, r['next_nonzero_diagnostic_ros_stamp_ns'] or end)
                       -max(start, r['diagnostic_ros_stamp_ns']) for r in zero_rows), default=0)
        covered = (not phase['censored'] and end > start
                   and coverage(states, start, end) and coverage(guidance, start, end)
                   and coverage(commands, start, end) and coverage(poses, start, end))
        positive = (len(ps) >= 2 and path > 0 and any(r['moving'] for r in ps)
                    and any(not r['zero'] for r in cs)
                    and any(r.get('proposal_valid') and r.get('proposal_nonzero') for r in gs))
        evidence.append({**phase, 'coverage_complete': covered,
            'measured_pose_count': len(ps), 'measured_path_length_m': path,
            'positive_motion_evidence': positive,
            'maximum_observed_stationary_duration_sec': low_ns/NS,
            'maximum_zero_command_duration_sec': max(0, zero_ns)/NS,
            'sustained_stationary_interval': low_ns >= gap_ns,
            'sustained_zero_command_interval': zero_ns >= gap_ns,
            'command_count': len(cs), 'zero_command_count': len(zero_rows),
            'guidance_reasons': dict(Counter(r.get('reason', '') for r in gs)),
            'zero_publications': zero_rows})
    base_complete = bool(authority_complete and command_pairing_complete and valid_states and monotone)
    if not phases:
        search = [r for r in states if r['state'] == 1]
        complete = bool(base_complete and len(search) >= 2
            and coverage(states, search[0]['stamp_ns'], search[-1]['stamp_ns'])
            and coverage(poses, search[0]['stamp_ns'], search[-1]['stamp_ns'])
            and coverage(commands, search[0]['stamp_ns'], search[-1]['stamp_ns']))
        status = 'NO_ACQUISITION_OBSERVED' if complete else 'EVIDENCE_UNAVAILABLE'
    else:
        complete = base_complete and all(r['coverage_complete'] for r in evidence)
        if not complete:
            status = 'EVIDENCE_UNAVAILABLE'
        elif any(r['sustained_stationary_interval'] for r in evidence):
            status = 'OBSERVED_STATIONARY_INTERVAL'
        elif any(r['sustained_zero_command_interval'] for r in evidence):
            status = 'OBSERVED_ZERO_COMMAND_INTERVAL'
        elif not all(r['positive_motion_evidence'] for r in evidence):
            complete, status = False, 'EVIDENCE_UNAVAILABLE'
        else:
            status = ('OBSERVED_CONTINUOUS_ACQUISITION' if {r['state'] for r in evidence} == {2,3}
                      else 'OBSERVED_CONTINUOUS_VERIFY_ONLY')
    return dict(status=status, analysis_complete=bool(complete),
        mandatory_stopped_acquisitions=0 if status == 'OBSERVED_CONTINUOUS_ACQUISITION' else None,
        acquisition_segments=evidence, acquisition_segment_count=len(phases),
        source_gap_limit_sec=.5, stationary_duration_limit_sec=.5,
        planar_speed_threshold_mps=.001, angular_speed_threshold_radps=.001,
        command_pairing_complete=bool(command_pairing_complete), authority_complete=bool(authority_complete),
        zero_publication_count=len(zeros),
        scope='Actual command/typed guidance/source pose evidence; measured stops do not establish a mandatory sensor sweep.')


def science_aliases(resolved_topics, *, pose_topic, stream_config=None,
                    experiment_version=VERSION, arm=None):
    """Resolve one finite union for the caller's existing filtered bag reader."""
    entries = resolved_topics.get('topics', resolved_topics) if isinstance(resolved_topics, dict) else resolved_topics
    by_topic = {entry['topic']: entry['alias'] for entry in entries}
    aliases = {entry['alias'] for entry in entries}
    if pose_topic not in by_topic:
        raise ValueError('selected pose topic has no recording alias')
    required = {'clock', 'algorithm_state', 'recording_ready', by_topic[pose_topic]}
    required |= aliases & {'algorithm_events', 'gaussian_fills', 'convergence_status',
                           'centroid_convergence_diagnostics', 'control_diagnostics',
                           'supervisor_command', 'timekeeper', 'stationary_fill_requests',
                           'cost_breakdown', 'gesc_diagnostics', 'odometry'}
    if stream_config is not None:
        from ros_esc.v2_stream import TOPIC_KEYS
        for key in TOPIC_KEYS:
            if stream_config[key] not in by_topic:
                raise ValueError('M4 moving input topic has no recording alias: ' + key)
            required.add(by_topic[stream_config[key]])
        required |= {'v2_direction_diagnostics', 'v2_direction_policy_diagnostics'}
        required |= aliases & {'v2_detector_confirmation', 'v2_candidate_snapshots',
                               'v2_recurrent_candidate_snapshots', 'v2_recurrent_fill_commands',
                               'v2_search_epoch', 'v2_pde_history_evidence',
                               'v2_fill_commands', 'v2_fill_results'}
    if is_arrival_experiment_version(experiment_version):
        if arm not in ARMS:
            raise ValueError('V10 science selection requires its explicit arm')
        required |= {'pose', 'command_final', 'control_diagnostics', 'algorithm_events',
                     'gaussian_fills', 'timekeeper'}
        if arm in ('B', 'D'):
            required.add('recurrent_convergence_diagnostics')
        if arm == 'B':
            required.add('stationary_recurrent_fill_requests')
        if arm in ('C', 'D'):
            required.add('v2_verification_guidance')
    if not required <= aliases:
        raise ValueError('missing M4 science aliases: ' + ', '.join(sorted(required-aliases)))
    return tuple(sorted(required))


def analyze_labels(bag, geometry, *, pose_topic, frame_id='odom', maximum_samples=MAX_OBSERVATIONS,
                   experiment_version=VERSION):
    """Freeze position-only intervals before projecting SEARCH or joining events.

    Short positive-region exposures are retained; the twelve-second sustained
    residence rule is applied independently of any detector or fill outcome.
    """
    fields = experiment_fields(experiment_version)
    from . import gesc_gaussian_bag_analysis as analysis
    from .q1_study import _selected_pose_samples
    if type(maximum_samples) is not int or not 0 < maximum_samples <= MAX_OBSERVATIONS:
        raise ValueError('M4 pose capacity must be within its frozen 40000 limit')
    if (geometry.get('method') != 'operational_enclosure_v1'
            or not geometry.get('basins') or not all(b.get('qualified') is True for b in geometry['basins'])):
        raise ValueError('M4 requires complete independently qualified enclosure geometry')
    poses, faults = _selected_pose_samples(bag, pose_topic, frame_id,
                                          maximum_samples=maximum_samples)
    intervals = analysis.label_v2_basin_intervals(poses, geometry, minimum_residence_sec=0.)
    for row in intervals:
        # The shared historical owner retains its54s replay annotation. M4 has
        # its own12s residence/censor contract and never consumes that annotation.
        row.pop('common_support_eligible', None)
    # Hash before reading even the state-only eligibility projection.
    position_hash = canonical_sha256({'poses': poses, 'geometry': geometry, 'intervals': intervals})
    labels = [row for row in intervals if row['kind'] != 'positive_basin_residence'
              or row['duration_sec'] >= 12.]
    short = [row for row in intervals if row['kind'] == 'positive_basin_residence'
             and row['duration_sec'] < 12.]
    masked = analysis.q1_pose_search_eligibility(poses, bag)
    eligible = [row for row in masked if row['qualified']]
    return {'version': VERSION, **fields, 'pose_topic': pose_topic, 'frame_id': frame_id,
            'geometry_sha256': canonical_sha256(geometry), 'position_inputs_sha256': position_hash,
            'labels_sha256': canonical_sha256(labels), 'labels': labels,
            'short_residences': short, 'residence_intervals': [r for r in intervals
                if r['kind'] == 'positive_basin_residence'],
            'poses': masked, 'pose_faults': faults,
            'admission_ns': eligible[0]['stamp_ns'] if eligible else None,
            'observation_start_ns': next((r['stamp_ns'] for r in poses if r['qualified']), None),
            'exposure_end_ns': max((r['stamp_ns'] for r in poses if r['qualified']), default=None),
            'spatial_labels_precede_event_join': True,
            'claim': 'finite_sampled_model_region_residence_not_attraction_dynamics'}


def join_first_opportunity(label_result, *, admission_ns=None, confirmation_stamps_ns=(),
                           confirmations=(), intervention_ns=None, intervention_evidence_complete=False,
                           exposure_end_ns=None, source_id='local'):
    """Join frozen pose-source entry to the actual ROS confirmation decision.

    A SEARCH transition caused by confirmation is not right censoring. A change
    to the objective is: later raw-field residence cannot qualify the earlier law.
    """
    if label_result.get('spatial_labels_precede_event_join') is not True:
        raise ValueError('position labels must precede detector/event joins')
    admission = _ns(label_result.get('admission_ns') if admission_ns is None else admission_ns,
                    'admission', optional=True)
    end = _ns(label_result.get('exposure_end_ns') if exposure_end_ns is None else exposure_end_ns,
              'exposure end', optional=True)
    intervention = _ns(intervention_ns, 'intervention', optional=True)
    decisions = [{'decision_ns': _ns(value, 'confirmation decision'), 'source_ns': value}
                 for value in confirmation_stamps_ns]
    for record in confirmations:
        decision = _ns(record['decision_ns'], 'confirmation decision')
        source = _ns(record['source_ns'], 'confirmation source')
        if source > decision:
            raise ValueError('confirmation decision precedes source support')
        decisions.append({'decision_ns': decision, 'source_ns': source})
    decisions.sort(key=lambda record: record['decision_ns'])
    result = {'status': 'EVIDENCE_UNAVAILABLE', 'reason': 'no_eligible_search_admission',
              'source_id': source_id, 'first_opportunity': None, 'latency_sec': None,
              'confirmation_ns': None, 'left_censored': False, 'right_censored': False,
              'censor_bound_sec': None, 'later_opportunity_count': 0,
              'independently_eligible': False, 'observed': False}
    if admission is None or end is None:
        return result
    if intervention_evidence_complete is not True:
        result['reason'] = 'objective_intervention_attribution_unavailable'
        return result
    opportunities = sorted((deepcopy(row) for row in label_result['residence_intervals']
                            if row['source_id'] == source_id and row['end_ns'] >= admission),
                           key=lambda row: row['start_ns'])
    if not opportunities:
        result['reason'] = 'no_positive_region_opportunity'
        return result
    first = opportunities[0]
    start, residence_end = first['start_ns'], first['end_ns']
    censor = min(residence_end, end, intervention if intervention is not None else end)
    result.update(first_opportunity=first, later_opportunity_count=len(opportunities)-1,
                  left_censored=start < admission or start == label_result.get('observation_start_ns'),
                  censor_bound_sec=max(0., (censor-start)/NS),
                  right_censored=True, reason='short_or_censored_first_residence')
    if intervention is not None and intervention <= start:
        result['reason'] = 'first_residence_after_objective_intervention'
        return result
    if result['left_censored']:
        result['reason'] = 'entry_precedes_eligible_search_admission'
        return result
    if censor-start < 12*NS:
        return result
    result['independently_eligible'] = True
    # Confirmed candidates must have intact pre-confirmation source/SEARCH
    # admission. We never demand SEARCH after the candidate transition.
    admitted = []
    for decision in decisions:
        stamp, source = decision['decision_ns'], decision['source_ns']
        if not start <= stamp <= censor or (intervention is not None and stamp >= intervention):
            continue
        support = [p for p in label_result['poses'] if type(p.get('stamp_ns')) is int
                   and start <= p['stamp_ns'] <= source]
        if (support and support[0]['stamp_ns'] == start and support[-1]['qualified']
                and source-support[-1]['stamp_ns'] <= 500_000_000
                and all(p['qualified'] for p in support)
                and len({p.get('history_generation') for p in support}) == 1
                and all(0 < b['stamp_ns']-a['stamp_ns'] <= 500_000_000
                        for a, b in zip(support, support[1:]))):
            admitted.append(decision)
    if not admitted:
        result['reason'] = 'first_residence_has_no_eligible_confirmation'
        return result
    stamp = admitted[0]['decision_ns']
    result.update(status='OBSERVED', reason=None, latency_sec=(stamp-start)/NS,
                  confirmation_ns=stamp, confirmation_source_ns=admitted[0]['source_ns'],
                  right_censored=False, observed=True,
                  latency_clock='absolute_ros_publication_decision_minus_pose_source_entry')
    return result


def normalize_direction_targets(observations, qualification, *, run_id, arm, partition,
                                condition, exposure_end_ns=None, terminal_stamp_ns=None, experiment_version=VERSION):
    """Freeze all24 input-only anchors; no confidence/error or nominee selection."""
    from .v2_direction_reference import select_causal_anchor
    fields = experiment_fields(experiment_version)
    if experiment_version != VERSION:
        from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
        bound = [row for row in expected_slots(experiment_version)
                 if experiment_run_id(row, experiment_version) == run_id]
        if len(bound) != 1 or any(bound[0][key] != value for key, value in
                (('arm', arm), ('partition', partition), ('condition', condition))):
            raise ValueError('M4 direction input belongs to a different experiment/run')
    if arm not in ('C', 'D') or partition not in ('development', 'holdout') or condition not in CONDITIONS:
        raise ValueError('M4 direction population identity is invalid')
    if not isinstance(run_id, str) or not run_id or len(observations) > MAX_OBSERVATIONS:
        raise ValueError('M4 direction identity/capacity is invalid')
    stamps = [_ns(row['stamp_ns'], 'observation') for row in observations]
    if any(a >= b for a, b in zip(stamps, stamps[1:])):
        raise ValueError('M4 direction observations must retain unique increasing source time')
    origin = _ns(qualification.get('origin_ns'), 'direction origin', optional=True)
    end = _ns(exposure_end_ns if exposure_end_ns is not None else (stamps[-1] if stamps else None),
              'direction exposure end', optional=True)
    terminal = _ns(terminal_stamp_ns, 'terminal source stamp', optional=True)
    qualified = qualification.get('qualified') is True and not qualification.get('integrity_errors')
    targets = []
    for number, offset in enumerate(TARGET_OFFSETS_SEC, 1):
        target = None if origin is None else origin+offset*NS
        index = select_causal_anchor(observations, target) if qualified else None
        if terminal is not None and target is not None and target > terminal:
            status, index = 'terminated', None
        elif target is None or not qualified:
            status, index = 'invalid_input', None
        elif end is None or target > end:
            status, index = 'unexposed', None
        else:
            status = 'observed' if index is not None else 'missing_anchor'
        targets.append({'run_id': run_id, 'arm': arm, 'partition': partition,
                        'condition': condition, 'number': number, 'offset_sec': offset,
                        'target_ns': target, 'observation_index': index, 'exposure_status': status,
                        'source_stamp_ns': observations[index]['stamp_ns'] if index is not None else None})
    return {'version': VERSION, **fields, 'run_id': run_id, 'arm': arm, 'partition': partition,
            'condition': condition, 'origin_ns': origin, 'exposure_end_ns': end,
            'terminal_stamp_ns': terminal, 'qualification': deepcopy(qualification),
            'observations': deepcopy(observations), 'observations_sha256': canonical_sha256(observations),
            'targets': targets, 'supplemental': direction_supplemental(observations)}


def evaluate_direction_targets(normalized, *, raw_owner, binding, sources, on_result=None):
    """Evaluate frozen anchors with the existing augmented/observed-phase owners."""
    from . import gesc_gaussian_bag_analysis as analysis
    from . import v2_direction_reference as numeric
    experiment_version = normalized.get('experiment_version', VERSION)
    validate_experiment_document(normalized, experiment_version)
    rows = normalized['observations']
    if (normalized.get('version') != VERSION
            or canonical_sha256(rows) != normalized['observations_sha256']):
        raise ValueError('M4 normalized input receipt changed')
    expected = normalize_direction_targets(rows, normalized['qualification'],
        run_id=normalized['run_id'], arm=normalized['arm'], partition=normalized['partition'],
        condition=normalized['condition'], exposure_end_ns=normalized['exposure_end_ns'],
        terminal_stamp_ns=normalized['terminal_stamp_ns'], experiment_version=experiment_version)
    if normalized['targets'] != expected['targets']:
        raise ValueError('M4 fixed target population or anchor changed')
    results = []
    for target in normalized['targets']:
        result = {**target, 'input_qualified': False, 'reference_qualified': False,
                  'informative': False, 'eligible': False, 'usable_output': False,
                  'usable_averaging': False, 'actual_error_deg': None,
                  'instant_error_deg': None, 'paired_improvement_deg': None,
                  'reason': target['exposure_status']}
        index = target['observation_index']
        if index is not None:
            row = rows[index]
            cycle = numeric.observed_phase_cycle(rows, index)
            result.update(cycle=cycle, method=deepcopy(row['method']),
                          input_qualified=cycle['qualified'], reason=cycle.get('reason'))
            if cycle['qualified'] and row['objective'].get('complete') is True:
                try:
                    law = row['objective']
                    objective = numeric.augmented_objective(raw_owner, base_xy=row['xy'],
                        binding=binding, weights=law['weights'], gaussian_fills=law['gaussian_fills'],
                        affine_terms=law['affine_terms'])
                    reference = numeric.observed_phase_reference(objective, cycle=cycle,
                                                                 xy=row['xy'], sources=sources)
                    result.update(reference=reference, objective_snapshot=deepcopy(law),
                                  reference_qualified=reference['qualified'],
                                  informative=reference['informative'], reason=reference.get('reason'))
                    result['eligible'] = bool(reference['qualified'] and reference['informative']
                                              and row.get('blend_allowed') is True)
                    if reference['qualified'] and reference['informative']:
                        actual = numeric.angular_error_deg(row['method']['v2_output_world'], reference['world_vector'])
                        instant = numeric.angular_error_deg(row['method']['aligned_instant_world'], reference['world_vector'])
                        result.update(actual_error_deg=actual, instant_error_deg=instant,
                                      usable_output=actual is not None,
                                      usable_averaging=bool(actual is not None and row['method'].get('usable_averaging')),
                                      paired_improvement_deg=None if actual is None or instant is None else instant-actual)
                except TimeoutError:
                    raise
                except (ValueError, ArithmeticError, KeyError, TypeError) as error:
                    result['reason'] = 'reference_unavailable: ' + str(error)
            elif cycle['qualified']:
                result['reason'] = 'objective_snapshot_unavailable'
        result = analysis._q1_plain(result)
        results.append(result)
        if on_result is not None:
            on_result(deepcopy(result))
    return {'version': VERSION, **experiment_fields(experiment_version), 'rows': results, 'summary': summarize_direction(results),
            'supplemental': normalized['supplemental']}


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = fraction*(len(ordered)-1)
    lo, hi = math.floor(index), math.ceil(index)
    return ordered[lo]+(index-lo)*(ordered[hi]-ordered[lo])


def summarize_direction(rows):
    """Keep scheduled/exposed/reference/output and paired denominators separate."""
    keys = [(r['run_id'], r['number']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('M4 direction target identity repeated')
    eligible = [r for r in rows if r.get('eligible') is True]
    angles = [r['actual_error_deg'] for r in eligible if _finite(r.get('actual_error_deg'))]
    paired = [r['paired_improvement_deg'] for r in eligible if _finite(r.get('paired_improvement_deg'))]
    counts = {'scheduled': len(rows), 'eligible_informative': len(eligible),
              'exposed': sum(r.get('exposure_status') in ('observed', 'missing_anchor') for r in rows),
              'usable_output': len(angles), 'paired': len(paired),
              'usable_averaging': sum(r.get('usable_averaging') is True for r in eligible)}
    counts.update({name: sum(r.get(name) is True for r in rows)
                   for name in ('input_qualified', 'reference_qualified', 'informative')})
    counts['exposure_status'] = dict(Counter(r['exposure_status'] for r in rows))
    availability = counts['usable_averaging']/len(eligible) if eligible else None
    median, p90 = _percentile(angles, .5), _percentile(angles, .9)
    status = ('EVIDENCE_UNAVAILABLE' if median is None or availability is None else
              'PASS' if median <= 30. and p90 <= 60. and availability >= .8 else 'FAIL')
    return {'counts': counts, 'median_error_deg': median, 'p90_error_deg': p90,
            'averaging_availability': availability, 'status': status,
            'median_paired_improvement_deg': _percentile(paired, .5),
            'paired_improved': sum(v > 0 for v in paired), 'paired_degraded': sum(v < 0 for v in paired)}


def direction_product_complete(rows, run):
    """V10 completion is measured coverage, independent of angle/availability pass."""
    if len(rows) != 24:
        return False
    for number, row in enumerate(rows, 1):
        if (row.get('number') != number or row.get('offset_sec') != TARGET_OFFSETS_SEC[number-1]
                or any(row.get(key) != run.get(key) for key in ('run_id', 'arm', 'partition', 'condition'))
                or row.get('exposure_status') not in ('observed', 'unexposed', 'terminated')
                or any(type(row.get(key)) is not bool for key in (
                    'input_qualified', 'reference_qualified', 'informative', 'eligible',
                    'usable_output', 'usable_averaging'))):
            return False
        if row['input_qualified'] and not row['reference_qualified']:
            return False
        if row['eligible'] and not (row['input_qualified'] and row['reference_qualified'] and row['informative']):
            return False
    return True


def _heading(vector):
    if (not isinstance(vector, (list, tuple)) or len(vector) != 2
            or not all(_finite(v) for v in vector) or math.hypot(*vector) <= 1e-6):
        return None
    return math.atan2(vector[1], vector[0])


def _same_context(a, b):
    return (a.get('context_id') == b.get('context_id')
            and a.get('objective_id') == b.get('objective_id')
            and a.get('frame_id') == b.get('frame_id'))


def direction_supplemental(observations):
    """Finite whole-trace fallback and fixed-grid operational jitter/relative lag."""
    if len(observations) > MAX_OBSERVATIONS:
        raise ValueError('M4 supplemental input capacity exceeded')
    eligible_sec = fallback_sec = unknown_sec = 0.
    delays = []
    for row in observations:
        if type(row.get('filter_stamp_ns')) is int and type(row.get('stamp_ns')) is int:
            dt = (row['filter_stamp_ns']-row['stamp_ns'])/NS
            if dt >= 0:
                delays.append(dt)
    for a, b in zip(observations, observations[1:]):
        dt = (b['stamp_ns']-a['stamp_ns'])/NS
        if dt <= 0:
            raise ValueError('M4 supplemental source times must increase')
        if not (dt <= .5 and _same_context(a, b) and a.get('qualified') and b.get('qualified')):
            unknown_sec += dt
        elif a.get('blend_allowed') and b.get('blend_allowed'):
            eligible_sec += dt
            if a['method'].get('fallback_used') is True:
                fallback_sec += dt
    grid = []
    stamps = [r['stamp_ns'] for r in observations]
    if stamps:
        # No extrapolation; interpolation is used only for these supplemental
        # headings, never detector labels, reference phase or target selection.
        start = ((stamps[0]+100_000_000-1)//100_000_000)*100_000_000
        if (stamps[-1]-start)//100_000_000+1 > MAX_OBSERVATIONS:
            raise ValueError('M4 supplemental time grid exceeds finite capacity')
        for stamp in range(start, stamps[-1]+1, 100_000_000):
            at = bisect_left(stamps, stamp)
            if at == len(stamps):
                break
            a = observations[at] if stamps[at] == stamp else observations[max(0, at-1)]
            b = observations[at]
            item = {'stamp_ns': stamp, 'actual': None, 'instant': None, 'context': None}
            if (a['stamp_ns'] <= stamp <= b['stamp_ns'] and b['stamp_ns']-a['stamp_ns'] <= 500_000_000
                    and _same_context(a, b) and all(r.get('qualified') and r.get('blend_allowed') for r in (a, b))):
                item['context'] = (a.get('context_id'), a.get('objective_id'), a.get('frame_id'))
                fraction = ((stamp-a['stamp_ns'])/(b['stamp_ns']-a['stamp_ns'])
                            if b['stamp_ns'] != a['stamp_ns'] else 0.)
                for key, name in [('actual', 'v2_output_world'), ('instant', 'aligned_instant_world')]:
                    first, last = _heading(a['method'].get(name)), _heading(b['method'].get(name))
                    if first is not None and last is not None:
                        item[key] = first+fraction*math.remainder(last-first, math.tau)
            grid.append(item)
    jitter = []
    for at in range(0, len(grid)-9, 10):
        window = grid[at:at+10]
        if (all(r['actual'] is not None for r in window)
                and len({r['context'] for r in window}) == 1):
            mean = math.atan2(sum(math.sin(r['actual']) for r in window),
                              sum(math.cos(r['actual']) for r in window))
            jitter.append(math.degrees(math.sqrt(statistics.mean(
                math.remainder(r['actual']-mean, math.tau)**2 for r in window))))
    lag_rows = []
    for at in range(0, len(grid)-299, 300):
        window = grid[at:at+300]
        valid = [r for r in window if r['actual'] is not None and r['instant'] is not None]
        result = {'start_ns': window[0]['stamp_ns'], 'lag_sec': None, 'reason': 'incomplete_context_or_support'}
        if len(valid) >= 270 and len({r['context'] for r in valid}) == 1:
            base = valid[0]['instant']
            excursion = max(math.remainder(r['instant']-base, math.tau) for r in valid)-min(
                math.remainder(r['instant']-base, math.tau) for r in valid)
            result['excursion_deg'] = math.degrees(excursion)
            if excursion < math.radians(10.):
                result['reason'] = 'insufficient_excitation'
            else:
                # Every lag sees the same fixed central support; missing values
                # cannot give one candidate lag a more favorable denominator.
                centers = [j for j in range(60, 240) if window[j]['actual'] is not None
                           and all(window[j-shift]['instant'] is not None for shift in range(61))]
                if len(centers) >= 162:
                    scores = [statistics.mean(math.remainder(window[j]['actual']-
                        window[j-shift]['instant'], math.tau)**2 for j in centers) for shift in range(61)]
                    minimum = min(scores)
                    best = next(i for i, value in enumerate(scores)
                                if math.isclose(value, minimum, rel_tol=0., abs_tol=1e-12))
                    result.update(lag_sec=best*.1, reason=None, common_grid_count=len(centers),
                                  tied_minimum_count=sum(math.isclose(v, scores[best], rel_tol=0., abs_tol=1e-12) for v in scores))
        lag_rows.append(result)
    lags = [row['lag_sec'] for row in lag_rows if row['lag_sec'] is not None]
    interval_observed = len(observations) >= 2
    return {'status': 'OBSERVED' if eligible_sec > 0 else 'EVIDENCE_UNAVAILABLE',
            'reason': None if eligible_sec > 0 else 'no_eligible_same_context_source_interval',
            'observation_count': len(observations),
            'eligible_source_duration_sec': eligible_sec if interval_observed else None,
            'fallback_duration_sec': fallback_sec if eligible_sec > 0 else None,
            'unknown_gap_duration_sec': unknown_sec if interval_observed else None, 'publication_delay_median_sec': _percentile(delays, .5),
            'publication_delay_p90_sec': _percentile(delays, .9), 'publication_delay_count': len(delays),
            'heading_jitter_median_deg': _percentile(jitter, .5), 'heading_jitter_window_count': len(jitter),
            'relative_smoothing_lag_median_sec': _percentile(lags, .5), 'relative_lag_windows': lag_rows,
            'scope': 'operational circular heading dispersion and relative smoothing lag; intentional turns contribute; not ground-truth response time'}


def _observed_latency_endpoint(row):
    """The existing fixed-population endpoint rule, shared without relabeling."""
    endpoint = row.get('latency', {})
    return (row.get('integrity_passed') is True and endpoint.get('observed') is True
            and endpoint.get('independently_eligible') is True
            and _finite(endpoint.get('latency_sec')) and endpoint['latency_sec'] >= 0)


def development_latency_feasibility(run_rows, *, experiment_version):
    """V11 development observability only; first-opportunity labels stay frozen."""
    from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
    if experiment_version != V11_EXPERIMENT_VERSION:
        raise ValueError('development latency feasibility is selected only for M4 v11')
    reserved = expected_slots(experiment_version)[:4]
    if (len(run_rows) != 4 or any(
            any(row.get(key) != value for key, value in expected.items())
            or row.get('run_id') != experiment_run_id(expected, experiment_version)
            for row, expected in zip(run_rows, reserved))):
        raise ValueError('development latency feasibility requires exact nominal slots 1..4')
    pairs = []
    observed_endpoints = 0
    for control, enabled in ((run_rows[0], run_rows[1]), (run_rows[2], run_rows[3])):
        validity = [_observed_latency_endpoint(row) for row in (control, enabled)]
        observed_endpoints += sum(validity)
        pairs.append(dict(condition='nominal', control_arm=control['arm'], enabled_arm=enabled['arm'],
            observed_pair=all(validity), control=deepcopy(control.get('latency', {})),
            enabled=deepcopy(enabled.get('latency', {}))))
    missing = [pair['control_arm']+'/'+pair['enabled_arm'] for pair in pairs if not pair['observed_pair']]
    return dict(policy='nominal_first_opportunity_pairs_v1', feasible=not missing,
        status='EVIDENCE_UNAVAILABLE' if missing else 'PASS',
        reason=('unobserved independently eligible development pair: '+', '.join(missing)) if missing else None,
        planned_pair_count=2, observed_pair_count=sum(pair['observed_pair'] for pair in pairs),
        planned_endpoint_count=4, observed_endpoint_count=observed_endpoints, pairs=pairs)


def _integrated_population_summary(runs, direction_rows):
    """Describe every planned integrated run through existing direction/motion results."""
    projected = []
    for run in runs:
        valid = run.get('integrity_passed') is True
        passed = run.get('arrival_passed')
        measured = (valid and run.get('arrival_measurement_complete') is True
                    and type(passed) is bool and (not passed or
                        (_finite(run.get('time_to_arrival_sec')) and run['time_to_arrival_sec'] >= 0)))
        arrival_status = ('EVIDENCE_UNAVAILABLE' if not measured else
                          'OBSERVED_ARRIVAL' if passed else 'OBSERVED_NONARRIVAL')
        components = run.get('combined_sequence_components', {})
        def flag(value):
            return value if valid and type(value) is bool else None
        motion = run.get('mandatory_stop_evidence') or {}
        acquisition = ('NOT_APPLICABLE' if run['arm'] not in ('C', 'D') else
                       motion.get('status', 'EVIDENCE_UNAVAILABLE')
                       if valid and motion.get('analysis_complete') is True else 'EVIDENCE_UNAVAILABLE')
        projected.append(dict(slot=run['slot'], arm=run['arm'], condition=run['condition'],
            arrival_status=arrival_status,
            time_to_arrival_sec=run.get('time_to_arrival_sec') if arrival_status == 'OBSERVED_ARRIVAL' else None,
            local_recovery_passed=flag(components.get('local_recovery_stage_passed')),
            combined_sequence_passed=flag(run.get('combined_sequence_passed')),
            first_verification_path_passed=flag(components.get('required_state_path_passed')),
            acquisition_status=acquisition,
            scientific_analysis_complete=valid and run.get('scientific_analysis_complete') is True))

    def summary(selected):
        selected_slots = {row['slot'] for row in selected}
        targets = [row for row in direction_rows if row['slot'] in selected_slots]
        moving = [run for run in runs if run['slot'] in selected_slots and run['arm'] in ('C', 'D')]
        direction = summarize_direction(targets)
        if not moving:
            direction['status'] = 'NOT_APPLICABLE'
        elif any(run.get('integrity_passed') is not True or
                 run.get('direction_analysis_complete') is not True or
                 not direction_product_complete([row for row in targets if row['slot'] == run['slot']], run)
                 for run in moving):
            direction['status'] = 'EVIDENCE_UNAVAILABLE'
        def outcomes(key):
            return dict(passed=sum(row[key] is True for row in selected),
                        failed=sum(row[key] is False for row in selected),
                        unavailable=sum(row[key] is None for row in selected))
        return dict(planned_run_count=len(selected),
            scientific_complete_run_count=sum(row['scientific_analysis_complete'] for row in selected),
            arrival_counts=dict(observed_arrival=sum(row['arrival_status'] == 'OBSERVED_ARRIVAL' for row in selected),
                observed_nonarrival=sum(row['arrival_status'] == 'OBSERVED_NONARRIVAL' for row in selected),
                unavailable=sum(row['arrival_status'] == 'EVIDENCE_UNAVAILABLE' for row in selected)),
            local_recovery_counts=outcomes('local_recovery_passed'),
            combined_recovery_counts=outcomes('combined_sequence_passed'),
            acquisition_status_counts=dict(Counter(row['acquisition_status'] for row in selected
                                                  if row['arm'] in ('C', 'D'))),
            direction=direction)

    return dict(summary(projected), runs=projected,
                by_arm=[dict(arm=arm, **summary([row for row in projected if row['arm'] == arm]))
                        for arm in ARMS])


def integrated_method_run_checks(run, *, direction_rows=None):
    """V13's D package needs measured arrival, recovery, motion and direction.

    A complete negative result remains FAIL. Missing measurements remain
    unavailable, and another arm or condition cannot replace this run's evidence.
    """
    if run.get('arm') != 'D':
        raise ValueError('integrated method checks require the explicit D arm')
    known = (run.get('integrity_passed') is True
             and run.get('scientific_analysis_complete') is True)
    arrival = run.get('arrival_passed')
    arrival_known = (known and run.get('arrival_measurement_complete') is True
        and run.get('arrival_binding_method') == RECORDED_ARRIVAL_BINDING
        and type(arrival) is bool and (not arrival or
            (_finite(run.get('time_to_arrival_sec')) and run['time_to_arrival_sec'] >= 0)))
    recovery = run.get('combined_sequence_passed')
    motion = run.get('mandatory_stop_evidence') or {}
    stopped = run.get('mandatory_stopped_acquisitions')
    motion_known = (known and all(motion.get(key) is True for key in
        ('analysis_complete', 'command_pairing_complete', 'authority_complete'))
        and motion.get('status') in ('NO_ACQUISITION_OBSERVED', 'OBSERVED_STATIONARY_INTERVAL',
            'OBSERVED_ZERO_COMMAND_INTERVAL', 'OBSERVED_CONTINUOUS_VERIFY_ONLY',
            'OBSERVED_CONTINUOUS_ACQUISITION')
        and (motion['status'] != 'OBSERVED_CONTINUOUS_ACQUISITION'
             or type(stopped) is int and stopped >= 0))
    continuous = (motion.get('status') == 'OBSERVED_CONTINUOUS_ACQUISITION'
                  and type(stopped) is int and stopped == 0)
    rows = (run.get('direction_rows') or []) if direction_rows is None else direction_rows
    direction = summarize_direction(rows)
    direction_complete = (known and run.get('direction_analysis_complete') is True
                          and direction_product_complete(rows, run))
    if not direction_complete:
        direction['status'] = 'EVIDENCE_UNAVAILABLE'
    checks = dict(arrival_passed=arrival if arrival_known else None,
        combined_recovery_passed=recovery if known and type(recovery) is bool else None,
        continuous_acquisition_passed=continuous if motion_known else None,
        direction_passed=(None if direction['status'] == 'EVIDENCE_UNAVAILABLE'
                          else direction['status'] == 'PASS'))
    status = ('EVIDENCE_UNAVAILABLE' if any(value is None for value in checks.values())
              else 'PASS' if all(checks.values()) else 'FAIL')
    return dict(slot=run['slot'], arm='D', condition=run['condition'], **checks,
        direction_measurement_complete=bool(direction_complete), direction_summary=direction,
        status=status)


def aggregate_pilot(run_rows, *, experiment_version=VERSION):
    """Summarize the fixed16 slots with all missing endpoints left explicit.

    V14's first four reserved descriptors retain their original V13 identities.
    The workflow authenticates reuse receipts; this owner only validates the
    fixed source-slot mapping and preserves the recorded measurement fields.
    """
    fields = experiment_fields(experiment_version)
    from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
    reserved = expected_slots(experiment_version)
    indexed = {}
    for row in run_rows:
        slot = row.get('slot')
        if type(slot) is not int or not 1 <= slot <= 16 or slot in indexed:
            raise ValueError('M4 slot is outside the fixed population or repeated')
        block, arm = (slot-1)//4, ARMS[(slot-1)%4]
        partition = 'development' if block == 0 else 'holdout'
        condition = 'nominal' if block <= 1 else CONDITIONS[block-1]
        if (row.get('arm') != arm or row.get('partition') != partition
                or row.get('condition') != condition or row.get('block', block) != block):
            raise ValueError('M4 slot identity/arm/condition changed')
        if experiment_version != VERSION:
            expected = reserved[slot-1]
            if (any(row.get(key) != value for key, value in expected.items())
                    or row.get('run_id') != experiment_run_id(expected, experiment_version)):
                raise ValueError('M4 aggregate row belongs to a different experiment')
        elif row.get('experiment_version', VERSION) != VERSION:
            raise ValueError('M4 aggregate row belongs to a different experiment')
        indexed[slot] = deepcopy(row)
    slots = [indexed.get(slot, {'slot': slot, 'arm': ARMS[(slot-1)%4],
                'partition': 'development' if slot <= 4 else 'holdout',
                'condition': 'nominal' if slot <= 8 else 'noise' if slot <= 12 else 'delay',
                'status': 'UNSTARTED', 'integrity_passed': False}) for slot in range(1, 17)]
    if experiment_version != VERSION:
        slots = [indexed.get(row['slot'], {**row, 'run_id': experiment_run_id(row, experiment_version),
                 'status': 'UNSTARTED', 'integrity_passed': False}) for row in reserved]
    pairs, controls, enabled = [], [], []
    observed_endpoints = 0
    error_known, no_extra_errors = True, True
    for block in range(1, 4):
        for control_arm, enabled_arm in [('A', 'B'), ('C', 'D')]:
            a, b = slots[block*4+ARMS.index(control_arm)], slots[block*4+ARMS.index(enabled_arm)]
            first, second = a.get('latency', {}), b.get('latency', {})
            endpoint_validity = [_observed_latency_endpoint(row) for row in (a, b)]
            observed_endpoints += sum(endpoint_validity)
            valid = all(endpoint_validity)
            pairs.append({'condition': CONDITIONS[block-1], 'control_arm': control_arm,
                          'enabled_arm': enabled_arm, 'observed_pair': valid,
                          'control': first, 'enabled': second})
            if valid:
                controls.append(first['latency_sec']); enabled.append(second['latency_sec'])
            for name in ('wrong_fills', 'wrong_goals'):
                va, vb = a.get(name), b.get(name)
                known = all(type(v) is int and v >= 0 for v in (va, vb))
                error_known &= known
                if known and vb > va:
                    no_extra_errors = False
    control_median, enabled_median = _percentile(controls, .5), _percentile(enabled, .5)
    improvement = (1-enabled_median/control_median if control_median is not None and control_median > 0 else None)
    primary_status = ('EVIDENCE_UNAVAILABLE' if len(controls) != 6 or not error_known or improvement is None
                      else 'PASS' if improvement >= .30 and no_extra_errors else 'FAIL')
    direction_rows, direction_complete = [], True
    for run in slots:
        if run['arm'] not in ('C', 'D'):
            if run.get('direction_rows'):
                raise ValueError('stationary arm cannot acquire M4 moving direction targets')
            continue
        present = {}
        for row in run.get('direction_rows', []):
            number = row.get('number')
            if (type(number) is not int or not 1 <= number <= 24 or number in present
                    or row.get('offset_sec') != TARGET_OFFSETS_SEC[number-1]
                    or any(row.get(name) != run[name] for name in ('arm', 'partition', 'condition'))
                    or ('run_id' in run and row.get('run_id') != run['run_id'])):
                raise ValueError('direction row differs from frozen run/target identity')
            present[number] = row
        if run['partition'] == 'holdout' and (
                len(present) != 24 or run.get('direction_analysis_complete') is not True
                or any(r.get('exposure_status') == 'analysis_unavailable' for r in present.values())):
            direction_complete = False
        for number, offset in enumerate(TARGET_OFFSETS_SEC, 1):
            direction_rows.append({**present.get(number, {
                'run_id': run.get('run_id', 'unstarted_slot_' + str(run['slot'])),
                'arm': run['arm'], 'partition': run['partition'], 'condition': run['condition'],
                'number': number, 'offset_sec': offset, 'target_ns': None,
                'exposure_status': 'analysis_unavailable', 'eligible': False}), 'slot': run['slot']})
    holdout = [r for r in direction_rows if r.get('partition') == 'holdout']
    direction = summarize_direction(holdout)
    if (not direction_complete or any(run.get('integrity_passed') is not True for run in slots[4:]
                                 if run['arm'] in ('C', 'D'))):
        direction['status'] = 'EVIDENCE_UNAVAILABLE'
    direction_groups = []
    for run in slots:
        if run['arm'] not in ('C', 'D'):
            continue
        group_rows = [row for row in direction_rows if row['arm'] == run['arm']
                      and row['partition'] == run['partition'] and row['condition'] == run['condition']]
        summary = summarize_direction(group_rows)
        if (run.get('direction_analysis_complete') is not True or run.get('integrity_passed') is not True
                or any(row['exposure_status'] == 'analysis_unavailable' for row in group_rows)):
            summary['status'] = 'EVIDENCE_UNAVAILABLE'
        direction_groups.append({**{name: run[name] for name in ('slot', 'arm', 'partition', 'condition')},
                                 'summary': summary})
    sequence = [{'condition': run['condition'], 'slot': run['slot'],
                 'passed': run.get('combined_sequence_passed') if run.get('integrity_passed') is True else None}
                for run in slots[4:] if run['arm'] == 'D']
    sequence_status = ('EVIDENCE_UNAVAILABLE' if any(r['passed'] is None for r in sequence)
                       else 'PASS' if all(r['passed'] is True for r in sequence) else 'FAIL')
    mandatory = [run.get('mandatory_stopped_acquisitions') for run in slots if run['arm'] in ('C', 'D')]
    stop_status = ('EVIDENCE_UNAVAILABLE' if any(type(v) is not int or v < 0 for v in mandatory)
                   else 'PASS' if sum(mandatory) == 0 else 'FAIL')
    result = {'version': VERSION, **fields, 'slots': slots, 'slot_status_counts': dict(Counter(r.get('status', 'UNKNOWN') for r in slots)),
            'latency': {'status': primary_status, 'planned_pair_count': 6, 'observed_pair_count': len(controls),
                        'planned_endpoint_count': 12, 'observed_endpoint_count': observed_endpoints,
                        'control_median_sec': control_median, 'enabled_median_sec': enabled_median,
                        'descriptive_fraction_reduction': improvement, 'error_attribution_complete': error_known,
                        'no_additional_errors': no_extra_errors if error_known else None, 'pairs': pairs},
            'direction': direction, 'direction_scheduled_total': len(direction_rows),
            'direction_by_condition_arm': direction_groups, 'direction_rows': direction_rows,
            'combined_sequence': {'status': sequence_status, 'conditions': sequence},
            'mandatory_stopped_acquisition': {'status': stop_status, 'counts': mandatory},
            'claim': 'selected_condition_pilot_evidence_not_broad_robustness'}
    if is_arrival_experiment_version(experiment_version):
        result['arrival'] = {'criterion': 'post_recovery_arrival_v1',
            'runs': [{key: run.get(key) for key in ('slot', 'arm', 'partition', 'condition',
                'arrival_passed', 'arrival_measurement_complete', 'time_to_arrival_sec',
                'arrival_ros_stamp_ns', 'arrival_distance_m', 'optional_controller_goal')}
                for run in slots],
            'measured_run_count': sum(run.get('arrival_measurement_complete') is True for run in slots),
            'arrival_count': sum(run.get('arrival_passed') is True for run in slots)}
        result['scientific_analysis'] = {
            'complete_run_count': sum(run.get('scientific_analysis_complete') is True for run in slots),
            'scope': 'Behavioral failure/censoring and no candidate can be valid analysis; untouched confirmation slots stay unstarted.'}
    if is_integrated_arrival_experiment_version(experiment_version):
        result.update(scientific_scope='integrated_arrival_direction_v1',
            secondary_endpoint='independent_basin_entry_latency',
            primary_outcomes=dict(
                development=_integrated_population_summary(slots[:4],
                    [row for row in direction_rows if row['partition'] == 'development']),
                confirmation=_integrated_population_summary(slots[4:], holdout)))
    if experiment_version == V13_EXPERIMENT_VERSION or is_retained_development_experiment_version(experiment_version):
        conditions = [integrated_method_run_checks(run,
            direction_rows=[row for row in direction_rows if row['slot'] == run['slot']])
            for run in slots[4:] if run['arm'] == 'D']
        statuses = [row['status'] for row in conditions]
        result['combined_method_confirmation'] = dict(planned_condition_count=3, conditions=conditions,
            status=('EVIDENCE_UNAVAILABLE' if 'EVIDENCE_UNAVAILABLE' in statuses
                    else 'PASS' if all(value == 'PASS' for value in statuses) else 'FAIL'))
    if is_retained_development_experiment_version(experiment_version):
        result['acquisition_population'] = {
            name: dict(planned_slots=[row['slot'] for row in selected],
                source_experiment_version=source_version,
                source_run_ids=[row['run_id'] for row in selected],
                complete_acquisition_count=sum(row.get('status') == 'COMPLETE'
                    and row.get('integrity_passed') is True for row in selected))
            for name, selected, source_version in (
                ('retained_development', slots[:4], V13_EXPERIMENT_VERSION),
                ('fresh_confirmation', slots[4:], experiment_version))}
        result['acquisition_population']['scope'] = (
            'Fixed source identities only; immutable reuse receipts are authenticated by the workflow. '
            'Four exposed V13 development acquisitions and twelve fresh V14 confirmation slots; '
            'no development executions or scientific observations are duplicated.')
    return result
