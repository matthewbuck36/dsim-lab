"""Pure tests for Phase 07 synchronization, metrics, and matrix summaries."""

import json
from types import SimpleNamespace

import pytest

from ros_esc.plotting_scripts.bag_reader import (
    BagRecord,
    build_timestamp_index,
    causal_indexed_record,
    causal_record,
    nearest_indexed_record,
    nearest_record,
)
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import (
    _apply_v4_metric_applicability,
    _candidate_ranking_metric,
    _candidate_rows,
    _escape_attempts,
    _ground_truth_metric,
    _revisit_count,
    _state_intervals,
    _v4_applicability_integrity,
    metric,
    summarize_matrix,
    unavailable,
)
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState


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


def test_prepared_timestamp_index_preserves_lookup_semantics():
    """Prepared indexes must match the original one-shot lookup contract."""
    records = [
        _record(100),
        _record(200, ros_timestamp=None),
        _record(300),
    ]
    index = build_timestamp_index(records, 'ros_timestamp_ns')

    assert index.records == tuple(records)
    assert index.timestamps == (100, 200, 300)
    for target, tolerance in ((50, 100), (220, 90), (400, 50)):
        assert nearest_indexed_record(index, target, tolerance) == (
            nearest_record(
                records, target, tolerance, 'ros_timestamp_ns'
            )
        )
        assert causal_indexed_record(index, target, tolerance) == (
            causal_record(
                records, target, tolerance, 'ros_timestamp_ns'
            )
        )


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


def test_counted_candidate_table_prefers_goal_and_reports_strict_ranking():
    """Expose raw-cost intervals as a table and an analyzer metric."""

    def candidate_event(event_type, ordinal, estimate, lower, upper):
        names = [
            'candidate_raw_cost_estimate',
            'candidate_raw_cost_mad',
            'candidate_raw_cost_uncertainty',
            'candidate_raw_cost_lower',
            'candidate_raw_cost_upper',
            'candidate_rotation_count',
            'candidate_ordinal',
            'filled_candidate_count',
            'known_source_count',
        ]
        values = [
            estimate,
            0.1,
            0.3,
            lower,
            upper,
            2.0,
            float(ordinal),
            float(ordinal - 1),
            2.0,
        ]
        if ordinal == 2:
            names.extend([
                'comparison_filled_raw_cost_lower',
                'candidate_strict_separation_margin',
            ])
            values.extend([-5.3, -5.3 - upper])
        return SimpleNamespace(
            event_type=event_type,
            state=AlgorithmState.STATE_GOAL_HOLD,
            state_name='GOAL_HOLD',
            detail='strictly lower counted candidate',
            value_names=names,
            values=values,
        )

    records = [
        _record(
            1,
            candidate_event(
                AlgorithmEvent.EVENT_STATE_TRANSITION,
                1,
                -5.0,
                -5.3,
                -4.7,
            ),
        ),
        _record(
            2,
            candidate_event(
                AlgorithmEvent.EVENT_STATE_TRANSITION,
                2,
                -10.0,
                -10.3,
                -9.7,
            ),
        ),
        _record(
            3,
            candidate_event(
                AlgorithmEvent.EVENT_GOAL_REACHED,
                2,
                -10.0,
                -10.3,
                -9.7,
            ),
        ),
    ]
    scenario = {
        'algorithm': {
            'launch_overrides': {
                'extremum_classification_mode': 'counted_candidates',
                'known_source_count': 2,
            },
        },
    }

    rows = _candidate_rows(records)
    result = _candidate_ranking_metric(scenario, rows)

    assert len(rows) == 2
    assert rows[0]['candidate_ordinal'] == 1.0
    assert rows[1]['event_name'] == 'EVENT_GOAL_REACHED'
    assert rows[1]['candidate_interval_valid'] is True
    assert rows[1]['candidate_strict_separation_margin'] == pytest.approx(
        4.4
    )
    assert result['status'] == 'valid'
    assert result['value'] is True

    rows[1]['candidate_strict_separation_margin'] = -1.0
    assert _candidate_ranking_metric(scenario, rows)['value'] is False
    assert _candidate_ranking_metric({}, rows)['status'] == 'not_applicable'


