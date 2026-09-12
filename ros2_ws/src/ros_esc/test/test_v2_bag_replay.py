"""Independent input labels, time domains and replay eligibility regressions."""

from pathlib import Path
from types import SimpleNamespace as NS
import json

import numpy as np
import pytest

from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import (
    _v2_common_positive_support,
    _v2_search_eligibility,
    _v2_write_json,
    classify_v2_detector_events,
    label_v2_basin_intervals,
    qualify_v2_cycle_basins,
    qualify_v2_replay_inputs,
)


def _record(message, t, *, source=None, receipt=None):
    stamp = round(t * 1e9)
    return BagRecord('topic', 'test', round((t if receipt is None else receipt) * 1e9),
                     stamp, t if source is None else source, True, message, True)


def _bag(**aliases):
    return BagData(Path('/unused'), {},
                   {name: {'topic': name} for name in aliases}, aliases, 0, None)


def _clock(t):
    return _record(NS(clock=NS(sec=int(t), nanosec=round((t - int(t)) * 1e9))), t)


def _pose(t, x=0.0, frame='odom'):
    return _record(NS(header=NS(frame_id=frame),
                      pose=NS(pose=NS(position=NS(x=x, y=0.0)))), t)


def _inputs(offset=0.0, publication_skew=0.0):
    times = [10.0, 10.1, 10.2]
    transform = NS(translation=NS(x=0.0, y=0.0, z=0.0),
                   rotation=NS(x=0.0, y=0.0, z=0.0, w=1.0))
    return _bag(
        pose=[_pose(t) for t in times],
        timekeeper=[_record(NS(start_time=offset, mode='sim time'), 10.0)],
        clock=[_clock(t) for t in times],
        source_cost=[_record(NS(raw_cost_valid=True, raw_cost=[-1.0]),
                             t + publication_skew, source=t - offset) for t in times],
        raw_cost_legacy=[_record(NS(data=[-1.0]), t, source=t - offset) for t in times],
        encoder=[_record(NS(data=[0.0]), t, source=t - offset) for t in times],
        sensor_transform=[_record(NS(transform_array=[transform]), t,
                                 source=t - offset) for t in times],
    )


def test_relative_source_time_is_reconciled_to_absolute_pose():
    samples, receipt = qualify_v2_replay_inputs(_inputs(offset=9.0))
    assert all(s['qualified'] for s in samples)
    assert receipt['experiment_start_sec'] == 9.0
    assert all(s['source_skews_ns']['source_cost'] == 0 for s in samples)


def test_publication_skew_uses_declared_tolerance_not_exact_timestamp_equality():
    samples, receipt = qualify_v2_replay_inputs(_inputs(publication_skew=0.02))
    assert all(s['qualified'] for s in samples)
    assert receipt['source_streams']['source_cost']['invalid_count'] == 0
    bad, receipt = qualify_v2_replay_inputs(_inputs(publication_skew=-0.02))
    assert not any(s['qualified'] for s in bad)
    assert receipt['source_streams']['source_cost']['invalid_count'] == 3


def test_source_regressions_remain_invalid_instead_of_being_sorted_away():
    bag = _inputs()
    bag.records_by_topic['encoder'].reverse()
    samples, receipt = qualify_v2_replay_inputs(bag)
    assert not any(s['qualified'] for s in samples)
    assert receipt['source_streams']['encoder']['regressions'] == 2


def test_frame_changes_create_an_unknown_boundary():
    bag = _inputs()
    bag.records_by_topic['pose'][1].message.header.frame_id = 'other'
    samples, receipt = qualify_v2_replay_inputs(bag)
    assert samples[0]['qualified']
    assert 'frame_change' in samples[1]['invalid_reasons']
    assert receipt['pose_reasons']['frame_change'] == 2


def _samples(duration=60, x=0.0):
    return [{'stamp_ns': t * 1_000_000_000, 'xy': [x, 0.0],
             'qualified': True, 'search_epoch': '1', 'readiness_eligible': True,
             'bag_timestamp_ns': t * 1_000_000_000, 'frame_id': 'odom'}
            for t in range(duration + 1)]


def _geometry(qualified=True):
    return {'basins': [{'source_id': 'local', 'center_xy': [0.0, 0.0],
                        'region_radius_m': 0.5, 'qualified': qualified}]}


def test_positive_labels_are_residence_with_independent_entry_time():
    samples = _samples(60)
    labels = label_v2_basin_intervals(samples, _geometry())
    assert len(labels) == 1
    assert labels[0]['start_ns'] == 0
    assert labels[0]['duration_sec'] == 60
    assert labels[0]['common_support_eligible']


