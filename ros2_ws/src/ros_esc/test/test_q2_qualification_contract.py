"""Fresh Q2 population, sealing and observed-phase branch contracts.

Generated wires, temporary receipts and synthetic reference functions only.
No retained bag, field, confirmation recording or runtime node is opened.
"""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import v2_direction_reference as numeric
from ros_esc.scenario_runner import aggregate_field_truth as truth
from ros_esc.scenario_runner.run_scenario import find_run_directory
from ros_esc.v2_direction_policy import MOVING_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC, policy_metadata
from test_q1_direction_inputs import bag_from_messages
from test_q1_direction_references import receipt, write_json
from test_q2_policy_recording import moving_fixture
from test_v2_direction_reference import _binding


CHECKPOINT_SHA = '7df68a0af0b4fb953fc0631a4a5d0f9572d718a5ba74818deed025b583327863'
Q2_BUILD = '/home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1'
PARAMETERS = {'window_seconds': 6, 'epsilon_m': .30, 'radius_m': .5,
              'candidate_epsilon_m': .10}


def test_prospective_contract_has_exact48_symbolic_slots_and_no_confirmation_times():
    fields = analysis.q2_contract_fields()
    assert fields['version'] == 'q2-primary-shadow-v1'
    assert fields['expected_build'] == Q2_BUILD
    assert fields['runtime_source_checkpoint']['sha256'] == CHECKPOINT_SHA
    assert fields['direction_policy'] == policy_metadata(MOVING_CYCLE_POLICY)
    assert fields['reference']['method'] == analysis.Q1_OBSERVED_PHASE_METHOD
    slots = fields['planned_reference_slots']
    assert len(slots) == 48
    expected = {(seed, number) for seed in (26090921, 26090922, 26090923, 26090924)
                for number in range(1, 13)}
    assert {(row['seed'], row['number']) for row in slots} == expected
    for row in slots:
        assert set(row) == {'run_id', 'seed', 'partition', 'exposure', 'number',
                            'target_offset_sec', 'source_identity_status'}
        assert row['target_offset_sec'] == 10*row['number']
        assert row['run_id'] == f"q2-primary-shadow-v1-{row['partition']}-{row['exposure']}-{row['seed']}"
        assert row['source_identity_status'] == ('SEALED' if row['partition'] == 'confirmation' else 'UNBOUND')
    fields['planned_reference_slots'][0]['number'] = 99
    assert analysis.q2_contract_fields()['planned_reference_slots'][0]['number'] == 1


@pytest.mark.parametrize('version,seeds', [
    ('q1-primary-shadow-v1', (26090911, 26090912, 26090913, 26090914)),
    ('q2-primary-shadow-v1', (26090921, 26090922, 26090923, 26090924)),
    ('q2-primary-shadow-v2', (26090931, 26090932, 26090933, 26090934)),
])
def test_partition_version_is_explicit_and_returns_detached_mapping(version, seeds):
    actual = analysis.qualification_partition_seeds(version)
    assert tuple(actual['discovery']) + tuple(actual['confirmation']) == seeds
    actual['confirmation'] = ()
    assert len(analysis.qualification_partition_seeds(version)['confirmation']) == 2


@pytest.mark.parametrize('version', ['', 'q2', 'q2-primary-shadow-v3',
                                      'q1-discovery-direction-diagnostic-v1', None])
def test_unsupported_population_cannot_inherit_either_study(version):
    with pytest.raises(ValueError):
        analysis.qualification_partition_seeds(version)


def _retag(messages, metadata, run_id):
    metadata['scenario_runner']['v2_identity']['run_id'] = run_id
    for values in messages.values():
        for _, msg in values:
            if hasattr(msg, 'run_id'):
                msg.run_id = run_id
            if hasattr(msg, 'observation'):
                msg.observation.run_id = run_id


