"""Focused tests for Phase 06 scenario orchestration and classification."""

import datetime as dt
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from ros_esc.cost_function_node.cost_function_objects.noise_objects import (
    Uniform,
)
from ros_esc.experiment_recording.record_run import load_metadata_input
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.run_scenario import (
    build_launch_command,
    build_metadata,
    build_record_command,
    classify_result,
    cleanup_evidence,
    execute_suite,
    find_run_directory,
    generate_scenario_run_id,
    resolved_noise_config,
)
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SMOKE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
)
DIAGNOSTIC_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_1_diagnostic_activation.yaml'
)


def _resolved(profile='robust_gaussian_v1'):
    suite = load_suite(SMOKE)
    runs, _ = expand_suite(suite)
    return next(run for run in runs if run['profile'] == profile)


def _v4_branch_resolved():
    resolved = _resolved()
    resolved['schema_version'] = 4
    resolved['acceptance_family'] = 'lifecycle'
    resolved['acceptance_partition'] = 'activation'
    resolved['repeat_reference'] = None
    resolved['metric_applicability'] = {
        'escape_attempt': True,
        'escape_duration': True,
        'orbit_count': True,
        'revisit': False,
        'delay': False,
        'saturation': False,
    }
    resolved['validation'] = {
        'world': True,
        'contacts_enabled': True,
    }
    resolved['success'] = {
        'all_of': [
            'recording_complete',
            'cleanup_complete',
            'ground_truth_goal',
            'required_state_path',
            'required_events',
            'no_forbidden_states',
            'no_forbidden_events',
            'collision_expectation',
        ],
        'controller': {
            'expected_terminal_state': None,
            'required_state_sequence': [],
            'required_state_path': [
                'VERIFY_EXTREMUM',
                'DESIGN_OR_MERGE_FILL',
                'ESCAPE_REPULSE',
            ],
            'required_events': [
                'FILL_CREATED',
                'ESCAPE_STARTED',
            ],
            'required_event_sequence': [],
            'forbidden_states': ['FAILSAFE'],
            'forbidden_events': ['TIMEOUT', 'FAILSAFE'],
        },
        'ground_truth': {
            'method': 'aggregate_field',
            'final_position_tolerance_m': 0.35,
            'wall_margin_m': 0.35,
            'minimum_source_score': 0.95,
            'aggregate_field': {
                'targets': [{
                    'target_id': 'aggregate_001',
                    'x_m': 1.5,
                    'y_m': 1.0,
                }],
            },
        },
        'minimum_saturation_samples': 0,
        'collision_expected': False,
        'result_scopes': {
            'activation_window': {
                'anchor_state': 'VERIFY_EXTREMUM',
                'boundary_state': 'ESCAPE_REPULSE',
                'graceful_stop': True,
                'all_of': [
                    'required_state_path',
                    'required_events',
                ],
            },
            'full_lifecycle': {
                'anchor_state': 'SEARCH',
                'boundary_state': None,
                'graceful_stop': False,
                'all_of': [
                    'recording_complete',
                    'cleanup_complete',
                    'ground_truth_goal',
                    'no_forbidden_states',
                    'no_forbidden_events',
                    'collision_expectation',
                ],
            },
        },
    }
    return resolved


def test_launch_and_record_argv_compose_existing_owners_without_shell():
    """Compose only the existing launch and recorder through direct argv."""
    resolved = _resolved()
    launch = build_launch_command(resolved, gui=False)
    record = build_record_command(
        resolved,
        'safe-run',
        '/tmp/metadata.yaml',
        '/tmp/runs',
        {
            'run_timeout_sec': 5.0,
            'preflight_timeout_sec': 10.0,
            'shutdown_grace_sec': 3.0,
        },
        launch,
    )

    assert launch[:4] == [
        'ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml'
    ]
    assert 'gazebo_gui:=False' in launch
    assert 'gazebo_use_random_seed:=True' in launch
    assert 'gazebo_random_seed:=6001' in launch
    assert 'algorithm_profile:=robust_gaussian_v1' in launch
    assert 'recording_ready_required:=True' in launch
    assert 'number_of_lights:=1' in launch
    assert record[:4] == ['ros2', 'run', 'ros_esc', 'record_run']
    assert record[record.index('--') + 1:] == launch
    assert all(
        not any(token in item for token in (';', '&&', '|'))
        for item in record
    )


