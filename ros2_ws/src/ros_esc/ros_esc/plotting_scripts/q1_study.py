"""Subordinate Q1 label freeze and finite detector/neighborhood comparison.

Uses the existing bag, label, centroid and moving-evidence owners. Source-time
replay demonstrates recorded evidence availability, not hypothetical DDS timing
or a trajectory after intervention. No CLI, model integration or run dispatcher.
"""

from collections import Counter
import ast
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from . import gesc_gaussian_bag_analysis as analysis
from .v2_enclosure import atomic_exclusive_json
from ros_esc.v2_stream import TOPIC_KEYS, time_to_ns


DETECTOR_CONTRACT = {
    'window_seconds': 6, 'epsilon_m': .30,
    'radius_grid_m': [.25, .50, .75],
    'candidate_epsilon_grid_m': [.05, .10, .15],
    'positive_support_sec': 42, 'verification_sec': 12,
    'label_job_timeout_sec': 600,
}
MAX_INPUTS_PER_RUN = 20000
NS = 1_000_000_000
FRESH_NS = 500_000_000
CLAIM = 'source_time_replay_with_first_recorded_publication_availability'


def _hash(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _read(reference):
    analysis._q1_verify_files([reference])
    return json.loads(Path(reference['path']).read_text())


def _check_contract(contract):
    analysis.qualification_partition_seeds(contract.get('version'))
    if contract.get('detector') != DETECTOR_CONTRACT:
        raise ValueError('Q1 detector/label contract differs from the frozen finite study')


def verify_q1_geometry(contract, resolved_scenario=None, *, runs=()):
    """Recheck original numerical identity and current selected inputs, without fields."""
    _check_contract(contract)
    return verify_geometry_receipts(contract, resolved_scenario, runs=runs)


def verify_geometry_receipts(contract, resolved_scenario=None, *, runs=()):
    """Share immutable numerical receipt checks without adopting a study contract."""
    geometry = _read(contract['label_geometry'])
    recovered = _read(contract['geometry_recovery'])
    reuse = recovered['numerical_geometry_recovery']
    analysis._v2_verify_recovery_freshness(reuse)

    def task_body(path):
        source = Path(path).read_text()
        nodes = [node for node in ast.parse(source).body
                 if isinstance(node, ast.FunctionDef) and node.name == '_v2_enclosure_geometry_task']
        if len(nodes) != 1:
            raise ValueError('Q1 geometry task has no unique original/current owner')
        return ast.get_source_segment(source, nodes[0])

    original = task_body(reuse['original_analyzer_snapshot_path'])
    if (original != task_body(analysis.__file__)
            or hashlib.sha256(original.encode()).hexdigest() != reuse['unchanged_geometry_task_sha256']):
        raise ValueError('Q1 original numerical geometry task changed')
    for owner in reuse['original_numerical_owners']:
        if Path(owner['path']).resolve() == Path(analysis.__file__).resolve():
            if owner['sha256'] != reuse['original_analyzer_sha256']:
                raise ValueError('Q1 original analyzer ownership mismatch')
        else:
            analysis._q1_verify_files([owner])
    matches = [json.loads(key) for key, receipt in reuse['group_receipts'].items()
               if Path(receipt['path']).resolve() == Path(contract['label_geometry']['path']).resolve()
               and receipt['sha256'] == contract['label_geometry']['sha256']]
    if len(matches) != 1:
        raise ValueError('Q1 selected geometry is absent from the verified original recovery')
    sources, bounds, model_hash, recorded_geometry = matches[0]
    provenance = geometry.get('provenance', {})
    if (geometry.get('method') != 'operational_enclosure_v1'
            or not geometry.get('basins') or not all(b['qualified'] for b in geometry['basins'])
            or [b['source_id'] for b in geometry['basins']] != [s['id'] for s in sources]
            or provenance.get('model_config_sha256') != model_hash
            or provenance.get('recorded_geometry_provenance') != recorded_geometry
            or provenance.get('owners') != reuse['original_numerical_owners']):
        raise ValueError('Q1 geometry/source/provenance differs from its original group')
    bound_points = {str(Path(r['path']).resolve()): r['sha256'] for r in contract['geometry_receipts']}
    for basin in geometry['basins']:
        if not basin.get('point_receipts'):
            raise ValueError('Q1 geometry has no retained numerical point receipts')
        for point in basin['point_receipts']:
            if bound_points.get(str(Path(point['path']).resolve())) != point['sha256']:
                raise ValueError('Q1 geometry point omitted from frozen receipt population')
    current_sources = {str(Path(r['path']).resolve()): r['sha256'] for r in contract['source_files']}
    for item in recorded_geometry:
        if current_sources.get(str(Path(item['path']).resolve())) != item['recorded_sha256']:
            raise ValueError('Q1 current sensor/URDF no longer matches the numerical geometry')
        analysis._q1_verify_files([{'path': item['path'], 'sha256': item['recorded_sha256']}])
    model_reference = {'path': provenance['model_config_path'], 'sha256': model_hash}
    analysis._q1_verify_files([model_reference])
    if current_sources.get(str(Path(model_reference['path']).resolve())) != model_hash:
        raise ValueError('Q1 geometry model is not bound by the frozen source receipt set')
    if resolved_scenario is not None and (
            resolved_scenario['sources'] != sources or resolved_scenario['bounds_m'] != bounds):
        raise ValueError('Q1 planned source/bounds inputs differ from frozen masks')
    for run in runs:
        scenario = analysis.load_yaml(Path(run['run_directory']) / 'resolved_scenario.yaml')
        selected = run['binding']['selected_configurations']
        if (scenario['sources'] != sources or scenario['bounds_m'] != bounds
                or run['model_configuration']['sha256'] != model_hash
                or selected['cost_function_config_filepath'] != run['model_configuration']):
            raise ValueError('Q1 selected source/bounds/model inputs differ from frozen masks')
        sensor = selected['sensor_transform_config_filepath']
        if not any(Path(r['path']).resolve() == Path(sensor['path']).resolve()
                   and r['recorded_sha256'] == sensor['sha256'] for r in recorded_geometry):
            raise ValueError('Q1 selected sensor transform differs from frozen masks')
    return geometry


def _selected_pose_samples(bag, topic, frame, *, maximum_samples=MAX_INPUTS_PER_RUN):
    """Retain actual source knots and invalidations; never resample observation XY."""
    samples, seen, errors = [], {}, Counter()
    frontier = None
    records = bag.records_by_topic.get(topic, [])
    if type(maximum_samples) is not int or maximum_samples <= 0:
        raise ValueError('selected pose capacity must be a positive integer')
    if len(records) > maximum_samples:
        raise ValueError('Q1 selected pose input capacity exceeded')
    for index, record in enumerate(records):
        stamp, xy, source_frame = None, None, ''
        reasons = []
        try:
            stamp = time_to_ns(record.message.header.stamp)
            source_frame = record.message.header.frame_id
            xy = [float(record.message.pose.pose.position.x), float(record.message.pose.pose.position.y)]
            if source_frame != frame or not all(math.isfinite(value) for value in xy):
                raise ValueError('nonfinite or differently framed pose')
            signature = (source_frame, *xy)
            if stamp in seen:
                if seen[stamp] == signature:
                    errors['identical_pose_repeat'] += 1
                    continue  # Preserve the first receipt; no extra numerical knot.
                seen[stamp] = None
                raise ValueError('conflicting_pose_timestamp')
            if frontier is not None and stamp < frontier:
                raise ValueError('regressing_pose_timestamp')
            seen[stamp] = signature
            frontier = stamp
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            reasons.append(str(exc))
            errors[str(exc)] += 1
        samples.append({
            'stamp_ns': stamp, 'bag_timestamp_ns': record.bag_timestamp_ns,
            'xy': xy if xy is not None and all(math.isfinite(v) for v in xy) else None,
            'frame_id': source_frame, 'qualified': not reasons,
            'readiness_eligible': bool(record.in_readiness_interval),
            'pose_record_index': index, 'invalid_reasons': reasons,
        })
    return samples, dict(errors)


def prepare_q1_study_run(bag_data, metadata, *, contract, run_spec, geometry):
    """Prepare one authorized in-memory run; freeze spatial truth before masks."""
    _check_contract(contract)
    if contract['version'] in analysis.Q2_VERSIONS:
        rows, qualification = analysis.prepare_moving_policy_direction_inputs(
            bag_data, metadata, run_spec=run_spec)
        if qualification['integrity_errors']:
            raise ValueError('Q2 typed input integrity errors prohibit scientific fallback')
    else:
        rows, qualification = analysis.prepare_q1_direction_inputs(
            bag_data, metadata, contract=contract, run_spec=run_spec)
    if len(rows) > MAX_INPUTS_PER_RUN:
        raise ValueError('Q1 typed input capacity exceeded')
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    poses, pose_faults = _selected_pose_samples(bag_data, config['pose_topic'], config['frame_id'])
    # Whole-run typed ambiguity excludes all scientific evaluation, including
    # labels; empty input is unavailable rather than an empty-denominator pass.
    usable = bool(qualification['qualified'] and not qualification['integrity_errors'])
    labels = analysis.label_v2_basin_intervals(poses, geometry) if usable else []
    spatial_hash = _hash(labels)
    # This fresh admission owner preserves every actual source knot. Its receipt
    # projection is explicitly a bag-observation proxy, never a DDS receipt claim.
    masked = analysis.q1_pose_search_eligibility(poses, bag_data) if usable else []
    raw_masked = analysis.q1_pose_search_eligibility(rows, bag_data) if usable else []
    supported, censored = analysis._v2_common_positive_support(
        masked, labels, minimum_duration_sec=42)
    return {
        'version': contract['version'], 'run': deepcopy(run_spec),
        'contract_canonical_sha256': _hash(contract),
        'geometry_canonical_sha256': _hash(geometry),
        'qualification': qualification, 'pose_faults': pose_faults,
        'pose_source': 'actual_selected_odometry_header_and_xy',
        'pose_topic': config['pose_topic'], 'poses': masked,
        'observations': raw_masked, 'labels': labels,
        'spatial_labels_sha256': spatial_hash,
        'supported_positives': supported, 'censored_positives': censored,
        'spatial_labels_precede_eligibility_mask': True,
        'detector_evaluated_for_labeling': False,
        'claim': CLAIM,
    }


def freeze_q1_study_labels(study_manifest_path, output_directory, *, partition,
                           nomination_manifest=None):
    """Verify selected inputs and write immutable labels before detector import."""
    manifest_path = Path(study_manifest_path).resolve()
    manifest_ref = {'path': str(manifest_path), 'sha256': analysis._v2_file_hash(manifest_path)}
    manifest = _read(manifest_ref)
    contract_ref = manifest['contract']
    contract = analysis._q1_contract(contract_ref)
    _check_contract(contract)
    partition_seeds = analysis.qualification_partition_seeds(contract['version'])
    if manifest.get('version') != contract['version'] or partition not in partition_seeds:
        raise ValueError('Q1 manifest version or partition invalid')
    runs = manifest['runs']
    if (len(runs) != 4 or len({run['run_id'] for run in runs}) != 4
            or any(sorted(run['seed'] for run in runs if run['partition'] == name) != list(seeds)
                   for name, seeds in partition_seeds.items())):
        raise ValueError('Q1 fixed four-run population changed')
    if partition == 'confirmation':
        if contract['version'] in analysis.Q2_VERSIONS:
            analysis._q2_evaluation_receipt(
                nomination_manifest, contract_ref['sha256'], 'discovery', manifest_ref,
                version=contract['version'])
        analysis._q1_nomination(nomination_manifest, contract_ref['sha256'])
    elif nomination_manifest is not None:
        raise ValueError('Q1 discovery cannot consume confirmation/nomination inputs')
    selected = sorted((r for r in runs if r['partition'] == partition), key=lambda r: r['seed'])
    if [r.get('exposure') for r in selected] != ['residence', 'approach']:
        raise ValueError('Q1 exposure assignment changed')
    for run in selected:
        analysis._q1_verify_run(run, contract)
    geometry = verify_q1_geometry(contract, runs=selected)
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    common = {'version': contract['version'], 'partition': partition,
              'contract': contract_ref, 'study_manifest': manifest_ref,
              'nomination': nomination_manifest, 'claim': CLAIM}
    atomic_exclusive_json(output / 'started.json', {**common, 'status': 'INCOMPLETE'})
    receipts = []
    for run in selected:
        directory = Path(run['run_directory'])
        metadata = analysis.load_yaml(directory / 'metadata.yaml')
        resolved = analysis.load_yaml(directory / 'resolved_topics.yaml')
        config = metadata['scenario_runner']['v2_identity']['stream_config']
        topics = {entry['topic']: entry['alias'] for entry in resolved['topics']}
        aliases = {topics[config[key]] for key in TOPIC_KEYS} | {
            'v2_direction_diagnostics', 'algorithm_state', 'clock'}
        if contract['version'] in analysis.Q2_VERSIONS:
            aliases.add('v2_direction_policy_diagnostics')
        # Existing reader adds recording_ready; retain all strict typed joins
        # while omitting unrelated PDE arrays and visualization streams.
        bag = analysis.read_run_bag(directory, aliases=aliases)
        prepared = prepare_q1_study_run(bag, metadata, contract=contract, run_spec=run, geometry=geometry)
        path = output / f'labels_{run["seed"]}.json'
        digest = atomic_exclusive_json(path, prepared)
        receipts.append({'path': str(path), 'sha256': digest, 'run': run})
    analysis._q1_contract(contract_ref)
    for run in selected:
        analysis._q1_verify_run(run, contract)
    _read(manifest_ref)
    result = {**common, 'status': 'FROZEN', 'runs': receipts,
              'detector_evaluated_for_labeling': False}
    atomic_exclusive_json(output / 'labels_manifest.json', result)
    return result


def _detector_events(prepared, radius):
    # Import after the verified frozen label manifest is read by the public owner.
    from ros_esc.convergence_detector_node.centroid_windows import CentroidConfig, CentroidWindowDetector
    core = CentroidWindowDetector(CentroidConfig(6., .30, radius, .5))
    events, previous_generation = [], None
    for index, pose in enumerate(prepared['poses']):
        epoch = pose.get('search_epoch')
        if not pose['qualified'] or epoch is None:
            core.invalidate('q1_pose_or_search_unavailable')
            previous_generation = None
            continue
        core.start_epoch(str(epoch))
        generation = pose.get('history_generation', 0)
        if previous_generation is not None and previous_generation != generation:
            core.invalidate('q1_recorded_admission_gap')
        previous_generation = generation
        for result in core.update(pose['stamp_ns'], pose['xy'], pose['frame_id']):
            if result.confirmed_event:
                events.append({
                    'stamp_ns': pose['stamp_ns'], 'window_end_ns': result.end_ns,
                    'history_start_ns': result.start_ns,
                    'last_pose_source_ns': pose['stamp_ns'],
                    'last_pose_bag_receipt_ns': pose['bag_timestamp_ns'],
                    'accepted_time_proxy_ns': pose['stamp_ns'],
                    'deadline_ns': pose['stamp_ns'] + 12 * NS,
                    'search_epoch': epoch, 'search_epoch_start_ns': pose['search_epoch_start_ns'],
                    'history_generation': generation, 'pose_index': index,
                    'center_xy': list(result.mean_xy), 'score_m': result.score_m,
                    'support_radius_m': result.radius_m,
                    'sample_count': result.sample_count,
                    'actual_detector_publication_reconstructed': False,
                })
    return analysis.classify_v2_detector_events(events, prepared['labels'])


def _evidence_receipt(result):
    summary = asdict(result.summary) if result.summary is not None else None
    return {'reason': result.reason, 'informative': result.informative,
            'amplitude': result.amplitude, 'disagreement': result.disagreement,
            'information_floor': result.information_floor, 'summary': summary,
            'cycle_bounds_ns': [[c.start_ns, c.end_ns] for c in result.cycles],
            'cycle_centroids': [list(c.centroid) for c in result.cycles],
            'observation_ids': [int(r.observation.observation_id) for r in result.records],
            'source_sequences': [int(r.observation.source_sequence) for r in result.records],
            'first_publication_bounds_ns': ([min(r.filter_stamp_ns for r in result.records),
                                           max(r.filter_stamp_ns for r in result.records)]
                                          if result.records else None)}


def _verify_event(prepared, event, radius, epsilon):
    """Latest-three evidence with measured departure priority and no revival."""
    from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence
    core = MovingRawEvidence()
    epoch, start = event['search_epoch'], event['search_epoch_start_ns']
    core.start_epoch(epoch, start)
    center, confirmation, deadline = event['center_xy'], event['stamp_ns'], event['deadline_ns']
    poses = prepared['poses']
    current_pose = poses[event['pose_index']]
    rows = prepared['observations']
    raw_at, pose_at = 0, event['pose_index'] + 1
    last_row, last_result, raw_generation = None, None, None
    evaluations, now = 0, confirmation

    def finish(status, reason, at=None):
        return {'status': status, 'reason': reason, 'evaluation_ns': at,
                'accepted_time_proxy_ns': confirmation, 'deadline_ns': deadline,
                'evaluation_count': evaluations,
                'qualified_cycle_count': sum(c.qualified for c in core.cycles),
                'evidence': _evidence_receipt(last_result) if last_result is not None else None,
                'claim': CLAIM, 'actual_subscriber_acceptance_reconstructed': False}

    def departure(pose):
        if (not pose['qualified'] or pose.get('search_epoch') != epoch
                or pose.get('history_generation', 0) != event['history_generation']):
            return 'pose_or_search_support_lost'
        if math.dist(pose['xy'], center) > radius:
            return 'candidate_departure'
        return None

    def add(row):
        nonlocal last_row, raw_generation
        if (not row['qualified'] or row.get('search_epoch') != epoch
                or not row['filter_state_valid'] or row['filter_state'] not in (1, 2, 3, 4, 5)):
            core.reset('q1_raw_unavailable')
            last_row = None
            return
        generation = row.get('history_generation', 0)
        if raw_generation is not None and generation != raw_generation:
            core.reset('q1_raw_state_admission_gap')
        raw_generation = generation
        # Deliberately ignore augmented-objective context_id/confidence resets.
        if core.add(analysis.q1_observation_from_row(row), row['filter_state'], row['filter_stamp_ns']):
            last_row = row

    reason = departure(current_pose)
    if reason:
        return finish('FAIL' if reason == 'candidate_departure' else 'EVIDENCE_UNAVAILABLE', reason, now)
    while raw_at < len(rows) and rows[raw_at]['filter_stamp_ns'] <= confirmation:
        if rows[raw_at]['stamp_ns'] >= start:
            add(rows[raw_at])
        raw_at += 1
    while True:
        if (last_row is not None and 0 <= now - last_row['stamp_ns'] <= FRESH_NS
                and 0 <= now - last_row['filter_stamp_ns'] <= FRESH_NS
                and 0 <= now - current_pose['stamp_ns'] <= FRESH_NS):
            evaluations += 1
            last_result = core.evaluate(center, radius, epsilon, confirmation)
            if last_result.ready:
                return finish('PASS', 'informative_latest_three_cycles', now)
        next_pose = poses[pose_at] if pose_at < len(poses) else None
        next_raw = rows[raw_at] if raw_at < len(rows) else None
        if next_pose is not None and next_pose['stamp_ns'] is None:
            return finish('EVIDENCE_UNAVAILABLE', 'unplaceable_invalid_pose_after_confirmation')
        pose_time = next_pose['stamp_ns'] if next_pose is not None else math.inf
        raw_time = next_raw['filter_stamp_ns'] if next_raw is not None else math.inf
        if min(pose_time, raw_time) > deadline:
            break
        if pose_time <= raw_time:  # Measured departure wins ties before acceptance.
            current_pose, pose_at, now = next_pose, pose_at + 1, max(now, pose_time)
            reason = departure(current_pose)
            if reason:
                return finish('FAIL' if reason == 'candidate_departure' else 'EVIDENCE_UNAVAILABLE', reason, now)
        else:
            now = max(now, raw_time)
            add(next_raw)
            raw_at += 1
    if current_pose['stamp_ns'] < deadline - FRESH_NS or last_row is None or last_row['stamp_ns'] < deadline - FRESH_NS:
        return finish('EVIDENCE_UNAVAILABLE', 'verification_input_right_censored', deadline)
    if sum(c.qualified for c in core.cycles) < 3:
        return finish('EVIDENCE_UNAVAILABLE', 'insufficient_measured_revolutions_by_deadline', deadline)
    return finish('FAIL', last_result.reason if last_result is not None else 'no_fresh_evidence_at_deadline', deadline)


def _eligible_negative_support(poses, labels):
    """Separate six-second detector exposure from unchanged spatial negatives."""
    spans, chain = [], []
    for pose in [*poses, None]:
        usable = pose is not None and pose['qualified'] and pose.get('search_epoch') is not None
        continuous = usable and (not chain or (
            pose['search_epoch'] == chain[-1]['search_epoch']
            and pose.get('history_generation', 0) == chain[-1].get('history_generation', 0)
            and 0 < pose['stamp_ns'] - chain[-1]['stamp_ns'] <= FRESH_NS))
        if not continuous and chain:
            for label in labels:
                start = max(chain[0]['stamp_ns'], label['start_ns'])
                end = min(chain[-1]['stamp_ns'], label['end_ns'])
                if end - start >= 6 * NS:
                    spans.append({'start_ns': start, 'end_ns': end,
                                  'search_epoch': chain[0]['search_epoch'],
                                  'history_generation': chain[0].get('history_generation', 0)})
            chain = []
        if usable:
            chain.append(pose)
    return spans


def _evaluate_run(prepared, parameters):
    run = prepared['run']
    unavailable, failures = [], []
    if not prepared['qualification']['qualified'] or prepared['qualification']['integrity_errors']:
        unavailable.append('typed_input_integrity_unavailable')
        events = []
    else:
        events = _detector_events(prepared, parameters['radius_m'])
        for event in events:
            event['moving_evidence'] = _verify_event(
                prepared, event, parameters['radius_m'], parameters['candidate_epsilon_m'])
    positives = prepared['supported_positives']
    negatives = [label for label in prepared['labels'] if label['kind'] == 'negative_directed_progress']
    negative_support = _eligible_negative_support(prepared['poses'], negatives)
    if run['exposure'] == 'residence' and not positives:
        unavailable.append('no_uncensored_first_42_second_positive_opportunity')
    if run['exposure'] == 'approach' and not negative_support:
        unavailable.append('no_eligible_six_second_directed_negative_interval')
    required = []
    for positive in positives:
        matches = [event for event in events if event['search_epoch'] == positive['search_epoch']
                   and positive['start_ns'] <= event['stamp_ns'] <= positive['end_ns']]
        receipt = {**positive, 'detected': bool(matches), 'event_ns': matches[0]['stamp_ns'] if matches else None}
        if not matches:
            failures.append('missed_required_positive')
        else:
            outcome = matches[0]['moving_evidence']
            receipt['moving_evidence_status'] = outcome['status']
            receipt['latency_sec'] = (matches[0]['stamp_ns'] - positive['truth_start_ns']) / NS
            if outcome['status'] == 'FAIL':
                failures.append('required_positive_moving_evidence_failed')
            elif outcome['status'] != 'PASS':
                unavailable.append('required_positive_moving_evidence_unavailable')
        required.append(receipt)
    if any(label['start_ns'] <= event['stamp_ns'] <= label['end_ns']
           for event in events for label in negatives):
        failures.append('detector_flag_on_declared_negative')
    status = 'FAIL' if failures else 'EVIDENCE_UNAVAILABLE' if unavailable else 'PASS'
    return {'run': run, 'status': status, 'failures': sorted(set(failures)),
            'unavailable': sorted(set(unavailable)), 'events': events,
            'required_positives': required, 'censored_positives': prepared['censored_positives'],
            'positive_opportunity_count': len(positives), 'negative_interval_count': len(negatives),
            'eligible_negative_support': negative_support,
            'eligible_negative_interval_count': len(negative_support),
            'event_label_counts': dict(Counter(e['independent_label'] for e in events)),
            'legacy_detector_latency': 'NOT_OBSERVED',
            'latency_claim': 'source_acquisition_proxy_not_live_callback_latency'}


def evaluate_q1_study_partition(frozen_labels_path, output_directory, *, nomination_manifest=None):
    """Evaluate exactly nine discovery pairs or one immutable confirmation pair."""
    path = Path(frozen_labels_path).resolve()
    reference = {'path': str(path), 'sha256': analysis._v2_file_hash(path)}
    frozen = _read(reference)
    contract_ref = frozen['contract']
    contract = analysis._q1_contract(contract_ref)
    _check_contract(contract)
    partition_seeds = analysis.qualification_partition_seeds(contract['version'])
    if frozen.get('status') != 'FROZEN' or frozen.get('version') != contract['version']:
        raise ValueError('Q1 immutable labels are incomplete or changed')
    partition = frozen['partition']
    if partition == 'confirmation':
        if contract['version'] in analysis.Q2_VERSIONS:
            analysis._q2_evaluation_receipt(
                nomination_manifest, contract_ref['sha256'], 'discovery', frozen['study_manifest'],
                version=contract['version'])
        nomination = analysis._q1_nomination(nomination_manifest, contract_ref['sha256'])
        if frozen.get('nomination') != nomination_manifest:
            raise ValueError('Q1 confirmation labels used another nomination')
        settings = [nomination['parameters']]
    elif partition == 'discovery' and nomination_manifest is None:
        settings = [{'window_seconds': 6, 'epsilon_m': .30, 'radius_m': radius,
                     'candidate_epsilon_m': epsilon}
                    for radius in (.25, .50, .75) for epsilon in (.05, .10, .15)]
    else:
        raise ValueError('Q1 partition/nomination mismatch')
    prepared = [_read(row) for row in frozen['runs']]
    if (len(prepared) != 2
            or sorted(p['run']['seed'] for p in prepared) != list(partition_seeds[partition])
            or any(p['run'] != r['run'] for p, r in zip(prepared, frozen['runs']))
            or any(p['run']['partition'] != partition or p['run']['exposure'] != exposure
                   for p, exposure in zip(sorted(prepared, key=lambda p: p['run']['seed']),
                                          ('residence', 'approach')))
            or any(p['contract_canonical_sha256'] != _hash(contract)
                   or p['spatial_labels_sha256'] != _hash(p['labels']) for p in prepared)):
        raise ValueError('Q1 frozen input/label population or binding changed')
    if contract['version'] in analysis.Q2_VERSIONS and any(
            p.get('version') != contract['version'] or p['qualification']['integrity_errors']
            for p in prepared):
        raise ValueError('Q2 prepared input integrity/version prohibits scientific fallback')
    for item in prepared:
        analysis._q1_verify_run(item['run'], contract)
    geometry = verify_q1_geometry(contract, runs=[item['run'] for item in prepared])
    if any(item['geometry_canonical_sha256'] != _hash(geometry) for item in prepared):
        raise ValueError('Q1 frozen spatial labels reference another geometry')
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    common = {'version': contract['version'], 'partition': partition,
              'contract_sha256': contract_ref['sha256'], 'labels': reference, 'claim': CLAIM}
    atomic_exclusive_json(output / 'started.json', {**common, 'status': 'INCOMPLETE'})
    results, receipts = [], []
    for index, parameters in enumerate(settings):
        outcomes = [_evaluate_run(run, parameters) for run in prepared]
        status = ('FAIL' if any(r['status'] == 'FAIL' for r in outcomes) else
                  'EVIDENCE_UNAVAILABLE' if any(r['status'] != 'PASS' for r in outcomes) else 'PASS')
        result = {**common, 'parameters': parameters, 'status': status, 'runs': outcomes}
        item_path = output / f'setting_{index + 1}.json'
        digest = atomic_exclusive_json(item_path, result)
        receipts.append({'path': str(item_path), 'sha256': digest})
        results.append(result)
    passing = [r for r in results if r['status'] == 'PASS']
    selected = passing[0] if passing else None  # Fixed smallest radius, then tolerance.
    status = 'PASS' if selected else ('EVIDENCE_UNAVAILABLE' if any(r['status'] == 'EVIDENCE_UNAVAILABLE' for r in results) else 'FAIL')
    result = {**common, 'status': status, 'parameters': selected['parameters'] if selected else None,
              'setting_receipts': receipts, 'settings_evaluated': len(settings),
              'selection_rule': 'smallest_radius_then_smallest_candidate_epsilon',
              'nomination': nomination_manifest, 'counterfactual_trajectory_claim': False}
    _read(reference)
    _read(frozen['study_manifest'])
    for receipt, item in zip(frozen['runs'], prepared):
        _read(receipt)
        analysis._q1_verify_run(item['run'], contract)
    analysis._q1_contract(contract_ref)
    atomic_exclusive_json(output / ('nomination.json' if partition == 'discovery' else 'confirmation.json'), result)
    return result
