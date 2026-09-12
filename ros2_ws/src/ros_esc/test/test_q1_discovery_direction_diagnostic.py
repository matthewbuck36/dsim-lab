"""Finite discovery diagnostic authorization and unchanged analytic references.

Fixtures contain synthetic streams and file receipts only. No retained study,
confirmation science, ROS graph or Gazebo field is opened by these tests.
"""

from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import v2_direction_reference as numeric
from ros_esc.scenario_runner import aggregate_field_truth as truth
from test_q1_direction_references import (analytic_rows, freeze, receipt, study,
                                          write_json)


def forbid_model(monkeypatch):
    monkeypatch.setattr(truth, '_model',
                        lambda *a, **k: pytest.fail('invalid boundary reached model construction'))


def test_default_still_requires_both_partitions_before_output(study, monkeypatch):
    path, _ = freeze(study, 'discovery')
    forbid_model(monkeypatch)
    output = study['directory']/'default_one_partition'
    with pytest.raises(ValueError, match='both|partition'):
        analysis.evaluate_q1_direction_references(
            [path], output, contract_path=study['manifest']['contract']['path'])
    assert not output.exists()


def test_default48_still_checks_passing_confirmation_nomination(study, monkeypatch):
    paths = [freeze(study, part)[0] for part in analysis.Q1_PARTITION_SEEDS]
    nomination = Path(study['nomination']['path'])
    content = json.loads(nomination.read_text())
    content['status'] = 'FAIL'
    write_json(nomination, content)
    forbid_model(monkeypatch)
    output = study['directory']/'default_bad_nomination'
    with pytest.raises(ValueError):
        analysis.evaluate_q1_direction_references(
            paths, output, contract_path=study['manifest']['contract']['path'])
    assert not output.exists()


def diagnostic_contract(study, targets_path, *, distinct_historical_analyzer=False):
    """Synthetic historic closure with real frozen-source and trace receipts."""
    directory = study['directory']
    old_ref = study['manifest']['contract']
    targets = json.loads(targets_path.read_text())
    source = Path(analysis.__file__).resolve()
    repository = next(p for p in source.parents if (p/'AGENTS.md').is_file())
    old_snapshot = directory/'original_analyzer_snapshot.py'
    old_snapshot.write_bytes(source.read_bytes() +
        (b'\n# Synthetic closed analyzer before the diagnostic extension.\n' if distinct_historical_analyzer else b''))
    old_digest=receipt(old_snapshot)['sha256']
    if distinct_historical_analyzer:
        old=deepcopy(study['contract'])
        next(r for r in old['source_files'] if r['path']==str(source))['sha256']=old_digest
        old_ref=write_json(Path(old_ref['path']),old)
        study['manifest']['contract']=old_ref
        manifest_ref=write_json(study['path'],study['manifest'])
        targets.update(contract=old_ref,study_manifest=manifest_ref)
        write_json(targets_path,targets)
    closed = write_json(directory/'study_closed.json', {
        'version':analysis.Q1_VERSION, 'status':'CLOSED_EVIDENCE_UNAVAILABLE', 'contract':old_ref,
        'scientific_confirmation':'SEALED_NOT_OPENED', 'pilot_released':False,
        'retained_artifacts':[receipt(targets_path),
            *[{k:r[k] for k in ('path','sha256')} for r in targets['input_traces']]]})
    checkpoint = write_json(directory/'checkpoint.json', {
        'files':[{'path':str(source.relative_to(repository)), 'sha256':old_digest}],
        'retained_logs':[closed], 'artifacts':[receipt(old_snapshot)]})
    value = {'version':'q1-discovery-direction-diagnostic-v1',
        'original_contract':old_ref, 'study_closed':closed, 'checkpoint':checkpoint,
        'old_analyzer_snapshot':receipt(old_snapshot), 'frozen_targets':receipt(targets_path),
        'analyzer_transition':{'path':str(source), 'old_sha256':old_digest,
                               'new_sha256':receipt(source)['sha256']},
        'current_source_files':deepcopy(study['contract']['source_files']) + [receipt(p) for p in (
            repository/'docs/codex/gesc_gaussian/v2/q1_discovery_direction_plan.md',
            repository/'docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py',
            Path(__file__).resolve())],
        'input_traces':[{k:r[k] for k in ('path','sha256')} for r in targets['input_traces']],
        'partition':'discovery', 'seeds':[26090911,26090912],
        'target_numbers':list(range(1,13)), 'fixed_anchor_count':24, 'job_timeout_sec':300,
        'reference':deepcopy(study['contract']['reference'])}
    path = directory/'diagnostic_contract.json'
    write_json(path,value)
    return path, value