def test_metadata_and_launch_share_inputs(tmp_path):
    """Derive metadata and launch inputs from the same resolved scenario."""
    resolved = _resolved('legacy')
    metadata = build_metadata(
        resolved, 'codex-test', 'phase06-test', 'unit test'
    )
    path = tmp_path / 'metadata.yaml'
    path.write_text(yaml.safe_dump(metadata), encoding='utf-8')
    loaded = load_metadata_input(path, 'simulation')
    launch = build_launch_command(resolved)

    assert loaded['algorithm_profile'] == 'legacy'
    assert loaded['random_seed'] == 6001
    assert loaded['robot_starting_pose'] == {
        'x_m': 0.0, 'y_m': 0.0, 'yaw_rad': 0.0
    }
    assert loaded['sources'][0]['relative_lumen_input'] == 1000.0
    assert loaded['environment']['bounds_m']['x_min'] == -2.0
    assert 'algorithm_profile:=legacy' in launch
    assert 'light_1_intensity_lumens:=1000.0' in launch


def test_v4_metadata_and_launch_bind_acceptance_and_contact_evidence():
    """Carry sealed dimensions and enable zero-collision contact probing."""
    resolved = _v4_branch_resolved()

    metadata = build_metadata(
        resolved,
        'codex-test',
        'phase08-v3-test',
        'unit test',
    )
    launch = build_launch_command(resolved)

    scenario = metadata['scenario_runner']
    assert scenario['acceptance_family'] == 'lifecycle'
    assert scenario['acceptance_partition'] == 'activation'
    assert scenario['metric_applicability']['escape_attempt'] is True
    assert (
        scenario['success']['ground_truth']['method']
        == 'aggregate_field'
    )
    assert 'simulation_contacts_enabled:=True' in launch
    assert 'simulation_contact_probe_enabled:=True' in launch


def test_unique_run_ids_are_safe_even_for_identical_case_and_time():
    """Keep otherwise identical run IDs unique and Phase 05 compatible."""
    resolved = _resolved()
    now = dt.datetime(2026, 7, 24, tzinfo=dt.timezone.utc)
    first = generate_scenario_run_id(resolved, now=now, unique='aaaaaaaa')
    second = generate_scenario_run_id(resolved, now=now, unique='bbbbbbbb')

    assert first != second
    assert first.endswith('_aaaaaaaa')
    assert '/' not in first
    assert len(first) <= 128


def test_run_directory_lookup_is_exact_across_utc_date_boundary(tmp_path):
    """Find an exact run ID regardless of its containing UTC date."""
    run_id = '20260724T235959999999Z_simulation_case_aaaaaaaa'
    expected = tmp_path / '2026-07-25' / run_id
    expected.mkdir(parents=True)
    (tmp_path / '2026-07-24' / f'{run_id}-suffix').mkdir(parents=True)

    assert find_run_directory(tmp_path, run_id) == expected


def test_seeded_uniform_noise_config_does_not_mutate_base(tmp_path):
    """Generate a seeded Uniform override without changing the base."""
    resolved = _resolved()
    resolved['disturbances']['sensor_noise'] = {
        'model': 'uniform', 'bound': 0.125
    }
    path = resolved_noise_config(resolved, tmp_path / 'cost.json')
    document = json.loads(path.read_text(encoding='utf-8'))

    assert document['Noise']['object_name'] == 'Uniform'
    assert document['Noise']['params'] == {'bound': 0.125, 'seed_num': 6001}


def test_uniform_noise_repeats_exactly_for_the_same_seed():
    """Verify identical Uniform seeds produce identical sample sequences."""
    inputs = [0.0, 0.5, -0.5, 1.0]
    first = Uniform({'bound': 0.125, 'seed_num': 6001})
    first_samples = first.add_noise(0.0, inputs)
    second = Uniform({'bound': 0.125, 'seed_num': 6001})
    second_samples = second.add_noise(0.0, inputs)

    assert list(first_samples) == list(second_samples)


def test_component_ablations_map_only_to_existing_launch_controls():
    """Map component ablations to existing launch controls only."""
    resolved = _resolved()
    resolved['algorithm']['ablations'] = {
        'gaussian_fill_enabled': False,
        'affine_assist_enabled': False,
        'recenter_enabled': False,
    }
    launch = build_launch_command(resolved)

    assert 'escape_policy:=none' in launch
    assert 'modified_cost_enable_affine_bias:=False' in launch
    assert 'recenter_after_escape:=False' in launch


def test_controller_and_ground_truth_are_separate_classification_inputs():
    """Keep controller-observed and ground-truth success independent."""
    resolved = _resolved()
    resolved['success']['all_of'] = [
        'recording_complete', 'cleanup_complete', 'controller_goal'
    ]
    result = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        {
            'controller_goal': 'failed',
            'simulation_ground_truth': 'passed',
            'required_state_sequence_passed': True,
            'required_events_passed': True,
            'forbidden_events_absent': True,
            'minimum_saturation_samples_passed': True,
        },
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'ready_at_utc': '2026-07-25T00:00:00Z',
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            }
        },
    )

    assert result['passed'] is False
    assert result['status'] == 'failed'
    assert result['infrastructure_status'] == 'completed'
    assert result['predicate_results']['controller_goal'] is False


