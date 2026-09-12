"""Exact V6 configuration/identity admission with retained V1-V5 parity.

Fixtures use retained small topology mappings and replace numerical validation.
No field evaluation, bag decoding, preparation, process or ROS graph is started.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from ros_esc.scenario_runner import m4_scenario as scenario


VERSION = 'm4-pilot-v6'
MODE = 'subreaper_group_v3'
RETAINED = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/'
                'm4_v6_matched_gain_v1/version_routes')
EARLIER = tuple(f'm4-pilot-v{number}' for number in range(1, 6))


def topology_inputs():
    values = json.loads((RETAINED/'topology_inputs.json').read_text())
    return ({condition: values[f'topology_secondary_{condition}.json']
             for condition in scenario.CONDITIONS}, values['topology_primary_nominal.json'])


@pytest.fixture
def document(tmp_path, monkeypatch):
    monkeypatch.setattr(scenario, 'PILOT_ROOT', tmp_path/'pilot')
    root = Path(scenario.experiment_identity(VERSION)['root'])
    root.mkdir(parents=True)
    secondary, primary = topology_inputs()
    return scenario.build_m4_document(secondary, runs_root=root/'runs',
        experiment_version=VERSION, primary_topology=primary)


def _build_contract(document, monkeypatch):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from ros_esc.scenario_runner import scenario_schema as schema
    from ros_esc.scenario_runner import run_scenario as runner

    def unavailable(*args, **kwargs):
        pytest.fail('source fixtures cannot evaluate a field')

    monkeypatch.setattr(truth, '_model', unavailable)
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification',
                        lambda record, *args, **kwargs: deepcopy(record))
    identity = scenario.experiment_identity(VERSION)
    root = Path(identity['root'])
    path = root/'scenario.yaml'
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    expanded, unsupported = schema.expand_suite(schema.load_suite(path))
    assert not unsupported and len(expanded) == 16
    configuration = scenario.v6_controller_configuration()
    value = dict(schema_version=1, version=VERSION, experiment_version=VERSION,
        method_version='m4-pilot-v1', root=str(root),
        contract_path=str(root/'preflight/contract.json'),
        scenario=dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()),
        controller_configuration=configuration,
        source_files=[dict(path=str(scenario._BASELINE_CONTROLLER_PATH),
                           sha256=scenario._BASELINE_CONTROLLER_SHA256),
                      dict(path=configuration['path'], sha256=configuration['sha256'])],
        execution=dict(runs_root=str(root/'runs'), process_ownership_mode=MODE,
                       recording_sec=720., case_timeout_sec=900., suite_timeout_sec=15300.,
                       cleanup_reserve_sec=30., science_budget_sec=900., shutdown_grace_sec=45.),
        science=dict(targets_sec=[15+30*k for k in range(24)], labels_sec=120.,
                     references_sec=45., summary_sec=10., freeze_report_sec=20.,
                     maximum_observations=40000),
        topology_receipts={name: dict(path=str(root/'preflight'/
            ('topology_'+('primary_nominal' if name == 'primary_nominal' else 'secondary_'+name)+'.json')),
            sha256='source-fixture') for name in (*scenario.CONDITIONS, 'primary_nominal')})
    by_case = {row['case_id']: row for row in expanded}
    value['runs'] = []
    for expected in scenario.expected_slots(VERSION):
        run_id = scenario.experiment_run_id(expected, VERSION)
        resolved = by_case[expected['case_id']]
        value['runs'].append({**expected, 'run_id': run_id, 'resolved_scenario': resolved,
            'summary_path': str(root/'acquisition'/f'summary_{expected["slot"]}.yaml'),
            'launch_argv': runner.build_launch_command(resolved, gui=expected['visible'], run_id=run_id)})
    return value


@pytest.fixture(scope='module')
def _pristine_contract(tmp_path_factory):
    """Resolve one synthetic population; every mutation gets its own deep copy."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v6_contract')/'pilot')
        root = Path(scenario.experiment_identity(VERSION)['root'])
        root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        value = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        return _build_contract(value, patch)


@pytest.fixture
def contract(_pristine_contract, monkeypatch):
    value = deepcopy(_pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(value['root']).parent)
    return value


