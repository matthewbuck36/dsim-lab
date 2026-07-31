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
M2_1_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_1_correction_probe.yaml'
)
M2_2_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_2_efficiency_correction_probe.yaml'
)
M2_3_CORRECTION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m2_3_assisted_recovery_stop_probe.yaml'
)
M3_SPATIAL_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m3_spatial_suite.yaml'
)
M4_2_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_2_visible_probe.yaml'
)
M4_3_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_3_visible_probe.yaml'
)
M4_4_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_4_visible_probe.yaml'
)
M4_4_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_4_two_light_suite.yaml'
)
M4_5_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_5_visible_probe.yaml'
)
M4_5_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_5_two_light_suite.yaml'
)
M4_6_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_6_visible_probe.yaml'
)
M4_6_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_6_two_light_suite.yaml'
)
M4_7_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_7_visible_probe.yaml'
)
M4_7_TWO_LIGHT_SUITE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v7_m4_7_two_light_suite.yaml'
)
V8_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_primary_visible_probe.yaml'
)
V8_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_primary_repeats.yaml'
)
V8_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_secondary_visible_probe.yaml'
)
V8_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_secondary_repeats.yaml'
)
V8_1_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_primary_visible_probe.yaml'
)
V8_1_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_primary_repeats.yaml'
)
V8_1_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_secondary_visible_probe.yaml'
)
V8_1_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_1_secondary_repeats.yaml'
)
V8_2_PRIMARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_primary_visible_probe.yaml'
)
V8_2_PRIMARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_primary_repeats.yaml'
)
V8_2_SECONDARY_VISIBLE_PROBE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_secondary_visible_probe.yaml'
)
V8_2_SECONDARY_REPEATS = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_v8_2_secondary_repeats.yaml'
)


def test_observed_local_recovery_binds_fill_to_local_convergence():
    """Accept a causal local fill and reject the same event at the global."""
    resolved = {
        'sources': [
            {'id': 'local', 'x_m': -0.8, 'y_m': 0.0},
            {'id': 'global', 'x_m': 1.3, 'y_m': 0.8},
        ],
        'success': {
            'local_recovery': {
                'local_source_id': 'local',
                'global_source_id': 'global',
                'convergence_to_local_max_m': 0.60,
                'convergence_to_global_min_m': 0.75,
                'fill_to_convergence_max_m': 0.50,
            },
        },
    }
    fill = SimpleNamespace(
        active=True,
        superseded=False,
        source_timestamp=42.0,
        source_timestamp_valid=True,
        center_x=-0.75,
        center_y=0.05,
    )
    event = SimpleNamespace(
        event_type=runner.AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED,
        source_timestamp=41.0,
        source_timestamp_valid=True,
        value_names=['fill_center_x_m', 'fill_center_y_m'],
        values=[-0.78, 0.02],
    )

    passed, evidence, error = runner._observed_local_recovery(
        resolved, [(1, event)], [fill]
    )
    assert passed is True
    assert error is None
    assert evidence['convergence_to_local_m'] < 0.60
    assert evidence['fill_source_timestamp'] == 42.0

    event.values = [1.25, 0.75]
    passed, evidence, error = runner._observed_local_recovery(
        resolved, [(1, event)], [fill]
    )
    assert passed is False
    assert error is None
    assert evidence['convergence_to_global_m'] < 0.75


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


def _v5_staged_resolved():
    resolved = _resolved()
    resolved.update({
        'schema_version': 5,
        'start': {
            'id': 'corner_start',
            'x_m': 0.0,
            'y_m': 0.0,
            'yaw_rad': 0.0,
        },
        'sources': [
            {
                'id': 'local',
                'x_m': 1.0606601717798212,
                'y_m': 1.0606601717798212,
                'relative_lumen_input': 400.0,
                'evaluation_role': 'local_minimum',
            },
            {
                'id': 'global',
                'x_m': 3.5,
                'y_m': 3.5,
                'relative_lumen_input': 1600.0,
                'evaluation_role': 'goal',
            },
        ],
        'bounds_m': [-0.25, 3.75, -0.25, 3.75],
        'room_center_m': [1.75, 1.75],
        'validation': {
            'world': True,
            'contacts_enabled': True,
            'geometry_profile': 'corner_origin_diagonal_sector_v1',
        },
        'known_topology': {
            'expected_local_minima': 1,
            'expected_global_minima': 1,
        },
        'acceptance_family': 'corner_origin_diagonal_sector',
        'acceptance_partition': 'development',
        'repeat_reference': None,
        'metric_applicability': {
            'escape_attempt': True,
            'escape_duration': True,
            'orbit_count': True,
            'revisit': False,
            'delay': False,
            'saturation': False,
        },
        'geometry': {
            'profile': 'corner_origin_diagonal_sector_v1',
            'world_file': (
                'gesc_gaussian_corner_origin_validation.world'
            ),
            'bounds_m': [-0.25, 3.75, -0.25, 3.75],
            'room_center_m': [1.75, 1.75],
            'wall_margin_m': 0.20,
            'allowed_center_domain_m': [
                -0.05, 3.55, -0.05, 3.55,
            ],
            'fixed_start': {
                'x_m': 0.0, 'y_m': 0.0, 'yaw_rad': 0.0,
            },
            'global_source_id': 'global',
            'fixed_global': {'x_m': 3.5, 'y_m': 3.5},
            'local_region': {
                'radius_min_m': 1.0,
                'radius_max_m': 2.0,
                'angle_center_rad': runner.math.pi / 4.0,
                'angle_half_width_rad': runner.math.pi / 4.0,
            },
            'local_placements': [{
                'source_id': 'local',
                'radius_m': 1.5,
                'angle_rad': runner.math.pi / 4.0,
                'angle_deg': 45.0,
                'angular_offset_rad': 0.0,
            }],
        },
    })
    resolved['algorithm']['launch_overrides'].update({
        'wall_margin_m': 0.20,
        'gaussian_fill_max_fills': 1,
    })
    resolved['success'] = {
        'all_of': [
            'recording_complete',
            'cleanup_complete',
            'local_recovery_stage',
            'post_recovery_global_proximity',
            'fill_cardinality',
            'collision_expectation',
        ],
        'controller': {},
        'ground_truth': {
            'method': 'declared_global_proximity',
            'global_source_id': 'global',
            'proximity_radius_m': 0.35,
        },
        'minimum_saturation_samples': 0,
        'collision_expected': False,
        'staged_recovery': {
            'local_source_ids': ['local'],
            'global_source_id': 'global',
            'convergence_to_local_max_m': 0.60,
            'convergence_to_global_min_m': 0.75,
            'fill_to_convergence_max_m': 0.50,
            'global_proximity_radius_m': 0.35,
        },
        'result_scopes': {},
    }
    return resolved


def _v6_staged_resolved():
    resolved = _v5_staged_resolved()
    resolved['schema_version'] = 6
    resolved['success']['ground_truth']['proximity_radius_m'] = 1.20
    resolved['success']['staged_recovery'].update({
        'local_association_mode': 'verified_trap',
        'global_proximity_radius_m': 1.20,
        'global_closer_radius_m': 1.00,
    })
    return resolved


def _v8_counted_resolved():
    return expand_suite(load_suite(V8_PRIMARY_VISIBLE_PROBE))[0][0]


def _v8_1_counted_resolved():
    return expand_suite(load_suite(V8_1_PRIMARY_VISIBLE_PROBE))[0][0]


def _v8_2_counted_resolved():
    return expand_suite(load_suite(V8_2_PRIMARY_VISIBLE_PROBE))[0][0]


