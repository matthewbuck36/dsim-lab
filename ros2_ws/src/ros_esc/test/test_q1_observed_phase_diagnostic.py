"""Observed-phase batch authorization and algebraic sensitivity boundaries.

Synthetic retained-file/analytic-stream fixtures only; no recorded field,
confirmation bag, ROS graph or Gazebo execution is used.
"""

from copy import deepcopy
import json
import math
from pathlib import Path
import sys

import pytest

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import v2_direction_reference as numeric
from ros_esc.scenario_runner import aggregate_field_truth as truth
from test_q1_direction_references import analytic_rows, freeze, receipt, study, write_json
from test_q1_discovery_direction_diagnostic import (
    diagnostic_contract, diagnostic, forbid_model, guard_confirmation_files)


VERSION='q1-observed-phase-direction-diagnostic-v1'
METHOD={'version':'observed-phase-periodic-v1','alpha_per_sec':1.,'sensor_radius_m':.18,
        'maximum_objective_evaluations':25000,'normalized_component_error_limit':1e-6,
        'informative_absolute_floor':1e-6,'informative_error_multiplier':20.}
LATENT={'version':'recorded-one-cycle-50-50-v1','instant_weight':.5,'recorded_mean_weight':.5,
        'output_magnitude_floor':1e-6,'actual_blend_component_tolerance':1e-12}


