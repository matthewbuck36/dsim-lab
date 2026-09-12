"""Fresh M4v4 identity admission with unchanged methods and ownership.

Only synthetic metadata/resources are used. No ROS graph, field computation,
recorded bag, preparation or acquisition is opened or started by these checks.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_v3_versions import (
    REPOSITORY, dispatch, evaluator, module, topology, workflow,
    test_v3_dispatch_passes_mode_to_inner_outer_and_cleanup_without_extra_slots as _check_dispatch,
    test_v3_science_hooks_propagate_ownership_and_preserve_caps as _check_science,
)

VERSION = 'm4-pilot-v4'
MODE = 'subreaper_group_v3'
BEFORE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v4_confirmation_mirror_v1/version_before')
EARLIER = ('m4-pilot-v1', 'm4-pilot-v2', 'm4-pilot-v3')


@pytest.fixture
def contract(tmp_path, monkeypatch):
    monkeypatch.setattr(scenario, 'PILOT_ROOT', tmp_path/'pilot')
    identity=scenario.experiment_identity(VERSION)
    root=Path(identity['root']);root.mkdir(parents=True)
    value=dict(schema_version=1,version=VERSION,experiment_version=VERSION,
        method_version='m4-pilot-v1',root=str(root),contract_path=str(root/'preflight/contract.json'),
        scenario={'path':str(root/'scenario.yaml'),'sha256':'fixture'},
        execution=dict(runs_root=str(root/'runs'),process_ownership_mode=MODE,
            recording_sec=720.,case_timeout_sec=900.,suite_timeout_sec=15300.,
            cleanup_reserve_sec=30.,science_budget_sec=900.,shutdown_grace_sec=45.),
        science=dict(targets_sec=list(metrics.TARGET_OFFSETS_SEC),labels_sec=120.,
            references_sec=45.,summary_sec=10.,freeze_report_sec=20.,maximum_observations=40000),
        source_files=[],topology_receipts={},geometry_contexts={},environment={},installed_entry_points={})
    value['runs']=[{**row,'run_id':scenario.experiment_run_id(row,VERSION),
        'resolved_scenario':{'suite_id':identity['suite_id']},
        'summary_path':str(root/'acquisition'/f'summary_{row["slot"]}.yaml'),
        'expected_cost_configuration':{'path':str(root/'cost.json'),'sha256':'fixture'}}
        for row in scenario.expected_slots(VERSION)]
    for row in value['runs']:row['runner_argv']=dispatch.runner_command(value,row)
    return value


def test_exact_fresh_root_population_gui_and_existing_owner():
    identity=scenario.experiment_identity(VERSION)
    assert identity==dict(experiment_version=VERSION,suite_id='m4_pilot_v4',
        root='/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v4',process_ownership_mode=MODE)
    rows=scenario.expected_slots(VERSION)
    expected_blocks=(('development','primary','nominal',26090801),
        ('holdout','secondary','nominal',26090802),('holdout','secondary','noise',26090803),
        ('holdout','secondary','delay',26090804))
    assert len(rows)==16 and [row['slot'] for row in rows]==list(range(1,17))
    for block,spec in enumerate(expected_blocks):
        selected=rows[4*block:4*block+4]
        assert [row['arm'] for row in selected]==list('ABCD')
        for row in selected:
            assert tuple(row[key] for key in ('partition','geometry','condition','seed'))==spec
            assert row['visible'] is (block==0)
            assert row['case_id']==f'm4_v4_{spec[0]}_{spec[2]}_{row["arm"]}_{spec[3]}'
            assert scenario.experiment_run_id(row,VERSION)==f'm4-pilot-v4-slot{row["slot"]:02d}-{row["arm"]}-{spec[3]}'
    old_ids={row['case_id'] for version in EARLIER for row in scenario.expected_slots(version)}
    assert not old_ids & {row['case_id'] for row in rows}


@pytest.mark.parametrize('version',EARLIER)
def test_prior_population_resource_argv_and_scientific_outputs_are_exact(version):
    old=module('m4_v4_retained_scenario_'+version[-1],BEFORE/'ros2_ws/src/ros_esc/ros_esc/scenario_runner/m4_scenario.py')
    old.SCENARIOS=scenario.SCENARIOS
    previous_metrics=module('ros_esc.plotting_scripts.m4_v4_retained_metrics_'+version[-1],
        BEFORE/'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py')
    previous_dispatch=module('m4_v4_retained_dispatch_'+version[-1],BEFORE/'docs/codex/gesc_gaussian/v2/tools/run_m4.py')
    assert scenario.experiment_identity(version)==old.experiment_identity(version)
    assert scenario.expected_slots(version)==old.expected_slots(version)
    kwargs=dict(runs_root=Path(old.experiment_identity(version)['root'])/'runs',experiment_version=version)
    assert scenario.build_m4_document(topology(),**kwargs)==old.build_m4_document(topology(),**kwargs)
    assert metrics.aggregate_pilot([],experiment_version=version)==previous_metrics.aggregate_pilot([],experiment_version=version)
    row=scenario.expected_slots(version)[2]
    planned=dict(case_id=row['case_id'],run_id=scenario.experiment_run_id(row,version),
        summary_path='/fixture/summary.yaml',visible=True)
    value=dict(version=version,scenario={'path':'/fixture/scenario.yaml'},execution={'runs_root':'/fixture/runs'})
    assert dispatch.runner_command(value,planned)==previous_dispatch.runner_command(value,planned)


def test_v4_resource_changes_only_declared_identity_and_preserves_all_caps(contract):
    root=Path(contract['root'])
    current=scenario.build_m4_document(topology(),runs_root=root/'runs',experiment_version=VERSION)
    legacy=scenario.build_m4_document(topology(),runs_root=root/'runs')
    assert current['suite_id']=='m4_pilot_v4'
    assert current['metadata']['experiment_version']==VERSION
    assert current['execution']==legacy['execution']
    assert current['execution']['run_timeout_sec']==720.
    assert current['execution']['wall_timeout_sec']==900.
    assert current['frozen_profile']==legacy['frozen_profile']
    for now,old in zip(current['cases'],legacy['cases']):
        normalized=deepcopy(now)
        normalized['case_id']=old['case_id']
        normalized['success']['controller']['contract_id']=old['case_id']
        assert normalized==old
    assert dispatch.validate_contract(contract)==root
    for row in contract['runs']:
        argv=row['runner_argv']
        assert argv[:4]==['ros2','run','ros_esc','run_scenario']
        assert argv[argv.index('--process-ownership-mode')+1]==MODE


@pytest.mark.parametrize('earlier',EARLIER)
@pytest.mark.parametrize('fault',['root','case','run','suite','experiment','analysis'])
def test_prior_experiment_cannot_substitute_fresh_v4_inputs(contract,earlier,fault):
    identity=scenario.experiment_identity(earlier);old=scenario.expected_slots(earlier)[0]
    row=contract['runs'][0]
    if fault=='root':contract['root']=identity['root']
    elif fault=='case':row['case_id']=old['case_id']
    elif fault=='run':row['run_id']=scenario.experiment_run_id(old,earlier)
    elif fault=='suite':row['resolved_scenario']['suite_id']=identity['suite_id']
    elif fault=='experiment':contract['experiment_version']=earlier
    else:
        document={'version':metrics.VERSION,**metrics.experiment_fields(earlier)}
        with pytest.raises(ValueError):metrics.validate_experiment_document(document,VERSION)
        return
    with pytest.raises(ValueError):dispatch.validate_contract(contract)


@pytest.mark.parametrize('mode',['observed_tree_v1','subreaper_v2','subreaper_group_v4'])
def test_v4_keeps_exact_existing_group_ownership_mode(contract,mode):
    contract['execution']['process_ownership_mode']=mode
    with pytest.raises(ValueError):dispatch.validate_contract(contract)


@pytest.mark.parametrize('version',['m4-pilot-v15','m4-pilot-v04','m4_pilot_v4',None])
def test_version_allowlist_remains_exact(version):
    with pytest.raises(ValueError):scenario.experiment_identity(version)


@pytest.mark.parametrize('mode,strict,accepted',[(MODE,True,True),(MODE,False,False),
    ('subreaper_v2',True,False),('observed_tree_v1',True,False)])
def test_actual_runner_admission_requires_v4_group_mode_before_expansion(monkeypatch,mode,strict,accepted):
    class Admitted(Exception):pass
    def expansion(*args,**kwargs):raise Admitted
    monkeypatch.setattr(runner,'load_suite',lambda *a:{'suite_id':'m4_pilot_v4'})
    monkeypatch.setattr(runner,'expand_suite',expansion)
    with pytest.raises(Admitted if accepted else ValueError):
        runner.execute_suite('synthetic','fixture',process_ownership_mode=mode,strict_cleanup=strict)


def test_centroid_evaluator_admits_exact_v4_without_changing_selected_method():
    resolved={'suite_id':'m4_pilot_v4','algorithm':{'launch_overrides':{
        'convergence_metric_mode':'centroid_two_block_v2','centroid_window_sec':6.,
        'centroid_epsilon_m':.18,'centroid_maximum_radius_m':.50}}}
    selected=runner._m4_centroid_event_selection(resolved)
    assert selected['metric_mode']=='centroid_two_block_v2'
    assert (selected['window_sec'],selected['epsilon_m'],selected['maximum_radius_m'])==(6.,.18,.50)
    resolved['suite_id']='m4_pilot_v13'
    assert runner._m4_centroid_event_selection(resolved) is None


def test_v4_method_and_all_target_denominators_remain_fixed(contract):
    result=metrics.aggregate_pilot([],experiment_version=VERSION)
    assert result['experiment_version']==VERSION and result['method_version']=='m4-pilot-v1'
    assert len(result['slots'])==16 and len(result['direction_rows'])==192
    row=contract['runs'][2]
    normalized=metrics.normalize_direction_targets([],{'qualified':False,'origin_ns':None,'integrity_errors':[]},
        run_id=row['run_id'],arm='C',partition='development',condition='nominal',experiment_version=VERSION)
    assert normalized['method_version']==metrics.VERSION and normalized['experiment_version']==VERSION
    assert len(normalized['targets'])==24
    value=metrics.evaluate_direction_targets(normalized,raw_owner=lambda *a:pytest.fail('no field for unavailable inputs'),binding={},sources=[])
    assert len(value['rows'])==24 and value['experiment_version']==VERSION


@pytest.mark.parametrize('earlier',EARLIER)
def test_acquisition_identity_rejects_old_input_before_any_receipt_read(contract,monkeypatch,earlier):
    row={**contract['runs'][0],'status':'COMPLETE','integrity_passed':True,'input_files':[]}
    path=Path(contract['root'])/'acquisition/slot_1.json';path.parent.mkdir();path.write_text(json.dumps(row))
    evaluator._acquired(contract,contract['runs'][0])
    row['experiment_version']=earlier;path.write_text(json.dumps(row))
    monkeypatch.setattr(evaluator,'check_receipts',lambda *a:pytest.fail('foreign input must reject before source reads'))
    with pytest.raises(ValueError,match='experiment/visibility'):evaluator._acquired(contract,contract['runs'][0])


def test_fresh_amendment_and_installed_wrapper_are_in_source_pins(monkeypatch):
    monkeypatch.setattr(workflow.subprocess,'check_output',lambda *a,**k:b'')
    paths={row['path'] for row in workflow.collect_sources()}
    assert str(REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v4_confirmation_mirror_plan.md') in paths
    assert '/opt/ros/humble/lib/python3.10/site-packages/ros2run/api/__init__.py' in paths


def test_dispatch_propagates_v4_identity_to_existing_group_owner_and_complete_ledger(contract,monkeypatch):
    _check_dispatch(contract,monkeypatch)


def test_science_v4_hooks_keep_group_owner_and_existing_900_second_allocation(contract,monkeypatch):
    _check_science(contract,monkeypatch)
