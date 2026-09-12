"""V11 registration preserves prior bytes and the selected arrival contract."""
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
from test_m4_dispatch import dispatch
import test_m4_v6_versions as inherited
from test_m4_v9_versions import topology_inputs, prohibit_models


VERSION = scenario.V11_EXPERIMENT_VERSION


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v11_contract') / 'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root'])
        root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root / 'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        value = inherited._build_contract(document, patch)
        value['method_version'] = scenario.V11_METHOD_VERSION
        value['development_release_policy'] = scenario.V10_RELEASE_POLICY
        budgets = scenario.experiment_execution_budgets(VERSION)
        for section in ('execution', 'science'):
            for key in value[section]:
                if key in budgets:
                    value[section][key] = budgets[key]
        for row in value['runs']:
            row['runner_argv'] = dispatch.runner_command(value, row)
        return value


@pytest.fixture
def contract(pristine_contract, monkeypatch):
    value = deepcopy(pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(value['root']).parent)
    return value


def test_v11_has_fresh_fixed_identity_and_unchanged_arrival_budgets():
    assert scenario.experiment_method_version(VERSION) == 'recurrent_arrival_v11'
    identity = scenario.experiment_identity(VERSION)
    assert identity['suite_id'] == 'm4_pilot_v11'
    assert identity['root'].endswith('/pilot/m4_pilot_v11')
    assert identity['process_ownership_mode'] == 'subreaper_group_v3'
    rows = scenario.expected_slots(VERSION)
    assert [row['slot'] for row in rows] == list(range(1, 17))
    assert [row['seed'] for row in rows] == [26091021 + index // 4 for index in range(16)]
    assert [row['arm'] for row in rows] == list('ABCD') * 4
    assert [row['partition'] for row in rows] == ['development'] * 4 + ['holdout'] * 12
    assert [row['geometry'] for row in rows] == ['primary'] * 4 + ['secondary'] * 12
    assert [row['condition'] for row in rows] == ['nominal'] * 8 + ['noise'] * 4 + ['delay'] * 4
    assert [row['visible'] for row in rows] == [True] * 4 + [False] * 12
    earlier_ids = {scenario.experiment_run_id(row, version)
        for version in scenario.EXPERIMENT_VERSIONS if version != VERSION
        for row in scenario.expected_slots(version)}
    assert not earlier_ids.intersection(scenario.experiment_run_id(row, VERSION) for row in rows)
    budgets = scenario.experiment_execution_budgets(VERSION)
    assert budgets == scenario.experiment_execution_budgets(scenario.V10_EXPERIMENT_VERSION)
    assert budgets == dict(suite_timeout_sec=15800., science_budget_sec=1400.,
        case_timeout_sec=900., recording_sec=720., shutdown_grace_sec=45., cleanup_reserve_sec=30.,
        labels_sec=240., references_sec=45., summary_sec=10., freeze_report_sec=40.)


@pytest.mark.parametrize('version,selected', [
    ('m4-pilot-v9', False), ('m4-pilot-v10', True), ('m4-pilot-v11', True),
    ('m4-pilot-v12', True), ('m4-pilot-v13', True), ('m4-pilot-v14', True), ('m4-pilot-v15', False), ('m4_pilot_v11', False), (None, False),
])
def test_arrival_family_is_exact_and_does_not_register_unknown_versions(version, selected):
    assert scenario.is_arrival_experiment_version(version) is selected
    assert scenario.ARRIVAL_SUITE_IDS == ('m4_pilot_v10', 'm4_pilot_v11', 'm4_pilot_v12', 'm4_pilot_v13', 'm4_pilot_v14')
    if version not in scenario.EXPERIMENT_VERSIONS:
        with pytest.raises(ValueError, match='unsupported'):
            scenario.experiment_identity(version)


def test_all_sixteen_resolved_arms_keep_matched_settings_and_selected_topics(contract):
    assert dispatch.validate_contract(contract) == Path(contract['root'])
    for row in contract['runs']:
        resolved = row['resolved_scenario']
        controls = resolved['algorithm']['launch_overrides']
        recurrent, moving = row['arm'] in 'BD', row['arm'] in 'CD'
        assert resolved['suite_id'] == 'm4_pilot_v11'
        assert controls['controller_spawner_load_recovery_enabled'] is True
        assert 'controller_spawner_load_recovery_enabled:=True' in row['launch_argv']
        assert controls['controller_config_filepath'] == str(scenario.V6_CONTROLLER_PATH)
        assert controls['convergence_metric_mode'] == (RECURRENT_MODE if recurrent else 'pde_mean_v1')
        assert controls['continuous_search_mode'] == ('rolling_gesc_v2' if moving else 'stationary_v1')
        assert controls['v2_verification_motion_mode'] == ('centered_tracking_v1' if moving else 'rolling_neighborhood_v1')
        assert controls['centroid_invalid_status_heartbeat_enabled'] is False
        assert 'centroid_window_sec' not in controls and 'centroid_epsilon_m' not in controls
        if recurrent:
            assert controls['recurrent_diagnostics_topic'] == RECURRENT_TOPIC
        if row['arm'] == 'B':
            assert controls['stationary_recurrent_fill_request_topic'] == STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
        if moving:
            assert controls['v2_direction_policy'] == 'moving_cycle_coherence_v1'
            assert (controls['v2_candidate_radius_m'], controls['v2_candidate_epsilon_m']) == (.75, .15)
        assert (runner._m4_centroid_event_selection(resolved) is not None) is recurrent
        assert (runner._m4_pde_event_selection(resolved) is not None) is (row['arm'] == 'C')
        assert not runner._requires_ranked_goal(resolved)
        assert resolved['success']['criterion'] == 'post_recovery_arrival_v1'
        recovery = resolved['success']['staged_recovery']
        assert (recovery['stage_a_timeout_sec'], recovery['post_stage_a_timeout_sec'],
                recovery['global_proximity_radius_m']) == (360., 300., .5)
        assert ('--gui' in row['runner_argv']) is row['visible']
        assert '--process-ownership-mode' in row['runner_argv']
        old_controls = scenario._arm_overrides(row['arm'], scenario.V10_EXPERIMENT_VERSION)
        new_controls = scenario._arm_overrides(row['arm'], VERSION)
        assert new_controls.pop('controller_spawner_load_recovery_enabled') is True
        assert new_controls == old_controls


@pytest.mark.parametrize('fault', ['old_method', 'old_seed', 'old_suite', 'old_policy',
    'spawner_false', 'spawner_missing', 'spawner_not_bool', 'old_labels_budget'])
def test_v11_contract_cannot_fall_back_to_old_identity_or_startup_path(contract, fault):
    row = contract['runs'][1]
    controls = row['resolved_scenario']['algorithm']['launch_overrides']
    if fault == 'old_method':
        contract['method_version'] = scenario.V10_METHOD_VERSION
    elif fault == 'old_seed':
        row['seed'] = 26091011
    elif fault == 'old_suite':
        row['resolved_scenario']['suite_id'] = 'm4_pilot_v10'
    elif fault == 'old_policy':
        contract['development_release_policy'] = 'historical_timeout_release'
    elif fault == 'spawner_false':
        controls['controller_spawner_load_recovery_enabled'] = False
    elif fault == 'spawner_missing':
        controls.pop('controller_spawner_load_recovery_enabled')
    elif fault == 'spawner_not_bool':
        controls['controller_spawner_load_recovery_enabled'] = 1
    else:
        contract['science']['labels_sec'] = 120.
    with pytest.raises(ValueError):
        dispatch.validate_contract(contract)


def test_retained_v10_scenario_bytes_remain_exact():
    root = Path('/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v10')
    retained = json.loads((root / 'preflight/contract.json').read_text())
    original_bytes = (root / 'scenario.yaml').read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == retained['scenario']['sha256']
    original = yaml.safe_load(original_bytes)
    primary = original['cases'][0]['success']['staged_recovery']['topology_qualification']
    secondary = {}
    for row, case in zip(scenario.expected_slots(scenario.V10_EXPERIMENT_VERSION), original['cases']):
        assert row['case_id'] == case['case_id']
        if row['geometry'] == 'secondary':
            secondary.setdefault(row['condition'], case['success']['staged_recovery']['topology_qualification'])
    generated = scenario.build_m4_document(secondary, runs_root=root / 'runs',
        experiment_version=scenario.V10_EXPERIMENT_VERSION, primary_topology=primary)
    assert yaml.safe_dump(generated, sort_keys=False).encode() == original_bytes
    assert all('controller_spawner_load_recovery_enabled' not in case['algorithm']['launch_overrides']
               for case in generated['cases'])


@pytest.mark.parametrize('fault', ['future_suite', 'development_suite_holdout'])
def test_schema_does_not_broaden_arrival_admission_beyond_selected_population(tmp_path, monkeypatch, fault):
    prohibit_models(monkeypatch)
    secondary, primary = topology_inputs()
    root = Path(scenario.experiment_identity(VERSION)['root'])
    document = scenario.build_m4_document(secondary, runs_root=root / 'runs',
        experiment_version=VERSION, primary_topology=primary)
    if fault == 'future_suite':
        document['suite_id'] = 'm4_pilot_v15'
    else:
        document['suite_id'] = 'v2_method_development_v1'
        document['cases'][1]['acceptance_partition'] = 'holdout'
    path = tmp_path / 'rejected.yaml'
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    with pytest.raises(ValueError):
        schema.load_suite(path)