def test_legacy_ground_truth_reason_and_missing_contract_are_stable(
    tmp_path,
):
    """Keep schema 1-3 reports byte-compatible with the legacy analyzer."""
    scenario = {
        'schema_version': 3,
        'sources': [{
            'id': 'goal',
            'x_m': 1.0,
            'y_m': 0.0,
        }],
        'success': {
            'ground_truth': {
                'goal_source_ids': ['goal'],
                'final_position_tolerance_m': 0.35,
            },
        },
    }
    (tmp_path / 'resolved_scenario.yaml').write_text(
        json.dumps(scenario),
        encoding='utf-8',
    )
    odometry = [_record(
        1,
        SimpleNamespace(
            pose=SimpleNamespace(
                pose=SimpleNamespace(
                    position=SimpleNamespace(x=0.8, y=0.0),
                ),
            ),
        ),
    )]

    result = _ground_truth_metric(tmp_path, odometry)

    assert result['status'] == 'valid'
    assert result['reason'] == 'nearest goal distance=0.200000 m'
    assert result['provenance'] == (
        'final odometry and Phase 06 ground-truth contract'
    )

    scenario['success']['ground_truth']['goal_source_ids'] = []
    (tmp_path / 'resolved_scenario.yaml').write_text(
        json.dumps(scenario),
        encoding='utf-8',
    )
    missing = _ground_truth_metric(tmp_path, odometry)
    assert missing['status'] == 'unavailable'
    assert missing['reason'] == (
        'ground-truth goal IDs, tolerance, or final pose are unavailable'
    )


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


def test_v4_sensor_only_delay_marks_pose_stream_not_applicable():
    """Require only streams whose exact delay is nonzero."""
    applicability = {
        'escape_attempt': False,
        'escape_duration': False,
        'orbit_count': False,
        'revisit': False,
        'delay': True,
        'saturation': False,
    }
    names = (
        'escape_attempt_count',
        'escape_success_count',
        'escape_failure_count',
        'radial_progress',
        'escape_time',
        'approximate_orbit_count',
        'revisit_count',
        'saturation_time',
        'saturation_fraction',
        'saturation_axis_counts',
        'maximum_limit_excess',
    )
    metrics = {name: metric(0.0) for name in names}
    metrics.update({
        'observed_raw_cost_delay': metric(0.05, unit='s'),
        'observed_source_cost_delay': metric(0.05, unit='s'),
        'observed_pose_delay': unavailable(
            'delay was not enabled',
            unit='s',
        ),
    })
    disturbances = {
        'sensor_delay_sec': 0.05,
        'pose_delay_sec': 0.0,
    }

    applied = _apply_v4_metric_applicability(
        metrics,
        applicability,
        disturbances,
    )
    integrity = _v4_applicability_integrity(
        applied,
        [],
        applicability,
        disturbances,
    )

    assert applied['observed_raw_cost_delay']['status'] == 'valid'
    assert applied['observed_source_cost_delay']['status'] == 'valid'
    assert applied['observed_pose_delay']['status'] == 'not_applicable'
    assert integrity['passed'] is True


def test_escape_attempt_spans_stall_redesign_and_assist():
    """Treat repulse-design-assist as one latched escape attempt."""

    def state_record(timestamp, state, name):
        return _record(
            timestamp,
            SimpleNamespace(
                state_valid=True,
                state=state,
                state_name=name,
                escape_geometry_valid=False,
                radial_progress_valid=False,
                radial_progress=0.0,
                escape_exit_hold_elapsed_valid=False,
                escape_exit_hold_elapsed_sec=0.0,
            ),
        )

    records = [
        state_record(1, AlgorithmState.STATE_SEARCH, 'SEARCH'),
        state_record(
            2,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            'ESCAPE_REPULSE',
        ),
        state_record(
            3,
            AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
            'DESIGN_OR_MERGE_FILL',
        ),
        state_record(
            4,
            AlgorithmState.STATE_ESCAPE_ASSIST,
            'ESCAPE_ASSIST',
        ),
        state_record(8, AlgorithmState.STATE_RECENTER, 'RECENTER'),
    ]

    attempts = _escape_attempts(
        records,
        [],
        [],
        end_ns=10,
        schema_version=4,
    )

    assert len(attempts) == 1
    assert attempts[0]['outcome'] == 'success'
    assert attempts[0]['assisted'] is True
    assert attempts[0]['start_bag_timestamp_ns'] == 2
    assert attempts[0]['end_bag_timestamp_ns'] == 8