def test_activation_path_is_contiguous_at_first_verification():
    """Reject a later goal cycle when the first verification chose a fill."""
    observed = [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'SEARCH',
        'VERIFY_EXTREMUM',
        'GOAL_HOLD',
    ]

    assert runner._first_verification_path(
        [
            'SEARCH',
            'VERIFY_EXTREMUM',
            'DESIGN_OR_MERGE_FILL',
            'ESCAPE_REPULSE',
        ],
        observed,
    )
    assert not runner._first_verification_path(
        ['SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD'],
        observed,
    )


def test_schema_v3_predicates_bind_terminal_path_and_forbidden_states():
    """Make every newly declared controller expectation affect the result."""
    resolved = expand_suite(load_suite(DIAGNOSTIC_ACTIVATION))[0][2]
    outcomes = {
        'controller_goal': 'passed',
        'simulation_ground_truth': 'passed',
        'expected_terminal_state_passed': True,
        'required_state_path_passed': True,
        'required_events_passed': True,
        'forbidden_states_absent': False,
        'forbidden_events_absent': True,
        'collision_expectation_passed': True,
        'readiness_interval_available': True,
    }
    result = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            },
        },
        run_directory_available=True,
    )

    assert result['passed'] is False
    assert result['predicate_results']['expected_terminal_state'] is True
    assert result['predicate_results']['required_state_path'] is True
    assert result['predicate_results']['no_forbidden_states'] is False


def test_bag_without_true_readiness_marks_behavior_unavailable(
    monkeypatch,
    tmp_path,
):
    """Do not turn missing motion authorization into behavioral failure."""

    class FakeReader:
        def __init__(self):
            self.records = [(
                '/gesc_gaussian/recording_ready',
                SimpleNamespace(data=False),
                1,
            )]

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )

    outcomes = runner._bag_outcomes(tmp_path, _resolved())

    assert outcomes['readiness_interval_available'] is False
    assert outcomes['controller_goal'] == 'unavailable'
    assert outcomes['simulation_ground_truth'] == 'unavailable'
    assert outcomes['required_state_path_passed'] is None
    assert outcomes['required_state_sequence_passed'] is None
    assert outcomes['required_event_sequence_passed'] is None
    assert outcomes['forbidden_states_absent'] is None
    assert outcomes['forbidden_events_absent'] is None
    assert outcomes['collision_observed'] is None


def test_bag_outcomes_evaluate_schema_v3_path_event_and_forbidden_evidence(
    monkeypatch,
    tmp_path,
):
    """Extract every new binding predicate from the retained bag interval."""

    def state(name, value):
        return SimpleNamespace(
            state_name=name,
            state=value,
            state_valid=True,
        )

    class FakeReader:
        def __init__(self):
            self.records = [
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=True),
                    1,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state('SEARCH', 1),
                    2,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(event_type=11),
                    3,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state('VERIFY_EXTREMUM', 2),
                    4,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state('DESIGN_OR_MERGE_FILL', 3),
                    5,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(event_type=60),
                    6,
                ),
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=False),
                    7,
                ),
            ]

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )
    resolved = expand_suite(load_suite(DIAGNOSTIC_ACTIVATION))[0][0]

    outcomes = runner._bag_outcomes(tmp_path, resolved)

    assert outcomes['required_state_path_passed'] is True
    assert outcomes['required_events_passed'] is True
    assert outcomes['forbidden_states_absent'] is True
    assert outcomes['forbidden_events_absent'] is False


def test_bag_outcomes_reject_state_name_enum_mismatch(
    monkeypatch,
    tmp_path,
):
    """Do not let free-form text conceal a typed forbidden FAILSAFE."""

    class FakeReader:
        def __init__(self):
            self.records = [
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=True),
                    1,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    SimpleNamespace(
                        state_name='SEARCH',
                        state=8,
                        state_valid=True,
                    ),
                    2,
                ),
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=False),
                    3,
                ),
            ]

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )
    resolved = expand_suite(load_suite(DIAGNOSTIC_ACTIVATION))[0][0]

    outcomes = runner._bag_outcomes(tmp_path, resolved)

    assert outcomes['observed_state_sequence'] == ['FAILSAFE']
    assert outcomes['forbidden_states_absent'] is False
    assert 'name/enum mismatch' in outcomes['outcome_error']