def _state_message(name):
    return SimpleNamespace(
        state=getattr(runner.AlgorithmState, f'STATE_{name}'),
        state_name=name,
        state_valid=True,
    )


def _event_message(name, **overrides):
    values = {
        'event_type': getattr(runner.AlgorithmEvent, f'EVENT_{name}'),
        'source_timestamp': 0.0,
        'source_timestamp_valid': False,
        'fill_id': 0,
        'fill_id_valid': False,
        'value_names': [],
        'values': [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _fill_message(fill_id=7, cluster_id=42, center=(1.05, 1.05)):
    return SimpleNamespace(
        fill_id=fill_id,
        cluster_id=cluster_id,
        revision=1,
        source_timestamp=11.0 + fill_id * 0.001,
        source_timestamp_valid=True,
        center_x=center[0],
        center_y=center[1],
        active=True,
        superseded=False,
    )


def _odom_message(x_m, y_m, stamp_sec=0.0):
    seconds = int(stamp_sec)
    nanoseconds = int(round((float(stamp_sec) - seconds) * 1e9))
    return SimpleNamespace(
        header=SimpleNamespace(
            stamp=SimpleNamespace(sec=seconds, nanosec=nanoseconds),
        ),
        pose=SimpleNamespace(
            pose=SimpleNamespace(
                position=SimpleNamespace(x=x_m, y=y_m),
            ),
        ),
    )


def _staged_records():
    states = [
        (1, _state_message('SEARCH')),
        (2, _state_message('VERIFY_EXTREMUM')),
        (4, _state_message('DESIGN_OR_MERGE_FILL')),
        (7, _state_message('ESCAPE_REPULSE')),
        (9, _state_message('RECENTER')),
        (12, _state_message('SEARCH')),
    ]
    events = [
        (3, _event_message(
            'CONVERGENCE_CONFIRMED',
            source_timestamp=10.0,
            source_timestamp_valid=True,
            value_names=['fill_center_x_m', 'fill_center_y_m'],
            values=[1.04, 1.04],
        )),
        (6, _event_message(
            'FILL_CREATED',
            source_timestamp=11.007,
            source_timestamp_valid=True,
            fill_id=7,
            fill_id_valid=True,
            value_names=['cluster_id', 'revision'],
            values=[42.0, 1.0],
        )),
        (8, _event_message('ESCAPE_STARTED')),
        (10, _event_message('RECENTER_STARTED')),
        (11, _event_message('RECENTER_COMPLETE')),
    ]
    fills = [(5, _fill_message())]
    return states, events, fills


def _assisted_staged_records():
    states = [
        (1, _state_message('SEARCH')),
        (2, _state_message('VERIFY_EXTREMUM')),
        (4, _state_message('DESIGN_OR_MERGE_FILL')),
        (7, _state_message('ESCAPE_REPULSE')),
        (9, _state_message('DESIGN_OR_MERGE_FILL')),
        (11, _state_message('ESCAPE_ASSIST')),
        (13, _state_message('RECENTER')),
        (16, _state_message('SEARCH')),
    ]
    events = [
        (3, _event_message(
            'CONVERGENCE_CONFIRMED',
            source_timestamp=10.0,
            source_timestamp_valid=True,
            value_names=['fill_center_x_m', 'fill_center_y_m'],
            values=[1.04, 1.04],
        )),
        (6, _event_message(
            'FILL_CREATED',
            source_timestamp=11.007,
            source_timestamp_valid=True,
            fill_id=7,
            fill_id_valid=True,
            value_names=['cluster_id', 'revision'],
            values=[42.0, 1.0],
        )),
        (8, _event_message('ESCAPE_STARTED')),
        (10, _event_message('ESCAPE_STALLED')),
        (14, _event_message('RECENTER_STARTED')),
        (15, _event_message('RECENTER_COMPLETE')),
    ]
    fills = [(5, _fill_message())]
    return states, events, fills


def _counted_staged_records():
    states = [
        (1, _state_message('SEARCH')),
        (2, _state_message('VERIFY_EXTREMUM')),
        (4, _state_message('DESIGN_OR_MERGE_FILL')),
        (7, _state_message('ESCAPE_REPULSE')),
        (10, _state_message('SEARCH')),
    ]
    events = [
        (3, _event_message(
            'CONVERGENCE_CONFIRMED',
            source_timestamp=10.0,
            source_timestamp_valid=True,
            value_names=['fill_center_x_m', 'fill_center_y_m'],
            values=[1.04, 1.04],
        )),
        (6, _event_message(
            'FILL_CREATED',
            source_timestamp=11.007,
            source_timestamp_valid=True,
            fill_id=7,
            fill_id_valid=True,
            value_names=['cluster_id', 'revision'],
            values=[42.0, 1.0],
        )),
        (8, _event_message('ESCAPE_STARTED')),
    ]
    fills = [(5, _fill_message())]
    return states, events, fills


def _counted_assisted_staged_records():
    states, events, fills = _counted_staged_records()
    states = [
        *states[:4],
        (9, _state_message('ESCAPE_ASSIST')),
        (11, _state_message('SEARCH')),
    ]
    events.append((8, _event_message('ESCAPE_STALLED')))
    return states, events, fills


def _ranked_goal_message(
    *,
    candidate_upper=-10.0,
    comparison_lower=-5.0,
    margin=5.0,
):
    return _event_message(
        'GOAL_REACHED',
        detail=(
            'counted candidate raw-cost interval strictly lower than '
            'all retained candidates'
        ),
        value_names=[
            'candidate_raw_cost_upper',
            'candidate_ordinal',
            'filled_candidate_count',
            'known_source_count',
            'comparison_filled_raw_cost_lower',
            'candidate_strict_separation_margin',
        ],
        values=[
            candidate_upper,
            2.0,
            1.0,
            2.0,
            comparison_lower,
            margin,
        ],
    )


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


def test_v5_launch_and_metadata_bind_shifted_world_profile():
    """Resolve the new world and typed geometry through existing owners."""
    resolved = _v5_staged_resolved()

    launch = build_launch_command(resolved, gui=False)
    metadata = build_metadata(
        resolved,
        operator='phase08_7_m1',
        experiment_version='phase08-v7',
        operator_notes='qualification only',
    )

    assert any(
        item.endswith(
            'gesc_gaussian_corner_origin_validation.world'
        )
        for item in launch
    )
    for expected in (
        'init_x_position:=0.0',
        'init_y_position:=0.0',
        'init_yaw_angle:=0.0',
        'room_bounds_x_min_m:=-0.25',
        'room_bounds_x_max_m:=3.75',
        'room_bounds_y_min_m:=-0.25',
        'room_bounds_y_max_m:=3.75',
        'room_center_x_m:=1.75',
        'room_center_y_m:=1.75',
        'wall_margin_m:=0.2',
        'gaussian_fill_max_fills:=1',
        'simulation_contacts_enabled:=True',
    ):
        assert expected in launch
    scenario = metadata['scenario_runner']
    assert scenario['known_topology']['expected_local_minima'] == 1
    local = scenario['geometry']['local_placements'][0]
    assert local['source_id'] == 'local'
    assert local['radius_m'] == pytest.approx(1.5)
    assert local['angle_rad'] == pytest.approx(runner.math.pi / 4.0)
    assert local['angle_deg'] == pytest.approx(45.0)
    assert metadata['environment']['geometry']['fixed_global'] == {
        'x_m': 3.5,
        'y_m': 3.5,
    }


def test_m2_1_launch_binds_detector_topology_affine_and_relaxed_stop():
    """Resolve every correction through the existing central launch owner."""
    runs, unsupported = expand_suite(load_suite(M2_1_CORRECTION))
    resolved = runs[0]
    launch = build_launch_command(resolved, gui=True)

    assert unsupported == []
    for expected in (
        'gazebo_gui:=True',
        'convergence_state_gating_enabled:=True',
        'convergence_minimum_path_length_m:=0.2',
        'convergence_maximum_path_efficiency:=0.35',
        'gaussian_fill_max_fills:=1',
        'modified_cost_enable_affine_bias:=True',
        'post_recovery_guidance_enabled:=True',
        'post_recovery_guidance_max_sec:=60.0',
        'post_recovery_retry_limit:=3',
        'modified_cost_affine_gain:=0.5',
        'modified_cost_affine_max_age:=60.0',
    ):
        assert expected in launch
    assert resolved['success']['staged_recovery'][
        'global_proximity_radius_m'
    ] == 0.60


def test_m2_2_launch_changes_only_motion_efficiency_cap():
    """Bind the evidence-calibrated cap without changing other controls."""
    m2_1 = expand_suite(load_suite(M2_1_CORRECTION))[0][0]
    m2_2 = expand_suite(load_suite(M2_2_CORRECTION))[0][0]
    launch_m2_1 = build_launch_command(m2_1, gui=True)
    launch_m2_2 = build_launch_command(m2_2, gui=True)

    assert 'convergence_maximum_path_efficiency:=0.35' in launch_m2_1
    assert 'convergence_maximum_path_efficiency:=0.5' in launch_m2_2
    normalized_m2_1 = [
        item.replace(
            'convergence_maximum_path_efficiency:=0.35',
            'convergence_maximum_path_efficiency:=0.5',
        )
        for item in launch_m2_1
    ]
    assert normalized_m2_1 == launch_m2_2


def test_m2_3_preserves_launch_and_binds_evidence_stop():
    """Keep algorithm launch bytes while correcting the runner contract."""
    m2_2 = expand_suite(load_suite(M2_2_CORRECTION))[0][0]
    m2_3 = expand_suite(load_suite(M2_3_CORRECTION))[0][0]

    assert build_launch_command(m2_3, gui=True) == (
        build_launch_command(m2_2, gui=True)
    )
    assert m2_3['success']['ground_truth'][
        'proximity_radius_m'
    ] == 1.20
    assert m2_3['success']['staged_recovery'][
        'global_proximity_radius_m'
    ] == 1.20
    assert len(
        m2_3['success']['controller']['required_state_paths']
    ) == 2


def test_m3_changes_only_position_seed_gui_and_reporting_contract():
    """Keep every M2.3 algorithm launch value across the fixed M3 cross."""
    m2_3 = expand_suite(load_suite(M2_3_CORRECTION))[0][0]
    suite = load_suite(M3_SPATIAL_SUITE)
    runs, unsupported = expand_suite(suite)
    ignored_launch_prefixes = (
        'gazebo_gui:=',
        'gazebo_random_seed:=',
        'light_1_x:=',
        'light_1_y:=',
    )

    def fixed_launch_values(resolved, gui):
        return [
            item for item in build_launch_command(resolved, gui=gui)
            if not item.startswith(ignored_launch_prefixes)
        ]

    expected_launch = fixed_launch_values(m2_3, gui=True)
    assert unsupported == []
    assert len(runs) == 5
    for resolved in runs:
        assert resolved['algorithm'] == m2_3['algorithm']
        assert fixed_launch_values(resolved, gui=False) == expected_launch
        staged = resolved['success']['staged_recovery']
        assert staged['global_proximity_radius_m'] == 1.00
        assert staged['global_approach_radius_m'] == 1.20


@pytest.mark.parametrize(
    'scenario_path',
    [M4_2_VISIBLE_PROBE, M4_3_VISIBLE_PROBE, M4_4_VISIBLE_PROBE],
)
def test_m4_2_through_m4_4_launch_binds_progress_and_staged_budget(
    scenario_path,
):
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)
    resolved = runs[0]
    launch = build_launch_command(resolved, gui=True)

    assert unsupported == []
    for expected in (
        'gazebo_gui:=True',
        'post_recovery_progress_enabled:=True',
        'post_recovery_guidance_min_progress_m:=0.6',
        'post_recovery_liveness_window_sec:=12.0',
        'post_recovery_liveness_min_path_length_m:=0.6',
        'post_recovery_liveness_max_displacement_m:=0.2',
        'post_recovery_direction_refresh_limit:=1',
        'robust_search_epoch_reset_enabled:=True',
        'recenter_tolerance_m:=0.15',
        'post_recovery_guidance_max_sec:=90.0',
    ):
        assert expected in launch
    assert resolved['success']['staged_recovery'][
        'post_stage_a_timeout_sec'
    ] == 120.0
    assert suite['execution']['run_timeout_sec'] == 480.0
    assert suite['execution']['wall_timeout_sec'] == 660.0
    assert suite['execution']['shutdown_grace_sec'] == 45.0


@pytest.mark.parametrize(
    'scenario_path',
    [M4_4_VISIBLE_PROBE, M4_4_TWO_LIGHT_SUITE],
)
def test_m4_4_launch_binds_only_default_off_behavior_controls(
    scenario_path,
):
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            gui=suite['execution']['gazebo_gui'],
        )
        assert 'adaptive_recenter_lookahead_enabled:=True' in launch
        assert 'post_recovery_source_led_handoff_enabled:=True' in launch
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            for token in launch
        )