def diagnostic(study, targets, contract, output):
    return analysis.evaluate_q1_direction_references(
        [targets], output, contract_path=study['manifest']['contract']['path'],
        diagnostic_contract_path=contract)


def reseal_targets(path, targets, diag_path, diag):
    """Change a synthetic receipt coherently so semantic guards are exercised."""
    updated = write_json(path,targets)
    old = diag['frozen_targets']
    closed_path = Path(diag['study_closed']['path'])
    closed = json.loads(closed_path.read_text())
    closed['retained_artifacts'] = [updated if r==old else r for r in closed['retained_artifacts']]
    diag['frozen_targets'] = updated
    diag['study_closed'] = write_json(closed_path,closed)
    checkpoint_path = Path(diag['checkpoint']['path'])
    checkpoint = json.loads(checkpoint_path.read_text())
    checkpoint['retained_logs'] = [diag['study_closed']]
    diag['checkpoint'] = write_json(checkpoint_path,checkpoint)
    write_json(diag_path,diag)


def guard_confirmation_files(study, monkeypatch):
    directories = [Path(r['run_directory']) for r in study['manifest']['runs']
                   if r['partition']=='confirmation']
    originals = {name:getattr(Path,name) for name in ('read_bytes','read_text')}
    for name, original in originals.items():
        def guarded(path, *args, _original=original, **kwargs):
            assert not any(path.resolve().is_relative_to(root) for root in directories), \
                'discovery diagnostic attempted confirmation file access'
            return _original(path,*args,**kwargs)
        monkeypatch.setattr(Path,name,guarded)


def test_explicit_diagnostic_keeps24_empty_slots_and_never_opens_confirmation(study, monkeypatch):
    targets, _ = freeze(study,'discovery')
    contract, _ = diagnostic_contract(study,targets)
    guard_confirmation_files(study,monkeypatch)
    forbid_model(monkeypatch)
    output = study['directory']/'diagnostic'
    result = diagnostic(study,targets,contract,output)
    assert result['status']=='COMPLETE_DIAGNOSTIC'
    assert result['qualification_status']=='NOT_EVALUATED' and result['nomination'] is None
    assert result['confirmation']=='SEALED' and result['pilot_released'] is False
    assert result['all']['fixed_anchor_count']==24
    assert result['all']['eligible_informative_count']==0
    assert result['all']['averaging_availability'] is None
    assert len(list(output.glob('anchor_*.json')))==24
    assert {r['seed'] for r in result['results']}=={26090911,26090912}
    assert len(study['reads'])==2


def test_only_explicit_verified_lineage_accepts_a_changed_analyzer(study,monkeypatch):
    targets,_=freeze(study,'discovery')
    contract,_=diagnostic_contract(study,targets,distinct_historical_analyzer=True)
    # Ordinary historical freshness remains strict despite the new route.
    with pytest.raises(ValueError):analysis._q1_contract(study['manifest']['contract'])
    forbid_model(monkeypatch)
    result=diagnostic(study,targets,contract,study['directory']/'lineage_diagnostic')
    assert result['status']=='COMPLETE_DIAGNOSTIC' and result['all']['fixed_anchor_count']==24
    with pytest.raises(ValueError):analysis._q1_contract(study['manifest']['contract'])