def test_cross_producer_required_events_ignore_rosbag_receipt_order(
    monkeypatch,
    tmp_path,
):
    """Use membership when DDS writers do not share an ordering guarantee."""

    class FakeReader:
        def __init__(self):
            states = [
                ('SEARCH', 1),
                ('VERIFY_EXTREMUM', 2),
                ('DESIGN_OR_MERGE_FILL', 3),
                ('ESCAPE_REPULSE', 4),
            ]
            self.records = [(
                '/gesc_gaussian/recording_ready',
                SimpleNamespace(data=True),
                1,
            )]
            self.records.extend(
                (
                    '/gesc_gaussian/algorithm_state',
                    SimpleNamespace(
                        state_name=name,
                        state=value,
                        state_valid=True,
                    ),
                    stamp,
                )
                for stamp, (name, value) in enumerate(states, start=2)
            )
            self.records.extend([
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(event_type=40),
                    6,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(event_type=20),
                    7,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(event_type=11),
                    8,
                ),
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=False),
                    9,
                ),
            ])

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )
    resolved = expand_suite(load_suite(DIAGNOSTIC_ACTIVATION))[0][3]

    outcomes = runner._bag_outcomes(tmp_path, resolved)

    assert outcomes['required_state_path_passed'] is True
    assert outcomes['observed_events'] == [
        'ESCAPE_STARTED', 'FILL_CREATED', 'CONVERGENCE_CONFIRMED',
    ]
    assert outcomes['required_events_passed'] is True


def test_v4_bag_outcomes_use_aggregate_target_and_named_scope(
    monkeypatch,
    tmp_path,
):
    """Classify scoped branch evidence and aggregate terminal position."""

    def state(name, value):
        return SimpleNamespace(
            state_name=name,
            state=value,
            state_valid=True,
        )

    class FakeReader:
        def __init__(self):
            odometry = SimpleNamespace(
                pose=SimpleNamespace(
                    pose=SimpleNamespace(
                        position=SimpleNamespace(x=1.5, y=1.0),
                    ),
                ),
            )
            self.records = [
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=True),
                    1,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state('SEARCH', runner.AlgorithmState.STATE_SEARCH),
                    2,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state(
                        'VERIFY_EXTREMUM',
                        runner.AlgorithmState.STATE_VERIFY_EXTREMUM,
                    ),
                    3,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state(
                        'DESIGN_OR_MERGE_FILL',
                        runner.AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                    ),
                    4,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(
                        event_type=runner.AlgorithmEvent.EVENT_FILL_CREATED
                    ),
                    5,
                ),
                (
                    '/gesc_gaussian/algorithm_state',
                    state(
                        'ESCAPE_REPULSE',
                        runner.AlgorithmState.STATE_ESCAPE_REPULSE,
                    ),
                    6,
                ),
                (
                    '/gesc_gaussian/algorithm_events',
                    SimpleNamespace(
                        event_type=runner.AlgorithmEvent.EVENT_ESCAPE_STARTED
                    ),
                    7,
                ),
                ('/odom', odometry, 8),
                (
                    '/gesc_gaussian/simulation/contacts',
                    SimpleNamespace(states=[]),
                    9,
                ),
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=False),
                    10,
                ),
            ]

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )
    resolved = _v4_branch_resolved()

    outcomes = runner._bag_outcomes(tmp_path, resolved)
    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {
            'timed_out': False,
            'return_code': 0,
            'graceful_boundary_stop': True,
        },
        metadata={
            'recording': {
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            },
        },
        run_directory_available=True,
    )

    assert outcomes['simulation_ground_truth'] == 'passed'
    assert outcomes['final_goal_distances_m'] == {
        'aggregate_001': 0.0,
    }
    activation = outcomes['result_scopes']['activation_window']
    assert activation['boundary_observed'] is True
    assert activation['predicate_results']['required_state_path'] is True
    assert activation['predicate_results']['required_events'] is True
    assert classification['result_scopes'][
        'activation_window'
    ]['passed'] is True
    assert classification['passed'] is True


def test_v4_named_scope_requires_its_declared_anchor():
    """Reject an apparently safe empty full-lifecycle slice."""
    resolved = _v4_branch_resolved()
    outcomes = {
        'controller_goal': 'unavailable',
        'simulation_ground_truth': 'passed',
        'expected_terminal_state_passed': True,
        'required_state_sequence_passed': True,
        'required_state_path_passed': True,
        'required_event_sequence_passed': True,
        'required_events_passed': True,
        'forbidden_states_absent': True,
        'forbidden_events_absent': True,
        'minimum_saturation_samples_passed': True,
        'collision_expectation_passed': True,
        'result_scopes': {
            'activation_window': {
                'anchor_observed': True,
                'boundary_observed': True,
                'predicate_results': {
                    'required_state_path': True,
                    'required_events': True,
                },
            },
            'full_lifecycle': {
                'anchor_observed': False,
                'boundary_observed': True,
                'predicate_results': {
                    'no_forbidden_states': True,
                    'no_forbidden_events': True,
                },
            },
        },
    }

    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 0},
        metadata={'recording': {'readiness_ever_true': True}},
        run_directory_available=True,
    )

    assert classification['result_scopes']['full_lifecycle'][
        'anchor_observed'
    ] is False
    assert classification['passed'] is False


