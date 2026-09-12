"""V10 arrival comparison selection through existing owners; no numerical jobs."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner import scenario_schema as schema
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
from test_q1_launch_frontend import parsed_launch  # noqa: F401
from test_q7_launch_selection import parameters
from test_m4_dispatch import dispatch
import test_m4_v6_versions as inherited
from test_m4_v9_versions import topology_inputs, prohibit_models


VERSION = scenario.V10_EXPERIMENT_VERSION
EARLIER = tuple(f'm4-pilot-v{number}' for number in range(1, 10))


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v10_contract')/'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root']); root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        value = inherited._build_contract(document, patch)
        value['method_version'] = scenario.V10_METHOD_VERSION
        value['development_release_policy'] = scenario.V10_RELEASE_POLICY
        budgets = scenario.experiment_execution_budgets(VERSION)
        for name in value['execution']:
            if name in budgets: value['execution'][name] = budgets[name]
        for name in value['science']:
            if name in budgets: value['science'][name] = budgets[name]
        for row in value['runs']:
            row['runner_argv'] = dispatch.runner_command(value, row)
        return value


@pytest.fixture
def contract(pristine_contract, monkeypatch):
    result = deepcopy(pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(result['root']).parent)
    return result


def test_v10_identity_population_and_caps_are_distinct_and_fixed():
    assert scenario.experiment_method_version(VERSION) == 'recurrent_arrival_v10'
    assert scenario.experiment_identity(VERSION)['suite_id'] == 'm4_pilot_v10'
    rows = scenario.expected_slots(VERSION)
    assert len(rows) == 16 and [r['seed'] for r in rows] == [26091011+i//4 for i in range(16)]
    assert [r['partition'] for r in rows] == ['development']*4+['holdout']*12
    assert [r['visible'] for r in rows] == [True]*4+[False]*12
    assert [r['arm'] for r in rows] == list('ABCD')*4
    assert [r['condition'] for r in rows] == ['nominal']*8+['noise']*4+['delay']*4
    old = {scenario.experiment_run_id(row, version) for version in EARLIER
           for row in scenario.expected_slots(version)}
    assert not old.intersection(scenario.experiment_run_id(row, VERSION) for row in rows)
    b = scenario.experiment_execution_budgets(VERSION)
    assert b == dict(suite_timeout_sec=15800., science_budget_sec=1400., case_timeout_sec=900.,
        recording_sec=720., shutdown_grace_sec=45., cleanup_reserve_sec=30., labels_sec=240.,
        references_sec=45., summary_sec=10., freeze_report_sec=40.)
    assert 16*b['case_timeout_sec']+b['science_budget_sec'] == b['suite_timeout_sec']
    assert 4*(b['labels_sec']+2*b['references_sec']+b['summary_sec'])+b['freeze_report_sec'] == b['science_budget_sec']
    for version in EARLIER:
        assert scenario.experiment_method_version(version) == 'm4-pilot-v1'
        assert scenario.experiment_execution_budgets(version)['labels_sec'] == 120.
        assert scenario.experiment_execution_budgets(version)['suite_timeout_sec'] == 15300.
        assert scenario.experiment_execution_budgets(version)['freeze_report_sec'] == 20.


def test_exact_selected_methods_arrival_and_matched_inherited_settings(contract):
    assert dispatch.validate_contract(contract) == Path(contract['root'])
    for row in contract['runs']:
        resolved = row['resolved_scenario']; controls = resolved['algorithm']['launch_overrides']
        recurrent, moving = row['arm'] in 'BD', row['arm'] in 'CD'
        assert controls['convergence_metric_mode'] == (RECURRENT_MODE if recurrent else 'pde_mean_v1')
        assert controls['continuous_search_mode'] == ('rolling_gesc_v2' if moving else 'stationary_v1')
        assert controls['v2_verification_motion_mode'] == ('centered_tracking_v1' if moving else 'rolling_neighborhood_v1')
        assert controls['centroid_invalid_status_heartbeat_enabled'] is False
        assert controls['controller_config_filepath'] == str(scenario.V6_CONTROLLER_PATH)
        assert 'centroid_window_sec' not in controls and 'centroid_epsilon_m' not in controls
        if recurrent: assert controls['recurrent_diagnostics_topic'] == RECURRENT_TOPIC
        if moving:
            assert controls['v2_direction_policy'] == 'moving_cycle_coherence_v1'
            assert (controls['v2_candidate_radius_m'], controls['v2_candidate_epsilon_m']) == (.75, .15)
        selected = runner._m4_centroid_event_selection(resolved)
        assert (selected is not None) is recurrent
        assert resolved['success']['criterion'] == 'post_recovery_arrival_v1'
        assert not runner._requires_ranked_goal(resolved)
        assert resolved['success']['controller']['required_event_sequence'] == [
            'CONVERGENCE_CONFIRMED', 'FILL_CREATED', 'ESCAPE_STARTED']
        recovery = resolved['success']['staged_recovery']
        assert (recovery['stage_a_timeout_sec'], recovery['post_stage_a_timeout_sec'],
                recovery['global_proximity_radius_m']) == (360., 300., .5)
        assert '--process-ownership-mode' in row['runner_argv']
        assert ('--gui' in row['runner_argv']) is row['visible']
    for block in range(4):
        c, d = [contract['runs'][block*4+n]['resolved_scenario']['algorithm']['launch_overrides'] for n in (2, 3)]
        c = {k:v for k,v in c.items() if k not in ('convergence_metric_mode', 'recurrent_diagnostics_topic')}
        d = {k:v for k,v in d.items() if k not in ('convergence_metric_mode', 'recurrent_diagnostics_topic')}
        assert c == d


@pytest.mark.parametrize('slot', [0, 1, 2, 3, 12, 13, 14, 15])
def test_v10_selected_actual_frontend_keeps_typed_pose_and_motion_routes(contract, parsed_launch, slot):
    row = contract['runs'][slot]
    values = dict(arg.split(':=', 1) for arg in row['launch_argv'][4:])
    _, owners = parameters(parsed_launch, values)
    pose = '/gesc_gaussian/simulation/pose_delayed' if row['condition'] == 'delay' else '/odom'
    assert owners['convergence_detector_node']['pose_topic'] == pose
    assert owners['supervisor_node']['pose_topic'] == pose
    if row['arm'] == 'B':
        assert owners['gaussian_fill_node']['pose_topic'] == pose
        assert owners['gaussian_fill_node']['stationary_recurrent_fill_request_topic'] == (
            '/gesc_gaussian/v2/stationary_recurrent_fill_requests')
    if row['arm'] in 'CD':
        assert owners['supervisor_node']['v2_verification_motion_mode'] == 'centered_tracking_v1'


@pytest.mark.parametrize('fault', ['old_method', 'policy', 'suite', 'seed', 'heartbeat', 'detector',
    'centered', 'request_topic', 'arrival', 'required_fill', 'radius', 'labels', 'science', 'suite_budget', 'freeze_budget'])
def test_v10_contract_rejects_cross_method_and_budget_substitutions(contract, fault):
    row = contract['runs'][1]; controls = row['resolved_scenario']['algorithm']['launch_overrides']
    success = row['resolved_scenario']['success']
    if fault == 'old_method': contract['method_version'] = 'm4-pilot-v1'
    elif fault == 'policy': contract['development_release_policy'] = 'historical_timeout_release'
    elif fault == 'suite': row['resolved_scenario']['suite_id'] = 'm4_pilot_v9'
    elif fault == 'seed': row['seed'] = 26090801
    elif fault == 'heartbeat': controls['centroid_invalid_status_heartbeat_enabled'] = True
    elif fault == 'detector': controls['convergence_metric_mode'] = 'centroid_two_block_v2'
    elif fault == 'centered': contract['runs'][2]['resolved_scenario']['algorithm']['launch_overrides']['v2_verification_motion_mode'] = 'rolling_neighborhood_v1'
    elif fault == 'request_topic': controls['stationary_recurrent_fill_request_topic'] = '/wrong'
    elif fault == 'arrival': success.pop('criterion')
    elif fault == 'required_fill': success['all_of'].remove('fill_cardinality')
    elif fault == 'radius': success['staged_recovery']['global_proximity_radius_m'] = .6
    elif fault == 'labels': contract['science']['labels_sec'] = 120.
    elif fault == 'science': contract['execution']['science_budget_sec'] = 900.
    elif fault == 'freeze_budget': contract['science']['freeze_report_sec'] = 20.
    else: contract['execution']['suite_timeout_sec'] = 15300.
    with pytest.raises(ValueError): dispatch.validate_contract(contract)


@pytest.mark.parametrize('mode,strict,accepted', [
    ('subreaper_group_v3', True, True), ('subreaper_group_v3', False, False),
    ('subreaper_v2', True, False), ('observed_tree_v1', True, False),
])
def test_v10_runner_requires_existing_strict_group_owner(monkeypatch, mode, strict, accepted):
    class Admitted(Exception): pass
    def expansion(*args, **kwargs): raise Admitted
    monkeypatch.setattr(runner, 'load_suite', lambda *_args: {'suite_id':'m4_pilot_v10'})
    monkeypatch.setattr(runner, 'expand_suite', expansion)
    with pytest.raises(Admitted if accepted else ValueError):
        runner.execute_suite('fixture', 'fixture', process_ownership_mode=mode, strict_cleanup=strict)


def test_v10_dispatch_reserves_new_outer_budget_before_any_runtime(contract, monkeypatch):
    """Actual dispatcher admission/receipt; stop at the first injected runtime hook."""
    monkeypatch.setenv('ROS_DOMAIN_ID', '79')
    contract['execution']['ros_domain_id'] = 79
    path = Path(contract['contract_path']); path.parent.mkdir(parents=True)
    path.write_text(json.dumps(contract))
    monkeypatch.setattr(dispatch.time, 'monotonic', lambda: 100.)
    def no_runtime(): raise RuntimeError('deliberate pre-runtime source fixture stop')
    monkeypatch.setattr(runner, 'ensure_ros_daemon', no_runtime)
    monkeypatch.setattr(runner, 'run_record_process', lambda *a, **k: pytest.fail('source fixture launched'))
    result = dispatch.dispatch(path, verify_frozen=lambda *_: None,
        analyze_block=lambda *_: pytest.fail('source fixture analyzed'),
        release_holdouts=lambda *_: pytest.fail('source fixture released'),
        finalize=lambda *_: {'complete':True})
    assert result['status'] == 'INCOMPLETE' and 'deliberate pre-runtime' in result['failure']
    assert result['suite_deadline'] == 15900.
    assert result['slots'][0]['case_deadline'] == 1000.
    assert result['slots'][0]['dispatch_attempted'] is False
    assert all(row['status'] == 'UNSTARTED' for row in result['slots'][1:])
    assert result['holdout_release'] is None and not result['replacements_dispatched']


def test_retained_v9_scenario_bytes_remain_exact(monkeypatch):
    root = Path('/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9')
    retained = json.loads((root/'preflight/contract.json').read_text())
    path = root/'scenario.yaml'
    import hashlib
    assert hashlib.sha256(path.read_bytes()).hexdigest() == retained['scenario']['sha256']
    # The retained JSON fixture sorts mapping keys; the original model-to-YAML
    # path preserves insertion order. Reuse its already bound inputs so this
    # remains exact byte parity, including the original serialization order.
    original = yaml.safe_load(path.read_text())
    primary = original['cases'][0]['success']['staged_recovery']['topology_qualification']
    secondary = {}
    for slot, case in zip(scenario.expected_slots('m4-pilot-v9'), original['cases']):
        assert case['case_id'] == slot['case_id']
        if slot['geometry'] == 'secondary':
            secondary.setdefault(slot['condition'], case['success']['staged_recovery']['topology_qualification'])
    fixture_secondary, fixture_primary = topology_inputs()
    assert secondary == fixture_secondary and primary == fixture_primary
    document = scenario.build_m4_document(secondary, runs_root=root/'runs',
        experiment_version='m4-pilot-v9', primary_topology=primary)
    assert yaml.safe_dump(document, sort_keys=False).encode() == path.read_bytes()


def test_m4v9_cannot_relabel_its_old_scenario_as_arrival(tmp_path, monkeypatch):
    prohibit_models(monkeypatch)
    secondary, primary = topology_inputs()
    root = Path(scenario.experiment_identity('m4-pilot-v9')['root'])
    document = scenario.build_m4_document(secondary, runs_root=root/'runs',
        experiment_version='m4-pilot-v9', primary_topology=primary)
    document['cases'][0]['success']['criterion'] = 'post_recovery_arrival_v1'
    path = tmp_path/'invalid.yaml'; path.write_text(yaml.safe_dump(document))
    with pytest.raises(ValueError, match='arrival contract'): schema.load_suite(path)