def test_invalid_interval_splits_residence_without_fabricating_continuity():
    samples = _samples(60)
    samples[30]['qualified'] = False
    labels = label_v2_basin_intervals(samples, _geometry())
    assert len(labels) == 2
    assert all(not label['common_support_eligible'] for label in labels)


def test_uncertified_geometry_produces_no_spatial_truth():
    assert label_v2_basin_intervals(_samples(60), _geometry(False)) == []


def test_directed_progress_is_negative_only_outside_certified_basin():
    samples = _samples(60, x=2.0)
    for i, sample in enumerate(samples):
        sample['xy'][0] += i * 0.03
    labels = label_v2_basin_intervals(samples, _geometry())
    assert labels
    assert all(label['kind'] == 'negative_directed_progress' for label in labels)
    assert labels[0]['start_ns'] == 0


def test_endpoint_outside_samples_do_not_hide_a_segment_crossing_the_basin():
    samples = _samples(13, x=2.0)
    for sample in samples[8:]:
        sample['xy'][0] = -2.0
    assert label_v2_basin_intervals(samples, _geometry()) == []


def test_json_validation_happens_before_exclusive_manifest_creation(tmp_path):
    path = tmp_path / 'manifest.json'
    with pytest.raises(TypeError):
        _v2_write_json(path, {'non_json_scalar': np.int64(1)})
    assert not path.exists()
    _v2_write_json(path, {'count': 1})
    with pytest.raises(FileExistsError):
        _v2_write_json(path, {'count': 2})


def test_common_positive_support_censors_short_intervals_for_every_grid_row():
    # Use source steps below the separately declared 0.5-second gap gate.
    samples = _samples(60)
    for i, sample in enumerate(samples):
        sample['stamp_ns'] = i * 100_000_000
    labels = [{'kind': 'positive_basin_residence', 'source_id': 'local',
               'start_ns': 0, 'end_ns': 6_000_000_000}]
    supported, censored = _v2_common_positive_support(samples, labels)
    assert supported == []
    assert len(censored) == 1
    assert censored[0]['duration_sec'] == 6


def test_one_search_epoch_cannot_require_two_positive_confirmations():
    samples = [{**_samples(0)[0], 'stamp_ns': round(t * 1e9)}
               for t in np.arange(0.0, 150.01, 0.1)]
    labels = [{'kind': 'positive_basin_residence', 'source_id': 'local',
               'start_ns': round(a * 1e9), 'end_ns': round(b * 1e9)}
              for a, b in [(0, 60), (80, 145)]]
    supported, censored = _v2_common_positive_support(samples, labels)
    assert len(supported) == 1
    assert supported[0]['start_ns'] == 0
    assert censored[0]['reason'] == 'later_residence_after_first_opportunity'


def test_short_first_opportunity_censors_epoch_instead_of_selecting_later_long_one():
    samples = [{**_samples(0)[0], 'stamp_ns': round(t * 1e9)}
               for t in np.arange(0.0, 150.01, 0.1)]
    labels = [{'kind': 'positive_basin_residence', 'source_id': 'local',
               'start_ns': round(a * 1e9), 'end_ns': round(b * 1e9)}
              for a, b in [(0, 20), (80, 145)]]
    supported, censored = _v2_common_positive_support(samples, labels)
    assert supported == []
    assert len(censored) == 2
    assert censored[0]['reason'] == 'first_opportunity_short_or_interrupted'


def test_unlabeled_detector_outputs_are_not_claimed_as_true_positives():
    events = [{'stamp_ns': x} for x in (1, 3, 5)]
    labels = [{'kind': 'positive_basin_residence', 'start_ns': 0, 'end_ns': 2},
              {'kind': 'negative_directed_progress', 'start_ns': 4, 'end_ns': 6}]
    assert [e['independent_label'] for e in classify_v2_detector_events(events, labels)] == [
        'positive', 'unknown', 'negative']


def _state(t, value=1, valid=True):
    return _record(NS(run_id='run', run_id_valid=True, state_valid=valid,
                      state=value, algorithm_profile='robust_gaussian_v1'), t)


def test_invalid_state_then_same_search_does_not_rearm_epoch():
    times = [0.1, 0.2, 0.3, 0.4, 0.5]
    bag = _bag(algorithm_state=[_state(0.1), _state(0.2, valid=False),
                               _state(0.3), _state(0.4, value=2), _state(0.5)],
               clock=[_clock(t) for t in times],
               recording_ready=[_record(NS(data=True), t) for t in times])
    samples = [{'stamp_ns': round(t * 1e9), 'bag_timestamp_ns': round(t * 1e9),
                'readiness_eligible': True} for t in times]
    masked = _v2_search_eligibility(samples, bag)
    assert [s['search_epoch'] for s in masked] == ['1', None, '1', None, '2']