def test_v4_activation_scope_cannot_hide_later_full_lifecycle_failsafe():
    """Keep global safety false after a passing branch-only window."""
    resolved = _v4_branch_resolved()
    outcomes = {
        'controller_goal': 'unavailable',
        'simulation_ground_truth': 'passed',
        'expected_terminal_state_passed': True,
        'required_state_sequence_passed': True,
        'required_state_path_passed': True,
        'required_event_sequence_passed': True,
        'required_events_passed': True,
        'forbidden_states_absent': False,
        'forbidden_events_absent': False,
        'minimum_saturation_samples_passed': True,
        'collision_expectation_passed': True,
        'result_scopes': {
            'activation_window': {
                'anchor_observed': True,
                'boundary_observed': True,
                'predicate_results': {
                    'required_state_path': True,
                    'required_events': True,
                },
            },
            'full_lifecycle': {
                'anchor_observed': True,
                'boundary_observed': True,
                'predicate_results': {
                    'no_forbidden_states': False,
                    'no_forbidden_events': False,
                },
            },
        },
    }

    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 0},
        metadata={'recording': {'readiness_ever_true': True}},
        run_directory_available=True,
    )

    assert classification['result_scopes']['activation_window'][
        'passed'
    ] is True
    assert classification['result_scopes']['full_lifecycle'][
        'passed'
    ] is False
    assert classification['passed'] is False


@pytest.mark.parametrize(
    ('terminal_x', 'source_x', 'error_text'),
    [
        (float('nan'), None, 'nonfinite position'),
        (sys.float_info.max, -sys.float_info.max, 'distance is nonfinite'),
    ],
)
def test_nonfinite_terminal_evidence_is_extraction_failure(
    monkeypatch,
    tmp_path,
    terminal_x,
    source_x,
    error_text,
):
    """Do not leak nonfinite pose evidence into strict downstream JSON."""

    class FakeReader:
        def __init__(self):
            position = SimpleNamespace(x=terminal_x, y=0.0)
            odometry = SimpleNamespace(
                pose=SimpleNamespace(
                    pose=SimpleNamespace(position=position),
                ),
            )
            self.records = [
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=True),
                    1,
                ),
                ('/odom', odometry, 2),
                (
                    '/gesc_gaussian/recording_ready',
                    SimpleNamespace(data=False),
                    3,
                ),
            ]

        def open(self, *_args):  # noqa: A003 - matches rosbag reader API.
            return None

        def has_next(self):
            return bool(self.records)

        def read_next(self):
            return self.records.pop(0)

    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', FakeReader)
    monkeypatch.setattr(
        runner,
        'deserialize_message',
        lambda serialized, _message_type: serialized,
    )

    resolved = _resolved()
    if source_x is not None:
        for source in resolved['sources']:
            source['x_m'] = source_x
    outcomes = runner._bag_outcomes(tmp_path, resolved)
    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            },
        },
        run_directory_available=True,
    )

    if source_x is None:
        assert outcomes['final_position'] is None
    else:
        assert outcomes['final_position'] == {
            'x_m': terminal_x,
            'y_m': 0.0,
        }
    assert outcomes['final_goal_distances_m'] == {}
    assert error_text in outcomes['outcome_error']
    assert outcomes['simulation_ground_truth'] == 'unavailable'
    assert classification['infrastructure_status'] == (
        'evidence_extraction_failed'
    )
    json.dumps(outcomes, allow_nan=False)


def test_readiness_never_true_is_infrastructure_invalid():
    """Classify retained startup failure separately from algorithm behavior."""
    resolved = _resolved()
    resolved['success']['all_of'] = [
        'recording_complete',
        'cleanup_complete',
        'controller_goal',
    ]
    outcomes = runner._unavailable_outcomes(
        'no recorded true readiness interval'
    )
    result = classify_result(
        resolved,
        {'passed': False},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': False,
                'run_error': 'controller manager service unavailable',
            }
        },
        run_directory_available=True,
    )

    assert result['passed'] is False
    assert result['status'] == 'infrastructure_invalid'
    assert result['infrastructure_status'] == 'infrastructure_invalid'
    assert result['predicate_results']['controller_goal'] is None
    assert 'controller manager' in result['infrastructure_reason']