@pytest.mark.parametrize(
    'scenario_path',
    [M4_5_VISIBLE_PROBE, M4_5_TWO_LIGHT_SUITE],
)
def test_m4_5_launch_binds_only_declared_recovery_controls(
    scenario_path,
):
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'post_recovery_source_continuity_enabled:=True',
            'post_recovery_source_continuity_min_displacement_m:=0.05',
            'post_recovery_source_reversal_dot_threshold:=-0.9',
            'post_recovery_source_bypass_clearance_m:=0.1',
            'controller_spawner_load_recovery_enabled:=True',
        ):
            assert expected in launch
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            for token in launch
        )
        staged = resolved['success']['staged_recovery']
        assert staged['stage_a_timeout_sec'] == 480.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
    assert suite['execution']['run_timeout_sec'] == 600.0
    assert suite['execution']['wall_timeout_sec'] == 780.0


@pytest.mark.parametrize(
    'scenario_path',
    [M4_6_VISIBLE_PROBE, M4_6_TWO_LIGHT_SUITE],
)
def test_m4_6_launch_changes_only_explicit_continuity_threshold(
    scenario_path,
):
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'post_recovery_source_continuity_enabled:=True',
            'post_recovery_source_continuity_min_displacement_m:=0.05',
            'post_recovery_source_reversal_dot_threshold:=-0.8',
            'post_recovery_source_bypass_clearance_m:=0.1',
            'controller_spawner_load_recovery_enabled:=True',
        ):
            assert expected in launch
        assert (
            'post_recovery_source_reversal_dot_threshold:=-0.9'
            not in launch
        )
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            for token in launch
        )
        staged = resolved['success']['staged_recovery']
        assert staged['stage_a_timeout_sec'] == 480.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
    assert suite['execution']['run_timeout_sec'] == 600.0
    assert suite['execution']['wall_timeout_sec'] == 780.0