def test_readiness_false_disarms_without_rearming_same_search():
    times = [0.1, 0.2, 0.3]
    bag = _bag(algorithm_state=[_state(t) for t in times],
               clock=[_clock(t) for t in times],
               recording_ready=[_record(NS(data=value), t)
                                for t, value in zip(times, [True, False, True])])
    samples = [{'stamp_ns': round(t * 1e9), 'bag_timestamp_ns': round(t * 1e9),
                'readiness_eligible': True} for t in times]
    assert [s['search_epoch'] for s in _v2_search_eligibility(samples, bag)] == ['1', None, '1']


def test_invalid_state_pulse_between_poses_invalidates_history_without_rearming():
    times = [0.1, 0.2, 0.3]
    bag = _bag(algorithm_state=[_state(0.1), _state(0.2, valid=False), _state(0.3)],
               clock=[_clock(t) for t in times],
               recording_ready=[_record(NS(data=True), t) for t in times])
    samples = [{'stamp_ns': round(t * 1e9), 'bag_timestamp_ns': round(t * 1e9),
                'readiness_eligible': True} for t in [0.1, 0.3]]
    masked = _v2_search_eligibility(samples, bag)
    assert [s['search_epoch'] for s in masked] == ['1', '1']
    assert masked[1]['history_generation'] > masked[0]['history_generation']


def test_pose_older_than_search_epoch_is_excluded():
    bag = _bag(algorithm_state=[_state(1.0)], clock=[_clock(1.0)],
               recording_ready=[_record(NS(data=True), 1.0)])
    samples = [{'stamp_ns': 900_000_000, 'bag_timestamp_ns': 1_000_000_000,
                'readiness_eligible': True}]
    assert _v2_search_eligibility(samples, bag)[0]['search_epoch'] is None


def test_prospective_geometry_certifies_a_well_but_rejects_flat_field(monkeypatch, tmp_path):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    path = tmp_path / 'model.json'
    path.write_text('{}')
    monkeypatch.setattr(truth, '_model', lambda *args: (object(), path))
    monkeypatch.setattr(truth, 'evaluate_raw_cost',
                        lambda model, x, y, yaw: (x - 0.1) ** 2 + y ** 2 + 0.01 * np.cos(yaw))
    scenario = {'sources': [{'id': 'local', 'x_m': 0.0, 'y_m': 0.0}],
                'bounds_m': [-2.0, 2.0, -2.0, 2.0]}
    result = qualify_v2_cycle_basins(scenario, model_config_path=path)
    assert result['basins'][0]['qualified']
    assert np.linalg.norm(np.asarray(result['basins'][0]['center_xy']) - [0.1, 0]) < 1e-5
    monkeypatch.setattr(truth, 'evaluate_raw_cost', lambda *args: -1.0)
    result = qualify_v2_cycle_basins(scenario, model_config_path=path)
    assert not result['basins'][0]['qualified']


def test_reader_alias_selection_excludes_outputs_and_preserves_default(monkeypatch):
    from ros_esc.plotting_scripts import bag_reader

    class Reader:
        def __init__(self):
            self.rows = [('ready', NS(data=True), 0),
                         ('pose', NS(timestamp=1.0), 1),
                         ('output', NS(timestamp=1.0), 2)]

        def open(self, *args):
            pass

        def get_all_topics_and_types(self):
            return [NS(name=name, type='test') for name in ('ready', 'pose', 'output')]

        def set_filter(self, selection):
            self.rows = [row for row in self.rows if row[0] in selection.topics]

        def has_next(self):
            return bool(self.rows)

        def read_next(self):
            return self.rows.pop(0)

    monkeypatch.setattr(bag_reader, 'load_yaml', lambda path: {'topics': [
        {'alias': 'recording_ready', 'topic': 'ready'},
        {'alias': 'pose', 'topic': 'pose'},
        {'alias': 'algorithm_events', 'topic': 'output'}]})
    monkeypatch.setattr(bag_reader, 'rosbag2_py', NS(
        SequentialReader=Reader, StorageOptions=lambda **kw: None,
        ConverterOptions=lambda *args: None, StorageFilter=lambda **kw: NS(**kw)))
    monkeypatch.setattr(bag_reader, 'get_message', lambda name: object)
    monkeypatch.setattr(bag_reader, 'deserialize_message', lambda message, cls: message)
    selected = bag_reader.read_run_bag('/unused', aliases=('pose',))
    assert set(selected.records_by_topic) == {'pose', 'ready'}
    assert set(bag_reader.read_run_bag('/unused').records_by_topic) == {'pose', 'ready', 'output'}


def _enclosure(mask, *, exclusion=None):
    mask = np.asarray(mask, dtype=bool)
    return {'method': 'operational_enclosure_v1', 'basins': [{
        'source_id': 'local', 'qualified': True,
        'grid_origin_xy': [0.0, 0.0], 'grid_spacing_m': 1.0,
        'positive_cells': mask.tolist(),
        'exclusion_cells': (mask if exclusion is None else exclusion).tolist(),
        'boundary_tolerance_m': 1e-9,
    }]}


