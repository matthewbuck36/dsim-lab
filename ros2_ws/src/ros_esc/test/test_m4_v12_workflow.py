"""V12 uses the existing workflow and exact completed R10 prerequisite receipts.

No child, model or bag is opened. Temporary workflow artifacts reuse existing
fixtures; R10 checks read only the small selected receipts/current source bytes.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
import m4_science_job
import test_m4_v10_workflow as inherited
from test_m4_workflow import acquisition, workflow
from test_m4_v12_science import integrated_rows

VERSION = 'm4-pilot-v12'
POLICY = 'component_response_integrated_arrival_v1'
_BASE_FAKE_JOBS = inherited.fake_jobs


@pytest.fixture(scope='module')
def preparation(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inherited, 'VERSION', VERSION)
        return inherited.preparation.__wrapped__(tmp_path_factory)


@pytest.fixture
def prepared(preparation, monkeypatch):
    monkeypatch.setattr(inherited, 'VERSION', VERSION)
    monkeypatch.setattr(inherited, 'FIELDS', dict(version=metrics.VERSION,
        **metrics.experiment_fields(VERSION)))
    return inherited.prepared.__wrapped__(preparation, monkeypatch)


def development(prepared, monkeypatch, *, timeout=None, later_recovery=True):
    def jobs(patch, contract, acquired, *, timeout=None):
        if later_recovery:
            enabled = acquired[1]
            enabled['runner_result']['outcomes']['required_state_path_passed'] = False
            path = Path(enabled['receipt']['path'])
            path.write_text(json.dumps({key:value for key,value in enabled.items() if key != 'receipt'}))
            enabled['receipt'] = workflow.receipt(path)
        calls = _BASE_FAKE_JOBS(patch, contract, acquired, timeout=timeout)
        original = m4_science_job.finite_science_job
        def run(argv, log_path, receipt_path, **kwargs):
            result = original(argv, log_path, receipt_path, **kwargs)
            if result['complete'] and argv[2] == 'labels':
                path = Path(log_path).parent / 'labels.json'
                data = workflow.read_json(path)
                for row in data['runs']:
                    row['combined_sequence_required_keys'] = list(metrics.arrival_sequence_required_keys(VERSION))
                    row['combined_sequence_diagnostic_keys'] = ['required_state_path_passed']
                path.write_text(json.dumps(data))
            elif result['complete'] and argv[2] == 'summary':
                path = Path(log_path).parent / 'result.json'
                data = workflow.read_json(path)
                data.update(scientific_scope='integrated_arrival_direction_v1',
                            secondary_endpoint='independent_basin_entry_latency')
                path.write_text(json.dumps(data))
            return result
        patch.setattr(m4_science_job, 'finite_science_job', run)
        return calls
    monkeypatch.setattr(inherited, 'fake_jobs', jobs)
    return inherited.development(prepared, monkeypatch, timeout=timeout)


def test_v12_real_preparation_binds_population_policy_and_actual_r10(prepared):
    assert workflow.verify_frozen(prepared)
    assert prepared['version'] == VERSION
    assert prepared['method_version'] == 'recurrent_integrated_arrival_v12'
    assert prepared['development_release_policy'] == POLICY
    assert {row['seed'] for row in prepared['runs']} == {26091131,26091132,26091133,26091134}
    binding = prepared['component_response_prerequisite']
    assert binding['status'] == 'PASS' and binding['decision']['sha256'] == workflow.R10_DECISION_SHA256
    assert binding['archive']['sha256'] == workflow.R10_ARCHIVE_SHA256
    assert len(binding['receipts']) >= 24
    assert not any(Path(ref['path']).suffix == '.db3' or 'timeline' in Path(ref['path']).name
                   for ref in binding['receipts'])
    assert prepared['science']['labels_sec'] == 240. and prepared['execution']['suite_timeout_sec'] == 15800.


def test_censored_secondary_and_later_recovery_release_v12_once(prepared, monkeypatch):
    rows, block, calls = development(prepared, monkeypatch)
    assert [name for name,*_ in calls] == ['labels','references_3','references_4','summary']
    assert rows[1]['runner_result']['outcomes']['required_state_path_passed'] is False
    summary = workflow.read_json(block['result']['path'])
    assert all(row['latency']['right_censored'] for row in summary['runs'])
    assert 'development_latency_feasibility' not in summary
    release = workflow.release_holdouts(prepared, rows, block, 1000.)
    assert release['development_release_policy'] == POLICY
    assert release['development_evidence']['enabled_arrival_slots'] == [2]
    assert release['development_evidence']['continuous_development_slot'] == 4
    assert release['development_evidence']['component_response_prerequisite'] == prepared['component_response_prerequisite']
    assert len(release['holdouts']) == 12
    with pytest.raises(FileExistsError):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('fault', ['old_policy', 'missing_prerequisite', 'forged_prerequisite'])
def test_frozen_v12_policy_and_component_binding_cannot_change(prepared, fault):
    if fault == 'old_policy': prepared['development_release_policy'] = 'usable_four_arm_analysis_v1'
    elif fault == 'missing_prerequisite': prepared.pop('component_response_prerequisite')
    else: prepared['component_response_prerequisite']['status'] = 'FAIL'
    Path(prepared['contract_path']).write_text(json.dumps(prepared))
    with pytest.raises(ValueError): workflow.verify_frozen(prepared)


@pytest.mark.parametrize('fault', ['missing_criterion', 'false_criterion', 'nonboolean_criterion', 'failed_status'])
def test_exact_r10_criteria_are_required_in_addition_to_hashes(monkeypatch, fault):
    original = workflow.read_json
    def read(path):
        data = original(path)
        if Path(path) == workflow.R10_ROOT / 'decision.json':
            data = deepcopy(data)
            if fault == 'missing_criterion': data['criteria'].pop('paired_synthetic_analysis_complete')
            elif fault == 'false_criterion': data['criteria']['paired_synthetic_analysis_complete'] = False
            elif fault == 'nonboolean_criterion': data['criteria']['paired_synthetic_analysis_complete'] = 1
            else: data['status'] = 'FAIL'
        return data
    monkeypatch.setattr(workflow, 'read_json', read)
    with pytest.raises(ValueError, match='eight passing criteria'):
        workflow._v12_component_response_binding()


@pytest.mark.parametrize('selected', ['decision.json', 'execution_empirical.json',
    'prepared_synthetic.json', 'core', 'parameter_origin', 'launch', 'archive'])
def test_changed_selected_r10_receipt_source_or_configuration_is_rejected(monkeypatch, selected):
    # Simulate a changed file at the receipt boundary without modifying retained evidence.
    original = workflow.receipt
    if selected == 'core':
        path = workflow.REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/recurrent_geometry.py'
    elif selected == 'parameter_origin':
        path = Path(workflow.read_json(workflow.R10_ROOT/'prepared_checks.json')['parameter_origin_path'])
    elif selected == 'launch':
        path = workflow.REPOSITORY / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    elif selected == 'archive': path = workflow.R10_ARCHIVE
    else: path = workflow.R10_ROOT / selected
    def changed(value):
        ref = original(value)
        if Path(value).resolve() == path.resolve(): ref['sha256'] = '0' * 64
        return ref
    monkeypatch.setattr(workflow, 'receipt', changed)
    with pytest.raises(ValueError, match='changed'):
        workflow._v12_component_response_binding()


def test_missing_r10_selected_receipt_blocks_without_reading_bags(monkeypatch):
    original = workflow.receipt
    def missing(path):
        if Path(path) == workflow.R10_ROOT/'synthetic/receipt.json':
            raise FileNotFoundError('missing selected prerequisite')
        return original(path)
    monkeypatch.setattr(workflow, 'receipt', missing)
    with pytest.raises(FileNotFoundError, match='missing selected prerequisite'):
        workflow._v12_component_response_binding()


def test_effective_launch_scalar_cannot_diverge_from_component_configuration(prepared):
    changed = deepcopy(prepared)
    argv = changed['runs'][0]['launch_argv']
    argv[:] = [value for value in argv if not value.startswith('convergence_threshold:=')]
    argv.append('convergence_threshold:=0.21')
    with pytest.raises(ValueError, match='selected method configuration differs'):
        workflow._verify_v12_method_configuration(changed, changed['component_response_prerequisite'])


@pytest.mark.parametrize('stage', ['labels', 'references_4', 'summary'])
def test_v12_still_withholds_incomplete_four_arm_science(prepared, monkeypatch, stage):
    rows, block, _ = development(prepared, monkeypatch, timeout=stage)
    with pytest.raises(ValueError, match='usable development analysis'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (Path(prepared['root'])/'preflight/holdout_release.json').exists()


@pytest.mark.parametrize('fault', ['authority', 'missing_reference', 'continuous_evidence', 'enabled_arrival'])
def test_r10_pass_does_not_replace_integrated_release_evidence(prepared, monkeypatch, fault):
    rows, block, _ = development(prepared, monkeypatch)
    def mutate(result):
        if fault == 'authority': result['runs'][1]['scientific_analysis_checks']['selected_authority_complete'] = False
        elif fault == 'missing_reference': result['references'].pop()
        elif fault == 'continuous_evidence': result['runs'][3]['mandatory_stop_evidence']['status'] = 'NO_ACQUISITION_OBSERVED'
        else: result['runs'][1]['combined_sequence_passed'] = False
    changed = inherited.rewrite_result(prepared, block, mutate)
    with pytest.raises(ValueError, match='usable development analysis'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)


def test_late_r10_change_after_development_verification_withholds(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    original_verify, original_receipt = workflow._verify_v10_development_science, workflow.receipt
    def verify(*args):
        evidence = original_verify(*args)
        def changed(path):
            ref = original_receipt(path)
            if Path(path) == workflow.R10_ROOT/'synthetic/receipt.json': ref['sha256'] = '0'*64
            return ref
        monkeypatch.setattr(workflow, 'receipt', changed)
        return evidence
    monkeypatch.setattr(workflow, '_verify_v10_development_science', verify)
    with pytest.raises(ValueError, match='changed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (Path(prepared['root'])/'preflight/holdout_release.json').exists()


def test_failed_v12_finalization_keeps_all_primary_denominators(prepared, monkeypatch):
    rows, _, _ = development(prepared, monkeypatch, timeout='labels')
    rows.extend(acquisition(prepared, slot, status='UNSTARTED', integrity=False) for slot in range(5,17))
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path']); report = Path(final['report']['path']).read_text()
    assert result['slot_status_counts']['UNSTARTED'] == 12
    assert result['development_release']['status'] == 'WITHHELD'
    assert result['primary_outcomes']['confirmation']['planned_run_count'] == 12
    assert result['primary_outcomes']['confirmation']['arrival_counts']['unavailable'] == 12
    assert report.index('Primary outcomes') < report.index('Secondary historical endpoint')
    assert '>=30% reduction' in report and 'R10 component prerequisite: PASS' in report
    assert '12 runs, 144 direction targets' in report and 'Time to arrival' in report


def test_v12_renderer_uses_per_arm_primary_counts_and_keeps_secondary_unavailable(prepared):
    result = metrics.aggregate_pilot(integrated_rows(), experiment_version=VERSION)
    result.update(component_response_prerequisite=prepared['component_response_prerequisite'],
                  git={'branch':'fixture','head':'fixture'})
    report = workflow.render_report(result, prepared)
    assert '| Global arrival | 12/12 observed arrivals |' in report
    assert '| confirmation | A | 3 | 3 / 0 / 0 |' in report
    assert '| confirmation | C | 3 | 3 / 0 / 0 |' in report
    assert 'EVIDENCE_UNAVAILABLE: 0/12 observed endpoints and 0/6 pairs' in report


def test_v12_source_collection_binds_current_plans_r9_r10_and_existing_helpers(prepared, monkeypatch, tmp_path):
    binding = prepared['component_response_prerequisite']
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **kw: b'')
    monkeypatch.setattr(workflow, 'TOOLS', tmp_path)
    monkeypatch.setattr(workflow, '_v10_runtime_binding', lambda: {'files': []})
    monkeypatch.setattr(workflow, '_v12_component_response_binding', lambda: deepcopy(binding))
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kw: {'metadata_files': [], 'entry_points': []})
    monkeypatch.setattr(workflow, 'receipt', lambda path: {'path':str(Path(path)), 'sha256':'fixture'})
    refs = {ref['path'] for ref in workflow.collect_sources(VERSION)}
    expected = {str(workflow.V12_DEVELOPMENT/'m4_v12_source_v1'/name) for name in (
        'validate_source.py','tests_v1.json','save_source_checkpoint.py','prepare_once.py',
        'archive_preparation.py','release_dispatch.py','acquire_once.py')}
    expected.update(ref['path'] for ref in binding['receipts'])
    expected.add(str(workflow.V10_DEVELOPMENT/'r9_motion_readiness_v1/motion_component_C.json'))
    assert expected <= refs