@pytest.fixture
def q2_study(tmp_path, monkeypatch, request):
    from ros_esc import v2_lifecycle, v2_stream, v2_direction_policy
    from ros_esc.experiment_recording import validate_run, record_run, v2_direction_policy_validation
    from ros_esc.plotting_scripts import bag_reader, q1_study
    version = getattr(request, 'param', analysis.Q2_VERSION)
    original_fields = analysis.q2_contract_fields
    expected = original_fields(version)
    # Substitute only historical transport receipts with synthetic closed
    # evidence. The real content/file verifiers remain active; no retained
    # checkpoint or failed acquisition is read.
    for key in ('runtime_source_checkpoint', 'prior_acquisition_closure',
                'acquisition_path_correction_checkpoint'):
        if key in expected:
            value = {'synthetic_receipt': key}
            if key == 'prior_acquisition_closure':
                value.update(version=analysis.Q2_VERSION, status='CLOSED_INCOMPLETE',
                             dispatched_cases=1, verified_runs=0,
                             scientific_evaluation_started=False,
                             scientific_confirmation_opened=False, all_cleanup_passed=True)
            expected[key] = write_json(tmp_path/(key+'.json'), value)
    monkeypatch.setattr(analysis, 'q2_contract_fields',
                        lambda version=analysis.Q2_VERSION: deepcopy(expected)
                        if version == expected['version'] else original_fields(version))
    modules = (analysis, numeric, bag_reader, v2_lifecycle, v2_stream, validate_run,
               record_run, truth, truth.cost_function_objects, v2_direction_policy,
               v2_direction_policy_validation, q1_study)
    source_files = [receipt(Path(module.__file__)) for module in modules]
    geometry = tmp_path/'synthetic_geometry.json'
    geometry.write_text('{"synthetic_receipt_only":true}')
    binding = {'binding': _binding(), 'settings': {}, 'selected_configurations': {
        'cost_function_config_filepath': receipt(geometry)}}
    monkeypatch.setattr(analysis, 'q1_recorded_binding', lambda *a, **k: deepcopy(binding))
    contract = {**deepcopy(expected), 'source_files': source_files,
                'execution': {'runs_root': str(tmp_path/'runs')},
                'geometry_receipts': [receipt(geometry)]}
    runs, streams, metadata_by_seed = [], {}, {}
    for slot in expected['planned_reference_slots'][::12]:
        run = {key: slot[key] for key in ('run_id', 'seed', 'partition', 'exposure')}
        created_at = datetime(2026, 9, 9, 23, 59, 59, tzinfo=timezone.utc)
        (tmp_path/'runs'/created_at.strftime('%Y-%m-%d')/run['run_id']/'bag').mkdir(parents=True)
        # Use the existing recorder/runner lookup contract, not a second assumed
        # direct-directory layout. Dedicated tests also execute recorder.run.
        directory = find_run_directory(tmp_path/'runs', run['run_id'])
        messages, metadata, _, _ = moving_fixture()
        _retag(messages, metadata, run['run_id'])
        streams[run['seed']], metadata_by_seed[run['seed']] = messages, metadata
        config = metadata['scenario_runner']['v2_identity']['stream_config']
        topic_entries = [{'topic': config[key], 'alias': key} for key in (
            'raw_cost_topic', 'augmented_cost_topic', 'provenance_topic',
            'objective_cost_topic', 'pose_topic', 'encoder_topic', 'timekeeper_topic')]
        topic_entries += [{'topic': POLICY_DIAGNOSTICS_TOPIC, 'alias': 'v2_direction_policy_diagnostics'},
                          {'topic': '/gesc_gaussian/v2/direction_diagnostics', 'alias': 'v2_direction_diagnostics'}]
        metadata['target_argv'] = ['ros2', 'launch', 'synthetic', 'test.launch.xml',
                                   'v2_direction_policy:='+MOVING_CYCLE_POLICY]
        values = {'metadata.yaml': metadata, 'resolved_scenario.yaml': {'sources': []},
                  'resolved_parameters.yaml': {'nodes': {}},
                  'resolved_topics.yaml': {'topics': topic_entries},
                  'bag/metadata.yaml': {'synthetic': True}}
        files = []
        for name, value in values.items():
            path = directory/name
            path.write_text(yaml.safe_dump(value))
            files.append(receipt(path))
        database = directory/'bag/data.db3'
        database.write_bytes(b'synthetic fixture, never opened as SQLite')
        files.append(receipt(database))
        run.update(run_directory=str(directory), input_files=files,
                   binding=deepcopy(binding), model_configuration=receipt(geometry))
        runs.append(run)
    contract['runs'] = [{key: run[key] for key in ('run_id', 'seed', 'partition', 'exposure')} |
                        {'resolved_scenario': {'sources': []},
                         'launch_argv': metadata_by_seed[run['seed']]['target_argv']}
                        for run in runs]
    contract_ref = write_json(tmp_path/'contract.json', contract)
    manifest = {'version': version, 'contract': contract_ref, 'runs': runs}
    manifest_path = tmp_path/'study_manifest.json'
    write_json(manifest_path, manifest)
    analysis_directory = tmp_path/'analysis'
    analysis_directory.mkdir()
    fixture = {'directory': analysis_directory, 'path': manifest_path, 'manifest': manifest,
               'contract': contract, 'contract_ref': contract_ref, 'runs': runs,
               'streams': streams, 'metadata': metadata_by_seed, 'reads': [],
               'aliases': [], 'rows': None}
    def read(directory, *, aliases):
        seed = next(run['seed'] for run in runs if run['run_id'] == Path(directory).name)
        fixture['reads'].append(seed)
        fixture['aliases'].append(set(aliases))
        return bag_from_messages(streams[seed])
    monkeypatch.setattr(analysis, 'read_run_bag', read)
    actual_normalize = analysis.prepare_moving_policy_direction_inputs
    def prepare(bag, metadata, *, run_spec):
        rows, qualification = actual_normalize(bag, metadata, run_spec=run_spec)
        if fixture['rows'] is not None and not qualification['integrity_errors']:
            rows = fixture['rows'](deepcopy(rows[0]), run_spec)
        return rows, qualification
    monkeypatch.setattr(analysis, 'prepare_moving_policy_direction_inputs', prepare)
    fixture['nomination'] = write_json(tmp_path/'nomination.json', {
        'version': version, 'status': 'PASS', 'partition': 'discovery',
        'contract_sha256': contract_ref['sha256'], 'parameters': PARAMETERS})
    return fixture


def freeze(study, partition='discovery', *, name=None, nomination=None):
    output = study['directory']/(name or partition+'_targets')
    kwargs = {'nomination_manifest': nomination or study['nomination']} if partition == 'confirmation' else {}
    result = analysis.freeze_q1_direction_targets(study['path'], output, partition=partition, **kwargs)
    return output/'targets.json', result


def test_discovery_freeze_uses_real_policy_companions_and_leaves_confirmation_unread(q2_study, monkeypatch):
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('no model at target freeze'))
    monkeypatch.setattr(numeric, 'observed_phase_cycle', lambda *a, **k: pytest.fail('cycle follows frozen selection'))
    _, frozen = freeze(q2_study)
    assert frozen['version'] == analysis.Q2_VERSION
    assert len(frozen['targets']) == 24
    assert q2_study['reads'] == [26090921, 26090922]
    assert all('v2_direction_policy_diagnostics' in aliases for aliases in q2_study['aliases'])
    for trace in frozen['input_traces']:
        data = json.loads(Path(trace['path']).read_text())
        assert data['qualification']['integrity_errors'] == []
        assert data['observations'][0]['method']['direction_policy'] == MOVING_CYCLE_POLICY
    confirmation_slots = [row for row in q2_study['contract']['planned_reference_slots']
                          if row['partition'] == 'confirmation']
    assert all(row['source_identity_status'] == 'SEALED' and 'target_ns' not in row
               for row in confirmation_slots)