def observed_fixture(study,monkeypatch,*,empty=False,variable=False,fallback=False,
                     full_population=False,instant_offset_rad=0.):
    if not empty:
        rows=analytic_rows(study['normalized'][0])
        if not full_population:rows=rows[:102]  # Two causal anchors; the other22 remain explicitly missing.
        for index,row in enumerate(rows):
            if variable:row['world_phase_rad']=math.remainder(math.tau/3*index*.1+.2*math.sin(math.tau/3*index*.1),math.tau)
            row['method'].update(diagnostic_sequence=index+1,blend_applied=not fallback,
                averaging_qualified=not fallback,usable_averaging=not fallback,fallback_used=fallback,
                fallback_reason='weak_cycle_direction' if fallback else '')
            if instant_offset_rad:
                x,y=row['method']['aligned_instant_world'];c,s=math.cos(instant_offset_rad),math.sin(instant_offset_rad)
                vector=[c*x-s*y,s*x+c*y]
                row['method'].update(aligned_instant_world=vector,v2_output_world=vector)
            row.update(filter_stamp_ns=row['stamp_ns'],first_diagnostic_bag_stamp_ns=row['stamp_ns']+5000,
                       bag_timestamp_ns=row['stamp_ns']+5000)
        monkeypatch.setattr(analysis,'prepare_q1_direction_inputs',
                            lambda *a,**k:(deepcopy(rows),study['qualification']))
    targets_path,targets=freeze(study,'discovery')
    d1_path,d1=diagnostic_contract(study,targets_path)
    directory=study['directory'];d1_ref=receipt(d1_path)
    source=Path(analysis.__file__).resolve()
    repo=next(p for p in source.parents if (p/'AGENTS.md').is_file())
    owners=[source,Path(numeric.__file__).resolve(),repo/'docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py']
    transitions=[]
    for index,owner in enumerate(owners):
        snapshot=directory/f'previous_owner_{index}.py';snapshot.write_bytes(owner.read_bytes())
        transitions.append({'path':str(owner),'old_sha256':receipt(owner)['sha256'],
                            'new_sha256':receipt(owner)['sha256'],'old_snapshot':receipt(snapshot)})
    traces={item['run']['run_id']:json.loads(Path(item['path']).read_text()) for item in targets['input_traces']}
    input_map={r['path']:r['sha256'] for r in d1['current_source_files']}
    for ref in [d1_ref,receipt(targets_path),*targets['input_traces']]:input_map[ref['path']]=ref['sha256']
    for trace in traces.values():
        for ref in trace['run']['input_files']:input_map[ref['path']]=ref['sha256']
    audit_rows=[]
    for target in targets['targets']:
        common={k:target[k] for k in ('seed','number','run_id','target_ns','source_stamp_ns','source_sequence')}
        if target['observation_index'] is None:
            audit_rows.append({**common,'unavailable_reason':'missing_causal_anchor'})
            continue
        row=traces[target['run_id']]['observations'][target['observation_index']]
        instant=row['method']['aligned_instant_world'];magnitude=math.hypot(*instant)
        audit_rows.append({**common,'diagnostic_sequence':row['method']['diagnostic_sequence'],
            'diagnostic_stamp_ns':row['filter_stamp_ns'],
            'diagnostic_bag_stamp_ns':row['first_diagnostic_bag_stamp_ns'],
            'observation_sha256':row['observation_sha256'],
            'readiness_eligible':row['readiness_eligible'],'first_recorded_message_exact_match':True,
            'legacy_exact_key':row['observation_wire']['legacy_cost_source_timestamp_sec'],'missing':[],
            'recorded':{'instant_world':list(instant),'instant_magnitude':magnitude,
                'mean_world':list(instant),'mean_magnitude':magnitude,'output_magnitude':magnitude,
                'blend_weight':0. if fallback else .5,
                'cycle_mean_world_x':[instant[0]]*3,'cycle_mean_world_y':[instant[1]]*3,
                'cycle_coverage_valid':[True]*3,'cycle_sector_counts':[3]*36,
                'max_pair_angle_rad':0.,'cycle_variability':0.,'magnitude_floor':1e-6,
                'completed_revolutions':3,'mean_full':True,'coverage_valid':True,'cycles_valid':not fallback,
                'qualified':not fallback,'fallback_used':fallback,'output_valid':True,'blend_allowed':True,
                'fallback_reason':'weak_cycle_direction' if fallback else '', 'output_units':'cost_units_per_metre',
                'cycle_start_ns':[row['stamp_ns']-int(v*1e9) for v in (9,6,3)],
                'cycle_end_ns':[row['stamp_ns']-int(v*1e9) for v in (6,3,0)],
                'rolling_start_ns':row['stamp_ns']-3_000_000_000,'rolling_end_ns':row['stamp_ns']}})
    audit_dir=directory/'confidence';audit_dir.mkdir()
    extractor=audit_dir/'extract.py';extractor.write_text('# synthetic receipt fixture, no extraction\n')
    audit={'version':'recorded_cycle_confidence_v1','targets':audit_rows,
        'inputs_and_sources_unchanged_after_extraction':True,'confirmation_opened':False,
        'new_numerical_reference_or_field_evaluation':False,'input_and_source_sha256':input_map,
        'script_sha256':receipt(extractor)['sha256']}
    audit_ref=write_json(audit_dir/'result.json',audit)
    manifest_ref=write_json(audit_dir/'manifest.json',{'exit_code':0,'files':{
        'result.json':{'sha256':audit_ref['sha256']},'extract.py':{'sha256':receipt(extractor)['sha256']}}})
    closed=write_json(directory/'d1_closed.json',{
        'version':d1['version'],'status':'CLOSED_COMPLETE_DIAGNOSTIC','contract':d1_ref,
        'qualification_status':'NOT_EVALUATED','confirmation':'SEALED','nomination':None,'pilot_released':False,
        'source_unchanged_through_analysis':True,'process_exit_code':0,'fixed_anchor_count':24,
        'retained_artifacts':[d1_ref,receipt(targets_path),*d1['input_traces']]})
    checkpoint=write_json(directory/'d1_checkpoint.json',{
        'files':[{'path':str(Path(t['path']).relative_to(repo)),'sha256':t['old_sha256']} for t in transitions],
        'retained_logs':[closed,d1_ref,audit_ref,manifest_ref],
        'artifacts':[t['old_snapshot'] for t in transitions]})
    current_sources=deepcopy(d1['current_source_files'])+[receipt(repo/name) for name in (
        'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_plan.md',
        'docs/codex/gesc_gaussian/v2/q1_observed_phase_reference_design.md',
        'ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py',
        'ros2_ws/src/ros_esc/test/test_q1_observed_phase_diagnostic.py')]
    contract={'version':VERSION,'original_contract':d1['original_contract'],'study_closed':d1['study_closed'],
        'preceding_diagnostic_contract':d1_ref,'preceding_diagnostic_closed':closed,
        'preceding_diagnostic_checkpoint':checkpoint,'frozen_targets':receipt(targets_path),
        'source_transitions':transitions,'current_source_files':current_sources,'input_traces':d1['input_traces'],
        'confidence_audit':audit_ref,'confidence_audit_manifest':manifest_ref,'partition':'discovery',
        'seeds':[26090911,26090912],'target_numbers':list(range(1,13)), 'fixed_anchor_count':24,
        'job_timeout_sec':300,'reference':d1['reference'],'observed_phase_reference':METHOD,'latent_blend':LATENT}
    path=directory/'observed_contract.json';write_json(path,contract)
    return {'path':path,'contract':contract,'targets_path':targets_path,'targets':targets,
            'audit':audit,'d1_path':d1_path,'traces':traces,'repository':repo}


