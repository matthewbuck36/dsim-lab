"""V8 workflow selection through existing owners with finite synthetic inputs.

Prepare V7 and V8 once each with numerical/graph operations replaced. Every
fault receives a deep copy and restored temporary files, never another field
derivation, bag read, ROS graph or acquisition.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.plotting_scripts import q1_study
from ros_esc.scenario_runner import aggregate_field_truth as truth
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import LAUNCH_OVERRIDES
from test_m4_workflow import acquisition, save, workflow
import m4_science_job
from test_m4_v5_versions import synthetic_topology


VERSION = 'm4-pilot-v8'
PREVIOUS = 'm4-pilot-v7'
EARLIER = tuple(f'm4-pilot-v{number}' for number in range(1, 8))


def unavailable(*args, **kwargs):
    pytest.fail('workflow source fixture cannot start a process or field model')


@pytest.fixture(scope='module')
def _prepared_versions(tmp_path_factory):
    """One real schema expansion per version, with existing numerical mocks."""
    directory = tmp_path_factory.mktemp('m4_v8_workflow')
    marker = save(directory/'source.json', {'scope': 'synthetic workflow fixture'})
    selected = scenario.v6_controller_configuration()
    sources = [marker, workflow.receipt(runner.GESC_CONTROLLER),
               workflow.receipt(selected['path'])]
    primary_sources = scenario._template('primary')['cases'][0]['sources']
    calls = []

    def topology(sources, start, bounds, disturbance, *args):
        geometry = 'primary' if sources == primary_sources else 'secondary'
        calls.append((geometry, deepcopy(sources), deepcopy(start),
                      deepcopy(bounds), deepcopy(disturbance), args))
        return synthetic_topology(geometry, disturbance)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', directory/'pilot')
        patch.setattr(workflow.subprocess, 'check_output',
                      lambda *args, **kwargs: 'feature/gesc-gaussian-robustness-v2\n')
        patch.setattr(workflow.subprocess, 'Popen', unavailable)
        patch.setattr(workflow, 'collect_sources', lambda: deepcopy(sources))
        patch.setattr(workflow, 'geometry_context', lambda *args: dict(
            label_geometry=marker, geometry_recovery=marker, geometry_receipts=[marker]))
        patch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
        patch.setattr(workflow, 'installed_entry_points', lambda **kwargs: {'fixture': 'installed'})
        patch.setenv('ROS_DOMAIN_ID', '200')
        patch.setattr(truth, 'derive_two_source_topology_qualification', topology)
        patch.setattr(truth, '_model', unavailable)
        patch.setattr(truth, 'validate_two_source_topology_qualification',
                      lambda record, *args, **kwargs: deepcopy(record))
        patch.setattr(q1_study, 'verify_geometry_receipts', lambda *args: True)
        contracts = {version: workflow.read_json(workflow.prepare(version)['path'])
                     for version in (PREVIOUS, VERSION)}
    files = {path: path.read_bytes() for path in directory.rglob('*') if path.is_file()}
    directories = {directory, *(path for path in directory.rglob('*') if path.is_dir())}
    return dict(directory=directory, contracts=contracts, calls=calls, files=files,
                directories=directories)


@pytest.fixture
def prepared(_prepared_versions, monkeypatch):
    baseline = _prepared_versions
    # Only this module's temporary tree is restored; retained/repository files
    # are never destinations. A contract mutation cannot poison the next case.
    for path in baseline['directory'].rglob('*'):
        if path.is_file() and path not in baseline['files']:
            path.unlink()
    for path in sorted(baseline['directory'].rglob('*'), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir() and path not in baseline['directories']:
            path.rmdir()
    for path, contents in baseline['files'].items():
        path.write_bytes(contents)
    contract = deepcopy(baseline['contracts'][VERSION])
    monkeypatch.setattr(scenario, 'PILOT_ROOT', baseline['directory']/'pilot')
    monkeypatch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kwargs: {'fixture': 'installed'})
    monkeypatch.setattr(workflow.subprocess, 'Popen', unavailable)
    monkeypatch.setattr(workflow.subprocess, 'check_output',
                        lambda *args, **kwargs: 'feature/gesc-gaussian-robustness-v2\n')
    monkeypatch.setattr(truth, '_model', unavailable)
    monkeypatch.setattr(truth, 'derive_two_source_topology_qualification', unavailable)
    return contract


def freeze(contract):
    """Update the temporary witness so faults reach their intended predicate."""
    Path(contract['contract_path']).write_text(json.dumps(contract, sort_keys=True))


def substitute_identity(value, previous, current, previous_root, current_root):
    """Replace declared experiment/path identities, keeping the V6 JSON/profile."""
    if isinstance(value, dict):
        return {key: substitute_identity(item, previous, current, previous_root, current_root)
                for key, item in value.items()}
    if isinstance(value, list):
        return [substitute_identity(item, previous, current, previous_root, current_root)
                for item in value]
    if isinstance(value, str):
        for before, after in (
            (previous_root, current_root),
            (previous['case_id'], current['case_id']),
            (previous['resolved_scenario']['case_key'], current['resolved_scenario']['case_key']),
            (previous['resolved_scenario']['case_key'][:12], current['resolved_scenario']['case_key'][:12]),
            ('m4_pilot_v7', 'm4_pilot_v8'),
            (PREVIOUS, VERSION),
        ):
            value = value.replace(before, after)
    return value


def test_preparation_retains_all_sixteen_v7_controls_topologies_and_budgets(
        prepared, _prepared_versions):
    contract = prepared
    previous = _prepared_versions['contracts'][PREVIOUS]
    calls = _prepared_versions['calls']
    selected = scenario.v6_controller_configuration()
    assert len(calls) == 8 and calls[:4] == calls[4:]
    assert [call[0] for call in calls[4:]] == ['secondary']*3+['primary']
    assert calls[5][4]['sensor_noise']['std_dev'] == .015
    assert calls[6][4]['sensor_delay_sec'] == calls[6][4]['pose_delay_sec'] == .1
    assert contract['version'] == contract['experiment_version'] == VERSION
    assert contract['method_version'] == 'm4-pilot-v1'
    assert contract['controller_configuration'] == previous['controller_configuration'] == selected
    assert selected['profile_id'] == 'm4_gain_half_control_v6'
    assert selected['sha256'] == 'e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606'
    assert contract['execution'] == dict(runs_root=str(Path(contract['root'])/'runs'),
        ros_domain_id=200, recording_sec=720., case_timeout_sec=900., suite_timeout_sec=15300.,
        cleanup_reserve_sec=30., science_budget_sec=900., shutdown_grace_sec=45.,
        process_ownership_mode='subreaper_group_v3')
    assert contract['science'] == previous['science'] == dict(
        targets_sec=[15+30*k for k in range(24)], labels_sec=120., references_sec=45.,
        summary_sec=10., freeze_report_sec=20., maximum_observations=40000)
    assert set(contract['topology_receipts']) == {'primary_nominal', 'nominal', 'noise', 'delay'}
    for name, receipt in contract['topology_receipts'].items():
        assert workflow.read_json(receipt['path']) == workflow.read_json(previous['topology_receipts'][name]['path'])
    assert len(contract['runs']) == 16
    original = deepcopy(contract)
    assert workflow.verify_frozen(contract) and contract == original
    for index, (old, row) in enumerate(zip(previous['runs'], contract['runs'])):
        block = index//4
        arm = 'ABCD'[index % 4]
        condition = ('nominal', 'nominal', 'noise', 'delay')[block]
        partition = 'development' if block == 0 else 'holdout'
        seed = 26090801+block
        assert row['slot'] == index+1 and row['arm'] == arm and row['seed'] == seed
        assert row['visible'] is (block == 0)
        assert row['case_id'] == f'm4_v8_{partition}_{condition}_{arm}_{seed}'
        assert row['run_id'] == f'm4-pilot-v8-slot{index+1:02d}-{arm}-{seed}'
        resolved = row['resolved_scenario']
        assert resolved == substitute_identity(old['resolved_scenario'], old, row,
                                               previous['root'], contract['root'])
        assert row['launch_argv'] == substitute_identity(old['launch_argv'], old, row,
                                                       previous['root'], contract['root'])
        assert row['runner_argv'] == substitute_identity(old['runner_argv'], old, row,
                                                       previous['root'], contract['root'])
        overrides = resolved['algorithm']['launch_overrides']
        assert overrides['controller_config_filepath'] == selected['path']
        assert resolved['frozen_profile']['profile_id'] == selected['profile_id']
        if arm in 'BD':
            assert overrides['centroid_invalid_status_heartbeat_enabled'] is True
            assert [overrides[key] for key in ('centroid_window_sec', 'centroid_epsilon_m',
                                              'centroid_maximum_radius_m')] == [6., .18, .5]
        else:
            assert 'centroid_invalid_status_heartbeat_enabled' not in overrides
        assert overrides['convergence_metric_mode'] == ('centroid_two_block_v2' if arm in 'BD' else 'pde_mean_v1')
        assert overrides['continuous_search_mode'] == ('rolling_gesc_v2' if arm in 'CD' else 'stationary_v1')
        recovery = resolved['success']['staged_recovery']
        assert {key: recovery[key] for key in ('stage_a_timeout_sec', 'post_stage_a_timeout_sec',
            'global_proximity_radius_m', 'convergence_to_global_min_m', 'convergence_to_local_max_m',
            'fill_to_convergence_max_m')} == dict(stage_a_timeout_sec=360., post_stage_a_timeout_sec=300.,
                global_proximity_radius_m=.5, convergence_to_global_min_m=.75,
                convergence_to_local_max_m=.6, fill_to_convergence_max_m=.5)
        metadata = runner.build_metadata(resolved, 'mattb', VERSION, '', run_id=row['run_id'])
        old_metadata = runner.build_metadata(old['resolved_scenario'], 'mattb', PREVIOUS, '', run_id=old['run_id'])
        assert metadata == substitute_identity(old_metadata, old, row, previous['root'], contract['root'])
        assert metadata['parameter_files'].count(selected['path']) == 1
        assert str(runner.GESC_CONTROLLER) not in metadata['parameter_files']


def test_prepared_receipt_is_complete_but_has_no_acquisition_or_replacement(prepared, _prepared_versions):
    root = Path(prepared['root'])
    receipt = workflow.read_json(root/'preflight/prepared.json')
    assert receipt['status'] == 'PREPARED' and receipt['acquisition_started'] is False
    assert receipt['contract'] == workflow.receipt(prepared['contract_path'])
    assert not (root/'acquisition').exists() and not (root/'runs').exists()
    with pytest.raises(FileExistsError):
        workflow.prepare(VERSION)
    assert len(_prepared_versions['calls']) == 8


@pytest.mark.parametrize('slot', range(16))
def test_each_row_rejects_launch_only_dwell_divergence(prepared, slot):
    row = prepared['runs'][slot]
    assert 'convergence_confirmation_dwell_sec:=6.0' in row['launch_argv']
    row['launch_argv'] = ['convergence_confirmation_dwell_sec:=7.0' if value.startswith(
        'convergence_confirmation_dwell_sec:=') else value for value in row['launch_argv']]
    freeze(prepared)
    with pytest.raises(ValueError, match='launch argv'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('slot', range(16))
def test_each_row_rejects_old_controller_metadata(prepared, monkeypatch, slot):
    original = runner.build_metadata
    selected_run = prepared['runs'][slot]['run_id']

    def metadata(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs['run_id'] == selected_run:
            result['parameter_files'] = [str(runner.GESC_CONTROLLER)]
        return result

    monkeypatch.setattr(runner, 'build_metadata', metadata)
    with pytest.raises(ValueError, match='controller metadata'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('fault', ['old_and_selected', 'duplicate_selected'])
def test_late_holdout_rejects_ambiguous_controller_metadata(prepared, monkeypatch, fault):
    original = runner.build_metadata
    target = prepared['runs'][-1]['run_id']
    selected = prepared['controller_configuration']['path']

    def metadata(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs['run_id'] == target:
            result['parameter_files'] = ([str(runner.GESC_CONTROLLER), selected]
                if fault == 'old_and_selected' else [selected, selected])
        return result

    monkeypatch.setattr(runner, 'build_metadata', metadata)
    with pytest.raises(ValueError, match='controller metadata'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('slot', range(16))
def test_each_row_rejects_divergent_effective_controller(prepared, slot):
    prepared['runs'][slot]['resolved_scenario']['algorithm']['launch_overrides'][
        'controller_config_filepath'] = str(runner.GESC_CONTROLLER)
    freeze(prepared)
    with pytest.raises(ValueError, match='method differs'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('fault', ['missing', 'path', 'hash', 'profile'])
def test_controller_receipt_cannot_be_omitted_or_relabelled(prepared, fault):
    if fault == 'missing':
        prepared.pop('controller_configuration')
    else:
        key = {'path': 'path', 'hash': 'sha256', 'profile': 'profile_id'}[fault]
        prepared['controller_configuration'][key] = 'foreign'
    freeze(prepared)
    with pytest.raises(ValueError, match='controller configuration receipt'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('slot', range(16))
def test_even_consistent_extra_allowed_control_is_rejected(prepared, slot):
    row = prepared['runs'][slot]
    name = 'gaussian_fill_amplitude_min'
    assert name in LAUNCH_OVERRIDES
    path = Path(prepared['scenario']['path'])
    document = yaml.safe_load(path.read_text())
    raw = document['cases'][slot]
    assert raw['case_id'] == row['case_id']
    raw['algorithm']['launch_overrides'][name] = .2
    overrides = {**document['frozen_profile']['launch_overrides'],
                 **raw['algorithm']['launch_overrides']}
    row['resolved_scenario']['algorithm']['launch_overrides'] = overrides
    row['launch_argv'] = runner.build_launch_command(row['resolved_scenario'],
        cost_path=row['expected_cost_configuration']['path'], gui=row['visible'], run_id=row['run_id'])
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    prepared['scenario'] = workflow.receipt(path)
    freeze(prepared)
    with pytest.raises(ValueError, match='method differs'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('earlier', EARLIER)
@pytest.mark.parametrize('field', ['root', 'experiment', 'run_id', 'summary', 'suite'])
def test_prior_version_context_cannot_replace_any_v8_contract_boundary(prepared, earlier, field):
    identity = scenario.experiment_identity(earlier)
    old_root = Path(identity['root'])
    if field == 'root':
        prepared['root'] = str(old_root)
    elif field == 'experiment':
        prepared['experiment_version'] = earlier
    elif field == 'run_id':
        prepared['runs'][-1]['run_id'] = scenario.experiment_run_id(prepared['runs'][-1], earlier)
    elif field == 'summary':
        prepared['runs'][-1]['summary_path'] = str(old_root/'acquisition/summary_16.yaml')
    else:
        prepared['runs'][-1]['resolved_scenario']['suite_id'] = identity['suite_id']
    freeze(prepared)
    with pytest.raises(ValueError, match='identity differs'):
        workflow.verify_frozen(prepared)


@pytest.mark.parametrize('field,value', [('method_version', 'm4-pilot-v8'),
                                      ('process_ownership_mode', 'subreaper_v2')])
def test_workflow_keeps_original_method_and_group_owner(prepared, field, value):
    destination = prepared['execution'] if field == 'process_ownership_mode' else prepared
    destination[field] = value
    freeze(prepared)
    with pytest.raises(ValueError, match='identity differs'):
        workflow.verify_frozen(prepared)


def test_source_collector_pins_both_controller_files_and_both_v8_amendments():
    paths = {row['path'] for row in workflow.collect_sources()}
    expected = {str(runner.GESC_CONTROLLER), str(scenario.V6_CONTROLLER_PATH), str(Path(__file__)),
        str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v8_stationary_causality_plan.md'),
        str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v8_stationary_causality_comparison_plan.md')}
    assert expected <= paths


@pytest.fixture
def development_ledger(prepared, monkeypatch):
    """Existing workflow with synthetic complete cases and one timed-out label job.

    The fixture represents prevalidated acquisition receipts; it does not run
    or bypass the actual recorder gate, and never launches a scientific child.
    """
    monkeypatch.setattr(workflow.time, 'monotonic', lambda: 100.)
    rows = [acquisition(prepared, slot) for slot in range(1, 5)]
    calls = []

    def unavailable_labels(argv, log_path, receipt_path, *, cap_sec, suite_end,
                           process_ownership_mode):
        assert argv[2] == 'labels' and argv[-2:] == ['--block', '0']
        assert argv[argv.index('--contract')+1] == prepared['contract_path']
        assert process_ownership_mode == 'subreaper_group_v3'
        calls.append((cap_sec, suite_end))
        record = dict(complete=False, integrity_passed=True, timed_out=True,
                      clean_termination=True, process_ownership_mode=process_ownership_mode)
        save(Path(receipt_path), record)
        Path(log_path).write_text('synthetic clean label timeout; no child launched\n')
        return record

    monkeypatch.setattr(m4_science_job, 'finite_science_job', unavailable_labels)
    block = workflow.analyze_block(prepared, 0, rows, 1000.)
    assert calls == [(120., 320.)]
    return rows, block


@pytest.mark.parametrize('earlier', EARLIER)
def test_fresh_acquisition_rejects_prior_experiment_even_after_rehash(prepared, earlier):
    row = acquisition(prepared, 16)
    record = {key: value for key, value in row.items() if key != 'receipt'}
    record['experiment_version'] = earlier
    record['run_id'] = scenario.experiment_run_id(prepared['runs'][-1], earlier)
    row = {**record, 'receipt': save(Path(prepared['root'])/'foreign_acquisition.json', record)}
    with pytest.raises(ValueError, match='different experiment'):
        workflow._verify_cases(prepared, [row], [16])


@pytest.mark.parametrize('earlier', EARLIER)
def test_fresh_scientific_rows_reject_prior_experiment(prepared, earlier):
    rows = [acquisition(prepared, 16)]
    result = workflow._science_unavailable(rows, 'synthetic absence')
    result[0]['experiment_version'] = earlier
    with pytest.raises(ValueError, match='different experiment'):
        workflow._verify_science_rows(prepared, result, rows)


def test_holdouts_release_once_after_exact_v8_behavior_failure_and_science_timeout(
        prepared, development_ledger):
    rows, block = development_ledger
    result = workflow.read_json(block['result']['path'])
    assert result['scientific_analysis_complete'] is False
    assert result['references_skipped'] == result['summary_skipped'] == 'no_complete_frozen_label_inputs'
    assert all(row['experiment_version'] == VERSION and row['behavior_passed'] is False
               and row['science_status'] == 'EVIDENCE_UNAVAILABLE' for row in result['runs'])
    released = workflow.release_holdouts(prepared, rows, block, 1000.)
    assert released['contract'] == workflow.receipt(prepared['contract_path'])
    assert released['development'] == [row['receipt'] for row in rows]
    assert released['analysis'] == block['receipt']
    assert released['holdouts'] == prepared['runs'][4:]
    assert [row['slot'] for row in released['holdouts']] == list(range(5, 17))
    assert released['source_files'] == prepared['source_files']
    assert released['tuning_performed'] is released['replacements_allowed'] is False
    assert released['scientific_pass_required'] is False
    with pytest.raises(FileExistsError):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('opened', ['summary', 'run', 'slot'])
def test_v8_release_refuses_any_started_final_holdout(prepared, development_ledger, opened):
    rows, block = development_ledger
    holdout = prepared['runs'][-1]
    root = Path(prepared['root'])
    if opened == 'summary':
        Path(holdout['summary_path']).write_text('synthetic started holdout')
    elif opened == 'run':
        (root/'runs'/'synthetic-date'/holdout['run_id']).mkdir(parents=True)
    else:
        save(root/'acquisition/slot_16.json', {'status': 'STARTED'})
    with pytest.raises(ValueError, match='sealed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (root/'preflight/holdout_release.json').exists()


@pytest.mark.parametrize('fault', ['old_science_version', 'old_science_run', 'foreign_cases',
                                  'incomplete_result', 'unsafe_acquisition'])
def test_v8_release_rejects_wrong_or_incomplete_bound_evidence(
        prepared, development_ledger, fault):
    rows, block = development_ledger
    root = Path(prepared['root'])
    result = workflow.read_json(block['result']['path'])
    payload = {key: value for key, value in block.items() if key != 'receipt'}
    if fault == 'old_science_version':
        result['runs'][-1]['experiment_version'] = PREVIOUS
    elif fault == 'old_science_run':
        result['runs'][-1]['run_id'] = scenario.experiment_run_id(prepared['runs'][3], PREVIOUS)
    elif fault == 'foreign_cases':
        payload['cases'] = [rows[0]['receipt']]*4
    elif fault == 'incomplete_result':
        result['complete'] = False
    else:
        rows[-1]['integrity_passed'] = False
        rows[-1]['status'] = 'INCOMPLETE'
    payload['result'] = save(root/'foreign_result.json', result)
    changed = {**payload, 'receipt': save(root/'foreign_block.json', payload)}
    with pytest.raises(ValueError):
        workflow.release_holdouts(prepared, rows, changed, 1000.)
    assert not (root/'preflight/holdout_release.json').exists()


@pytest.mark.parametrize('fault', [None, 'old_contract', 'old_prepared', 'holdout_initial_release',
                                  'missing_source_pins', 'unverified_archive'])
def test_v8_public_release_binds_current_contract_preparation_and_source(
        prepared, _prepared_versions, fault):
    root = Path(prepared['root'])
    old = _prepared_versions['contracts'][PREVIOUS]
    pins = {row['path']: row['sha256'] for row in prepared['source_files']}
    validation = dict(returncode=0, source_stable=True, before=deepcopy(pins), after=deepcopy(pins))
    checkpoint = dict(archive_verified=True)
    if fault == 'missing_source_pins':
        validation['before'] = validation['after'] = {}
    elif fault == 'unverified_archive':
        checkpoint['archive_verified'] = False
    release = dict(status='RELEASED', initial_slots=[1, 2, 3, 4],
        contract=workflow.receipt(prepared['contract_path']),
        prepared=workflow.receipt(root/'preflight/prepared.json'),
        source_validation=save(root/'synthetic_validation.json', validation),
        source_checkpoint=save(root/'synthetic_checkpoint.json', checkpoint))
    if fault == 'old_contract':
        release['contract'] = workflow.receipt(old['contract_path'])
    elif fault == 'old_prepared':
        release['prepared'] = workflow.receipt(Path(old['root'])/'preflight/prepared.json')
    elif fault == 'holdout_initial_release':
        release['initial_slots'] = [5, 6, 7, 8]
    save(root/'preflight/dispatch_release.json', release)
    if fault is None:
        assert workflow.verify_dispatch_release(prepared['contract_path']) == release
    else:
        with pytest.raises(ValueError):
            workflow.verify_dispatch_release(prepared['contract_path'])


def test_v8_final_report_retains_all_sixteen_slots_and_192_missing_direction_targets(
        prepared, development_ledger):
    rows, block = development_ledger
    rows.append(acquisition(prepared, 5, status='INCOMPLETE', integrity=False))
    rows.extend(acquisition(prepared, slot, status='UNSTARTED', integrity=False)
                for slot in range(6, 17))
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path'])
    assert result['experiment_version'] == VERSION and result['method_version'] == 'm4-pilot-v1'
    assert result['contract'] == workflow.receipt(prepared['contract_path'])
    assert result['block_receipts'] == [block['receipt']]
    assert [row['slot'] for row in result['slots']] == list(range(1, 17))
    assert result['slot_status_counts'] == {'COMPLETE': 4, 'INCOMPLETE': 1, 'UNSTARTED': 11}
    assert len(result['direction_rows']) == result['direction_scheduled_total'] == 192
    for slot in (3, 4, 7, 8, 11, 12, 15, 16):
        targets = [row for row in result['direction_rows'] if row['slot'] == slot]
        assert [row['number'] for row in targets] == list(range(1, 25))
        assert [row['offset_sec'] for row in targets] == [15+30*k for k in range(24)]
        assert all(row['run_id'] == prepared['runs'][slot-1]['run_id']
                   and row['exposure_status'] == 'analysis_unavailable'
                   and row['eligible'] is False for row in targets)
    assert result['direction']['counts']['scheduled'] == 144
    assert result['latency']['planned_pair_count'] == 6
    assert result['latency']['planned_endpoint_count'] == 12
    assert result['latency']['observed_endpoint_count'] == 0
    assert result['direction']['status'] == result['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['latency']['no_additional_errors'] is None
    report = Path(final['report']['path']).read_text()
    assert VERSION in report and 'All 192' in report and '0/12 observed endpoints; 0/6 pairs' in report
    workflow.check_receipts([final['receipt'], final['result'], final['report']])
    with pytest.raises(FileExistsError):
        workflow.finalize(prepared, rows, 1000.)


@pytest.mark.parametrize('fault', ['experiment', 'run_id', 'case_id'])
def test_v8_finalizer_rejects_rehashed_prior_version_acquisition(prepared, monkeypatch, fault):
    monkeypatch.setattr(workflow.time, 'monotonic', lambda: 100.)
    rows = [acquisition(prepared, slot, status='UNSTARTED', integrity=False)
            for slot in range(1, 17)]
    record = {key: value for key, value in rows[-1].items() if key != 'receipt'}
    if fault == 'experiment':
        record['experiment_version'] = PREVIOUS
    elif fault == 'run_id':
        record['run_id'] = scenario.experiment_run_id(prepared['runs'][-1], PREVIOUS)
    else:
        record['case_id'] = record['case_id'].replace('m4_v8_', 'm4_v7_', 1)
    rows[-1] = {**record, 'receipt': save(Path(prepared['root'])/'foreign_final_slot.json', record)}
    with pytest.raises(ValueError):
        workflow.finalize(prepared, rows, 1000.)
    assert not (Path(prepared['root'])/'report/report_receipt.json').exists()
