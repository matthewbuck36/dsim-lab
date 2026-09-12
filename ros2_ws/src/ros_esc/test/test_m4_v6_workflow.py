"""V6 preparation/frozen controller binding with mocked field derivation only.

Temporary files exercise the real sixteen-slot builder and metadata owners.
No numerical topology evaluation, bag read, ROS graph or acquisition runs.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import q1_study
from ros_esc.scenario_runner import aggregate_field_truth as truth
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from test_m4_workflow import save, workflow
from test_m4_v5_versions import synthetic_topology


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(scenario, 'PILOT_ROOT', tmp_path/'pilot')
    root = Path(scenario.experiment_identity('m4-pilot-v6')['root'])
    marker = save(tmp_path/'source.json', {'scope': 'synthetic preparation fixture'})
    selected = scenario.v6_controller_configuration()
    sources = [marker, workflow.receipt(runner.GESC_CONTROLLER),
               workflow.receipt(selected['path'])]
    primary_sources = scenario._template('primary')['cases'][0]['sources']
    calls = []

    def topology(sources, start, bounds, disturbance, *args):
        geometry = 'primary' if sources == primary_sources else 'secondary'
        calls.append((geometry, deepcopy(disturbance)))
        return synthetic_topology(geometry, disturbance)

    monkeypatch.setattr(workflow.subprocess, 'check_output',
                        lambda *args, **kwargs: 'feature/gesc-gaussian-robustness-v2\n')
    monkeypatch.setattr(workflow.subprocess, 'Popen',
                        lambda *args, **kwargs: pytest.fail('no acquisition in source fixture'))
    monkeypatch.setattr(workflow, 'collect_sources', lambda: deepcopy(sources))
    monkeypatch.setattr(workflow, 'geometry_context', lambda *args: dict(
        label_geometry=marker, geometry_recovery=marker, geometry_receipts=[marker]))
    monkeypatch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kwargs: {'fixture': 'installed'})
    monkeypatch.setenv('ROS_DOMAIN_ID', '189')
    monkeypatch.setattr(truth, 'derive_two_source_topology_qualification', topology)
    monkeypatch.setattr(truth, '_model',
                        lambda *args, **kwargs: pytest.fail('no field model in source fixture'))
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification',
                        lambda record, *args, **kwargs: deepcopy(record))
    monkeypatch.setattr(q1_study, 'verify_geometry_receipts', lambda *args: True)
    result = workflow.prepare('m4-pilot-v6')
    return workflow.read_json(result['path']), calls, root


def test_preparation_freezes_one_controller_for_all_sixteen_slots(prepared):
    contract, calls, root = prepared
    selected = scenario.v6_controller_configuration()
    assert contract['controller_configuration'] == selected
    assert len(calls) == 4 and [row[0] for row in calls] == ['secondary']*3+['primary']
    assert calls[1][1]['sensor_noise']['std_dev'] == .015
    assert calls[2][1]['sensor_delay_sec'] == calls[2][1]['pose_delay_sec'] == .1
    original = deepcopy(contract)
    controls = contract['runs'][0]['resolved_scenario']['algorithm']['launch_overrides']
    assert list(controls) == sorted(controls)  # Real saved JSON sorts its keys.
    assert workflow.verify_frozen(contract)
    assert contract == original
    assert len(contract['runs']) == 16
    for row in contract['runs']:
        assert row['launch_argv'].count('controller_config_filepath:='+selected['path']) == 1
        metadata = runner.build_metadata(row['resolved_scenario'], 'mattb',
                                         'm4-pilot-v6', '', run_id=row['run_id'])
        assert metadata['parameter_files'].count(selected['path']) == 1
        assert str(runner.GESC_CONTROLLER) not in metadata['parameter_files']
    receipt = workflow.read_json(root/'preflight/prepared.json')
    assert receipt['status'] == 'PREPARED' and receipt['acquisition_started'] is False
    with pytest.raises(FileExistsError):
        workflow.prepare('m4-pilot-v6')
    assert len(calls) == 4  # A second call cannot derive or replace this version.


@pytest.mark.parametrize('fault', ['old_only', 'old_and_selected', 'duplicate_selected'])
def test_frozen_audit_rejects_metadata_controller_divergence(prepared, monkeypatch, fault):
    contract, _, _ = prepared
    selected = contract['controller_configuration']['path']
    files = {'old_only': [str(runner.GESC_CONTROLLER)],
             'old_and_selected': [str(runner.GESC_CONTROLLER), selected],
             'duplicate_selected': [selected, selected]}[fault]
    monkeypatch.setattr(runner, 'build_metadata', lambda *args, **kwargs: {'parameter_files': files})
    with pytest.raises(ValueError, match='controller metadata'):
        workflow.verify_frozen(contract)


def test_frozen_audit_rejects_launch_only_method_change_before_dispatch(prepared):
    contract, _, _ = prepared
    row = contract['runs'][1]  # B's resolved window remains the approved 6 seconds.
    assert row['resolved_scenario']['algorithm']['launch_overrides']['centroid_window_sec'] == 6.
    row['launch_argv'] = [
        'centroid_window_sec:=8.0' if value.startswith('centroid_window_sec:=') else value
        for value in row['launch_argv']]
    Path(contract['contract_path']).write_text(json.dumps(contract))
    with pytest.raises(ValueError, match='launch argv'):
        workflow.verify_frozen(contract)


def test_frozen_audit_preserves_exact_argument_order(prepared):
    contract, _, _ = prepared
    argv = contract['runs'][0]['launch_argv']
    argv[-1], argv[-2] = argv[-2], argv[-1]
    Path(contract['contract_path']).write_text(json.dumps(contract, sort_keys=True))
    with pytest.raises(ValueError, match='launch argv'):
        workflow.verify_frozen(contract)


def test_frozen_audit_rejects_scenario_override_divergence(prepared):
    contract, _, _ = prepared
    import yaml
    path = Path(contract['scenario']['path'])
    document = yaml.safe_load(path.read_text())
    document['cases'][1]['algorithm']['launch_overrides']['centroid_window_sec'] = 8.
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    contract['scenario'] = workflow.receipt(path)
    Path(contract['contract_path']).write_text(json.dumps(contract, sort_keys=True))
    with pytest.raises(ValueError, match='scenario overrides'):
        workflow.verify_frozen(contract)


def test_current_source_collection_includes_both_configurations_and_adopted_plans():
    paths = {row['path'] for row in workflow.collect_sources()}
    assert {str(runner.GESC_CONTROLLER), str(scenario.V6_CONTROLLER_PATH),
            str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v6_centroid_heartbeat_plan.md'),
            str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v6_matched_gain_plan.md')} <= paths