@pytest.mark.parametrize('outcome',['analytic','weak_output','fallback','uninformative'])
def test_diagnostic_per_anchor_matches_unchanged_default_discovery_numeric_owner(study, monkeypatch,outcome):
    rows = analytic_rows(study['normalized'][0],weak=outcome=='weak_output',fallback=outcome=='fallback')
    monkeypatch.setattr(analysis,'prepare_q1_direction_inputs',
                        lambda *a,**k:(deepcopy(rows),study['qualification']))
    paths = [freeze(study,part)[0] for part in analysis.Q1_PARTITION_SEEDS]
    contract, _ = diagnostic_contract(study,paths[0])
    monkeypatch.setattr(truth,'_model',lambda *a,**k:(object(),None))
    monkeypatch.setattr(truth,'evaluate_raw_cost',
                        lambda model,x,y,angle: -1. if outcome=='uninformative' else math.cos(angle))
    default = analysis.evaluate_q1_direction_references(
        paths,study['directory']/'default48',contract_path=study['manifest']['contract']['path'])
    guard_confirmation_files(study,monkeypatch)
    result = diagnostic(study,paths[0],contract,study['directory']/'diagnostic24')
    expected = [row for row in default['results'] if row['partition']=='discovery']
    assert result['results']==expected
    assert default['all']['fixed_anchor_count']==48 and result['all']['fixed_anchor_count']==24
    assert result['status']=='COMPLETE_DIAGNOSTIC' and result['qualification_status']=='NOT_EVALUATED'
    assert result['all']['eligible_informative_count']==(0 if outcome=='uninformative' else 24)
    if outcome=='analytic':
        assert result['all']['v2_median_error_deg']<1e-5
        assert result['all']['averaging_availability']==1.
    elif outcome=='weak_output':
        assert result['all']['v2_median_error_deg'] is None
        assert result['all']['missing_or_weak_output_count']==24
    elif outcome=='fallback':
        assert result['all']['fallback_count']==24 and result['all']['averaging_availability']==0.
    else:
        assert result['all']['unavailable_reasons']=={'uninformative_reference':24}


@pytest.mark.parametrize('fault',['old_snapshot','lineage','numerical_source','dropped_source',
                                  'extra_source','duplicate_source','closed_status','opened_confirmation',
                                  'checkpoint_owner','empty_checkpoint','target_receipt','trace_receipt','reference','extra_key'])
def test_invalid_diagnostic_provenance_fails_before_output_or_model(study,monkeypatch,fault):
    targets, _ = freeze(study,'discovery')
    path, value = diagnostic_contract(study,targets)
    if fault=='old_snapshot':
        Path(value['old_analyzer_snapshot']['path']).write_text('changed historical owner')
    elif fault=='lineage':value['analyzer_transition']['old_sha256']='0'*64
    elif fault=='numerical_source':
        next(r for r in value['current_source_files'] if r['path']==str(Path(numeric.__file__).resolve()))['sha256']='0'*64
    elif fault=='dropped_source':value['current_source_files'].pop()
    elif fault=='extra_source':
        extra=study['directory']/'unapproved_new_owner.py';extra.write_text('changed_model=True')
        value['current_source_files'].append(receipt(extra))
    elif fault=='duplicate_source':value['current_source_files'].append(value['current_source_files'][0])
    elif fault in ('closed_status','opened_confirmation'):
        p=Path(value['study_closed']['path']);doc=json.loads(p.read_text())
        if fault=='closed_status':doc['status']='PASS'
        else:doc['scientific_confirmation']='OPENED'
        value['study_closed']=write_json(p,doc)
    elif fault in ('checkpoint_owner','empty_checkpoint'):
        p=Path(value['checkpoint']['path']);doc=json.loads(p.read_text())
        if fault=='checkpoint_owner':doc['files'][0]['sha256']='0'*64
        else:doc['artifacts']=[]
        value['checkpoint']=write_json(p,doc)
    elif fault=='target_receipt':targets.write_text('{}')
    elif fault=='trace_receipt':Path(value['input_traces'][0]['path']).write_text('{}')
    elif fault=='reference':value['reference']['anchor_window_sec']=.1
    else:value['bypass_nomination']=True
    write_json(path,value)
    forbid_model(monkeypatch)
    output=study['directory']/'invalid_diagnostic'
    with pytest.raises(ValueError):diagnostic(study,targets,path,output)
    assert not output.exists()


