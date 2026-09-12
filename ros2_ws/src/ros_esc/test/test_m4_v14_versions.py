"""V14 references exact V13 development plans and keeps twelve fresh strict cases.

Source fixtures use the existing schema/launch owner and cached topology records.
No model, bag, preparation or dispatch is run.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import scenario_schema as schema
import test_m4_v6_versions as inherited
from test_m4_v9_versions import topology_inputs, prohibit_models
from test_m4_v12_versions import PRIMARY

VERSION = scenario.V14_EXPERIMENT_VERSION


def original_contract():
    reference = scenario.V14_RETAINED_SOURCE_CONTRACT
    raw = Path(reference['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == reference['sha256']
    return json.loads(raw)


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v14_contract')/'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root']);root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        value = inherited._build_contract(document, patch)
        value['method_version'] = scenario.V14_METHOD_VERSION
        value['development_release_policy'] = scenario.V14_RELEASE_POLICY
        budgets = scenario.experiment_execution_budgets(VERSION)
        for section in ('execution', 'science'):
            for key in value[section]:
                if key in budgets:value[section][key] = budgets[key]
        value['retained_development'] = dict(policy='v13_development_r22_motion_v1',
            source_contract=deepcopy(scenario.V14_RETAINED_SOURCE_CONTRACT), source_slots=[1,2,3,4])
        value['runs'][:4] = deepcopy(original_contract()['runs'][:4])
        return value


@pytest.fixture
def contract(pristine_contract, monkeypatch):
    value=deepcopy(pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(value['root']).parent)
    return value


def test_exact_retained_population_and_twelve_fresh_identities():
    slots=scenario.expected_slots(VERSION);previous=scenario.expected_slots('m4-pilot-v13')
    assert slots[:4] == previous[:4]
    assert [s['experiment_version'] for s in slots] == ['m4-pilot-v13']*4+[VERSION]*12
    assert [s['seed'] for s in slots] == [26091141]*4+[26091152]*4+[26091153]*4+[26091154]*4
    assert [s['slot'] for s in slots] == list(range(1,17))
    assert [s['arm'] for s in slots] == list('ABCD')*4
    for key in ('block','partition','geometry','condition','visible'):
        assert [s[key] for s in slots] == [s[key] for s in previous]
    ids=[scenario.experiment_run_id(s,VERSION) for s in slots]
    original_ids=[scenario.experiment_run_id(s,'m4-pilot-v13') for s in previous]
    assert ids[:4] == original_ids[:4]
    assert set(ids)&set(original_ids) == set(original_ids[:4])
    assert all(i.startswith(VERSION+'-slot') for i in ids[4:])
    assert len(set(ids))==16
    assert scenario.experiment_method_version(VERSION)=='recurrent_trapping_integrated_arrival_v14'
    assert scenario.experiment_release_policy(VERSION)=='retained_development_integrated_arrival_v1'
    identity=scenario.experiment_identity(VERSION)
    assert identity['suite_id']=='m4_pilot_v14' and identity['process_ownership_mode']=='subreaper_group_v3'
    assert scenario.experiment_execution_budgets(VERSION)==scenario.experiment_execution_budgets('m4-pilot-v13')


@pytest.mark.parametrize('version,retained,trapping,integrated',[
    ('m4-pilot-v12',False,False,True),('m4-pilot-v13',False,True,True),
    ('m4-pilot-v14',True,True,True),('m4-pilot-v15',False,False,False),
    ('m4_pilot_v14',False,False,False),(None,False,False,False),
])
def test_version_families_are_exact(version,retained,trapping,integrated):
    assert scenario.is_retained_development_experiment_version(version) is retained
    assert scenario.is_trapping_experiment_version(version) is trapping
    assert scenario.is_integrated_arrival_experiment_version(version) is integrated


def test_contract_authenticates_original_records_and_new_cases(contract):
    assert scenario.validate_experiment_contract(contract)['suite_id']=='m4_pilot_v14'
    assert contract['runs'][:4]==original_contract()['runs'][:4]
    for row in contract['runs']:
        resolved=row['resolved_scenario'];success=resolved['success']
        assert resolved['suite_id']==('m4_pilot_v13' if row['slot']<=4 else 'm4_pilot_v14')
        assert set(success['all_of'])==set(success['result_scopes']['full_lifecycle']['all_of'])==PRIMARY
        assert (success['staged_recovery']['stage_a_timeout_sec'],success['staged_recovery']['post_stage_a_timeout_sec'])==(360.,300.)
        assert 'simulation_duration_sec' not in resolved.get('execution',{})
        controls=resolved['algorithm']['launch_overrides']
        assert controls['controller_spawner_load_recovery_enabled'] is True
        assert controls.get('v2_verification_evidence_policy','angular_profiles_v1')==(
            'recurrent_trapping_v1' if row['arm']=='D' else 'angular_profiles_v1')
        assert scenario._arm_overrides(row['arm'],VERSION)==scenario._arm_overrides(row['arm'],'m4-pilot-v13')


@pytest.mark.parametrize('fault',[
    'missing_binding','policy','contract_path','contract_hash','slot_order','boolean_slot',
    'retained_id','retained_summary','retained_version','retained_controls',
    'fresh_id','fresh_summary','fresh_suite','fresh_seed','fresh_policy','old_method','old_release',
])
def test_contract_rejects_cross_version_or_unbound_substitution(contract,fault):
    binding=contract['retained_development'];old=contract['runs'][0];fresh=contract['runs'][7]
    if fault=='missing_binding':del contract['retained_development']
    elif fault=='policy':binding['policy']='unqualified_reuse'
    elif fault=='contract_path':binding['source_contract']['path']='/tmp/other_contract.json'
    elif fault=='contract_hash':binding['source_contract']['sha256']='0'*64
    elif fault=='slot_order':binding['source_slots']=[4,3,2,1]
    elif fault=='boolean_slot':binding['source_slots'][0]=True
    elif fault=='retained_id':old['run_id']=old['run_id'].replace('v13','v14')
    elif fault=='retained_summary':old['summary_path']=str(Path(contract['root'])/'acquisition/summary_1.yaml')
    elif fault=='retained_version':old['experiment_version']=VERSION
    elif fault=='retained_controls':old['resolved_scenario']['algorithm']['launch_overrides']['controller_spawner_load_recovery_enabled']=False
    elif fault=='fresh_id':fresh['run_id']=fresh['run_id'].replace('v14','v13')
    elif fault=='fresh_summary':fresh['summary_path']=old['summary_path']
    elif fault=='fresh_suite':fresh['resolved_scenario']['suite_id']='m4_pilot_v13'
    elif fault=='fresh_seed':fresh['seed']=26091142
    elif fault=='fresh_policy':fresh['resolved_scenario']['algorithm']['launch_overrides']['v2_verification_evidence_policy']='angular_profiles_v1'
    elif fault=='old_method':contract['method_version']=scenario.V13_METHOD_VERSION
    elif fault=='old_release':contract['development_release_policy']=scenario.V13_RELEASE_POLICY
    with pytest.raises(ValueError):scenario.validate_experiment_contract(contract)


def test_retained_run_id_rejects_an_arbitrary_renamed_descriptor():
    row=deepcopy(scenario.expected_slots(VERSION)[0]);row['seed']+=1
    with pytest.raises(ValueError,match='retained run descriptor'):
        scenario.experiment_run_id(row,VERSION)


def test_v13_scenario_serialization_remains_exact():
    original=original_contract();path=Path(original['scenario']['path']);raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==original['scenario']['sha256']
    old=yaml.safe_load(raw);secondary={}
    for row,case in zip(scenario.expected_slots('m4-pilot-v13'),old['cases']):
        if row['geometry']=='secondary':secondary.setdefault(row['condition'],case['success']['staged_recovery']['topology_qualification'])
    new=scenario.build_m4_document(secondary,runs_root=Path(original['root'])/'runs',
        experiment_version='m4-pilot-v13',primary_topology=old['cases'][0]['success']['staged_recovery']['topology_qualification'])
    assert yaml.safe_dump(new,sort_keys=False).encode()==raw


def test_future_suite_cannot_borrow_completed_recovery(tmp_path,monkeypatch):
    prohibit_models(monkeypatch);secondary,primary=topology_inputs()
    document=scenario.build_m4_document(secondary,runs_root=Path(scenario.experiment_identity(VERSION)['root'])/'runs',experiment_version=VERSION,primary_topology=primary)
    document['suite_id']='m4_pilot_v15';document['cases']=document['cases'][:1]
    path=tmp_path/'future.yaml';path.write_text(yaml.safe_dump(document,sort_keys=False))
    with pytest.raises(ValueError):schema.load_suite(path)