def test_runtime_failed_recording_cannot_be_classified_completed():
    """Propagate a finalized runtime failure after readiness became true."""
    resolved = _resolved()
    resolved['success']['all_of'] = [
        'recording_complete',
        'cleanup_complete',
    ]
    result = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        {
            'controller_goal': 'passed',
            'simulation_ground_truth': 'passed',
            'required_state_sequence_passed': True,
            'required_events_passed': True,
            'forbidden_events_absent': True,
            'minimum_saturation_samples_passed': True,
            'readiness_interval_available': True,
        },
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': True,
                'infrastructure_status': 'runtime_failed',
                'failure_stage': 'recording',
                'run_error': 'rosbag process exited unexpectedly',
            }
        },
        run_directory_available=True,
    )

    assert result['passed'] is False
    assert result['infrastructure_status'] == 'runtime_failed'
    assert result['failure_stage'] == 'recording'
    assert 'rosbag process' in result['infrastructure_reason']


def test_retained_readiness_failure_precedes_missing_completeness():
    """Do not mislabel a retained preflight failure as a missing directory."""
    result = classify_result(
        _resolved(),
        {},
        {'passed': True},
        runner._unavailable_outcomes('no true readiness interval'),
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': False,
                'failure_stage': 'operational_preflight',
                'run_error': 'operational readiness failed',
            }
        },
        run_directory_available=True,
    )

    assert result['infrastructure_status'] == 'infrastructure_invalid'
    assert result['failure_stage'] == 'operational_preflight'


def test_completed_readiness_with_bag_error_is_evidence_failure():
    """Do not pass an infrastructure-only case with unreadable outcomes."""
    resolved = _resolved()
    resolved['success']['all_of'] = [
        'recording_complete',
        'cleanup_complete',
    ]
    outcomes = runner._unavailable_outcomes(
        'ValueError: bag outcome decoding failed',
        readiness_interval_available=None,
    )
    result = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            }
        },
        run_directory_available=True,
    )

    assert result['passed'] is False
    assert result['infrastructure_status'] == 'evidence_extraction_failed'
    assert 'decoding failed' in result['infrastructure_reason']


def test_completed_readiness_with_cleanup_failure_is_infrastructure_failure():
    """Do not label a process/graph leak as infrastructure completed."""
    resolved = _resolved()
    resolved['success']['all_of'] = [
        'recording_complete',
        'cleanup_complete',
    ]
    result = classify_result(
        resolved,
        {'passed': True},
        {'passed': False},
        {
            'controller_goal': 'passed',
            'simulation_ground_truth': 'passed',
            'required_state_sequence_passed': True,
            'required_events_passed': True,
            'forbidden_events_absent': True,
            'minimum_saturation_samples_passed': True,
            'readiness_interval_available': True,
        },
        {'timed_out': False, 'return_code': 1},
        metadata={
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': True,
                'infrastructure_status': 'completed',
            }
        },
        run_directory_available=True,
    )

    assert result['passed'] is False
    assert result['infrastructure_status'] == 'cleanup_failed'


def test_cleanup_compares_only_new_graph_and_exact_session(monkeypatch):
    """Report only new graph nodes and exact-session survivors."""
    monkeypatch.setattr(
        runner, 'ros_graph_nodes', lambda: {'/baseline', '/new_node'}
    )
    monkeypatch.setattr(
        runner,
        'session_processes',
        lambda session_id: [{'pid': 42, 'session_id': session_id}],
    )

    evidence = cleanup_evidence({'/baseline'}, 1234, settle_sec=0.0)

    assert evidence['passed'] is False
    assert evidence['remaining_new_nodes'] == ['/new_node']
    assert evidence['remaining_session_processes'][0]['session_id'] == 1234


