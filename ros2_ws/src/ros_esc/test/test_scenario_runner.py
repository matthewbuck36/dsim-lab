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
V3_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_v3_activation.yaml'
)


def _install_boundary_executor(
    monkeypatch,
    context,
    node,
    spin_once,
    events,
):
    """Install a context-bound executor fake with visible lifecycle events."""
    expected_context = context

    class FakeExecutor:
        def __init__(self, *, context):
            assert context is expected_context
            events.append('created')

        def add_node(self, added_node):
            assert added_node is node
            events.append('added')

        def spin_once(self, timeout_sec):
            spin_once(timeout_sec)

        def remove_node(self, removed_node):
            assert removed_node is node
            events.append('removed')

        def shutdown(self):
            events.append('shutdown')

    monkeypatch.setattr(runner, 'SingleThreadedExecutor', FakeExecutor)


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


def test_route_blocker_encounter_matches_first_active_typed_fill():
    """Require the first accepted fill to belong to the route blocker."""
    resolved = {
        'success': {
            'ground_truth': {
                'aggregate_field': {
                    'route_barrier_qualification': {
                        'basin': {'x_m': -0.5, 'y_m': 0.1},
                        'fill_center_tolerance_m': 0.35,
                    },
                },
            },
        },
    }
    close_fill = SimpleNamespace(
        active=True,
        superseded=False,
        center_x=-0.4,
        center_y=0.1,
    )
    far_fill = SimpleNamespace(
        active=True,
        superseded=False,
        center_x=0.5,
        center_y=0.1,
    )

    assert runner._route_blocker_encounter(
        resolved,
        [close_fill],
    ) == (
        True,
        {'x_m': -0.4, 'y_m': 0.1},
        pytest.approx(0.1),
        None,
    )
    assert runner._route_blocker_encounter(
        resolved,
        [far_fill],
    )[0] is False
    assert runner._route_blocker_encounter(
        resolved,
        [],
    ) == (False, None, None, None)
    assert runner._route_blocker_encounter(
        {'success': {'ground_truth': {'aggregate_field': {}}}},
        [],
    ) == (None, None, None, None)


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


def test_v4_metadata_and_launch_bind_passive_contact_evidence():
    """Carry sealed dimensions without contaminating a no-collision case."""
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
    assert 'simulation_contact_probe_enabled:=False' in launch


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


@pytest.mark.parametrize(
    ('failure_stage', 'expected_events'),
    [
        (
            'create_node',
            ['context_init', 'create_node', 'context_shutdown'],
        ),
        (
            'executor_init',
            [
                'context_init',
                'create_node',
                'executor_init',
                'node_destroy',
                'context_shutdown',
            ],
        ),
        (
            'add_node',
            [
                'context_init',
                'create_node',
                'executor_init',
                'add_node',
                'executor_shutdown',
                'node_destroy',
                'context_shutdown',
            ],
        ),
    ],
)
def test_boundary_setup_failure_cleans_partial_lifecycle(
    monkeypatch,
    failure_stage,
    expected_events,
):
    """Preserve setup errors while attempting every available cleanup."""
    events = []
    private_context = object()

    class SetupFailure(RuntimeError):
        pass

    class CleanupFailure(RuntimeError):
        pass

    class FakeNode:
        def create_subscription(self, *args, **kwargs):
            raise AssertionError('setup failure reached subscriptions')

        def destroy_node(self):
            events.append('node_destroy')
            raise CleanupFailure('node cleanup failed')

    node = FakeNode()

    class FakeExecutor:
        def __init__(self, *, context):
            assert context is private_context
            events.append('executor_init')
            if failure_stage == 'executor_init':
                raise SetupFailure(failure_stage)

        def add_node(self, added_node):
            assert added_node is node
            events.append('add_node')
            if failure_stage == 'add_node':
                raise SetupFailure(failure_stage)

        def remove_node(self, removed_node):
            raise AssertionError(
                f'partially added node was removed: {removed_node}'
            )

        def shutdown(self):
            events.append('executor_shutdown')
            raise CleanupFailure('executor cleanup failed')

    def init(*, context):
        assert context is private_context
        events.append('context_init')

    def create_node(*args, **kwargs):
        del args
        assert kwargs['context'] is private_context
        events.append('create_node')
        if failure_stage == 'create_node':
            raise SetupFailure(failure_stage)
        return node

    def shutdown(*, context):
        assert context is private_context
        events.append('context_shutdown')
        raise CleanupFailure('context cleanup failed')

    monkeypatch.setattr(
        runner.rclpy.context,
        'Context',
        lambda: private_context,
    )
    monkeypatch.setattr(runner.rclpy, 'init', init)
    monkeypatch.setattr(runner.rclpy, 'create_node', create_node)
    monkeypatch.setattr(runner, 'SingleThreadedExecutor', FakeExecutor)
    monkeypatch.setattr(runner.rclpy, 'shutdown', shutdown)
    monkeypatch.setattr(
        runner.subprocess,
        'Popen',
        lambda *args, **kwargs: pytest.fail(
            'setup failure must precede child dispatch'
        ),
    )

    with pytest.raises(SetupFailure, match=failure_stage):
        runner.run_record_process(
            ['must-not-start'],
            5.0,
            1.0,
            anchor_state='VERIFY_EXTREMUM',
            boundary_state='ESCAPE_REPULSE',
            boundary_required_events=['ESCAPE_STARTED'],
        )

    assert events == expected_events


