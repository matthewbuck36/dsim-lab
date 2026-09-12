"""Selected simulation publication durations preserve the historical bag clock."""
import csv
import json
from types import SimpleNamespace

import pytest
import yaml

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts.bag_reader import BagRecord
from test_bag_analysis_integration import _create_run


NS = 1_000_000_000
BASIS = 'simulation_publication_v1'


def record(bag_ns, ros_ns, state=1, name='SEARCH', valid=True):
    stamp = SimpleNamespace(sec=ros_ns // NS, nanosec=ros_ns % NS)
    message = SimpleNamespace(stamp=stamp, state_valid=valid, state=state,
                              state_name=name, source_timestamp=999999.)
    return BagRecord('/gesc_gaussian/algorithm_state',
                     'ros_esc_interfaces/msg/AlgorithmState', bag_ns, ros_ns,
                     999999., True, message, True, 0.)


def selected(rows, start=NS, end=20 * NS, rate=20.):
    return analysis._state_intervals(rows, start, end, rate, state_duration_basis=BASIS)


def write(path, document):
    path.write_text(yaml.safe_dump(document), encoding='utf-8')


def captured(tmp_path, *, rate=20., clock=True):
    """Mirror real nested ROS parameter capture, including conflicting type names."""
    write(tmp_path / 'resolved_topics.yaml', {'topics': [{
        'alias': 'algorithm_state', 'topic': '/gesc_gaussian/algorithm_state',
        'type': 'ros_esc_interfaces/msg/AlgorithmState',
        'publishers': ['/gesc_gaussian_supervisor']} ]})
    document = {'nodes': {'/gesc_gaussian_supervisor': {
        'available': True,
        'parameters': {'/gesc_gaussian_supervisor': {'ros__parameters': {
            'use_sim_time': clock, 'supervisor_publish_rate_hz': rate}}},
        'parameter_types': {'supervisor_publish_rate_hz': 'double', 'use_sim_time': 'bool'}}}}
    write(tmp_path / 'resolved_parameters.yaml', document)
    return document


@pytest.mark.parametrize('bags', [
    [NS, NS + 10_000_000, NS + 20_000_000],
    [NS, NS + 156_291_035, NS + 309_947_180],
    [NS, 5 * NS, 9 * NS],
])
def test_receipt_speed_and_bursts_do_not_change_publication_dwell(bags):
    rows = [record(bags[0], 2 * NS), record(bags[1], 2 * NS + 100_000_000),
            record(bags[2], 2 * NS + 200_000_000, 4, 'ESCAPE_REPULSE')]
    intervals, result = selected(rows)
    assert result['status'] == 'valid'
    assert result['value'] == {'SEARCH': .2}
    assert result['support_start_ros_timestamp_ns'] == 2 * NS
    assert result['support_end_ros_timestamp_ns'] == 2 * NS + 200_000_000
    assert result['boundary_extrapolation_used'] is False
    assert [x['start_bag_timestamp_ns'] for x in intervals] == bags[:-1]
    assert [x['duration_sec'] for x in intervals] == [.1, .1]


def test_real_publication_gap_is_invalid_despite_fast_receipts():
    rows = [record(NS, 2 * NS), record(NS + 1, 2 * NS + 200_000_000)]
    intervals, result = selected(rows)
    assert result['status'] == 'invalid'
    assert result['value'] is None
    assert 'exceed three periods (0.150000 s)' in result['reason']
    assert intervals[0]['gap_valid'] is False


def test_quantized_clock_has_zero_dwell_without_extending_source_support():
    rows = [record(NS, 2 * NS), record(2 * NS, 2 * NS),
            record(3 * NS, 2 * NS + 100_000_000)]
    intervals, result = selected(rows)
    assert result['status'] == 'valid'
    assert result['value'] == {'SEARCH': .1}
    assert [x['duration_sec'] for x in intervals] == [0., .1]


def test_conflicting_equal_stamp_state_is_invalid():
    rows = [record(NS, 2 * NS), record(NS + 1, 2 * NS, 4, 'ESCAPE_REPULSE')]
    assert 'conflicting states' in selected(rows)[1]['reason']


@pytest.mark.parametrize('case', ['missing', 'negative', 'nan', 'backward',
                                 'bad_nanoseconds', 'stamp_disagrees', 'invalid_state',
                                 'unknown_state', 'conflicting_state_name'])
def test_invalid_publication_evidence_is_not_silently_filtered(case):
    first = record(NS, 2 * NS)
    second = record(NS + 1, 2 * NS + 100_000_000)
    if case == 'missing':
        second = record(NS + 1, 0)
        second.message.stamp = None
    elif case in ('negative', 'nan'):
        second = BagRecord(second.topic, second.type_name, second.bag_timestamp_ns,
                           -1 if case == 'negative' else float('nan'),
                           second.source_timestamp_sec, True, second.message, True, 0.)
    elif case == 'backward':
        second = record(NS + 1, NS)
    elif case == 'bad_nanoseconds':
        second.message.stamp.nanosec = NS
    elif case == 'stamp_disagrees':
        second.message.stamp.nanosec += 1
    elif case == 'unknown_state':
        second.message.state = 99
    elif case == 'conflicting_state_name':
        second.message.state_name = 'ESCAPE_REPULSE'
    else:
        second.message.state_valid = False
    assert selected([first, second])[1]['status'] == 'invalid'


def test_bag_order_rollback_cannot_be_hidden_by_source_sorting():
    rows = [record(2 * NS, 2 * NS), record(NS, 2 * NS + 100_000_000)]
    assert selected(rows)[1]['status'] == 'invalid'


def test_readiness_membership_and_first_to_last_support_have_no_extrapolation():
    rows = [record(NS - 1, 0, valid=False), record(NS + 10, 2 * NS),
            record(2 * NS - 10, 2 * NS + 100_000_000),
            record(2 * NS + 1, 100 * NS, valid=False)]
    intervals, result = selected(rows, start=NS, end=2 * NS)
    assert result['status'] == 'valid'
    assert result['value'] == {'SEARCH': .1}
    assert len(intervals) == 1
    assert intervals[0]['start_bag_timestamp_ns'] == NS + 10
    assert intervals[0]['end_bag_timestamp_ns'] == 2 * NS - 10
    assert result['readiness_start_bag_timestamp_ns'] == NS
    assert result['readiness_end_bag_timestamp_ns'] == 2 * NS


@pytest.mark.parametrize('start,end', [(None, NS), (NS, None), (-1, NS), (NS, NS)])
def test_unbounded_readiness_is_unavailable(start, end):
    assert selected([record(NS, NS), record(2 * NS, 2 * NS)], start, end)[1]['status'] == 'invalid'


def test_no_positive_source_support_cannot_pass():
    assert selected([record(NS, NS), record(NS + 1, NS)])[1]['status'] == 'invalid'


def test_unknown_basis_cannot_fall_back_to_legacy():
    with pytest.raises(ValueError, match='unknown state duration basis'):
        analysis._state_intervals([], NS, 2 * NS, 20., state_duration_basis='unknown')


def test_legacy_default_retains_bag_durations_and_rows_exactly():
    rows = [record(NS, 50 * NS), record(NS + 50_000_000, 50 * NS)]
    expected = ([
        dict(state=1, state_name='SEARCH', start_bag_timestamp_ns=NS,
             end_bag_timestamp_ns=NS + 50_000_000, duration_sec=.05, gap_valid=True),
        dict(state=1, state_name='SEARCH', start_bag_timestamp_ns=NS + 50_000_000,
             end_bag_timestamp_ns=NS + 100_000_000, duration_sec=.05, gap_valid=True),
    ], analysis.metric({'SEARCH': .1}, unit='s by state',
                       provenance='readiness-clipped algorithm state samples'))
    assert analysis._state_intervals(rows, NS, NS + 100_000_000, 20.) == expected
    assert analysis._state_intervals(rows, NS, NS + 100_000_000, 20.,
                                    state_duration_basis='bag_receipt_v1') == expected
    assert analysis._state_intervals(rows, NS, 3 * NS, 20.)[1]['status'] == 'invalid'


def test_selected_rate_uses_actual_node_parameters_not_types(tmp_path):
    captured(tmp_path)
    rate, origin = analysis._simulation_supervisor_rate(tmp_path, {'mode': 'simulation'})
    assert rate == 20.
    assert origin == 'resolved_parameters.yaml:/gesc_gaussian_supervisor:parameters'


@pytest.mark.parametrize('clock', [False, None, 'True', 1])
def test_missing_or_nonboolean_simulation_clock_rejected(tmp_path, clock):
    captured(tmp_path, clock=clock)
    with pytest.raises(ValueError, match='simulation clock'):
        analysis._simulation_supervisor_rate(tmp_path, {'mode': 'simulation'})


@pytest.mark.parametrize('rate', [None, False, 0., -1., float('nan'), float('inf'), '20'])
def test_missing_or_invalid_selected_rate_rejected(tmp_path, rate):
    captured(tmp_path, rate=rate)
    with pytest.raises(ValueError, match='rate'):
        analysis._simulation_supervisor_rate(tmp_path, {'mode': 'simulation'})


@pytest.mark.parametrize('case', ['physical', 'missing_mode', 'missing_node', 'unavailable',
                                 'missing_publisher', 'multiple_publishers'])
def test_incompatible_or_missing_captured_selection_rejected(tmp_path, case):
    document = captured(tmp_path)
    metadata = {'mode': 'simulation'}
    if case == 'physical':
        metadata['mode'] = 'physical'
    elif case == 'missing_mode':
        metadata = {}
    elif case in ('missing_node', 'unavailable'):
        if case == 'missing_node':
            document['nodes'] = {}
        else:
            document['nodes']['/gesc_gaussian_supervisor']['available'] = False
        write(tmp_path / 'resolved_parameters.yaml', document)
    else:
        topics = yaml.safe_load((tmp_path / 'resolved_topics.yaml').read_text())
        topics['topics'][0]['publishers'] = [] if case == 'missing_publisher' else ['/a', '/b']
        write(tmp_path / 'resolved_topics.yaml', topics)
    with pytest.raises(ValueError):
        analysis._simulation_supervisor_rate(tmp_path, metadata)


def test_actual_analyze_run_forwards_selection_and_writes_both_domains(tmp_path, monkeypatch):
    run = _create_run(tmp_path)
    topics = yaml.safe_load((run / 'resolved_topics.yaml').read_text())
    for topic in topics['topics']:
        if topic['alias'] == 'algorithm_state':
            topic['publishers'] = ['/gesc_gaussian_supervisor']
    write(run / 'resolved_topics.yaml', topics)
    parameters = yaml.safe_load((run / 'resolved_parameters.yaml').read_text())
    node = parameters['nodes']['/gesc_gaussian_supervisor']
    node['available'] = True
    node['parameters']['use_sim_time'] = True
    node['parameter_types'] = {'supervisor_publish_rate_hz': 'double'}
    write(run / 'resolved_parameters.yaml', parameters)
    monkeypatch.setattr(analysis, 'validate_run_directory', lambda *a, **k: {
        'passed': True, 'failures': [], 'warnings': []})
    output = tmp_path / 'selected_analysis'
    result = analysis.analyze_run(run, output, state_duration_basis=BASIS)
    metric = result['metrics']['state_durations']
    assert result['analysis_status'] == 'complete'
    assert result['settings']['state_duration_basis'] == BASIS
    assert result['settings']['supervisor_publish_rate_source'].endswith(':parameters')
    assert metric['state_duration_basis'] == BASIS
    assert metric['boundary_extrapolation_used'] is False
    with (output / 'tables/state_intervals.csv').open() as stream:
        intervals = list(csv.DictReader(stream))
    assert intervals
    assert int(intervals[0]['start_ros_timestamp_ns']) == metric['support_start_ros_timestamp_ns']
    assert int(intervals[-1]['end_ros_timestamp_ns']) == metric['support_end_ros_timestamp_ns']
    assert all(row['state_duration_basis'] == BASIS for row in intervals)
    assert all('start_bag_timestamp_ns' in row for row in intervals)
    completeness = json.loads((output / 'analysis_completeness.json').read_text())
    assert completeness['metric_validity']['state_durations'] == 'valid'
    assert sum(float(row['duration_sec']) for row in intervals) == pytest.approx(
        (metric['support_end_ros_timestamp_ns'] - metric['support_start_ros_timestamp_ns']) / NS)


def test_actual_analyze_run_rejects_physical_opt_in_before_reading(tmp_path, monkeypatch):
    run = _create_run(tmp_path)
    metadata = yaml.safe_load((run / 'metadata.yaml').read_text())
    metadata['mode'] = 'physical'
    write(run / 'metadata.yaml', metadata)
    def forbidden(*args, **kwargs):
        pytest.fail('incompatible clock selection must reject before bag decoding')
    monkeypatch.setattr(analysis, 'read_run_bag', forbidden)
    with pytest.raises(ValueError, match='simulation metadata'):
        analysis.analyze_run(run, tmp_path / 'rejected', state_duration_basis=BASIS)


def test_cli_forwards_only_explicit_selected_basis(monkeypatch, capsys):
    calls = []
    def analyze(*args, **kwargs):
        calls.append(kwargs)
        return {'run_id': 'fixture', 'analysis_status': 'complete'}
    monkeypatch.setattr(analysis, 'analyze_run', analyze)
    assert analysis.main(['fixture']) == 0
    assert 'state_duration_basis' not in calls[-1]
    assert analysis.main(['fixture', '--state-duration-basis', BASIS]) == 0
    assert calls[-1]['state_duration_basis'] == BASIS
    capsys.readouterr()
