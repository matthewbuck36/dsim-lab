"""V7 workflow selection through existing owners with finite synthetic inputs.

Prepare V6 and V7 once each with numerical/graph operations replaced. Every
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
from test_m4_workflow import save, workflow
from test_m4_v5_versions import synthetic_topology


VERSION = 'm4-pilot-v7'
PREVIOUS = 'm4-pilot-v6'
EARLIER = tuple(f'm4-pilot-v{number}' for number in range(1, 7))


def unavailable(*args, **kwargs):
    pytest.fail('workflow source fixture cannot start a process or field model')


@pytest.fixture(scope='module')
def _prepared_versions(tmp_path_factory):
    """One real schema expansion per version, with existing numerical mocks."""
    directory = tmp_path_factory.mktemp('m4_v7_workflow')
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
        patch.setenv('ROS_DOMAIN_ID', '189')
        patch.setattr(truth, 'derive_two_source_topology_qualification', topology)
        patch.setattr(truth, '_model', unavailable)
        patch.setattr(truth, 'validate_two_source_topology_qualification',
                      lambda record, *args, **kwargs: deepcopy(record))
        patch.setattr(q1_study, 'verify_geometry_receipts', lambda *args: True)
        contracts = {version: workflow.read_json(workflow.prepare(version)['path'])
                     for version in (PREVIOUS, VERSION)}
    files = {path: path.read_bytes() for path in directory.rglob('*') if path.is_file()}
    return dict(directory=directory, contracts=contracts, calls=calls, files=files)


@pytest.fixture
def prepared(_prepared_versions, monkeypatch):
    baseline = _prepared_versions
    # Only this module's temporary tree is restored; retained/repository files
    # are never destinations. A contract mutation cannot poison the next case.
    for path in baseline['directory'].rglob('*'):
        if path.is_file() and path not in baseline['files']:
            path.unlink()
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
            ('m4_pilot_v6', 'm4_pilot_v7'),
            (PREVIOUS, VERSION),
        ):
            value = value.replace(before, after)
    return value


def test_preparation_retains_all_sixteen_v6_controls_topologies_and_budgets(
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
        ros_domain_id=189, recording_sec=720., case_timeout_sec=900., suite_timeout_sec=15300.,
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
        assert row['case_id'] == f'm4_v7_{partition}_{condition}_{arm}_{seed}'
        assert row['run_id'] == f'm4-pilot-v7-slot{index+1:02d}-{arm}-{seed}'
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
def test_prior_version_context_cannot_replace_any_v7_contract_boundary(prepared, earlier, field):
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


@pytest.mark.parametrize('field,value', [('method_version', 'm4-pilot-v7'),
                                      ('process_ownership_mode', 'subreaper_v2')])
def test_workflow_keeps_original_method_and_group_owner(prepared, field, value):
    destination = prepared['execution'] if field == 'process_ownership_mode' else prepared
    destination[field] = value
    freeze(prepared)
    with pytest.raises(ValueError, match='identity differs'):
        workflow.verify_frozen(prepared)


def test_source_collector_pins_both_controller_files_and_both_v7_amendments():
    paths = {row['path'] for row in workflow.collect_sources()}
    expected = {str(runner.GESC_CONTROLLER), str(scenario.V6_CONTROLLER_PATH), str(Path(__file__)),
        str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v7_recording_clock_range_plan.md'),
        str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v7_clock_range_comparison_plan.md')}
    assert expected <= paths
