"""Existing analyzer adds explicit lifecycle intervals, preserving goal time."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import _v2_lifecycle_analysis
from ros_esc.experiment_recording.v2_lifecycle_validation import TOPICS
from test_v2_lifecycle_recording import centered_fixture, fixture, recurrent_fixture


def inputs(metric='centroid_windows_v2', activated=True):
    data = fixture(metric, activated=activated)
    messages, identity = data[:2]
    bag = SimpleNamespace(
        records_by_topic={topic: [SimpleNamespace(bag_timestamp_ns=t, message=msg)
                                  for t, msg in rows] for topic, rows in messages.items()},
        topics_by_alias={alias: {'topic': topic} for alias, topic in TOPICS.items()})
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
                'scenario_runner': {'v2_identity': {
                    **identity, 'continuous_search_mode': 'rolling_gesc_v2'}}}
    scenario = {'algorithm': {'launch_overrides': {'convergence_metric_mode': metric}}}
    return bag, metadata, scenario, data


@pytest.mark.parametrize('mode', ['centroid_windows_v2', 'pde_mean_v1'])
def test_observed_timing_units_denominators_and_goal_metric_name_remain_separate(mode):
    bag, metadata, scenario, data = inputs(mode)
    summary, metrics, tables = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert summary['status'] == 'valid', summary['errors']
    assert 'convergence_time' not in metrics
    epoch = metrics['v2_median_epoch_to_confirmation_sec']
    assert epoch['value'] == pytest.approx(6.) and epoch['unit'] == 's'
    assert epoch['valid_interval_count'] == epoch['observed_interval_count'] == 1
    assert metrics['v2_unique_fill_commits']['value'] == 1
    assert metrics['v2_median_prepare_to_commit_sec']['value'] >= 0
    assert len(tables['v2_lifecycle_timelines.csv']) == 3
    assert 'no independent basin-entry label' in summary['scope']


def test_no_activation_reports_unavailable_commit_timing_not_zero():
    bag, metadata, scenario, _ = inputs(activated=False)
    summary, metrics, _ = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert summary['status'] == 'valid', summary['errors']
    timing = metrics['v2_median_prepare_to_commit_sec']
    assert timing['status'] == 'unavailable' and timing['value'] is None
    assert timing['valid_interval_count'] == timing['observed_interval_count'] == 0
    assert metrics['v2_unique_fill_commits']['value'] == 0


def test_invalid_evidence_retains_audit_and_withholds_latency_claim():
    bag, metadata, scenario, _ = inputs()
    result = bag.records_by_topic[TOPICS['v2_fill_results']][-1].message
    result.registry_digest_after = '0' * 64
    summary, metrics, tables = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert summary['status'] == 'invalid' and summary['errors']
    assert metrics['v2_median_epoch_to_confirmation_sec']['value'] is None
    assert metrics['v2_median_epoch_to_confirmation_sec']['status'] == 'invalid'
    assert tables['v2_lifecycle_timelines.csv']


def test_legacy_metadata_has_no_v2_tables_or_metrics():
    assert _v2_lifecycle_analysis(None, {}, {}) == (None, {}, {})


def test_analyzer_requires_explicit_centered_mode_and_retains_stage_audit():
    bag, metadata, scenario, _ = inputs(activated=False)
    messages = centered_fixture()[0]
    bag.records_by_topic = {
        topic: [SimpleNamespace(bag_timestamp_ns=t, message=msg) for t, msg in rows]
        for topic, rows in messages.items()}
    historical, metrics, _ = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert historical['status'] == 'invalid'
    assert metrics['v2_median_candidate_to_verification_snapshot_sec']['value'] is None
    scenario['algorithm']['launch_overrides']['v2_verification_motion_mode'] = 'centered_tracking_v1'
    selected, metrics, tables = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert selected['status'] == 'valid', selected['errors']
    assert metrics['v2_median_candidate_to_verification_snapshot_sec']['value'] == pytest.approx(18.)
    assert tables['v2_verification_collection_admissions.csv'] == [{
        'candidate_id': 1, 'search_epoch': 1, 'collection_admitted_at_ns': 13_020_000_000}]


def test_run_validator_resolves_centered_deadline_from_actual_target_metadata(monkeypatch, tmp_path):
    """Exercise the real report boundary with wire records, without a bag process."""
    import yaml
    from ros_esc.experiment_recording import validate_run as validator
    data = centered_fixture()
    messages, identity = data[:2]
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
        'run_id': identity['run_id'], 'target_argv': [
            'continuous_search_mode:=rolling_gesc_v2', 'convergence_metric_mode:=centroid_windows_v2'],
        'scenario_runner': {'v2_identity': {
            **identity, 'continuous_search_mode': 'rolling_gesc_v2'}}}
    resolved = {'schema_version': 1, 'validation': {}, 'topics': [
        {'alias': alias, 'topic': topic, 'type': 'ros_esc_interfaces/msg/AlgorithmEvent', 'required': False}
        for alias, topic in TOPICS.items()]}
    (tmp_path/'resolved_topics.yaml').write_text(yaml.safe_dump(resolved))
    (tmp_path/'resolved_parameters.yaml').write_text(yaml.safe_dump({'failures': []}))
    (tmp_path/'notes.md').write_text('synthetic lifecycle report boundary\n')
    (tmp_path/'console.log').write_text('')
    monkeypatch.setattr(validator, '_read_bag', lambda *args: ({}, messages))
    def report():
        (tmp_path/'metadata.yaml').write_text(yaml.safe_dump(metadata))
        return validator.validate_run_directory(tmp_path, write_report=False)
    historical = report()
    assert not historical['checks']['v2_lifecycle_contract']['passed']
    metadata['target_argv'].append('v2_verification_motion_mode:=centered_tracking_v1')
    selected = report()
    assert selected['checks']['v2_lifecycle_contract']['passed'], selected['v2_lifecycle_metrics']
    assert selected['v2_lifecycle_metrics']['moving_verification_mode'] == 'centered_tracking_v1'


def test_analyzer_uses_separate_recurrent_typed_confirmation_support():
    bag, metadata, scenario, _ = inputs(activated=False)
    messages = recurrent_fixture()[0]
    bag.records_by_topic = {
        topic: [SimpleNamespace(bag_timestamp_ns=t, message=msg) for t, msg in rows]
        for topic, rows in messages.items()}
    scenario['algorithm']['launch_overrides']['convergence_metric_mode'] = 'recurrent_geometry_v3'
    summary, metrics, _ = _v2_lifecycle_analysis(bag, metadata, scenario)
    assert summary['status'] == 'valid', summary['errors']
    assert metrics['v2_median_epoch_to_confirmation_sec']['value'] == pytest.approx(30.)
    assert metrics['v2_median_candidate_to_verification_snapshot_sec']['value'] is None