@pytest.mark.parametrize(
    'scenario_path',
    [M4_7_VISIBLE_PROBE, M4_7_TWO_LIGHT_SUITE],
)
def test_m4_7_launch_binds_source_resume_without_ground_truth_controls(
    scenario_path,
):
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'post_recovery_source_continuity_enabled:=True',
            'post_recovery_source_reversal_dot_threshold:=-0.8',
            'post_recovery_source_bypass_clearance_m:=0.1',
            'post_recovery_source_resume_enabled:=True',
            'post_recovery_source_resume_min_progress_m:=0.2',
            'post_recovery_progress_enabled:=True',
            'recoverable_navigation_enabled:=True',
        ):
            assert expected in launch
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            for token in launch
        )
        staged = resolved['success']['staged_recovery']
        assert staged['stage_a_timeout_sec'] == 480.0
        assert staged['post_stage_a_timeout_sec'] == 120.0
    assert suite['execution']['run_timeout_sec'] == 600.0
    assert suite['execution']['wall_timeout_sec'] == 780.0


@pytest.mark.parametrize(
    'scenario_path',
    [
        V8_PRIMARY_VISIBLE_PROBE,
        V8_PRIMARY_REPEATS,
        V8_SECONDARY_VISIBLE_PROBE,
        V8_SECONDARY_REPEATS,
    ],
)
def test_v8_launch_binds_count_only_and_open_field_without_evaluator_controls(
    scenario_path,
):
    """Pass source count, never evaluator geometry, into the controller."""
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            cost_path=Path('/tmp/phase08_v8_cost.yaml'),
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'number_of_lights:=2',
            'extremum_classification_mode:=counted_candidates',
            'known_source_count:=2',
            'candidate_cost_rotation_period_sec:=3.0',
            'candidate_cost_required_rotations:=2',
            'candidate_cost_mad_scale:=3.0',
            'convergence_confirmation_policy:=qualified_dwell',
            'convergence_confirmation_dwell_sec:=6.0',
            'robust_search_epoch_reset_enabled:=True',
            'operating_bounds_enabled:=False',
            'modified_cost_enable_affine_bias:=False',
            'recenter_after_escape:=False',
            'post_recovery_guidance_enabled:=False',
            'recoverable_navigation_enabled:=False',
            'simulation_contacts_enabled:=False',
        ):
            assert expected in launch
        assert not any(token.startswith('gazebo_world:=') for token in launch)
        forbidden_fragments = {
            str(source[field])
            for source in resolved['sources']
            for field in ('x_m', 'y_m', 'relative_lumen_input')
        }
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            or (
                not token.startswith('light_')
                and any(
                    fragment in token for fragment in forbidden_fragments
                )
            )
            for token in launch
            if not token.startswith('number_of_lights:=')
        )


@pytest.mark.parametrize(
    'scenario_path',
    [
        V8_1_PRIMARY_VISIBLE_PROBE,
        V8_1_PRIMARY_REPEATS,
        V8_1_SECONDARY_VISIBLE_PROBE,
        V8_1_SECONDARY_REPEATS,
    ],
)
def test_v8_1_launch_binds_outward_assist_without_evaluator_controls(
    scenario_path,
):
    """Expose only the opt-in assist and count through the launch graph."""
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            cost_path=Path('/tmp/phase08_v8_1_cost.yaml'),
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'number_of_lights:=2',
            'extremum_classification_mode:=counted_candidates',
            'known_source_count:=2',
            'open_field_escape_assist_enabled:=True',
            'gaussian_fill_exit_sigma:=8.0',
            'escape_max_sec:=35.0',
            'operating_bounds_enabled:=False',
            'modified_cost_enable_affine_bias:=False',
            'recenter_after_escape:=False',
            'post_recovery_guidance_enabled:=False',
            'recoverable_navigation_enabled:=False',
            'simulation_contacts_enabled:=False',
        ):
            assert expected in launch
        forbidden_fragments = {
            str(source[field])
            for source in resolved['sources']
            for field in ('x_m', 'y_m', 'relative_lumen_input')
        }
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            or (
                not token.startswith('light_')
                and any(
                    fragment in token for fragment in forbidden_fragments
                )
            )
            for token in launch
            if not token.startswith('number_of_lights:=')
        )


@pytest.mark.parametrize(
    'scenario_path',
    [
        V8_2_PRIMARY_VISIBLE_PROBE,
        V8_2_PRIMARY_REPEATS,
        V8_2_SECONDARY_VISIBLE_PROBE,
        V8_2_SECONDARY_REPEATS,
    ],
)
def test_v8_2_launch_binds_bounded_raw_history_without_evaluator_controls(
    scenario_path,
):
    """Expose bounded raw history, never source geometry, to the controller."""
    suite = load_suite(scenario_path)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    for resolved in runs:
        launch = build_launch_command(
            resolved,
            cost_path=Path('/tmp/phase08_v8_2_cost.yaml'),
            gui=suite['execution']['gazebo_gui'],
        )
        for expected in (
            'number_of_lights:=2',
            'extremum_classification_mode:=counted_candidates',
            'known_source_count:=2',
            'candidate_cost_rotation_period_sec:=3.0',
            'candidate_cost_required_rotations:=3',
            'candidate_cost_pretrigger_rotations:=6',
            'candidate_cost_mad_scale:=3.0',
            'open_field_escape_assist_enabled:=True',
            'operating_bounds_enabled:=False',
            'modified_cost_enable_affine_bias:=False',
            'recenter_after_escape:=False',
            'post_recovery_guidance_enabled:=False',
            'recoverable_navigation_enabled:=False',
            'simulation_contacts_enabled:=False',
        ):
            assert expected in launch
        forbidden_fragments = {
            str(source[field])
            for source in resolved['sources']
            for field in ('x_m', 'y_m', 'relative_lumen_input')
        }
        assert not any(
            token.startswith('global_source_')
            or token.startswith('source_role_')
            or token.startswith('simulation_truth_')
            or (
                not token.startswith('light_')
                and any(
                    fragment in token for fragment in forbidden_fragments
                )
            )
            for token in launch
            if not token.startswith('number_of_lights:=')
        )


def test_staged_recovery_reports_stage_a_cardinality_and_global_sample():
    """Separate local recovery, exact clusters, and post-recovery arrival."""
    resolved = _v5_staged_resolved()
    states, events, fills = _staged_records()

    stage_a, cardinality, evidence, error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events,
            fills + [fills[0]],
        )
    )
    stage_b, proximity, proximity_error = (
        runner._post_recovery_global_proximity(
            resolved,
            stage_a,
            evidence,
            [
                (11, _odom_message(3.5, 3.5)),
                (13, _odom_message(3.0, 3.0)),
                (14, _odom_message(3.30, 3.30)),
                (15, _odom_message(3.49, 3.49)),
            ],
        )
    )

    assert error is None
    assert stage_a is True
    assert cardinality is True
    assert evidence['created_cluster_ids'] == [42]
    assert evidence['assignments'][0]['local_source_id'] == 'local'
    assert stage_b is True
    assert proximity_error is None
    assert proximity['sample_bag_stamp'] == 14
    assert proximity['distance_m'] == pytest.approx(
        runner.math.hypot(0.20, 0.20)
    )
    assert proximity['interpolation_used'] is False

    extra_fill = _fill_message(
        fill_id=8,
        cluster_id=43,
        center=(3.5, 3.5),
    )
    extra_event = _event_message(
        'FILL_CREATED',
        source_timestamp=extra_fill.source_timestamp,
        source_timestamp_valid=True,
        fill_id=8,
        fill_id_valid=True,
        value_names=['cluster_id', 'revision'],
        values=[43.0, 1.0],
    )
    stage_a, cardinality, evidence, error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events + [(13, extra_event)],
            fills + [(13, extra_fill)],
        )
    )
    assert error is None
    assert stage_a is True
    assert cardinality is False
    assert evidence['unassigned_cluster_ids'] == [43]


