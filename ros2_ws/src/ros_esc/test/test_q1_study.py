"""Synthetic Q1 labels, causal M3 and immutable selection; no bag/field runs."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
from nav_msgs.msg import Odometry
from ros_esc.plotting_scripts import q1_study as q
from ros_esc.plotting_scripts.bag_reader import BagRecord
from ros_esc.v2_lifecycle import message_payload
from ros_esc.v2_stream import set_time
from test_v2_moving_evidence import observation

NS = q.NS
CONTRACT = {'version': q.analysis.Q1_VERSION, 'detector': q.DETECTOR_CONTRACT}
PARAMETERS = {'window_seconds': 6, 'epsilon_m': .30, 'radius_m': .5, 'candidate_epsilon_m': .1}


def poses(duration=49, *, dt=.1, position=lambda t: (0., 0.), offset=0.):
    return [{'stamp_ns': round((i*dt+offset)*NS), 'bag_timestamp_ns': round((i*dt+offset+.01)*NS),
             'xy': list(position(i*dt+offset)), 'frame_id': 'odom', 'qualified': True,
             'search_epoch': 1, 'search_epoch_start_ns': 0, 'history_generation': 0,
             'readiness_eligible': True} for i in range(round(duration/dt)+1)]


def raw_rows(duration=49, *, dt=.05, begin=0., delay=0., position=lambda t:(0.,0.), cost=None):
    result = []
    for i in range(round((duration-begin)/dt)+1):
        t = round(begin+i*dt, 9)
        wire = observation(t, xy=position(t), raw=cost(t) if cost else None)
        result.append({'stamp_ns': round(t*NS), 'filter_stamp_ns': round((t+delay)*NS),
                       'observation_wire': message_payload(wire), 'qualified': True,
                       'filter_state_valid': True, 'filter_state': 1, 'search_epoch': 1,
                       'history_generation': 0, 'context_id': 0})
    return result


def positive(start=0, end=49):
    return {'kind':'positive_basin_residence', 'source_id':'local',
            'start_ns':round(start*NS), 'end_ns':round(end*NS), 'duration_sec':end-start}


def prepared(*, exposure='residence', duration=49, position=lambda t:(0.,0.), rows=True):
    ps = poses(duration, position=position)
    labels = [positive(0,duration)] if exposure == 'residence' else [
        {'kind':'negative_directed_progress','start_ns':0,'end_ns':round(duration*NS)}]
    supported, censored = q.analysis._v2_common_positive_support(ps, labels, minimum_duration_sec=42)
    return {'run':{'run_id':'synthetic', 'seed':26090911, 'partition':'discovery', 'exposure':exposure},
            'poses':ps, 'observations':raw_rows(duration,position=position) if rows else [],
            'labels':labels, 'supported_positives':supported, 'censored_positives':censored,
            'qualification':{'qualified':True,'integrity_errors':[]}}


def event(p, at=36, center=(0.,0.)):
    index = next(i for i,r in enumerate(p['poses']) if r['stamp_ns'] >= round(at*NS))
    stamp = p['poses'][index]['stamp_ns']
    return {'stamp_ns':stamp,'deadline_ns':stamp+12*NS,'center_xy':list(center),
            'pose_index':index,'search_epoch':1,'search_epoch_start_ns':0,'history_generation':0}


def write(path, document):
    path.write_text(json.dumps(document,sort_keys=True))
    return {'path':str(path), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def test_actual_pose_knots_first_receipt_conflicts_and_regressions():
    records=[]
    for index,(stamp,x) in enumerate([(1.,2.),(1.,2.),(1.,3.),(1.,2.),(.9,2.),(1.1,4.)]):
        m=Odometry(); set_time(m.header.stamp,round(stamp*NS)); m.header.frame_id='odom'; m.pose.pose.position.x=x
        records.append(BagRecord('/selected','Odometry',index,round(stamp*NS),None,False,m,True))
    result, faults = q._selected_pose_samples(SimpleNamespace(records_by_topic={'/selected':records}),'/selected','odom')
    assert [r['qualified'] for r in result] == [True,False,False,False,True]
    assert result[0]['bag_timestamp_ns']==0 and result[-1]['xy']==[4.,0.]
    assert faults['identical_pose_repeat']==1


def test_prepare_labels_actual_pose_before_masks_never_observation_xy(monkeypatch):
    m=Odometry(); m.header.frame_id='odom'; m.pose.pose.position.x=3.
    record=BagRecord('/selected','Odometry',0,0,None,False,m,True)
    bag=SimpleNamespace(records_by_topic={'/selected':[record]})
    metadata={'scenario_runner':{'v2_identity':{'stream_config':{'pose_topic':'/selected','frame_id':'odom'}}}}
    row={'xy':[99.,99.], 'stamp_ns':0}
    calls=[]
    monkeypatch.setattr(q.analysis,'prepare_q1_direction_inputs',lambda *a,**k:([row],{'qualified':True,'integrity_errors':[]}))
    def label(ps, geometry):
        calls.append('label'); assert ps[0]['xy']==[3.,0.]; return []
    def mask(ps,bag):
        calls.append('mask'); return ps
    monkeypatch.setattr(q.analysis,'label_v2_basin_intervals',label)
    monkeypatch.setattr(q.analysis,'q1_pose_search_eligibility',mask)
    out=q.prepare_q1_study_run(bag,metadata,contract=CONTRACT,run_spec={},geometry={})
    assert calls==['label','mask','mask'] and out['observations'][0]['xy']==[99.,99.]
    assert not out['detector_evaluated_for_labeling']
    monkeypatch.setattr(q.analysis,'prepare_q1_direction_inputs',lambda *a,**k:([],{'qualified':False,'integrity_errors':['conflict']}))
    calls.clear()
    out=q.prepare_q1_study_run(bag,metadata,contract=CONTRACT,run_spec={},geometry={})
    assert calls==[] and out['poses']==[] and out['labels']==[]


def test_42_second_first_opportunity_preserves_historical_default_and_censoring():
    ps=poses(100); labels=[positive(0,42)]
    assert len(q.analysis._v2_common_positive_support(ps,labels,minimum_duration_sec=42)[0])==1
    assert not q.analysis._v2_common_positive_support(ps,labels)[0]
    supported,censored=q.analysis._v2_common_positive_support(ps,[positive(0,20),positive(30,100)],minimum_duration_sec=42)
    assert not supported and len(censored)==2
    assert censored[-1]['reason']=='later_residence_after_first_opportunity'


def test_actual_completing_pose_time_separate_window_end_once_epoch():
    p=prepared(rows=False); p['poses']=poses(80,dt=.13)
    events=q._detector_events(p,.5)
    assert len(events)==1
    e=events[0]
    assert e['window_end_ns']==36*NS < e['stamp_ns']==36_010_000_000
    assert e['deadline_ns']==e['stamp_ns']+12*NS and not e['actual_detector_publication_reconstructed']
    p['poses'][300]['qualified']=False
    for r in p['poses'][301:]: r['history_generation']=1
    assert len(q._detector_events(p,.5))==1


@pytest.mark.parametrize('position,expected',[(lambda t:(0.,0.),1),
    (lambda t:(.15*math.cos(2*math.pi*t/3),.15*math.sin(2*math.pi*t/3)),1),
    (lambda t:(.04*t,0.),0)])
def test_stationary_circle_and_directed_centroid_traces(position,expected):
    p=prepared(rows=False,position=position)
    assert len(q._detector_events(p,.5))==expected


def test_ready_pretrigger_raw_evidence_ignores_augmented_context_and_confidence():
    p=prepared(); e=event(p)
    for i,row in enumerate(p['observations']): row['context_id']=i; row['method']={'qualified':False}
    result=q._verify_event(p,e,.5,.1)
    assert result['status']=='PASS' and result['evaluation_ns']==36*NS
    assert result['evidence']['informative'] and len(result['evidence']['cycle_bounds_ns'])==3
    assert result['evidence']['summary']['pretrigger_rotation_count']==3


@pytest.mark.parametrize('change,reason',[('constant','uninformative_raw_profiles'),('departure','candidate_departure')])
def test_uninformative_profiles_and_completing_pose_departure_fail(change,reason):
    p=prepared()
    if change=='constant': p['observations']=raw_rows(cost=lambda t:-2.)
    else: p['poses'][360]['xy']=[.6,0.]
    result=q._verify_event(p,event(p),.5,.1)
    assert result['status']=='FAIL' and result['reason']==reason


def test_first_publication_not_future_evidence_and_fixed_deadline():
    p=prepared(); p['observations']=raw_rows(begin=36,delay=.2)
    result=q._verify_event(p,event(p),.5,.1)
    assert result['status']=='PASS' and result['evaluation_ns']==45_200_000_000
    assert result['evidence']['first_publication_bounds_ns'][-1]<=result['evaluation_ns']
    p['observations']=raw_rows(begin=40,delay=.2)
    result=q._verify_event(p,event(p),.5,.1)
    assert result['status']=='EVIDENCE_UNAVAILABLE' and result['evaluation_ns']==48*NS


def test_pose_departure_wins_same_timestamp_and_return_cannot_revive():
    p=prepared(); p['observations']=raw_rows(begin=36)
    p['poses'][450]['xy']=[.6,0.]
    result=q._verify_event(p,event(p),.5,.1)
    assert result['status']=='FAIL' and result['evaluation_ns']==45*NS
    assert result['reason']=='candidate_departure'


def test_candidate_center_is_frozen_not_oracle_and_stale_raw_unavailable():
    p=prepared(position=lambda t:(1.,1.))
    assert q._verify_event(p,event(p,center=(1.,1.)),.5,.1)['status']=='PASS'
    assert q._verify_event(p,event(p,center=(0.,0.)),.5,.1)['reason']=='candidate_departure'
    p['observations']=raw_rows(duration=30,position=lambda t:(1.,1.))
    assert q._verify_event(p,event(p,center=(1.,1.)),.5,.1)['status']=='EVIDENCE_UNAVAILABLE'


def test_no_empty_positive_or_negative_exposure_pass():
    p=prepared(duration=20)
    assert q._evaluate_run(p,PARAMETERS)['status']=='EVIDENCE_UNAVAILABLE'
    p=prepared(exposure='approach',rows=False,position=lambda t:(.04*t,0.))
    assert q._evaluate_run(p,PARAMETERS)['status']=='PASS'
    for r in p['poses']: r['search_epoch']=None
    result=q._evaluate_run(p,PARAMETERS)
    assert result['status']=='EVIDENCE_UNAVAILABLE' and result['negative_interval_count']==1
    assert result['eligible_negative_interval_count']==0


def test_negative_support_does_not_join_across_generation_or_missing_pose():
    p=prepared(exposure='approach',rows=False,duration=10)
    for i,r in enumerate(p['poses']):r['history_generation']=int(i>=50)
    assert q._eligible_negative_support(p['poses'],p['labels'])==[]
    p['poses']=poses(6)
    assert len(q._eligible_negative_support(p['poses'],p['labels']))==1


def test_all_negative_flags_veto_even_overlapping_ambiguous_truth():
    p=prepared(); p['labels'].append({'kind':'negative_directed_progress','start_ns':35*NS,'end_ns':40*NS})
    result=q._evaluate_run(p,PARAMETERS)
    assert result['status']=='FAIL' and result['event_label_counts']=={'ambiguous':1}
    assert 'detector_flag_on_declared_negative' in result['failures']


def frozen_fixture(tmp_path,monkeypatch,partition='discovery'):
    contract=deepcopy(CONTRACT); contract_ref=write(tmp_path/'contract.json',contract)
    monkeypatch.setattr(q.analysis,'_q1_contract',lambda ref:q._read(ref))
    monkeypatch.setattr(q.analysis,'_q1_verify_run',lambda *a:None)
    monkeypatch.setattr(q,'verify_q1_geometry',lambda *a,**k:{})
    receipts=[]
    for seed,exposure in zip(q.analysis.Q1_PARTITION_SEEDS[partition],('residence','approach')):
        p=prepared(exposure=exposure,rows=False)
        p['run'].update(seed=seed,partition=partition,run_id=f'synthetic-{seed}')
        p.update(contract_canonical_sha256=q._hash(contract),geometry_canonical_sha256=q._hash({}),
                 spatial_labels_sha256=q._hash(p['labels']))
        ref=write(tmp_path/f'{seed}.json',p); ref['run']=p['run']; receipts.append(ref)
    manifest=write(tmp_path/'study.json',{'runs':[r['run'] for r in receipts]})
    frozen={'version':q.analysis.Q1_VERSION,'status':'FROZEN','partition':partition,
            'contract':contract_ref,'runs':receipts,'study_manifest':manifest,'nomination':None}
    ref=write(tmp_path/'labels_manifest.json',frozen)
    return frozen,ref


def test_freeze_labels_writes_before_any_detector_and_confirmation_stays_sealed(tmp_path,monkeypatch):
    contract_ref=write(tmp_path/'contract.json',CONTRACT)
    runs=[{'run_id':str(seed),'run_directory':str(tmp_path/str(seed)), 'seed':seed,
           'partition':partition,'exposure':exposure}
          for partition,seeds in q.analysis.Q1_PARTITION_SEEDS.items()
          for seed,exposure in zip(seeds,('residence','approach'))]
    manifest=write(tmp_path/'study.json',{'version':q.analysis.Q1_VERSION,'contract':contract_ref,'runs':runs})
    monkeypatch.setattr(q.analysis,'_q1_contract',lambda ref:q._read(ref))
    monkeypatch.setattr(q.analysis,'_q1_verify_run',lambda *a:None)
    monkeypatch.setattr(q,'verify_q1_geometry',lambda *a,**k:{})
    config={key:f'/selected/{key}' for key in q.TOPIC_KEYS}
    def load_yaml(path):
        if path.name=='metadata.yaml':return {'scenario_runner':{'v2_identity':{'stream_config':config}}}
        return {'topics':[{'topic':topic,'alias':key} for key,topic in config.items()]+
                [{'topic':'/pde_history','alias':'pde_history'},{'topic':'/plot','alias':'unused_plot'}]}
    monkeypatch.setattr(q.analysis,'load_yaml',load_yaml)
    read=[]
    def read_bag(path,*,aliases):
        assert aliases==set(q.TOPIC_KEYS)|{'v2_direction_diagnostics','algorithm_state','clock'}
        read.append(path);return None
    monkeypatch.setattr(q.analysis,'read_run_bag',read_bag)
    monkeypatch.setattr(q,'prepare_q1_study_run',lambda *a,**k:{'labels':[], 'detector_evaluated_for_labeling':False})
    def no_detector(*a):raise AssertionError('detector invoked during label freeze')
    monkeypatch.setattr(q,'_detector_events',no_detector)
    with pytest.raises((ValueError,TypeError)):
        q.freeze_q1_study_labels(manifest['path'],tmp_path/'sealed',partition='confirmation')
    assert read==[] and not (tmp_path/'sealed').exists()
    result=q.freeze_q1_study_labels(manifest['path'],tmp_path/'labels',partition='discovery')
    assert result['status']=='FROZEN' and len(read)==2
    assert all(str(path).endswith(('26090911','26090912')) for path in read)
    assert not result['detector_evaluated_for_labeling']


def test_all_unavailable_grid_remains_unavailable_no_nomination(tmp_path,monkeypatch):
    _,ref=frozen_fixture(tmp_path,monkeypatch)
    monkeypatch.setattr(q,'_evaluate_run',lambda *a:{'status':'EVIDENCE_UNAVAILABLE'})
    result=q.evaluate_q1_study_partition(ref['path'],tmp_path/'out')
    assert result['status']=='EVIDENCE_UNAVAILABLE' and result['parameters'] is None
    assert result['settings_evaluated']==9


def test_fixed_nine_selection_smallest_radius_then_tolerance(tmp_path,monkeypatch):
    frozen,ref=frozen_fixture(tmp_path,monkeypatch)
    seen=[]
    def evaluate(p,parameters):
        seen.append((parameters['radius_m'],parameters['candidate_epsilon_m']))
        return {'status':'PASS' if parameters['radius_m']>=.5 and parameters['candidate_epsilon_m']>=.1 else 'FAIL'}
    monkeypatch.setattr(q,'_evaluate_run',evaluate)
    result=q.evaluate_q1_study_partition(ref['path'],tmp_path/'out')
    assert len(seen)==18 and result['settings_evaluated']==9
    assert result['parameters']==PARAMETERS and result['status']=='PASS'
    with pytest.raises(FileExistsError): q.evaluate_q1_study_partition(ref['path'],tmp_path/'out')


def test_confirmation_requires_pass_before_child_read_and_never_selects_alternative(tmp_path,monkeypatch):
    frozen,ref=frozen_fixture(tmp_path,monkeypatch,'confirmation')
    with pytest.raises((ValueError,TypeError)): q.evaluate_q1_study_partition(ref['path'],tmp_path/'none')
    assert not (tmp_path/'none').exists()
    nomination={'status':'PASS','partition':'discovery','contract_sha256':frozen['contract']['sha256'],'parameters':PARAMETERS}
    nomination_ref=write(tmp_path/'nomination.json',nomination)
    frozen['nomination']=nomination_ref; write(Path(ref['path']),frozen)
    seen=[]
    def evaluate(p,parameters):seen.append(parameters); return {'status':'FAIL'}
    monkeypatch.setattr(q,'_evaluate_run',evaluate)
    result=q.evaluate_q1_study_partition(ref['path'],tmp_path/'out',nomination_manifest=nomination_ref)
    assert seen==[PARAMETERS,PARAMETERS] and result['status']=='FAIL' and result['settings_evaluated']==1


@pytest.mark.parametrize('changed',['child','manifest','input'])
def test_mid_job_mutation_prevents_final_nomination_preserves_partial(tmp_path,monkeypatch,changed):
    frozen,ref=frozen_fixture(tmp_path,monkeypatch)
    checks=[0]
    def verify_run(*a):
        checks[0]+=1
        if changed=='input' and checks[0]>2:raise ValueError('changed input')
    monkeypatch.setattr(q.analysis,'_q1_verify_run',verify_run)
    def evaluate(*a):
        if changed!='input':
            target=frozen['runs'][0] if changed=='child' else frozen['study_manifest']
            Path(target['path']).write_text('{}')
        return {'status':'PASS'}
    monkeypatch.setattr(q,'_evaluate_run',evaluate)
    with pytest.raises(ValueError):q.evaluate_q1_study_partition(ref['path'],tmp_path/'out')
    assert (tmp_path/'out'/'started.json').exists() and not (tmp_path/'out'/'nomination.json').exists()


def geometry_fixture(tmp_path,monkeypatch):
    task='def _v2_enclosure_geometry_task():\n    return None'
    owner=tmp_path/'current.py'; owner.write_text(task)
    old=tmp_path/'old.py'; old.write_text(task)
    model=write(tmp_path/'model.json',{'analytic_fixture_only':True})
    sensor=write(tmp_path/'sensor.json',{})
    point=write(tmp_path/'point.json',{'diagnostic':'fixture'})
    monkeypatch.setattr(q.analysis,'__file__',str(owner))
    owners=[{'path':str(owner),'sha256':hashlib.sha256(old.read_bytes()).hexdigest()}]
    binding=[{'path':sensor['path'],'recorded_sha256':sensor['sha256']}]
    sources=[{'id':'local'}]; bounds=[-1,1,-1,1]
    geometry={'method':'operational_enclosure_v1','basins':[{'source_id':'local','qualified':True,'point_receipts':[point]}],
              'provenance':{'model_config_path':model['path'],'model_config_sha256':model['sha256'],
                            'recorded_geometry_provenance':binding,'owners':owners}}
    geometry_ref=write(tmp_path/'geometry.json',geometry)
    recovery_manifest={'original_analyzer_snapshot_path':str(old),'original_analyzer_snapshot_sha256':owners[0]['sha256'],
                       'receipts':[point,geometry_ref]}
    recovery_ref=write(tmp_path/'recovery_manifest.json',recovery_manifest)
    reuse={'recovery_manifest_path':recovery_ref['path'],'recovery_manifest_sha256':recovery_ref['sha256'],
           'original_analyzer_snapshot_path':str(old),'original_analyzer_sha256':owners[0]['sha256'],
           'unchanged_geometry_task_sha256':hashlib.sha256(task.encode()).hexdigest(),
           'original_numerical_owners':owners,
           'group_receipts':{json.dumps([sources,bounds,model['sha256'],binding]):geometry_ref}}
    recovered=write(tmp_path/'labels.json',{'numerical_geometry_recovery':reuse})
    contract={**CONTRACT,'label_geometry':geometry_ref,'geometry_recovery':recovered,
              'source_files':[model,sensor], 'geometry_receipts':[point,geometry_ref]}
    return contract,{'sources':sources,'bounds_m':bounds},geometry,point,owner


def test_geometry_chain_reuses_receipts_and_exact_task_without_evaluation(tmp_path,monkeypatch):
    contract,scenario,geometry,_,_=geometry_fixture(tmp_path,monkeypatch)
    assert q.verify_q1_geometry(contract,scenario)==geometry
    scenario['bounds_m']=[-2,2,-2,2]
    with pytest.raises(ValueError,match='source/bounds'):q.verify_q1_geometry(contract,scenario)


@pytest.mark.parametrize('change',['point','task','missing_point','sensor','detector'])
def test_geometry_chain_rejects_provenance_or_contract_change(tmp_path,monkeypatch,change):
    contract,scenario,_,point,owner=geometry_fixture(tmp_path,monkeypatch)
    if change=='point':Path(point['path']).write_text('{}')
    elif change=='task':owner.write_text('def _v2_enclosure_geometry_task():\n    return 1')
    elif change=='missing_point':contract['geometry_receipts']=[]
    elif change=='sensor':Path(contract['source_files'][1]['path']).write_text('[]')
    else:contract['detector']={**q.DETECTOR_CONTRACT,'verification_sec':13}
    with pytest.raises(ValueError):q.verify_q1_geometry(contract,scenario)