def test_live_boundary_stop_waits_for_state_and_required_event(monkeypatch):
    """Request SIGINT only after the declared branch evidence is observable."""
    callbacks = {}
    dispatched = []
    executor_events = []
    signals = []
    wait_timeouts = []
    private_context = object()

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

    node = FakeNode()

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
            wait_timeouts.append(timeout)
            self.returncode = 0
            return 0

    sequence = [
        (
            '/gesc_gaussian/algorithm_events',
            SimpleNamespace(
                event_type=(
                    runner.AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
                )
            ),
        ),
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

    def spin_once(timeout_sec):
        del timeout_sec
        topic, message = sequence.pop(0)
        dispatched.append(topic)
        callbacks[topic](message)

    monkeypatch.setattr(
        runner.rclpy.context,
        'Context',
        lambda: private_context,
    )
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy,
        'create_node',
        lambda *args, **kwargs: node,
    )
    _install_boundary_executor(
        monkeypatch,
        private_context,
        node,
        spin_once,
        executor_events,
    )
    monkeypatch.setattr(
        runner.rclpy,
        'spin_once',
        lambda *args, **kwargs: pytest.fail(
            'boundary observer must not use the global executor'
        ),
    )
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
        boundary_required_events=[
            'CONVERGENCE_CONFIRMED',
            'ESCAPE_STARTED',
        ],
    )

    assert dispatched == [
        '/gesc_gaussian/algorithm_events',
        '/gesc_gaussian/algorithm_state',
        '/gesc_gaussian/algorithm_state',
        '/gesc_gaussian/algorithm_events',
    ]
    assert signals == [(4321, runner.signal.SIGINT)]
    assert wait_timeouts == [
        1.0 + runner.BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
    ]
    assert result['graceful_boundary_stop'] is True
    assert result['boundary_required_events_observed'] == [
        'CONVERGENCE_CONFIRMED',
        'ESCAPE_STARTED'
    ]
    assert result['stdout'] == 'boundary test\n'
    assert executor_events == ['created', 'added', 'removed', 'shutdown']


def test_scope_includes_causal_event_and_clips_pre_anchor_state():
    """Evaluate a VERIFY scope from the causal SEARCH transition."""
    scope = {
        'anchor_state': 'VERIFY_EXTREMUM',
        'boundary_state': 'ESCAPE_REPULSE',
    }
    state_records = [
        (1, 'SEARCH'),
        (3, 'VERIFY_EXTREMUM'),
        (5, 'DESIGN_OR_MERGE_FILL'),
        (7, 'ESCAPE_REPULSE'),
    ]
    event_records = [
        (2, 'CONVERGENCE_CONFIRMED'),
        (4, 'FILL_CREATED'),
        (6, 'ESCAPE_STARTED'),
    ]
    expectations = {
        'required_state_path': [
            'SEARCH',
            'VERIFY_EXTREMUM',
            'DESIGN_OR_MERGE_FILL',
            'ESCAPE_REPULSE',
        ],
        'required_events': [
            'CONVERGENCE_CONFIRMED',
            'FILL_CREATED',
            'ESCAPE_STARTED',
        ],
    }

    observations = runner._scope_observations(
        scope,
        state_records,
        event_records,
    )
    evidence = runner._controller_evidence(
        runner._scope_controller_expectations(scope, expectations),
        observations['observed_state_sequence'],
        observations['observed_events'],
    )

    assert observations['observed_events'] == [
        'CONVERGENCE_CONFIRMED',
        'FILL_CREATED',
        'ESCAPE_STARTED',
    ]
    assert evidence['required_state_path'] is True
    assert evidence['required_events'] is True