def _timed_samples(times, position):
    return [{**_samples(0)[0], 'stamp_ns': round(t * 1e9),
             'xy': list(position(t))} for t in times]


def test_enclosure_positive_keeps_shared_edges_but_hole_crossing_splits_residence():
    mask = np.ones((3, 3), dtype=bool)
    mask[1, 1] = False
    samples = _timed_samples(np.arange(0.0, 30.01, 0.1),
                             lambda t: (0.5, 1.5) if t < 15 else (2.5, 1.5))
    labels = label_v2_basin_intervals(samples, _enclosure(mask))
    positives = [label for label in labels if label['kind'] == 'positive_basin_residence']
    assert len(positives) == 2
    assert positives[0]['end_ns'] == 14_900_000_000
    assert positives[1]['start_ns'] == 15_000_000_000
    shared = _timed_samples(np.arange(0.0, 15.01, 0.1), lambda t: (1.0, 0.5))
    assert len(label_v2_basin_intervals(shared, _enclosure(mask))) == 1
    boundary = _timed_samples(np.arange(0.0, 15.01, 0.1), lambda t: (1.0, 1.5))
    assert label_v2_basin_intervals(boundary, _enclosure(mask)) == []


def test_m1a_negative_uses_exact_six_seconds_not_an_oversized_sample_window():
    mask = np.ones((2, 2), dtype=bool)
    # 6.3 s * .0195 m/s exceeds .12 m, but exact 6 s does not.
    times = np.arange(0.0, 14.01, 0.45)
    slow = _timed_samples(times, lambda t: (4.0 + 0.0195 * t, 0.5))
    assert label_v2_basin_intervals(slow, _enclosure(mask)) == []
    fast = _timed_samples(times, lambda t: (4.0 + 0.03 * t, 0.5))
    labels = label_v2_basin_intervals(fast, _enclosure(mask))
    assert len(labels) == 1
    assert labels[0]['start_ns'] == 300_000_000
    # Clipping the measurement segment must not mutate frozen coordinates.
    assert fast[0]['xy'] == [4.0, 0.5]


def test_m1a_exclusion_mask_blocks_negative_even_outside_positive_mask():
    positive = np.zeros((5, 5), dtype=bool)
    positive[2, 2] = True
    exclusion = np.ones((5, 5), dtype=bool)
    samples = _timed_samples(np.arange(0.0, 8.01, 0.1), lambda t: (0.3 + 0.04 * t, 0.5))
    assert label_v2_basin_intervals(samples, _enclosure(positive, exclusion=exclusion)) == []


def _m1a_fixture(tmp_path):
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analyzer
    repo = next(parent for parent in Path(__file__).resolve().parents
                if (parent / 'AGENTS.md').is_file())
    contract = json.loads((repo / 'docs/codex/gesc_gaussian/v2/validation/m1a_contract_v1.json').read_text())
    synthetic = tmp_path / 'synthetic.json'
    _v2_write_json(synthetic, [{'trace_id': str(i), 'label': 'positive' if i < 27 else 'negative',
                              'times_ns': [0], 'positions_xy': [[0, 0]]} for i in range(79)])
    model = tmp_path / 'model.json'
    model.write_text('{}')
    rows, runs = [], []
    for seed in contract['development_seeds'] + contract['holdout_seeds']:
        run_dir = tmp_path / str(seed)
        run_dir.mkdir()
        (run_dir / 'resolved_scenario.yaml').write_text(
            'sources: [{id: local, x_m: 0.0, y_m: 0.0}]\nbounds_m: [-2, 2, -2, 2]\n')
        row = {'seed': seed, 'run_id': str(seed), 'run_directory': str(run_dir),
               'partition': ('development_replay' if seed in contract['development_seeds']
                             else 'retrospective_holdout'),
               'bag_files': [], 'artifacts': [],
               'parameter_file_provenance': [{'path': str(model),
                    'recorded_blob_sha256': analyzer._v2_file_hash(model)}]}
        rows.append(row)
        if seed in contract['development_seeds']:
            trace = run_dir / 'trace.json'
            _v2_write_json(trace, {'samples': _timed_samples(
                np.arange(0.0, 13.01, 0.1), lambda t: (0.5, 0.5)), 'qualification': {}})
            runs.append({**row, 'input_trace_path': str(trace),
                         'input_trace_sha256': analyzer._v2_file_hash(trace)})
    inventory = tmp_path / 'inventory.json'
    _v2_write_json(inventory, {'runs': rows})
    prior = tmp_path / 'prior_labels.json'
    prior_value = {'inventory_sha256': analyzer._v2_file_hash(inventory), 'runs': runs,
                   'synthetic_inputs_path': str(synthetic),
                   'synthetic_inputs_sha256': analyzer._v2_file_hash(synthetic)}
    _v2_write_json(prior, prior_value)
    contract.update(inventory_sha256=analyzer._v2_file_hash(inventory),
                    prior_labels_path=str(prior), prior_labels_sha256=analyzer._v2_file_hash(prior),
                    synthetic_inputs_path=str(synthetic),
                    synthetic_inputs_sha256=analyzer._v2_file_hash(synthetic))
    path = tmp_path / 'contract.json'
    _v2_write_json(path, contract)
    return analyzer, inventory, path, contract, prior_value