@pytest.mark.parametrize('version', EARLIER)
def test_all_prior_scenario_outputs_match_the_preedit_bytes(version):
    path = RETAINED/(version.replace('-', '_')+'_outputs.json')
    expected = json.loads(path.read_text())
    manifest = json.loads((RETAINED/'preedit_outputs_manifest.json').read_text())
    pinned = next(row for row in manifest['outputs'] if row['path'] == str(path))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pinned['sha256']
    secondary, primary = topology_inputs()
    identity = scenario.experiment_identity(version)
    options = dict(runs_root=Path(identity['root'])/'runs', experiment_version=version)
    if version == 'm4-pilot-v5':
        options['primary_topology'] = primary
    actual = dict(experiment_identity=identity, population=scenario.expected_slots(version),
                  scenario=scenario.build_m4_document(secondary, **options))
    assert actual == expected
    assert (json.dumps(actual, sort_keys=True, indent=2, allow_nan=False)+'\n').encode() == path.read_bytes()


def test_default_version_and_new_population_keep_exact_fixed_blocks():
    assert scenario.experiment_identity() == scenario.experiment_identity('m4-pilot-v1')
    assert scenario.expected_slots() == scenario.expected_slots('m4-pilot-v1')
    assert scenario.experiment_identity(VERSION) == dict(experiment_version=VERSION,
        suite_id='m4_pilot_v6', root='/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v6',
        process_ownership_mode=MODE)
    rows = scenario.expected_slots(VERSION)
    assert [row['slot'] for row in rows] == list(range(1, 17))
    blocks = (('development', 'primary', 'nominal', 26090801),
              ('holdout', 'secondary', 'nominal', 26090802),
              ('holdout', 'secondary', 'noise', 26090803),
              ('holdout', 'secondary', 'delay', 26090804))
    for block, values in enumerate(blocks):
        for row, arm in zip(rows[4*block:4*block+4], 'ABCD'):
            assert row['arm'] == arm and row['block'] == block
            assert tuple(row[key] for key in ('partition', 'geometry', 'condition', 'seed')) == values
            assert row['visible'] is (block == 0)
            assert row['case_id'] == f'm4_v6_{values[0]}_{values[2]}_{arm}_{values[3]}'
            assert scenario.experiment_run_id(row, VERSION) == f'm4-pilot-v6-slot{row["slot"]:02d}-{arm}-{values[3]}'
    previous = {row['case_id'] for version in EARLIER for row in scenario.expected_slots(version)}
    assert not previous.intersection(row['case_id'] for row in rows)


@pytest.mark.parametrize('value', ['m4-pilot-v15', 'm4-pilot-v06', 'm4_pilot_v6', None])
def test_version_allowlist_is_still_exact(value):
    with pytest.raises(ValueError, match='unsupported'):
        scenario.experiment_identity(value)


def test_adopted_json_receipt_proves_the_only_value_change():
    receipt = scenario.v6_controller_configuration()
    assert receipt == dict(path=str(scenario.V6_CONTROLLER_PATH),
        sha256='e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606',
        profile_id='m4_gain_half_control_v6')
    old = json.loads(scenario._BASELINE_CONTROLLER_PATH.read_text())
    new = json.loads(scenario.V6_CONTROLLER_PATH.read_text())
    assert old['gains'] == dict(k_vx=1., k_wz=5.)
    assert new['gains'] == dict(k_vx=.5, k_wz=5.)
    old['gains']['k_vx'] = .5
    assert new == old
    assert new['params']['set_max_vx'] == .1 and new['params']['set_max_wz'] == .5


@pytest.mark.parametrize('fault', ['missing_selected', 'missing_baseline', 'old_gain',
                                  'ceiling', 'angular_gain', 'whitespace', 'baseline_changed'])
