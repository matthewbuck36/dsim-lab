"""Fresh Q2 acquisition routing; synthetic manifests and real runner dry-runs.

No recording, numerical field evaluation, confirmation read or ROS dispatch.
Existing analytical owners independently test full source/geometry contracts.
"""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import sys

import pytest
import yaml

REPOSITORY = Path(__file__).resolve().parents[4]
TOOLS = REPOSITORY / 'docs/codex/gesc_gaussian/v2/tools'
Q2_VERSIONS = ('q2-primary-shadow-v1', 'q2-primary-shadow-v2')


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(TOOLS))
    return tuple(importlib.import_module(name) for name in (
        'q1_acquisition_layout', 'freeze_q1_contract', 'acquire_q1'))


def write(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document))
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def contract_fixture(tmp_path, monkeypatch, modules, version=Q2_VERSIONS[0]):
    layout, freeze, acquire = modules
    root = tmp_path / 'qualification' / version.replace('-', '_')
    monkeypatch.setattr(layout, 'BASE', root.parent)
    monkeypatch.setattr(layout, 'ACQUISITION_ROOTS', {**layout.ACQUISITION_ROOTS, version: root})
    scenario = layout.acquisition_scenario(version)
    suite = freeze.load_suite(scenario)
    resolved, unsupported = freeze.expand_suite(suite)
    assert not unsupported
    contract = acquire.analysis.q2_contract_fields(version)
    contract.update(acquisition_version=version, acquisition_root=str(root),
                    scenario=freeze.receipt(scenario),
                    execution={**suite['execution'], 'runs_root': str(root / 'runs'),
                               'outer_acquisition_ceiling_sec': 1200., 'ros_domain_id': 191},
                    runs=freeze.build_acquisition_runs(suite, resolved, root, version))
    return contract, root / 'preflight/contract.json', root


def test_q2_scenario_changes_only_fixed_identity_population_and_direction_policy(modules):
    layout, freeze, _ = modules
    before = yaml.safe_load(freeze.SCENARIO.read_text())
    after = yaml.safe_load(layout.acquisition_scenario(layout.Q2_SCIENCE_VERSION).read_text())
    expected = deepcopy(before)
    for key in ('suite_id',):
        expected[key] = expected[key].replace('q1_', 'q2_')
    expected['execution']['runs_root'] = str(layout.acquisition_root(layout.Q2_SCIENCE_VERSION) / 'runs')
    expected['metadata']['experiment_version'] = layout.Q2_SCIENCE_VERSION
    expected['metadata']['operator_notes'] = expected['metadata']['operator_notes'].replace(
        'seeds26090911/12, sealed confirmation26090913/14',
        'seeds26090921/22, sealed confirmation26090923/24')
    expected['frozen_profile']['profile_id'] = 'q2_primary_shadow_v1'
    expected['frozen_profile']['launch_overrides']['v2_direction_policy'] = 'moving_cycle_coherence_v1'
    for index, case in enumerate(expected['cases']):
        case['case_id'] = case['case_id'].replace('q1_', 'q2_')
        case['seeds'] = [26090921 + index]
    assert after == expected
    assert after['metadata']['experiment_version'] == layout.Q2_SCIENCE_VERSION
    assert after['execution']['simulation_duration_sec'] == 125.
    assert after['execution']['wall_timeout_sec'] + after['execution']['shutdown_grace_sec'] == 225.
    assert after['execution']['run_timeout_sec'] == 0.


def test_corrected_q2_profile_preserves_all_controls_and_original_default(modules):
    layout, _, acquire = modules
    original = layout.acquisition_scenario(layout.Q2_SCIENCE_VERSION).read_text()
    corrected = layout.acquisition_scenario(layout.Q2_CORRECTED_VERSION).read_text()
    expected = original.replace('q2_primary_shadow_v1', 'q2_primary_shadow_v2').replace(
        'q2-primary-shadow-v1', 'q2-primary-shadow-v2').replace(
        'seeds26090921/22, sealed confirmation26090923/24',
        'seeds26090931/32, sealed confirmation26090933/34')
    for old, new in zip(range(26090921, 26090925), range(26090931, 26090935)):
        expected = expected.replace(str(old), str(new))
    assert corrected == expected
    assert layout.Q2_VERSIONS == Q2_VERSIONS
    assert acquire.analysis.q2_contract_fields() == acquire.analysis.q2_contract_fields(layout.Q2_SCIENCE_VERSION)
    before = acquire.analysis.q2_contract_fields(layout.Q2_SCIENCE_VERSION)
    after = acquire.analysis.q2_contract_fields(layout.Q2_CORRECTED_VERSION)
    for key in ('direction_policy', 'expected_build', 'reference', 'reference_branch_rule',
                'runtime_source_checkpoint'):
        assert before[key] == after[key]
    assert 'prior_acquisition_closure' not in before
    assert after['prior_acquisition_closure']['sha256'] == (
        '672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02')
    assert after['acquisition_path_correction_checkpoint']['sha256'] == (
        '670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44')