@pytest.mark.parametrize('fault',['duplicate','missing','extra','timing','source_stamp','foreign_seed'])
def test_resealed_invalid_target_population_or_timing_fails_before_model(study,monkeypatch,fault):
    targets, _ = freeze(study,'discovery')
    path,value=diagnostic_contract(study,targets)
    doc=json.loads(targets.read_text())
    if fault=='duplicate':doc['targets'][-1]=deepcopy(doc['targets'][0])
    elif fault=='missing':doc['targets'].pop()
    elif fault=='extra':doc['targets'].append(deepcopy(doc['targets'][0]))
    elif fault=='timing':doc['targets'][0]['target_ns']+=1
    elif fault=='source_stamp':doc['targets'][0]['source_stamp_ns']=99
    else:doc['targets'][0]['seed']=26090913
    reseal_targets(targets,doc,path,value)
    forbid_model(monkeypatch)
    output=study['directory']/'invalid_targets'
    with pytest.raises(ValueError):diagnostic(study,targets,path,output)
    assert not output.exists()


@pytest.mark.parametrize('fault',['duplicate','extra','orphan','confirmation'])
def test_discovery_trace_metadata_rejected_before_foreign_file_read(study,monkeypatch,fault):
    targets,_=freeze(study,'discovery')
    path,value=diagnostic_contract(study,targets)
    doc=json.loads(targets.read_text())
    original=deepcopy(doc['input_traces'])
    if fault=='duplicate':doc['input_traces'][1]=deepcopy(doc['input_traces'][0])
    elif fault=='extra':doc['input_traces'].append(deepcopy(doc['input_traces'][0]))
    elif fault=='orphan':doc['input_traces'][0]['run']['run_id']='orphan_run'
    else:
        foreign=next(r for r in study['manifest']['runs'] if r['seed']==26090913)
        trace=deepcopy(json.loads(Path(original[0]['path']).read_text()));trace['run']=foreign
        foreign_path=Path(foreign['run_directory'])/'foreign_trace.json'
        doc['input_traces'][0]={**write_json(foreign_path,trace),'run':foreign}
    old_closed=Path(value['study_closed']['path'])
    closed=json.loads(old_closed.read_text())
    old_refs=[{k:r[k] for k in ('path','sha256')} for r in original]
    new_refs=[{k:r[k] for k in ('path','sha256')} for r in doc['input_traces']]
    closed['retained_artifacts']=[r for r in closed['retained_artifacts'] if r not in old_refs]+new_refs
    value['study_closed']=write_json(old_closed,closed)
    value['input_traces']=new_refs
    reseal_targets(targets,doc,path,value)
    guard_confirmation_files(study,monkeypatch)
    forbid_model(monkeypatch)
    output=study['directory']/'invalid_traces'
    with pytest.raises(ValueError):diagnostic(study,targets,path,output)
    assert not output.exists()


def test_diagnostic_timeout_retains_first_anchor_without_final_and_refuses_overwrite(study,monkeypatch):
    rows=analytic_rows(study['normalized'][0])
    monkeypatch.setattr(analysis,'prepare_q1_direction_inputs',
                        lambda *a,**k:(deepcopy(rows),study['qualification']))
    targets,_=freeze(study,'discovery')
    path,_=diagnostic_contract(study,targets)
    monkeypatch.setattr(truth,'_model',lambda *a,**k:(object(),None))
    monkeypatch.setattr(truth,'evaluate_raw_cost',lambda model,x,y,angle:math.cos(angle))
    actual=numeric.integrate_stationary_harmonics
    calls=[]
    def bounded(*args,**kwargs):
        calls.append(None)
        if len(calls)==2:raise TimeoutError('synthetic second-anchor deadline')
        return actual(*args,**kwargs)
    monkeypatch.setattr(numeric,'integrate_stationary_harmonics',bounded)
    output=study['directory']/'partial_diagnostic'
    with pytest.raises(TimeoutError):diagnostic(study,targets,path,output)
    assert (output/'started.json').is_file()
    saved=output/'anchor_26090911_01.json'
    assert json.loads(saved.read_text())['informative'] is True
    before=receipt(saved)
    assert not (output/'references.json').exists()
    assert len(list(output.glob('anchor_*.json')))==1
    forbid_model(monkeypatch)
    with pytest.raises(FileExistsError):diagnostic(study,targets,path,output)
    assert receipt(saved)==before and not (output/'references.json').exists()


