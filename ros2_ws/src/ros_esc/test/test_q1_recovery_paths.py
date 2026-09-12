"""Finite infrastructure recovery paths; actual runner dry-run, no ROS dispatch."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import sys

import pytest

REPOSITORY = Path(__file__).resolve().parents[4]
TOOLS = REPOSITORY / 'docs/codex/gesc_gaussian/v2/tools'


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(TOOLS))
    return tuple(importlib.import_module(name) for name in (
        'q1_acquisition_layout','freeze_q1_contract','acquire_q1','evaluate_q1'))


def write(path,document):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(document))
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def fixture_contract(tmp_path,monkeypatch,modules,version=None):
    layout,freeze,_,_=modules
    # This file exercises path/runner routing; environment binding has its own
    # real-wrapper regression suite and is checked before actual dispatch.
    monkeypatch.setattr(modules[2], 'verify_environment', lambda *args: None)
    version=version or layout.SCIENCE_VERSION+'-recovery1'
    roots={layout.SCIENCE_VERSION:tmp_path/'original',layout.SCIENCE_VERSION+'-recovery1':tmp_path/'recovery1'}
    monkeypatch.setattr(layout,'ACQUISITION_ROOTS',roots)
    root=roots[version]
    runs=[{'seed':seed,'partition':partition,'exposure':exposure,
           'run_id':f'{version}-{partition}-{exposure}-{seed}', 'case_id':f'q1_{partition}_{exposure}',
           'visible':seed==26090911}
          for partition,first in (('discovery',26090911),('confirmation',26090913))
          for seed,exposure in ((first,'residence'),(first+1,'approach'))]
    contract={'version':layout.SCIENCE_VERSION,'acquisition_version':version,'acquisition_root':str(root),
              'execution':{'runs_root':str(root/'runs'),'ros_domain_id':191}, 'runs':runs,
              'scenario':{'path':'/synthetic/scenario.yaml'}}
    if version!=layout.SCIENCE_VERSION:
        prior={'version':layout.SCIENCE_VERSION,'status':'INCOMPLETE','verified_input_runs':[],
               'completed_runner_results':[{'runner_result':{'run_directory':None,'cleanup':{'passed':True}}}]}
        contract['recovery']={
            'amendment':write(tmp_path/'amendment.json',{}),
            'closure':write(tmp_path/'closure.json',{}),
            'prior_acquisition':write(roots[layout.SCIENCE_VERSION]/'acquisition/acquisition.json',prior)}
    path=root/'preflight/contract.json'
    return contract,path,root


@pytest.mark.parametrize('version',['q1-primary-shadow-v1','q1-primary-shadow-v1-recovery1',
                                   'q1-primary-shadow-v1-recovery2','q1-primary-shadow-v1-recovery3'])
def test_actual_runner_dry_run_matches_fixed_preview_and_separate_root(modules,version):
    layout,freeze,_,_=modules
    suite=freeze.load_suite(freeze.SCENARIO)
    before=deepcopy(suite)
    resolved,unsupported=freeze.expand_suite(suite)
    assert not unsupported
    root=layout.acquisition_root(version)
    planned=freeze.build_acquisition_runs(suite,resolved,root,version)
    assert suite==before
    for item in planned:
        summary=freeze.runner.execute_suite(freeze.SCENARIO,'mattb',case_ids=[item['case_id']],
                    runs_root=root/'runs',gui=item['visible'],dry_run=True,run_id=item['run_id'])
        actual=summary['runs'][0]
        assert actual['launch_argv']==item['launch_argv']
        assert actual['metadata']==item['metadata_preview']
        command=actual['record_argv'][:]
        command[command.index('--metadata-input')+1]=item['record_argv_template'][item['record_argv_template'].index('--metadata-input')+1]
        assert command==item['record_argv_template']
        assert command[command.index('--runs-root')+1]==str(root/'runs')
        assert item['runner_argv'][item['runner_argv'].index('--runs-root')+1]==str(root/'runs')
        assert item['metadata_preview']['experiment_version']==layout.SCIENCE_VERSION
    assert [p['seed'] for p in planned]==list(range(26090911,26090915))
    assert [p['visible'] for p in planned]==[True,False,False,False]


def test_original_contract_without_new_fields_remains_compatible(tmp_path,monkeypatch,modules):
    layout=modules[0]
    contract,path,root=fixture_contract(tmp_path,monkeypatch,modules,layout.SCIENCE_VERSION)
    del contract['acquisition_version'];del contract['acquisition_root']
    assert layout.validate_acquisition_layout(contract,path)==root


def second_recovery_contract(tmp_path, monkeypatch, modules):
    layout = modules[0]
    contract, _, prior_root = fixture_contract(tmp_path, monkeypatch, modules)
    prior_version = contract['acquisition_version']
    version = layout.SCIENCE_VERSION + '-recovery2'
    root = tmp_path / 'recovery2'
    layout.ACQUISITION_ROOTS[version] = root
    prior_id = contract['runs'][0]['run_id']
    prior = {'version': layout.SCIENCE_VERSION, 'acquisition_version': prior_version,
             'status': 'INCOMPLETE', 'verified_input_runs': [],
             'completed_runner_results': [{'runner_result': {
                 'run_id': prior_id, 'run_directory': str(prior_root / 'runs/day' / prior_id),
                 'cleanup': {'passed': True}, 'classification': {'passed': False}}}]}
    prior_ref = write(prior_root / 'acquisition/acquisition.json', prior)
    closure = {'status': 'CLOSED_INCOMPLETE', 'acquisition_version': prior_version,
               'verified_runs': 0, 'dispatched_cases': 1, 'remaining_cases_dispatched': False,
               'scientific_confirmation_opened': False, 'completeness_passed': False,
               'cleanup': {'passed': True}, 'artifacts': [prior_ref]}
    contract['recovery'].update(
        source_correction=write(tmp_path / 'correction.json', {}),
        prior_acquisition=prior_ref,
        closure=write(prior_root / 'acquisition_closed.json', closure))
    contract.update(acquisition_version=version, acquisition_root=str(root))
    contract['execution']['runs_root'] = str(root / 'runs')
    for run in contract['runs']:
        run['run_id'] = run['run_id'].replace(prior_version, version)
    return contract, root / 'preflight/contract.json', root


def test_recovery2_requires_its_separate_failed_exposure_boundary(tmp_path, monkeypatch, modules):
    contract, path, root = second_recovery_contract(tmp_path, monkeypatch, modules)
    assert modules[0].validate_acquisition_layout(contract, path) == root
    assert not root.exists()


@pytest.mark.parametrize('change', ['missing_correction', 'opened_confirmation',
                                   'extra_case', 'unmatched_closure', 'prior_success',
                                   'wrong_prior_identity', 'qualified_prior_input'])
def test_recovery2_rejects_reuse_outside_declared_failure(tmp_path, monkeypatch, modules, change):
    contract, path, root = second_recovery_contract(tmp_path, monkeypatch, modules)
    recovery = contract['recovery']
    prior_ref = recovery['prior_acquisition']
    prior = json.loads(Path(prior_ref['path']).read_text())
    closure_path = Path(recovery['closure']['path'])
    closure = json.loads(closure_path.read_text())
    if change == 'missing_correction':
        del recovery['source_correction']
    elif change == 'opened_confirmation':
        closure['scientific_confirmation_opened'] = True
    elif change == 'extra_case':
        closure['dispatched_cases'] = 2
    elif change == 'unmatched_closure':
        closure['artifacts'][0]['sha256'] = '0' * 64
    else:
        if change == 'prior_success':
            prior['completed_runner_results'][0]['runner_result']['classification']['passed'] = True
        elif change == 'wrong_prior_identity':
            prior['acquisition_version'] = modules[0].SCIENCE_VERSION
        else:
            prior['verified_input_runs'] = [{'run_id': 'qualified'}]
        recovery['prior_acquisition'] = write(Path(prior_ref['path']), prior)
        closure['artifacts'] = [recovery['prior_acquisition']]
    recovery['closure'] = write(closure_path, closure)
    with pytest.raises(ValueError):
        modules[0].validate_acquisition_layout(contract, path)
    assert not root.exists()


def third_recovery_contract(tmp_path, monkeypatch, modules):
    layout=modules[0]
    contract,_,prior_root=second_recovery_contract(tmp_path,monkeypatch,modules)
    prior_version=contract['acquisition_version'];version=layout.SCIENCE_VERSION+'-recovery3'
    root=tmp_path/'recovery3';layout.ACQUISITION_ROOTS[version]=root
    prior_id=contract['runs'][0]['run_id'];directory=prior_root/'runs/day'/prior_id
    predicates={'no_forbidden_events':True,'cleanup_complete':True,'recording_complete':False}
    prior={'version':layout.SCIENCE_VERSION,'acquisition_version':prior_version,'status':'INCOMPLETE',
           'verified_input_runs':[],'scientific_confirmation_opened':False,
           'completed_runner_results':[{'runner_result':{'run_id':prior_id,'run_directory':str(directory),
             'cleanup':{'passed':True},'classification':{'passed':False,'predicate_results':predicates}}}]}
    prior_ref=write(prior_root/'acquisition/acquisition.json',prior)
    failed={'algorithm_event_producer_identified':{'passed':False,'detail':[{
        'event_type':1,'detail':'centroid_windows_v2 source-time configuration'}]}}
    report_ref=write(directory/'completeness.json',{'passed':False,'checks':{
        **failed,'final_commands_zero':{'passed':True},'v2_synchronized_stream_contract':{'passed':True}}})
    closure={'status':'CLOSED_INCOMPLETE','acquisition_version':prior_version,'verified_runs':0,
             'dispatched_cases':1,'remaining_cases_dispatched':False,'scientific_confirmation_opened':False,
             'completeness_passed':False,'recording_complete':True,'final_zero_observed':True,
             'cleanup':{'passed':True},'classification':{'passed':False,'predicate_results':predicates},
             'simulation_duration':{'completed':True,'requested_sec':125.,'elapsed_sec':125.},
             'failed_checks':failed,'artifacts':[prior_ref,report_ref]}
    contract['recovery'].update(prior_acquisition=prior_ref,
        closure=write(prior_root/'acquisition_closed.json',closure))
    contract.update(acquisition_version=version,acquisition_root=str(root))
    contract['execution']['runs_root']=str(root/'runs')
    for run in contract['runs']:run['run_id']=run['run_id'].replace(prior_version,version)
    return contract,root/'preflight/contract.json',root


def test_recovery3_binds_only_the_closed_attribution_failure(tmp_path,monkeypatch,modules):
    contract,path,root=third_recovery_contract(tmp_path,monkeypatch,modules)
    assert modules[0].validate_acquisition_layout(contract,path)==root
    assert not root.exists()


@pytest.mark.parametrize('change',['extra_failure','wrong_event','unsafe','opened_confirmation','report_changed'])
def test_recovery3_rejects_different_or_changed_evidence(tmp_path,monkeypatch,modules,change):
    contract,path,root=third_recovery_contract(tmp_path,monkeypatch,modules)
    ref=contract['recovery']['closure'];closure=json.loads(Path(ref['path']).read_text())
    report_ref=closure['artifacts'][1];report=json.loads(Path(report_ref['path']).read_text())
    if change=='unsafe':closure['classification']['predicate_results']['no_forbidden_events']=False
    elif change=='opened_confirmation':closure['scientific_confirmation_opened']=True
    else:
        if change in ('extra_failure','report_changed'):report['checks']['final_commands_zero']['passed']=False
        else:report['checks']['algorithm_event_producer_identified']['detail'][0]['detail']='another unknown event'
        updated=write(Path(report_ref['path']),report)
        if change!='report_changed':
            closure['artifacts'][1]=updated
            closure['failed_checks']={k:v for k,v in report['checks'].items() if not v['passed']}
    contract['recovery']['closure']=write(Path(ref['path']),closure)
    with pytest.raises(ValueError):modules[0].validate_acquisition_layout(contract,path)
    assert not root.exists()


def fourth_recovery_contract(tmp_path,monkeypatch,modules):
    layout,freeze,acquire,_=modules
    prior_version=layout.SCIENCE_VERSION+'-recovery3';version=layout.SCIENCE_VERSION+'-recovery4'
    prior_root=tmp_path/'recovery3';root=tmp_path/'recovery4';repo=tmp_path/'repo'
    monkeypatch.setattr(layout,'ACQUISITION_ROOTS',{prior_version:prior_root,version:root})
    monkeypatch.setattr(layout,'REPOSITORY',repo)
    monkeypatch.setattr(acquire,'verify_environment',lambda *a:None)
    plans=[{'seed':seed,'partition':partition,'exposure':exposure,'case_id':f'q1_{partition}_{exposure}',
            'run_id':f'{prior_version}-{partition}-{exposure}-{seed}','visible':seed==26090911,
            'resolved_scenario':{'seed':seed},'launch_argv':['node',f'run_id:={prior_version}-{partition}-{exposure}-{seed}']}
           for partition,first in (('discovery',26090911),('confirmation',26090913))
           for seed,exposure in ((first,'residence'),(first+1,'approach'))]
    predicates={'recording_complete':True,'cleanup_complete':True,'no_forbidden_events':True}
    old={'version':layout.SCIENCE_VERSION,'acquisition_version':prior_version,'runs':plans,'source_files':[],
         'execution':{'runs_root':str(prior_root/'runs'),'outer_acquisition_ceiling_sec':1200.,
                      'recorder_process_ceiling_sec':240.,'ros_domain_id':191},
         'scenario':{'path':'/synthetic/scenario.yaml'},'detector':{'fixed':True},'reference':{'fixed':True}}
    old_ref=write(prior_root/'preflight/contract.json',old)
    inputs=[];refs=[];attempts=[];artifacts=[];audit_refs=[]
    for plan in plans[:2]:
        directory=prior_root/'runs/day'/plan['run_id']
        files=[write(directory/'completeness.json',{'passed':True})]
        result={'run_id':plan['run_id'],'run_directory':str(directory),'classification':{'passed':True,'predicate_results':predicates},
                'cleanup':{'passed':True}}
        metadata={'recording':{'completion_reason':'simulation_duration_elapsed',
                  'simulation_duration':{'completed':True,'requested_sec':125.,'elapsed_sec':125.}}}
        files += [write(directory/'scenario_result.yaml',result),write(directory/'metadata.yaml',metadata)]
        spawn=write(prior_root/'acquisition'/f"spawn_{plan['seed']}.json",{'passed':True})
        row={k:plan[k] for k in ('run_id','seed','partition','exposure')}
        row.update(run_directory=str(directory),input_files=files,spawn_check=spawn)
        ref=write(prior_root/'acquisition'/f"input_{plan['seed']}.json",row)
        inputs.append(row);refs.append(ref);artifacts.append(ref);attempts.append({'runner_result':result})
        audit_refs.append(write(prior_root/'diagnostics/discovery_expiry_audit_v1'/f"resets_{plan['seed']}.json",{
            'input':ref,'seed':plan['seed'],'diagnostic_sequence_discontinuities':[],
            'reset_sequence_jumps_or_regressions':[], 'expiry_reason_message_counts':{
                'during_readiness':{'pending_expired':0,'pending_receipt_expired':0}}}))
    attempts.append({'runner_result':{'run_id':plans[2]['run_id'],'classification':{'passed':False},'cleanup':{'passed':True}}})
    acquisition={'contract':old_ref,'acquisition_version':prior_version,'status':'INCOMPLETE',
                 'verified_input_runs':inputs,'completed_runner_results':attempts,'scientific_confirmation_opened':False}
    a_ref=write(prior_root/'acquisition/acquisition.json',acquisition);artifacts.append(a_ref)
    closure={'status':'CLOSED_INCOMPLETE','acquisition_version':prior_version,'verified_runs':2,'dispatched_cases':3,
             'remaining_cases_dispatched':False,'failed_case_pre_readiness':True,'all_cleanup_passed':True,
             'scientific_confirmation_opened':False,'artifacts':artifacts,
             'runs':[{}, {}, {'recording':{'readiness_ever_true':False}}]}
    c_ref=write(prior_root/'acquisition_closed.json',closure)
    audit=write(prior_root/'diagnostics/discovery_expiry_audit_v1/result.json',{
        'status':'COMPLETE','contract':old_ref,'closure':c_ref,'confirmation_scientific_outputs_opened':False,'results':audit_refs})
    evidence=write(tmp_path/'review.json',{'test':'synthetic routing only'})
    proof=write(root/'preflight/source_equivalence.json',{'schema_version':1,'version':'q1-recovery4-source-equivalence-v1',
        'status':'PASS','prior_contract':old_ref,'expiry_audit':audit,'valid_nonexpiry_path_unchanged':True,
        'scientific_confirmation_opened':False,'source_changes':[],'evidence':[evidence]})
    contract=deepcopy(old);contract.update(acquisition_version=version,acquisition_root=str(root))
    contract['execution'].update(runs_root=str(root/'runs'),outer_acquisition_ceiling_sec=600.)
    for plan in contract['runs'][2:]:
        plan['run_id']=plan['run_id'].replace(prior_version,version)
        plan['launch_argv']=[s.replace(prior_version,version) for s in plan['launch_argv']]
    contract['imports']={'prior_contract':old_ref,'prior_acquisition':a_ref,'prior_closure':c_ref,
                         'input_files':refs,'expiry_audit':audit,'source_equivalence':proof}
    contract['recovery']={name:write(repo/'docs/codex/gesc_gaussian/v2'/file,{}) for name,file in (
        ('amendment','q1_acquisition_recovery4_plan.md'),('source_correction','q1_filter_expiry_recovery_plan.md'))}
    verified=[]
    def normal(row,contract):
        verified.append(row['run_id'])
        for ref in row['input_files']:
            if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('input changed')
    monkeypatch.setattr(acquire.analysis,'_q1_verify_run',normal)
    path=root/'preflight/contract.json';ref=write(path,contract)
    write(root/'preflight/dispatch_release.json',{'contract':ref,'status':'RELEASED'})
    monkeypatch.setattr(acquire.analysis,'_q1_contract',lambda ref:contract)
    monkeypatch.setenv('ROS_DOMAIN_ID','191');monkeypatch.setattr(sys,'argv',['acquire','--contract',str(path)])
    return contract,path,root,inputs,verified


def test_recovery4_exact_imports_pass_normal_validation_before_output(tmp_path,monkeypatch,modules):
    contract,path,root,inputs,verified=fourth_recovery_contract(tmp_path,monkeypatch,modules)
    assert modules[0].validate_acquisition_layout(contract,path)==root
    assert modules[0].imported_inputs(contract)==inputs
    assert verified==[r['run_id'] for r in inputs]*2
    assert not (root/'acquisition').exists()


@pytest.mark.parametrize('change',['extra_import','failed_input','fresh_override','new_identity','unreviewed_source',
                                    'equivalence_failure','expiry_observed','opened_confirmation'])
def test_recovery4_rejects_changed_import_science_or_evidence(tmp_path,monkeypatch,modules,change):
    contract,path,root,inputs,_=fourth_recovery_contract(tmp_path,monkeypatch,modules)
    if change=='extra_import':contract['imports']['input_files'].append(contract['imports']['input_files'][0])
    elif change=='failed_input':Path(inputs[0]['input_files'][0]['path']).write_text('{"passed": false}')
    elif change=='fresh_override':contract['runs'][2]['launch_argv'].append('gain:=999')
    elif change=='new_identity':contract['runs'][0]['run_id']=contract['runs'][0]['run_id'].replace('recovery3','recovery4')
    elif change=='unreviewed_source':contract['source_files']=[{'path':str(tmp_path/'unexpected.py'),'sha256':'0'*64}]
    elif change=='equivalence_failure':
        ref=contract['imports']['source_equivalence'];doc=json.loads(Path(ref['path']).read_text());doc['status']='FAIL'
        contract['imports']['source_equivalence']=write(Path(ref['path']),doc)
    else:
        ref=contract['imports']['expiry_audit'];doc=json.loads(Path(ref['path']).read_text())
        if change=='opened_confirmation':doc['confirmation_scientific_outputs_opened']=True
        else:
            child=doc['results'][0];value=json.loads(Path(child['path']).read_text())
            value['expiry_reason_message_counts']['during_readiness']['pending_expired']=1
            doc['results'][0]=write(Path(child['path']),value)
        contract['imports']['expiry_audit']=write(Path(ref['path']),doc)
        proof=contract['imports']['source_equivalence'];value=json.loads(Path(proof['path']).read_text())
        value['expiry_audit']=contract['imports']['expiry_audit']
        contract['imports']['source_equivalence']=write(Path(proof['path']),value)
    write(path,contract)
    with pytest.raises(ValueError):modules[2].main()
    assert not (root/'acquisition').exists()


def configure_fresh_cases(contract,root,monkeypatch,modules,*,after_first=None):
    acquire=modules[2];calls=[]
    def execute(*args,**kw):
        calls.append(kw)
        plan=next(p for p in contract['runs'] if p['run_id']==kw['run_id'])
        directory=root/'runs/day'/plan['run_id']
        metadata={'target_argv':plan['launch_argv'],'recording':{'completion_reason':'simulation_duration_elapsed',
                  'simulation_duration':{'completed':True,'requested_sec':125.}}}
        for name,value in [('metadata.yaml',metadata),('resolved_scenario.yaml',plan['resolved_scenario']),
                           ('resolved_topics.yaml',{}),('resolved_parameters.yaml',{}),('bag/metadata.yaml',{}),
                           ('completeness.json',{'passed':True}),('scenario_result.yaml',{})]:write(directory/name,value)
        write(directory/'bag/bag_0.db3',{'synthetic':'not a real bag'})
        if len(calls)==1 and after_first:after_first()
        return {'runs':[{'run_id':plan['run_id'],'run_directory':str(directory),'classification':{'passed':True}}]}
    monkeypatch.setattr(acquire,'execute_suite',execute)
    monkeypatch.setattr(acquire,'spawn_receipt',lambda *a:{'passed':True})
    monkeypatch.setattr(acquire.analysis,'q1_recorded_binding',lambda *a,**k:{'selected_configurations':{'cost_function_config_filepath':{}}})
    return calls


def test_recovery4_dispatches_only_two_fresh_and_keeps_original_rows(tmp_path,monkeypatch,modules):
    contract,path,root,inputs,_=fourth_recovery_contract(tmp_path,monkeypatch,modules)
    original=[Path(ref['path']).read_bytes() for ref in contract['imports']['input_files']]
    calls=configure_fresh_cases(contract,root,monkeypatch,modules)
    assert modules[2].main()==0
    assert [c['run_id'] for c in calls]==[p['run_id'] for p in contract['runs'][2:]]
    assert all(c['runs_root']==str(root/'runs') and not c['gui'] for c in calls)
    result=json.loads((root/'acquisition/acquisition.json').read_text())
    assert result['imported_inputs']==2 and result['newly_dispatched']==2
    manifest=json.loads((root/'study_manifest.json').read_text())
    assert manifest['runs'][:2]==inputs and manifest['imports']==contract['imports']
    assert [Path(ref['path']).read_bytes() for ref in contract['imports']['input_files']]==original


@pytest.mark.parametrize('cause',['changed_import','budget'])
def test_recovery4_stops_before_second_dispatch_after_input_change_or_budget(tmp_path,monkeypatch,modules,cause):
    contract,path,root,inputs,_=fourth_recovery_contract(tmp_path,monkeypatch,modules)
    clock=[0.];monkeypatch.setattr(modules[2].time,'monotonic',lambda:clock[0])
    def change():
        if cause=='budget':clock[0]=301.
        else:Path(inputs[0]['input_files'][0]['path']).write_text('{}')
    calls=configure_fresh_cases(contract,root,monkeypatch,modules,after_first=change)
    assert modules[2].main()==1 and len(calls)==1
    result=json.loads((root/'acquisition/acquisition.json').read_text())
    assert result['imported_inputs']==2 and result['newly_dispatched']==1
    assert not (root/'study_manifest.json').exists()


@pytest.mark.parametrize('change',['unknown','scientific','root','runs_root','contract_path','old_run_id','population','receipt','prior_exposure'])
def test_mismatched_layout_or_recovery_fails_before_output(tmp_path,monkeypatch,modules,change):
    layout=modules[0];contract,path,root=fixture_contract(tmp_path,monkeypatch,modules)
    if change=='unknown':contract['acquisition_version']='q1-primary-shadow-v1-recovery99'
    elif change=='scientific':contract['version']='q1-primary-shadow-v2'
    elif change=='root':contract['acquisition_root']=str(tmp_path/'original')
    elif change=='runs_root':contract['execution']['runs_root']=str(tmp_path/'original/runs')
    elif change=='contract_path':path=tmp_path/'original/preflight/contract.json'
    elif change=='old_run_id':contract['runs'][0]['run_id']=contract['runs'][0]['run_id'].replace('-recovery1','')
    elif change=='population':contract['runs'][0]['seed']+=1
    elif change=='receipt':Path(contract['recovery']['closure']['path']).write_text('changed')
    else:
        ref=contract['recovery']['prior_acquisition'];prior=json.loads(Path(ref['path']).read_text())
        prior['verified_input_runs']=[{'run_id':'already_observed'}]
        contract['recovery']['prior_acquisition']=write(Path(ref['path']),prior)
    with pytest.raises(ValueError):layout.validate_acquisition_layout(contract,path)
    assert not (root/'acquisition').exists() and not (root/'analysis').exists()


@pytest.mark.parametrize('tool', ['acquire','evaluate'])
def test_entrypoints_reject_wrong_root_before_analytical_checks_or_dispatch(tmp_path,monkeypatch,modules,tool):
    _,_,acquire,evaluate=modules
    contract,path,root=fixture_contract(tmp_path,monkeypatch,modules)
    contract['acquisition_root']=str(tmp_path/'original')
    write(path,contract)
    selected=acquire if tool=='acquire' else evaluate
    def unexpected(*a,**k):raise AssertionError('invalid layout reached downstream owner')
    monkeypatch.setattr(selected.analysis,'_q1_contract',unexpected)
    monkeypatch.setattr(sys,'argv',[tool,*(['labels'] if tool=='evaluate' else []),'--contract',str(path)])
    with pytest.raises(ValueError,match='acquisition root'):selected.main()
    assert not (root/'acquisition').exists() and not (root/'analysis').exists()


def test_acquire_uses_bound_override_preserves_prior_attempt_and_exclusive_output(tmp_path,monkeypatch,modules):
    _,_,acquire,_=modules
    contract,path,root=fixture_contract(tmp_path,monkeypatch,modules)
    ref=write(path,contract)
    prior=Path(contract['recovery']['prior_acquisition']['path']);before=prior.read_bytes()
    write(root/'preflight/dispatch_release.json',{'contract':ref,'status':'RELEASED'})
    monkeypatch.setattr(acquire.analysis,'_q1_contract',lambda r:contract)
    monkeypatch.setenv('ROS_DOMAIN_ID','191')
    monkeypatch.setattr(sys,'argv',['acquire','--contract',str(path)])
    calls=[]
    def execute(*a,**kw):calls.append(kw);raise RuntimeError('synthetic stop before ROS')
    monkeypatch.setattr(acquire,'execute_suite',execute)
    assert acquire.main()==1
    assert len(calls)==1 and calls[0]['runs_root']==str(root/'runs')
    assert calls[0]['run_id']==contract['runs'][0]['run_id']
    assert str(root/'acquisition') in calls[0]['summary_output']
    result=json.loads((root/'acquisition/acquisition.json').read_text())
    assert result['status']=='INCOMPLETE' and result['acquisition_version']==contract['acquisition_version']
    assert prior.read_bytes()==before
    with pytest.raises(FileExistsError):acquire.main()
    assert len(calls)==1


def test_acquire_rejects_returned_run_outside_reserved_root(tmp_path,monkeypatch,modules):
    _,_,acquire,_=modules
    contract,path,root=fixture_contract(tmp_path,monkeypatch,modules)
    ref=write(path,contract);write(root/'preflight/dispatch_release.json',{'contract':ref,'status':'RELEASED'})
    monkeypatch.setattr(acquire.analysis,'_q1_contract',lambda r:contract)
    monkeypatch.setenv('ROS_DOMAIN_ID','191');monkeypatch.setattr(sys,'argv',['acquire','--contract',str(path)])
    monkeypatch.setattr(acquire,'execute_suite',lambda *a,**k:{'runs':[{
        'run_id':contract['runs'][0]['run_id'],'classification':{'passed':True},
        'run_directory':str(tmp_path/'elsewhere'/contract['runs'][0]['run_id'])}]})
    assert acquire.main()==1
    result=json.loads((root/'acquisition/acquisition.json').read_text())
    assert 'reserved acquisition root' in result['failure']


def test_evaluation_routes_only_to_recovery_root(tmp_path,monkeypatch,modules):
    _,_,_,evaluate=modules
    contract,path,root=fixture_contract(tmp_path,monkeypatch,modules)
    write(path,contract);write(root/'study_manifest.json',{})
    monkeypatch.setattr(evaluate.analysis,'_q1_contract',lambda r:contract)
    calls=[]
    def freeze(manifest,output,**kw):calls.append((manifest,output,kw))
    monkeypatch.setattr(evaluate.q1_study,'freeze_q1_study_labels',freeze)
    monkeypatch.setattr(evaluate.analysis,'freeze_q1_direction_targets',freeze)
    monkeypatch.setattr(evaluate.q1_study,'evaluate_q1_study_partition',lambda *a,**k:{'status':'EVIDENCE_UNAVAILABLE'})
    monkeypatch.setattr(sys,'argv',['evaluate','labels','--contract',str(path)])
    result=evaluate.main()
    assert result['confirmation']=='SEALED_NOT_OPENED' and len(calls)==2
    assert all(m==root/'study_manifest.json' and o.is_relative_to(root/'analysis') for m,o,_ in calls)
    def references(targets,output,**kw):
        assert all(p.is_relative_to(root/'analysis') for p in targets)
        assert output==root/'analysis/references' and kw['contract_path']==path
        return {'status':'EVIDENCE_UNAVAILABLE'}
    monkeypatch.setattr(evaluate.analysis,'evaluate_q1_direction_references',references)
    monkeypatch.setattr(sys,'argv',['evaluate','references','--contract',str(path)])
    assert evaluate.main()['status']=='EVIDENCE_UNAVAILABLE'


def test_freeze_cli_rejects_misrooted_output_before_reading_scenario(tmp_path,monkeypatch,modules):
    layout,freeze,_,_=modules
    monkeypatch.setattr(sys,'argv',['freeze','--acquisition-version',layout.SCIENCE_VERSION+'-recovery1',
                                   '--output',str(tmp_path/'contract.json')])
    monkeypatch.setattr(freeze,'load_suite',lambda *a:pytest.fail('unexpected scenario load'))
    with pytest.raises(ValueError,match='preflight'):freeze.main()


@pytest.mark.parametrize('suffix',['recovery1','recovery3','recovery4'])
def test_freeze_assembly_keeps_geometry_and_acquisition_recovery_distinct(tmp_path,monkeypatch,modules,suffix):
    layout,freeze,_,_=modules
    version=layout.SCIENCE_VERSION+'-'+suffix;root=tmp_path/suffix
    monkeypatch.setattr(layout,'ACQUISITION_ROOTS',{version:root,
        layout.SCIENCE_VERSION+'-recovery2':tmp_path/'recovery2',
        layout.SCIENCE_VERSION+'-recovery3':tmp_path/'recovery3'})
    suite=freeze.load_suite(freeze.SCENARIO)
    old_runs=freeze.build_acquisition_runs(suite,freeze.expand_suite(suite)[0],tmp_path/'recovery3',layout.SCIENCE_VERSION+'-recovery3')
    old_source=write(tmp_path/'old_source.json',{})
    old={'runs':old_runs,'source_files':[old_source]}
    original_read=Path.read_text
    def read(path,*a,**k):
        if suffix=='recovery4' and path==tmp_path/'recovery3/preflight/contract.json':return json.dumps(old)
        if str(path).endswith('/m1a_labels_v1/geometry_1.json'):
            return json.dumps({'basins':[]})
        if str(path).endswith('/m1a_labels_v1_recovery1/labels.json'):
            return json.dumps({'numerical_geometry_recovery':{
                'recovery_manifest_path':'/synthetic/geometry_recovery.json',
                'original_analyzer_snapshot_path':'/synthetic/original.py'}})
        return original_read(path,*a,**k)
    monkeypatch.setattr(Path,'read_text',read)
    monkeypatch.setattr(freeze,'receipt',lambda path:{'path':str(Path(path)), 'sha256':'0'*64})
    def git(command,**kw):
        if 'branch' in command:return 'feature/gesc-gaussian-robustness-v2\n'
        if 'ls-files' in command:return b''
        return '0'*40+'\n'
    monkeypatch.setattr(freeze.subprocess,'check_output',git)
    monkeypatch.setattr(freeze,'validate_acquisition_layout',lambda *a:root)
    from ros_esc.plotting_scripts import q1_study
    monkeypatch.setattr(q1_study,'verify_q1_geometry',lambda *a:None)
    monkeypatch.setattr(sys,'argv',['freeze','--acquisition-version',version])
    freeze.main()
    contract=json.loads((root/'preflight/contract.json').read_text())
    assert contract['geometry_recovery']['path'].endswith('/m1a_labels_v1_recovery1/labels.json')
    assert set(contract['recovery'])==({'amendment','source_correction'} if suffix=='recovery4' else
                                      {'amendment','closure','prior_acquisition'} |
                                      ({'source_correction'} if suffix=='recovery3' else set()))
    if suffix=='recovery3':
        assert contract['recovery']['amendment']['path'].endswith('/q1_acquisition_recovery3_plan.md')
        assert contract['recovery']['source_correction']['path'].endswith('/q1_event_attribution_plan.md')
        assert contract['recovery']['closure']['path']==str(tmp_path/'recovery2/acquisition_closed.json')
    if suffix=='recovery4':
        assert contract['runs'][:2]==old_runs[:2]
        assert contract['execution']['outer_acquisition_ceiling_sec']==600.
        assert [r['path'] for r in contract['imports']['input_files']]==[
            str(tmp_path/'recovery3/acquisition'/f'input_{seed}.json') for seed in (26090911,26090912)]
        assert old_source['path'] in [r['path'] for r in contract['source_files']]
        for plan in contract['runs'][2:]:
            assert 'recovery4-confirmation' in plan['run_id']
            actual=freeze.runner.execute_suite(freeze.SCENARIO,'mattb',case_ids=[plan['case_id']],
                runs_root=root/'runs',gui=False,dry_run=True,run_id=plan['run_id'])['runs'][0]
            assert actual['launch_argv']==plan['launch_argv']
    assert contract['acquisition_version']==version and contract['version']==layout.SCIENCE_VERSION
    assert contract['execution']['runs_root']==str(root/'runs')
