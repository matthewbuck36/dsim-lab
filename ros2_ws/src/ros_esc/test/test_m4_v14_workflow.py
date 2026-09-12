"""V14 actual cached workflow with authenticated retained fields; no replay.

The module fixture authenticates the real small V13/R22 receipt chain once.
Subsequent tests use that frozen binding and temporary comparison files through
the existing V10 preparation fixture. Raw receipt hashing and all scientific
children/model calls are forbidden. Negative gate fixtures copy small JSON
products; they never mutate historical artifacts or claim new qualification.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
import m4_science_job
import test_m4_v10_workflow as inherited
from test_m4_workflow import acquisition, save, workflow


VERSION = 'm4-pilot-v14'
POLICY = 'retained_development_integrated_arrival_v1'
_RECEIPT = workflow.receipt


def no_raw_hash(path):
    path = Path(path)
    if '/bag/' in str(path) or path.suffix in ('.db3', '.mcap'):
        pytest.fail('retained V14 workflow must not rehash raw bags or bag metadata')
    return _RECEIPT(path)


@pytest.fixture(scope='module')
def preparation(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(workflow, 'receipt', no_raw_hash)
        binding = workflow._v14_retained_development_binding()
        patch.setattr(inherited, 'VERSION', VERSION)
        patch.setattr(workflow, '_v14_retained_development_binding', lambda: deepcopy(binding))
        patch.setattr(workflow, '_runtime_binding', lambda version: workflow._v10_runtime_binding())
        result = inherited.preparation.__wrapped__(tmp_path_factory)
    result['binding'] = binding
    return result


@pytest.fixture
def prepared(preparation, monkeypatch):
    monkeypatch.setattr(inherited, 'VERSION', VERSION)
    monkeypatch.setattr(workflow, 'receipt', no_raw_hash)
    monkeypatch.setattr(workflow, '_v14_retained_development_binding', lambda: deepcopy(preparation['binding']))
    monkeypatch.setattr(workflow, '_runtime_binding', lambda version: workflow._v10_runtime_binding())
    monkeypatch.setattr(m4_science_job, 'finite_science_job', inherited.unavailable)
    return inherited.prepared.__wrapped__(preparation, monkeypatch)


def cached(prepared):
    qualified = workflow.prepare_retained_development(prepared, absolute_deadline=160.)
    rows, block = workflow.load_retained_development(prepared, 1000.)
    return qualified, rows, block


def rewrite(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True))
    return workflow.receipt(path)


def isolated_products(prepared, monkeypatch, *, summary_change=None, motion_change=None):
    """A coherent temporary binding for testing gates, not provenance admission."""
    binding = deepcopy(workflow._load_v14_reuse(prepared))
    folder = Path(prepared['root'])/'preflight/gate_fixture'
    if summary_change is not None:
        value = workflow.read_json(binding['source_summary']['path'])
        summary_change(value)
        binding['source_summary'] = save(folder/'source_summary.json', value)
    if motion_change is not None:
        value = workflow.read_json(binding['selected_motion']['4']['path'])
        motion_change(value)
        binding['selected_motion']['4'] = save(folder/'selected_D.json', value)
    path = prepared['retained_development']['reuse_receipt']['path']
    prepared['retained_development']['reuse_receipt'] = rewrite(path, binding)
    rewrite(prepared['contract_path'], prepared)
    monkeypatch.setattr(workflow, '_v14_retained_development_binding', lambda: deepcopy(binding))


def public_release(prepared, qualified, *, fault=None):
    root = Path(prepared['root'])
    contract = workflow.receipt(prepared['contract_path'])
    pins = {ref['path']: ref['sha256'] for ref in prepared['source_files']}
    validation = save(root/'preflight/source_validation.json', dict(
        returncode=0, source_stable=True, before=pins, after=pins))
    checkpoint = save(root/'preflight/source_checkpoint.json', {'archive_verified': True})
    review = dict(status='PASS', contract=contract, qualification=qualified['receipt'])
    if fault == 'review_failed': review['status'] = 'FAIL'
    elif fault == 'review_wrong_contract': review['contract'] = validation
    elif fault == 'review_wrong_qualification': review['qualification'] = validation
    review_ref = save(root/'preflight/retained_review.json', review)
    release = dict(status='RELEASED', initial_slots=list(range(5,17)), contract=contract,
        prepared=workflow.receipt(root/'preflight/prepared.json'), source_validation=validation,
        source_checkpoint=checkpoint, retained_development_review=review_ref,
        retained_development_qualification=qualified['receipt'])
    if fault == 'old_initial_slots': release['initial_slots'] = [1,2,3,4]
    elif fault == 'missing_review': release.pop('retained_development_review')
    save(root/'preflight/dispatch_release.json', release)
    return release


def test_real_preparation_retains_original_plans_and_copies_topology(prepared, preparation):
    assert workflow.verify_frozen(prepared)
    binding = preparation['binding']
    original = workflow.read_json(binding['source_contract']['path'])
    assert binding['status'] == 'PASS' and binding['source_slots'] == [1,2,3,4]
    assert binding['source_binding']['original_source_count'] == 948
    assert prepared['runs'][:4] == original['runs'][:4]
    assert prepared['runs'][3]['run_id'] == 'm4-pilot-v13-slot04-D-26091141'
    assert prepared['method_version'] == 'recurrent_trapping_integrated_arrival_v14'
    assert prepared['development_release_policy'] == POLICY
    assert {row['seed'] for row in prepared['runs'][4:]} == {26091152,26091153,26091154}
    assert prepared['science']['labels_sec'] == 240. and prepared['execution']['suite_timeout_sec'] == 15800.
    # The inherited fixture also prepares V9: its four synthetic topology calls
    # are the only calls. V14 copies the actual qualified old topology products.
    assert len(preparation['calls']) == 4
    for key, ref in prepared['topology_receipts'].items():
        assert workflow.read_json(ref['path']) == workflow.read_json(original['topology_receipts'][key]['path'])
    assert len(binding['source_acquisitions']) == 4 and set(binding['selected_motion']) == {'3','4'}
    assert binding['inherited_raw_files']
    assert all('/bag/' not in ref['path'] for ref in binding['receipts'])


def test_cached_composition_changes_only_the_declared_four_fields(prepared):
    reuse = workflow._load_v14_reuse(prepared)
    source = workflow.read_json(reuse['source_summary']['path'])
    original = deepcopy(source)
    motion = {int(slot): workflow.read_json(ref['path']) for slot,ref in reuse['selected_motion'].items()}
    effective = workflow._compose_v14_development(source, motion)
    assert source == original and effective['runs'][:2] == original['runs'][:2]
    for before, after in zip(original['runs'][2:], effective['runs'][2:]):
        expected = deepcopy(before)
        expected['mandatory_stop_evidence'] = motion[before['slot']]
        expected['mandatory_stopped_acquisitions'] = 0
        expected['scientific_analysis_checks']['motion_measurement_complete'] = True
        expected['scientific_analysis_complete'] = all(expected['scientific_analysis_checks'].values())
        assert after == expected
    assert original['scientific_analysis_complete'] is False
    assert original['runs'][3]['mandatory_stopped_acquisitions'] is None
    assert effective['scientific_analysis_complete'] is True
    assert effective['scientific_analysis_checks'] == dict(four_arm_analysis_complete=True,
        both_reference_products_complete=True)
    assert effective['references'] == original['references'] and effective['labels'] == original['labels']
    assert all(row['latency']['status'] == 'EVIDENCE_UNAVAILABLE' for row in effective['runs'])


def test_cached_job_and_loader_keep_original_receipts_and_release_once(prepared):
    root = Path(prepared['root'])
    with pytest.raises(FileNotFoundError):
        workflow.load_retained_development(prepared, 1000.)
    qualified, rows, block = cached(prepared)
    assert qualified['status'] == 'QUALIFIED' and qualified['dispatch_released'] is False
    assert qualified['no_new_acquisition'] and qualified['no_scientific_replay']
    assert block['jobs'] == [] and block['acquisition_origin'] == 'retained_v13'
    reuse = workflow._load_v14_reuse(prepared)
    assert [r['receipt'] for r in rows] == reuse['source_acquisitions'] == block['cases']
    assert rows[3]['receipt']['path'].endswith('m4_pilot_v13/acquisition/slot_4.json')
    assert workflow.load_retained_development(prepared, 1000.) == (rows, block)
    assert not (root/'acquisition').exists() and not (root/'runs').exists()
    assert not (root/'preflight/holdout_release.json').exists()
    release = workflow.release_holdouts(prepared, rows, block, 1000.)
    assert release['development'] == reuse['source_acquisitions']
    assert release['development_evidence']['enabled_arrival_slots'] == [2,4]
    assert release['development_evidence']['integrated_D_checks']['status'] == 'PASS'
    assert [r['slot'] for r in release['holdouts']] == list(range(5,17))
    assert rows[0]['behavior_passed'] is False
    with pytest.raises(FileExistsError):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    with pytest.raises(FileExistsError):
        workflow.prepare_retained_development(prepared, absolute_deadline=160.)


@pytest.mark.parametrize('fault', ['receipt_bytes','extra_arrival_change','invented_job'])
def test_loader_rejects_changed_or_coherently_rehashed_cached_composition(prepared, fault):
    _, _, block = cached(prepared)
    result = workflow.read_json(block['result']['path'])
    if fault == 'receipt_bytes':
        Path(block['result']['path']).write_text('{}')
    else:
        if fault == 'extra_arrival_change':
            result['runs'][3]['time_to_arrival_sec'] += 1.
            block['result'] = rewrite(block['result']['path'], result)
        else:
            block['jobs'] = [{'invented': 'new-development-labels'}]
        ref = rewrite(block['receipt']['path'], {k:v for k,v in block.items() if k != 'receipt'})
        qpath = Path(prepared['root'])/'analysis/block_0/cached_qualification.json'
        qualified = workflow.read_json(qpath); qualified['block'] = ref
        rewrite(qpath, qualified)
    with pytest.raises(ValueError):
        workflow.load_retained_development(prepared, 1000.)


@pytest.mark.parametrize('arm', ['B','D'])
def test_missing_either_enabled_arrival_withholds_cached_qualification(prepared, monkeypatch, arm):
    def change(data):
        row = next(r for r in data['runs'] if r['arm'] == arm)
        row.update(arrival_passed=False, combined_sequence_passed=False, time_to_arrival_sec=None)
    isolated_products(prepared, monkeypatch, summary_change=change)
    with pytest.raises(ValueError, match='both B and D'):
        workflow.prepare_retained_development(prepared, absolute_deadline=160.)
    assert not (Path(prepared['root'])/'analysis/block_0/cached_qualification.json').exists()


@pytest.mark.parametrize('fault', ['stopped','unknown_stops','no_acquisition','authority','incomplete_motion'])
def test_stops_unknown_motion_and_missing_authority_do_not_qualify(prepared, monkeypatch, fault):
    def change(motion):
        if fault == 'stopped': motion['mandatory_stopped_acquisitions'] = 1
        elif fault == 'unknown_stops': motion['mandatory_stopped_acquisitions'] = None
        elif fault == 'no_acquisition': motion['status'] = 'NO_ACQUISITION_OBSERVED'
        elif fault == 'authority': motion['authority_complete'] = False
        else: motion['analysis_complete'] = False
    isolated_products(prepared, monkeypatch, motion_change=change)
    with pytest.raises(ValueError, match='incomplete|gates'):
        workflow.prepare_retained_development(prepared, absolute_deadline=160.)


@pytest.mark.parametrize('fault', ['failed_direction','unavailable_target','missing_target','forged_summary'])
def test_direction_failure_or_unavailable_denominator_cannot_release(prepared, monkeypatch, fault):
    def change(data):
        row = data['runs'][3]
        if fault == 'failed_direction':
            for target in row['direction_rows']:
                if target['eligible']: target['actual_error_deg'] = 80.
            row['direction_summary'] = metrics.summarize_direction(row['direction_rows'])
        elif fault == 'unavailable_target': row['direction_rows'][0]['exposure_status'] = 'analysis_unavailable'
        elif fault == 'missing_target': row['direction_rows'].pop()
        else: row['direction_summary']['median_error_deg'] = 0.
    isolated_products(prepared, monkeypatch, summary_change=change)
    with pytest.raises(ValueError, match='direction'):
        workflow.prepare_retained_development(prepared, absolute_deadline=160.)


@pytest.mark.parametrize('fault', ['old_initial_slots','missing_review','review_failed',
    'review_wrong_contract','review_wrong_qualification'])
def test_public_dispatch_requires_reviewed_cached_qualification_and_fresh_initial_slots(prepared, fault):
    qualified, _, _ = cached(prepared)
    public_release(prepared, qualified, fault=fault)
    with pytest.raises((ValueError, KeyError)):
        workflow.verify_dispatch_release(prepared['contract_path'])


def test_public_release_admits_only_fresh_twelve_after_review(prepared):
    qualified, _, _ = cached(prepared)
    release = public_release(prepared, qualified)
    assert workflow.verify_dispatch_release(prepared['contract_path']) == release
    assert release['initial_slots'] == list(range(5,17))


def test_expired_cached_job_never_creates_a_qualification(prepared):
    with pytest.raises(TimeoutError):
        workflow.prepare_retained_development(prepared, absolute_deadline=100.)
    assert not (Path(prepared['root'])/'analysis/block_0').exists()


def test_final_report_separates_retained_four_and_unstarted_twelve_without_raw_hashes(prepared):
    _, rows, block = cached(prepared)
    workflow.release_holdouts(prepared, rows, block, 1000.)
    rows += [acquisition(prepared, slot, status='UNSTARTED', integrity=False) for slot in range(5,17)]
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path'])
    assert [r['status'] for r in result['slots']] == ['COMPLETE']*4+['UNSTARTED']*12
    assert result['slots'][3]['receipt'] == rows[3]['receipt']
    assert result['acquisition_population']['retained_development']['complete_acquisition_count'] == 4
    assert result['acquisition_population']['fresh_confirmation']['complete_acquisition_count'] == 0
    assert result['primary_outcomes']['development']['direction']['counts']['scheduled'] == 48
    assert result['primary_outcomes']['confirmation']['direction']['counts']['scheduled'] == 144
    assert result['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['latency']['observed_pair_count'] == 0
    assert result['combined_method_confirmation']['status'] == 'EVIDENCE_UNAVAILABLE'
    report = Path(final['report']['path']).read_text()
    assert 'four original V13 development recordings' in report
    assert 'complete fresh confirmations: 0/12' in report
    assert 'V13 remains closed incomplete' in report
    assert 'not an isolated detector' in report