@pytest.mark.parametrize('fault', ['missing', 'hash', 'policy', 'false_output'])
def test_corrupt_policy_pair_stops_freeze_before_final_targets(q2_study, fault):
    messages = q2_study['streams'][26090921]
    companion = messages[POLICY_DIAGNOSTICS_TOPIC][0][1]
    if fault == 'missing':
        del messages[POLICY_DIAGNOSTICS_TOPIC]
    elif fault == 'hash':
        companion.policy_config_sha256 = '0'*64
    elif fault == 'policy':
        companion.direction_policy = 'three_cycle_v1'
    else:
        messages['/gesc_gaussian/v2/direction_diagnostics'][0][1].output_body = [999., 999.]
    with pytest.raises(ValueError):
        freeze(q2_study)
    assert not (q2_study['directory']/'discovery_targets/targets.json').exists()
    assert not any(seed in (26090923, 26090924) for seed in q2_study['reads'])


@pytest.mark.parametrize('fault', ['checkpoint', 'build', 'slot_seed', 'slot_time', 'method', 'branch', 'policy'])
def test_changed_prospective_contract_refused_before_bag_read(q2_study, fault):
    contract = deepcopy(q2_study['contract'])
    if fault == 'checkpoint':
        Path(contract['runtime_source_checkpoint']['path']).write_text('changed checkpoint')
    elif fault == 'build':
        contract['expected_build'] = '/arbitrary/installed/build'
    elif fault == 'slot_seed':
        contract['planned_reference_slots'][24]['seed'] = 26090913
    elif fault == 'slot_time':
        contract['planned_reference_slots'][24]['target_ns'] = 1
    elif fault == 'method':
        contract['reference']['method']['version'] = 'old-reference'
    elif fault == 'branch':
        contract['reference_branch_rule']['incomplete_or_integrity_error'] = 'discovery_24_diagnostic'
    else:
        contract['direction_policy'] = policy_metadata('three_cycle_v1')
    q2_study['manifest']['contract'] = write_json(q2_study['directory']/'contract.json', contract)
    write_json(q2_study['path'], q2_study['manifest'])
    with pytest.raises(ValueError):
        freeze(q2_study)
    assert q2_study['reads'] == []


def label_job(study, discovery='PASS', confirmation='PASS'):
    """Create saved synthetic settings; exercise real receipt aggregation."""
    contract_ref = study['contract_ref']
    version = study['contract']['version']
    study_ref = receipt(study['path'])
    def partition_result(partition, status, nomination=None):
        directory = study['directory']/('discovery_nomination' if partition == 'discovery'
                                       else 'confirmation_evaluation')
        directory.mkdir()
        runs = [run for run in study['runs'] if run['partition'] == partition]
        support = []
        for run in runs:
            ref = write_json(directory/f'prepared_{run["seed"]}.json', {'run': run, 'synthetic': True})
            support.append({**ref, 'run': run})
        labels_directory = study['directory']/(partition+'_labels')
        labels_directory.mkdir()
        labels = write_json(labels_directory/'labels_manifest.json', {
            'version': version, 'status': 'FROZEN', 'partition': partition,
            'contract': contract_ref, 'study_manifest': study_ref, 'runs': support,
            'nomination': nomination})
        settings = ([{'window_seconds': 6, 'epsilon_m': .30, 'radius_m': radius,
                      'candidate_epsilon_m': epsilon}
                     for radius in (.25, .5, .75) for epsilon in (.05, .10, .15)]
                    if partition == 'discovery' else [PARAMETERS])
        common = {'version': version, 'partition': partition,
                  'contract_sha256': contract_ref['sha256'], 'labels': labels}
        refs = []
        for number, parameters in enumerate(settings):
            selected_status = ('PASS' if parameters == PARAMETERS else 'FAIL') if status == 'PASS' else status
            value = {**common, 'parameters': parameters, 'status': selected_status,
                     'runs': [{'run': run, 'status': selected_status,
                               'failures': ['synthetic_supported_miss'] if selected_status == 'FAIL' else [],
                               'unavailable': ['synthetic_missing_exposure'] if selected_status == 'EVIDENCE_UNAVAILABLE' else []}
                              for run in runs]}
            refs.append(write_json(directory/f'setting_{number+1}.json', value))
        result = {**common, 'status': status, 'parameters': PARAMETERS if status == 'PASS' else None,
                  'setting_receipts': refs, 'settings_evaluated': len(settings),
                  'selection_rule': 'smallest_radius_then_smallest_candidate_epsilon',
                  'nomination': nomination, 'counterfactual_trajectory_claim': False}
        ref = write_json(directory/('nomination.json' if partition == 'discovery'
                                    else 'confirmation.json'), result)
        return result, ref
    discovery_result, discovery_ref = partition_result('discovery', discovery)
    study['nomination'] = discovery_ref
    if discovery == 'PASS':
        confirmation_result, confirmation_ref = partition_result('confirmation', confirmation, discovery_ref)
    else:
        confirmation_result, confirmation_ref = 'SEALED_NOT_OPENED', None
    result = {'version': version, 'contract': contract_ref,
              'study_manifest': study_ref, 'completed': True, 'integrity_errors': [],
              'discovery_nomination': discovery_ref, 'confirmation_evaluation': confirmation_ref,
              'reference_branch': 'qualification48' if discovery == 'PASS' else 'discovery24_diagnostic',
              'status': confirmation if discovery == 'PASS' else discovery,
              'discovery': discovery_result, 'confirmation': confirmation_result,
              'pilot_released': False}
    path = study['directory']/'label_job.json'
    write_json(path, result)
    return path, result


