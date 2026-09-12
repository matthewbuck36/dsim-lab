"""Fresh V11 workflow through existing preparation, science and release owners.

Child jobs and topology are inherited fixtures. Latency endpoints come from the
unchanged position-label/first-opportunity owner; no retained bag is opened.
"""
import json
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from ros_esc.scenario_runner import run_scenario as runner
import test_m4_v10_workflow as inherited
from test_m4_v11_science import first_opportunity_latency
from test_m4_workflow import acquisition, workflow
import m4_science_job


VERSION = 'm4-pilot-v11'
_BASE_FAKE_JOBS = inherited.fake_jobs


@pytest.fixture(scope='module')
def preparation(tmp_path_factory):
    # Reuse the real preparation fixture with a fresh temporary population.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inherited, 'VERSION', VERSION)
        return inherited.preparation.__wrapped__(tmp_path_factory)


@pytest.fixture
def prepared(preparation, monkeypatch):
    monkeypatch.setattr(inherited, 'VERSION', VERSION)
    monkeypatch.setattr(inherited, 'FIELDS', dict(version=metrics.VERSION,
        **metrics.experiment_fields(VERSION)))
    return inherited.prepared.__wrapped__(preparation, monkeypatch)


def development(prepared, monkeypatch, *, missing_arm=None, timeout=None):
    def jobs(patch, contract, acquired, *, timeout=None):
        calls = _BASE_FAKE_JOBS(patch, contract, acquired, timeout=timeout)
        original = m4_science_job.finite_science_job

        def run(argv, log_path, receipt_path, **kwargs):
            result = original(argv, log_path, receipt_path, **kwargs)
            output = Path(log_path).parent
            if result['complete'] and argv[2] == 'labels':
                path = output / 'labels.json'
                labels = workflow.read_json(path)
                for row in labels['runs']:
                    row['latency'] = first_opportunity_latency(
                        decision_sec=20. if row['arm'] in 'BD' else 18.,
                        fault='no_confirmation' if row['arm'] == missing_arm else None)
                path.write_text(json.dumps(labels))
            elif result['complete'] and argv[2] == 'summary':
                path = output / 'result.json'
                summary = workflow.read_json(path)
                summary['development_latency_feasibility'] = metrics.development_latency_feasibility(
                    summary['runs'], experiment_version=contract['version'])
                path.write_text(json.dumps(summary))
            return result

        patch.setattr(m4_science_job, 'finite_science_job', run)
        return calls

    monkeypatch.setattr(inherited, 'fake_jobs', jobs)
    return inherited.development(prepared, monkeypatch, timeout=timeout)


def test_v11_real_prepare_verify_and_four_jobs_keep_selected_contract(prepared, preparation, monkeypatch):
    assert workflow.verify_frozen(prepared)
    assert prepared['version'] == VERSION and prepared['method_version'] == 'recurrent_arrival_v11'
    assert {row['seed'] for row in prepared['runs']} == {26091021, 26091022, 26091023, 26091024}
    assert prepared['runtime_binding'] == preparation['runtime']
    assert prepared['science']['labels_sec'] == 240.
    assert prepared['science']['freeze_report_sec'] == 40.
    assert prepared['execution']['science_budget_sec'] == 1400.
    assert prepared['execution']['suite_timeout_sec'] == 15800.
    rows, block, calls = development(prepared, monkeypatch)
    assert [name for name, *_ in calls] == ['labels', 'references_3', 'references_4', 'summary']
    assert [cap for _, cap, _ in calls] == [240., 45., 45., 10.]
    assert block['scientific_analysis_complete'] is True
    release = workflow.release_holdouts(prepared, rows, block, 1000.)
    evidence = release['development_evidence']
    feasibility = evidence['development_latency_feasibility']
    assert feasibility['feasible'] is True and feasibility['observed_pair_count'] == 2
    assert all(pair['enabled']['latency_sec'] > pair['control']['latency_sec']
               for pair in feasibility['pairs'])  # No development improvement target.
    assert release['scientific_pass_required'] is False
    assert evidence['enabled_arrival_slots'] == [2]
    assert len(release['holdouts']) == 12 and all(row['behavior_passed'] is False for row in (rows[0], rows[2]))
    assert len(evidence['nested_receipts']) >= 16
    with pytest.raises(FileExistsError):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('missing_arm', ['A', 'B', 'C', 'D'])