def test_counted_stage_requires_direct_recovery_ranked_goal_then_near_sample():
    """Keep controller ranking causally ahead of evaluator-only proximity."""
    resolved = _v8_counted_resolved()
    states, events, fills = _counted_staged_records()
    stage_a, cardinality, stage_evidence, stage_error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events,
            fills,
        )
    )
    ranked, ranked_evidence, ranked_error = runner._ranked_goal_evidence(
        resolved,
        events + [(12, _ranked_goal_message())],
        stage_evidence,
    )
    proximity = runner._post_recovery_global_proximity(
        resolved,
        stage_a,
        stage_evidence,
        [
            (11, _odom_message(3.5, 3.5)),
            (13, _odom_message(3.2, 3.2)),
        ],
        minimum_bag_stamp=ranked_evidence['event_bag_stamp'],
    )

    assert stage_error is None
    assert stage_a is True
    assert cardinality is True
    assert stage_evidence['accepted_state_paths'] == [[
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'SEARCH',
    ]]
    assert ranked_error is None
    assert ranked is True
    assert ranked_evidence['candidate_ordinal'] == 2.0
    assert ranked_evidence['strict_separation_margin'] == 5.0
    assert proximity[2] is None
    assert proximity[0] is True
    assert proximity[1]['sample_bag_stamp'] == 13
    assert proximity[1]['minimum_bag_stamp'] == 12
    ranked_without_proximity = runner._post_recovery_global_proximity(
        resolved,
        stage_a,
        stage_evidence,
        [(13, _odom_message(2.5, 2.5))],
        minimum_bag_stamp=ranked_evidence['event_bag_stamp'],
    )
    assert ranked_without_proximity[0] is False
    assert ranked_without_proximity[2] is None

    missing_rank, missing_evidence, missing_error = (
        runner._ranked_goal_evidence(
            resolved,
            events,
            stage_evidence,
        )
    )
    assert missing_error is None
    assert missing_rank is False
    assert 'no valid' in missing_evidence['reason']

    ambiguous_rank = runner._ranked_goal_evidence(
        resolved,
        events + [(
            12,
            _ranked_goal_message(
                candidate_upper=-4.0,
                comparison_lower=-5.0,
                margin=-1.0,
            ),
        )],
        stage_evidence,
    )
    assert ambiguous_rank[0] is False
    assert ambiguous_rank[1]['invalid_ranked_goal_event_count'] == 1


def test_counted_stage_accepts_versioned_outward_assist_without_redesign():
    """Recognize direct repulse-to-assist as one counted Stage A episode."""
    resolved = _v8_1_counted_resolved()
    states, events, fills = _counted_assisted_staged_records()

    stage_a, cardinality, evidence, error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events,
            fills,
        )
    )

    assert error is None
    assert stage_a is True
    assert cardinality is True
    assert evidence['completed_episode_count'] == 1
    assert evidence['episodes'][0]['state_path'] == [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'ESCAPE_ASSIST',
        'SEARCH',
    ]
    assert 'DESIGN_OR_MERGE_FILL' not in (
        evidence['episodes'][0]['state_path'][3:]
    )


def test_verified_trap_stage_a_reports_but_does_not_gate_local_distance():
    states, events, fills = _staged_records()
    events[0][1].values = [1.70, 1.80]
    fills[0][1].center_x = 1.72
    fills[0][1].center_y = 1.82

    legacy_stage, legacy_cardinality, unused_evidence, error = (
        runner._staged_recovery_evidence(
            _v5_staged_resolved(),
            states,
            events,
            fills,
        )
    )
    trap_stage, trap_cardinality, evidence, trap_error = (
        runner._staged_recovery_evidence(
            _v6_staged_resolved(),
            states,
            events,
            fills,
        )
    )

    assert error is None
    assert legacy_stage is False
    assert legacy_cardinality is False
    assert trap_error is None
    assert trap_stage is True
    assert trap_cardinality is True
    assignment = evidence['assignments'][0]
    assert evidence['local_association_mode'] == 'verified_trap'
    assert assignment['convergence_to_local_m'] > 0.60
    assert assignment['declared_local_distance_gate_applied'] is False
    assert assignment['declared_local_distance_gate_passed'] is False
    assert assignment['nearest_declared_local_source_id'] == 'local'
    assert assignment['nearest_declared_local_m'] == pytest.approx(
        assignment['convergence_to_local_m']
    )


def test_verified_trap_stage_a_requires_exact_cluster_cardinality():
    resolved = _v6_staged_resolved()
    states, events, fills = _staged_records()
    extra_fill = _fill_message(
        fill_id=8,
        cluster_id=43,
        center=(2.0, 2.0),
    )
    extra_event = _event_message(
        'FILL_CREATED',
        source_timestamp=extra_fill.source_timestamp,
        source_timestamp_valid=True,
        fill_id=8,
        fill_id_valid=True,
        value_names=['cluster_id', 'revision'],
        values=[43.0, 1.0],
    )

    stage_a, cardinality, evidence, error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events + [(13, extra_event)],
            fills + [(13, extra_fill)],
        )
    )

    assert error is None
    assert cardinality is False
    assert stage_a is False
    assert evidence['unassigned_cluster_ids'] == [43]


def test_m3_approach_and_primary_select_distinct_first_samples():
    """Report approach first while retaining the stricter primary sample."""
    resolved = expand_suite(load_suite(M3_SPATIAL_SUITE))[0][0]
    stage_a_evidence = {'stage_a_completion_stamp': 10}
    odometry = [
        (9, _odom_message(3.5, 3.5)),
        (11, _odom_message(3.5, 2.35)),
        (12, _odom_message(3.5, 2.55)),
    ]

    approach = runner._post_recovery_global_proximity(
        resolved,
        True,
        stage_a_evidence,
        odometry,
        radius_key='global_approach_radius_m',
    )
    primary = runner._post_recovery_global_proximity(
        resolved,
        True,
        stage_a_evidence,
        odometry,
    )

    assert approach[0] is True
    assert approach[2] is None
    assert approach[1]['sample_bag_stamp'] == 11
    assert approach[1]['distance_m'] == pytest.approx(1.15)
    assert approach[1]['proximity_radius_m'] == 1.20
    assert primary[0] is True
    assert primary[2] is None
    assert primary[1]['sample_bag_stamp'] == 12
    assert primary[1]['distance_m'] == pytest.approx(0.95)
    assert primary[1]['proximity_radius_m'] == 1.00


def test_m3_approach_rejects_collision_before_sample():
    """Scope the diagnostic to collision-free evidence before its sample."""
    ground = SimpleNamespace(
        states=[SimpleNamespace(
            collision1_name='ground_plane::link::collision',
            collision2_name='burger::base_footprint::collision',
        )],
    )
    wall = SimpleNamespace(
        states=[SimpleNamespace(
            collision1_name='east_wall::link::collision',
            collision2_name='burger::base_footprint::collision',
        )],
    )
    evidence = {'sample_bag_stamp': 12}

    assert runner._collision_before_sample(
        [(10, ground), (13, wall)],
        evidence,
    ) is False
    assert runner._collision_before_sample(
        [(10, ground), (11, wall)],
        evidence,
    ) is True