def batch(study, target_paths, *, job=None, name='references', **kwargs):
    return analysis.evaluate_q1_direction_references(
        target_paths, study['directory']/name, contract_path=study['contract_ref']['path'],
        qualification_result_path=job, **kwargs)


@pytest.mark.parametrize('discovery', ['PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE'])
def test_completed_saved_settings_determine_branch_without_inputs_or_model(q2_study, monkeypatch, discovery):
    path, job = label_job(q2_study, discovery)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('branch never evaluates field'))
    selected = analysis._q2_reference_branch(path, q2_study['contract_ref'])
    assert selected['branch'] == ('qualification48' if discovery == 'PASS' else 'discovery24_diagnostic')
    assert selected['job']['status'] == discovery
    assert q2_study['reads'] == []


@pytest.mark.parametrize('fault', ['not_complete', 'timeout', 'integrity', 'missing_nomination',
    'nomination_hash', 'embedded_nomination', 'settings_count', 'setting_hash',
    'setting_aggregate', 'setting_population', 'setting_parameters', 'wrong_label_contract',
    'wrong_run_identity', 'wrong_branch', 'confirmation_unsealed'])
def test_invalid_completed_job_never_authorizes_reference_or_confirmation(q2_study, monkeypatch, fault):
    path, job = label_job(q2_study, 'FAIL')
    nomination = job['discovery']
    if fault == 'not_complete':
        job['completed'] = False
    elif fault == 'timeout':
        job['status'] = 'INCOMPLETE'
    elif fault == 'integrity':
        job['integrity_errors'] = ['lost selected source']
    elif fault == 'missing_nomination':
        job.pop('discovery_nomination')
    elif fault == 'nomination_hash':
        job['discovery_nomination']['sha256'] = '0'*64
    elif fault == 'embedded_nomination':
        job['discovery']['status'] = 'PASS'
    elif fault == 'settings_count':
        nomination['setting_receipts'].pop()
    elif fault == 'setting_hash':
        nomination['setting_receipts'][0]['sha256'] = '0'*64
    elif fault in ('setting_aggregate', 'setting_population', 'setting_parameters', 'wrong_run_identity'):
        ref = nomination['setting_receipts'][0]
        setting = json.loads(Path(ref['path']).read_text())
        if fault == 'setting_aggregate':
            setting['status'] = 'PASS'
        elif fault == 'setting_population':
            setting['runs'][0]['run']['seed'] = 26090923
        elif fault == 'wrong_run_identity':
            setting['runs'][0]['run']['run_id'] = 'different-run-same-seed'
        else:
            setting['parameters']['radius_m'] = .99
        nomination['setting_receipts'][0] = write_json(Path(ref['path']), setting)
    elif fault == 'wrong_label_contract':
        ref = nomination['labels']
        labels = json.loads(Path(ref['path']).read_text())
        labels['contract'] = {'path': '/different/contract', 'sha256': '0'*64}
        nomination['labels'] = write_json(Path(ref['path']), labels)
        for index, setting_ref in enumerate(nomination['setting_receipts']):
            setting = json.loads(Path(setting_ref['path']).read_text())
            setting['labels'] = nomination['labels']
            nomination['setting_receipts'][index] = write_json(Path(setting_ref['path']), setting)
    elif fault == 'wrong_branch':
        job['reference_branch'] = 'qualification48'
    else:
        job['confirmation'] = {'status': 'PASS'}
    if fault in ('settings_count', 'setting_hash', 'setting_aggregate', 'setting_population',
                 'setting_parameters', 'wrong_label_contract', 'wrong_run_identity'):
        job['discovery_nomination'] = write_json(Path(job['discovery_nomination']['path']), nomination)
    write_json(path, job)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('invalid job cannot model'))
    with pytest.raises(ValueError):
        analysis._q2_reference_branch(path, q2_study['contract_ref'])
    assert q2_study['reads'] == []


@pytest.mark.parametrize('status', ['FAIL', 'EVIDENCE_UNAVAILABLE', 'INCOMPLETE'])
def test_confirmation_t0_never_derived_from_nonpassing_nomination(q2_study, status):
    value = {'version': analysis.Q2_VERSION, 'status': status, 'partition': 'discovery',
             'contract_sha256': q2_study['contract_ref']['sha256'], 'parameters': PARAMETERS}
    ref = write_json(q2_study['directory']/'bad_nomination.json', value)
    with pytest.raises(ValueError):
        freeze(q2_study, 'confirmation', nomination=ref)
    assert q2_study['reads'] == []


def sparse_rows(template, run_spec, *, later_good=False, output='pass'):
    origin = template['stamp_ns']
    rows = [deepcopy(template)]
    for number in range(1, 13):
        row = deepcopy(template)
        row.update(stamp_ns=origin+number*10_000_000_000,
                   source_sequence=number*2, observation_id=number*2,
                   filter_stamp_ns=origin+number*10_000_000_000+1_000_000,
                   synthetic_cycle_available=not later_good)
        row['method'].update(aligned_instant_world=[0., 1.], v2_output_world=[.75, .25],
                             usable_output=True, blend_applied=True, usable_averaging=True,
                             fallback_used=False)
        if output == 'weak':
            row['method'].update(v2_output_world=None, usable_output=False, usable_averaging=False)
        elif output == 'fallback':
            row['method'].update(v2_output_world=[0., 1.], blend_applied=False,
                                 usable_averaging=False, fallback_used=True)
        rows.append(row)
        if later_good:
            later = deepcopy(row)
            later.update(stamp_ns=row['stamp_ns']+20_000_000, source_sequence=number*2+1,
                         observation_id=number*2+1, synthetic_cycle_available=True)
            rows.append(later)
    return rows