def evaluate(study,fixture,output):
    return analysis.evaluate_q1_direction_references(
        [fixture['targets_path']],output,contract_path=study['manifest']['contract']['path'],
        observed_phase_contract_path=fixture['path'])


def reseal_audit(fixture):
    contract=fixture['contract'];audit_path=Path(contract['confidence_audit']['path'])
    audit_path.write_text(json.dumps(fixture['audit'],sort_keys=True,allow_nan=True))
    contract['confidence_audit']=receipt(audit_path)
    manifest_path=Path(contract['confidence_audit_manifest']['path'])
    manifest=json.loads(manifest_path.read_text())
    manifest['files']['result.json']['sha256']=contract['confidence_audit']['sha256']
    contract['confidence_audit_manifest']=write_json(manifest_path,manifest)
    cp_path=Path(contract['preceding_diagnostic_checkpoint']['path'])
    cp=json.loads(cp_path.read_text())
    updates={contract[k]['path']:contract[k] for k in ('confidence_audit','confidence_audit_manifest')}
    cp['retained_logs']=[updates.get(ref['path'],ref) for ref in cp['retained_logs']]
    contract['preceding_diagnostic_checkpoint']=write_json(cp_path,cp)
    write_json(fixture['path'],contract)


@pytest.mark.parametrize('fault',['missing_owner','duplicate_owner','snapshot','old_hash','new_hash',
                                  'changed_runtime','missing_new_receipt','extra_receipt','wrong_method',
                                  'wrong_weight','old_closure','checkpoint','audit_hash','target_hash'])
def test_observed_contract_faults_stop_before_output_or_model(study,monkeypatch,fault):
    f=observed_fixture(study,monkeypatch,empty=True);c=f['contract']
    if fault=='missing_owner':c['source_transitions'].pop()
    elif fault=='duplicate_owner':c['source_transitions'][-1]=deepcopy(c['source_transitions'][0])
    elif fault=='snapshot':Path(c['source_transitions'][0]['old_snapshot']['path']).write_text('changed')
    elif fault=='old_hash':c['source_transitions'][1]['old_sha256']='0'*64
    elif fault=='new_hash':c['source_transitions'][1]['new_sha256']='0'*64
    elif fault=='changed_runtime':
        next(r for r in c['current_source_files'] if r['path'].endswith('/v2_stream.py'))['sha256']='0'*64
    elif fault=='missing_new_receipt':c['current_source_files'].pop()
    elif fault=='extra_receipt':
        extra=study['directory']/'unapproved.py';extra.write_text('')
        c['current_source_files'].append(receipt(extra))
    elif fault=='wrong_method':c['observed_phase_reference']=dict(METHOD,alpha_per_sec=2.)
    elif fault=='wrong_weight':c['latent_blend']=dict(LATENT,instant_weight=.25)
    elif fault=='old_closure':
        p=Path(c['preceding_diagnostic_closed']['path']);doc=json.loads(p.read_text());doc['confirmation']='OPENED'
        c['preceding_diagnostic_closed']=write_json(p,doc)
    elif fault=='checkpoint':
        p=Path(c['preceding_diagnostic_checkpoint']['path']);doc=json.loads(p.read_text());doc['files'][0]['sha256']='0'*64
        c['preceding_diagnostic_checkpoint']=write_json(p,doc)
    elif fault=='audit_hash':Path(c['confidence_audit']['path']).write_text('{}')
    else:f['targets_path'].write_text('{}')
    write_json(f['path'],c);forbid_model(monkeypatch)
    output=study['directory']/'invalid_observed'
    with pytest.raises(ValueError):evaluate(study,f,output)
    assert not output.exists()


