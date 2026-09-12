"""Finite source fixtures for M4 labels, references and complete denominators."""

from copy import deepcopy
import ast
from pathlib import Path
from types import SimpleNamespace as Obj
import json
import math
import time

import numpy as np
import pytest

from ros_esc.plotting_scripts import m4_pilot as m4
from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from ros_esc.plotting_scripts.q1_study import _selected_pose_samples


def stamp(ns):
    return Obj(sec=ns//m4.NS, nanosec=ns % m4.NS)


def geometry():
    return {'method': 'operational_enclosure_v1', 'basins': [{
        'source_id': 'local', 'qualified': True, 'grid_origin_xy': [0., 0.],
        'grid_spacing_m': 1., 'boundary_tolerance_m': 1e-9,
        'positive_cells': [[True]], 'exclusion_cells': [[True]]}]}


def bag_fixture(count=181, step_ns=250_000_000):
    topics = {'odometry': '/odom', 'clock': '/clock', 'algorithm_state': '/state',
              'recording_ready': '/ready'}
    rows = {topic: [] for topic in topics.values()}
    for i in range(count):
        source = 1_000_000_000+i*step_ns
        xy = (-1., -1.) if i < 4 else (.5, .5)
        pose = Obj(header=Obj(stamp=stamp(source), frame_id='odom'),
                   pose=Obj(pose=Obj(position=Obj(x=xy[0], y=xy[1]))))
        state = Obj(stamp=stamp(source), state_valid=True, run_id_valid=True, run_id='m4-fixture',
                    state=1, algorithm_profile='robust_gaussian_v1',
                    state_elapsed_valid=True, state_elapsed_sec=(source-m4.NS)/m4.NS)
        for topic, message, delta in [('/clock', Obj(clock=stamp(source)), 0),
                                       ('/state', state, 1), ('/ready', Obj(data=True), 1),
                                       ('/odom', pose, 2)]:
            rows[topic].append(BagRecord(topic, 'fixture', source+delta, source, None, False,
                                         message, True))
    return BagData(Path('/unused'), {}, {a: {'topic': t, 'alias': a} for a, t in topics.items()},
                   rows, m4.NS, rows['/odom'][-1].bag_timestamp_ns)


def endpoint(latency=10.):
    return {'observed': True, 'independently_eligible': True, 'latency_sec': latency}


def normalized(observations, **kwargs):
    return m4.normalize_direction_targets(observations, {'origin_ns': 0, 'qualified': True,
        'integrity_errors': []}, run_id='m4-C', arm='C', partition='holdout',
        condition='nominal', **kwargs)


def observation(ns, *, angle=0., instantaneous=None, context=1, fallback=False):
    if instantaneous is None:
        instantaneous = angle
    return {'stamp_ns': ns, 'qualified': True, 'readiness_eligible': True,
            'context_id': context, 'objective_id': 'law', 'frame_id': 'odom',
            'blend_allowed': True, 'filter_stamp_ns': ns+20_000_000,
            'world_phase_rad': (2*math.pi*ns/(3*m4.NS)) % math.tau, 'xy': [.5, .5],
            'objective': {'complete': True, 'weights': [1., 1., 0.],
                          'gaussian_fills': [], 'affine_terms': []},
            'method': {'v2_output_world': [math.cos(angle), math.sin(angle)],
                       'aligned_instant_world': [math.cos(instantaneous), math.sin(instantaneous)],
                       'usable_averaging': not fallback, 'fallback_used': fallback}}


def complete_rows():
    runs = []
    for slot in range(1, 17):
        block = (slot-1)//4
        arm = m4.ARMS[(slot-1) % 4]
        run = {'slot': slot, 'block': block, 'arm': arm, 'run_id': f'm4-{slot}',
               'partition': 'development' if block == 0 else 'holdout',
               'condition': 'nominal' if block <= 1 else m4.CONDITIONS[block-1],
               'status': 'COMPLETE', 'integrity_passed': True,
               'latency': endpoint(10. if arm in ('A', 'C') else 6.),
               'wrong_fills': 0, 'wrong_goals': 0, 'combined_sequence_passed': True,
               'mandatory_stopped_acquisitions': 0}
        if arm in ('C', 'D'):
            run['direction_analysis_complete'] = True
            run['direction_rows'] = [{**{k: run[k] for k in ('run_id', 'arm', 'partition', 'condition')},
                'number': n, 'offset_sec': offset, 'exposure_status': 'observed',
                'eligible': True, 'input_qualified': True, 'reference_qualified': True,
                'informative': True, 'usable_output': True, 'usable_averaging': True,
                'actual_error_deg': 10., 'instant_error_deg': 20., 'paired_improvement_deg': 10.}
                for n, offset in enumerate(m4.TARGET_OFFSETS_SEC, 1)]
        runs.append(run)
    return runs


def test_labels_are_frozen_before_search_and_detector_join():
    bag = bag_fixture()
    result = m4.analyze_labels(bag, geometry(), pose_topic='/odom')
    assert len(result['labels']) == 1
    assert result['labels'][0]['start_ns'] == 2*m4.NS
    assert 'common_support_eligible' not in result['labels'][0]
    assert result['spatial_labels_precede_event_join']
    before = result['position_inputs_sha256']
    for record in bag.records_by_topic['/state']:
        record.message.state = 2
    changed = m4.analyze_labels(bag, geometry(), pose_topic='/odom')
    assert changed['position_inputs_sha256'] == before
    assert changed['labels'] == result['labels'] and changed['admission_ns'] is None


def test_decision_publication_sets_latency_and_search_ends_at_source_support():
    result = m4.analyze_labels(bag_fixture(), geometry(), pose_topic='/odom')
    source, decision = 18*m4.NS, 18*m4.NS+250_000_000
    for pose in result['poses']:
        if pose['stamp_ns'] > source:
            pose['qualified'] = False
    joined = m4.join_first_opportunity(result, confirmations=[{'source_ns': source, 'decision_ns': decision}],
                                       intervention_ns=19*m4.NS, intervention_evidence_complete=True)
    assert joined['observed'] and joined['latency_sec'] == 16.25
    assert joined['confirmation_source_ns'] == source


def test_first_short_residence_cannot_be_replaced_by_later_favorable_episode():
    result = m4.analyze_labels(bag_fixture(), geometry(), pose_topic='/odom')
    result['residence_intervals'].insert(0, {'source_id': 'local', 'start_ns': 1500000000,
        'end_ns': 1750000000, 'duration_sec': .25, 'kind': 'positive_basin_residence'})
    joined = m4.join_first_opportunity(result, confirmation_stamps_ns=[18*m4.NS], intervention_evidence_complete=True)
    assert joined['reason'] == 'short_or_censored_first_residence'
    assert joined['later_opportunity_count'] == 1 and joined['latency_sec'] is None


@pytest.mark.parametrize('kind', ['intervention', 'left', 'missing', 'source_guard'])
def test_censoring_and_missing_attribution_never_count_as_observed(kind):
    result = m4.analyze_labels(bag_fixture(), geometry(), pose_topic='/odom')
    kwargs = {'confirmation_stamps_ns': [18*m4.NS], 'intervention_evidence_complete': True}
    if kind == 'intervention':
        kwargs['intervention_ns'] = 10*m4.NS
    elif kind == 'left':
        kwargs['admission_ns'] = 3*m4.NS
    elif kind == 'missing':
        kwargs['confirmation_stamps_ns'] = []
    else:
        result['poses'][30]['qualified'] = False
    joined = m4.join_first_opportunity(result, **kwargs)
    assert not joined['observed'] and joined['status'] == 'EVIDENCE_UNAVAILABLE'


def test_large_source_fixture_preserves_q1_capacity_and_finishes_bounded_label_work():
    started = time.monotonic()
    bag = bag_fixture(21000, 34_000_000)
    with pytest.raises(ValueError, match='capacity'):
        _selected_pose_samples(bag, '/odom', 'odom')
    result = m4.analyze_labels(bag, geometry(), pose_topic='/odom')
    assert len(result['poses']) == 21000 and result['labels'][0]['duration_sec'] > 700.
    encoded = m4.canonical_sha256(result)
    assert len(encoded) == 64
    elapsed = time.monotonic()-started
    print(f'M4_LARGE_LABEL_FIXTURE count=21000 elapsed_sec={elapsed:.6f}')
    assert elapsed < 30.  # Resource-feasibility diagnostic, never a field-performance claim.


def test_fixed_targets_preserve_missing_terminal_and_confidence_failures():
    data = normalized([observation(15*m4.NS, fallback=True), observation(16*m4.NS)],
                      exposure_end_ns=60*m4.NS, terminal_stamp_ns=60*m4.NS)
    assert len(data['targets']) == 24
    assert data['targets'][0]['observation_index'] == 0
    assert data['targets'][1]['exposure_status'] == 'missing_anchor'
    assert all(t['exposure_status'] == 'terminated' for t in data['targets'][2:])
    assert data['targets'][-1]['offset_sec'] == 705


def test_large_normalization_and_serialization_remain_finite_without_model_calls():
    started = time.monotonic()
    rows = [observation(i*34_000_000) for i in range(21000)]
    data = normalized(rows)
    assert len(data['observations']) == 21000 and len(data['targets']) == 24
    assert len(m4.canonical_sha256(data)) == 64
    elapsed = time.monotonic()-started
    print(f'M4_LARGE_DIRECTION_FIXTURE count=21000 elapsed_sec={elapsed:.6f}')
    assert elapsed < 30.


def test_reference_uses_existing_numerical_owner_and_full_objective(monkeypatch):
    from ros_esc.plotting_scripts import v2_direction_reference as numeric
    rows = [observation(i*100_000_000) for i in range(181)]
    rows[150]['objective']['affine_terms'] = [{'anchor': [0., 0.], 'vector': [2., 3.]}]
    data = normalized(rows)
    captures = []
    monkeypatch.setattr(numeric, 'augmented_objective', lambda raw, **kwargs: captures.append(kwargs) or raw)
    monkeypatch.setattr(numeric, 'observed_phase_reference', lambda *args, **kwargs: {
        'qualified': True, 'informative': True, 'world_vector': [1., 0.], 'reason': None})
    result = m4.evaluate_direction_targets(data, raw_owner=lambda x, y, theta: 0., binding={}, sources=[])
    assert captures[0]['affine_terms'] == rows[150]['objective']['affine_terms']
    assert result['rows'][0]['actual_error_deg'] == pytest.approx(0.)
    assert result['summary']['counts']['eligible_informative'] == 1
    data['targets'][0]['observation_index'] = 149
    with pytest.raises(ValueError, match='target population'):
        m4.evaluate_direction_targets(data, raw_owner=lambda *args: pytest.fail('no model before binding'),
                                      binding={}, sources=[])


@pytest.mark.parametrize('boundary', ['publication', 'summary_flags'])
def test_reference_native_scalar_boundary_with_actual_numerical_result(tmp_path, monkeypatch, boundary):
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
    from ros_esc.plotting_scripts import v2_direction_reference as numeric
    from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
    rows = [observation(i*100_000_000) for i in range(181)]
    data = normalized(rows)
    binding = {'joint_position_m': [0., 0., .355], 'rotation_axis': [0., 0., 1.],
               'sensor_transform': [[1., 0., 0., .18], [0., 1., 0., 0.],
                                    [0., 0., 1., .015], [0., 0., 0., 1.]]}
    numerical_owner = numeric.observed_phase_reference
    numerical_results = []
    def reference(*args, **kwargs):
        result = numerical_owner(*args, **kwargs)
        assert result['qualified'] and result['informative'], result
        # Real numerical output exposes nested NumPy scalar publication. Also
        # exercise the same scalar family at flags consumed by strict counters.
        if boundary == 'summary_flags':
            result['qualified'] = np.bool_(result['qualified'])
            result['informative'] = np.bool_(result['informative'])
        numerical_results.append(deepcopy(result))
        return result
    monkeypatch.setattr(numeric, 'observed_phase_reference', reference)
    published = []
    def publish(value):
        published.append(deepcopy(value))
        if boundary == 'publication':
            atomic_exclusive_json(tmp_path/f"target_{value['number']}.json", value)
    result = m4.evaluate_direction_targets(data, raw_owner=lambda x, y, theta: -math.cos(theta),
        binding=binding, sources=[], on_result=publish)
    assert len(numerical_results) == 1
    assert len(result['rows']) == len(published) == 24
    assert result['summary']['counts']['reference_qualified'] == 1
    assert result['summary']['counts']['informative'] == 1
    first = result['rows'][0]
    assert first['reference_qualified'] is first['informative'] is True
    assert first['reference'] == analysis._q1_plain(numerical_results[0])
    assert published == result['rows']
    atomic_exclusive_json(tmp_path/'references.json', result)
    assert json.loads((tmp_path/'references.json').read_text()) == result
    if boundary == 'publication':
        assert len(list(tmp_path.glob('target_*.json'))) == 24
        with pytest.raises(FileExistsError):
            atomic_exclusive_json(tmp_path/'target_1.json', published[0])


def test_availability_retains_failed_output_and_distinct_angle_denominator():
    rows = complete_rows()[2]['direction_rows']
    for row in rows[:6]:
        row.update(actual_error_deg=None, usable_output=False, usable_averaging=False, paired_improvement_deg=None)
    summary = m4.summarize_direction(rows)
    assert summary['counts']['eligible_informative'] == 24
    assert summary['counts']['usable_output'] == 18
    assert summary['averaging_availability'] == .75 and summary['status'] == 'FAIL'


def test_all_six_pairs_and_error_attribution_are_required_for_original_target():
    runs = complete_rows()
    aggregate = m4.aggregate_pilot(runs)
    assert aggregate['latency']['status'] == 'PASS'
    assert aggregate['direction']['status'] == 'PASS' and aggregate['direction_scheduled_total'] == 192
    runs[5]['latency'] = {'observed': False, 'reason': 'short_residence'}
    partial = m4.aggregate_pilot(runs)['latency']
    assert partial['status'] == 'EVIDENCE_UNAVAILABLE' and partial['observed_pair_count'] == 5
    assert partial['observed_endpoint_count'] == 11
    assert partial['descriptive_fraction_reduction'] == pytest.approx(.4)
    runs = complete_rows(); runs[5]['wrong_goals'] = None
    assert m4.aggregate_pilot(runs)['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    runs[5]['wrong_goals'] = 1
    assert m4.aggregate_pilot(runs)['latency']['status'] == 'FAIL'


def test_missing_runs_targets_and_each_combined_condition_remain_visible():
    empty = m4.aggregate_pilot([])
    assert len(empty['slots']) == 16 and empty['direction_scheduled_total'] == 192
    assert empty['direction']['status'] == 'EVIDENCE_UNAVAILABLE'
    runs = complete_rows(); runs[11]['combined_sequence_passed'] = False
    assert m4.aggregate_pilot(runs)['combined_sequence']['status'] == 'FAIL'
    runs[11]['combined_sequence_passed'] = None
    assert m4.aggregate_pilot(runs)['combined_sequence']['status'] == 'EVIDENCE_UNAVAILABLE'
    runs[6]['direction_rows'].pop()
    assert m4.aggregate_pilot(runs)['direction']['status'] == 'EVIDENCE_UNAVAILABLE'
    with pytest.raises(ValueError, match='repeated'):
        m4.aggregate_pilot(runs+[runs[0]])


def test_relative_lag_and_fallback_use_finite_same_context_source_grid():
    rows = [observation(i*100_000_000, angle=.5*math.sin((i*.1-2.)/4.),
                         instantaneous=.5*math.sin(i*.1/4.), fallback=i < 100)
            for i in range(601)]
    result = m4.direction_supplemental(rows)
    assert result['fallback_duration_sec'] == pytest.approx(10.)
    assert result['eligible_source_duration_sec'] == pytest.approx(60.)
    assert result['relative_smoothing_lag_median_sec'] == pytest.approx(2.)
    assert result['publication_delay_median_sec'] == pytest.approx(.02)
    assert result['heading_jitter_window_count'] == 60
    assert m4.direction_supplemental([observation(i*100_000_000) for i in range(301)])[
        'relative_lag_windows'][0]['reason'] == 'insufficient_excitation'
    with pytest.raises(ValueError, match='finite capacity'):
        m4.direction_supplemental([observation(0), observation(10**18)])


def test_geometry_wrapper_preserves_old_contract_check(monkeypatch):
    from ros_esc.plotting_scripts import q1_study
    called = []
    monkeypatch.setattr(q1_study, 'verify_geometry_receipts', lambda *a, **kw: called.append(a) or 'geometry')
    with pytest.raises(ValueError):
        q1_study.verify_q1_geometry({'version': m4.VERSION})
    assert not called


@pytest.mark.parametrize('disturbance', ['duplicates', 'boundaries', 'invalidations'])
def test_search_bisect_preserves_retained_numpy_owner_exactly(disturbance):
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
    path = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_pilot_runtime_v1/analyzer_before_search_bisect.py')
    source = path.read_text()
    function = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef) and n.name == '_v2_search_eligibility')
    namespace = dict(analysis.__dict__)
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
    old = namespace['_v2_search_eligibility']
    bag = bag_fixture(81)
    if disturbance == 'duplicates':
        for topic in ('/clock', '/ready', '/state'):
            bag.records_by_topic[topic].insert(21, bag.records_by_topic[topic][20])
    elif disturbance == 'invalidations':
        bag.records_by_topic['/state'][20].message.state_valid = False
        bag.records_by_topic['/ready'][30].message.data = False
    poses, _ = _selected_pose_samples(bag, '/odom', 'odom')
    if disturbance == 'boundaries':
        for row, delta in zip(poses[:3], [-1, 0, 1]):
            row['bag_timestamp_ns'] = bag.records_by_topic['/clock'][0].bag_timestamp_ns+delta
    assert analysis._v2_search_eligibility(poses, bag) == old(poses, bag)


