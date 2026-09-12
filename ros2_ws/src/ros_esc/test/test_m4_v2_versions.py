"""Version separation fixtures: no simulation, bag reads or field evaluation."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.plotting_scripts import m4_pilot as metrics

REPOSITORY=Path(__file__).resolve().parents[4]
TOOLS=REPOSITORY/'docs/codex/gesc_gaussian/v2/tools'
BEFORE=Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v2_recovery_v1/version_before')
sys.path.insert(0,str(TOOLS))


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


workflow=module('m4_v2_workflow_fixture',TOOLS/'m4_workflow.py')
dispatch=module('m4_v2_dispatch_fixture',TOOLS/'run_m4.py')
evaluator=module('m4_v2_evaluator_fixture',TOOLS/'evaluate_m4.py')


def topology():
    original=scenario._template('secondary')['cases'][0]['success']['staged_recovery']['topology_qualification']
    return {key:deepcopy(original) for key in scenario.CONDITIONS}


def test_v1_default_population_and_resource_are_exact_retained_owner_outputs():
    old=module('m4_v1_scenario_retained',BEFORE/'ros2_ws/src/ros_esc/ros_esc/scenario_runner/m4_scenario.py')
    old.SCENARIOS=scenario.SCENARIOS
    assert scenario.expected_slots()==old.expected_slots()
    assert scenario.build_m4_document(topology(),runs_root='/same/fixture') == old.build_m4_document(topology(),runs_root='/same/fixture')
    assert scenario.experiment_run_id(scenario.expected_slots()[0]) == 'm4-pilot-v1-slot01-A-26090801'


def test_v1_default_scientific_outputs_are_exact_retained_owner_outputs():
    old=module('ros_esc.plotting_scripts.m4_v1_metrics_retained',BEFORE/'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py')
    assert metrics.aggregate_pilot([])==old.aggregate_pilot([])
    kwargs=dict(run_id='old-fixture',arm='C',partition='development',condition='nominal')
    qualification={'qualified':False,'origin_ns':None,'integrity_errors':['fixture']}
    assert metrics.normalize_direction_targets([],qualification,**kwargs)==old.normalize_direction_targets([],qualification,**kwargs)


@pytest.fixture
def contract(tmp_path,monkeypatch):
    monkeypatch.setattr(scenario,'PILOT_ROOT',tmp_path/'pilot')
    version='m4-pilot-v2'; identity=scenario.experiment_identity(version)
    root=Path(identity['root']); root.mkdir(parents=True)
    record=dict(schema_version=1,version=version,experiment_version=version,method_version=metrics.VERSION,
        root=str(root),contract_path=str(root/'preflight/contract.json'),scenario={'path':str(root/'scenario.yaml'),'sha256':'fixture'},
        execution=dict(runs_root=str(root/'runs'),process_ownership_mode='subreaper_v2',
            recording_sec=720.,case_timeout_sec=900.,suite_timeout_sec=15300.,cleanup_reserve_sec=30.,science_budget_sec=900.,shutdown_grace_sec=45.),
        science=dict(targets_sec=list(metrics.TARGET_OFFSETS_SEC),labels_sec=120.,references_sec=45.,summary_sec=10.,freeze_report_sec=20.,maximum_observations=40000),
        source_files=[],topology_receipts={},geometry_contexts={},environment={},installed_entry_points={})
    record['runs']=[{**row,'run_id':scenario.experiment_run_id(row,version),
        'resolved_scenario':{'suite_id':identity['suite_id']},
        'summary_path':str(root/'acquisition'/f'summary_{row["slot"]}.yaml'),
        'expected_cost_configuration':{'path':str(root/'cost.json'),'sha256':'fixture'}}
        for row in scenario.expected_slots(version)]
    for row in record['runs']: row['runner_argv']=dispatch.runner_command(record,row)
    return record


def test_fresh_version_preserves_every_scientific_setting_and_all_caps(contract):
    root=Path(contract['root']);version=contract['version']
    v2=scenario.build_m4_document(topology(),runs_root=root/'runs',experiment_version=version)
    v1=scenario.build_m4_document(topology(),runs_root=root/'runs')
    assert v2['suite_id']=='m4_pilot_v2' and v2['metadata']['experiment_version']==version
    for first,second in zip(v1['cases'],v2['cases']):
        assert second['case_id'].startswith('m4_v2_')
        expected=deepcopy(second)
        expected['case_id']=first['case_id']
        expected['success']['controller']['contract_id']=first['case_id']
        assert expected==first
    assert len(set(r['run_id'] for r in contract['runs']))==16
    assert not set(r['case_id'] for r in scenario.expected_slots()) & set(r['case_id'] for r in contract['runs'])
    assert dispatch.validate_contract(contract)==root
    assert all('--process-ownership-mode' in row['runner_argv'] and 'subreaper_v2' in row['runner_argv'] for row in contract['runs'])


@pytest.mark.parametrize('fault',['old_root','old_run','old_case','old_suite','old_mode','old_method','old_experiment','wrong_target','changed_cap'])
def test_v2_contract_rejects_old_identity_or_changed_method(contract,fault):
    row=contract['runs'][0]
    if fault=='old_root': contract['root']=str(Path(contract['root']).parent/'m4_pilot_v1')
    elif fault=='old_run': row['run_id']=scenario.experiment_run_id(scenario.expected_slots()[0])
    elif fault=='old_case': row['case_id']=scenario.expected_slots()[0]['case_id']
    elif fault=='old_suite': row['resolved_scenario']['suite_id']='m4_pilot_v1'
    elif fault=='old_mode': contract['execution']['process_ownership_mode']='observed_tree_v1'
    elif fault=='old_method': contract['method_version']='another-method'
    elif fault=='old_experiment': contract['experiment_version']='m4-pilot-v1'
    elif fault=='wrong_target': contract['science']['targets_sec'][0]=16
    else: contract['science']['references_sec']=46.
    with pytest.raises(ValueError): dispatch.validate_contract(contract)


def test_v2_resource_cannot_write_old_root_and_preserves_existing_files(contract):
    root=Path(contract['root']); path=root/'scenario.yaml'
    with pytest.raises(ValueError):
        scenario.write_m4_scenario(path,topology(),runs_root=root.parent/'m4_pilot_v1/runs',experiment_version=contract['version'])
    assert not path.exists()
    scenario.write_m4_scenario(path,topology(),runs_root=root/'runs',experiment_version=contract['version'])
    before=path.read_bytes()
    with pytest.raises(FileExistsError):
        scenario.write_m4_scenario(path,topology(),runs_root=root/'runs',experiment_version=contract['version'])
    assert path.read_bytes()==before


def test_analysis_identity_is_separate_from_unchanged_method(contract):
    row=contract['runs'][2]
    normalized=metrics.normalize_direction_targets([],{'qualified':False,'origin_ns':None,'integrity_errors':[]},
        run_id=row['run_id'],arm='C',partition='development',condition='nominal',experiment_version=contract['version'])
    assert normalized['version']==normalized['method_version']=='m4-pilot-v1'
    assert normalized['experiment_version']=='m4-pilot-v2'
    assert len(normalized['targets'])==24
    metrics.validate_experiment_document(normalized,contract['version'])
    with pytest.raises(ValueError): metrics.validate_experiment_document(normalized)
    with pytest.raises(ValueError):
        metrics.normalize_direction_targets([],{'qualified':False,'origin_ns':None},
            run_id='m4-pilot-v1-slot03-C-26090801',arm='C',partition='development',condition='nominal',experiment_version=contract['version'])
    result=metrics.evaluate_direction_targets(normalized,raw_owner=lambda *a:pytest.fail('no field for unavailable input'),binding={},sources=[])
    assert result['experiment_version']==contract['version'] and len(result['rows'])==24


def test_v2_all_slot_aggregation_retains_192_targets_and_rejects_v1_row(contract):
    result=metrics.aggregate_pilot([],experiment_version=contract['version'])
    assert result['experiment_version']==contract['version'] and result['method_version']==metrics.VERSION
    assert len(result['slots'])==16 and len(result['direction_rows'])==192
    assert all(r['run_id'].startswith('m4-pilot-v2-') for r in result['direction_rows'])
    row={**contract['runs'][0],'status':'INCOMPLETE','integrity_passed':False}
    assert metrics.aggregate_pilot([row],experiment_version=contract['version'])['slot_status_counts']=={'INCOMPLETE':1,'UNSTARTED':15}
    row['experiment_version']='m4-pilot-v1'
    with pytest.raises(ValueError):metrics.aggregate_pilot([row],experiment_version=contract['version'])


def test_v2_process_proof_cannot_be_replaced_by_old_empty_cleanup(contract):
    with pytest.raises(ValueError): dispatch.validate_process_ownership(contract,{'process_ownership':{'inspection_complete':True}})
    keys=('complete','baseline_echild','subreaper_verified','root_reaped','final_echild','scope_exclusive','sigchld_valid','state_restored')
    proof={k:True for k in keys}
    result={'process_ownership':{'mode':'subreaper_v2','inspection_complete':True,'kernel_proof':proof}}
    dispatch.validate_process_ownership(contract,result)
    for key in keys:
        bad=deepcopy(result);bad['process_ownership']['kernel_proof'][key]=False
        with pytest.raises(ValueError):dispatch.validate_process_ownership(contract,bad)
    dispatch.validate_process_ownership({'version':'m4-pilot-v1'},{})


def test_fresh_plan_is_frozen_by_existing_source_collector(monkeypatch):
    monkeypatch.setattr(workflow.subprocess,'check_output',lambda *a,**k:b'')
    paths={row['path'] for row in workflow.collect_sources()}
    assert str(REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v2_recovery_plan.md') in paths


@pytest.mark.parametrize('fault',['experiment_version','visible'])
def test_v2_acquisition_binding_rejects_metadata_substitution_before_read(contract,fault,monkeypatch):
    row={**contract['runs'][0],'status':'COMPLETE','integrity_passed':True,'input_files':[]}
    path=Path(contract['root'])/'acquisition/slot_1.json';path.parent.mkdir()
    path.write_text(json.dumps(row))
    evaluator._acquired(contract,contract['runs'][0])
    row[fault]='m4-pilot-v1' if fault=='experiment_version' else False
    path.write_text(json.dumps(row))
    monkeypatch.setattr(evaluator,'check_receipts',lambda *a:pytest.fail('identity must precede input reads'))
    with pytest.raises(ValueError,match='experiment/visibility'):evaluator._acquired(contract,contract['runs'][0])


@pytest.mark.parametrize('fault',['contract','block','incomplete'])
def test_v2_reference_requires_exact_completed_label_contract_before_any_model(contract,fault,monkeypatch):
    path=Path(contract['contract_path']);path.parent.mkdir();path.write_text(json.dumps(contract))
    labels=dict(version=metrics.VERSION,**metrics.experiment_fields(contract['version']),
                contract=workflow.receipt(path),block=0,complete=True,integrity_passed=True,runs=[])
    if fault=='contract':labels['contract']['sha256']='changed'
    elif fault=='block':labels['block']=1
    else:labels['complete']=False
    folder=Path(contract['root'])/'analysis/block_0';folder.mkdir(parents=True)
    (folder/'labels.json').write_text(json.dumps(labels))
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    monkeypatch.setattr(truth,'_model',lambda *a:pytest.fail('model constructed before exact label binding'))
    with pytest.raises(ValueError,match='contract/block'):evaluator.references_stage(contract,3)


def proof(pid):
    return {'mode':'subreaper_v2','inspection_complete':True,
            'kernel_proof':{k:True for k in ('complete','baseline_echild','subreaper_verified',
                'root_reaped','final_echild','scope_exclusive','sigchld_valid','state_restored')},
            'identities':[{'pid':pid,'session_id':pid,'start_ticks':1}],'session_ids':[pid]}


def test_v2_dispatch_passes_mode_to_inner_outer_and_cleanup_without_extra_slots(contract,monkeypatch):
    from ros_esc.scenario_runner import run_scenario as runner
    contract['execution']['ros_domain_id']=79
    monkeypatch.setenv('ROS_DOMAIN_ID','79')
    path=Path(contract['contract_path']);path.parent.mkdir();path.write_text(json.dumps(contract))
    monkeypatch.setattr(dispatch.time,'monotonic',lambda:100.)
    monkeypatch.setattr(runner,'ensure_ros_daemon',lambda:None)
    monkeypatch.setattr(runner,'ros_graph_nodes',lambda **k:set())
    calls,cleanups,blocks,releases=[],[],[],[]
    def process(argv,*args,**kwargs):
        assert args==(900.,45.) and kwargs['process_ownership_mode']=='subreaper_v2'
        assert kwargs['strict_process_tracking'] is True
        assert argv[argv.index('--process-ownership-mode')+1]=='subreaper_v2'
        calls.append(argv[argv.index('--run-id')+1])
        return {'stdout':'fixture','session_id':100+len(calls),'return_code':0,'timed_out':False,
                'process_ownership':proof(100+len(calls))}
    def cleanup(*args,**kwargs):
        assert kwargs['strict'] is True and kwargs['process_ownership_mode']=='subreaper_v2'
        cleanups.append(kwargs)
        return {'passed':True,'strict':True}
    def validate(value,planned,outer):
        directory=Path(contract['root'])/'runs/2026-09-10'/planned['run_id']
        (directory/'bag').mkdir(parents=True)
        for name in ('metadata.yaml','resolved_topics.yaml','resolved_scenario.yaml','resolved_parameters.yaml',
                     'scenario_result.yaml','completeness.json','bag/metadata.yaml'):
            (directory/name).write_text('{}')
        return {'record_process':{'session_id':200+planned['slot'],'process_ownership':proof(200+planned['slot'])},
                'classification':{'passed':False}},directory
    monkeypatch.setattr(runner,'run_record_process',process)
    monkeypatch.setattr(runner,'cleanup_evidence',cleanup)
    monkeypatch.setattr(dispatch,'validate_case_result',validate)
    def analyze(c,block,rows,end):
        blocks.append(block)
        assert all(row['experiment_version']==contract['version'] for row in rows)
        return {'complete':True,'integrity_passed':True}
    def release(*args):releases.append(True);return {'status':'RELEASED'}
    result=dispatch.dispatch(path,verify_frozen=lambda c:None,analyze_block=analyze,
        release_holdouts=release,finalize=lambda *a:None,bind_recorded=lambda *a,**k:{})
    assert result['status']=='COMPLETE' and len(calls)==16 and len(cleanups)==32
    assert blocks==[0,1,2,3] and releases==[True]
    assert [row['run_id'] for row in result['slots']]==calls
    with pytest.raises(FileExistsError):
        dispatch.dispatch(path,verify_frozen=lambda c:None,analyze_block=analyze,
                         release_holdouts=release,finalize=lambda *a:None)
    assert len(calls)==16


def test_v2_science_hooks_propagate_ownership_and_preserve_caps(contract,monkeypatch):
    import m4_science_job
    monkeypatch.setattr(workflow,'verify_frozen',lambda *a,**k:True)
    monkeypatch.setattr(workflow.time,'monotonic',lambda:100.)
    rows=[]
    directory=Path(contract['root'])/'acquisition';directory.mkdir()
    for planned in contract['runs'][:4]:
        row={**planned,'status':'COMPLETE','integrity_passed':True,'input_files':[]}
        path=directory/f"slot_{row['slot']}.json";path.write_text(json.dumps(row))
        rows.append({**row,'receipt':workflow.receipt(path)})
    calls=[]
    def job(argv,log_path,receipt_path,*,cap_sec,suite_end,process_ownership_mode):
        assert process_ownership_mode=='subreaper_v2'
        stage=argv[2]; calls.append((stage,cap_sec))
        result={'complete':True,'integrity_passed':True}
        Path(receipt_path).write_text(json.dumps(result));Path(log_path).write_text('fixture')
        if stage in ('labels','summary'):
            output=Path(log_path).parent/('labels.json' if stage=='labels' else 'result.json')
            output.write_text(json.dumps({'complete':True,'integrity_passed':True,
                'runs':workflow._science_unavailable(rows,'fixture')}))
        return result
    monkeypatch.setattr(m4_science_job,'finite_science_job',job)
    result=workflow.analyze_block(contract,0,rows,1000.)
    assert result['complete'] and calls==[('labels',120.),('references',45.),('references',45.),('summary',10.)]


def test_v2_summary_cannot_import_another_experiment_contract(contract):
    path=Path(contract['contract_path']);path.parent.mkdir();path.write_text(json.dumps(contract))
    labels=dict(version=metrics.VERSION,**metrics.experiment_fields(contract['version']),
                contract={'path':'/old/contract.json','sha256':'old'},block=0,complete=True,integrity_passed=True,runs=[])
    directory=Path(contract['root'])/'analysis/block_0';directory.mkdir(parents=True)
    (directory/'labels.json').write_text(json.dumps(labels))
    with pytest.raises(ValueError,match='label contract'):evaluator.summary_stage(contract,0)