def test_boundary_stop_cleans_nested_session_after_outer_exit(monkeypatch):
    """Clean nested-session survivors while retaining boundary-stop output."""
    callbacks = {}
    executor_events = []
    signals = []
    private_context = object()
    identities = {
        5321: {
            'pid': 5321,
            'state': 'S',
            'parent_pid': 1,
            'process_group_id': 5321,
            'session_id': 5321,
            'start_ticks': 600,
        },
        5322: {
            'pid': 5322,
            'state': 'S',
            'parent_pid': 5321,
            'process_group_id': 5322,
            'session_id': 5322,
            'start_ticks': 700,
        },
    }
    alive = {5321, 5322}

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

    node = FakeNode()

    class FakeProcess:
        def __init__(self, command, stdout, **unused_kwargs):
            del command, unused_kwargs
            self.pid = 5321
            self.returncode = None
            self.reaped = False
            stdout.write('nested boundary output\n')

        def poll(self):
            if self.pid in alive:
                return None
            self.returncode = 0
            self.reaped = True
            return self.returncode

        def wait(self, timeout=None):
            del timeout
            if self.pid in alive:
                raise runner.subprocess.TimeoutExpired(['record'], 0.0)
            self.returncode = 0
            self.reaped = True
            return self.returncode

    process_holder = {}

    def popen(*args, **kwargs):
        process_holder['process'] = FakeProcess(*args, **kwargs)
        return process_holder['process']

    def spin_once(timeout_sec):
        del timeout_sec
        callbacks['/gesc_gaussian/algorithm_state'](
            SimpleNamespace(
                state_name='VERIFY_EXTREMUM',
                state=runner.AlgorithmState.STATE_VERIFY_EXTREMUM,
                state_valid=True,
            )
        )
        callbacks['/gesc_gaussian/algorithm_state'](
            SimpleNamespace(
                state_name='ESCAPE_REPULSE',
                state=runner.AlgorithmState.STATE_ESCAPE_REPULSE,
                state_valid=True,
            )
        )
        callbacks['/gesc_gaussian/algorithm_events'](
            SimpleNamespace(
                event_type=runner.AlgorithmEvent.EVENT_ESCAPE_STARTED
            )
        )

    def process_identity(pid):
        return dict(identities[pid]) if pid in alive else None

    def killpg(process_group_id, signum):
        signals.append((process_group_id, signum))
        if process_group_id == 5321 and signum == runner.signal.SIGINT:
            alive.discard(5321)
        if process_group_id == 5322 and signum == runner.signal.SIGTERM:
            alive.discard(5322)

    monkeypatch.setattr(
        runner.rclpy.context,
        'Context',
        lambda: private_context,
    )
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy,
        'create_node',
        lambda *args, **kwargs: node,
    )
    _install_boundary_executor(
        monkeypatch,
        private_context,
        node,
        spin_once,
        executor_events,
    )
    monkeypatch.setattr(runner.subprocess, 'Popen', popen)
    monkeypatch.setattr(runner, '_process_identity', process_identity)
    monkeypatch.setattr(
        runner,
        '_snapshot_process_tree',
        lambda unused_pid: dict(identities),
    )
    monkeypatch.setattr(runner.os, 'killpg', killpg)
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', 0.0)

    result = runner.run_record_process(
        ['record'],
        5.0,
        0.0,
        anchor_state='VERIFY_EXTREMUM',
        boundary_state='ESCAPE_REPULSE',
        boundary_required_events=['ESCAPE_STARTED'],
    )

    assert signals == [
        (5321, runner.signal.SIGINT),
        (5322, runner.signal.SIGINT),
        (5322, runner.signal.SIGTERM),
    ]
    assert result['graceful_boundary_stop'] is True
    assert result['stdout'] == 'nested boundary output\n'
    assert process_holder['process'].reaped is True
    assert alive == set()
    assert executor_events == ['created', 'added', 'removed', 'shutdown']