@pytest.mark.parametrize('fault',['run','source','sequence','observation_hash','diagnostic_sequence',
                                  'publication','bag_receipt','first_publication','units','duplicate','missing','extra'])
def test_supplement_must_join_exact_original_first_diagnostic_before_model(study,monkeypatch,fault):
    f=observed_fixture(study,monkeypatch,fallback=True)
    row=f['audit']['targets'][0]
    if fault=='run':row['run_id']='another_run'
    elif fault=='source':row['source_stamp_ns']+=1
    elif fault=='sequence':row['source_sequence']+=1
    elif fault=='observation_hash':row['observation_sha256']='0'*64
    elif fault=='diagnostic_sequence':row['diagnostic_sequence']+=1
    elif fault=='publication':row['diagnostic_stamp_ns']+=1
    elif fault=='bag_receipt':row['diagnostic_bag_stamp_ns']+=1
    elif fault=='first_publication':row['first_recorded_message_exact_match']=False
    elif fault=='units':row['recorded']['output_units']='arbitrary_vector'
    elif fault=='duplicate':f['audit']['targets'][-1]=deepcopy(row)
    elif fault=='missing':f['audit']['targets'].pop()
    else:f['audit']['targets'].append(deepcopy(row))
    reseal_audit(f);forbid_model(monkeypatch)
    output=study['directory']/'bad_join'
    with pytest.raises(ValueError):evaluate(study,f,output)
    assert not output.exists()


def cosine_model(monkeypatch):
    monkeypatch.setattr(truth,'_model',lambda *a,**k:(object(),None))
    monkeypatch.setattr(truth,'evaluate_raw_cost',lambda model,x,y,angle:math.cos(angle))


def test_observed_missing_slots_are_retained_without_model_or_confirmation(study,monkeypatch):
    f=observed_fixture(study,monkeypatch,empty=True)
    guard_confirmation_files(study,monkeypatch);forbid_model(monkeypatch)
    result=evaluate(study,f,study['directory']/'empty_observed')
    assert result['status']=='COMPLETE_DIAGNOSTIC' and result['version']==VERSION
    assert result['qualification_status']=='NOT_EVALUATED' and result['confirmation']=='SEALED'
    assert result['pilot_released'] is False and result['nomination'] is None
    assert result['all']['fixed_anchor_count']==result['latent']['fixed_anchor_count']==24
    assert result['all']['eligible_informative_count']==result['latent']['paired_error_count']==0
    assert all(r['latent']['reason']=='missing_causal_anchor' for r in result['results'])
    assert len(list((study['directory']/'empty_observed').glob('anchor_*.json')))==24


def test_uniform_observed24_matches_primary_d1_and_actual_recorded_blends(study,monkeypatch):
    f=observed_fixture(study,monkeypatch,full_population=True)
    cosine_model(monkeypatch)
    prior=diagnostic(study,f['targets_path'],f['d1_path'],study['directory']/'d1_uniform')
    guard_confirmation_files(study,monkeypatch)
    result=evaluate(study,f,study['directory']/'observed_uniform')
    assert result['all']['eligible_informative_count']==24
    assert result['all']['usable_averaging_count']==24
    assert result['latent']['paired_error_count']==result['latent']['latent_available_count']==24
    for old,new in zip(prior['results'],result['results']):
        assert old['method']==new['method']
        assert old['world_vector']==pytest.approx(new['world_vector'],abs=1e-9)
        assert new['latent']['world_vector']==pytest.approx(new['method']['v2_output_world'],abs=1e-12)
        assert new['latent']['recorded_actual_blend_match'] is True
        assert new['latent']['error_deg']==pytest.approx(new['v2_error_deg'],abs=1e-8)
    assert result['latent']['median_error_deg']<1e-5


