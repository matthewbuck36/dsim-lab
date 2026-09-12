"""Fresh M4v5 identity admission and the matched bounded interior-anchor selection.

Only synthetic metadata/resources are used. No ROS graph, field computation,
recorded bag or real preparation/acquisition is started. Temporary preparation
fixtures explicitly replace numerical qualification and geometry verification.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_v3_versions import (
    REPOSITORY, dispatch, evaluator, module, topology, workflow,
    test_v3_dispatch_passes_mode_to_inner_outer_and_cleanup_without_extra_slots as _check_dispatch,
    test_v3_science_hooks_propagate_ownership_and_preserve_caps as _check_science,
)

VERSION = 'm4-pilot-v5'
MODE = 'subreaper_group_v3'
BEFORE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v5_moving_fill_v1/version_routes/before')
EARLIER = ('m4-pilot-v1', 'm4-pilot-v2', 'm4-pilot-v3', 'm4-pilot-v4')


def synthetic_topology(geometry, disturbance=None):
    """Declared finite fixture; copied numerical values are not qualification."""
    template=scenario._template(geometry);case=template['cases'][0]
    record=deepcopy(topology()['nominal']);record.pop('result_sha256')
    disturbance=disturbance or dict(sensor_noise=dict(model='none',bound=0.),sensor_delay_sec=0.,pose_delay_sec=0.)
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    record.update(source_list_sha256=digest([{key:source[key] for key in
        ('id','x_m','y_m','relative_lumen_input')} for source in case['sources']]),
        start_sha256=digest(case['starts'][0]),bounds_sha256=digest(template['defaults']['bounds_m']),
        disturbances_sha256=digest(disturbance))
    record['result_sha256']=digest(record)
    return record


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
        'resolved_scenario':{'suite_id':identity['suite_id'], 'algorithm':{'launch_overrides':{
            'open_field_escape_approach_continuity_enabled':True,
            'open_field_escape_interior_anchor_fallback_enabled':True,
            'open_field_escape_interior_anchor_min_displacement_m':.50}}},
        'summary_path':str(root/'acquisition'/f'summary_{row["slot"]}.yaml'),
        'expected_cost_configuration':{'path':str(root/'cost.json'),'sha256':'fixture'}}
        for row in scenario.expected_slots(VERSION)]
    value['topology_receipts']={name:{'path':str(root/'preflight'/('topology_'+('primary_nominal' if name=='primary_nominal' else 'secondary_'+name)+'.json')),'sha256':'fixture'} for name in (*scenario.CONDITIONS,'primary_nominal')}
    for row in value['runs']:
        if row['geometry']=='primary':
            row['resolved_scenario']['success']={'staged_recovery':{'local_association_mode':'verified_trap','topology_qualification':synthetic_topology('primary')}}
        row['runner_argv']=dispatch.runner_command(value,row)
    return value


def test_exact_fresh_root_population_gui_and_existing_owner():
    identity=scenario.experiment_identity(VERSION)
    assert identity==dict(experiment_version=VERSION,suite_id='m4_pilot_v5',
        root='/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v5',process_ownership_mode=MODE)
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
            assert row['case_id']==f'm4_v5_{spec[0]}_{spec[2]}_{row["arm"]}_{spec[3]}'
            assert scenario.experiment_run_id(row,VERSION)==f'm4-pilot-v5-slot{row["slot"]:02d}-{row["arm"]}-{spec[3]}'
    old_ids={row['case_id'] for version in EARLIER for row in scenario.expected_slots(version)}
    assert not old_ids & {row['case_id'] for row in rows}


@pytest.mark.parametrize('version',EARLIER)
def test_prior_population_resource_argv_and_scientific_outputs_are_exact(version):
    old=module('m4_v5_retained_scenario_'+version[-1],BEFORE/'ros2_ws/src/ros_esc/ros_esc/scenario_runner/m4_scenario.py')
    old.SCENARIOS=scenario.SCENARIOS
    previous_metrics=module('ros_esc.plotting_scripts.m4_v5_retained_metrics_'+version[-1],
        BEFORE/'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py')
    previous_dispatch=module('m4_v5_retained_dispatch_'+version[-1],BEFORE/'docs/codex/gesc_gaussian/v2/tools/run_m4.py')
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


def test_v5_resource_changes_only_declared_amendments_with_fixed_caps(contract):
    root=Path(contract['root'])
    current=scenario.build_m4_document(topology(),runs_root=root/'runs',experiment_version=VERSION,primary_topology=synthetic_topology('primary'))
    legacy=scenario.build_m4_document(topology(),runs_root=root/'runs')
    assert current['suite_id']=='m4_pilot_v5'
    assert current['metadata']['experiment_version']==VERSION
    assert current['execution']==legacy['execution']
    assert current['execution']['run_timeout_sec']==720.
    assert current['execution']['wall_timeout_sec']==900.
    assert current['frozen_profile']==legacy['frozen_profile']
    for now,old in zip(current['cases'],legacy['cases']):
        normalized=deepcopy(now)
        normalized['case_id']=old['case_id']
        normalized['success']['controller']['contract_id']=old['case_id']
        assert normalized['algorithm']['launch_overrides'].pop('open_field_escape_interior_anchor_fallback_enabled') is True
        assert normalized['algorithm']['launch_overrides'].pop('open_field_escape_interior_anchor_min_displacement_m') == .50
        assert (current['frozen_profile']['launch_overrides'] | normalized['algorithm']['launch_overrides'])['open_field_escape_approach_continuity_enabled'] is True
        if now['case_id'].startswith('m4_v5_development_'):
            recovery=normalized['success']['staged_recovery']
            assert recovery.pop('topology_qualification')==synthetic_topology('primary')
            assert recovery['local_association_mode']=='verified_trap'
            recovery['local_association_mode']=old['success']['staged_recovery']['local_association_mode']
        assert normalized==old
    assert dispatch.validate_contract(contract)==root
    for row in contract['runs']:
        argv=row['runner_argv']
        assert argv[:4]==['ros2','run','ros_esc','run_scenario']
        assert argv[argv.index('--process-ownership-mode')+1]==MODE


@pytest.mark.parametrize('earlier',EARLIER)
@pytest.mark.parametrize('fault',['root','case','run','suite','experiment','analysis'])
def test_prior_experiment_cannot_substitute_fresh_v5_inputs(contract,earlier,fault):
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
def test_v5_keeps_exact_existing_group_ownership_mode(contract,mode):
    contract['execution']['process_ownership_mode']=mode
    with pytest.raises(ValueError):dispatch.validate_contract(contract)


@pytest.mark.parametrize('version',['m4-pilot-v15','m4-pilot-v04','m4_pilot_v5',None])
def test_version_allowlist_remains_exact(version):
    with pytest.raises(ValueError):scenario.experiment_identity(version)


@pytest.mark.parametrize('mode,strict,accepted',[(MODE,True,True),(MODE,False,False),
    ('subreaper_v2',True,False),('observed_tree_v1',True,False)])
def test_actual_runner_admission_requires_v5_group_mode_before_expansion(monkeypatch,mode,strict,accepted):
    class Admitted(Exception):pass
    def expansion(*args,**kwargs):raise Admitted
    monkeypatch.setattr(runner,'load_suite',lambda *a:{'suite_id':'m4_pilot_v5'})
    monkeypatch.setattr(runner,'expand_suite',expansion)
    with pytest.raises(Admitted if accepted else ValueError):
        runner.execute_suite('synthetic','fixture',process_ownership_mode=mode,strict_cleanup=strict)


def test_centroid_evaluator_admits_exact_v5_without_changing_selected_method():
    resolved={'suite_id':'m4_pilot_v5','algorithm':{'launch_overrides':{
        'convergence_metric_mode':'centroid_two_block_v2','centroid_window_sec':6.,
        'centroid_epsilon_m':.18,'centroid_maximum_radius_m':.50}}}
    selected=runner._m4_centroid_event_selection(resolved)
    assert selected['metric_mode']=='centroid_two_block_v2'
    assert (selected['window_sec'],selected['epsilon_m'],selected['maximum_radius_m'])==(6.,.18,.50)
    resolved['suite_id']='m4_pilot_v13'
    assert runner._m4_centroid_event_selection(resolved) is None


def test_v5_method_and_all_target_denominators_remain_fixed(contract):
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
    assert str(REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v5_moving_fill_plan.md') in paths
    assert str(REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v5_primary_topology_amendment.md') in paths
    assert '/opt/ros/humble/lib/python3.10/site-packages/ros2run/api/__init__.py' in paths


def test_dispatch_propagates_v5_identity_to_existing_group_owner_and_complete_ledger(contract,monkeypatch):
    _check_dispatch(contract,monkeypatch)


def test_science_v5_hooks_keep_group_owner_and_existing_900_second_allocation(contract,monkeypatch):
    _check_science(contract,monkeypatch)


@pytest.mark.parametrize('version',EARLIER)
def test_preedit_scenario_outputs_match_retained_json_fixture(version):
    fixture_path=BEFORE.parent/(version.replace('-','_')+'_outputs.json')
    expected=json.loads(fixture_path.read_text())
    identity=scenario.experiment_identity(version)
    assert expected==dict(experiment_identity=identity,population=scenario.expected_slots(version),
        scenario=scenario.build_m4_document(topology(),runs_root=Path(identity['root'])/'runs',experiment_version=version))


@pytest.mark.parametrize('slot',range(16))
@pytest.mark.parametrize('key,value',[
    ('open_field_escape_approach_continuity_enabled',False),
    ('open_field_escape_interior_anchor_fallback_enabled',False),
    ('open_field_escape_interior_anchor_min_displacement_m',.49),
    ('open_field_escape_interior_anchor_min_displacement_m',.51),
    ('open_field_escape_interior_anchor_min_displacement_m',None),
])
def test_every_v5_slot_requires_exact_matched_bounded_selection(contract,slot,key,value):
    contract['runs'][slot]['resolved_scenario']['algorithm']['launch_overrides'][key]=value
    with pytest.raises(ValueError,match='matched bounded interior-anchor'):
        dispatch.validate_contract(contract)


@pytest.mark.parametrize('fault',['absent','secondary','source','start','bounds','disturbance','hash'])
def test_primary_input_binds_original_geometry_and_rejects_missing_or_foreign(contract,fault):
    primary=synthetic_topology('primary')
    if fault=='absent':primary=None
    elif fault=='secondary':primary=synthetic_topology('secondary')
    elif fault=='hash':primary['result_sha256']='changed'
    else:
        key={'source':'source_list_sha256','start':'start_sha256','bounds':'bounds_sha256','disturbance':'disturbances_sha256'}[fault]
        primary.pop('result_sha256');primary[key]='changed'
        primary['result_sha256']=hashlib.sha256(json.dumps(primary,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with pytest.raises(ValueError,match='primary topology'):
        scenario.build_m4_document(topology(),runs_root=Path(contract['root'])/'runs',
            experiment_version=VERSION,primary_topology=primary)


@pytest.mark.parametrize('slot',range(4))
@pytest.mark.parametrize('fault',['missing','declared_source','cross_arm','missing_receipt','wrong_receipt_path'])
def test_primary_four_arm_binding_is_mandatory_before_dispatch(contract,slot,fault):
    recovery=contract['runs'][slot]['resolved_scenario']['success']['staged_recovery']
    if fault=='missing':recovery.pop('topology_qualification')
    elif fault=='declared_source':recovery['local_association_mode']='declared_source'
    elif fault=='cross_arm':recovery['topology_qualification']=synthetic_topology('secondary')
    elif fault=='missing_receipt':contract['topology_receipts'].pop('primary_nominal')
    else:contract['topology_receipts']['primary_nominal']['path']='/foreign/primary.json'
    with pytest.raises(ValueError,match='primary'):
        dispatch.validate_contract(contract)


@pytest.mark.parametrize('version',EARLIER)
def test_primary_argument_does_not_select_fallback_or_association_for_old_versions(version):
    root=Path(scenario.experiment_identity(version)['root'])
    with pytest.raises(ValueError,match='only by M4 v5'):
        scenario.build_m4_document(topology(),runs_root=root/'runs',experiment_version=version,
            primary_topology=synthetic_topology('primary'))


@pytest.mark.parametrize('fault',[None,'missing','declared_source'])
def test_real_schema_preserves_primary_gate_and_delegates_topology_validation(contract,monkeypatch,fault):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from ros_esc.scenario_runner import scenario_schema as schema
    calls=[]
    def validate(record,sources,start,bounds,disturbance,local_id,global_id):
        calls.append((deepcopy(record),deepcopy(sources),deepcopy(start),deepcopy(bounds),deepcopy(disturbance),local_id,global_id))
        return deepcopy(record)  # Explicit mocked numerical owner; no qualification claim.
    monkeypatch.setattr(truth,'_model',lambda *a,**k:pytest.fail('no numerical evaluation in source fixtures'))
    monkeypatch.setattr(truth,'validate_two_source_topology_qualification',validate)
    root=Path(contract['root']);document=scenario.build_m4_document(topology(),runs_root=root/'runs',
        experiment_version=VERSION,primary_topology=synthetic_topology('primary'))
    recovery=document['cases'][0]['success']['staged_recovery']
    if fault=='missing':recovery.pop('topology_qualification')
    elif fault=='declared_source':recovery['local_association_mode']='declared_source'
    path=root/'schema_fixture.yaml';path.write_text(yaml.safe_dump(document,sort_keys=False))
    if fault:
        with pytest.raises(ValueError,match='topology_qualification.*required'):
            schema.load_suite(path)
        assert not calls
        return
    expanded,unsupported=schema.expand_suite(schema.load_suite(path))
    assert not unsupported and len(expanded)==16 and len(calls)==16
    for index,(record,sources,start,bounds,disturbance,local_id,global_id) in enumerate(calls):
        raw=document['cases'][index]
        assert sources==raw['sources'] and start==raw['starts'][0]
        assert bounds==document['defaults']['bounds_m'] and disturbance==raw['disturbances']
        assert (local_id,global_id)==('local','global')
        assert record==raw['success']['staged_recovery']['topology_qualification']
    assert all(row['success']['staged_recovery']['local_association_mode']=='verified_trap' for row in expanded)


@pytest.fixture
def prepared_fixture(tmp_path,monkeypatch,request):
    """Real scenario expansion with mocked numerics/geometry and no subprocess."""
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from ros_esc.plotting_scripts import q1_study
    monkeypatch.setattr(scenario,'PILOT_ROOT',tmp_path/'pilot')
    root=Path(scenario.experiment_identity(VERSION)['root'])
    marker_path=tmp_path/'frozen_source.json';marker_path.write_text('{"fixture":true}')
    marker=workflow.receipt(marker_path);calls=[]
    def derive(sources,start,bounds,disturbance,local_id,global_id):
        geometry='primary' if sources==scenario._template('primary')['cases'][0]['sources'] else 'secondary'
        expected=scenario._template(geometry)
        assert sources==expected['cases'][0]['sources'] and start==expected['cases'][0]['starts'][0]
        assert bounds==expected['defaults']['bounds_m'] and (local_id,global_id)==('local','global')
        calls.append((geometry,deepcopy(disturbance)))
        if geometry=='primary' and getattr(request,'param',None)=='primary_failure':
            raise ValueError('fixture primary topology qualification failed')
        return synthetic_topology(geometry,disturbance)
    monkeypatch.setattr(workflow.subprocess,'check_output',lambda *a,**k:'feature/gesc-gaussian-robustness-v2\n')
    monkeypatch.setattr(workflow.subprocess,'Popen',lambda *a,**k:pytest.fail('no subprocess or acquisition in preparation fixture'))
    monkeypatch.setattr(workflow,'collect_sources',lambda:[marker])
    monkeypatch.setattr(workflow,'geometry_context',lambda *a:dict(label_geometry=marker,geometry_recovery=marker,geometry_receipts=[marker]))
    monkeypatch.setattr(workflow,'selected_environment',lambda:{'fixture':'environment'})
    monkeypatch.setattr(workflow,'installed_entry_points',lambda **k:{'fixture':'installed'})
    monkeypatch.setenv('ROS_DOMAIN_ID','186')
    monkeypatch.setattr(truth,'_model',lambda *a,**k:pytest.fail('no numerical evaluation in source fixtures'))
    monkeypatch.setattr(truth,'derive_two_source_topology_qualification',derive)
    monkeypatch.setattr(truth,'validate_two_source_topology_qualification',lambda record,*a,**k:deepcopy(record))
    monkeypatch.setattr(q1_study,'verify_geometry_receipts',lambda *a,**k:True)
    if getattr(request,'param',None)=='primary_failure':
        with pytest.raises(ValueError,match='fixture primary topology qualification failed'):
            workflow.prepare(VERSION)
        return root,None,calls
    ref=workflow.prepare(VERSION)
    return root,workflow.read_json(ref['path']),calls


def test_mocked_preparation_keeps_one_budget_and_exact_four_topology_delegations(prepared_fixture):
    root,contract,calls=prepared_fixture
    assert [row[0] for row in calls]==['secondary']*3+['primary']
    assert calls[0][1]==calls[3][1]==dict(sensor_noise=dict(model='none',bound=0.),sensor_delay_sec=0.,pose_delay_sec=0.)
    assert set(contract['topology_receipts'])=={*scenario.CONDITIONS,'primary_nominal'}
    assert workflow.read_json(root/'preflight/started.json')['budget_sec']==600
    assert workflow.read_json(root/'preflight/prepared.json')['topology_conditions']==['nominal','noise','delay','primary_nominal']
    assert workflow.verify_frozen(contract)
    primary=workflow.read_json(contract['topology_receipts']['primary_nominal']['path'])
    assert primary==synthetic_topology('primary')
    for row in contract['runs'][:4]:
        assert row['resolved_scenario']['success']['staged_recovery']['topology_qualification']==primary
    assert not (root/'runs').exists() and not (root/'acquisition').exists()
    with pytest.raises(FileExistsError):workflow.prepare(VERSION)
    assert len(calls)==4


@pytest.mark.parametrize('fault',['stale_receipt','wrong_bound_receipt','cross_arm'])
def test_frozen_primary_receipt_must_match_every_resolved_case(prepared_fixture,fault):
    root,contract,_=prepared_fixture
    path=Path(contract['topology_receipts']['primary_nominal']['path'])
    if fault=='cross_arm':
        contract['runs'][1]['resolved_scenario']['success']['staged_recovery']['topology_qualification']=synthetic_topology('secondary')
    else:
        path.write_text(json.dumps(synthetic_topology('secondary')))
        if fault=='wrong_bound_receipt':contract['topology_receipts']['primary_nominal']=workflow.receipt(path)
    Path(contract['contract_path']).write_text(json.dumps(contract))
    with pytest.raises(ValueError):workflow.verify_frozen(contract)


@pytest.mark.parametrize('prepared_fixture',['primary_failure'],indirect=True)
def test_primary_qualification_failure_preserves_one_attempt_without_scenario_or_retry(prepared_fixture):
    root,contract,calls=prepared_fixture
    assert contract is None and len(calls)==4
    assert workflow.read_json(root/'preflight/started.json')['status']=='INCOMPLETE'
    assert len(list((root/'preflight').glob('topology_secondary_*.json')))==3
    assert not (root/'scenario.yaml').exists() and not (root/'preflight/contract.json').exists()
    assert not (root/'preflight/prepared.json').exists()
    with pytest.raises(FileExistsError):workflow.prepare(VERSION)
    assert len(calls)==4