def test_m1a_contract_rejects_changed_grid_acceptance_and_temporal_boundary(tmp_path):
    analyzer, _, path, contract, _ = _m1a_fixture(tmp_path)
    assert analyzer._v2_m1a_contract(path)['calibration_grid']['epsilon_m'] == [0.24, 0.3, 0.36, 0.48]
    for section, key, value in [('calibration_grid', 'epsilon_m', [0.24]),
                                ('acceptance', 'nonempty_retained_positive_denominator', False),
                                ('temporal', 'negative_start_boundary', 'preceding_sample')]:
        changed = json.loads(json.dumps(contract))
        changed[section][key] = value
        path.write_text(json.dumps(changed))
        with pytest.raises(ValueError):
            analyzer._v2_m1a_contract(path)


@pytest.mark.parametrize('changed', ['synthetic', 'trace', 'partition'])
def test_m1a_rejects_immutable_population_and_trace_drift(tmp_path, changed):
    analyzer, inventory, _, contract, prior = _m1a_fixture(tmp_path)
    values = json.loads(inventory.read_text())
    if changed == 'synthetic':
        Path(contract['synthetic_inputs_path']).write_text('[]')
    elif changed == 'trace':
        Path(prior['runs'][0]['input_trace_path']).write_text('{}')
    else:
        values['runs'][0]['partition'] = 'retrospective_holdout'
    with pytest.raises(ValueError):
        analyzer._v2_verify_m1a_prior(contract, inventory, values)


def test_m1a_freezes_immutable_refs_before_detector_import_and_never_reads_output_bags(tmp_path, monkeypatch):
    import builtins
    analyzer, inventory, path, contract, prior = _m1a_fixture(tmp_path)
    monkeypatch.setattr(analyzer, '_v2_verify_inventory_inputs', lambda row: [])
    monkeypatch.setattr(analyzer, 'read_run_bag', lambda *args, **kw: pytest.fail('label pass reread bag'))
    monkeypatch.setattr(analyzer, '_v2_synthetic_traces', lambda: pytest.fail('synthetics regenerated'))
    def geometries(inventory, verified, contract, output, owners, contract_hash):
        assert (output / 'started.json').is_file()
        assert any('cost_function_objects.py' in owner['path'] for owner in owners)
        assert not (output / 'labels.json').exists()
        row = inventory['runs'][0]
        key = json.dumps([[{'id': 'local', 'x_m': 0.0, 'y_m': 0.0}], [-2, 2, -2, 2],
                          row['parameter_file_provenance'][0]['recorded_blob_sha256'], []], sort_keys=True)
        return {key: _enclosure(np.ones((2, 2), dtype=bool))}
    monkeypatch.setattr(analyzer, '_v2_prepare_m1a_geometries', geometries)
    original_import = builtins.__import__
    def checked_import(name, *args, **kwargs):
        assert 'convergence_detector_node' not in name
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', checked_import)
    output = tmp_path / 'attempt'
    result = analyzer.freeze_v2_replay_labels(inventory, path, output)
    assert (output / 'labels.json').is_file()
    assert result['detector_imported_for_labeling'] is False
    assert result['synthetic_inputs_path'] == contract['synthetic_inputs_path']
    assert [r['input_trace_sha256'] for r in result['runs']] == [r['input_trace_sha256'] for r in prior['runs']]
    assert len(result['runs']) == 8
    assert all(len(r['labels']) == 1 for r in result['runs'])
    assert not list(output.glob('*_inputs.json'))
    with pytest.raises(FileExistsError):
        analyzer.freeze_v2_replay_labels(inventory, path, output)


def test_m1a_interruption_retains_started_receipt_without_publishing_labels(tmp_path, monkeypatch):
    analyzer, inventory, path, _, _ = _m1a_fixture(tmp_path)
    monkeypatch.setattr(analyzer, '_v2_verify_inventory_inputs', lambda row: [])
    def interrupt(*args):
        raise TimeoutError('bounded fixture interruption')
    monkeypatch.setattr(analyzer, '_v2_prepare_m1a_geometries', interrupt)
    output = tmp_path / 'partial'
    with pytest.raises(TimeoutError):
        analyzer.freeze_v2_replay_labels(inventory, path, output)
    assert (output / 'started.json').is_file()
    assert not (output / 'labels.json').exists()