def test_controller_receipt_rejects_missing_or_nonadopted_bytes(tmp_path, monkeypatch, fault):
    old = scenario._BASELINE_CONTROLLER_PATH.read_bytes()
    selected = scenario.V6_CONTROLLER_PATH.read_bytes()
    first, second = tmp_path/'original.json', tmp_path/'selected.json'
    if fault == 'old_gain':
        selected = old
    elif fault == 'ceiling':
        selected = selected.replace(b'"set_max_vx": 0.1', b'"set_max_vx": 0.05')
    elif fault == 'angular_gain':
        selected = selected.replace(b'"k_wz": 5.0', b'"k_wz": 2.5')
    elif fault == 'whitespace':
        selected += b'\n'
    elif fault == 'baseline_changed':
        old += b'\n'
    if fault != 'missing_baseline':
        first.write_bytes(old)
    if fault != 'missing_selected':
        second.write_bytes(selected)
    monkeypatch.setattr(scenario, '_BASELINE_CONTROLLER_PATH', first)
    monkeypatch.setattr(scenario, 'V6_CONTROLLER_PATH', second)
    with pytest.raises((ValueError, FileNotFoundError)):
        scenario.v6_controller_configuration()


def test_v6_resource_adds_only_the_adopted_changes_to_v5(document):
    secondary, primary = topology_inputs()
    root = Path(scenario.experiment_identity('m4-pilot-v5')['root'])
    old = scenario.build_m4_document(secondary, runs_root=root/'runs',
        experiment_version='m4-pilot-v5', primary_topology=primary)
    normalized = deepcopy(document)
    normalized['suite_id'] = old['suite_id']
    normalized['metadata']['experiment_version'] = old['metadata']['experiment_version']
    normalized['execution']['runs_root'] = old['execution']['runs_root']
    assert normalized['frozen_profile']['profile_id'] == scenario.V6_CONTROL_PROFILE_ID
    normalized['frozen_profile']['profile_id'] = old['frozen_profile']['profile_id']
    assert normalized['frozen_profile']['launch_overrides'].pop('controller_config_filepath') == str(scenario.V6_CONTROLLER_PATH)
    for new, previous, arm in zip(normalized['cases'], old['cases'], 'ABCD'*4):
        new['case_id'] = previous['case_id']
        new['success']['controller']['contract_id'] = previous['case_id']
        controls = new['algorithm']['launch_overrides']
        assert 'controller_config_filepath' not in controls
        if arm in 'BD':
            assert controls.pop('centroid_invalid_status_heartbeat_enabled') is True
        else:
            assert 'centroid_invalid_status_heartbeat_enabled' not in controls
    assert normalized == old


def test_actual_schema_runner_and_contract_agree_for_all_sixteen_slots(contract):
    from ros_esc.scenario_runner import run_scenario as runner
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION
    for row in contract['runs']:
        resolved = row['resolved_scenario']
        selected = runner.resolve_controller_config_filepath(resolved['algorithm']['launch_overrides'])
        assert str(selected) == contract['controller_configuration']['path']
        metadata = runner.build_metadata(resolved, 'source-fixture', VERSION,
                                         'source fixture', run_id=row['run_id'])
        assert metadata['parameter_files'].count(str(selected)) == 1
        assert str(scenario._BASELINE_CONTROLLER_PATH) not in metadata['parameter_files']
        assert resolved['success']['staged_recovery']['local_association_mode'] == 'verified_trap'
        controls = resolved['algorithm']['launch_overrides']
        assert controls['open_field_escape_interior_anchor_fallback_enabled'] is True
        assert controls['open_field_escape_interior_anchor_min_displacement_m'] == .50
        assert controls['escape_max_sec'] == 35. and controls['verification_max_sec'] == 12.
        assert controls['convergence_metric_mode'] == ('centroid_two_block_v2' if row['arm'] in 'BD' else 'pde_mean_v1')
        assert controls['continuous_search_mode'] == ('rolling_gesc_v2' if row['arm'] in 'CD' else 'stationary_v1')


def test_v6_validation_reads_each_verified_template_once_per_call(contract, monkeypatch):
    original = scenario._template
    observed = []

    def read(name):
        observed.append(name)
        return original(name)

    monkeypatch.setattr(scenario, '_template', read)
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION
    assert observed == ['primary', 'secondary']
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION
    assert observed == ['primary', 'secondary', 'primary', 'secondary']


