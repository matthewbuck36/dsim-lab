"""Q1 immutable population/reference orchestration with analytic inputs only."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import pytest
import yaml

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import v2_direction_reference as numeric
from ros_esc.scenario_runner import aggregate_field_truth as truth
from test_q1_direction_inputs import typed_fixture, bag_from_messages, normalize
from test_v2_direction_reference import _binding


REFERENCE = {'target_offsets_sec': list(range(10, 121, 10)), 'anchor_window_sec': .05,
             'minimum_confirmation_informative_anchors_per_run': 6,
             'maximum_median_error_deg': 30, 'maximum_p90_error_deg': 60,
             'minimum_usable_averaging_availability': .8,
             'output_magnitude_floor': 1e-6, 'job_timeout_sec': 300}


def receipt(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def write_json(path, content):
    path.write_text(json.dumps(content, sort_keys=True, allow_nan=False))
    return receipt(path)


@pytest.fixture
def study(tmp_path, monkeypatch):
    from ros_esc import v2_lifecycle, v2_stream
    from ros_esc.experiment_recording import validate_run, record_run
    from ros_esc.plotting_scripts import bag_reader
    source_modules = (analysis, numeric, bag_reader, v2_lifecycle, v2_stream, validate_run,
                      record_run, truth, truth.cost_function_objects)
    sources = [receipt(Path(module.__file__)) for module in source_modules]
    geometry = tmp_path / 'retained_geometry.json'
    geometry.write_text('{"synthetic_receipt_only":true}')
    contract = {'version': analysis.Q1_VERSION, 'reference': REFERENCE,
                'source_files': sources, 'geometry_receipts': [receipt(geometry)]}
    contract_ref = write_json(tmp_path / 'contract.json', contract)
    binding = {'binding': _binding(), 'settings': {}, 'selected_configurations': {
        'cost_function_config_filepath': receipt(geometry)}}
    monkeypatch.setattr(analysis, 'q1_recorded_binding', lambda *a, **k: deepcopy(binding))
    fixture = typed_fixture()
    messages, metadata = fixture[:2]
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    runs = []
    for partition, seeds in analysis.Q1_PARTITION_SEEDS.items():
        for index, seed in enumerate(seeds):
            directory = tmp_path / str(seed)
            (directory / 'bag').mkdir(parents=True)
            files = []
            for name, value in (
                ('metadata.yaml', metadata),
                ('resolved_scenario.yaml', {'sources': []}),
                ('resolved_parameters.yaml', {'nodes': {}}),
                ('resolved_topics.yaml', {'topics': [
                    {'topic': config[key], 'alias': key} for key in (
                        'raw_cost_topic', 'augmented_cost_topic', 'provenance_topic',
                        'objective_cost_topic', 'pose_topic', 'encoder_topic', 'timekeeper_topic')]}),
                ('bag/metadata.yaml', {'synthetic': True}),
            ):
                path = directory / name
                path.write_text(yaml.safe_dump(value))
                files.append(receipt(path))
            database = directory / 'bag/data.db3'
            database.write_bytes(b'synthetic fixture; never opened as a bag')
            files.append(receipt(database))
            runs.append({'run_id': 'run_' + str(seed), 'seed': seed, 'partition': partition,
                         'exposure': 'residence' if index == 0 else 'approach',
                         'run_directory': str(directory), 'input_files': files,
                         'binding': deepcopy(binding), 'model_configuration': receipt(geometry)})
    manifest = {'version': analysis.Q1_VERSION, 'contract': contract_ref, 'runs': runs}
    manifest_path = tmp_path / 'study.json'
    write_json(manifest_path, manifest)
    reads = []
    def read(directory, **kwargs):
        reads.append(str(directory))
        return bag_from_messages(messages)
    monkeypatch.setattr(analysis, 'read_run_bag', read)
    # Fixture run identities are set by the typed normalizer's caller; preserve
    # the actual normalizer for the separate wire tests, no bag/model here.
    normalized, qualification = normalize(fixture)
    def prepare(bag, metadata, *, contract, run_spec):
        q = dict(qualification, run_id=run_spec['run_id'])
        return deepcopy(normalized), q
    monkeypatch.setattr(analysis, 'prepare_q1_direction_inputs', prepare)
    nomination = write_json(tmp_path / 'nomination.json', {
        'status': 'PASS', 'partition': 'discovery', 'contract_sha256': contract_ref['sha256'],
        'parameters': {'window_seconds': 6, 'epsilon_m': .30, 'radius_m': .5, 'candidate_epsilon_m': .10}})
    return {'directory': tmp_path, 'path': manifest_path, 'manifest': manifest,
            'contract': contract, 'nomination': nomination, 'reads': reads,
            'normalized': normalized, 'qualification': qualification}


def freeze(study, partition):
    output = study['directory'] / ('frozen_' + partition)
    kwargs = {'nomination_manifest': study['nomination']} if partition == 'confirmation' else {}
    result = analysis.freeze_q1_direction_targets(study['path'], output, partition=partition, **kwargs)
    return output / 'targets.json', result


def test_freeze_keeps_fixed_twelve_empty_slots_without_model_or_filter(study, monkeypatch):
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('no field before target freeze'))
    monkeypatch.setattr(numeric, 'replay_matched_direction', lambda *a, **k: pytest.fail('no callback replay'))
    _, result = freeze(study, 'discovery')
    assert len(result['targets']) == 24
    assert all(item['observation_index'] is None for item in result['targets'])
    first = result['targets'][:12]
    assert [item['target_ns'] for item in first] == [10_250_000_000+k*10_000_000_000 for k in range(1, 13)]
    assert all('26090913' not in path and '26090914' not in path for path in study['reads'])


def test_post_readiness_first_publication_cannot_fill_target(study, monkeypatch):
    first = deepcopy(study['normalized'][0])
    after = deepcopy(first)
    after.update(stamp_ns=first['stamp_ns']+10_000_000_000, source_sequence=2,
                 observation_id=2, readiness_eligible=False)
    monkeypatch.setattr(analysis, 'prepare_q1_direction_inputs',
                        lambda *a, **k: ([first, after], study['qualification']))
    _, result = freeze(study, 'discovery')
    assert result['targets'][0]['target_ns'] == after['stamp_ns']
    assert result['targets'][0]['observation_index'] is None


@pytest.mark.parametrize('fault', ['missing', 'failed', 'hash', 'contract', 'parameters'])
def test_confirmation_is_unread_before_passing_immutable_nomination(study, fault):
    nomination = deepcopy(study['nomination'])
    if fault == 'missing':
        nomination = None
    elif fault == 'hash':
        nomination['sha256'] = 'wrong'
    else:
        path = Path(nomination['path'])
        data = json.loads(path.read_text())
        if fault == 'failed':
            data['status'] = 'FAIL'
        elif fault == 'contract':
            data['contract_sha256'] = 'wrong'
        else:
            data['parameters']['radius_m'] = 1.
        nomination = write_json(path, data)
    with pytest.raises(ValueError):
        analysis.freeze_q1_direction_targets(study['path'], study['directory'] / 'bad',
                                             partition='confirmation', nomination_manifest=nomination)
    assert study['reads'] == []


def test_target_attempt_cannot_overwrite_previous_freeze(study):
    freeze(study, 'discovery')
    with pytest.raises(FileExistsError):
        freeze(study, 'discovery')


@pytest.mark.parametrize('fault', ['bag', 'geometry', 'owner', 'contract_value', 'missing_input'])
def test_frozen_provenance_is_checked_before_reading_any_bag(study, fault):
    if fault == 'bag':
        Path(study['manifest']['runs'][0]['input_files'][-1]['path']).write_bytes(b'changed')
    elif fault == 'geometry':
        Path(study['contract']['geometry_receipts'][0]['path']).write_text('changed')
    elif fault in ('owner', 'contract_value'):
        contract = deepcopy(study['contract'])
        if fault == 'owner':
            contract['source_files'][0]['sha256'] = 'wrong'
        else:
            contract['reference'] = dict(REFERENCE, anchor_window_sec=.1)
        study['manifest']['contract'] = write_json(Path(study['manifest']['contract']['path']), contract)
        write_json(study['path'], study['manifest'])
    else:
        study['manifest']['runs'][0]['input_files'].pop(0)
        write_json(study['path'], study['manifest'])
    with pytest.raises(ValueError):
        freeze(study, 'discovery')
    assert study['reads'] == []


def test_empty_reference_population_retains48_unavailable_and_never_calls_model(study, monkeypatch):
    paths = [freeze(study, partition)[0] for partition in analysis.Q1_PARTITION_SEEDS]
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('empty anchors cannot probe a field'))
    result = analysis.evaluate_q1_direction_references(
        paths, study['directory'] / 'reference', contract_path=study['manifest']['contract']['path'])
    assert result['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['all']['fixed_anchor_count'] == 48
    assert result['confirmation']['averaging_availability'] is None
    assert result['confirmation']['v2_median_error_deg'] is None
    assert len(list((study['directory'] / 'reference').glob('anchor_*.json'))) == 48


def test_changed_frozen_trace_is_rejected_before_any_reference(study, monkeypatch):
    discovery, frozen = freeze(study, 'discovery')
    confirmation, _ = freeze(study, 'confirmation')
    Path(frozen['input_traces'][0]['path']).write_text('{}')
    monkeypatch.setattr(truth, '_model', lambda *a, **k: pytest.fail('changed inputs must not reach model'))
    with pytest.raises(ValueError, match='frozen file'):
        analysis.evaluate_q1_direction_references(
            [discovery, confirmation], study['directory'] / 'reference',
            contract_path=study['manifest']['contract']['path'])


@pytest.mark.parametrize('change', [None, 'seed', 'start', 'control'])
def test_retained_run_is_bound_to_reserved_scenario_and_exact_control_argv(study, change):
    run = study['manifest']['runs'][0]
    directory = Path(run['run_directory'])
    metadata_path = directory / 'metadata.yaml'
    metadata = yaml.safe_load(metadata_path.read_text())
    metadata['target_argv'] = ['ros2', 'launch', 'fixture_package', 'fixture.launch.xml']
    metadata_path.write_text(yaml.safe_dump(metadata))
    run['input_files'] = [receipt(Path(item['path'])) for item in run['input_files']]
    planned = {key: run[key] for key in ('run_id', 'seed', 'partition', 'exposure')}
    planned.update(resolved_scenario=yaml.safe_load((directory / 'resolved_scenario.yaml').read_text()),
                   launch_argv=list(metadata['target_argv']))
    if change == 'seed':
        planned['seed'] = 999
    elif change == 'start':
        planned['resolved_scenario']['start'] = {'x_m': 99, 'y_m': 99}
    elif change == 'control':
        planned['launch_argv'].append('different_gain:=2')
    contract = {**study['contract'], 'runs': [planned]}
    if change is None:
        analysis._q1_verify_run(run, contract)
    else:
        with pytest.raises(ValueError, match='reserved|planned acquisition'):
            analysis._q1_verify_run(run, contract)


def analytic_rows(template, *, weak=False, fallback=False):
    rows = []
    omega = math.tau/3
    transfer = numeric.continuous_transfer(omega)
    vector = [-transfer.real/.18, transfer.imag/.18]
    for index in range(1251):
        row = deepcopy(template)
        stamp = 10_250_000_000 + index*100_000_000
        row.update(stamp_ns=stamp, source_sequence=index+1, observation_id=index+1,
                   world_phase_rad=math.remainder(omega*index*.1, math.tau), context_id=0)
        row['method'].update(aligned_instant_world=vector,
                             v2_output_world=None if weak else vector,
                             usable_output=not weak, blend_applied=True,
                             usable_averaging=not (weak or fallback),
                             fallback_used=fallback)
        rows.append(row)
    return rows


@pytest.mark.parametrize('outcome', ['pass', 'fallback', 'weak'])
def test_analytic_reference_uses_actual_pair_and_full_eligible_denominator(study, monkeypatch, outcome):
    rows = analytic_rows(study['normalized'][0], weak=outcome == 'weak', fallback=outcome == 'fallback')
    monkeypatch.setattr(analysis, 'prepare_q1_direction_inputs',
                        lambda *a, **k: (deepcopy(rows), study['qualification']))
    paths = [freeze(study, partition)[0] for partition in analysis.Q1_PARTITION_SEEDS]
    monkeypatch.setattr(truth, '_model', lambda *a, **k: (object(), None))
    monkeypatch.setattr(truth, 'evaluate_raw_cost', lambda model, x, y, angle: math.cos(angle))
    monkeypatch.setattr(numeric, 'replay_matched_direction', lambda *a, **k: pytest.fail('no old callback replay'))
    result = analysis.evaluate_q1_direction_references(
        paths, study['directory'] / 'reference', contract_path=study['manifest']['contract']['path'])
    assert result['confirmation']['eligible_informative_count'] == 24
    assert result['confirmation']['blend_applied_count'] == 24
    assert result['confirmation']['averaging_availability'] == (1. if outcome == 'pass' else 0.)
    assert result['status'] == ('PASS' if outcome == 'pass' else 'FAIL')
    if outcome == 'weak':
        assert result['confirmation']['v2_median_error_deg'] is None
        assert result['confirmation']['missing_or_weak_output_count'] == 24
    else:
        assert result['confirmation']['v2_median_error_deg'] < 1e-5


def test_usable_availability_does_not_count_zero_vector_as_blend_success():
    fixture = typed_fixture()
    direction = fixture[4]
    direction.blend_weight = .5
    direction.output_body = [0., 0.]
    result = analysis._q1_method(direction)
    assert result['blend_applied'] and not result['usable_averaging']


def test_recorded_binding_uses_frozen_source_and_actual_captured_sensor_geometry(tmp_path):
    from test_v2_recording_contract import prepared
    target, metadata, _ = prepared()
    metadata['target_argv'] = target
    (tmp_path / 'metadata.yaml').write_text(yaml.safe_dump(metadata))
    description = Path(truth.SENSOR_GEOMETRY_PATH).read_text()
    parameters = {'nodes': {'robot_state_publisher': {'parameters': {
        '/robot_state_publisher': {'ros__parameters': {'robot_description': description}}}}}}
    (tmp_path / 'resolved_parameters.yaml').write_text(yaml.safe_dump(parameters))
    repository = Path(analysis.__file__).resolve().parents[5]
    launch = repository / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    selected = [Path(arg.split(':=', 1)[1]) for arg in target
                if arg.startswith(('cost_function_config_filepath:=', 'filter_config_filepath:=',
                                   'sensor_transform_config_filepath:='))]
    files = [receipt(path) for path in [launch, Path(truth.SENSOR_GEOMETRY_PATH), *selected]]
    result = analysis.q1_recorded_binding(tmp_path, source_files=files)
    assert result['selected_configurations']['filter_config_filepath']['sha256'] \
        == numeric.SELECTED_FILTER_SHA256
    assert result['captured_robot_description_hashes'] == [hashlib.sha256(description.encode()).hexdigest()]
    values = parameters['nodes']['robot_state_publisher']['parameters']['/robot_state_publisher']['ros__parameters']
    values['robot_description'] = \
        description.replace('xyz="0 0 0.355"', 'xyz="0 0 0.4"')
    # Replacing the actual joint origin without changing its file should be caught.
    if values['robot_description'] == description:
        values['robot_description'] = \
            '<robot><joint name="rotating_frame_joint"><origin xyz="0 0 .4" rpy="0 0 0"/></joint></robot>'
    (tmp_path / 'resolved_parameters.yaml').write_text(yaml.safe_dump(parameters))
    with pytest.raises(ValueError, match='captured sensor geometry'):
        analysis.q1_recorded_binding(tmp_path, source_files=files)


@pytest.mark.parametrize('outcome', ['uninformative', 'timeout'])
def test_numerical_unavailability_preserves_fixed_receipts_or_partial_attempt(study, monkeypatch, outcome):
    rows = analytic_rows(study['normalized'][0])
    monkeypatch.setattr(analysis, 'prepare_q1_direction_inputs',
                        lambda *a, **k: (deepcopy(rows), study['qualification']))
    paths = [freeze(study, partition)[0] for partition in analysis.Q1_PARTITION_SEEDS]
    monkeypatch.setattr(truth, '_model', lambda *a, **k: (object(), None))
    def raw(model, x, y, angle):
        if outcome == 'timeout':
            raise TimeoutError('declared synthetic deadline')
        return -1.
    monkeypatch.setattr(truth, 'evaluate_raw_cost', raw)
    output = study['directory'] / 'reference'
    if outcome == 'timeout':
        with pytest.raises(TimeoutError):
            analysis.evaluate_q1_direction_references(
                paths, output, contract_path=study['manifest']['contract']['path'])
        assert (output / 'started.json').is_file() and not (output / 'references.json').exists()
    else:
        result = analysis.evaluate_q1_direction_references(
            paths, output, contract_path=study['manifest']['contract']['path'])
        assert result['status'] == 'EVIDENCE_UNAVAILABLE'
        assert result['all']['fixed_anchor_count'] == 48
        assert result['all']['unavailable_reasons'] == {'uninformative_reference': 48}