@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_actual_q2_runner_dry_run_matches_all_four_frozen_previews(modules, version, tmp_path):
    layout, freeze, acquire = modules
    scenario = layout.acquisition_scenario(version)
    suite = freeze.load_suite(scenario)
    resolved, unsupported = freeze.expand_suite(suite)
    assert not unsupported
    root = tmp_path / version.replace('-', '_')
    planned = freeze.build_acquisition_runs(suite, resolved, root, version)
    assert [run['seed'] for run in planned] == [row[0] for row in layout.acquisition_population(version)]
    assert [run['visible'] for run in planned] == [True, False, False, False]
    assert [seed for values in acquire.analysis.qualification_partition_seeds(version).values()
            for seed in values] == [run['seed'] for run in planned]
    policy = acquire.analysis.q2_contract_fields(version)['direction_policy']
    for run in planned:
        actual = freeze.runner.execute_suite(
            scenario, 'mattb', case_ids=[run['case_id']], runs_root=root / 'runs',
            gui=run['visible'], dry_run=True, run_id=run['run_id'])['runs'][0]
        assert actual['launch_argv'] == run['launch_argv']
        assert actual['metadata'] == run['metadata_preview']
        assert actual['metadata']['experiment_version'] == version
        assert actual['metadata']['scenario_runner']['direction_policy'] == policy
        command = actual['record_argv'][:]
        command[command.index('--metadata-input') + 1] = run['record_argv_template'][
            run['record_argv_template'].index('--metadata-input') + 1]
        assert command == run['record_argv_template']
        assert command[command.index('--sim-duration-sec') + 1] == '125.0'
        assert 'v2_direction_policy:=moving_cycle_coherence_v1' in actual['launch_argv']


@pytest.mark.parametrize('change', ['science', 'root', 'build', 'scenario', 'seed',
                                   'case', 'visibility', 'imports', 'recovery', 'unknown_version'])
@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_rejects_profile_or_identity_change_before_any_output(tmp_path, monkeypatch, modules, change, version):
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    layout = modules[0]
    assert layout.validate_acquisition_layout(contract, path) == root
    if change == 'science': contract['version'] = layout.SCIENCE_VERSION
    elif change == 'root': contract['acquisition_root'] = str(root.parent / 'other')
    elif change == 'build': contract['expected_build'] = str(layout.BUILD_BASE / 'initial')
    elif change == 'scenario': contract['scenario']['path'] = str(modules[1].SCENARIO)
    elif change == 'seed': contract['runs'][0]['seed'] = 26090911
    elif change == 'case': contract['runs'][0]['case_id'] = 'q1_discovery_residence'
    elif change == 'visibility': contract['runs'][1]['visible'] = True
    elif change == 'unknown_version': contract['acquisition_version'] += '-recovery1'
    else: contract[change] = {}
    with pytest.raises(ValueError):
        layout.validate_acquisition_layout(contract, path)
    assert not root.exists()


@pytest.mark.parametrize('artifact', ['runs', 'acquisition', 'study_manifest.json',
                                    'acquisition_closed.json', 'contract', 'other_seed', 'other_id'])
@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_nonuse_check_reads_only_identity_manifests_and_rejects_reuse(
        tmp_path, monkeypatch, modules, artifact, version):
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    layout = modules[0]
    layout.require_unused_q2_acquisition(path, version=version)
    # A sealed arbitrary recording would fail if accidentally opened.
    recording = root.parent / 'old' / 'runs' / 'sealed.db3'
    recording.parent.mkdir(parents=True)
    recording.write_bytes(b'not JSON and not a permitted metadata input')
    if artifact in ('other_seed', 'other_id'):
        row = {'seed': contract['runs'][2]['seed']} if artifact == 'other_seed' else {'run_id': contract['runs'][0]['run_id']}
        write(root.parent / 'old' / 'preflight/contract.json', {'runs': [row]})
    elif artifact == 'contract': write(path, contract)
    elif artifact in ('runs', 'acquisition'): (root / artifact).mkdir(parents=True)
    else: write(root / artifact, {})
    with pytest.raises(ValueError, match='already'):
        layout.require_unused_q2_acquisition(path, version=version)


