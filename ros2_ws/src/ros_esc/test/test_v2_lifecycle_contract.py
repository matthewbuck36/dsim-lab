"""Common wire hashes, explicit neighborhood configuration and graph ownership."""

import copy
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import CandidateSnapshot, FillResult, GaussianFill, SynchronizedObservation
from ros_esc.v2_lifecycle import (
    fill_registry_digest, fill_registry_payload, hash_payload, message_payload,
    result_sha256, snapshot_sha256,
)
from ros_esc.v2_stream import canonical_json, set_time
from ros_esc.modified_cost_node.v2_objective import objective_configuration, digest
from ros_esc.scenario_runner.scenario_schema import _validate_correction_overrides
from ros_esc.experiment_recording.record_run import applicable_topics, load_manifest, require_selected_algorithm_topics
from test_v2_stream import descriptor, resolve_frontend_command


PACKAGE = Path(__file__).resolve().parents[1]


def active_fill(identity=1):
    return GaussianFill(fill_id=identity, cluster_id=identity, revision=1,
                        center_x=1., center_y=2., amplitude=.3,
                        covariance_xx=.4, covariance_xy=.1, covariance_yy=.5,
                        active=True, covariance_valid=True)


def test_snapshot_hash_excludes_publication_but_binds_admission_and_first_state():
    snapshot = CandidateSnapshot(candidate_id=1, search_epoch=4,
                                 center_x_m=1., center_y_m=2.)
    observation = SynchronizedObservation(observation_id=3)
    set_time(observation.source_stamp, 11)
    set_time(observation.receipt_stamp, 10)
    set_time(observation.admission_stamp, 12)
    snapshot.observations = [observation]
    snapshot.observation_filter_state = [1]
    snapshot.observation_filter_stamp = [copy.deepcopy(observation.admission_stamp)]
    original = snapshot_sha256(snapshot)
    snapshot.evidence_sha256 = original
    set_time(snapshot.stamp, 50)
    set_time(snapshot.observations[0].stamp, 51)
    assert snapshot_sha256(snapshot) == original
    snapshot.observation_filter_state = [2]
    assert snapshot_sha256(snapshot) != original
    snapshot.observation_filter_state = [1]
    set_time(snapshot.observations[0].admission_stamp, 13)
    assert snapshot_sha256(snapshot) != original
    decoded = deserialize_message(serialize_message(snapshot), CandidateSnapshot)
    assert snapshot_sha256(decoded) == snapshot_sha256(snapshot)


def test_committed_envelope_hash_binds_result_generation_and_both_versions():
    result = FillResult(result=FillResult.ACTIVATED, registry_generation=2,
                        fill=active_fill(2), superseded_fill=active_fill(1),
                        has_superseded_fill=True)
    original = result_sha256(result)
    result.committed_sha256 = original
    set_time(result.stamp, 200)
    assert result_sha256(result) == original
    result.superseded_fill.amplitude = .4
    assert result_sha256(result) != original
    result.superseded_fill.amplitude = .3
    result.result = FillResult.ALREADY_ACTIVATED
    assert result_sha256(result) != original


def test_registry_digest_matches_actual_composer_law_and_ignores_diagnostics():
    fill = active_fill()
    host = SimpleNamespace(
        algorithm_state=SimpleNamespace(sensor_weight=1., gaussian_weight=1., affine_weight=0.),
        robust_terms={1: dict(cluster_id=1, revision=1, amplitude=.3,
                             center=[1., 2.], covariance=[[.4, .1], [.1, .5]])},
        robust_affine_terms={}, bias_all=False, enable_affine_bias=False,
        affine_decay_rate=.2, affine_max_age=30., affine_min_norm=1e-6)
    expected = digest(objective_configuration(host)['fills'])
    assert fill_registry_digest([fill]) == expected
    assert fill_registry_digest(fill_registry_payload([fill])) == expected
    fill.fit_residual = 50.
    set_time(fill.stamp, 900)
    assert fill_registry_digest([fill]) == expected
    with pytest.raises(ValueError): fill_registry_digest([fill, fill])
    fill.amplitude = float('nan')
    with pytest.raises(ValueError): fill_registry_digest([fill])
    assert hash_payload([]) == fill_registry_digest([])