def test_record_interrupt_cleans_nested_session_and_reraises(monkeypatch):
    """Reap the outer runner and kill an owned surviving nested session."""
    signals = []
    identities = {
        8765: {
            'pid': 8765,
            'state': 'S',
            'parent_pid': 1,
            'process_group_id': 8765,
            'session_id': 8765,
            'start_ticks': 100,
        },
        8766: {
            'pid': 8766,
            'state': 'S',
            'parent_pid': 8765,
            'process_group_id': 8766,
            'session_id': 8766,
            'start_ticks': 200,
        },
    }
    alive = {8765, 8766}

    class FakeProcess:
        def __init__(self):
            self.pid = 8765
            self.returncode = None
            self.communicate_timeouts = []
            self.reaped = False

        def communicate(self, timeout=None):
            self.communicate_timeouts.append(timeout)
            if len(self.communicate_timeouts) == 1:
                raise KeyboardInterrupt
            if self.pid in alive:
                raise runner.subprocess.TimeoutExpired(
                    ['record'],
                    timeout,
                )
            self.returncode = 0
            self.reaped = True
            return '', None

        def poll(self):
            if self.pid in alive:
                return None
            self.returncode = 0
            self.reaped = True
            return self.returncode

    process = FakeProcess()

    def process_identity(pid):
        if pid not in alive:
            return None
        return dict(identities[pid])

    def killpg(process_group_id, signum):
        signals.append((process_group_id, signum))
        if process_group_id == 8765 and signum == runner.signal.SIGINT:
            alive.discard(8765)
        if process_group_id == 8766 and signum == runner.signal.SIGKILL:
            alive.discard(8766)

    monkeypatch.setattr(
        runner.subprocess,
        'Popen',
        lambda *args, **kwargs: process,
    )
    monkeypatch.setattr(runner, '_process_identity', process_identity)
    monkeypatch.setattr(
        runner,
        '_snapshot_process_tree',
        lambda unused_pid: dict(identities),
    )
    monkeypatch.setattr(runner.os, 'killpg', killpg)
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', 0.0)

    with pytest.raises(KeyboardInterrupt):
        runner.run_record_process(['record'], 10.0, 0.0)

    assert signals == [
        (8765, runner.signal.SIGINT),
        (8766, runner.signal.SIGINT),
        (8766, runner.signal.SIGTERM),
        (8766, runner.signal.SIGKILL),
    ]
    assert process.communicate_timeouts == [10.0, 0.0, 0.0, 0.0, 0.0]
    assert process.reaped is True
    assert alive == set()


def test_record_timeout_cleans_nested_session_and_keeps_result(monkeypatch):
    """Keep timeout output while cleaning a child in a separate session."""
    signals = []
    identities = {
        8865: {
            'pid': 8865,
            'state': 'S',
            'parent_pid': 1,
            'process_group_id': 8865,
            'session_id': 8865,
            'start_ticks': 400,
        },
        8866: {
            'pid': 8866,
            'state': 'S',
            'parent_pid': 8865,
            'process_group_id': 8866,
            'session_id': 8866,
            'start_ticks': 500,
        },
    }
    alive = {8865, 8866}

    class FakeProcess:
        def __init__(self):
            self.pid = 8865
            self.returncode = None
            self.communicate_calls = 0
            self.reaped = False

        def communicate(self, timeout=None):
            self.communicate_calls += 1
            if self.communicate_calls == 1:
                raise runner.subprocess.TimeoutExpired(
                    ['record'],
                    timeout,
                )
            if self.pid in alive:
                raise runner.subprocess.TimeoutExpired(
                    ['record'],
                    timeout,
                )
            self.returncode = 0
            self.reaped = True
            return 'retained timeout log', None

        def poll(self):
            if self.pid in alive:
                return None
            self.returncode = 0
            self.reaped = True
            return self.returncode

    process = FakeProcess()

    def process_identity(pid):
        return dict(identities[pid]) if pid in alive else None

    def killpg(process_group_id, signum):
        signals.append((process_group_id, signum))
        if process_group_id == 8865 and signum == runner.signal.SIGINT:
            alive.discard(8865)
        if process_group_id == 8866 and signum == runner.signal.SIGTERM:
            alive.discard(8866)

    monkeypatch.setattr(
        runner.subprocess,
        'Popen',
        lambda *args, **kwargs: process,
    )
    monkeypatch.setattr(runner, '_process_identity', process_identity)
    monkeypatch.setattr(
        runner,
        '_snapshot_process_tree',
        lambda unused_pid: dict(identities),
    )
    monkeypatch.setattr(runner.os, 'killpg', killpg)
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', 0.0)

    result = runner.run_record_process(['record'], 10.0, 0.0)

    assert result['timed_out'] is True
    assert result['return_code'] == 0
    assert result['stdout'] == 'retained timeout log'
    assert signals == [
        (8865, runner.signal.SIGINT),
        (8866, runner.signal.SIGINT),
        (8866, runner.signal.SIGTERM),
    ]
    assert process.reaped is True
    assert alive == set()