def test_complete_censored_science_withholds_v11_confirmation_and_reports_endpoint(prepared, monkeypatch, missing_arm):
    rows, block, _ = development(prepared, monkeypatch, missing_arm=missing_arm)
    summary = workflow.read_json(block['result']['path'])
    assert block['scientific_analysis_complete'] is True
    assert summary['scientific_analysis_complete'] is True
    assert summary['development_latency_feasibility']['observed_pair_count'] == 1
    with pytest.raises(ValueError, match='unobserved independently eligible development pair'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (Path(prepared['root']) / 'preflight/holdout_release.json').exists()
    assert not list((Path(prepared['root']) / 'acquisition').glob('slot_[5-9].json'))
    rows.extend(acquisition(prepared, slot, status='UNSTARTED', integrity=False) for slot in range(5, 17))
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path'])
    report = Path(final['report']['path']).read_text()
    assert len(result['slots']) == 16 and result['slot_status_counts']['UNSTARTED'] == 12
    assert result['analysis_completion']['complete_blocks'] == 1
    assert result['development_latency_feasibility'] == summary['development_latency_feasibility']
    assert result['development_release']['status'] == 'WITHHELD'
    assert summary['development_latency_feasibility']['reason'] in report
    assert 'recurrent_arrival_v11' in report and 'Time to arrival' in report
    assert '1/2 independently eligible observed pairs' in report
    assert '>=30% reduction' in report and 'previously exposed conditions' in report


@pytest.mark.parametrize('fault', ['missing', 'feasible_claim', 'endpoint_copy'])
def test_rehashed_summary_cannot_change_feasibility_from_retained_endpoints(prepared, monkeypatch, fault):
    rows, block, _ = development(prepared, monkeypatch, missing_arm='C')
    def mutate(result):
        if fault == 'missing':
            result.pop('development_latency_feasibility')
        elif fault == 'feasible_claim':
            result['development_latency_feasibility'].update(feasible=True, observed_pair_count=2)
        else:
            result['development_latency_feasibility']['pairs'][1]['control'] = first_opportunity_latency()
    changed = inherited.rewrite_result(prepared, block, mutate)
    with pytest.raises(ValueError, match='feasibility differs from retained first-opportunity endpoints'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)


@pytest.mark.parametrize('stage', ['labels', 'references_3', 'references_4', 'summary'])
def test_v11_failed_finite_science_stage_cannot_use_old_timeout_release(prepared, monkeypatch, stage):
    rows, block, _ = development(prepared, monkeypatch, timeout=stage)
    with pytest.raises(ValueError, match='usable development analysis'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    if stage in ('labels', 'summary'):
        unavailable = workflow.read_json(block['result']['path'])['runs']
        assert all(row['method_version'] == 'recurrent_arrival_v11' for row in unavailable)
        assert all(row['scientific_analysis_complete'] is False for row in unavailable)


def test_v11_rechecks_nested_inputs_after_endpoint_feasibility(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    original = workflow._verify_v10_development_science
    def changed_after(*args):
        result = original(*args)
        path = Path(prepared['root']) / 'analysis/block_0/slot_3_normalized.json'
        path.write_text('changed after full semantic checks')
        return result
    monkeypatch.setattr(workflow, '_verify_v10_development_science', changed_after)
    with pytest.raises(ValueError, match='changed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


def test_v11_source_collection_requires_correction_receipts_and_helpers(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **kw: b'')
    monkeypatch.setattr(workflow, 'TOOLS', tmp_path)
    monkeypatch.setattr(workflow, '_v10_runtime_binding', lambda: {'files': []})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kw: {'metadata_files': [], 'entry_points': []})
    monkeypatch.setattr(workflow, 'receipt', lambda path: {'path': str(Path(path)), 'sha256': 'fixture'})
    old = {row['path'] for row in workflow.collect_sources('m4-pilot-v10')}
    new = {row['path'] for row in workflow.collect_sources(VERSION)}
    expected = {str(workflow.V10_DEVELOPMENT / name) for name in (
        'r5_validation_v1/focused_v1/source_validation.json',
        'r6_validation_v1/focused_v1/source_validation.json',
        'r7_runtime_validation_v1/focused_v1/source_validation.json',
        'r8_pde_evaluator_v1/focused_v1/source_validation.json',
        'visible_integrated_C_03/attempt_result.json',
        'visible_integrated_C_03/analysis_v1/receipt.json',
        'visible_integrated_C_03/direction_reference_v1/receipt.json',
        'r8_pde_evaluator_v1/cached_c03_v1/result.json',
        'm4_v11_source_v1/prepare_once.py', 'm4_v11_source_v1/release_dispatch.py')}
    assert expected <= new and not expected & old and old <= new
    missing = workflow.V10_DEVELOPMENT / 'r8_pde_evaluator_v1/cached_c03_v1/result.json'
    original = Path.is_file
    monkeypatch.setattr(Path, 'is_file', lambda path: False if path == missing else original(path))
    with pytest.raises(ValueError, match='prerequisite source/evidence missing'):
        workflow.collect_sources(VERSION)


@pytest.mark.parametrize('mode,strict', [('observed_tree_v1', True), ('subreaper_v2', True),
                                        ('subreaper_group_v3', False)])
def test_v11_runner_rejects_weaker_process_ownership_before_any_launch(monkeypatch, mode, strict):
    monkeypatch.setattr(runner, 'load_suite', lambda _: {'suite_id': 'm4_pilot_v11'})
    with pytest.raises(ValueError, match='exact explicit ownership mode and strict cleanup'):
        runner.execute_suite('fixture', 'fixture-operator', process_ownership_mode=mode, strict_cleanup=strict)


def test_v11_runner_requires_exact_shared_daemon_before_case_work(monkeypatch, tmp_path):
    suite = dict(suite_id='m4_pilot_v11', schema_version=1, source_path='fixture',
                 execution={'runs_root': str(tmp_path)})
    monkeypatch.setattr(runner, 'load_suite', lambda _: suite)
    monkeypatch.setattr(runner, 'expand_suite', lambda *a, **kw: ([{}], []))
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    calls = []
    class AdmissionStop(Exception):
        pass
    def graph(**kwargs):
        calls.append(kwargs)
        raise AdmissionStop
    monkeypatch.setattr(runner, 'ros_graph_nodes', graph)
    end = runner.time.monotonic() + 10.
    with pytest.raises(AdmissionStop):
        runner.execute_suite('fixture', 'fixture-operator', run_id='m4_v11_fixture', strict_cleanup=True,
            cleanup_deadline=end, process_ownership_mode='subreaper_group_v3')
    assert calls == [dict(strict=True, absolute_deadline=end, require_shared_daemon=True)]


def test_v11_private_pde_bridge_uses_exact_retained_join():
    from test_r8_pde_evaluator_timestamp import fixture, normalize
    from ros_esc.v2_lifecycle import message_payload
    data = fixture()
    data[0]['suite_id'] = 'm4_pilot_v11'
    before = [message_payload(row[1]) for row in data[2]]
    normalized, audit, error = normalize(data)
    assert error is None and audit
    assert normalized[0][1].source_timestamp == 84.927
    assert [message_payload(row[1]) for row in data[2]] == before