def synthetic_references(monkeypatch, *, outcome='pass', calls=None):
    calls = calls if calls is not None else []
    monkeypatch.setattr(numeric, 'reference_cycle', lambda *a, **k: pytest.fail('no old constant-rate cycle'))
    monkeypatch.setattr(numeric, 'replay_matched_direction', lambda *a, **k: pytest.fail('no callback replay'))
    monkeypatch.setattr(analysis, '_q1_observed_phase_latent', lambda *a, **k: pytest.fail('no D2 latent blend'))
    monkeypatch.setattr(numeric, 'integrate_stationary_harmonics', lambda *a, **k: pytest.fail('no old harmonics'))
    def cycle(rows, index):
        calls.append(('cycle', rows[index]['stamp_ns']))
        good = rows[index].get('synthetic_cycle_available', True)
        return {'version': 'observed-phase-periodic-v1', 'qualified': good,
                'reason': '' if good else 'missing_full_cycle', 'omega_rad_sec': 1.,
                'uniform_step_sec': .1}
    monkeypatch.setattr(numeric, 'observed_phase_cycle', cycle)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: (object(), None))
    monkeypatch.setattr(truth, 'evaluate_raw_cost', lambda *a, **k: pytest.fail('mocked reference never samples field'))
    def reference(objective, *, cycle, xy, sources):
        calls.append(('reference', len(calls)))
        if outcome == 'timeout' and sum(item[0] == 'reference' for item in calls) == 2:
            raise TimeoutError('synthetic reference deadline')
        if outcome == 'unavailable':
            return {'qualified': False, 'informative': False, 'reason': 'synthetic_numerical_unavailable'}
        return {'qualified': True, 'informative': True, 'reason': '',
                'world_vector': [.75, .25], 'magnitude': .7905694150420949,
                'estimated_vector_error': 1e-12, 'informative_threshold': 1e-6}
    monkeypatch.setattr(numeric, 'observed_phase_reference', reference)
    return calls


@pytest.mark.parametrize('status', ['FAIL', 'EVIDENCE_UNAVAILABLE'])
def test_completed_discovery_nonpass_retains24_results_and24_sealed_without_confirmation_read(
        q2_study, monkeypatch, status):
    job, _ = label_job(q2_study, status)
    q2_study['rows'] = sparse_rows
    targets, _ = freeze(q2_study)
    calls = synthetic_references(monkeypatch)
    original_read_text = Path.read_text
    def guarded_read_text(path, *args, **kwargs):
        if any(str(seed) in str(path) for seed in (26090923, 26090924)):
            pytest.fail('scientific confirmation read before nomination')
        return original_read_text(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', guarded_read_text)
    result = batch(q2_study, [targets], job=job)
    assert result['status'] == 'COMPLETE_DIAGNOSTIC'
    assert result['detector_qualification_status'] == status
    assert result['direction_qualification_status'] == result['combined_qualification_status'] == 'NOT_EVALUATED'
    assert result['fixed_anchor_count'] == result['all']['fixed_anchor_count'] == 24
    assert result['planned_anchor_count'] == 48 and len(result['sealed_slots']) == 24
    assert result['confirmation'] == 'SEALED' and not result['pilot_released']
    assert len(result['results']) == sum(item[0] == 'reference' for item in calls) == 24
    assert all('target_ns' not in row and 'source_stamp_ns' not in row for row in result['sealed_slots'])
    assert q2_study['reads'] == [26090921, 26090922]
    assert 'latent' not in result and all('latent' not in row for row in result['results'])


@pytest.mark.parametrize('detector,output,numerical,expected_direction,expected_combined', [
    ('PASS', 'pass', 'pass', 'PASS', 'PASS'),
    ('FAIL', 'pass', 'pass', 'PASS', 'FAIL'),
    ('EVIDENCE_UNAVAILABLE', 'pass', 'pass', 'PASS', 'EVIDENCE_UNAVAILABLE'),
    ('PASS', 'weak', 'pass', 'FAIL', 'FAIL'),
    ('PASS', 'fallback', 'pass', 'FAIL', 'FAIL'),
    ('PASS', 'pass', 'unavailable', 'EVIDENCE_UNAVAILABLE', 'EVIDENCE_UNAVAILABLE'),
])
def test_full_branch_keeps_direction_detector_and_combined_status_distinct(
        q2_study, monkeypatch, detector, output, numerical, expected_direction, expected_combined):
    job, _ = label_job(q2_study, 'PASS', detector)
    q2_study['rows'] = lambda row, run: sparse_rows(row, run, output=output)
    paths = [freeze(q2_study, partition)[0] for partition in ('discovery', 'confirmation')]
    calls = synthetic_references(monkeypatch, outcome=numerical)
    result = batch(q2_study, paths, job=job)
    assert result['version'] == analysis.Q2_VERSION
    assert result['status'] == result['direction_qualification_status'] == expected_direction
    assert result['detector_qualification_status'] == detector
    assert result['combined_qualification_status'] == expected_combined
    assert result['planned_anchor_count'] == result['fixed_anchor_count'] == 48
    assert len(result['results']) == 48 and result['sealed_slots'] == []
    assert len([item for item in calls if item[0] == 'reference']) == 48
    assert not result['pilot_released'] and 'latent' not in result
    assert result['all']['fixed_anchor_count'] == 48
    if numerical == 'pass':
        assert result['confirmation']['eligible_informative_count'] == 24
        assert result['confirmation']['averaging_availability'] == (1. if output == 'pass' else 0.)
        if output == 'weak':
            assert result['confirmation']['missing_or_weak_output_count'] == 24
            assert result['confirmation']['v2_median_error_deg'] is None


def test_first_causal_sample_is_not_replaced_by_later_complete_cycle(q2_study, monkeypatch):
    job, _ = label_job(q2_study, 'FAIL')
    q2_study['rows'] = lambda row, run: sparse_rows(row, run, later_good=True)
    monkeypatch.setattr(numeric, 'observed_phase_cycle', lambda *a, **k: pytest.fail('freeze must not inspect cycle'))
    path, frozen = freeze(q2_study)
    assert [row['observation_index'] for row in frozen['targets'][:12]] == list(range(1, 25, 2))
    calls = synthetic_references(monkeypatch)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('selected cycle unavailable'))
    result = batch(q2_study, [path], job=job)
    assert len(result['results']) == 24 and result['all']['causal_anchor_count'] == 24
    assert result['all']['input_cycle_qualified_count'] == 0
    assert result['all']['unavailable_reasons'] == {'missing_full_cycle': 24}
    assert all(kind == 'cycle' for kind, _ in calls)