@pytest.mark.parametrize('geometry', ['primary', 'secondary'])
def test_next_validation_call_rejects_template_bytes_changed_after_a_pass(contract, tmp_path, monkeypatch, geometry):
    paths = {}
    for name, (filename, _) in scenario.TEMPLATES.items():
        paths[name] = tmp_path/filename
        paths[name].write_bytes((scenario.SCENARIOS/filename).read_bytes())
    monkeypatch.setattr(scenario, 'SCENARIOS', tmp_path)
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION
    with paths[geometry].open('ab') as stream:
        stream.write(b'\n# changed after the successful validation call\n')
    with pytest.raises(ValueError, match='inherited scenario template changed'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('slot', range(16))
@pytest.mark.parametrize('fault', ['profile_id', 'profile_path', 'merged_path', 'inherited_control',
                                  'heartbeat', 'heartbeat_type', 'launch_path',
                                  'duplicate_launch_path', 'launch_heartbeat'])
def test_each_slot_requires_the_exact_profile_and_launch_binding(contract, slot, fault):
    row = contract['runs'][slot]
    resolved = row['resolved_scenario']
    controls = resolved['algorithm']['launch_overrides']
    if fault == 'profile_id':
        resolved['frozen_profile']['profile_id'] = 'm4_inherited_control_v1'
    elif fault == 'profile_path':
        resolved['frozen_profile']['launch_overrides']['controller_config_filepath'] = str(scenario._BASELINE_CONTROLLER_PATH)
    elif fault == 'merged_path':
        controls['controller_config_filepath'] = str(scenario._BASELINE_CONTROLLER_PATH)
    elif fault == 'inherited_control':
        controls['escape_max_sec'] = 70.
    elif fault == 'heartbeat':
        controls['centroid_invalid_status_heartbeat_enabled'] = row['arm'] not in 'BD'
    elif fault == 'heartbeat_type':
        controls['centroid_invalid_status_heartbeat_enabled'] = 1 if row['arm'] in 'BD' else 0
    elif fault == 'launch_path':
        row['launch_argv'] = [arg for arg in row['launch_argv'] if not arg.startswith('controller_config_filepath:=')]
    elif fault == 'duplicate_launch_path':
        row['launch_argv'].append('controller_config_filepath:='+str(scenario.V6_CONTROLLER_PATH))
    else:
        row['launch_argv'].append('centroid_invalid_status_heartbeat_enabled:=False')
    with pytest.raises(ValueError, match='M4 v6'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('fault', ['missing_receipt', 'wrong_receipt_hash', 'wrong_receipt_path',
                                  'wrong_receipt_profile', 'missing_original_pin', 'missing_selected_pin'])
def test_receipt_and_original_selected_source_pins_are_mandatory(contract, fault):
    if fault == 'missing_receipt':
        contract.pop('controller_configuration')
    elif fault == 'wrong_receipt_hash':
        contract['controller_configuration']['sha256'] = '0'*64
    elif fault == 'wrong_receipt_path':
        contract['controller_configuration']['path'] = str(scenario._BASELINE_CONTROLLER_PATH)
    elif fault == 'wrong_receipt_profile':
        contract['controller_configuration']['profile_id'] = 'm4_inherited_control_v1'
    elif fault == 'missing_original_pin':
        contract['source_files'].pop(0)
    else:
        contract['source_files'].pop(1)
    with pytest.raises(ValueError, match='M4 v6 controller'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('slot', range(16))
@pytest.mark.parametrize('key,value', [
    ('convergence_metric_mode', 'centroid_window_v2'),
    ('continuous_search_mode', 'unsupported'),
    ('v2_qualification_observation_only', True),
    ('centroid_window_sec', 8.), ('centroid_epsilon_m', .24),
    ('centroid_maximum_radius_m', 1.),
    ('v2_direction_policy', 'other'),
    ('v2_candidate_radius_m', 1.), ('v2_candidate_epsilon_m', .3),
])
def test_each_arm_rejects_changed_or_foreign_method_selectors(contract, slot, key, value):
    row = contract['runs'][slot]
    row['resolved_scenario']['algorithm']['launch_overrides'][key] = value
    row['launch_argv'] = [arg for arg in row['launch_argv'] if not arg.startswith(key+':=')]
    row['launch_argv'].append(key+':='+str(value))
    with pytest.raises(ValueError, match='M4 v6 detector/direction'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('slot', range(16))
@pytest.mark.parametrize('key,value', [('centroid_maximum_gap_sec', 5.),
                                     ('centroid_pose_stale_sec', 5.),
                                     ('supervisor_command_stale_sec', 5.),
                                     ('convergence_state_gating_enabled', 1)])
def test_extra_or_mistyped_override_cannot_weaken_saved_gates(contract, slot, key, value):
    row = contract['runs'][slot]
    row['resolved_scenario']['algorithm']['launch_overrides'][key] = value
    row['launch_argv'] = [arg for arg in row['launch_argv'] if not arg.startswith(key+':=')]
    row['launch_argv'].append(key+':='+str(value))
    with pytest.raises(ValueError, match='M4 v6 detector/direction'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('slot', [0, 2, 4, 6, 8, 10, 12, 14])
def test_only_explicit_false_heartbeat_is_permitted_as_an_optional_pde_override(contract, slot):
    row = contract['runs'][slot]
    assert row['arm'] in ('A', 'C')
    row['resolved_scenario']['algorithm']['launch_overrides']['centroid_invalid_status_heartbeat_enabled'] = False
    row['launch_argv'].append('centroid_invalid_status_heartbeat_enabled:=False')
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION


@pytest.mark.parametrize('version', EARLIER)
@pytest.mark.parametrize('fault', ['root', 'case', 'run', 'suite', 'experiment'])
def test_earlier_version_cannot_replace_fresh_v6_identity(contract, version, fault):
    old = scenario.expected_slots(version)[0]
    row = contract['runs'][0]
    if fault == 'root':
        contract['root'] = scenario.experiment_identity(version)['root']
    elif fault == 'case':
        row['case_id'] = old['case_id']
    elif fault == 'run':
        row['run_id'] = scenario.experiment_run_id(old, version)
    elif fault == 'suite':
        row['resolved_scenario']['suite_id'] = scenario.experiment_identity(version)['suite_id']
    else:
        contract['experiment_version'] = version
    with pytest.raises(ValueError):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('slot', range(4))
@pytest.mark.parametrize('fault', ['missing', 'declared_source', 'cross_geometry'])
def test_all_four_primary_slots_keep_v5_topology_binding(contract, slot, fault):
    recovery = contract['runs'][slot]['resolved_scenario']['success']['staged_recovery']
    if fault == 'missing':
        recovery.pop('topology_qualification')
    elif fault == 'declared_source':
        recovery['local_association_mode'] = 'declared_source'
    else:
        recovery['topology_qualification'] = topology_inputs()[0]['nominal']
    with pytest.raises(ValueError, match='primary'):
        scenario.validate_experiment_contract(contract)


def test_schema_does_not_allow_one_arm_to_override_frozen_controller(document, monkeypatch):
    from ros_esc.scenario_runner import scenario_schema as schema
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('no field evaluation'))
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification',
                        lambda *a, **k: pytest.fail('conflict must reject before topology validation'))
    document['cases'][0]['algorithm']['launch_overrides']['controller_config_filepath'] = str(scenario._BASELINE_CONTROLLER_PATH)
    root = Path(scenario.experiment_identity(VERSION)['root'])
    path = root/'conflicting_profile.yaml'
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    with pytest.raises(ValueError, match='conflicts with frozen_profile'):
        schema.load_suite(path)


def test_v6_keeps_all_sixteen_slots_and_192_science_target_placeholders():
    from ros_esc.plotting_scripts import m4_pilot
    result = m4_pilot.aggregate_pilot([], experiment_version=VERSION)
    assert result['experiment_version'] == VERSION and result['method_version'] == 'm4-pilot-v1'
    assert len(result['slots']) == 16 and len(result['direction_rows']) == 192
    for slot in (3, 4, 7, 8, 11, 12, 15, 16):
        rows = [row for row in result['direction_rows'] if row['slot'] == slot]
        assert len(rows) == 24