@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_reserved_contract_is_allowed_only_for_initial_acquisition(tmp_path, monkeypatch, modules, version):
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    write(path, contract)
    modules[0].require_unused_q2_acquisition(path, version=version, allow_reserved_contract=True)
    assert not (root / 'acquisition').exists()


def test_corrected_nonuse_keeps_original_used_namespace_closed(tmp_path, monkeypatch, modules):
    layout, _, _ = modules
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, layout.Q2_CORRECTED_VERSION)
    old_root = root.parent / 'q2_primary_shadow_v1'
    monkeypatch.setattr(layout, 'ACQUISITION_ROOTS', {
        **layout.ACQUISITION_ROOTS, layout.Q2_SCIENCE_VERSION: old_root})
    old_path = old_root / 'preflight/contract.json'
    write(old_path, {'runs': [{'seed': 26090921, 'run_id':
                             'q2-primary-shadow-v1-discovery-residence-26090921'}]})
    write(old_root / 'acquisition_closed.json', {'status': 'CLOSED_INCOMPLETE'})
    layout.require_unused_q2_acquisition(path, version=layout.Q2_CORRECTED_VERSION)
    with pytest.raises(ValueError, match='already'):
        layout.require_unused_q2_acquisition(old_path)
    # Version selection cannot silently redirect a corrected contract to old identities.
    contract['acquisition_version'] = layout.Q2_SCIENCE_VERSION
    with pytest.raises(ValueError):
        layout.validate_acquisition_layout(contract, path)
    with pytest.raises(ValueError, match='version'):
        layout.require_unused_q2_acquisition(path, version='q2-primary-shadow-v3')


@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_acquirer_uses_explicit_build_before_output_and_each_dispatch(
        tmp_path, monkeypatch, modules, version):
    layout, _, acquire = modules
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    ref = write(path, contract)
    write(root / 'preflight/dispatch_release.json', {'status': 'RELEASED', 'contract': ref})
    monkeypatch.setenv('ROS_DOMAIN_ID', '191')
    monkeypatch.setattr(acquire.analysis, '_q1_contract', lambda ref: contract)
    calls = []
    def environment(document, release, *, expected_build):
        assert expected_build == layout.acquisition_expected_build(version)
        calls.append(expected_build)
    monkeypatch.setattr(acquire, 'verify_environment', environment)
    dispatch = []
    def execute(scenario, **kwargs):
        dispatch.append(kwargs)
        return {'runs': [{'run_id': contract['runs'][0]['run_id'], 'classification': {'passed': False}}]}
    monkeypatch.setattr(acquire, 'execute_suite', execute)
    monkeypatch.setattr(sys, 'argv', ['acquire', '--contract', str(path)])
    assert acquire.main() == 1
    assert len(calls) == 2 and len(dispatch) == 1
    result = json.loads((root / 'acquisition/acquisition.json').read_text())
    assert result['status'] == 'INCOMPLETE' and result['newly_dispatched'] == 1
    assert result['scientific_confirmation_opened'] is False
    assert not (root / 'study_manifest.json').exists()
    # The same acquisition is never an automatic retry.
    with pytest.raises(ValueError, match='already'):
        acquire.main()
    assert len(dispatch) == 1


@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_acquirer_environment_rejection_precedes_output_or_dispatch(tmp_path, monkeypatch, modules, version):
    _, _, acquire = modules
    contract, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    ref = write(path, contract)
    write(root / 'preflight/dispatch_release.json', {'status': 'RELEASED', 'contract': ref})
    monkeypatch.setenv('ROS_DOMAIN_ID', '191')
    monkeypatch.setattr(acquire.analysis, '_q1_contract', lambda ref: contract)
    def reject(*args, expected_build):
        assert str(expected_build) == contract['expected_build']
        raise ValueError('installed Q2 binding differs')
    monkeypatch.setattr(acquire, 'verify_environment', reject)
    monkeypatch.setattr(acquire, 'execute_suite', lambda *a, **kw: pytest.fail('unexpected dispatch'))
    monkeypatch.setattr(sys, 'argv', ['acquire', '--contract', str(path)])
    with pytest.raises(ValueError, match='binding'):
        acquire.main()
    assert not (root / 'acquisition').exists()


def test_old_acquirer_environment_call_keeps_original_default(modules, monkeypatch):
    _, _, acquire = modules
    calls = []
    monkeypatch.setattr(acquire, 'verify_environment', lambda *args: calls.append(args))
    old = {'version': modules[0].SCIENCE_VERSION}
    acquire.verify_acquisition_environment(old, {})
    assert calls == [(old, {})]