def test_escape_attempt_legacy_semantics_remain_schema_gated():
    """Preserve historical attempt boundaries for schema versions 1-3."""

    def state_record(timestamp, state, name):
        return _record(
            timestamp,
            SimpleNamespace(
                state_valid=True,
                state=state,
                state_name=name,
                escape_geometry_valid=False,
                radial_progress_valid=False,
                radial_progress=0.0,
                escape_exit_hold_elapsed_valid=False,
                escape_exit_hold_elapsed_sec=0.0,
            ),
        )

    records = [
        state_record(
            2,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            'ESCAPE_REPULSE',
        ),
        state_record(
            3,
            AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
            'DESIGN_OR_MERGE_FILL',
        ),
        state_record(
            4,
            AlgorithmState.STATE_ESCAPE_ASSIST,
            'ESCAPE_ASSIST',
        ),
        state_record(8, AlgorithmState.STATE_RECENTER, 'RECENTER'),
    ]

    legacy = _escape_attempts(records, [], [], end_ns=10)
    schema_v3 = _escape_attempts(
        records, [], [], end_ns=10, schema_version=3
    )
    schema_v4 = _escape_attempts(
        records, [], [], end_ns=10, schema_version=4
    )

    assert legacy == schema_v3
    assert [item['outcome'] for item in legacy] == [
        'unknown',
        'success',
    ]
    assert len(schema_v4) == 1
    assert schema_v4[0]['outcome'] == 'success'


def test_revisit_count_preserves_earlier_and_superseded_fill_crossings():
    """Count from the first escape against fills active at each timestamp."""

    def fill_record(
        timestamp,
        fill_id,
        revision,
        *,
        active=True,
        superseded=False,
    ):
        return _record(
            timestamp,
            SimpleNamespace(
                cluster_id=1,
                revision=revision,
                fill_id=fill_id,
                active=active,
                superseded=superseded,
                covariance_valid=True,
                exit_radius_valid=True,
                covariance_xx=1.0,
                covariance_xy=0.0,
                covariance_yy=1.0,
                exit_radius=1.0,
                sigma_major=1.0,
                center_x=0.0,
                center_y=0.0,
            ),
        )

    def pose_record(timestamp, x_value):
        return _record(
            timestamp,
            SimpleNamespace(
                pose=SimpleNamespace(
                    pose=SimpleNamespace(
                        position=SimpleNamespace(x=x_value, y=0.0),
                    ),
                ),
            ),
        )

    fills = [
        fill_record(1, 10, 1),
        fill_record(20, 10, 1, active=False, superseded=True),
        fill_record(21, 11, 2),
    ]
    odometry = [
        pose_record(11, 2.0),
        pose_record(12, 0.0),
        pose_record(22, 2.0),
        pose_record(23, 0.0),
    ]
    attempts = [
        {'outcome': 'success', 'end_bag_timestamp_ns': 10},
        {'outcome': 'success', 'end_bag_timestamp_ns': 30},
    ]

    result = _revisit_count(
        odometry,
        fills,
        attempts,
        schema_version=4,
    )

    assert result['status'] == 'valid'
    assert result['value'] == 2
    assert result['provenance'] == (
        'odometry against timestamped active fill exit ellipses'
    )

    legacy = _revisit_count(odometry, fills, attempts)
    schema_v3 = _revisit_count(
        odometry,
        fills,
        attempts,
        schema_version=3,
    )
    assert legacy == schema_v3
    assert legacy['status'] == 'valid'
    assert legacy['value'] == 0
    assert legacy['provenance'] == (
        'odometry against current active fill exit ellipses'
    )


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