def test_observed_variable_rate_keeps_old_inapplicability_and_missing_slots(study,monkeypatch):
    f=observed_fixture(study,monkeypatch,variable=True,fallback=True)
    cosine_model(monkeypatch)
    old=diagnostic(study,f['targets_path'],f['d1_path'],study['directory']/'d1_variable')
    result=evaluate(study,f,study['directory']/'observed_variable')
    assert old['all']['eligible_informative_count']==0
    assert old['all']['unavailable_reasons']['variable_world_rate']==2
    assert result['all']['fixed_anchor_count']==24 and result['all']['eligible_informative_count']==2
    assert result['all']['unavailable_reasons']['missing_causal_anchor']==22
    assert result['latent']['paired_error_count']==2
    assert all(not r['cycle']['constant_rate_qualified'] for r in result['results'] if r['eligible'])


@pytest.mark.parametrize('fault,reason',[
    ('missing','recorded_mean_or_instant_missing_or_nonfinite'),
    ('not_full','recorded_mean_not_full'),('not_covered','recorded_mean_not_covered'),
    ('nonfinite','recorded_mean_or_instant_missing_or_nonfinite'),
    ('weak','latent_output_missing_or_weak')])
def test_invalid_one_cycle_mean_serializes_unavailable_without_erasing_primary(study,monkeypatch,fault,reason):
    f=observed_fixture(study,monkeypatch,fallback=True)
    recorded=f['audit']['targets'][0]['recorded']
    if fault=='missing':recorded['mean_world']=None
    elif fault=='not_full':recorded['mean_full']=False
    elif fault=='not_covered':recorded['coverage_valid']=False
    elif fault=='nonfinite':recorded['mean_world']=[math.nan,0.]
    else:recorded['mean_world']=[-x for x in recorded['instant_world']]
    reseal_audit(f);cosine_model(monkeypatch)
    output=study['directory']/'unavailable_mean'
    result=evaluate(study,f,output)
    serialized=json.loads((output/'references.json').read_text())
    assert result['all']['eligible_informative_count']==2
    assert result['latent']['paired_error_count']==1 and result['latent']['unavailable_at_eligible_count']==1
    assert result['results'][0]['latent']['reason']==reason
    assert not result['results'][0]['latent']['available']
    assert serialized['results'][0]['latent'].get('error_deg') is None
    assert serialized['status']=='COMPLETE_DIAGNOSTIC'
    assert serialized['all']['fixed_anchor_count']==serialized['latent']['fixed_anchor_count']==24


@pytest.mark.parametrize('offset,accepted',[(1e-12,True),(4e-12,False)])
def test_actual_blend_component_agreement_is_enforced_before_model(study,monkeypatch,offset,accepted):
    f=observed_fixture(study,monkeypatch)
    f['audit']['targets'][0]['recorded']['mean_world'][0]+=offset
    reseal_audit(f);output=study['directory']/'blend_match'
    if accepted:
        cosine_model(monkeypatch);result=evaluate(study,f,output)
        assert result['results'][0]['latent']['recorded_actual_blend_match'] is True
    else:
        forbid_model(monkeypatch)
        with pytest.raises(ValueError,match='blend'):evaluate(study,f,output)
        assert not output.exists()


def test_latent_comparison_reports_improvement_and_degradation_separately(study,monkeypatch):
    f=observed_fixture(study,monkeypatch,fallback=True,instant_offset_rad=.5)
    for target in f['audit']['targets']:
        if 'recorded' not in target:continue
        instant=target['recorded']['instant_world'];delta=-.5 if target['seed']==26090911 else 1.
        c,s=math.cos(delta),math.sin(delta);x,y=instant
        target['recorded']['mean_world']=[c*x-s*y,s*x+c*y]
        # Deliberately distinct three-cycle means cannot substitute for the rolling mean.
        target['recorded']['cycle_mean_world_x']=[999.]*3
        target['recorded']['cycle_mean_world_y']=[999.]*3
    reseal_audit(f);cosine_model(monkeypatch)
    result=evaluate(study,f,study['directory']/'paired_changes')
    assert result['all']['usable_averaging_count']==0
    assert result['latent']['paired_error_count']==2
    assert result['latent']['improved_count']==result['latent']['degraded_count']==1
    assert result['latent']['equal_count']==0
    assert all(r['latent']['recorded_actual_blend_match'] is None for r in result['results'] if r['eligible'])