def test_staged_recovery_accepts_legal_assisted_path():
    """Count the redesign-assisted topology as one completed recovery."""
    resolved = _v5_staged_resolved()
    states, events, fills = _assisted_staged_records()

    stage_a, cardinality, evidence, error = (
        runner._staged_recovery_evidence(
            resolved,
            states,
            events,
            fills,
        )
    )

    assert error is None
    assert stage_a is True
    assert cardinality is True
    assert evidence['completed_episode_count'] == 1
    assert evidence['episodes'][0]['state_path'] == [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_ASSIST',
        'RECENTER',
        'SEARCH',
    ]
    assert evidence['episodes'][0]['state_path'] in (
        evidence['accepted_state_paths']
    )

    expectations = {
        'required_state_path': evidence['accepted_state_paths'][0],
        'required_state_paths': evidence['accepted_state_paths'],
    }
    observed_states = [
        message.state_name for unused_stamp, message in states
    ]
    controller = runner._controller_evidence(
        expectations,
        observed_states,
        [],
    )
    assert controller['required_state_path'] is True


def test_staged_classification_retains_stage_a_when_global_stop_fails():
    """Keep Stage A visible while Stage B and combined result fail."""
    resolved = _v5_staged_resolved()
    base_outcomes = runner._unavailable_outcomes('unused')
    base_outcomes.update({
        'readiness_interval_available': True,
        'local_recovery_stage_passed': True,
        'local_recovery_stage': {'completed_episode_count': 1},
        'fill_cardinality_passed': True,
        'post_recovery_global_proximity_passed': True,
        'post_recovery_global_proximity': {'distance_m': 0.20},
        'collision_expectation_passed': True,
        'outcome_error': None,
    })
    common = {
        'resolved': resolved,
        'completeness': {'passed': True},
        'cleanup': {'passed': True},
        'outcomes': base_outcomes,
        'metadata': {},
        'run_directory_available': True,
    }

    missed_stop = classify_result(
        process_result={
            'timed_out': False,
            'return_code': 0,
            'graceful_global_proximity_stop': False,
        },
        **common,
    )
    assert missed_stop['staged_results'][
        'stage_a_local_recovery'
    ]['passed'] is True
    assert missed_stop['staged_results'][
        'stage_b_post_recovery_global_proximity'
    ]['passed'] is False
    assert missed_stop['staged_results']['combined']['passed'] is False

    stopped = classify_result(
        process_result={
            'timed_out': False,
            'return_code': 0,
            'graceful_global_proximity_stop': True,
        },
        **common,
    )
    assert stopped['staged_results'][
        'stage_b_post_recovery_global_proximity'
    ]['passed'] is True
    assert stopped['staged_results']['combined']['passed'] is True
    assert 'global_region_approach' not in stopped['staged_results']


def test_m3_approach_diagnostic_cannot_rescue_or_fail_combined_result():
    """Keep the 1.20 m observation outside all primary predicates."""
    resolved = expand_suite(load_suite(M3_SPATIAL_SUITE))[0][0]
    outcomes = runner._unavailable_outcomes('unused')
    outcomes.update({
        'readiness_interval_available': True,
        'required_state_path_passed': True,
        'required_events_passed': True,
        'forbidden_states_absent': True,
        'forbidden_events_absent': True,
        'local_recovery_stage_passed': True,
        'local_recovery_stage': {'completed_episode_count': 1},
        'fill_cardinality_passed': True,
        'post_recovery_global_proximity_passed': True,
        'post_recovery_global_proximity': {'distance_m': 0.95},
        'post_recovery_global_approach_passed': False,
        'post_recovery_global_approach': {
            'reason': 'collision before approach',
        },
        'collision_expectation_passed': True,
        'result_scopes': {
            'full_lifecycle': {
                'anchor_observed': True,
                'boundary_observed': None,
                'predicate_results': {},
            },
        },
        'outcome_error': None,
    })
    process_result = {
        'timed_out': False,
        'return_code': 0,
        'graceful_global_proximity_stop': True,
        'global_approach_observed_live': True,
    }

    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        process_result,
        metadata={},
        run_directory_available=True,
    )

    assert classification['passed'] is True
    diagnostic = classification['staged_results'][
        'global_region_approach'
    ]
    assert diagnostic['passed'] is False
    assert diagnostic['observed_live'] is True
    assert 'post_recovery_global_approach' not in (
        classification['required_predicates']
    )


def test_schema_v6_closer_diagnostic_cannot_fail_primary_stage_b():
    resolved = _v6_staged_resolved()
    outcomes = runner._unavailable_outcomes('unused')
    outcomes.update({
        'readiness_interval_available': True,
        'local_recovery_stage_passed': True,
        'local_recovery_stage': {'completed_episode_count': 1},
        'fill_cardinality_passed': True,
        'post_recovery_global_proximity_passed': True,
        'post_recovery_global_proximity': {'distance_m': 1.10},
        'post_recovery_global_closer_passed': False,
        'post_recovery_global_closer': {
            'reason': 'no post-Stage-A sample reached 1.00 m',
        },
        'collision_expectation_passed': True,
        'outcome_error': None,
    })

    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        {
            'timed_out': False,
            'return_code': 0,
            'graceful_global_proximity_stop': True,
            'global_closer_observed_live': False,
        },
        metadata={},
        run_directory_available=True,
    )

    assert classification['passed'] is True
    diagnostic = classification['staged_results'][
        'global_closer_diagnostic'
    ]
    assert diagnostic == {
        'passed': False,
        'observed_live': False,
        'evidence': {
            'reason': 'no post-Stage-A sample reached 1.00 m',
        },
        'gating': False,
    }
    assert 'post_recovery_global_closer' not in (
        classification['required_predicates']
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


@pytest.mark.parametrize(
    ('collision_stamp', 'approach_passed'),
    [(12.5, False), (13.5, True)],
)
def test_m3_bag_report_scopes_collision_to_approach_sample(
    monkeypatch,
    tmp_path,
    collision_stamp,
    approach_passed,
):
    """Reject only a diagnostic whose first sample follows a collision."""
    states, events, fills = _staged_records()
    records = [
        (
            '/gesc_gaussian/recording_ready',
            SimpleNamespace(data=True),
            0,
        ),
    ]
    records.extend(
        ('/gesc_gaussian/algorithm_state', message, stamp)
        for stamp, message in states
    )
    records.extend(
        ('/gesc_gaussian/algorithm_events', message, stamp)
        for stamp, message in events
    )
    records.extend(
        ('/gesc_gaussian/gaussian_fills', message, stamp)
        for stamp, message in fills
    )
    records.extend([
        (
            '/gesc_gaussian/simulation/contacts',
            SimpleNamespace(states=[SimpleNamespace(
                collision1_name='east_wall::link::collision',
                collision2_name='burger::base_footprint::collision',
            )]),
            collision_stamp,
        ),
        ('/odom', _odom_message(3.5, 2.35), 13),
        ('/odom', _odom_message(3.5, 2.55), 14),
        (
            '/gesc_gaussian/recording_ready',
            SimpleNamespace(data=False),
            15,
        ),
    ])

    class FakeReader:
        def __init__(self):
            self.records = sorted(records, key=lambda item: item[2])

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
    resolved = expand_suite(load_suite(M3_SPATIAL_SUITE))[0][0]

    outcomes = runner._bag_outcomes(tmp_path, resolved)

    assert outcomes['local_recovery_stage_passed'] is True
    assert outcomes[
        'post_recovery_global_approach_passed'
    ] is approach_passed
    assert outcomes['post_recovery_global_proximity_passed'] is False
    if approach_passed:
        assert outcomes['post_recovery_global_approach'][
            'sample_bag_stamp'
        ] == 13
    else:
        assert outcomes['post_recovery_global_approach'][
            'collision_before_approach'
        ] is True


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


@pytest.mark.parametrize(
    ('assisted', 'approach_diagnostic'),
    [(False, False), (True, False), (False, True)],
)
def test_live_global_stop_waits_for_stage_a_cardinality_and_near_odom(
    monkeypatch,
    assisted,
    approach_diagnostic,
):
    """Stop after either legal recovery path and a near odometry sample."""
    callbacks = {}
    dispatched = []
    executor_events = []
    signals = []
    wait_timeouts = []
    private_context = object()
    resolved = _v5_staged_resolved()
    if approach_diagnostic:
        resolved['success']['staged_recovery'].update({
            'global_proximity_radius_m': 1.00,
            'global_approach_radius_m': 1.20,
        })

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
            self.pid = 7321
            self.returncode = None
            stdout.write('global proximity test\n')

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            wait_timeouts.append(timeout)
            self.returncode = 0
            return 0

    states, events, fills = (
        _assisted_staged_records() if assisted else _staged_records()
    )
    timed_messages = [
        (
            stamp,
            '/gesc_gaussian/algorithm_state',
            message,
        )
        for stamp, message in states
    ]
    timed_messages.extend(
        (
            stamp,
            '/gesc_gaussian/algorithm_events',
            message,
        )
        for stamp, message in events
    )
    timed_messages.extend(
        (
            stamp,
            '/gesc_gaussian/gaussian_fills',
            message,
        )
        for stamp, message in fills
    )
    sequence = [
        (topic, message)
        for unused_stamp, topic, message in sorted(timed_messages)
    ]
    if approach_diagnostic:
        sequence.extend([
            ('/odom', _odom_message(3.5, 2.35)),
            ('/odom', _odom_message(3.5, 2.55)),
        ])
    else:
        sequence.extend([
            ('/odom', _odom_message(2.5, 2.5)),
            ('/odom', _odom_message(3.30, 3.30)),
        ])

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
        staged_recovery=resolved,
    )

    assert sequence == []
    assert dispatched[-2:] == ['/odom', '/odom']
    assert signals == [(7321, runner.signal.SIGINT)]
    assert wait_timeouts == [
        1.0 + runner.BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
    ]
    assert result['stage_a_observed_live'] is True
    assert result['fill_cardinality_observed_live'] is True
    assert result['graceful_global_proximity_stop'] is True
    expected_primary_distance = (
        0.95 if approach_diagnostic
        else runner.math.hypot(0.20, 0.20)
    )
    assert result['global_proximity_sample_live'][
        'distance_m'
    ] == pytest.approx(expected_primary_distance)
    if approach_diagnostic:
        assert result['global_approach_observed_live'] is True
        assert result['global_approach_sample_live'][
            'distance_m'
        ] == pytest.approx(1.15)
    else:
        assert 'global_approach_observed_live' not in result
        assert 'global_approach_sample_live' not in result
    assert result['stdout'] == 'global proximity test\n'
    assert executor_events == ['created', 'added', 'removed', 'shutdown']


