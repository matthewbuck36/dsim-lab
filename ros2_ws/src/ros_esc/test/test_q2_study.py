"""Fresh Q2 label/workflow dispatch on synthetic inputs; no bags or field jobs."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from nav_msgs.msg import Odometry

from ros_esc.plotting_scripts import q1_study as q
from ros_esc.plotting_scripts.bag_reader import BagRecord
from test_q1_study import PARAMETERS, geometry_fixture, poses, positive, prepared, write


def contract(version=q.analysis.Q2_VERSION):
    return {**q.analysis.q2_contract_fields(version), 'detector': deepcopy(q.DETECTOR_CONTRACT)}


@pytest.fixture
def workflow(monkeypatch):
    repository = Path(__file__).resolve().parents[4]
    tools = repository / 'docs/codex/gesc_gaussian/v2/tools'
    monkeypatch.syspath_prepend(str(tools))
    spec = importlib.util.spec_from_file_location('q2_study_workflow_fixture', tools / 'evaluate_q1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen(tmp_path, monkeypatch, *, partition='discovery', version=q.analysis.Q2_VERSION):
    document = contract(version)
    preflight = tmp_path / 'preflight'
    preflight.mkdir(exist_ok=True)
    label_directory = tmp_path / 'analysis' / f'{partition}_labels'
    label_directory.mkdir(parents=True)
    contract_ref = write(preflight / 'contract.json', document)
    monkeypatch.setattr(q.analysis, '_q1_contract', lambda ref: q._read(ref))
    monkeypatch.setattr(q.analysis, '_q1_verify_run', lambda *args: None)
    monkeypatch.setattr(q, 'verify_q1_geometry', lambda *args, **kwargs: {})
    receipts = []
    for seed, exposure in zip(q.analysis.qualification_partition_seeds(version)[partition],
                              ('residence', 'approach')):
        item = prepared(exposure=exposure, rows=False)
        item['run'].update(seed=seed, partition=partition,
                           run_id=f'{version}-{partition}-{exposure}-{seed}')
        item.update(version=version, contract_canonical_sha256=q._hash(document),
                    geometry_canonical_sha256=q._hash({}), spatial_labels_sha256=q._hash(item['labels']))
        item_ref = write(label_directory / f'labels_{seed}.json', item)
        receipts.append({**item_ref, 'run': item['run']})
    all_runs = [{'run_id': f'{version}-{name}-{exposure}-{seed}',
                 'seed': seed, 'partition': name, 'exposure': exposure}
                for name, seeds in q.analysis.qualification_partition_seeds(version).items()
                for seed, exposure in zip(seeds, ('residence', 'approach'))]
    study_ref = write(tmp_path / 'study_manifest.json', {'version': version,
                                                        'contract': contract_ref, 'runs': all_runs})
    manifest = {'version': version, 'status': 'FROZEN', 'partition': partition,
                'contract': contract_ref, 'runs': receipts, 'study_manifest': study_ref, 'nomination': None}
    return manifest, write(label_directory / 'labels_manifest.json', manifest)


@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_q2_dispatch_uses_moving_inputs_and_preserves_actual_pose_label_order(monkeypatch, version):
    pose = Odometry()
    pose.header.frame_id = 'odom'
    pose.pose.pose.position.x = 3.
    bag = SimpleNamespace(records_by_topic={
        '/selected': [BagRecord('/selected', 'Odometry', 0, 0, None, False, pose, True)]})
    metadata = {'scenario_runner': {'v2_identity': {
        'stream_config': {'pose_topic': '/selected', 'frame_id': 'odom'}}}}
    calls = []
    row = {'stamp_ns': 0, 'xy': [99., 99.], 'qualified': True}

    def selected(*args, **kwargs):
        calls.append('moving_inputs')
        assert kwargs == {'run_spec': {'run_id': 'q2'}}
        return [row], {'qualified': True, 'integrity_errors': []}

    def forbidden(*args, **kwargs):
        pytest.fail('fresh Q2 must not use the old policy input interpretation')

    def label(values, geometry):
        calls.append('spatial_labels')
        assert values[0]['xy'] == [3., 0.]
        return []

    def mask(values, _bag):
        calls.append('eligibility_mask')
        return values

    monkeypatch.setattr(q.analysis, 'prepare_moving_policy_direction_inputs', selected)
    monkeypatch.setattr(q.analysis, 'prepare_q1_direction_inputs', forbidden)
    monkeypatch.setattr(q.analysis, 'label_v2_basin_intervals', label)
    monkeypatch.setattr(q.analysis, 'q1_pose_search_eligibility', mask)
    result = q.prepare_q1_study_run(bag, metadata, contract=contract(version), run_spec={'run_id': 'q2'}, geometry={})
    assert result['version'] == version
    assert calls == ['moving_inputs', 'spatial_labels', 'eligibility_mask', 'eligibility_mask']
    assert result['observations'][0]['xy'] == [99., 99.]
    assert result['spatial_labels_precede_eligibility_mask']
    assert not result['detector_evaluated_for_labeling']


def test_q2_integrity_failure_cannot_become_completed_empty_label_fallback(monkeypatch):
    monkeypatch.setattr(q.analysis, 'prepare_moving_policy_direction_inputs',
                        lambda *args, **kwargs: ([], {'qualified': False, 'integrity_errors': ['conflict']}))
    with pytest.raises(ValueError, match='integrity'):
        q.prepare_q1_study_run(None, {}, contract=contract(), run_spec={}, geometry={})


def test_q2_empty_input_without_integrity_error_remains_unavailable(monkeypatch):
    monkeypatch.setattr(q.analysis, 'prepare_moving_policy_direction_inputs',
                        lambda *args, **kwargs: ([], {'qualified': False, 'integrity_errors': []}))
    metadata = {'scenario_runner': {'v2_identity': {
        'stream_config': {'pose_topic': '/selected', 'frame_id': 'odom'}}}}
    result = q.prepare_q1_study_run(SimpleNamespace(records_by_topic={}), metadata,
                                    contract=contract(), run_spec={}, geometry={})
    assert result['labels'] == result['poses'] == result['observations'] == []
    assert not result['qualification']['qualified']


def test_q2_geometry_reuses_the_original_verified_chain(tmp_path, monkeypatch):
    document, scenario, geometry, point, _ = geometry_fixture(tmp_path, monkeypatch)
    document.update(q.analysis.q2_contract_fields())
    assert q.verify_q1_geometry(document, scenario) == geometry
    Path(point['path']).write_text('{}')
    with pytest.raises(ValueError):
        q.verify_q1_geometry(document, scenario)


@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_q2_reader_includes_companion_and_keeps_confirmation_closed(tmp_path, monkeypatch, version):
    document = contract(version)
    contract_ref = write(tmp_path / 'contract.json', document)
    runs = [{'run_id': str(seed), 'run_directory': str(tmp_path / str(seed)), 'seed': seed,
             'partition': partition, 'exposure': exposure}
            for partition, seeds in q.analysis.qualification_partition_seeds(version).items()
            for seed, exposure in zip(seeds, ('residence', 'approach'))]
    manifest = write(tmp_path / 'study.json', {'version': version,
                                              'contract': contract_ref, 'runs': runs})
    monkeypatch.setattr(q.analysis, '_q1_contract', lambda ref: q._read(ref))
    monkeypatch.setattr(q.analysis, '_q1_verify_run', lambda *args: None)
    monkeypatch.setattr(q, 'verify_q1_geometry', lambda *args, **kwargs: {})
    config = {key: f'/selected/{key}' for key in q.TOPIC_KEYS}

    def load_yaml(path):
        if path.name == 'metadata.yaml':
            return {'scenario_runner': {'v2_identity': {'stream_config': config}}}
        return {'topics': [{'topic': topic, 'alias': key} for key, topic in config.items()]}

    seen = []

    def read_bag(path, *, aliases):
        assert aliases == set(q.TOPIC_KEYS) | {
            'v2_direction_diagnostics', 'v2_direction_policy_diagnostics', 'algorithm_state', 'clock'}
        assert str(path).endswith(tuple(str(seed) for seed in
            q.analysis.qualification_partition_seeds(version)['discovery']))
        seen.append(path)
        return None

    monkeypatch.setattr(q.analysis, 'load_yaml', load_yaml)
    monkeypatch.setattr(q.analysis, 'read_run_bag', read_bag)
    monkeypatch.setattr(q, 'prepare_q1_study_run', lambda *args, **kwargs: {
        'version': version, 'labels': [], 'detector_evaluated_for_labeling': False})
    with pytest.raises((ValueError, TypeError)):
        q.freeze_q1_study_labels(manifest['path'], tmp_path / 'sealed', partition='confirmation')
    assert not seen and not (tmp_path / 'sealed').exists()
    result = q.freeze_q1_study_labels(manifest['path'], tmp_path / 'discovery', partition='discovery')
    assert result['version'] == version and len(seen) == 2
    assert not result['detector_evaluated_for_labeling']


@pytest.mark.parametrize('change', ['old_seed', 'old_version', 'other_q2_version', 'integrity'])
@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_q2_frozen_inputs_reject_old_population_or_ambiguity_before_detector(tmp_path, monkeypatch, change, version):
    manifest, ref = frozen(tmp_path, monkeypatch, version=version)
    child = q._read(manifest['runs'][0])
    if change == 'old_seed':
        child['run']['seed'] = 26090911
        manifest['runs'][0]['run'] = child['run']
    elif change == 'old_version':
        child['version'] = q.analysis.Q1_VERSION
    elif change == 'other_q2_version':
        child['version'] = next(item for item in q.analysis.Q2_VERSIONS if item != version)
    else:
        child['qualification']['integrity_errors'] = ['ambiguous acquisition']
    manifest['runs'][0].update(write(Path(manifest['runs'][0]['path']), child))
    write(Path(ref['path']), manifest)
    monkeypatch.setattr(q, '_detector_events', lambda *args: pytest.fail('detector must remain unopened'))
    with pytest.raises(ValueError):
        q.evaluate_q1_study_partition(ref['path'], tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


@pytest.mark.parametrize('pattern,expected', [('all_fail', 'FAIL'), ('all_unavailable', 'EVIDENCE_UNAVAILABLE'),
                                             ('mixed', 'EVIDENCE_UNAVAILABLE')])
def test_q2_failed_settings_stay_failed_while_unresolved_pairs_remain_explicit(
        tmp_path, monkeypatch, pattern, expected):
    _, ref = frozen(tmp_path, monkeypatch)

    def evaluate(_prepared, parameters):
        status = ('FAIL' if pattern == 'all_fail' or pattern == 'mixed' and parameters['radius_m'] == .25
                  else 'EVIDENCE_UNAVAILABLE')
        return {'status': status, 'failures': ['measured failure'] if status == 'FAIL' else [],
                'unavailable': ['missing exposure'] if status != 'FAIL' else []}

    monkeypatch.setattr(q, '_evaluate_run', evaluate)
    result = q.evaluate_q1_study_partition(ref['path'], tmp_path / 'out')
    assert result['status'] == expected and result['parameters'] is None
    assert result['settings_evaluated'] == 9
    settings = [q._read(item) for item in result['setting_receipts']]
    assert len(settings) == 9
    if pattern == 'mixed':
        assert [item['status'] for item in settings] == ['FAIL'] * 3 + ['EVIDENCE_UNAVAILABLE'] * 6


@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_q2_nine_pair_selection_and_single_confirmation_preserve_parameters(tmp_path, monkeypatch, version):
    discovery_manifest, ref = frozen(tmp_path, monkeypatch, version=version)
    discovery_output = tmp_path / 'analysis/discovery_nomination'
    calls = []

    def evaluate(_prepared, parameters):
        calls.append(deepcopy(parameters))
        return {'run': deepcopy(_prepared['run']),
                'status': 'PASS' if parameters['radius_m'] >= .5 and parameters['candidate_epsilon_m'] >= .1
                else 'FAIL'}

    monkeypatch.setattr(q, '_evaluate_run', evaluate)
    result = q.evaluate_q1_study_partition(ref['path'], discovery_output)
    assert result['parameters'] == PARAMETERS and len(calls) == 18
    nomination_ref = {'path': str(discovery_output / 'nomination.json'),
                      'sha256': q.analysis._v2_file_hash(discovery_output / 'nomination.json')}
    manifest, ref = frozen(tmp_path, monkeypatch, partition='confirmation', version=version)
    # Both partitions must bind the same prospectively frozen contract bytes.
    assert manifest['contract']['sha256'] == result['contract_sha256']
    manifest['contract'] = discovery_manifest['contract']
    manifest['study_manifest'] = discovery_manifest['study_manifest']
    manifest['nomination'] = nomination_ref
    write(Path(ref['path']), manifest)
    calls.clear()
    confirmed = q.evaluate_q1_study_partition(ref['path'], tmp_path / 'analysis/confirmation_evaluation',
                                             nomination_manifest=nomination_ref)
    assert calls == [PARAMETERS, PARAMETERS] and confirmed['settings_evaluated'] == 1


@pytest.mark.parametrize('stage', ['freeze', 'evaluate'])
@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_q2_forged_passing_nomination_cannot_open_confirmation_support(tmp_path, monkeypatch, stage, version):
    manifest, ref = frozen(tmp_path, monkeypatch, partition='confirmation', version=version)
    nomination_path = tmp_path / 'analysis/discovery_nomination/nomination.json'
    nomination_path.parent.mkdir()
    nomination_ref = write(nomination_path, {
        'version': version, 'status': 'PASS', 'partition': 'discovery',
        'contract_sha256': manifest['contract']['sha256'], 'parameters': PARAMETERS})
    manifest['nomination'] = nomination_ref
    write(Path(ref['path']), manifest)
    # A hash-valid top-level PASS alone has no completed nine-setting authority.
    children = {row['path'] for row in manifest['runs']}
    original_read = q._read

    def guarded_read(receipt):
        if receipt['path'] in children:
            pytest.fail('confirmation prepared input was read before nomination validation')
        return original_read(receipt)

    monkeypatch.setattr(q, '_read', guarded_read)
    monkeypatch.setattr(q.analysis, 'read_run_bag',
                        lambda *args, **kwargs: pytest.fail('confirmation bag was opened'))
    if stage == 'freeze':
        runs = [{'run_id': f'{version}-{partition}-{exposure}-{seed}',
                 'seed': seed, 'partition': partition, 'exposure': exposure}
                for partition, seeds in q.analysis.qualification_partition_seeds(version).items()
                for seed, exposure in zip(seeds, ('residence', 'approach'))]
        study = write(tmp_path / 'study_manifest.json', {'version': version,
                                                   'contract': manifest['contract'], 'runs': runs})
        operation = lambda: q.freeze_q1_study_labels(
            study['path'], tmp_path / 'out', partition='confirmation', nomination_manifest=nomination_ref)
    else:
        operation = lambda: q.evaluate_q1_study_partition(
            ref['path'], tmp_path / 'out', nomination_manifest=nomination_ref)
    with pytest.raises(ValueError, match='setting population'):
        operation()
    assert not (tmp_path / 'out').exists()


def test_q2_first_short_residence_cannot_be_replaced_and_required_miss_is_failure():
    path = poses(100)
    supported, censored = q.analysis._v2_common_positive_support(
        path, [positive(0, 20), positive(30, 100)], minimum_duration_sec=42)
    assert not supported and censored[-1]['reason'] == 'later_residence_after_first_opportunity'
    item = prepared(rows=False, position=lambda t: (.04 * t, 0.))
    item.update(version=q.analysis.Q2_VERSION)
    item['run']['seed'] = 26090921
    outcome = q._evaluate_run(item, PARAMETERS)
    assert outcome['status'] == 'FAIL' and 'missed_required_positive' in outcome['failures']


def evaluation_fixture(tmp_path, contract_ref, *, partition, status, nomination=None):
    """Canonical completed receipts with real central authority validation."""
    version = json.loads(Path(contract_ref['path']).read_text())['version']
    directory = tmp_path / 'analysis' / (
        'discovery_nomination' if partition == 'discovery' else 'confirmation_evaluation')
    directory.mkdir(parents=True, exist_ok=True)
    label_directory = tmp_path / 'analysis' / f'{partition}_labels'
    label_directory.mkdir(exist_ok=True)
    study_ref = write(tmp_path / 'study_manifest.json',
                      {'version': version, 'contract': contract_ref})
    labels = write(label_directory / 'labels_manifest.json', {
        'version': version, 'status': 'FROZEN', 'partition': partition,
        'study_manifest': study_ref, 'contract': contract_ref})
    parameters = ([{'window_seconds': 6, 'epsilon_m': .30, 'radius_m': radius,
                   'candidate_epsilon_m': epsilon}
                  for radius in (.25, .50, .75) for epsilon in (.05, .10, .15)]
                  if partition == 'discovery' else [PARAMETERS])
    setting_refs = []
    for number, selected in enumerate(parameters, 1):
        setting_status = ('FAIL' if partition == 'discovery' and status == 'PASS'
                          and number < parameters.index(PARAMETERS) + 1 else status)
        runs = [{'run': {'run_id': f'{version}-{partition}-{exposure}-{seed}',
                         'seed': seed, 'partition': partition, 'exposure': exposure}, 'status': setting_status}
                for seed, exposure in zip(q.analysis.qualification_partition_seeds(version)[partition], ('residence', 'approach'))]
        setting_refs.append(write(directory / f'setting_{number}.json', {
            'version': version, 'partition': partition, 'contract_sha256': contract_ref['sha256'],
            'labels': labels, 'parameters': selected, 'status': setting_status, 'runs': runs}))
    result = {'version': version, 'status': status, 'partition': partition,
              'contract_sha256': contract_ref['sha256'], 'parameters': PARAMETERS if status == 'PASS' else None,
              'settings_evaluated': len(parameters), 'setting_receipts': setting_refs, 'labels': labels,
              'selection_rule': 'smallest_radius_then_smallest_candidate_epsilon'}
    if partition == 'confirmation':
        result['nomination'] = nomination
    ref = write(directory / ('nomination.json' if partition == 'discovery' else 'confirmation.json'), result)
    return result, ref, study_ref


def label_job_fixture(tmp_path, workflow, *, discovery_status='FAIL', confirmation_status='PASS',
                      version=q.analysis.Q2_VERSION):
    document = contract(version)
    contract_ref = write(tmp_path / 'contract.json', document)
    discovery, nomination_ref, study_ref = evaluation_fixture(
        tmp_path, contract_ref, partition='discovery', status=discovery_status)
    confirmation, confirmation_ref = 'SEALED_NOT_OPENED', None
    if discovery_status == 'PASS':
        confirmation, confirmation_ref, _ = evaluation_fixture(
            tmp_path, contract_ref, partition='confirmation', status=confirmation_status, nomination=nomination_ref)
    job = {'version': version, 'contract': deepcopy(contract_ref), 'completed': True,
           'integrity_errors': [], 'status': confirmation_status if discovery_status == 'PASS' else discovery_status,
           'study_manifest': study_ref,
           'discovery': discovery, 'confirmation': confirmation, 'discovery_nomination': nomination_ref,
           'confirmation_evaluation': confirmation_ref,
           'reference_branch': 'qualification48' if discovery_status == 'PASS' else 'discovery24_diagnostic'}
    path = tmp_path / 'analysis/label_job.json'
    write(path, job)
    return document, contract_ref, job, path


@pytest.mark.parametrize('status', ['FAIL', 'EVIDENCE_UNAVAILABLE'])
@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_reference_diagnostic_branch_does_not_read_any_confirmation_receipt(
        tmp_path, monkeypatch, workflow, status, version):
    _, contract_ref, job, path = label_job_fixture(tmp_path, workflow, version=version, discovery_status=status)
    original = Path.read_text

    def guarded(file, *args, **kwargs):
        if 'confirmation' in str(file):
            pytest.fail('sealed confirmation was opened')
        return original(file, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', guarded)
    targets, result_path = workflow._q2_reference_target_paths(tmp_path, contract_ref)
    assert targets == [tmp_path / 'analysis/discovery_targets/targets.json']
    assert result_path == path and job['status'] == status


@pytest.mark.parametrize('confirmation_status', ['PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE'])
@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_passing_discovery_unlocks_48_even_when_detector_confirmation_fails(
        tmp_path, workflow, confirmation_status, version):
    _, contract_ref, job, _ = label_job_fixture(tmp_path, workflow, version=version,
                                               discovery_status='PASS', confirmation_status=confirmation_status)
    paths, _ = workflow._q2_reference_target_paths(tmp_path, contract_ref)
    assert paths == [tmp_path / 'analysis/discovery_targets/targets.json',
                     tmp_path / 'analysis/confirmation_targets/targets.json']
    assert job['status'] == confirmation_status  # Direction evaluation has no authority over this.


@pytest.mark.parametrize('child_failure', ['hash', 'status_conflict'])
def test_wrapper_rejects_forged_top_level_pass_before_any_sealed_confirmation_read(
        tmp_path, monkeypatch, workflow, child_failure):
    _, contract_ref, job, path = label_job_fixture(tmp_path, workflow, discovery_status='PASS')
    discovery = job['discovery']
    if child_failure == 'hash':
        discovery['setting_receipts'][0]['sha256'] = '0' * 64
    else:
        setting_path = Path(discovery['setting_receipts'][0]['path'])
        setting = json.loads(setting_path.read_text())
        setting['status'] = 'PASS'  # Contradicts the retained FAIL run outcomes.
        discovery['setting_receipts'][0] = write(setting_path, setting)
    job['discovery_nomination'] = write(Path(job['discovery_nomination']['path']), discovery)
    write(path, job)
    assert (tmp_path / 'analysis/confirmation_evaluation/confirmation.json').exists()
    original_open = Path.open

    def guarded_open(file, *args, **kwargs):
        if any(part.startswith('confirmation_') for part in file.parts):
            pytest.fail('sealed confirmation was opened or hashed before full discovery authority')
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', guarded_open)
    with pytest.raises(ValueError):
        workflow._q2_reference_target_paths(tmp_path, contract_ref)


@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
@pytest.mark.parametrize('owner', ['job', 'nomination', 'labels', 'setting'])
def test_q2_versions_cannot_mix_completed_authority(tmp_path, monkeypatch, workflow, version, owner):
    _, contract_ref, job, path = label_job_fixture(
        tmp_path, workflow, version=version, discovery_status='FAIL')
    other = next(item for item in q.analysis.Q2_VERSIONS if item != version)
    if owner == 'job':
        job['version'] = other
    else:
        discovery = job['discovery']
        if owner == 'nomination':
            discovery['version'] = other
        elif owner == 'labels':
            label_path = Path(discovery['labels']['path'])
            labels = json.loads(label_path.read_text())
            labels['version'] = other
            discovery['labels'] = write(label_path, labels)
        else:
            setting_path = Path(discovery['setting_receipts'][0]['path'])
            setting = json.loads(setting_path.read_text())
            setting['version'] = other
            discovery['setting_receipts'][0] = write(setting_path, setting)
        job['discovery_nomination'] = write(Path(job['discovery_nomination']['path']), discovery)
    write(path, job)
    original_open = Path.open

    def guarded_open(file, *args, **kwargs):
        if any(part.startswith('confirmation_') for part in file.parts):
            pytest.fail('cross-version authority opened sealed confirmation')
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', guarded_open)
    with pytest.raises(ValueError):
        workflow._q2_reference_target_paths(tmp_path, contract_ref)


@pytest.mark.parametrize('change', ['missing_completion', 'timeout', 'integrity', 'wrong_contract',
                                  'nomination_hash', 'nomination_payload', 'bad_branch', 'open_confirmation'])
def test_reference_branch_rejects_incomplete_changed_or_unsealed_authority(
        tmp_path, workflow, change):
    _, contract_ref, job, path = label_job_fixture(tmp_path, workflow)
    if change == 'missing_completion':
        del job['completed']
    elif change == 'timeout':
        job['status'] = 'INCOMPLETE'
    elif change == 'integrity':
        job['integrity_errors'] = ['source ambiguity']
    elif change == 'wrong_contract':
        job['contract']['sha256'] = '0' * 64
    elif change == 'nomination_hash':
        job['discovery_nomination']['sha256'] = '0' * 64
    elif change == 'nomination_payload':
        job['discovery']['status'] = 'PASS'
    elif change == 'bad_branch':
        job['reference_branch'] = 'qualification48'
    else:
        job['confirmation'] = {'status': 'PASS'}
    write(path, job)
    with pytest.raises((ValueError, KeyError)):
        workflow._q2_reference_target_paths(tmp_path, contract_ref)


@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_reference_main_passes_completed_job_to_independent_analyzer_validation(
        tmp_path, monkeypatch, workflow, version):
    document, contract_ref, _, path = label_job_fixture(tmp_path, workflow, version=version)
    monkeypatch.setattr(workflow, 'validate_acquisition_layout', lambda *args: tmp_path)
    monkeypatch.setattr(workflow.analysis, '_q1_contract', lambda *args: document)
    seen = []

    def evaluate(paths, output, **kwargs):
        seen.append((paths, output, kwargs))
        return {'version': version, 'status': 'COMPLETE_DIAGNOSTIC'}

    monkeypatch.setattr(workflow.analysis, 'evaluate_q1_direction_references', evaluate)
    monkeypatch.setattr(sys, 'argv', ['evaluate_q1.py', 'references', '--contract', contract_ref['path']])
    result = workflow.main()
    assert result['status'] == 'COMPLETE_DIAGNOSTIC'
    assert seen == [([tmp_path / 'analysis/discovery_targets/targets.json'], tmp_path / 'analysis/references',
                     {'contract_path': Path(contract_ref['path']), 'qualification_result_path': path})]


@pytest.mark.parametrize('discovery_status', ['PASS', 'FAIL', 'EVIDENCE_UNAVAILABLE'])
@pytest.mark.parametrize('version', q.analysis.Q2_VERSIONS)
def test_label_main_publishes_exact_completion_receipts_and_keeps_detector_status(
        tmp_path, monkeypatch, workflow, discovery_status, version):
    document = contract(version)
    contract_ref = write(tmp_path / 'contract.json', document)
    write(tmp_path / 'study_manifest.json', {'version': version, 'contract': contract_ref})
    monkeypatch.setattr(workflow, 'validate_acquisition_layout', lambda *args: tmp_path)
    monkeypatch.setattr(workflow.analysis, '_q1_contract', lambda *args: document)
    seen = []

    def freeze_labels(_manifest, output, *, partition, **kwargs):
        seen.append(('labels', partition))
        output.mkdir()
        write(output / 'labels_manifest.json', {'partition': partition})

    def freeze_targets(_manifest, output, *, partition, **kwargs):
        seen.append(('targets', partition))
        output.mkdir()
        write(output / 'targets.json', {'partition': partition})

    def evaluate(_labels, output, *, nomination_manifest=None):
        partition = 'discovery' if nomination_manifest is None else 'confirmation'
        seen.append(('evaluate', partition))
        result, _, _ = evaluation_fixture(
            tmp_path, contract_ref, partition=partition,
            status=discovery_status if partition == 'discovery' else 'FAIL', nomination=nomination_manifest)
        return result

    monkeypatch.setattr(workflow.q1_study, 'freeze_q1_study_labels', freeze_labels)
    monkeypatch.setattr(workflow.analysis, 'freeze_q1_direction_targets', freeze_targets)
    monkeypatch.setattr(workflow.q1_study, 'evaluate_q1_study_partition', evaluate)
    monkeypatch.setattr(sys, 'argv', ['evaluate_q1.py', 'labels', '--contract', contract_ref['path']])
    result = workflow.main()
    assert result['completed'] is True and result['integrity_errors'] == []
    assert result['discovery_nomination'] == workflow.receipt(
        tmp_path / 'analysis/discovery_nomination/nomination.json')
    assert result['status'] == ('FAIL' if discovery_status == 'PASS' else discovery_status)
    expected_partitions = ['discovery', 'confirmation'] if discovery_status == 'PASS' else ['discovery']
    assert seen == [(stage, partition) for partition in expected_partitions
                    for stage in ('labels', 'targets', 'evaluate')]
    paths, _ = workflow._q2_reference_target_paths(tmp_path, contract_ref)
    assert len(paths) == (2 if discovery_status == 'PASS' else 1)
    assert result['pilot_released'] is False


def test_old_q1_reference_orchestration_keeps_its_original_two_manifest_api(tmp_path, monkeypatch, workflow):
    document = {'version': q.analysis.Q1_VERSION}
    contract_ref = write(tmp_path / 'contract.json', document)
    monkeypatch.setattr(workflow, 'validate_acquisition_layout', lambda *args: tmp_path)
    monkeypatch.setattr(workflow.analysis, '_q1_contract', lambda *args: document)
    seen = []
    monkeypatch.setattr(workflow.analysis, 'evaluate_q1_direction_references',
                        lambda paths, output, **kwargs: seen.append((paths, kwargs)) or {'status': 'PASS'})
    monkeypatch.setattr(sys, 'argv', ['evaluate_q1.py', 'references', '--contract', contract_ref['path']])
    assert workflow.main()['status'] == 'PASS'
    assert seen == [([tmp_path / 'analysis/discovery_targets/targets.json',
                      tmp_path / 'analysis/confirmation_targets/targets.json'],
                     {'contract_path': Path(contract_ref['path'])})]


def test_label_job_completion_is_not_published_after_integrity_exception(tmp_path, monkeypatch, workflow):
    document = contract()
    contract_ref = write(tmp_path / 'contract.json', document)
    write(tmp_path / 'study_manifest.json', {'version': q.analysis.Q2_VERSION, 'contract': contract_ref})
    monkeypatch.setattr(workflow, 'validate_acquisition_layout', lambda *args: tmp_path)
    monkeypatch.setattr(workflow.analysis, '_q1_contract', lambda *args: document)

    def reject(*args, **kwargs):
        raise ValueError('input integrity error')

    monkeypatch.setattr(workflow.q1_study, 'freeze_q1_study_labels', reject)
    monkeypatch.setattr(sys, 'argv', ['evaluate_q1.py', 'labels', '--contract', contract_ref['path']])
    with pytest.raises(ValueError, match='integrity'):
        workflow.main()
    assert (tmp_path / 'analysis/label_job_started.json').exists()
    assert not (tmp_path / 'analysis/label_job.json').exists()