def test_atomic_receipt_failure_never_publishes_partial_json(tmp_path, monkeypatch):
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analyzer
    monkeypatch.setattr(analyzer.os, 'link', lambda *args: (_ for _ in ()).throw(OSError('fixture failure')))
    with pytest.raises(OSError):
        _v2_write_json(tmp_path / 'receipt.json', {'ok': True})
    assert not list(tmp_path.iterdir())


def test_m1a_dispatch_bounds_independent_groups_and_preserves_input_order(tmp_path, monkeypatch):
    import concurrent.futures
    analyzer, inventory_path, _, contract, _ = _m1a_fixture(tmp_path)
    inventory = json.loads(inventory_path.read_text())
    rows = inventory['runs'][:8]
    for i, row in enumerate(rows):
        (Path(row['run_directory']) / 'resolved_scenario.yaml').write_text(
            f'sources: [{{id: local, x_m: {i % 3}, y_m: 0.0}}]\nbounds_m: [-2, 4, -2, 2]\n')
    calls = []
    class FixtureExecutor:
        def __init__(self, **kwargs):
            calls.append(kwargs['max_workers'])
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def map(self, function, tasks):
            calls.append([task['scenario']['sources'][0]['x_m'] for task in tasks])
            return [(task['key'], {'fixture': True}) for task in tasks]
    monkeypatch.setattr(concurrent.futures, 'ProcessPoolExecutor', FixtureExecutor)
    result = analyzer._v2_prepare_m1a_geometries(
        inventory, {row['run_id']: [] for row in rows}, contract, tmp_path, [], 'fixture')
    assert len(result) == 3
    assert calls == [3, [0, 1, 2]]

    assert json.loads((tmp_path / 'geometry_dispatch.json').read_text())['automatic_retry'] is False
    # A fourth geometry is rejected before any executor is constructed.
    (Path(rows[3]['run_directory']) / 'resolved_scenario.yaml').write_text(
        'sources: [{id: local, x_m: 3, y_m: 0.0}]\nbounds_m: [-2, 4, -2, 2]\n')
    with pytest.raises(ValueError, match='population cap'):
        analyzer._v2_prepare_m1a_geometries(
            inventory, {row['run_id']: [] for row in rows}, contract, tmp_path, [], 'fixture')
    assert calls == [3, [0, 1, 2]]


def _retained_pre_recovery_labeler():
    import ast
    import hashlib
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analyzer
    path = Path('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_v1/gesc_gaussian_bag_analysis_before_recovery.py')
    if not path.is_file():
        pytest.skip('retained pre-recovery analyzer snapshot is unavailable')
    source = path.read_text()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == 'c95a509fef294fff89ec61a08fb3b8d022bc653a9e0790f0e12fe69e68c64a09'
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
                and n.name == 'label_v2_basin_intervals')
    namespace = dict(analyzer.__dict__)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['label_v2_basin_intervals']


@pytest.mark.parametrize('case', ['drift', 'threshold_below', 'threshold_above',
                                 'hole_crossing', 'invalid', 'gap', 'clipped_exit'])
def test_cached_labels_equal_retained_pre_recovery_implementation(case):
    old = _retained_pre_recovery_labeler()
    mask = np.ones((3, 3), dtype=bool)
    mask[1, 1] = False
    times = np.arange(0.0, 16.01, 0.4)
    speed = {'threshold_below': 0.02 - 1e-12, 'threshold_above': 0.02 + 1e-12}.get(case, 0.03)
    samples = _timed_samples(times, lambda t: (4.0 + speed * t, 0.5))
    if case == 'hole_crossing':
        samples = _timed_samples(np.arange(0.0, 30.01, 0.3),
                                 lambda t: (0.5, 1.5) if t < 15 else (2.5, 1.5))
    elif case == 'invalid':
        samples[17]['qualified'] = False
    elif case == 'gap':
        del samples[17:20]
    elif case == 'clipped_exit':
        times = [0.0, 0.4] + list(np.arange(0.8, 6.01, 0.4)) + [6.3]
        samples = _timed_samples(times, lambda t: (0.5, 0.5) if t == 0 else (1.5 + .03 * (t - .4), .5))
        mask = np.ones((1, 1), dtype=bool)
    before = json.dumps(samples, sort_keys=True)
    geometry = _enclosure(mask)
    assert label_v2_basin_intervals(samples, geometry) == old(samples, geometry)
    assert json.dumps(samples, sort_keys=True) == before
    if case == 'clipped_exit':
        # The full first segment intersects exclusion, but the clipped piece
        # starts outside it. Its cached failure must not poison this window.
        labels = label_v2_basin_intervals(samples, geometry)
        assert labels[0]['start_ns'] == 300_000_000