def test_v8_live_stop_requires_ranked_goal_and_later_near_odom(
    monkeypatch,
):
    """Do not let evaluator proximity create a controller success."""
    callbacks = {}
    dispatched = []
    executor_events = []
    signals = []
    wait_timeouts = []
    private_context = object()
    resolved = _v8_counted_resolved()

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
            del command
            self.stdout = stdout
            self.pid = 8521
            self.returncode = None
            stdout.write('counted ranked-goal stop test\n')

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            wait_timeouts.append(timeout)
            self.returncode = 0
            return 0

    states, events, fills = _counted_staged_records()
    timed_messages = [
        (stamp, '/gesc_gaussian/algorithm_state', message)
        for stamp, message in states
    ]
    timed_messages.extend(
        (stamp, '/gesc_gaussian/algorithm_events', message)
        for stamp, message in events
    )
    timed_messages.extend(
        (stamp, '/gesc_gaussian/gaussian_fills', message)
        for stamp, message in fills
    )
    timed_messages.extend([
        (11, '/odom', _odom_message(3.5, 3.5, stamp_sec=100.0)),
        (12, '/gesc_gaussian/algorithm_state', _state_message(
            'VERIFY_EXTREMUM'
        )),
        (13, '/gesc_gaussian/algorithm_events', _event_message(
            'CONVERGENCE_CONFIRMED',
            source_timestamp=20.0,
            source_timestamp_valid=True,
            value_names=['fill_center_x_m', 'fill_center_y_m'],
            values=[3.45, 3.45],
        )),
        (14, '/gesc_gaussian/algorithm_state', _state_message('GOAL_HOLD')),
        (15, '/gesc_gaussian/algorithm_events', _ranked_goal_message()),
        (16, '/odom', _odom_message(3.2, 3.2, stamp_sec=101.0)),
    ])
    sequence = [
        (topic, message)
        for unused_stamp, topic, message in sorted(timed_messages)
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
        staged_recovery=resolved,
    )

    assert sequence == []
    assert dispatched.count('/odom') == 2
    assert dispatched[-1] == '/odom'
    assert signals == [(8521, runner.signal.SIGINT)]
    assert wait_timeouts == [
        1.0 + runner.BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
    ]
    assert result['stage_a_observed_live'] is True
    assert result['fill_cardinality_observed_live'] is True
    assert result['controller_ranked_goal_observed_live'] is True
    assert result['graceful_global_proximity_stop'] is True
    sample = result['global_proximity_sample_live']
    assert sample['distance_m'] == pytest.approx(
        runner.math.hypot(0.3, 0.3)
    )
    assert sample['controller_ranked_goal_required'] is True
    assert sample['callback_sequence'] > (
        sample['controller_ranked_goal_sequence']
    )
    assert result['stdout'] == 'counted ranked-goal stop test\n'
    assert executor_events == ['created', 'added', 'removed', 'shutdown']