def test_live_boundary_stop_waits_for_state_and_required_event(monkeypatch):
    """Request SIGINT only after the declared branch evidence is observable."""
    callbacks = {}
    dispatched = []
    signals = []

    class FakeNode:
        def create_subscription(
            self,
            unused_type,
            topic,
            callback,
            unused_depth,
        ):
            callbacks[topic] = callback
            return object()

        def destroy_node(self):
            return None

    class FakeProcess:
        def __init__(self, command, stdout, **unused_kwargs):
            self.command = command
            self.stdout = stdout
            self.pid = 4321
            self.returncode = None
            stdout.write('boundary test\n')

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            del timeout
            self.returncode = 0
            return 0

    sequence = [
        (
            '/gesc_gaussian/algorithm_state',
            SimpleNamespace(
                state_name='VERIFY_EXTREMUM',
                state=runner.AlgorithmState.STATE_VERIFY_EXTREMUM,
                state_valid=True,
            ),
        ),
        (
            '/gesc_gaussian/algorithm_state',
            SimpleNamespace(
                state_name='ESCAPE_REPULSE',
                state=runner.AlgorithmState.STATE_ESCAPE_REPULSE,
                state_valid=True,
            ),
        ),
        (
            '/gesc_gaussian/algorithm_events',
            SimpleNamespace(
                event_type=runner.AlgorithmEvent.EVENT_ESCAPE_STARTED
            ),
        ),
    ]

    def spin_once(unused_node, timeout_sec):
        del timeout_sec
        topic, message = sequence.pop(0)
        dispatched.append(topic)
        callbacks[topic](message)

    monkeypatch.setattr(runner.rclpy.context, 'Context', lambda: object())
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy,
        'create_node',
        lambda *args, **kwargs: FakeNode(),
    )
    monkeypatch.setattr(runner.rclpy, 'spin_once', spin_once)
    monkeypatch.setattr(runner.subprocess, 'Popen', FakeProcess)
    monkeypatch.setattr(
        runner.os,
        'killpg',
        lambda pid, signum: signals.append((pid, signum)),
    )

    result = runner.run_record_process(
        ['record'],
        5.0,
        1.0,
        anchor_state='VERIFY_EXTREMUM',
        boundary_state='ESCAPE_REPULSE',
        boundary_required_events=['ESCAPE_STARTED'],
    )

    assert dispatched == [
        '/gesc_gaussian/algorithm_state',
        '/gesc_gaussian/algorithm_state',
        '/gesc_gaussian/algorithm_events',
    ]
    assert signals == [(4321, runner.signal.SIGINT)]
    assert result['graceful_boundary_stop'] is True
    assert result['boundary_required_events_observed'] == [
        'ESCAPE_STARTED'
    ]
    assert result['stdout'] == 'boundary test\n'


def test_failed_run_is_retained_and_cleanup_failure_stops_suite(
    monkeypatch, tmp_path
):
    """Retain a failed run and stop after a cleanup failure."""
    runs_root = tmp_path / 'runs'
    run_id = '20260724T000000000000Z_simulation_failed_aaaaaaaa'
    run_directory = runs_root / '2026-07-24' / run_id
    run_directory.mkdir(parents=True)
    (run_directory / 'completeness.json').write_text(
        json.dumps({'passed': False}), encoding='utf-8'
    )
    (run_directory / 'metadata.yaml').write_text(
        yaml.safe_dump({
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': False,
                'run_error': 'operational readiness failed',
            }
        }),
        encoding='utf-8',
    )
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda: {'/baseline'})
    monkeypatch.setattr(
        runner, 'generate_scenario_run_id',
        lambda resolved: run_id,
    )
    monkeypatch.setattr(
        runner, 'run_record_process',
        lambda *args, **kwargs: {
            'return_code': 1,
            'timed_out': False,
            'stdout': 'retained failure',
            'session_id': 1234,
        },
    )
    monkeypatch.setattr(
        runner, 'cleanup_evidence',
        lambda *args, **kwargs: {
            'passed': False,
            'baseline_nodes': ['/baseline'],
            'remaining_new_nodes': ['/leak'],
            'remaining_session_processes': [],
        },
    )
    monkeypatch.setattr(
        runner, '_bag_outcomes',
        lambda *args, **kwargs: {
            'controller_goal': 'failed',
            'simulation_ground_truth': 'failed',
            'required_state_sequence_passed': True,
            'required_events_passed': True,
            'forbidden_events_absent': True,
            'minimum_saturation_samples_passed': True,
        },
    )

    summary = execute_suite(
        SMOKE,
        'codex-test',
        runs_root=runs_root,
        summary_output=tmp_path / 'summary.yaml',
    )

    assert summary['stopped_early_reason'] == 'cleanup_failure'
    assert len(summary['runs']) == 1
    assert run_directory.is_dir()
    assert (run_directory / 'completeness.json').exists()
    assert (run_directory / 'scenario_result.yaml').exists()
    assert summary['runs'][0]['record_stdout_tail'] == 'retained failure'
    assert summary['runs'][0]['classification'][
        'infrastructure_status'
    ] == 'infrastructure_invalid'