def test_payload_detaches_arrays_and_refuses_nonfinite_hash_payload():
    msg = CandidateSnapshot(observation_filter_state=[1, 2])
    payload = message_payload(msg)
    payload['observation_filter_state'][0] = 8
    assert msg.observation_filter_state[0] == 1
    with pytest.raises(ValueError): hash_payload({'required': float('nan')})


@pytest.mark.parametrize('name', ['v2_candidate_radius_m', 'v2_candidate_epsilon_m'])
@pytest.mark.parametrize('value', [None, 0., -1., float('nan'), float('inf'), True])
def test_continuous_startup_has_no_silent_neighborhood_default(name, value):
    overrides = {'continuous_search_mode': 'rolling_gesc_v2',
                 'v2_candidate_radius_m': .5, 'v2_candidate_epsilon_m': .3}
    if value is None: overrides.pop(name)
    else: overrides[name] = value
    with pytest.raises(ValueError, match=name):
        _validate_correction_overrides(overrides, {}, 'test')


def test_launch_binds_all_existing_owners_and_nested_controller():
    launch = ET.parse(PACKAGE.parent / 'turtlebot3_rotating_sensor/launch/gazebo.launch.xml')
    defaults = {arg.attrib['name']: arg.attrib.get('default', '') for arg in launch.findall('arg')}
    assert defaults['v2_candidate_radius_m'] == defaults['v2_candidate_epsilon_m'] == '0.0'
    commands = [item.attrib.get('cmd', '') for item in launch.findall('.//executable')]
    for node in ('pde_history_node', 'convergence_detector_node', 'gaussian_fill_node', 'supervisor_node'):
        command = next(cmd for cmd in commands if f'ros_esc {node} ' in cmd)
        for name in ('continuous_search_mode', 'v2_run_id', 'v2_stream_config_json'):
            assert f'$(var {name})' in command
    controller = next(cmd for cmd in commands if 'ros_esc controller_node' in cmd)
    values = {**defaults, 'continuous_search_mode': 'rolling_gesc_v2', 'v2_run_id': 'm3-test'}
    args = resolve_frontend_command(controller, values)
    assert '--continuous-search-mode=rolling_gesc_v2' in args
    assert '--v2-run-id=m3-test' in args


@pytest.mark.parametrize('metric', ['pde_mean_v1', 'centroid_windows_v2'])
def test_recording_registers_event_streams_without_demanding_candidate_occurrence(metric):
    manifest = load_manifest(PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml')
    entries = applicable_topics(manifest, 'simulation')
    config = descriptor(2)
    # Use actual manifest routing; descriptor fixture alone has test-only topics.
    mapping = {'raw_cost_topic': 'raw_cost_legacy', 'source_cost_topic': 'source_cost',
               'augmented_cost_topic': 'augmented_cost_legacy', 'objective_cost_topic': 'v2_objective_cost',
               'provenance_topic': 'v2_source_provenance', 'pose_topic': 'pose',
               'encoder_topic': 'encoder', 'timekeeper_topic': 'timekeeper'}
    by_alias = {entry['alias']: entry for entry in entries}
    for key, alias in mapping.items():
        config[key] = by_alias[alias]['topic']
    target = ['continuous_search_mode:=rolling_gesc_v2', 'algorithm_profile:=robust_gaussian_v1',
              'v2_run_id:=m3-test', 'v2_stream_config_json:=' + canonical_json(config),
              'convergence_metric_mode:=' + metric]
    selected = {entry['alias']: entry for entry in require_selected_algorithm_topics(entries, 'simulation', target)}
    assert selected['v2_search_epoch']['required'] and selected['v2_search_epoch']['minimum_messages'] == 1
    for alias in ('v2_detector_confirmation', 'v2_candidate_snapshots', 'v2_fill_commands', 'v2_fill_results'):
        assert selected[alias]['required'] and selected[alias]['minimum_messages'] == 0
        assert selected[alias]['coverage'] == 'none'
    assert selected['v2_pde_history_evidence']['required'] == (metric == 'pde_mean_v1')
    assert not any(entry['alias'].startswith('v2_') for entry in applicable_topics(manifest, 'physical'))