def test_negative_membership_queries_are_bounded_by_segments_plus_windows(monkeypatch):
    from ros_esc.plotting_scripts import v2_enclosure
    calls = []
    original = v2_enclosure.segment_outside_exclusion
    def counted(*args):
        calls.append(1)
        return original(*args)
    monkeypatch.setattr(v2_enclosure, 'segment_outside_exclusion', counted)
    samples = _timed_samples(np.arange(0.0, 24.01, 0.17), lambda t: (4.0 + .03 * t, .5))
    label_v2_basin_intervals(samples, _enclosure(np.ones((2, 2), dtype=bool)))
    windows = sum(sample['stamp_ns'] >= 6_000_000_000 for sample in samples)
    assert len(calls) <= len(samples) - 1 + windows


def _recovery_fixture(tmp_path):
    analyzer, inventory_path, contract_path, contract, prior = _m1a_fixture(tmp_path)
    from ros_esc.plotting_scripts import v2_enclosure, bag_reader
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    snapshot = Path('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_v1/gesc_gaussian_bag_analysis_before_recovery.py')
    if not snapshot.is_file():
        pytest.skip('retained recovery snapshot unavailable')
    snapshot_bytes = snapshot.read_bytes()
    snapshot = tmp_path / 'original_analyzer.py'
    snapshot.write_bytes(snapshot_bytes)
    inventory = json.loads(inventory_path.read_text())
    verified = {r['run_id']: [] for r in prior['runs']}
    owner_paths = [analyzer.__file__, v2_enclosure.__file__, bag_reader.__file__,
                   truth.__file__, truth.cost_function_objects.__file__]
    owners = [{'path': str(Path(p).resolve()), 'sha256': analyzer._v2_file_hash(p)} for p in owner_paths]
    old_owners = json.loads(json.dumps(owners))
    old_owners[0]['sha256'] = analyzer._v2_file_hash(snapshot)
    old_output = tmp_path / 'old_attempt'
    old_output.mkdir()
    contract_hash = analyzer._v2_file_hash(contract_path)
    input_fields = ('seed', 'run_id', 'input_trace_path', 'input_trace_sha256', 'bag_files')
    inputs = [{k: run[k] for k in input_fields} for run in prior['runs']]
    _v2_write_json(old_output / 'started.json', {
        'owners': old_owners, 'locked_contract': contract, 'contract_sha256': contract_hash,
        'inventory_sha256': contract['inventory_sha256'], 'immutable_input_traces': inputs,
        'verified_geometry_provenance': verified})
    tasks = analyzer._v2_m1a_geometry_tasks(inventory, verified, contract, old_output, old_owners, contract_hash)
    _v2_write_json(old_output / 'geometry_dispatch.json', {'ordered_tasks': list(tasks.values())})
    for task in tasks.values():
        source = task['scenario']['sources'][0]
        source_dir = Path(task['receipt_directory']) / 'source_1'
        source_dir.mkdir(parents=True)
        point_path = source_dir / 'point_001_001.json'
        _v2_write_json(point_path, {'qualified': True, 'enclosure_identity_sha256': 'fixture',
                                   'canonical_contract_sha256': 'fixture-contract'})
        basin = _enclosure(np.ones((2, 2), dtype=bool))['basins'][0]
        basin.update(reason=None, completed_location_count=1, enclosure_identity_sha256='fixture',
                     canonical_contract_sha256='fixture-contract',
                     point_receipts=[{'path': str(point_path), 'sha256': analyzer._v2_file_hash(point_path)}])
        _v2_write_json(source_dir / 'geometry.json', basin)
        _v2_write_json(source_dir / 'started.json', {
            'source': source, 'sources': task['scenario']['sources'],
            'bounds_m': task['scenario']['bounds_m'], 'provenance': task['provenance'],
            'contract': contract, 'helper_sha256': analyzer._v2_file_hash(v2_enclosure.__file__),
            'enclosure_identity_sha256': 'fixture'})
        _v2_write_json(task['geometry_path'], {'method': 'operational_enclosure_v1',
                      'basins': [basin], 'provenance': task['provenance']})
    manifest = {'version': 'm1a-technical-recovery-v1', 'original_exit_code': 124,
                'original_timeout_sec': 600, 'original_complete_labels': False,
                'contract_sha256': contract_hash, 'inventory_sha256': contract['inventory_sha256'],
                'original_attempt_path': str(old_output), 'original_analyzer_path': owners[0]['path'],
                'original_analyzer_sha256': analyzer._v2_file_hash(snapshot),
                'original_analyzer_snapshot_path': str(snapshot),
                'original_analyzer_snapshot_sha256': analyzer._v2_file_hash(snapshot),
                'old_owners': old_owners, 'input_traces': inputs,
                'receipts': [{'path': str(p), 'sha256': analyzer._v2_file_hash(p)}
                             for p in sorted(old_output.rglob('*.json'))]}
    manifest_path = tmp_path / 'recovery.json'
    _v2_write_json(manifest_path, manifest)
    return analyzer, inventory_path, contract_path, manifest_path, manifest


