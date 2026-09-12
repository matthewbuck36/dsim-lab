"""V12 integrated selection preserves earlier scenarios and recovery evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner import scenario_schema as schema
from ros_esc.stationary_fill_protocol import STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
from ros_esc_interfaces.msg import AlgorithmState, AlgorithmEvent, GaussianFill
from test_m4_dispatch import dispatch
from test_m4_centroid_event_evaluation import wire
import test_m4_v6_versions as inherited
import test_scenario_runner as recovery
from test_m4_v9_versions import topology_inputs, prohibit_models

VERSION = scenario.V12_EXPERIMENT_VERSION
PRIMARY = {'recording_complete', 'cleanup_complete', 'required_events',
    'required_event_sequence', 'no_forbidden_states', 'no_forbidden_events',
    'local_recovery_stage', 'fill_cardinality', 'escape_command_ownership',
    'ground_truth_goal', 'post_recovery_global_proximity'}


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v12_contract') / 'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root']); root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        value = inherited._build_contract(document, patch)
        value['method_version'] = scenario.V12_METHOD_VERSION
        value['development_release_policy'] = scenario.V12_RELEASE_POLICY
        budgets = scenario.experiment_execution_budgets(VERSION)
        for section in ('execution', 'science'):
            for key in value[section]:
                if key in budgets: value[section][key] = budgets[key]
        for row in value['runs']: row['runner_argv'] = dispatch.runner_command(value, row)
        return value


@pytest.fixture
def contract(pristine_contract, monkeypatch):
    value = deepcopy(pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(value['root']).parent)
    return value


def test_v12_exact_identity_seeds_release_policy_and_unchanged_budgets():
    assert scenario.experiment_method_version(VERSION) == 'recurrent_integrated_arrival_v12'
    assert scenario.experiment_release_policy(VERSION) == 'component_response_integrated_arrival_v1'
    identity = scenario.experiment_identity(VERSION)
    assert identity['suite_id'] == 'm4_pilot_v12'
    assert identity['root'].endswith('/pilot/m4_pilot_v12')
    assert identity['process_ownership_mode'] == 'subreaper_group_v3'
    rows = scenario.expected_slots(VERSION)
    assert [row['seed'] for row in rows] == [26091131+i//4 for i in range(16)]
    assert [row['slot'] for row in rows] == list(range(1,17))
    assert [row['arm'] for row in rows] == list('ABCD')*4
    assert [row['partition'] for row in rows] == ['development']*4+['holdout']*12
    assert [row['geometry'] for row in rows] == ['primary']*4+['secondary']*12
    assert [row['condition'] for row in rows] == ['nominal']*8+['noise']*4+['delay']*4
    assert [row['visible'] for row in rows] == [True]*4+[False]*12
    old_ids = {scenario.experiment_run_id(row, version)
        for version in scenario.EXPERIMENT_VERSIONS if version != VERSION
        for row in scenario.expected_slots(version)}
    assert not old_ids.intersection(scenario.experiment_run_id(row, VERSION) for row in rows)
    assert scenario.experiment_execution_budgets(VERSION) == dict(
        suite_timeout_sec=15800., science_budget_sec=1400., case_timeout_sec=900.,
        recording_sec=720., shutdown_grace_sec=45., cleanup_reserve_sec=30.,
        labels_sec=240., references_sec=45., summary_sec=10., freeze_report_sec=40.)


def test_release_policy_lookup_preserves_every_old_version_and_rejects_future():
    for version in (f'm4-pilot-v{number}' for number in range(1,12)):
        assert scenario.experiment_release_policy(version) == (
            scenario.V10_RELEASE_POLICY if version in ('m4-pilot-v10','m4-pilot-v11') else None)
    with pytest.raises(ValueError, match='unsupported'):
        scenario.experiment_release_policy('m4-pilot-v15')


def test_all16_resolved_routes_topics_and_primary_predicates(contract):
    # Full workflow prerequisite validation belongs to its independently pinned
    # R10 fixture; this tests the existing scenario contract owner only.
    assert scenario.validate_experiment_contract(contract)['suite_id'] == 'm4_pilot_v12'
    for row in contract['runs']:
        resolved = row['resolved_scenario']; controls = resolved['algorithm']['launch_overrides']
        success = resolved['success']; recurrent = row['arm'] in 'BD'; moving = row['arm'] in 'CD'
        assert resolved['suite_id'] == 'm4_pilot_v12'
        assert controls['convergence_metric_mode'] == (RECURRENT_MODE if recurrent else 'pde_mean_v1')
        assert controls['continuous_search_mode'] == ('rolling_gesc_v2' if moving else 'stationary_v1')
        assert controls['controller_spawner_load_recovery_enabled'] is True
        assert controls['controller_config_filepath'] == str(scenario.V6_CONTROLLER_PATH)
        assert controls['v2_verification_motion_mode'] == ('centered_tracking_v1' if moving else 'rolling_neighborhood_v1')
        assert controls['centroid_invalid_status_heartbeat_enabled'] is False
        assert 'centroid_window_sec' not in controls and 'centroid_epsilon_m' not in controls
        if recurrent: assert controls['recurrent_diagnostics_topic'] == RECURRENT_TOPIC
        if row['arm'] == 'B': assert controls['stationary_recurrent_fill_request_topic'] == STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
        if moving:
            assert controls['v2_direction_policy'] == 'moving_cycle_coherence_v1'
            assert (controls['v2_candidate_radius_m'],controls['v2_candidate_epsilon_m']) == (.75,.15)
        assert scenario._arm_overrides(row['arm'],VERSION) == scenario._arm_overrides(row['arm'],scenario.V11_EXPERIMENT_VERSION)
        assert (runner._m4_centroid_event_selection(resolved) is not None) is recurrent
        assert (runner._m4_pde_event_selection(resolved) is not None) is (row['arm']=='C')
        assert success['criterion']=='post_recovery_arrival_v1' and not runner._requires_ranked_goal(resolved)
        assert set(success['all_of']) == set(success['result_scopes']['full_lifecycle']['all_of']) == PRIMARY
        assert success['controller']['required_state_path']
        assert len(success['controller']['required_state_paths']) == 2
        staged = success['staged_recovery']
        assert (staged['stage_a_timeout_sec'],staged['post_stage_a_timeout_sec'],staged['global_proximity_radius_m']) == (360.,300.,.5)
        assert ('--gui' in row['runner_argv']) is row['visible']
        assert 'controller_spawner_load_recovery_enabled:=True' in row['launch_argv']


@pytest.mark.parametrize('fault',['old_method','old_seed','old_suite','old_policy','startup_false','first_path_primary'])
def test_v12_contract_rejects_old_selection_or_changed_primary_scope(contract,fault):
    row=contract['runs'][1]
    if fault=='old_method': contract['method_version']=scenario.V11_METHOD_VERSION
    elif fault=='old_seed': row['seed']=26091021
    elif fault=='old_suite': row['resolved_scenario']['suite_id']='m4_pilot_v11'
    elif fault=='old_policy': contract['development_release_policy']=scenario.V10_RELEASE_POLICY
    elif fault=='startup_false': row['resolved_scenario']['algorithm']['launch_overrides']['controller_spawner_load_recovery_enabled']=False
    else:
        row['resolved_scenario']['success']['all_of'].append('required_state_path')
        row['resolved_scenario']['success']['result_scopes']['full_lifecycle']['all_of'].append('required_state_path')
    with pytest.raises(ValueError): scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('predicate',sorted(PRIMARY))
def test_every_other_primary_predicate_remains_mandatory(contract,predicate):
    success=contract['runs'][0]['resolved_scenario']['success']
    success['all_of'].remove(predicate); success['result_scopes']['full_lifecycle']['all_of'].remove(predicate)
    with pytest.raises(ValueError):
        scenario.validate_experiment_contract(contract)


def test_retained_v11_scenario_bytes_remain_exact():
    root=Path('/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v11')
    retained=json.loads((root/'preflight/contract.json').read_text()); original_bytes=(root/'scenario.yaml').read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest()==retained['scenario']['sha256']
    original=yaml.safe_load(original_bytes)
    primary=original['cases'][0]['success']['staged_recovery']['topology_qualification']; secondary={}
    for row,case in zip(scenario.expected_slots(scenario.V11_EXPERIMENT_VERSION),original['cases']):
        assert row['case_id']==case['case_id']
        if row['geometry']=='secondary': secondary.setdefault(row['condition'],case['success']['staged_recovery']['topology_qualification'])
    generated=scenario.build_m4_document(secondary,runs_root=root/'runs',experiment_version=scenario.V11_EXPERIMENT_VERSION,primary_topology=primary)
    assert yaml.safe_dump(generated,sort_keys=False).encode()==original_bytes
    assert all('required_state_path' in case['success']['all_of'] for case in generated['cases'])


@pytest.mark.parametrize('version',[scenario.V11_EXPERIMENT_VERSION,VERSION])
def test_schema_exemption_is_exact_and_keeps_path_declarations(tmp_path,monkeypatch,version):
    prohibit_models(monkeypatch); secondary,primary=topology_inputs()
    root=Path(scenario.experiment_identity(version)['root'])
    document=scenario.build_m4_document(secondary,runs_root=root/'runs',experiment_version=version,primary_topology=primary)
    document['cases']=document['cases'][:1]
    success=document['cases'][0]['success']
    success['all_of']=[p for p in success['all_of'] if p!='required_state_path']
    for scope in success['result_scopes'].values(): scope['all_of']=[p for p in scope['all_of'] if p!='required_state_path']
    path=tmp_path/'selected.yaml'; path.write_text(yaml.safe_dump(document,sort_keys=False))
    if version==scenario.V11_EXPERIMENT_VERSION:
        with pytest.raises(ValueError,match='required_state_path'): schema.load_suite(path)
    else:
        assert schema.load_suite(path)['cases'][0]['success']['controller']['required_state_path']
        success['controller']['required_state_path']=[]
        path.write_text(yaml.safe_dump(document,sort_keys=False))
        with pytest.raises(ValueError): schema.load_suite(path)


def recovery_fixture(contract,assisted=False):
    resolved=deepcopy(contract['runs'][2]['resolved_scenario'])
    states,events,fills=(recovery._counted_assisted_staged_records() if assisted else recovery._counted_staged_records())
    prefix=[(1,recovery._state_message('SEARCH')),(2,recovery._state_message('VERIFY_EXTREMUM')),
            (3,recovery._state_message('SEARCH'))]
    states=prefix+[(stamp+10,message) for stamp,message in states]
    return (resolved,[(t,wire(AlgorithmState,m)) for t,m in states],
            [(t+10,wire(AlgorithmEvent,m)) for t,m in events],
            [(t+10,wire(GaussianFill,m)) for t,m in fills])


@pytest.mark.parametrize('assisted',[False,True])
def test_later_completed_recovery_retains_false_first_path_diagnostic(contract,assisted):
    resolved,states,events,fills=recovery_fixture(contract,assisted)
    names,error=runner._canonical_state_sequence([m for _,m in states]); assert error is None
    controller=runner._controller_evidence(resolved['success']['controller'],names,
        runner._canonical_event_sequence([m for _,m in events])[0])
    assert controller['required_state_path'] is False
    stage,cardinality,evidence,error=runner._staged_recovery_evidence(resolved,states,events,fills)
    assert error is None and stage is True and cardinality is True
    assert evidence['completed_episode_count']==1 and evidence['episodes'][0]['state_path'][-1]=='SEARCH'
    assert len(evidence['assignments'])==1 and not evidence['unassigned_cluster_ids']
    outcomes=dict(required_state_path_passed=False,required_events_passed=True,
        required_event_sequence_passed=True,forbidden_states_absent=True,forbidden_events_absent=True,
        local_recovery_stage_passed=stage,fill_cardinality_passed=cardinality,
        escape_command_ownership_passed=True,simulation_ground_truth='passed',
        post_recovery_global_proximity_passed=True,
        result_scopes={'full_lifecycle':{'anchor_observed':True}})
    arguments=({'passed':True},{'passed':True},outcomes,
        {'timed_out':False,'return_code':0,'graceful_global_proximity_stop':True})
    assert runner.classify_result(resolved,*arguments)['passed'] is True
    old=deepcopy(resolved); old['suite_id']='m4_pilot_v11'
    old['success']['all_of'].append('required_state_path')
    old['success']['result_scopes']['full_lifecycle']['all_of'].append('required_state_path')
    assert runner.classify_result(old,*arguments)['passed'] is False


@pytest.mark.parametrize('fault',['no_returned_search','incomplete_escape','prefix_only','missing_fill',
    'conflicting_fill','invalid_fill_source','invalid_convergence_source','extra_cluster'])
def test_cancelled_prefix_cannot_replace_required_completed_recovery(contract,fault):
    resolved,states,events,fills=recovery_fixture(contract)
    if fault=='no_returned_search': states=states[:-1]
    elif fault=='incomplete_escape': states=[row for row in states if row[1].state_name!='ESCAPE_REPULSE']
    elif fault=='prefix_only': states=states[:3]
    elif fault=='missing_fill': fills=[]
    elif fault=='invalid_fill_source': fills[0][1].source_timestamp_valid=False
    elif fault=='invalid_convergence_source': events[0][1].source_timestamp_valid=False
    elif fault=='extra_cluster':
        extra=deepcopy(fills[0][1]); extra.fill_id+=1; extra.cluster_id+=1
        fills.append((fills[0][0]+1,extra))
    else:
        duplicate=deepcopy(fills[0][1]); duplicate.cluster_id+=1
        fills.append((fills[0][0]+1,duplicate))
    stage,cardinality,evidence,error=runner._staged_recovery_evidence(resolved,states,events,fills)
    assert stage is not True
    if fault in ('missing_fill','conflicting_fill','invalid_fill_source','invalid_convergence_source'):
        assert error and cardinality is not True
