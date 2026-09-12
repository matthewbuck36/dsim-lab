"""V13 selects authenticated trapping only for D and preserves old scenarios."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner import scenario_schema as schema
from ros_esc.v2_lifecycle import ANGULAR_PROFILES_POLICY, RECURRENT_TRAPPING_POLICY
from test_m4_dispatch import dispatch
import test_m4_v6_versions as inherited
from test_m4_v9_versions import topology_inputs, prohibit_models
from test_m4_v12_versions import PRIMARY
from test_q1_launch_frontend import parsed_launch  # noqa: F401
from test_q7_launch_selection import parameters


VERSION = scenario.V13_EXPERIMENT_VERSION


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v13_contract')/'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root']); root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        value = inherited._build_contract(document, patch)
        value['method_version'] = scenario.V13_METHOD_VERSION
        value['development_release_policy'] = scenario.V13_RELEASE_POLICY
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


def test_v13_exact_identity_population_release_and_caps():
    assert scenario.experiment_method_version(VERSION) == 'recurrent_trapping_integrated_arrival_v13'
    assert scenario.experiment_release_policy(VERSION) == 'qualified_trapping_integrated_arrival_v1'
    identity = scenario.experiment_identity(VERSION)
    assert identity['suite_id'] == 'm4_pilot_v13'
    assert identity['root'].endswith('/pilot/m4_pilot_v13')
    assert identity['process_ownership_mode'] == 'subreaper_group_v3'
    slots = scenario.expected_slots(VERSION)
    assert [s['seed'] for s in slots] == [26091141+i//4 for i in range(16)]
    assert [s['slot'] for s in slots] == list(range(1,17))
    assert [s['arm'] for s in slots] == list('ABCD')*4
    assert [s['partition'] for s in slots] == ['development']*4+['holdout']*12
    assert [s['geometry'] for s in slots] == ['primary']*4+['secondary']*12
    assert [s['condition'] for s in slots] == ['nominal']*8+['noise']*4+['delay']*4
    assert [s['visible'] for s in slots] == [True]*4+[False]*12
    earlier = {scenario.experiment_run_id(row, version)
        for version in scenario.EXPERIMENT_VERSIONS[:scenario.EXPERIMENT_VERSIONS.index(VERSION)]
        for row in scenario.expected_slots(version)}
    assert not earlier.intersection(scenario.experiment_run_id(s,VERSION) for s in slots)
    assert scenario.experiment_execution_budgets(VERSION) == scenario.experiment_execution_budgets(scenario.V12_EXPERIMENT_VERSION)


@pytest.mark.parametrize('version,selected', [
    ('m4-pilot-v11',False), ('m4-pilot-v12',True), ('m4-pilot-v13',True),
    ('m4-pilot-v14',True), ('m4-pilot-v15',False), ('m4_pilot_v13',False), (None,False),
])
def test_integrated_family_is_explicit(version, selected):
    assert scenario.is_integrated_arrival_experiment_version(version) is selected
    if version == 'm4-pilot-v15':
        with pytest.raises(ValueError, match='unsupported'):
            scenario.experiment_release_policy(version)


def test_all16_routes_require_complete_recovery_and_only_D_trapping(contract):
    assert scenario.validate_experiment_contract(contract)['suite_id'] == 'm4_pilot_v13'
    for row in contract['runs']:
        resolved = row['resolved_scenario']; controls = resolved['algorithm']['launch_overrides']
        recurrent, moving = row['arm'] in 'BD', row['arm'] in 'CD'
        assert controls['convergence_metric_mode'] == (RECURRENT_MODE if recurrent else 'pde_mean_v1')
        assert controls['continuous_search_mode'] == ('rolling_gesc_v2' if moving else 'stationary_v1')
        assert controls['v2_verification_motion_mode'] == ('centered_tracking_v1' if moving else 'rolling_neighborhood_v1')
        assert controls.get('v2_verification_evidence_policy',ANGULAR_PROFILES_POLICY) == (
            RECURRENT_TRAPPING_POLICY if row['arm']=='D' else ANGULAR_PROFILES_POLICY)
        baseline = scenario._arm_overrides(row['arm'],scenario.V12_EXPERIMENT_VERSION)
        expected = {**baseline, **({'v2_verification_evidence_policy':RECURRENT_TRAPPING_POLICY} if row['arm']=='D' else {})}
        assert scenario._arm_overrides(row['arm'],VERSION) == expected
        assert controls['controller_spawner_load_recovery_enabled'] is True
        assert controls['controller_config_filepath'] == str(scenario.V6_CONTROLLER_PATH)
        assert controls['centroid_invalid_status_heartbeat_enabled'] is False
        success = resolved['success']
        assert success['criterion'] == 'post_recovery_arrival_v1' and not runner._requires_ranked_goal(resolved)
        assert set(success['all_of']) == set(success['result_scopes']['full_lifecycle']['all_of']) == PRIMARY
        assert success['controller']['required_state_path'] and len(success['controller']['required_state_paths'])==2
        staged = success['staged_recovery']
        assert (staged['stage_a_timeout_sec'],staged['post_stage_a_timeout_sec'],staged['global_proximity_radius_m']) == (360.,300.,.5)
        assert 'simulation_duration_sec' not in resolved.get('execution', {})
        assert ('v2_verification_evidence_policy:=recurrent_trapping_v1' in row['launch_argv']) is (row['arm']=='D')
        assert 'controller_spawner_load_recovery_enabled:=True' in row['launch_argv']
        assert ('--gui' in row['runner_argv']) is row['visible']


def test_actual_frontend_routes_new_wrapper_only_for_D(contract, parsed_launch):
    for row in contract['runs'][:4]:
        overrides = dict(arg.split(':=',1) for arg in row['launch_argv'][4:])
        _, owners = parameters(parsed_launch, overrides)
        policy = RECURRENT_TRAPPING_POLICY if row['arm']=='D' else ANGULAR_PROFILES_POLICY
        for name in ('supervisor_node','gaussian_fill_node'):
            assert owners[name]['v2_verification_evidence_policy'] == policy
        suffix = 'recurrent_fill_commands' if row['arm']=='D' else 'fill_commands'
        assert owners['gaussian_fill_node']['v2_fill_command_topic'] == '/gesc_gaussian/v2/'+suffix
        assert 'v2_verification_evidence_policy' not in owners['convergence_detector_node']


@pytest.mark.parametrize('fault',['old_method','old_policy','old_seed','D_angular','C_trapping','B_trapping','startup_false','first_path_primary'])
def test_contract_rejects_changed_version_or_arm_selection(contract, fault):
    if fault=='old_method': contract['method_version']=scenario.V12_METHOD_VERSION
    elif fault=='old_policy': contract['development_release_policy']=scenario.V12_RELEASE_POLICY
    elif fault=='old_seed': contract['runs'][0]['seed']=26091131
    elif fault=='startup_false': contract['runs'][0]['resolved_scenario']['algorithm']['launch_overrides']['controller_spawner_load_recovery_enabled']=False
    elif fault=='first_path_primary':
        success=contract['runs'][0]['resolved_scenario']['success']
        success['all_of'].append('required_state_path')
        success['result_scopes']['full_lifecycle']['all_of'].append('required_state_path')
    else:
        arm= fault[0]
        controls=next(r for r in contract['runs'] if r['arm']==arm)['resolved_scenario']['algorithm']['launch_overrides']
        controls['v2_verification_evidence_policy']=ANGULAR_PROFILES_POLICY if arm=='D' else RECURRENT_TRAPPING_POLICY
    with pytest.raises(ValueError): scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('predicate',sorted(PRIMARY))
def test_all_eleven_primary_predicates_stay_required(contract, predicate):
    success=contract['runs'][0]['resolved_scenario']['success']
    success['all_of'].remove(predicate);success['result_scopes']['full_lifecycle']['all_of'].remove(predicate)
    with pytest.raises(ValueError):scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('version',[scenario.V11_EXPERIMENT_VERSION,scenario.V12_EXPERIMENT_VERSION])
def test_historical_scenario_bytes_remain_exact(version):
    root=Path(scenario.experiment_identity(version)['root'])
    retained=json.loads((root/'preflight/contract.json').read_text())
    original_bytes=(root/'scenario.yaml').read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest()==retained['scenario']['sha256']
    original=yaml.safe_load(original_bytes)
    primary=original['cases'][0]['success']['staged_recovery']['topology_qualification'];secondary={}
    for row,case in zip(scenario.expected_slots(version),original['cases']):
        if row['geometry']=='secondary':secondary.setdefault(row['condition'],case['success']['staged_recovery']['topology_qualification'])
    generated=scenario.build_m4_document(secondary,runs_root=root/'runs',experiment_version=version,primary_topology=primary)
    assert yaml.safe_dump(generated,sort_keys=False).encode()==original_bytes
    assert all('v2_verification_evidence_policy' not in case['algorithm']['launch_overrides'] for case in generated['cases'])


def test_unknown_suite_cannot_borrow_completed_recovery_exception(tmp_path, monkeypatch):
    prohibit_models(monkeypatch);secondary,primary=topology_inputs()
    root=Path(scenario.experiment_identity(VERSION)['root'])
    document=scenario.build_m4_document(secondary,runs_root=root/'runs',experiment_version=VERSION,primary_topology=primary)
    document['suite_id']='m4_pilot_v15';document['cases']=document['cases'][:1]
    path=tmp_path/'future.yaml';path.write_text(yaml.safe_dump(document,sort_keys=False))
    with pytest.raises(ValueError):schema.load_suite(path)
