"""V13 extends existing workflow fixtures; no scientific child or model runs."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
import m4_science_job
import test_m4_v10_workflow as inherited
from test_m4_workflow import acquisition, workflow

VERSION = 'm4-pilot-v13'
POLICY = 'qualified_trapping_integrated_arrival_v1'
_REAL_BINDING = workflow._v13_trapping_integrated_binding
_BASE_JOBS = inherited.fake_jobs


@pytest.fixture(scope='module')
def preparation(tmp_path_factory):
    binding = _REAL_BINDING()  # Read only the exact small receipts and preserved source files.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inherited, 'VERSION', VERSION)
        patch.setattr(workflow, '_v13_trapping_integrated_binding', lambda: deepcopy(binding))
        patch.setattr(workflow, '_runtime_binding', lambda version: workflow._v10_runtime_binding())
        result = inherited.preparation.__wrapped__(tmp_path_factory)
    result['binding'] = binding
    return result


@pytest.fixture
def prepared(preparation, monkeypatch):
    monkeypatch.setattr(inherited, 'VERSION', VERSION)
    monkeypatch.setattr(inherited, 'FIELDS', dict(version=metrics.VERSION, **metrics.experiment_fields(VERSION)))
    monkeypatch.setattr(workflow, '_v13_trapping_integrated_binding', lambda: deepcopy(preparation['binding']))
    monkeypatch.setattr(workflow, '_runtime_binding', lambda version: workflow._v10_runtime_binding())
    return inherited.prepared.__wrapped__(preparation, monkeypatch)


def development(prepared, monkeypatch, *, absent_arrival=None, stops=0,
                motion_status='OBSERVED_CONTINUOUS_ACQUISITION', direction_error=20., timeout=None):
    def jobs(patch, contract, acquired, *, timeout=None):
        for row in acquired:
            passed = row['arm'] in ('B', 'D') and row['arm'] != absent_arrival
            row['behavior_passed'] = passed
            row['runner_result']['outcomes'] = dict.fromkeys(inherited.SEQUENCE_KEYS, passed)
            row['runner_result']['outcomes']['required_state_path_passed'] = False
            path = Path(row['receipt']['path'])
            path.write_text(json.dumps({key:value for key,value in row.items() if key != 'receipt'}))
            row['receipt'] = workflow.receipt(path)
        calls = _BASE_JOBS(patch, contract, acquired, timeout=timeout)
        original = m4_science_job.finite_science_job
        def run(argv, log_path, receipt_path, **kwargs):
            result = original(argv, log_path, receipt_path, **kwargs)
            if not result['complete']:
                return result
            output = Path(log_path).parent
            if argv[2] == 'labels':
                path = output/'labels.json'; data = workflow.read_json(path)
                for row in data['runs']:
                    arrived = row['arm'] in ('B', 'D') and row['arm'] != absent_arrival
                    row.update(arrival_passed=arrived, time_to_arrival_sec=175. if arrived else None,
                        arrival_binding_method=metrics.RECORDED_ARRIVAL_BINDING,
                        combined_sequence_passed=arrived,
                        combined_sequence_required_keys=list(metrics.arrival_sequence_required_keys(VERSION)),
                        combined_sequence_diagnostic_keys=['required_state_path_passed'])
                    if row['arm'] == 'D':
                        row['mandatory_stopped_acquisitions'] = stops
                        row['mandatory_stop_evidence']['status'] = motion_status
                path.write_text(json.dumps(data))
            elif argv[2] == 'references':
                path = output/f'slot_{argv[-1]}_references.json'; data = workflow.read_json(path)
                data['rows'][0].update(exposure_status='observed', input_qualified=True,
                    reference_qualified=True, informative=True, eligible=True, usable_output=True,
                    usable_averaging=True, actual_error_deg=direction_error,
                    instantaneous_error_deg=30., paired_improvement_deg=30.-direction_error)
                path.write_text(json.dumps(data))
            else:
                path = output/'result.json'; data = workflow.read_json(path)
                data.update(scientific_scope='integrated_arrival_direction_v1',
                            secondary_endpoint='independent_basin_entry_latency')
                for row in data['runs']:
                    if row['arm'] in ('C', 'D'):
                        row['direction_summary'] = metrics.summarize_direction(row.get('direction_rows', []))
                path.write_text(json.dumps(data))
            return result
        patch.setattr(m4_science_job, 'finite_science_job', run)
        return calls
    monkeypatch.setattr(inherited, 'fake_jobs', jobs)
    return inherited.development(prepared, monkeypatch, timeout=timeout)


def test_v13_real_preparation_preserves_population_budgets_and_completed_bridge(prepared):
    assert workflow.verify_frozen(prepared)
    assert prepared['method_version'] == 'recurrent_trapping_integrated_arrival_v13'
    assert prepared['development_release_policy'] == POLICY
    assert {row['seed'] for row in prepared['runs']} == set(range(26091141,26091145))
    assert prepared['science']['labels_sec'] == 240.
    assert prepared['execution']['suite_timeout_sec'] == 15800.
    binding = prepared['trapping_integrated_prerequisite']
    assert binding['status'] == 'PASS' and binding['archive']['sha256'] == workflow.D02_ARCHIVE_SHA256
    assert binding['component_response']['decision']['sha256'] == workflow.R10_DECISION_SHA256
    assert len(binding['permitted_orchestration_changes']) == 6
    assert not any(Path(ref['path']).suffix == '.db3' for ref in binding['receipts'])
    assert prepared['runs'][3]['resolved_scenario']['algorithm']['launch_overrides']['v2_verification_evidence_policy'] == 'recurrent_trapping_v1'


def test_actual_r21_runtime_has_new_types_and_rejects_old_overlay(monkeypatch):
    binding = workflow._runtime_binding(VERSION)
    assert binding['environment_script']['path'] == str(workflow.R21_ROOT/'runtime_environment.sh')
    assert {'RecurrentCandidateSnapshot','RecurrentFillCommand'} <= set(binding['generated_fields'])
    import ament_index_python.packages as packages
    monkeypatch.setattr(packages, 'get_package_prefix', lambda _: str(workflow.V10_INTERFACE_INSTALL/'ros_esc_interfaces'))
    with pytest.raises(ValueError, match='selected stationary recurrent interface overlay'):
        workflow._runtime_binding(VERSION)


def test_both_arrivals_continuous_direction_release_once_despite_censored_latency(prepared, monkeypatch):
    rows, block, calls = development(prepared, monkeypatch)
    assert [name for name,*_ in calls] == ['labels','references_3','references_4','summary']
    release = workflow.release_holdouts(prepared, rows, block, 1000.)
    evidence = release['development_evidence']
    assert evidence['enabled_arrival_slots'] == [2,4]
    assert evidence['integrated_D_checks']['status'] == 'PASS'
    assert len(release['holdouts']) == 12
    summary = workflow.read_json(block['result']['path'])
    assert all(row['latency']['right_censored'] for row in summary['runs'])
    assert all(row['behavior_passed'] is False for row in rows if row['arm'] in ('A','C'))
    with pytest.raises(FileExistsError): workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('arm', ['B','D'])
def test_either_enabled_arrival_alone_cannot_release_v13(prepared, monkeypatch, arm):
    rows, block, _ = development(prepared, monkeypatch, absent_arrival=arm)
    with pytest.raises(ValueError, match='both B and D'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('stops,status', [(1,'OBSERVED_CONTINUOUS_ACQUISITION'),
    (None,'OBSERVED_CONTINUOUS_ACQUISITION'), (0,'NO_ACQUISITION_OBSERVED'),
    (0,'OBSERVED_ZERO_COMMAND_INTERVAL')])
def test_unknown_or_measured_stops_do_not_release(prepared, monkeypatch, stops, status):
    rows, block, _ = development(prepared, monkeypatch, stops=stops, motion_status=status)
    with pytest.raises(ValueError, match='continuous verification/design'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


def test_failed_direction_blocks_even_when_acquisition_and_arrival_pass(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch, direction_error=80.)
    with pytest.raises(ValueError, match='direction gates'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


def test_forged_direction_summary_is_not_authority(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    changed = inherited.rewrite_result(prepared, block,
        lambda data: data['runs'][3]['direction_summary'].update(median_error_deg=0.))
    with pytest.raises(ValueError, match='direction gates'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)


@pytest.mark.parametrize('stage', ['labels','references_4','summary'])
def test_incomplete_science_still_withholds(prepared, monkeypatch, stage):
    rows, block, _ = development(prepared, monkeypatch, timeout=stage)
    with pytest.raises(ValueError, match='usable development analysis'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('fault', ['missing','status','archive','runtime'])
def test_frozen_prerequisite_or_runtime_change_rejected(prepared, fault):
    if fault == 'missing': prepared.pop('trapping_integrated_prerequisite')
    elif fault == 'runtime': prepared['runtime_binding'] = {}
    else: prepared['trapping_integrated_prerequisite'][fault] = 'changed'
    Path(prepared['contract_path']).write_text(json.dumps(prepared))
    with pytest.raises(ValueError): workflow.verify_frozen(prepared)


@pytest.mark.parametrize('name', ['retained_component/result.json',
    'visible_integrated_D_02/analysis_v1/receipt.json',
    'visible_integrated_D_02/cached_complete_review_v1.json'])
def test_incomplete_original_prerequisite_is_rejected(monkeypatch, name):
    original = workflow.read_json
    def read(path):
        data = original(path)
        if Path(path) == workflow.R21_ROOT/name:
            data = deepcopy(data)
            if 'analysis_complete' in data: data['analysis_complete'] = False
            else: data['status'] = 'FAIL'
        return data
    monkeypatch.setattr(workflow, 'read_json', read)
    with pytest.raises(ValueError, match='prerequisite'):
        _REAL_BINDING()


@pytest.mark.parametrize('name', ['ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/recurrent_geometry.py',
    'ros2_ws/src/ros_esc/test/test_r21_trapping_nomination.py'])
def test_undeclared_science_or_test_source_change_rejected(monkeypatch, name):
    original = workflow.receipt
    def changed(path):
        ref = original(path)
        if Path(path) == workflow.REPOSITORY/name: ref['sha256'] = '0'*64
        return ref
    monkeypatch.setattr(workflow, 'receipt', changed)
    with pytest.raises(ValueError, match='changed'): _REAL_BINDING()


def test_old_v12_current_source_gate_still_fails_closed():
    with pytest.raises(ValueError, match='changed'):
        workflow._v12_component_response_binding()


def test_late_original_prerequisite_mutation_withholds(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    original, original_receipt = workflow._verify_v10_development_science, workflow.receipt
    def verify(*args):
        evidence = original(*args)
        def changed(path):
            ref = original_receipt(path)
            if Path(path) == workflow.R21_ROOT/'retained_component/result.json': ref['sha256'] = '0'*64
            return ref
        monkeypatch.setattr(workflow, 'receipt', changed)
        return evidence
    monkeypatch.setattr(workflow, '_verify_v10_development_science', verify)
    with pytest.raises(ValueError, match='changed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (Path(prepared['root'])/'preflight/holdout_release.json').exists()


def test_failed_finalization_keeps_sixteen_and_secondary_unavailable(prepared, monkeypatch):
    rows, _, _ = development(prepared, monkeypatch, timeout='labels')
    rows.extend(acquisition(prepared, slot, status='UNSTARTED', integrity=False) for slot in range(5,17))
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path']); report = Path(final['report']['path']).read_text()
    assert result['slot_status_counts']['UNSTARTED'] == 12
    assert result['primary_outcomes']['confirmation']['planned_run_count'] == 12
    assert result['combined_method_confirmation']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['development_release']['status'] == 'WITHHELD'
    assert 'R21/D02 prerequisite: PASS' in report and '>=30% reduction' in report
    assert '12 runs, 144 direction targets' in report


def test_missing_archived_component_receipt_blocks(monkeypatch):
    original = workflow.receipt
    def missing(path):
        if Path(path) == workflow.R21_ROOT/'retained_component/result.json':
            raise FileNotFoundError('missing retained component')
        return original(path)
    monkeypatch.setattr(workflow, 'receipt', missing)
    with pytest.raises(FileNotFoundError, match='missing retained component'):
        _REAL_BINDING()


def test_source_collection_reuses_helpers_and_binds_all_prerequisite_receipts(prepared, monkeypatch, tmp_path):
    binding = prepared['trapping_integrated_prerequisite']
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **kw: b'')
    monkeypatch.setattr(workflow, 'TOOLS', tmp_path)
    monkeypatch.setattr(workflow, '_runtime_binding', lambda version: {'files': []})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kw: {'metadata_files': [], 'entry_points': []})
    monkeypatch.setattr(workflow, 'receipt', lambda path: {'path':str(Path(path)), 'sha256':'fixture'})
    refs = {ref['path'] for ref in workflow.collect_sources(VERSION)}
    expected = {str(workflow.V13_SOURCE_ROOT/name) for name in (
        'validate_source.py','tests_v1.json','save_source_checkpoint.py','prepare_once.py',
        'archive_preparation.py','release_dispatch.py','acquire_once.py','version_fixture_bridge.json')}
    expected.update(ref['path'] for ref in binding['receipts'])
    expected.add(str(workflow.REPOSITORY/'docs/codex/gesc_gaussian/v2/m4_v13_integrated_comparison_plan.md'))
    assert expected <= refs


def test_b_arrival_cannot_use_historical_binding(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    labels_path = Path(prepared['root'])/'analysis/block_0/labels.json'
    labels = workflow.read_json(labels_path)
    labels['runs'][1]['arrival_binding_method'] = 'historical_binding'
    labels_path.write_text(json.dumps(labels))
    def mutate(data):
        data['runs'][1]['arrival_binding_method'] = 'historical_binding'
        data['labels'] = workflow.receipt(labels_path)
    changed = inherited.rewrite_result(prepared, block, mutate)
    with pytest.raises(ValueError, match='recorded arrival binding'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)