@pytest.mark.parametrize('stage',['before_second_model','after_last_anchor'])
def test_changed_receipts_during_job_stop_model_or_final_publication(study,monkeypatch,stage):
    rows=analytic_rows(study['normalized'][0])
    monkeypatch.setattr(analysis,'prepare_q1_direction_inputs',
                        lambda *a,**k:(deepcopy(rows),study['qualification']))
    targets,frozen=freeze(study,'discovery')
    path,_=diagnostic_contract(study,targets)
    model_calls=[]
    def model(*args,**kwargs):
        model_calls.append(None)
        if stage=='before_second_model':
            assert len(model_calls)==1, 'changed input reached second model construction'
            Path(frozen['input_traces'][1]['path']).write_text('{}')
        return object(),None
    monkeypatch.setattr(truth,'_model',model)
    monkeypatch.setattr(truth,'evaluate_raw_cost',lambda model,x,y,angle:math.cos(angle))
    actual=numeric.integrate_stationary_harmonics
    integrated=[]
    def integrate(*args,**kwargs):
        value=actual(*args,**kwargs)
        integrated.append(None)
        if stage=='after_last_anchor' and len(integrated)==24:path.write_text('{}')
        return value
    monkeypatch.setattr(numeric,'integrate_stationary_harmonics',integrate)
    output=study['directory']/'changed_during_job'
    with pytest.raises(ValueError):diagnostic(study,targets,path,output)
    assert len(model_calls)==(1 if stage=='before_second_model' else 2)
    assert len(list(output.glob('anchor_*.json')))==(12 if stage=='before_second_model' else 24)
    assert (output/'started.json').exists() and not (output/'references.json').exists()


@pytest.fixture
def workflow(tmp_path,monkeypatch):
    import importlib
    repository=next(p for p in Path(analysis.__file__).resolve().parents if (p/'AGENTS.md').is_file())
    monkeypatch.syspath_prepend(str(repository/'docs/codex/gesc_gaussian/v2/tools'))
    tool=importlib.import_module('q1_discovery_direction')
    monkeypatch.setattr(tool,'OUTPUT',tmp_path/'diagnostic')
    return tool


@pytest.mark.parametrize('fault',['branch','existing_analysis'])
def test_workflow_freeze_rejects_wrong_context_before_old_input_reads(workflow,monkeypatch,fault):
    branch='feature/gesc-gaussian-robustness-v1' if fault=='branch' else 'feature/gesc-gaussian-robustness-v2'
    monkeypatch.setattr(workflow.subprocess,'check_output',lambda *a,**k:branch+'\n')
    if fault=='existing_analysis':(workflow.OUTPUT/'analysis').mkdir(parents=True)
    monkeypatch.setattr(Path,'read_text',lambda *a,**k:pytest.fail('freeze rejection must precede historical reads'))
    with pytest.raises(ValueError if fault=='branch' else FileExistsError):workflow.freeze()
    assert not (workflow.OUTPUT/'preflight/contract.json').exists()


@pytest.mark.parametrize('fault',['absent','status','contract'])
def test_workflow_evaluate_requires_matching_released_receipt_before_owner(workflow,monkeypatch,fault):
    preflight=workflow.OUTPUT/'preflight';preflight.mkdir(parents=True)
    contract=write_json(preflight/'contract.json',{'synthetic':True})
    monkeypatch.setattr(workflow,'selected_environment',lambda:{'fixture':True})
    monkeypatch.setattr(workflow,'installed_entry_points',lambda:{'fixture':'installed'})
    proof=write_json(preflight/'proof.json',{})
    release={'status':'INCOMPLETE' if fault=='status' else 'RELEASED','contract':contract,
             'environment':{'fixture':True},'installed_entry_points':{'fixture':'installed'},
             'job_timeout_sec':300,'checkpoint':proof,'validation_evidence':[proof]}
    if fault=='contract':release['contract']={'path':contract['path'],'sha256':'0'*64}
    if fault!='absent':write_json(preflight/'dispatch_release.json',release)
    monkeypatch.setattr(workflow.analysis,'evaluate_q1_direction_references',
                        lambda *a,**k:pytest.fail('unreleased workflow reached numerical owner'))
    with pytest.raises(FileNotFoundError if fault=='absent' else ValueError):workflow.evaluate()
    assert not (workflow.OUTPUT/'analysis').exists()