def test_partial_reference_job_cannot_pass_by_filling_missing_slots_with_placeholders():
    runs = complete_rows()
    runs[6]['direction_analysis_complete'] = False
    assert m4.aggregate_pilot(runs)['direction']['status'] == 'EVIDENCE_UNAVAILABLE'
    runs[6]['direction_analysis_complete'] = True
    runs[6]['direction_rows'][0]['exposure_status'] = 'analysis_unavailable'
    assert m4.aggregate_pilot(runs)['direction']['status'] == 'EVIDENCE_UNAVAILABLE'


def test_missing_intervention_attribution_cannot_mean_no_intervention():
    labels = m4.analyze_labels(bag_fixture(), geometry(), pose_topic='/odom')
    result = m4.join_first_opportunity(labels, confirmation_stamps_ns=[18*m4.NS])
    assert result['reason'] == 'objective_intervention_attribution_unavailable'
    assert not result['observed']



def test_aggregate_exposes_all_fixed_direction_slots_including_missing_rows():
    runs = complete_rows()
    runs[2]['direction_rows'] = runs[2]['direction_rows'][:1]
    result = m4.aggregate_pilot(runs)
    rows = result['direction_rows']
    assert len(rows) == 192
    for slot in (3, 4, 7, 8, 11, 12, 15, 16):
        actual = [row for row in rows if row['slot'] == slot]
        assert [row['number'] for row in actual] == list(range(1, 25))
        assert [row['offset_sec'] for row in actual] == list(m4.TARGET_OFFSETS_SEC)
        assert all(row['run_id'] == f'm4-{slot}' for row in actual)
    assert rows[0]['exposure_status'] == 'observed'
    assert all(row['exposure_status'] == 'analysis_unavailable' for row in rows[1:24])
    runs[3]['direction_rows'][0]['offset_sec'] = 16
    with pytest.raises(ValueError, match='target identity'):
        m4.aggregate_pilot(runs)



def test_missing_supplemental_exposure_cannot_report_zero_fallback_duration():
    for rows in ([], [observation(0)]):
        result = m4.direction_supplemental(rows)
        assert result['status'] == 'EVIDENCE_UNAVAILABLE'
        assert result['observation_count'] == len(rows)
        assert result['fallback_duration_sec'] is None
        assert result['eligible_source_duration_sec'] is None
        assert result['unknown_gap_duration_sec'] is None
    rows = [observation(0), observation(100_000_000)]
    for row in rows:
        row['blend_allowed'] = False
    result = m4.direction_supplemental(rows)
    assert result['eligible_source_duration_sec'] == 0.
    assert result['fallback_duration_sec'] is None
    assert result['unknown_gap_duration_sec'] == 0.
    rows[0]['blend_allowed'] = rows[1]['blend_allowed'] = True
    result = m4.direction_supplemental(rows)
    assert result['fallback_duration_sec'] == 0.
    assert result['status'] == 'OBSERVED'
