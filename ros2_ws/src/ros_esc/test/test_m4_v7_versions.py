"""Fresh V7 identity with exact V6 controls and retained six-version parity.

Only synthetic schema/builder inputs are used. Numerical qualification is
replaced by retained mappings, and the model owner must never be invoked.
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
import test_m4_v6_versions as inherited


VERSION = 'm4-pilot-v7'
MODE = 'subreaper_group_v3'
RETAINED = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/'
                'm4_v7_clock_range_comparison_v1/version_routes')
CAPTURE_SHA = '68c450ff6274005f39138ae3954f1b4c8e3d3d58c197378d3b84d7bb63bd844e'
EARLIER = tuple(f'm4-pilot-v{value}' for value in range(1, 7))


def captured(name):
    receipt_path = RETAINED/'capture_preedit_v1_receipt.json'
    assert hashlib.sha256(receipt_path.read_bytes()).hexdigest() == CAPTURE_SHA
    receipt = json.loads(receipt_path.read_text())
    assert receipt['status'] == 'PASS' and receipt['expanded_rows'] == 96
    path = RETAINED/'capture_v1'/name
    pinned = next(row for row in receipt['outputs'] if row['path'] == str(path))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pinned['sha256']
    return path


def topology_inputs():
    values = json.loads(captured('topology_inputs.json').read_text())
    return ({name: values[f'topology_secondary_{name}.json'] for name in scenario.CONDITIONS},
            values['topology_primary_nominal.json'])


def prohibit_models(monkeypatch):
    from ros_esc.scenario_runner import aggregate_field_truth as truth

    def forbidden(*_args, **_kwargs):
        pytest.fail('source fixture cannot evaluate a field')

    monkeypatch.setattr(truth, '_model', forbidden)
    monkeypatch.setattr(truth, 'derive_aggregate_field_truth', forbidden)
    monkeypatch.setattr(truth, 'derive_two_source_topology_qualification', forbidden)
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification',
                        lambda record, *_args, **_kwargs: deepcopy(record))


@pytest.fixture(scope='module')
def pristine_contract(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', tmp_path_factory.mktemp('m4_v7_contract')/'pilot')
        patch.setattr(inherited, 'VERSION', VERSION)
        root = Path(scenario.experiment_identity(VERSION)['root'])
        root.mkdir(parents=True)
        secondary, primary = topology_inputs()
        document = scenario.build_m4_document(secondary, runs_root=root/'runs',
            experiment_version=VERSION, primary_topology=primary)
        prohibit_models(patch)
        return inherited._build_contract(document, patch)


@pytest.fixture
def contract(pristine_contract, monkeypatch):
    value = deepcopy(pristine_contract)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', Path(value['root']).parent)
    return value


@pytest.mark.parametrize('version', EARLIER)
def test_all_six_prior_populations_and_ninety_six_builder_rows_are_exact(version, monkeypatch):
    from ros_esc.scenario_runner import scenario_schema as schema
    prohibit_models(monkeypatch)
    path = captured(version.replace('-', '_')+'_outputs.json')
    expected = json.loads(path.read_text())
    secondary, primary = topology_inputs()
    identity = scenario.experiment_identity(version)
    options = dict(runs_root=Path(identity['root'])/'runs', experiment_version=version)
    if version in ('m4-pilot-v5', 'm4-pilot-v6'):
        options['primary_topology'] = primary
    document = scenario.build_m4_document(secondary, **options)
    assert document == expected['scenario']
    scenario_path = captured(version.replace('-', '_')+'_scenario.yaml')
    assert yaml.safe_dump(document, sort_keys=False).encode() == scenario_path.read_bytes()
    expanded, unsupported = schema.expand_suite(schema.load_suite(scenario_path))
    assert not unsupported and len(expanded) == 16
    by_case = {row['case_id']: row for row in expanded}
    rows = []
    for slot in scenario.expected_slots(version):
        resolved = by_case[slot['case_id']]
        run_id = scenario.experiment_run_id(slot, version)
        kwargs = dict(gui=slot['visible'], run_id=run_id)
        rows.append(dict(slot=slot, resolved=resolved, kwargs=kwargs,
            launch_argv=runner.build_launch_command(resolved, **kwargs),
            metadata=runner.build_metadata(resolved, 'retained-fixture', version,
                'Pure pre-edit builder fixture; no runtime acquisition.', run_id=run_id)))
    actual = dict(experiment_identity=identity, population=scenario.expected_slots(version),
                  scenario=document, expanded_rows=rows, scenario_path=str(scenario_path))
    assert (json.dumps(actual, indent=2, sort_keys=True, allow_nan=False)+'\n').encode() == path.read_bytes()


def test_fresh_v7_identity_keeps_the_default_and_exact_fixed_blocks():
    assert scenario.experiment_identity() == scenario.experiment_identity('m4-pilot-v1')
    assert scenario.experiment_identity(VERSION) == dict(experiment_version=VERSION,
        suite_id='m4_pilot_v7', root='/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v7',
        process_ownership_mode=MODE)
    prior = scenario.expected_slots('m4-pilot-v6')
    rows = scenario.expected_slots(VERSION)
    assert len(rows) == 16
    previous_ids = {item['case_id'] for version in EARLIER for item in scenario.expected_slots(version)}
    for old, new in zip(prior, rows):
        assert new == {**old, 'experiment_version': VERSION,
                       'case_id': old['case_id'].replace('m4_v6_', 'm4_v7_', 1)}
        assert new['case_id'] not in previous_ids
        assert scenario.experiment_run_id(new, VERSION) == (
            f'm4-pilot-v7-slot{new["slot"]:02d}-{new["arm"]}-{new["seed"]}')


@pytest.mark.parametrize('value', ['m4-pilot-v15', 'm4-pilot-v07', 'm4_pilot_v7', None])
def test_future_and_noncanonical_versions_remain_rejected(value):
    with pytest.raises(ValueError, match='unsupported'):
        scenario.experiment_identity(value)


def test_v7_inherits_the_complete_v6_controller_and_stage_maps(contract):
    assert scenario.validate_experiment_contract(contract)['experiment_version'] == VERSION
    old = json.loads(captured('m4_pilot_v6_outputs.json').read_text())
    expected = {row['slot']['slot']: row for row in old['expanded_rows']}
    assert contract['controller_configuration'] == scenario.v6_controller_configuration()
    assert contract['controller_configuration']['profile_id'] == 'm4_gain_half_control_v6'
    for row in contract['runs']:
        previous = expected[row['slot']]['resolved']
        resolved = row['resolved_scenario']
        assert resolved['algorithm'] == previous['algorithm']
        assert resolved['frozen_profile'] == previous['frozen_profile']
        assert resolved['success']['staged_recovery'] == previous['success']['staged_recovery']
        for key in ('start', 'bounds_m', 'sources', 'disturbances', 'validation', 'metric_applicability'):
            assert resolved[key] == previous[key]
        metadata = runner.build_metadata(resolved, 'fixture', VERSION, '', run_id=row['run_id'])
        assert metadata['parameter_files'].count(str(scenario.V6_CONTROLLER_PATH)) == 1
        assert str(runner.GESC_CONTROLLER) not in metadata['parameter_files']
        selected = runner._m4_centroid_event_selection(resolved)
        assert (selected is not None) is (row['arm'] in ('B', 'D'))
        if selected is not None:
            assert (selected['metric_mode'], selected['window_sec'], selected['epsilon_m'],
                    selected['maximum_radius_m']) == ('centroid_two_block_v2', 6., .18, .5)


@pytest.mark.parametrize('slot', range(16))
@pytest.mark.parametrize('fault', ['heartbeat', 'merged_path', 'inherited_control'])
def test_every_v7_slot_retains_strict_configuration_guards(contract, slot, fault):
    inherited.test_each_slot_requires_the_exact_profile_and_launch_binding(contract, slot, fault)


@pytest.mark.parametrize('fault', ['missing_receipt', 'wrong_receipt_hash', 'wrong_receipt_path',
                                  'wrong_receipt_profile', 'missing_original_pin', 'missing_selected_pin'])
def test_v7_retains_controller_receipt_guards(contract, fault):
    inherited.test_receipt_and_original_selected_source_pins_are_mandatory(contract, fault)


@pytest.mark.parametrize('field', ['root', 'run', 'case', 'suite', 'summary', 'experiment', 'method', 'mode'])
def test_v6_receipts_and_identifiers_cannot_be_substituted_into_v7(contract, field):
    row = contract['runs'][0]
    if field == 'root':
        contract['root'] = str(Path(contract['root']).with_name('m4_pilot_v6'))
    elif field == 'run':
        row['run_id'] = row['run_id'].replace('m4-pilot-v7', 'm4-pilot-v6')
    elif field == 'case':
        row['case_id'] = row['case_id'].replace('m4_v7_', 'm4_v6_')
    elif field == 'suite':
        row['resolved_scenario']['suite_id'] = 'm4_pilot_v6'
    elif field == 'summary':
        row['summary_path'] = row['summary_path'].replace('m4_pilot_v7', 'm4_pilot_v6')
    elif field == 'experiment':
        contract['experiment_version'] = 'm4-pilot-v6'
    elif field == 'method':
        contract['method_version'] = VERSION
    else:
        contract['execution']['process_ownership_mode'] = 'subreaper_v2'
    with pytest.raises(ValueError, match='M4'):
        scenario.validate_experiment_contract(contract)


@pytest.mark.parametrize('mode,strict,accepted', [
    (MODE, True, True), (MODE, False, False),
    ('subreaper_v2', True, False), ('observed_tree_v1', True, False),
])
def test_runner_admits_v7_only_with_existing_strict_group_owner(monkeypatch, mode, strict, accepted):
    class Admitted(Exception):
        pass

    def expansion(*_args, **_kwargs):
        raise Admitted

    monkeypatch.setattr(runner, 'load_suite', lambda *_args: {'suite_id': 'm4_pilot_v7'})
    monkeypatch.setattr(runner, 'expand_suite', expansion)
    with pytest.raises(Admitted if accepted else ValueError):
        runner.execute_suite('synthetic', 'fixture', process_ownership_mode=mode, strict_cleanup=strict)


def test_method_denominators_and_cross_version_analysis_remain_strict(contract):
    result = metrics.aggregate_pilot([], experiment_version=VERSION)
    assert result['experiment_version'] == VERSION and result['method_version'] == 'm4-pilot-v1'
    assert len(result['slots']) == 16 and len(result['direction_rows']) == 192
    assert result['slot_status_counts'] == {'UNSTARTED': 16}
    row = contract['runs'][2]
    normalized = metrics.normalize_direction_targets([], {'qualified': False, 'origin_ns': None,
        'integrity_errors': []}, run_id=row['run_id'], arm='C', partition='development',
        condition='nominal', experiment_version=VERSION)
    assert len(normalized['targets']) == 24
    assert normalized['method_version'] == metrics.VERSION
    with pytest.raises(ValueError):
        metrics.validate_experiment_document(normalized, 'm4-pilot-v6')