def test_infrastructure_invalid_run_executes_once_without_retry(
    monkeypatch,
    tmp_path,
):
    """Retain one no-readiness attempt without silently retrying it."""
    runs_root = tmp_path / 'runs'
    run_id = '20260724T000000000000Z_simulation_noready_bbbbbbbb'
    run_directory = runs_root / '2026-07-24' / run_id
    run_directory.mkdir(parents=True)
    (run_directory / 'metadata.yaml').write_text(
        yaml.safe_dump({
            'recording': {
                'status': 'finalized',
                'readiness_ever_true': False,
                'failure_stage': 'operational_preflight',
                'run_error': 'operational readiness failed',
            }
        }),
        encoding='utf-8',
    )
    resolved = _resolved()
    attempts = []
    monkeypatch.setattr(
        runner,
        'expand_suite',
        lambda _suite, case_ids=None: ([resolved], []),
    )
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda: {'/baseline'})
    monkeypatch.setattr(
        runner, 'generate_scenario_run_id', lambda _resolved: run_id
    )

    def run_once(*_args, **_kwargs):
        attempts.append(run_id)
        return {
            'return_code': 1,
            'timed_out': False,
            'stdout': 'no readiness',
            'session_id': 4321,
        }

    monkeypatch.setattr(runner, 'run_record_process', run_once)
    monkeypatch.setattr(
        runner,
        'cleanup_evidence',
        lambda *_args, **_kwargs: {
            'passed': True,
            'baseline_nodes': ['/baseline'],
            'remaining_new_nodes': [],
            'remaining_session_processes': [],
        },
    )
    monkeypatch.setattr(
        runner,
        '_bag_outcomes',
        lambda *_args, **_kwargs: runner._unavailable_outcomes(
            'no recorded true readiness interval'
        ),
    )

    summary = execute_suite(
        SMOKE,
        'codex-test',
        runs_root=runs_root,
        summary_output=tmp_path / 'summary.yaml',
    )

    assert attempts == [run_id]
    assert len(summary['runs']) == 1
    assert summary['runs'][0]['classification'][
        'infrastructure_status'
    ] == 'infrastructure_invalid'


def test_dry_run_expands_profiles_without_default_summary(tmp_path):
    """Expand both profiles without launch or a default summary."""
    runs_root = tmp_path / 'runs'
    summary = execute_suite(
        SMOKE, 'codex-test', runs_root=runs_root, dry_run=True
    )

    assert summary['resolved_run_count'] == 2
    assert [run['profile'] for run in summary['runs']] == [
        'robust_gaussian_v1', 'legacy'
    ]
    assert not runs_root.exists()
    assert all(run['record_argv'][:4] == [
        'ros2', 'run', 'ros_esc', 'record_run'
    ] for run in summary['runs'])


def test_dry_run_writes_explicit_summary_and_preserves_unsupported(tmp_path):
    """Write a dry-run summary containing unsupported cases."""
    output = tmp_path / 'summary.yaml'
    catalog = (
        PACKAGE_ROOT
        / 'ros_esc/scenario_runner/scenarios/phase06_catalog.yaml'
    )
    summary = execute_suite(
        catalog,
        'codex-test',
        case_ids=['sensor_pose_delay'],
        summary_output=output,
        dry_run=True,
    )

    assert summary['runs'] == []
    assert summary['unsupported'][0]['case_id'] == 'sensor_pose_delay'
    assert yaml.safe_load(output.read_text(encoding='utf-8'))[
        'unsupported_count'
    ] == 1


def test_phase08_1_dry_run_exposes_bound_activation_contracts(tmp_path):
    """Make every corrected path and timing argument inspectable pre-launch."""
    output = tmp_path / 'phase08_1_dry_run.yaml'
    summary = execute_suite(
        DIAGNOSTIC_ACTIVATION,
        'codex-test',
        summary_output=output,
        dry_run=True,
    )

    assert summary['scenario_schema_version'] == 3
    assert summary['resolved_run_count'] == 10
    assert len(summary['runs']) == 10
    assert all(
        run['activation_contract']['contract_id'] == run['case_id']
        for run in summary['runs']
    )
    assert all(
        run['activation_contract']['verification_timing'][
            'selected_margin_sec'
        ] == pytest.approx(3.0)
        for run in summary['runs']
    )
    assert yaml.safe_load(output.read_text(encoding='utf-8'))[
        'resolved_run_count'
    ] == 10


@pytest.mark.skipif(
    os.environ.get('RUN_GESC_PHASE06_GAZEBO_E2E') != '1',
    reason=(
        'set RUN_GESC_PHASE06_GAZEBO_E2E=1 to run the recorded headless '
        'Gazebo integration'
    ),
)
def test_recorded_short_headless_end_to_end(tmp_path):
    """Record and clean up short robust and legacy Gazebo runs."""
    summary = execute_suite(
        SMOKE,
        'codex-automated-test',
        case_ids=['recorded_profile_smoke'],
        runs_root=tmp_path / 'runs',
        summary_output=tmp_path / 'summary.yaml',
    )

    assert len(summary['runs']) == 2
    assert all(run['recording_complete'] for run in summary['runs'])
    assert all(run['cleanup']['passed'] for run in summary['runs'])
    assert all(
        (Path(run['run_directory']) / 'scenario_result.yaml').exists()
        for run in summary['runs']
    )