def test_boundary_base_exception_cleans_process_group_and_reraises(
    monkeypatch,
):
    """Clean the boundary run session before propagating a BaseException."""
    executor_events = []
    signals = []
    private_context = object()
    identity = {
        'pid': 9876,
        'state': 'S',
        'parent_pid': 1,
        'process_group_id': 9876,
        'session_id': 9876,
        'start_ticks': 300,
    }
    alive = {9876}
    lifecycle = {
        'node_destroyed': False,
        'rclpy_shutdown': False,
    }

    class CancelRun(BaseException):
        pass

    class FakeNode:
        def create_subscription(self, *args, **kwargs):
            return object()

        def destroy_node(self):
            lifecycle['node_destroyed'] = True

    node = FakeNode()

    def cancel_on_spin(timeout_sec):
        del timeout_sec
        raise CancelRun

    class FakeProcess:
        def __init__(self, command, stdout, **unused_kwargs):
            del command, unused_kwargs
            self.pid = 9876
            self.returncode = None
            self.wait_timeouts = []
            self.reaped = False
            stdout.write('interrupted boundary test\n')

        def poll(self):
            if self.pid not in alive:
                self.returncode = -runner.signal.SIGKILL
                self.reaped = True
            return self.returncode

        def wait(self, timeout=None):
            self.wait_timeouts.append(timeout)
            if self.pid in alive:
                raise runner.subprocess.TimeoutExpired(
                    ['record'],
                    timeout,
                )
            self.returncode = -runner.signal.SIGKILL
            self.reaped = True
            return self.returncode

    process_holder = {}

    def popen(*args, **kwargs):
        process_holder['process'] = FakeProcess(*args, **kwargs)
        return process_holder['process']

    def killpg(process_group_id, signum):
        signals.append((process_group_id, signum))
        if signum == runner.signal.SIGKILL:
            alive.discard(process_group_id)

    monkeypatch.setattr(
        runner.rclpy.context,
        'Context',
        lambda: private_context,
    )
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy,
        'shutdown',
        lambda context: lifecycle.update(rclpy_shutdown=True),
    )
    monkeypatch.setattr(
        runner.rclpy,
        'create_node',
        lambda *args, **kwargs: node,
    )
    _install_boundary_executor(
        monkeypatch,
        private_context,
        node,
        cancel_on_spin,
        executor_events,
    )
    monkeypatch.setattr(runner.subprocess, 'Popen', popen)
    monkeypatch.setattr(runner.os, 'killpg', killpg)
    monkeypatch.setattr(
        runner,
        '_snapshot_process_tree',
        lambda unused_pid: {9876: dict(identity)},
    )
    monkeypatch.setattr(
        runner,
        '_process_identity',
        lambda pid: dict(identity) if pid in alive else None,
    )
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', 0.0)

    with pytest.raises(CancelRun):
        runner.run_record_process(
            ['record'],
            10.0,
            0.0,
            anchor_state='VERIFY_EXTREMUM',
            boundary_state='ESCAPE_REPULSE',
            boundary_required_events=['ESCAPE_STARTED'],
        )

    process = process_holder['process']
    assert signals == [
        (9876, runner.signal.SIGINT),
        (9876, runner.signal.SIGTERM),
        (9876, runner.signal.SIGKILL),
    ]
    assert process.wait_timeouts == [0.0, 0.0, 0.0]
    assert process.reaped is True
    assert alive == set()
    assert lifecycle == {
        'node_destroyed': True,
        'rclpy_shutdown': True,
    }
    assert executor_events == ['created', 'added', 'removed', 'shutdown']


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


def test_v3_formal_cli_requires_qualified_workflow(
    monkeypatch,
):
    """Allow v3 dry inspection but reject direct empirical dispatch."""
    calls = []

    def fake_execute(*args, **kwargs):
        calls.append((args, kwargs))
        return {'runs': []}

    monkeypatch.setattr(runner, 'execute_suite', fake_execute)

    assert runner.main([
        str(V3_ACTIVATION),
        '--operator', 'test',
    ]) == 2
    assert calls == []
    assert runner.main([
        str(V3_ACTIVATION),
        '--operator', 'test',
        '--dry-run',
    ]) == 0
    assert len(calls) == 1


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
