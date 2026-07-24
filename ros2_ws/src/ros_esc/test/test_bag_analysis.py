"""Pure tests for Phase 07 synchronization, metrics, and matrix summaries."""

import json

import pytest

from ros_esc.plotting_scripts.bag_reader import (
    BagRecord,
    causal_record,
    nearest_record,
)
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import (
    _state_intervals,
    metric,
    summarize_matrix,
    unavailable,
)


class _State:
    def __init__(self, name='SEARCH', value=1, valid=True):
        self.state_name = name
        self.state = value
        self.state_valid = valid


def _record(timestamp, message=None, ros_timestamp=None):
    return BagRecord(
        topic='/test',
        type_name='test/msg/Test',
        bag_timestamp_ns=timestamp,
        ros_timestamp_ns=(
            timestamp if ros_timestamp is None else ros_timestamp
        ),
        source_timestamp_sec=timestamp / 1e9,
        source_timestamp_valid=True,
        message=message or object(),
        in_readiness_interval=True,
        t_motion_sec=timestamp / 1e9,
    )


def test_nearest_match_is_bounded_and_does_not_interpolate():
    """Nearest matching must reject rather than interpolate distant data."""
    records = [_record(100), _record(300)]

    selected, skew = nearest_record(
        records, 220, 90, 'ros_timestamp_ns'
    )
    missing, missing_skew = nearest_record(
        records, 220, 70, 'ros_timestamp_ns'
    )

    assert selected.bag_timestamp_ns == 300
    assert skew == 80
    assert missing is None
    assert missing_skew is None


def test_causal_match_never_uses_a_future_state():
    """Causal state matching must never select a future state sample."""
    records = [_record(100), _record(300)]

    selected, skew = causal_record(
        records, 250, 200, 'ros_timestamp_ns'
    )

    assert selected.bag_timestamp_ns == 100
    assert skew == -150


def test_metric_statuses_do_not_fabricate_missing_values():
    """Unavailable behavior must carry no fabricated numeric value."""
    valid = metric(2.0, unit='m', provenance='/odom')
    missing = unavailable(
        'no fill occurred', status='not_applicable', provenance='fills'
    )

    assert valid['status'] == 'valid'
    assert missing['value'] is None
    assert missing['status'] == 'not_applicable'
    assert missing['reason'] == 'no fill occurred'


def test_state_duration_marks_excessive_sampling_gap_invalid():
    """State dwell becomes invalid when sampling gaps exceed the contract."""
    records = [
        _record(1_000_000_000, _State()),
        _record(1_050_000_000, _State()),
        _record(2_000_000_000, _State('ESCAPE_REPULSE', 4)),
    ]

    intervals, result = _state_intervals(
        records,
        1_000_000_000,
        2_100_000_000,
        rate_hz=20.0,
    )

    assert intervals
    assert result['status'] == 'invalid'
    assert 'exceed three periods' in result['reason']


def _summary(run_id, status, success, escape_time):
    return {
        'run_id': run_id,
        'analysis_status': status,
        'metrics': {
            'controller_success': metric(success, unit='boolean'),
            'escape_time': metric(escape_time, unit='s'),
        },
    }


def test_matrix_summary_aggregates_complete_and_failed_runs(tmp_path):
    """Matrix aggregation must retain complete and failed-run evidence."""
    analyses = tmp_path / 'analyses'
    first = analyses / 'first'
    second = analyses / 'second'
    first.mkdir(parents=True)
    second.mkdir()
    (first / 'summary_metrics.json').write_text(
        json.dumps(_summary('first', 'complete', True, 4.0)),
        encoding='utf-8',
    )
    (second / 'summary_metrics.json').write_text(
        json.dumps(_summary('second', 'partial', False, 8.0)),
        encoding='utf-8',
    )
    output = tmp_path / 'matrix'

    result = summarize_matrix([analyses], output)

    assert result['run_count'] == 2
    assert result['analysis_status_counts'] == {
        'complete': 1,
        'partial': 1,
    }
    assert result['controller_success_rate'] == pytest.approx(0.5)
    assert result['median_escape_time_sec'] == pytest.approx(6.0)
    assert (output / 'matrix_summary.csv').is_file()
    assert (output / 'matrix_summary.json').is_file()


def test_matrix_summary_refuses_to_overwrite(tmp_path):
    """Matrix aggregation must not overwrite a prior result directory."""
    analysis = tmp_path / 'analysis'
    analysis.mkdir()
    (analysis / 'summary_metrics.json').write_text(
        json.dumps(_summary('run', 'complete', True, 1.0)),
        encoding='utf-8',
    )
    output = tmp_path / 'matrix'
    output.mkdir()

    with pytest.raises(FileExistsError):
        summarize_matrix([analysis], output)