def test_recovery_reuses_verified_geometry_without_calling_numerical_owner(tmp_path, monkeypatch):
    analyzer, inventory, contract, manifest_path, manifest = _recovery_fixture(tmp_path)
    from ros_esc.plotting_scripts import v2_enclosure
    monkeypatch.setattr(analyzer, '_v2_verify_inventory_inputs', lambda row: [])
    monkeypatch.setattr(analyzer, '_v2_prepare_m1a_geometries', lambda *a: pytest.fail('new geometry dispatch'))
    monkeypatch.setattr(v2_enclosure, 'qualify_enclosure', lambda *a, **kw: pytest.fail('numerical geometry called'))
    result = analyzer.freeze_v2_replay_labels(inventory, contract, tmp_path / 'recovered',
        recovery_manifest_path=manifest_path,
        recovery_manifest_sha256=analyzer._v2_file_hash(manifest_path))
    reuse = result['numerical_geometry_recovery']
    assert reuse['reused_point_count'] == 1
    assert reuse['numerical_evaluations_performed'] == 0
    assert reuse['original_analyzer_sha256'] == manifest['original_analyzer_sha256']
    assert reuse['new_label_owner_sha256'] != reuse['original_analyzer_sha256']
    assert len(result['runs']) == 8
    assert result['runs'][0]['geometry']['provenance']['owners'] == manifest['old_owners']


@pytest.mark.parametrize('drift', ['receipt', 'owner', 'snapshot', 'manifest', 'group_binding'])
def test_recovery_rejects_changed_numerical_evidence_before_labels(tmp_path, monkeypatch, drift):
    analyzer, inventory, contract, manifest_path, manifest = _recovery_fixture(tmp_path)
    monkeypatch.setattr(analyzer, '_v2_verify_inventory_inputs', lambda row: [])
    expected_hash = analyzer._v2_file_hash(manifest_path)
    if drift == 'receipt':
        Path(manifest['receipts'][0]['path']).write_text('{}')
    elif drift == 'manifest':
        manifest_path.write_text('{}')
    else:
        if drift == 'owner':
            manifest['old_owners'][1]['sha256'] = 'changed'
        elif drift == 'snapshot':
            manifest['original_analyzer_snapshot_sha256'] = 'changed'
        elif drift == 'group_binding':
            # Change an input scenario independently of the frozen old task.
            row = json.loads(inventory.read_text())['runs'][0]
            (Path(row['run_directory']) / 'resolved_scenario.yaml').write_text(
                'sources: [{id: local, x_m: 0.2, y_m: 0.0}]\nbounds_m: [-2, 2, -2, 2]\n')
        manifest_path.write_text(json.dumps(manifest))
        expected_hash = analyzer._v2_file_hash(manifest_path)
    output = tmp_path / 'rejected'
    with pytest.raises(ValueError):
        analyzer.freeze_v2_replay_labels(inventory, contract, output,
            recovery_manifest_path=manifest_path, recovery_manifest_sha256=expected_hash)
    assert not (output / 'labels.json').exists()


@pytest.mark.parametrize('drift', ['receipt', 'manifest', 'snapshot'])
def test_calibration_rechecks_recovery_chain_before_detector_import(tmp_path, monkeypatch, drift):
    import builtins
    analyzer, inventory, contract, manifest_path, manifest = _recovery_fixture(tmp_path)
    monkeypatch.setattr(analyzer, '_v2_verify_inventory_inputs', lambda row: [])
    output = tmp_path / 'recovered'
    analyzer.freeze_v2_replay_labels(inventory, contract, output,
        recovery_manifest_path=manifest_path,
        recovery_manifest_sha256=analyzer._v2_file_hash(manifest_path))
    if drift == 'receipt':
        Path(manifest['receipts'][0]['path']).write_text('{}')
    elif drift == 'manifest':
        manifest_path.write_text('{}')
    else:
        Path(manifest['original_analyzer_snapshot_path']).write_text('changed')
    original_import = builtins.__import__
    def no_detector(name, *args, **kwargs):
        assert 'convergence_detector_node' not in name
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', no_detector)
    with pytest.raises(ValueError):
        analyzer.calibrate_v2_detector(output / 'labels.json', tmp_path / 'calibration')