@pytest.mark.parametrize('version,receipt_failure', [
    (Q2_VERSIONS[0], None), (Q2_VERSIONS[1], None),
    (Q2_VERSIONS[1], 'prior_acquisition_closure'),
    (Q2_VERSIONS[1], 'acquisition_path_correction_checkpoint')])
def test_q2_freezer_merges_prospective_slots_and_binds_explicit_build(
        tmp_path, monkeypatch, modules, version, receipt_failure):
    layout, freeze, acquire = modules
    _, path, root = contract_fixture(tmp_path, monkeypatch, modules, version)
    additions = acquire.analysis.q2_contract_fields(version)
    real_read = Path.read_text
    def read(source, *args, **kwargs):
        if str(source).endswith('/m1a_labels_v1/geometry_1.json'):
            return json.dumps({'basins': []})
        if str(source).endswith('/m1a_labels_v1_recovery1/labels.json'):
            return json.dumps({'numerical_geometry_recovery': {
                'recovery_manifest_path': '/synthetic/recovery.json',
                'original_analyzer_snapshot_path': '/synthetic/original.py'}})
        return real_read(source, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', read)
    monkeypatch.setattr(freeze, 'collect_source_paths', lambda version: set())
    def reference(source):
        for name in ('runtime_source_checkpoint', 'prior_acquisition_closure',
                     'acquisition_path_correction_checkpoint'):
            if name in additions and str(source) == additions[name]['path']:
                return ({**additions[name], 'sha256': '0' * 64}
                        if name == receipt_failure else additions[name])
        return {'path': str(source), 'sha256': '0' * 64}
    monkeypatch.setattr(freeze, 'receipt', reference)
    monkeypatch.setattr(freeze.subprocess, 'check_output',
                        lambda cmd, **kw: 'feature/gesc-gaussian-robustness-v2\n' if 'branch' in cmd else '0' * 40 + '\n')
    builds = []
    def installed(*, expected_build):
        builds.append(expected_build)
        return {'synthetic': True}
    monkeypatch.setattr(freeze, 'installed_entry_points', installed)
    from ros_esc.plotting_scripts import q1_study
    checks = []
    monkeypatch.setattr(q1_study, 'verify_q1_geometry', lambda contract, run: checks.append(run['seed']))
    monkeypatch.setattr(sys, 'argv', ['freeze', '--acquisition-version', version])
    if receipt_failure:
        with pytest.raises(ValueError, match='closure/checkpoint'):
            freeze.main()
        assert not path.exists() and not checks
        return
    freeze.main()
    frozen = json.loads(path.read_text())
    assert all(frozen[key] == value for key, value in additions.items())
    assert len(frozen['planned_reference_slots']) == 48
    assert all(slot['source_identity_status'] == 'SEALED'
               and 'source_stamp_ns' not in slot and 'target_ns' not in slot
               for slot in frozen['planned_reference_slots'] if slot['partition'] == 'confirmation')
    assert frozen['execution']['outer_acquisition_ceiling_sec'] == 1200.
    assert frozen['execution']['recorder_process_ceiling_sec'] == 240.
    assert builds == [layout.acquisition_expected_build(version)]
    assert checks == [row[0] for row in layout.acquisition_population(version)]
    assert 'imports' not in frozen and 'recovery' not in frozen
    assert not (root / 'acquisition').exists()


def test_corrected_freeze_binds_new_amendment_without_changing_original_docs(modules, monkeypatch):
    layout, freeze, _ = modules
    monkeypatch.setattr(freeze.subprocess, 'check_output', lambda *a, **kw: b'')
    old = freeze.collect_source_paths(layout.Q2_SCIENCE_VERSION)
    corrected = freeze.collect_source_paths(layout.Q2_CORRECTED_VERSION)
    amendment = TOOLS.parent / 'q2_acquisition_path_correction_plan.md'
    assert corrected == old | {amendment}


@pytest.mark.parametrize('version', Q2_VERSIONS)
def test_q2_freezer_rejects_output_redirection_before_scenario_load(tmp_path, monkeypatch, modules, version):
    layout, freeze, _ = modules
    monkeypatch.setattr(sys, 'argv', ['freeze', '--acquisition-version', version,
                                     '--output', str(tmp_path / 'contract.json')])
    monkeypatch.setattr(freeze, 'load_suite', lambda *a: pytest.fail('unexpected scenario load'))
    with pytest.raises(ValueError, match='preflight'):
        freeze.main()