@pytest.mark.parametrize('selector', ['default', 'diagnostic_contract_path', 'observed_phase_contract_path'])
def test_q2_cannot_be_presented_as_historical_reference_lineage(q2_study, monkeypatch, selector):
    job, _ = label_job(q2_study, 'PASS')
    paths = [freeze(q2_study, partition)[0] for partition in ('discovery', 'confirmation')]
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('wrong lineage cannot model'))
    kwargs = {} if selector == 'default' else {selector: q2_study['contract_ref']['path']}
    with pytest.raises(ValueError):
        analysis.evaluate_q1_direction_references(paths, q2_study['directory']/'bad_reference',
            contract_path=q2_study['contract_ref']['path'], **kwargs)
    assert not (q2_study['directory']/'bad_reference').exists()
    if selector != 'default':
        with pytest.raises(ValueError):
            batch(q2_study, paths, job=job, name='bad_mixed_reference', **kwargs)


def test_incomplete_job_does_not_even_hash_supplied_confirmation_targets(q2_study, monkeypatch):
    job, value = label_job(q2_study, 'FAIL')
    value['completed'] = False
    write_json(job, value)
    sealed = q2_study['directory']/'confirmation_targets/targets.json'
    sealed.parent.mkdir()
    sealed.write_text('{"synthetic_sealed":true}')
    original_hash = analysis._v2_file_hash
    def guarded_hash(path):
        assert Path(path) != sealed, 'confirmation target read before branch authorization'
        return original_hash(path)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('incomplete job cannot model'))
    with pytest.raises(ValueError):
        batch(q2_study, [sealed], job=job)
    assert not (q2_study['directory']/'references').exists()


def test_timeout_retains_partial_receipts_and_exclusive_attempt(q2_study, monkeypatch):
    job, _ = label_job(q2_study, 'FAIL')
    q2_study['rows'] = sparse_rows
    targets, _ = freeze(q2_study)
    synthetic_references(monkeypatch, outcome='timeout')
    with pytest.raises(TimeoutError):
        batch(q2_study, [targets], job=job)
    output = q2_study['directory']/'references'
    assert (output/'started.json').exists()
    assert len(list(output.glob('anchor_*.json'))) == 1
    assert not (output/'references.json').exists()
    with pytest.raises(FileExistsError):
        batch(q2_study, [targets], job=job)


@pytest.mark.parametrize('selector', ['diagnostic_contract_path', 'observed_phase_contract_path'])
def test_historical_single_manifest_route_rejects_new_version_lineage(q2_study, monkeypatch, selector):
    targets, _ = freeze(q2_study)
    declared = write_json(q2_study['directory']/'new_version_diagnostic.json', {
        'version': analysis.Q2_VERSION, 'frozen_targets': receipt(targets)})
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('new study cannot borrow old lineage'))
    with pytest.raises(ValueError):
        analysis.evaluate_q1_direction_references([targets], q2_study['directory']/'wrong_lineage',
            contract_path=q2_study['contract_ref']['path'], **{selector: declared['path']})
    assert not (q2_study['directory']/'wrong_lineage').exists()


@pytest.mark.parametrize('boundary', ['target', 'nomination'])
def test_cross_partition_path_is_rejected_before_hashing_sealed_file(q2_study, monkeypatch, boundary):
    job, value = label_job(q2_study, 'FAIL')
    targets, _ = freeze(q2_study)
    sealed = q2_study['directory']/'confirmation_targets/targets.json'
    sealed.parent.mkdir()
    sealed.write_text('{"synthetic_sealed":true}')
    if boundary == 'nomination':
        value['discovery_nomination'] = {'path': str(sealed), 'sha256': '0'*64}
        write_json(job, value)
    original_hash = analysis._v2_file_hash
    def guarded_hash(path):
        assert Path(path) != sealed, 'sealed file must not be opened to reject its path'
        return original_hash(path)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        batch(q2_study, [sealed if boundary == 'target' else targets], job=job)
    assert not (q2_study['directory']/'references').exists()


def test_completed_job_mutation_during_reference_preserves_partial_without_final_claim(q2_study, monkeypatch):
    job, value = label_job(q2_study, 'FAIL')
    q2_study['rows'] = sparse_rows
    targets, _ = freeze(q2_study)
    calls = synthetic_references(monkeypatch)
    def model(*args, **kwargs):
        value['integrity_errors'] = ['changed after branch selection']
        write_json(job, value)
        return object(), None
    monkeypatch.setattr(truth, '_model', model)
    with pytest.raises(ValueError):
        batch(q2_study, [targets], job=job)
    output = q2_study['directory']/'references'
    assert (output/'started.json').exists() and not (output/'references.json').exists()
    assert len(list(output.glob('anchor_*.json'))) == 12
    assert sum(kind == 'reference' for kind, _ in calls) == 12