def test_observed_timeout_retains_prior_anchor_without_final_or_overwrite(study,monkeypatch):
    f=observed_fixture(study,monkeypatch);cosine_model(monkeypatch)
    original=numeric.observed_phase_reference;calls=[]
    def reference(*args,**kwargs):
        calls.append(None)
        if len(calls)==2:raise TimeoutError('synthetic second-observed-reference timeout')
        return original(*args,**kwargs)
    monkeypatch.setattr(numeric,'observed_phase_reference',reference)
    output=study['directory']/'partial'
    with pytest.raises(TimeoutError):evaluate(study,f,output)
    assert (output/'started.json').exists() and not (output/'references.json').exists()
    assert len(list(output.glob('anchor_*.json')))==12
    first=receipt(output/'anchor_26090911_01.json')
    forbid_model(monkeypatch)
    with pytest.raises(FileExistsError):evaluate(study,f,output)
    assert receipt(output/'anchor_26090911_01.json')==first


@pytest.fixture
def workflow(tmp_path,monkeypatch):
    import importlib
    repository=next(p for p in Path(analysis.__file__).resolve().parents if (p/'AGENTS.md').is_file())
    monkeypatch.syspath_prepend(str(repository/'docs/codex/gesc_gaussian/v2/tools'))
    tool=importlib.import_module('q1_discovery_direction')
    monkeypatch.setattr(tool,'OBSERVED_OUTPUT',tmp_path/'observed')
    return tool


@pytest.mark.parametrize('stage',['freeze','evaluate'])
@pytest.mark.parametrize('version',[None,'stationary-v1','observed-phase-v1'])
def test_workflow_routes_explicit_versions_without_changing_default(workflow,monkeypatch,stage,version):
    calls=[]
    for name in ('freeze','evaluate','freeze_observed_phase','evaluate_observed_phase'):
        monkeypatch.setattr(workflow,name,lambda _name=name:(calls.append(_name) or {'selected':_name}))
    argv=['diagnostic',stage]+([] if version is None else ['--reference-version',version])
    monkeypatch.setattr(sys,'argv',argv)
    workflow.main()
    assert calls==[stage+('_observed_phase' if version=='observed-phase-v1' else '')]


def test_observed_workflow_rejects_old_version_release_before_owner(workflow,monkeypatch):
    p=workflow.OBSERVED_OUTPUT/'preflight';p.mkdir(parents=True)
    contract=write_json(p/'contract.json',{'version':VERSION})
    old_contract=write_json(p/'old_contract.json',{'version':'q1-discovery-direction-diagnostic-v1'})
    proof=write_json(p/'proof.json',{})
    release={'status':'RELEASED','contract':old_contract,'environment':{},'installed_entry_points':{},
             'job_timeout_sec':300,'checkpoint':proof,
             'validation_evidence':[proof]}
    write_json(p/'dispatch_release.json',release)
    monkeypatch.setattr(workflow,'selected_environment',lambda:{})
    monkeypatch.setattr(workflow,'installed_entry_points',lambda:{})
    monkeypatch.setattr(analysis,'evaluate_q1_direction_references',
                        lambda *a,**k:pytest.fail('wrong version reached numerical owner'))
    with pytest.raises(ValueError):workflow.evaluate_observed_phase()
    assert not (workflow.OBSERVED_OUTPUT/'analysis').exists()


def test_old48_and_discovery24_keep_the_same_empty_anchor_results(study,monkeypatch):
    paths=[freeze(study,part)[0] for part in analysis.Q1_PARTITION_SEEDS]
    d1,_=diagnostic_contract(study,paths[0])
    forbid_model(monkeypatch)
    old=analysis.evaluate_q1_direction_references(
        paths,study['directory']/'original48',contract_path=study['manifest']['contract']['path'])
    guard_confirmation_files(study,monkeypatch)
    prior=diagnostic(study,paths[0],d1,study['directory']/'prior24')
    assert old['all']['fixed_anchor_count']==48 and old['status']=='EVIDENCE_UNAVAILABLE'
    assert prior['status']=='COMPLETE_DIAGNOSTIC' and prior['confirmation']=='SEALED'
    assert prior['results']==[r for r in old['results'] if r['partition']=='discovery']
    with pytest.raises(ValueError,match='both|partition'):
        analysis.evaluate_q1_direction_references(
            paths[:1],study['directory']/'forbidden_one',contract_path=study['manifest']['contract']['path'])
    assert not (study['directory']/'forbidden_one').exists()