@pytest.mark.parametrize(
    ('final_position', 'expect_proximity'),
    [
        ((2.1, 2.0), False),
        ((3.3, 3.3), True),
    ],
    ids=['budget_expires', 'global_wins_at_budget_boundary'],
)
def test_schema_v7_live_post_stage_a_budget_and_proximity_precedence(
    monkeypatch,
    final_position,
    expect_proximity,
):
    """Make global proximity win at the exact Stage B budget boundary."""
    callbacks = {}
    signals = []
    wait_timeouts = []
    executor_events = []
    private_context = object()
    resolved = _v6_staged_resolved()
    resolved['schema_version'] = 7
    resolved['success']['staged_recovery'][
        'post_stage_a_timeout_sec'
    ] = 120.0

    class FakeNode:
        def create_subscription(
            self, unused_type, topic, callback, unused_depth
        ):
            callbacks[topic] = callback
            return object()

        def destroy_node(self):
            return None

    node = FakeNode()

    class FakeProcess:
        def __init__(self, command, stdout, **unused_kwargs):
            del command
            self.stdout = stdout
            self.pid = 8123
            self.returncode = None
            stdout.write('post-stage-a timeout test\n')

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            wait_timeouts.append(timeout)
            self.returncode = 0
            return 0

    states, events, fills = _staged_records()
    timed_messages = [
        (stamp, '/gesc_gaussian/algorithm_state', message)
        for stamp, message in states
    ]
    timed_messages.extend(
        (stamp, '/gesc_gaussian/algorithm_events', message)
        for stamp, message in events
    )
    timed_messages.extend(
        (stamp, '/gesc_gaussian/gaussian_fills', message)
        for stamp, message in fills
    )
    sequence = [
        (topic, message)
        for unused_stamp, topic, message in sorted(timed_messages)
    ]
    sequence.extend([
        ('/odom', _odom_message(2.0, 2.0, stamp_sec=300.0)),
        (
            '/odom',
            _odom_message(
                final_position[0],
                final_position[1],
                stamp_sec=420.0,
            ),
        ),
    ])

    def spin_once(timeout_sec):
        del timeout_sec
        topic, message = sequence.pop(0)
        callbacks[topic](message)

    monkeypatch.setattr(
        runner.rclpy.context, 'Context', lambda: private_context
    )
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy, 'create_node', lambda *args, **kwargs: node
    )
    _install_boundary_executor(
        monkeypatch,
        private_context,
        node,
        spin_once,
        executor_events,
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
        staged_recovery=resolved,
    )

    assert sequence == []
    assert signals == [(8123, runner.signal.SIGINT)]
    assert wait_timeouts == [
        1.0 + runner.BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
    ]
    assert result['timed_out'] is False
    assert (
        result['graceful_global_proximity_stop'] is expect_proximity
    )
    assert (
        result['graceful_post_stage_a_timeout_stop']
        is (not expect_proximity)
    )
    if expect_proximity:
        assert result['global_proximity_sample_live'][
            'sample_sim_sec'
        ] == pytest.approx(420.0)
        assert result['post_stage_a_timeout_sample_live'] is None
        assert executor_events == [
            'created', 'added', 'removed', 'shutdown'
        ]
        return

    sample = result['post_stage_a_timeout_sample_live']
    assert sample['started_sim_sec'] == pytest.approx(300.0)
    assert sample['elapsed_sim_sec'] == pytest.approx(120.0)
    assert sample['timeout_sec'] == pytest.approx(120.0)
    assert executor_events == ['created', 'added', 'removed', 'shutdown']

    outcomes = runner._unavailable_outcomes('unused')
    outcomes.update({
        'readiness_interval_available': True,
        'local_recovery_stage_passed': True,
        'local_recovery_stage': {'completed_episode_count': 1},
        'fill_cardinality_passed': True,
        'post_recovery_global_proximity_passed': False,
        'post_recovery_global_proximity': {
            'reason': 'post-Stage-A budget elapsed',
        },
        'collision_expectation_passed': True,
        'outcome_error': None,
    })
    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        result,
        metadata={},
        run_directory_available=True,
    )
    assert classification['infrastructure_status'] == 'completed'
    assert classification['passed'] is False
    assert classification['staged_results'][
        'stage_b_time_budget'
    ]['expired'] is True


@pytest.mark.parametrize(
    'stage_a_completes_at_boundary',
    [False, True],
    ids=['stage_a_timeout', 'stage_a_wins_and_reserves_stage_b'],
)
def test_schema_v7_live_stage_a_budget_and_exact_boundary_precedence(
    monkeypatch,
    stage_a_completes_at_boundary,
):
    callbacks = {}
    signals = []
    wait_timeouts = []
    executor_events = []
    private_context = object()
    resolved = _v6_staged_resolved()
    resolved['schema_version'] = 7
    resolved['success']['staged_recovery'].update({
        'stage_a_timeout_sec': 480.0,
        'post_stage_a_timeout_sec': 120.0,
    })

    class FakeNode:
        def create_subscription(
            self, unused_type, topic, callback, unused_depth
        ):
            callbacks[topic] = callback
            return object()

        def destroy_node(self):
            return None

    node = FakeNode()

    class FakeProcess:
        def __init__(self, command, stdout, **unused_kwargs):
            del command
            self.pid = 9123
            self.returncode = None
            stdout.write('stage-a timeout test\n')

        def poll(self):
            return self.returncode

        def wait(self, timeout=None):
            wait_timeouts.append(timeout)
            self.returncode = 0
            return 0

    sequence = [
        ('/odom', _odom_message(2.0, 2.0, stamp_sec=100.0)),
    ]
    if stage_a_completes_at_boundary:
        states, events, fills = _staged_records()
        timed_messages = [
            (stamp, '/gesc_gaussian/algorithm_state', message)
            for stamp, message in states
        ]
        timed_messages.extend(
            (stamp, '/gesc_gaussian/algorithm_events', message)
            for stamp, message in events
        )
        timed_messages.extend(
            (stamp, '/gesc_gaussian/gaussian_fills', message)
            for stamp, message in fills
        )
        sequence.extend(
            (topic, message)
            for unused_stamp, topic, message in sorted(timed_messages)
        )
    sequence.append(
        ('/odom', _odom_message(2.0, 2.0, stamp_sec=580.0))
    )
    if stage_a_completes_at_boundary:
        sequence.append(
            ('/odom', _odom_message(3.3, 3.3, stamp_sec=700.0))
        )

    def spin_once(timeout_sec):
        del timeout_sec
        topic, message = sequence.pop(0)
        callbacks[topic](message)

    monkeypatch.setattr(
        runner.rclpy.context, 'Context', lambda: private_context
    )
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(
        runner.rclpy, 'create_node', lambda *args, **kwargs: node
    )
    _install_boundary_executor(
        monkeypatch,
        private_context,
        node,
        spin_once,
        executor_events,
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
        staged_recovery=resolved,
    )

    assert sequence == []
    assert signals == [(9123, runner.signal.SIGINT)]
    assert wait_timeouts == [
        1.0 + runner.BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
    ]
    assert result['stage_a_monitor_started_sim_sec_live'] == 100.0
    assert result['stage_a_latest_sim_sec_live'] == 580.0
    assert executor_events == ['created', 'added', 'removed', 'shutdown']

    if stage_a_completes_at_boundary:
        assert result['stage_a_observed_live'] is True
        assert result['fill_cardinality_observed_live'] is True
        assert result['graceful_stage_a_timeout_stop'] is False
        assert result['stage_a_timeout_sample_live'] is None
        assert result['post_stage_a_started_sim_sec_live'] == 580.0
        assert result['post_stage_a_latest_sim_sec_live'] == 700.0
        assert result['graceful_global_proximity_stop'] is True
        assert result['graceful_post_stage_a_timeout_stop'] is False
        return

    assert result['stage_a_observed_live'] is False
    assert result['fill_cardinality_observed_live'] is False
    assert result['graceful_stage_a_timeout_stop'] is True
    assert result['graceful_global_proximity_stop'] is False
    sample = result['stage_a_timeout_sample_live']
    assert sample['started_sim_sec'] == pytest.approx(100.0)
    assert sample['elapsed_sim_sec'] == pytest.approx(480.0)
    assert sample['timeout_sec'] == pytest.approx(480.0)

    outcomes = runner._unavailable_outcomes('unused')
    outcomes.update({
        'readiness_interval_available': True,
        'local_recovery_stage_passed': False,
        'fill_cardinality_passed': False,
        'post_recovery_global_proximity_passed': False,
        'collision_expectation_passed': True,
        'outcome_error': None,
    })
    classification = classify_result(
        resolved,
        {'passed': True},
        {'passed': True},
        outcomes,
        result,
        metadata={},
        run_directory_available=True,
    )
    assert classification['passed'] is False
    stage_a_budget = classification['staged_results'][
        'stage_a_time_budget'
    ]
    assert stage_a_budget['expired'] is True
    assert stage_a_budget['timeout_sec'] == 480.0


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