def test_pooled_coverage_cannot_replace_six_informative_anchors_in_each_confirmation_run(q2_study, monkeypatch):
    job, _ = label_job(q2_study, 'PASS')
    q2_study['rows'] = sparse_rows
    paths = [freeze(q2_study, partition)[0] for partition in ('discovery', 'confirmation')]
    synthetic_references(monkeypatch)
    original = numeric.observed_phase_reference
    count = 0
    def reference(*args, **kwargs):
        nonlocal count
        count += 1
        # Discovery24; then only five informative in confirmation residence,
        # followed by all12 in confirmation approach. Pooled17 is insufficient.
        if 30 <= count <= 36:
            return {'qualified': False, 'informative': False, 'reason': 'synthetic_weak_reference'}
        return original(*args, **kwargs)
    monkeypatch.setattr(numeric, 'observed_phase_reference', reference)
    result = batch(q2_study, paths, job=job)
    assert result['confirmation']['eligible_informative_count'] == 17
    assert result['direction_qualification_status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['combined_qualification_status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['confirmation']['averaging_availability'] == 1.


@pytest.mark.parametrize('child', ['labels', 'setting'])
def test_discovery_child_receipt_cannot_open_a_sealed_confirmation_file(q2_study, monkeypatch, child):
    job, value = label_job(q2_study, 'FAIL')
    sealed = q2_study['directory']/'confirmation_labels/labels_manifest.json'
    sealed.parent.mkdir()
    sealed.write_text('{"synthetic_sealed":true}')
    replacement = receipt(sealed)
    nomination = value['discovery']
    if child == 'labels':
        nomination['labels'] = replacement
    else:
        nomination['setting_receipts'][0] = replacement
    value['discovery_nomination'] = write_json(Path(value['discovery_nomination']['path']), nomination)
    write_json(job, value)
    original_hash = analysis._v2_file_hash
    def guarded_hash(path):
        assert Path(path) != sealed, 'discovery child path must be rejected before any sealed read'
        return original_hash(path)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        analysis._q2_reference_branch(job, q2_study['contract_ref'])


@pytest.mark.parametrize('fault', ['trace_path', 'trace_identity', 'extra_trace'])
def test_discovery_trace_population_is_checked_before_sealed_receipt_read(q2_study, monkeypatch, fault):
    job, _ = label_job(q2_study, 'FAIL')
    path, frozen = freeze(q2_study)
    sealed = q2_study['directory']/'confirmation_targets/inputs_26090923.json'
    sealed.parent.mkdir()
    sealed.write_text('{"synthetic_sealed":true}')
    replacement = {**receipt(sealed), 'run': q2_study['runs'][2]}
    if fault == 'trace_path':
        frozen['input_traces'][0].update(receipt(sealed))
    elif fault == 'trace_identity':
        frozen['input_traces'][0]['run'] = q2_study['runs'][2]
    else:
        frozen['input_traces'].append(replacement)
    write_json(path, frozen)
    original_hash = analysis._v2_file_hash
    def guarded_hash(candidate):
        assert Path(candidate) != sealed, 'trace receipt read must follow exact population/path admission'
        return original_hash(candidate)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        batch(q2_study, [path], job=job)
    assert not (q2_study['directory']/'references').exists()


def test_run_directory_cannot_redirect_discovery_to_confirmation_bag(q2_study, monkeypatch):
    manifest = deepcopy(q2_study['manifest'])
    sealed = Path(manifest['runs'][2]['run_directory'])
    manifest['runs'][0]['run_directory'] = str(sealed)
    manifest['runs'][0]['input_files'] = deepcopy(manifest['runs'][2]['input_files'])
    write_json(q2_study['path'], manifest)
    original_hash = analysis._v2_file_hash
    def guarded_hash(candidate):
        assert not Path(candidate).is_relative_to(sealed), 'run scope must precede confirmation bag hashes'
        return original_hash(candidate)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        freeze(q2_study)
    assert q2_study['reads'] == []


def test_public_confirmation_freeze_rejects_non_nomination_path_before_hash(q2_study, monkeypatch):
    sealed = q2_study['directory']/'confirmation_labels/labels_manifest.json'
    sealed.parent.mkdir()
    ref = write_json(sealed, {'version': analysis.Q2_VERSION, 'status': 'PASS',
        'partition': 'discovery', 'contract_sha256': q2_study['contract_ref']['sha256'],
        'parameters': PARAMETERS})
    original_hash = analysis._v2_file_hash
    def guarded_hash(path):
        assert Path(path) != sealed, 'nomination path authority must precede even legacy PASS parsing'
        return original_hash(path)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        freeze(q2_study, 'confirmation', nomination=ref)
    assert q2_study['reads'] == []


def test_label_job_cannot_redirect_study_receipt_into_confirmation(q2_study, monkeypatch):
    job, value = label_job(q2_study, 'FAIL')
    sealed = q2_study['directory']/'confirmation_targets/targets.json'
    sealed.parent.mkdir()
    value['study_manifest'] = write_json(sealed, {'synthetic_sealed': True})
    write_json(job, value)
    original_hash = analysis._v2_file_hash
    def guarded_hash(path):
        assert Path(path) != sealed, 'study receipt scope must precede sealed file hash'
        return original_hash(path)
    monkeypatch.setattr(analysis, '_v2_file_hash', guarded_hash)
    with pytest.raises(ValueError):
        analysis._q2_reference_branch(job, q2_study['contract_ref'])


def test_corrected_version_preserves_old_default_and_all_scientific_values():
    old = analysis.q2_contract_fields()
    assert old == analysis.q2_contract_fields(analysis.Q2_VERSION)
    assert analysis.Q2_VERSION == 'q2-primary-shadow-v1'
    assert analysis.Q2_CORRECTED_VERSION == 'q2-primary-shadow-v2'
    assert set(analysis.Q2_VERSIONS) == {analysis.Q2_VERSION, analysis.Q2_CORRECTED_VERSION}
    corrected = analysis.q2_contract_fields(analysis.Q2_CORRECTED_VERSION)
    for key in ('reference', 'reference_branch_rule', 'direction_policy',
                'expected_build', 'runtime_source_checkpoint'):
        assert corrected[key] == old[key]
    assert corrected['prior_acquisition_closure']['sha256'] == \
        '672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02'
    assert corrected['acquisition_path_correction_checkpoint']['sha256'] == \
        '670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44'
    assert 'prior_acquisition_closure' not in old
    assert len(corrected['planned_reference_slots']) == 48
    assert {row['seed'] for row in corrected['planned_reference_slots']} == \
        {26090931, 26090932, 26090933, 26090934}
    for row in corrected['planned_reference_slots']:
        assert row['run_id'].startswith(analysis.Q2_CORRECTED_VERSION+'-')
        assert row['target_offset_sec'] == 10*row['number']
        assert row['source_identity_status'] == ('SEALED' if row['partition'] == 'confirmation' else 'UNBOUND')


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v1', 'q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('discovery', ['PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE'])
def test_each_version_runs_its_own_bound_full_or_sealed_synthetic_branch(q2_study, monkeypatch, discovery):
    version = q2_study['contract']['version']
    job, _ = label_job(q2_study, discovery)
    q2_study['rows'] = sparse_rows
    partitions = ('discovery', 'confirmation') if discovery == 'PASS' else ('discovery',)
    paths = [freeze(q2_study, partition)[0] for partition in partitions]
    calls = synthetic_references(monkeypatch)
    result = batch(q2_study, paths, job=job)
    assert result['version'] == version and result['planned_anchor_count'] == 48
    expected_count = 48 if discovery == 'PASS' else 24
    assert result['fixed_anchor_count'] == len(result['results']) == expected_count
    assert sum(name == 'reference' for name, _ in calls) == expected_count
    expected_seeds = analysis.qualification_partition_seeds(version)
    assert {row['seed'] for row in result['results']} == {
        seed for partition in partitions for seed in expected_seeds[partition]}
    assert set(q2_study['reads']) == {seed for partition in partitions for seed in expected_seeds[partition]}
    assert result['detector_qualification_status'] == discovery
    assert result['combined_qualification_status'] == ('PASS' if discovery == 'PASS' else 'NOT_EVALUATED')
    assert len(result['sealed_slots']) == (0 if discovery == 'PASS' else 24)


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('component', ['job', 'nomination', 'setting', 'labels', 'targets', 'trace'])
def test_cross_version_receipt_cannot_enter_corrected_reference_branch(q2_study, monkeypatch, component):
    job, value = label_job(q2_study, 'FAIL')
    targets, frozen = freeze(q2_study)
    old = analysis.Q2_VERSION
    nomination = value['discovery']
    if component == 'job':
        value['version'] = old
    elif component == 'nomination':
        nomination['version'] = old
    elif component == 'setting':
        ref = nomination['setting_receipts'][0]
        setting = json.loads(Path(ref['path']).read_text())
        setting['version'] = old
        nomination['setting_receipts'][0] = write_json(Path(ref['path']), setting)
    elif component == 'labels':
        ref = nomination['labels']
        labels = json.loads(Path(ref['path']).read_text())
        labels['version'] = old
        nomination['labels'] = write_json(Path(ref['path']), labels)
        for i, ref in enumerate(nomination['setting_receipts']):
            setting = json.loads(Path(ref['path']).read_text())
            setting['labels'] = nomination['labels']
            nomination['setting_receipts'][i] = write_json(Path(ref['path']), setting)
    elif component == 'targets':
        frozen['version'] = old
        write_json(targets, frozen)
    else:
        ref = frozen['input_traces'][0]
        trace = json.loads(Path(ref['path']).read_text())
        trace['version'] = old
        updated = write_json(Path(ref['path']), trace)
        frozen['input_traces'][0].update(updated)
        for target in frozen['targets']:
            if target['input_trace_path'] == updated['path']:
                target['input_trace_sha256'] = updated['sha256']
        write_json(targets, frozen)
    if component in ('nomination', 'setting', 'labels'):
        value['discovery_nomination'] = write_json(Path(value['discovery_nomination']['path']), nomination)
    write_json(job, value)
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('mixed-version input cannot model'))
    with pytest.raises(ValueError):
        batch(q2_study, [targets], job=job)
    assert not (q2_study['directory']/'references').exists()


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('field', ['prior_acquisition_closure', 'acquisition_path_correction_checkpoint'])
def test_corrected_version_rechecks_failed_attempt_and_correction_receipts(q2_study, field):
    Path(q2_study['contract'][field]['path']).write_text('changed receipt')
    with pytest.raises(ValueError):
        freeze(q2_study)
    assert q2_study['reads'] == []


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('field,value', [
    ('version', 'q2-primary-shadow-v2'), ('status', 'PASS'),
    ('dispatched_cases', 2), ('verified_runs', 1),
    ('scientific_evaluation_started', True),
    ('scientific_confirmation_opened', True), ('all_cleanup_passed', False),
])
def test_corrected_version_checks_closed_attempt_semantics_not_only_hash(
        q2_study, monkeypatch, field, value):
    contract = deepcopy(q2_study['contract'])
    path = Path(contract['prior_acquisition_closure']['path'])
    closed = json.loads(path.read_text())
    closed[field] = value
    updated = write_json(path, closed)
    expected = analysis.q2_contract_fields(analysis.Q2_CORRECTED_VERSION)
    expected['prior_acquisition_closure'] = updated
    contract['prior_acquisition_closure'] = updated
    original = analysis.q2_contract_fields
    monkeypatch.setattr(analysis, 'q2_contract_fields',
                        lambda version=analysis.Q2_VERSION: deepcopy(expected)
                        if version == analysis.Q2_CORRECTED_VERSION else original(version))
    with pytest.raises(ValueError, match='preserved incomplete closure'):
        analysis._q1_validate_contract(contract)
    assert q2_study['reads'] == []
