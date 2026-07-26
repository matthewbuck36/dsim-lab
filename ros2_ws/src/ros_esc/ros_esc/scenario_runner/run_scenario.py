#!/usr/bin/env python3

"""Execute deterministic serial Gazebo scenarios through Phase 05 recording."""

import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

from gazebo_msgs.msg import ContactsState
from nav_msgs.msg import Odometry

import rclpy
from rclpy.serialization import deserialize_message

from ros_esc.experiment_recording.record_run import (
    atomic_yaml,
    validate_run_id,
)

from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
)

import rosbag2_py

from std_msgs.msg import Bool

import yaml

from .scenario_schema import expand_suite, load_suite


def _repository_root():
    """Resolve the live checkout without assuming its module layout."""
    try:
        root = Path(subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            check=True, capture_output=True, text=True, timeout=5.0,
        ).stdout.strip()).resolve()
        if (root / 'ros2_ws/src/ros_esc').is_dir():
            return root
    except (OSError, subprocess.SubprocessError):
        pass
    for parent in Path(__file__).resolve().parents:
        if (parent / 'ros2_ws/src/ros_esc').is_dir():
            return parent
    conventional = Path.home() / 'dsim-lab'
    if (conventional / 'ros2_ws/src/ros_esc').is_dir():
        return conventional
    raise RuntimeError(
        'cannot locate dsim-lab; run inside the checkout or set up ~/dsim-lab'
    )


REPOSITORY_ROOT = _repository_root()
ROS_ESC_ROOT = REPOSITORY_ROOT / 'ros2_ws/src/ros_esc'
MULTI_LIGHT_COST = (
    ROS_ESC_ROOT
    / 'paper_recreations/heavy_ball_PDE_ESC/cost_function/'
    'multi_light_source_photoresistor.json'
)
GESC_CONTROLLER = (
    ROS_ESC_ROOT
    / 'ros_esc/controller_node/controller_config_files/turtlebot_vehicle/'
    'gradient_methods/gesc_controller_full_rotation_voltage.json'
)
GESC_FILTER = (
    ROS_ESC_ROOT
    / 'ros_esc/filter_node/filter_config_files/turtlebot_vehicle/'
    'gradient_methods/gesc_filter_full_rotation.json'
)
VALIDATION_WORLD = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/turtlebot3_rotating_sensor/worlds/'
    'gesc_gaussian_validation.world'
)
STATE_NAMES = {
    value: name.removeprefix('STATE_')
    for name, value in vars(AlgorithmState).items()
    if name.startswith('STATE_') and isinstance(value, int)
}
EVENT_NAMES = {
    value: name.removeprefix('EVENT_')
    for name, value in vars(AlgorithmEvent).items()
    if name.startswith('EVENT_') and isinstance(value, int)
}
RUN_ID_SAFE = re.compile('[^A-Za-z0-9._-]+')


def _utc_now():
    return dt.datetime.now(dt.timezone.utc)


def _utc_text(value=None):
    return (value or _utc_now()).isoformat().replace('+00:00', 'Z')


def generate_scenario_run_id(resolved, now=None, unique=None):
    """Generate one unique Phase 05-compatible scenario run ID."""
    now = now or _utc_now()
    unique = unique or uuid.uuid4().hex[:8]
    slug = (
        f"{resolved['suite_id']}-{resolved['case_id']}-"
        f"{resolved['profile']}-{resolved['case_key'][:10]}"
    )
    slug = RUN_ID_SAFE.sub('-', slug).strip('-._')[:80]
    stamp = now.strftime('%Y%m%dT%H%M%S%fZ')
    return validate_run_id(f'{stamp}_simulation_{slug}_{unique}')


def _bool_text(value):
    return 'True' if value else 'False'


def _launch_value(value):
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def build_launch_command(resolved, cost_path=None, gui=False):
    """Build the exact existing Gazebo launch argv without shell evaluation."""
    ablations = resolved['algorithm']['ablations']
    bounds = resolved['bounds_m']
    center = resolved['room_center_m']
    start = resolved['start']
    disturbances = resolved['disturbances']
    sensor_delayed = disturbances['sensor_delay_sec'] > 0.0
    pose_delayed = disturbances['pose_delay_sec'] > 0.0
    disturbance_enabled = sensor_delayed or pose_delayed
    contact_probe_enabled = (
        resolved['success'].get('collision_expected') is True
    )
    arguments = {
        'gazebo_gui': gui,
        'gazebo_use_random_seed': True,
        'gazebo_random_seed': resolved['seed'],
        'algorithm_profile': resolved['profile'],
        'use_pde_extensions': True,
        'enable_observability': True,
        'recording_ready_required': True,
        'show_cost_surface_plot': False,
        'live_plot_mode': 'None',
        'cost_function_config_filepath': str(cost_path or MULTI_LIGHT_COST),
        'filter_config_filepath': str(GESC_FILTER),
        'controller_config_filepath': str(GESC_CONTROLLER),
        'init_x_position': start['x_m'],
        'init_y_position': start['y_m'],
        'init_yaw_angle': start['yaw_rad'],
        'number_of_lights': len(resolved['sources']),
        'room_bounds_x_min_m': bounds[0],
        'room_bounds_x_max_m': bounds[1],
        'room_bounds_y_min_m': bounds[2],
        'room_bounds_y_max_m': bounds[3],
        'room_center_x_m': center[0],
        'room_center_y_m': center[1],
        'escape_policy': (
            'conditional_gaussian_fill'
            if ablations['gaussian_fill_enabled'] else 'none'
        ),
        'modified_cost_enable_affine_bias': ablations[
            'affine_assist_enabled'
        ],
        'recenter_after_escape': ablations['recenter_enabled'],
        'gazebo_world': (
            str(VALIDATION_WORLD)
            if resolved['validation']['world'] else ''
        ),
        'simulation_contacts_enabled': resolved[
            'validation'
        ]['contacts_enabled'],
        'simulation_disturbance_enabled': disturbance_enabled,
        'simulation_validation_support_enabled': (
            disturbance_enabled or contact_probe_enabled
        ),
        'simulation_contact_probe_enabled': contact_probe_enabled,
        'simulation_sensor_delay_sec': disturbances['sensor_delay_sec'],
        'simulation_pose_delay_sec': disturbances['pose_delay_sec'],
        'algorithm_raw_cost_topic': (
            '/gesc_gaussian/simulation/raw_cost_delayed'
            if sensor_delayed else '/turtlebot3/cost_value_chatter'
        ),
        'algorithm_source_cost_topic': (
            '/gesc_gaussian/simulation/source_cost_delayed'
            if sensor_delayed else '/gesc_gaussian/source_cost'
        ),
        'algorithm_pose_topic': (
            '/gesc_gaussian/simulation/pose_delayed'
            if pose_delayed else '/odom'
        ),
        'gaussian_fill_pose_topic': (
            '/gesc_gaussian/simulation/pose_delayed'
            if pose_delayed else '/odom'
        ),
        'pde_cost_history_topic': (
            '/gesc_gaussian/simulation/raw_cost_delayed'
            if sensor_delayed else '/turtlebot3/cost_value_chatter'
        ),
    }
    if not resolved['validation']['world']:
        arguments.pop('gazebo_world')
    for index, source in enumerate(resolved['sources'], start=1):
        arguments.update({
            f'light_{index}_x': source['x_m'],
            f'light_{index}_y': source['y_m'],
            f'light_{index}_intensity_lumens': source[
                'relative_lumen_input'
            ],
        })
    arguments.update(resolved['algorithm']['launch_overrides'])
    command = [
        'ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml'
    ]
    command.extend(
        f'{name}:={_launch_value(value)}' for name, value in arguments.items()
    )
    return command


def build_metadata(resolved, operator, experiment_version, operator_notes):
    """Generate recording metadata from the same resolved launch object."""
    return {
        'schema_version': 1,
        'experiment_version': experiment_version,
        'operator': operator,
        'mode': 'simulation',
        'algorithm_profile': resolved['profile'],
        'scenario_id': (
            f"{resolved['suite_id']}.{resolved['case_id']}."
            f"{resolved['case_key'][:12]}"
        ),
        'random_seed': resolved['seed'],
        'environment': {
            'bounds_m': {
                'x_min': resolved['bounds_m'][0],
                'x_max': resolved['bounds_m'][1],
                'y_min': resolved['bounds_m'][2],
                'y_max': resolved['bounds_m'][3],
            },
            'room_center_m': {
                'x': resolved['room_center_m'][0],
                'y': resolved['room_center_m'][1],
            },
            'disturbances': resolved['disturbances'],
            'validation': resolved['validation'],
        },
        'robot_starting_pose': {
            'x_m': resolved['start']['x_m'],
            'y_m': resolved['start']['y_m'],
            'yaw_rad': resolved['start']['yaw_rad'],
        },
        'sources': [
            {
                'id': source['id'],
                'x_m': source['x_m'],
                'y_m': source['y_m'],
                'relative_lumen_input': source['relative_lumen_input'],
                'evaluation_role': source['evaluation_role'],
                **(
                    {'level': source['level']}
                    if 'level' in source else {}
                ),
            }
            for source in resolved['sources']
        ],
        'calibration': {
            'file': 'not_applicable_simulation',
            'source_score_definition': (
                'dimensionless simulator model-range normalization'
            ),
            'intensity_semantics': (
                'relative input scaled by reference_intensity_lumens; not lux'
            ),
        },
        'parameter_files': [
            str(MULTI_LIGHT_COST),
            str(GESC_FILTER),
            str(GESC_CONTROLLER),
        ],
        'human_intervention': False,
        'operator_notes': operator_notes,
        'scenario_runner': {
            'schema_version': resolved['schema_version'],
            'suite_id': resolved['suite_id'],
            'case_id': resolved['case_id'],
            'case_key': resolved['case_key'],
            'family': resolved['family'],
            'profile': resolved['profile'],
            'seed': resolved['seed'],
            'start': resolved['start'],
            'sources': resolved['sources'],
            'bounds_m': resolved['bounds_m'],
            'room_center_m': resolved['room_center_m'],
            'disturbances': resolved['disturbances'],
            'validation': resolved['validation'],
            'frozen_profile': resolved['frozen_profile'],
            'algorithm': resolved['algorithm'],
            'success': resolved['success'],
        },
    }


def build_record_command(
    resolved,
    run_id,
    metadata_path,
    runs_root,
    execution,
    launch_command,
):
    """Build exact Phase 05 recorder argv."""
    return [
        'ros2', 'run', 'ros_esc', 'record_run',
        '--mode', 'simulation',
        '--metadata-input', str(metadata_path),
        '--runs-root', str(runs_root),
        '--run-id', run_id,
        '--duration-sec', str(execution['run_timeout_sec']),
        '--preflight-timeout-sec', str(execution['preflight_timeout_sec']),
        '--target-exit-timeout-sec', str(execution['shutdown_grace_sec']),
        '--',
        *launch_command,
    ]


def resolved_noise_config(resolved, output_path):
    """Write exact cost JSON when seeded Uniform or Gaussian noise is used."""
    noise = resolved['disturbances']['sensor_noise']
    if noise['model'] == 'uniform' and noise['bound'] > 0.0:
        object_name = 'Uniform'
        parameters = {
            'bound': noise['bound'],
            'seed_num': resolved['seed'],
        }
    elif noise['model'] == 'gaussian' and noise.get('std_dev', 0.0) > 0.0:
        object_name = 'Gaussian'
        parameters = {
            'std_dev': noise['std_dev'],
            'seed_num': resolved['seed'],
        }
    else:
        return None
    document = json.loads(MULTI_LIGHT_COST.read_text(encoding='utf-8'))
    document['Noise'] = {
        'filepath': (
            '~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/'
            'cost_function_node/cost_function_objects/noise_objects.py'
        ),
        'object_name': object_name,
        'params': parameters,
    }
    output_path = Path(output_path)
    output_path.write_text(
        json.dumps(document, indent=2, allow_nan=False) + '\n',
        encoding='utf-8',
    )
    return output_path


def find_run_directory(runs_root, run_id):
    """Find an exact run ID independent of the UTC date directory."""
    matches = [
        path for path in Path(runs_root).glob(f'*/{run_id}')
        if path.is_dir() and path.name == run_id
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f'expected one run directory for {run_id}, found {len(matches)}'
        )
    return matches[0]


def ros_graph_nodes():
    """Return the current ROS node set without changing the graph."""
    try:
        rclpy.init(args=[])
        node = rclpy.create_node(
            f'phase06_graph_probe_{uuid.uuid4().hex[:8]}'
        )
        rclpy.spin_once(node, timeout_sec=0.25)
        names = {
            (
                f"{namespace.rstrip('/')}/{name}"
                if namespace != '/' else f'/{name}'
            )
            for name, namespace in node.get_node_names_and_namespaces()
            if name != node.get_name()
        }
        node.destroy_node()
        rclpy.try_shutdown()
        return names
    except Exception:
        if rclpy.ok():
            rclpy.try_shutdown()
        return set()


def session_processes(session_id):
    """Return live processes in the exact session created for one run."""
    try:
        output = subprocess.run(
            ['ps', '-eo', 'pid=,sid=,stat=,comm='],
            check=True, capture_output=True, text=True, timeout=5.0,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return [{'pid': None, 'error': 'process inspection failed'}]
    survivors = []
    for line in output.splitlines():
        fields = line.split(None, 3)
        if len(fields) != 4:
            continue
        pid, sid, state, command = fields
        if int(sid) == int(session_id) and not state.startswith('Z'):
            survivors.append({
                'pid': int(pid), 'session_id': int(sid),
                'state': state, 'command': command,
            })
    return survivors


def cleanup_evidence(baseline_nodes, session_id, settle_sec=5.0):
    """Wait for graph settling and report exact-node/process contamination."""
    deadline = time.monotonic() + settle_sec
    new_nodes = set()
    survivors = []
    while True:
        new_nodes = ros_graph_nodes() - set(baseline_nodes)
        survivors = session_processes(session_id)
        if not new_nodes and not survivors:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(0.25)
    return {
        'passed': not new_nodes and not survivors,
        'baseline_nodes': sorted(baseline_nodes),
        'remaining_new_nodes': sorted(new_nodes),
        'remaining_session_processes': survivors,
    }


def ensure_ros_daemon():
    """Start shared ros2cli discovery outside any per-run process session."""
    subprocess.run(
        ['ros2', 'daemon', 'start'],
        check=True, capture_output=True, text=True, timeout=15.0,
    )


def run_record_process(command, wall_timeout_sec, shutdown_grace_sec):
    """Run record_run with a wall timeout and scoped session escalation."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    timed_out = False
    try:
        output, _ = process.communicate(timeout=wall_timeout_sec)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGINT)
        except ProcessLookupError:
            pass
        try:
            output, _ = process.communicate(timeout=shutdown_grace_sec)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                output, _ = process.communicate(timeout=5.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                output, _ = process.communicate()
    return {
        'return_code': process.returncode,
        'timed_out': timed_out,
        'stdout': output,
        'session_id': process.pid,
    }


def _subsequence(required, observed):
    iterator = iter(observed)
    return all(
        any(item == expected for item in iterator)
        for expected in required
    )


def _first_verification_path(required, observed):
    """Match one contiguous path at the first observed verification entry."""
    if not required:
        return True
    try:
        required_verify = required.index('VERIFY_EXTREMUM')
        observed_verify = observed.index('VERIFY_EXTREMUM')
    except ValueError:
        return False
    start = observed_verify - required_verify
    if start < 0:
        return False
    return observed[start:start + len(required)] == required


def _canonical_state_sequence(messages):
    """Use the typed enum and reject contradictory free-form state names."""
    observed = []
    error = None
    for message in messages:
        if not message.state_valid:
            continue
        try:
            state_value = int(message.state)
        except (TypeError, ValueError):
            state_value = None
        canonical = STATE_NAMES.get(state_value)
        declared = str(message.state_name or '').strip().removeprefix(
            'STATE_'
        )
        if canonical is None:
            error = f'algorithm state contains unknown enum {message.state}'
            continue
        if canonical == 'UNAVAILABLE':
            error = 'valid algorithm state reports STATE_UNAVAILABLE'
        if declared and declared != canonical:
            error = (
                'algorithm state name/enum mismatch: '
                f'{declared} != {canonical}'
            )
        if not observed or canonical != observed[-1]:
            observed.append(canonical)
    return observed, error


def _canonical_event_sequence(messages):
    """Resolve event enums and reject unknown typed event values."""
    observed = []
    error = None
    for message in messages:
        try:
            event_value = int(message.event_type)
        except (TypeError, ValueError):
            event_value = None
        canonical = EVENT_NAMES.get(event_value)
        if canonical is None:
            error = f'algorithm event contains unknown enum {message.event_type}'
            continue
        if canonical == 'UNSPECIFIED':
            error = 'algorithm event reports EVENT_UNSPECIFIED'
        observed.append(canonical)
    return observed, error


def _unavailable_outcomes(reason, readiness_interval_available=False):
    """Return tri-state behavioral outcomes for invalid infrastructure."""
    return {
        'readiness_interval_available': readiness_interval_available,
        'observed_state_sequence': [],
        'observed_terminal_state': None,
        'observed_events': [],
        'controller_goal': 'unavailable',
        'simulation_ground_truth': 'unavailable',
        'final_position': None,
        'final_goal_distances_m': {},
        'required_state_path_passed': None,
        'required_state_sequence_passed': None,
        'required_event_sequence_passed': None,
        'required_events_passed': None,
        'forbidden_states_absent': None,
        'forbidden_events_absent': None,
        'expected_terminal_state_passed': None,
        'saturation_sample_count': None,
        'minimum_saturation_samples_passed': None,
        'collision_evidence_available': False,
        'collision_observed': None,
        'collision_expectation_passed': None,
        'outcome_error': reason,
    }


def _bag_outcomes(run_directory, resolved):
    bag_directory = Path(run_directory) / 'bag'
    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(
            uri=str(bag_directory), storage_id='sqlite3'
        ),
        rosbag2_py.ConverterOptions('', ''),
    )
    wanted = {
        '/gesc_gaussian/recording_ready': Bool,
        '/gesc_gaussian/algorithm_state': AlgorithmState,
        '/gesc_gaussian/algorithm_events': AlgorithmEvent,
        '/gesc_gaussian/control_diagnostics': ControlDiagnostics,
        '/odom': Odometry,
        '/gesc_gaussian/simulation/contacts': ContactsState,
    }
    records = {name: [] for name in wanted}
    while reader.has_next():
        topic, serialized, bag_stamp = reader.read_next()
        message_type = wanted.get(topic)
        if message_type is not None:
            records[topic].append(
                (bag_stamp, deserialize_message(serialized, message_type))
            )
    readiness = [
        (stamp, message.data)
        for stamp, message in records['/gesc_gaussian/recording_ready']
    ]
    first_true = next((stamp for stamp, value in readiness if value), None)
    first_false = next(
        (
            stamp for stamp, value in readiness
            if first_true is not None and stamp >= first_true and not value
        ),
        None,
    )
    if first_true is None:
        return _unavailable_outcomes(
            'no recorded true readiness interval',
            readiness_interval_available=False,
        )

    def inside(stamp):
        return (
            first_true is not None
            and stamp >= first_true
            and (first_false is None or stamp <= first_false)
        )

    states = [
        message for stamp, message
        in records['/gesc_gaussian/algorithm_state'] if inside(stamp)
    ]
    events = [
        message for stamp, message
        in records['/gesc_gaussian/algorithm_events'] if inside(stamp)
    ]
    diagnostics = [
        message for stamp, message
        in records['/gesc_gaussian/control_diagnostics'] if inside(stamp)
    ]
    odometry = [
        message for stamp, message in records['/odom'] if inside(stamp)
    ]
    contacts = [
        message for stamp, message
        in records['/gesc_gaussian/simulation/contacts'] if inside(stamp)
    ]
    collision_observed = any(
        state
        for message in contacts
        for state in message.states
        if (
            'ground_plane' not in state.collision1_name
            and 'ground_plane' not in state.collision2_name
        )
    )
    collision_expected = resolved['success'].get('collision_expected')
    observed_states, state_error = _canonical_state_sequence(states)
    observed_events, event_error = _canonical_event_sequence(events)
    saturation_samples = sum(
        1 for message in diagnostics if any(message.saturation_flags)
    )
    final_position = None
    outcome_error = state_error or event_error
    if odometry:
        final_x = float(odometry[-1].pose.pose.position.x)
        final_y = float(odometry[-1].pose.pose.position.y)
        if math.isfinite(final_x) and math.isfinite(final_y):
            final_position = {
                'x_m': final_x,
                'y_m': final_y,
            }
        else:
            outcome_error = outcome_error or (
                'terminal odometry contains a nonfinite position'
            )
    distances = {}
    if final_position:
        for source in resolved['sources']:
            if source['id'] in resolved['success']['ground_truth'][
                'goal_source_ids'
            ]:
                distance = math.hypot(
                    final_position['x_m'] - source['x_m'],
                    final_position['y_m'] - source['y_m'],
                )
                if not math.isfinite(distance):
                    distances = {}
                    outcome_error = outcome_error or (
                        'terminal goal distance is nonfinite'
                    )
                    break
                distances[source['id']] = distance
    controller_goal = 'not_applicable'
    if resolved['profile'] == 'robust_gaussian_v1':
        controller_goal = (
            'passed'
            if (
                'GOAL_REACHED' in observed_events
                and 'GOAL_HOLD' in observed_states
            )
            else 'failed'
        )
    goal_ids = resolved['success']['ground_truth']['goal_source_ids']
    ground_truth = 'not_applicable'
    if outcome_error is not None:
        ground_truth = 'unavailable'
    elif goal_ids:
        tolerance = resolved['success']['ground_truth'][
            'final_position_tolerance_m'
        ]
        ground_truth = (
            'passed'
            if distances and min(distances.values()) <= tolerance
            else 'failed'
        )
    controller_expectations = resolved['success']['controller']
    expected_terminal = controller_expectations.get(
        'expected_terminal_state'
    )
    terminal_ok = (
        expected_terminal is None
        or bool(observed_states)
        and observed_states[-1]
        == str(expected_terminal).removeprefix('STATE_')
    )
    required_states = [
        str(name).removeprefix('STATE_')
        for name in controller_expectations.get('required_state_sequence', [])
    ]
    required_state_path = [
        str(name).removeprefix('STATE_')
        for name in controller_expectations.get('required_state_path', [])
    ]
    required_events = [
        str(name).removeprefix('EVENT_')
        for name in controller_expectations.get('required_events', [])
    ]
    required_event_sequence = [
        str(name).removeprefix('EVENT_')
        for name in controller_expectations.get(
            'required_event_sequence', []
        )
    ]
    forbidden_states = [
        str(name).removeprefix('STATE_')
        for name in controller_expectations.get('forbidden_states', [])
    ]
    forbidden_events = [
        str(name).removeprefix('EVENT_')
        for name in controller_expectations.get('forbidden_events', [])
    ]
    return {
        'readiness_interval_available': first_true is not None,
        'observed_state_sequence': observed_states,
        'observed_terminal_state': (
            observed_states[-1] if observed_states else None
        ),
        'observed_events': observed_events,
        'controller_goal': controller_goal,
        'simulation_ground_truth': ground_truth,
        'final_position': final_position,
        'final_goal_distances_m': distances,
        'required_state_path_passed': _first_verification_path(
            required_state_path, observed_states
        ),
        'required_state_sequence_passed': _subsequence(
            required_states, observed_states
        ),
        'required_event_sequence_passed': _subsequence(
            required_event_sequence, observed_events
        ),
        'required_events_passed': all(
            event in observed_events for event in required_events
        ),
        'forbidden_states_absent': all(
            state not in observed_states for state in forbidden_states
        ),
        'forbidden_events_absent': all(
            event not in observed_events for event in forbidden_events
        ),
        'expected_terminal_state_passed': terminal_ok,
        'saturation_sample_count': saturation_samples,
        'minimum_saturation_samples_passed': (
            saturation_samples
            >= resolved['success']['minimum_saturation_samples']
        ),
        'collision_evidence_available': bool(contacts),
        'collision_observed': collision_observed,
        'collision_expectation_passed': (
            collision_expected is None
            or bool(contacts)
            and collision_observed is collision_expected
        ),
        'outcome_error': outcome_error,
    }


def classify_result(
    resolved,
    completeness,
    cleanup,
    outcomes,
    process_result,
    metadata=None,
    run_directory_available=None,
):
    """Evaluate explicit predicates while keeping outcomes separate."""

    def outcome_status(value):
        if value in (None, 'unavailable'):
            return None
        return value == 'passed'

    facts = {
        'recording_complete': bool(completeness.get('passed')),
        'cleanup_complete': bool(cleanup.get('passed')),
        'controller_goal': outcome_status(outcomes.get('controller_goal')),
        'ground_truth_goal': outcome_status(
            outcomes.get('simulation_ground_truth')
        ),
        'expected_terminal_state': outcomes.get(
            'expected_terminal_state_passed'
        ),
        'required_state_sequence': outcomes.get(
            'required_state_sequence_passed'
        ),
        'required_state_path': outcomes.get(
            'required_state_path_passed'
        ),
        'required_events': outcomes.get('required_events_passed'),
        'required_event_sequence': outcomes.get(
            'required_event_sequence_passed'
        ),
        'no_forbidden_states': outcomes.get(
            'forbidden_states_absent'
        ),
        'no_forbidden_events': outcomes.get(
            'forbidden_events_absent'
        ),
        'minimum_saturation_samples': outcomes.get(
            'minimum_saturation_samples_passed'
        ),
        'collision_expectation': outcomes.get(
            'collision_expectation_passed'
        ),
    }
    all_of = resolved['success']['all_of']
    passed = all(facts[name] is True for name in all_of)
    if run_directory_available is None:
        run_directory_available = bool(completeness)
    recording = (
        metadata.get('recording')
        if isinstance(metadata, dict)
        else None
    )
    metadata_no_readiness = (
        isinstance(recording, dict)
        and (
            recording.get('readiness_ever_true') is False
            or (
                'readiness_ever_true' not in recording
                and recording.get('status') == 'finalized'
                and not recording.get('ready_at_utc')
            )
        )
    )
    infrastructure_status = 'completed'
    infrastructure_reason = None
    failure_stage = None
    if process_result['timed_out']:
        infrastructure_status = 'wall_timeout'
    elif not run_directory_available:
        infrastructure_status = 'run_directory_missing'
    elif process_result['return_code'] not in (0, 1):
        infrastructure_status = 'runner_or_recorder_failure'
    elif (
        outcomes.get('readiness_interval_available') is False
        or metadata_no_readiness
    ):
        infrastructure_status = 'infrastructure_invalid'
        infrastructure_reason = (
            recording.get('run_error')
            if isinstance(recording, dict)
            else None
        ) or outcomes.get(
            'outcome_error',
            'no recorded true readiness interval',
        )
        failure_stage = (
            recording.get('failure_stage')
            if isinstance(recording, dict)
            else None
        )
    elif (
        isinstance(recording, dict)
        and recording.get('infrastructure_status') == 'runtime_failed'
    ):
        infrastructure_status = 'runtime_failed'
        infrastructure_reason = (
            recording.get('run_error') or 'recording runtime failed'
        )
        failure_stage = recording.get('failure_stage')
    elif outcomes.get('outcome_error'):
        infrastructure_status = 'evidence_extraction_failed'
        infrastructure_reason = outcomes['outcome_error']
    elif not completeness or completeness.get('passed') is not True:
        infrastructure_status = 'recording_evidence_invalid'
        infrastructure_reason = (
            'completeness.json is missing, unreadable, or failed'
        )
    elif not cleanup.get('passed'):
        infrastructure_status = 'cleanup_failed'
        infrastructure_reason = (
            'run-scoped ROS graph or process cleanup failed'
        )
    status = 'passed' if passed else 'failed'
    if infrastructure_status != 'completed':
        passed = False
        status = (
            'infrastructure_invalid'
            if infrastructure_status == 'infrastructure_invalid'
            else 'failed'
        )
    return {
        'passed': passed,
        'status': status,
        'infrastructure_status': infrastructure_status,
        'infrastructure_reason': infrastructure_reason,
        'failure_stage': failure_stage,
        'required_predicates': all_of,
        'predicate_results': {name: facts[name] for name in all_of},
    }


def _write_run_artifacts(
    run_directory,
    suite_path,
    resolved,
    result,
    noise_config=None,
):
    shutil.copy2(suite_path, Path(run_directory) / 'scenario_definition.yaml')
    atomic_yaml(Path(run_directory) / 'resolved_scenario.yaml', resolved)
    if noise_config is not None:
        shutil.copy2(
            noise_config, Path(run_directory) / 'resolved_cost_function.json'
        )
    atomic_yaml(Path(run_directory) / 'scenario_result.yaml', result)


def execute_suite(
    scenario_path,
    operator,
    case_ids=None,
    runs_root=None,
    summary_output=None,
    gui=False,
    dry_run=False,
):
    """Validate, expand, and optionally execute one serial simulation suite."""
    suite = load_suite(scenario_path)
    resolved_runs, unsupported = expand_suite(suite, case_ids=case_ids)
    execution = deepcopy_mapping(suite['execution'])
    if runs_root is not None:
        execution['runs_root'] = str(runs_root)
    if gui:
        execution['gazebo_gui'] = True
    root = Path(execution['runs_root']).expanduser().resolve()
    start_utc = _utc_now()
    summary = {
        'schema_version': 1,
        'suite_id': suite['suite_id'],
        'scenario_schema_version': suite['schema_version'],
        'source_path': suite['source_path'],
        'started_at_utc': _utc_text(start_utc),
        'completed_at_utc': None,
        'serial_execution': True,
        'selected_case_ids': list(case_ids or []),
        'resolved_run_count': len(resolved_runs),
        'unsupported_count': len(unsupported),
        'unsupported': unsupported,
        'dry_run': dry_run,
        'runs': [],
    }
    if not dry_run:
        ensure_ros_daemon()
    baseline_nodes = ros_graph_nodes() if not dry_run else set()
    for resolved in resolved_runs:
        run_id = generate_scenario_run_id(resolved)
        with tempfile.TemporaryDirectory(prefix='gesc_phase06_') as temporary:
            temporary_path = Path(temporary)
            noise_path = resolved_noise_config(
                resolved, temporary_path / 'resolved_cost_function.json'
            )
            metadata = build_metadata(
                resolved,
                operator,
                suite['metadata']['experiment_version'],
                suite['metadata']['operator_notes'],
            )
            metadata_path = temporary_path / 'metadata.yaml'
            atomic_yaml(metadata_path, metadata)
            launch = build_launch_command(
                resolved, cost_path=noise_path,
                gui=execution['gazebo_gui'],
            )
            record = build_record_command(
                resolved, run_id, metadata_path, root, execution, launch
            )
            if dry_run:
                dry_run_record = {
                    'run_id': run_id,
                    'case_id': resolved['case_id'],
                    'case_key': resolved['case_key'],
                    'profile': resolved['profile'],
                    'seed': resolved['seed'],
                    'launch_argv': launch,
                    'record_argv': record,
                    'metadata': metadata,
                }
                if resolved['schema_version'] >= 3:
                    dry_run_record['activation_contract'] = (
                        resolved['success']['controller']
                    )
                summary['runs'].append(dry_run_record)
                continue
            process_result = run_record_process(
                record,
                execution['wall_timeout_sec'],
                execution['shutdown_grace_sec'],
            )
            cleanup = cleanup_evidence(
                baseline_nodes, process_result['session_id']
            )
            try:
                run_directory = find_run_directory(root, run_id)
            except Exception:
                run_directory = None
            completeness = {}
            finalized_metadata = {}
            outcomes = _unavailable_outcomes(
                'run directory is unavailable',
                readiness_interval_available=None,
            )
            if run_directory is not None:
                try:
                    completeness_path = run_directory / 'completeness.json'
                    completeness = json.loads(
                        completeness_path.read_text(encoding='utf-8')
                    )
                except Exception:
                    completeness = {}
                try:
                    finalized_metadata = yaml.safe_load(
                        (run_directory / 'metadata.yaml').read_text(
                            encoding='utf-8'
                        )
                    )
                    if not isinstance(finalized_metadata, dict):
                        finalized_metadata = {}
                except Exception:
                    finalized_metadata = {}
                try:
                    outcomes = _bag_outcomes(run_directory, resolved)
                except Exception as exc:
                    outcomes = _unavailable_outcomes(
                        f'{type(exc).__name__}: {exc}',
                        readiness_interval_available=None,
                    )
            classification = classify_result(
                resolved,
                completeness,
                cleanup,
                outcomes,
                process_result,
                metadata=finalized_metadata,
                run_directory_available=run_directory is not None,
            )
            record_stdout = process_result.pop('stdout')
            result = {
                'schema_version': 1,
                'run_id': run_id,
                'case_id': resolved['case_id'],
                'case_key': resolved['case_key'],
                'profile': resolved['profile'],
                'seed': resolved['seed'],
                'run_directory': (
                    str(run_directory) if run_directory is not None else None
                ),
                'record_process': process_result,
                'recording_complete': bool(completeness.get('passed')),
                'cleanup': cleanup,
                'outcomes': outcomes,
                'classification': classification,
            }
            result['record_stdout_tail'] = record_stdout[-4000:]
            if run_directory is not None:
                _write_run_artifacts(
                    run_directory, suite['source_path'], resolved, result,
                    noise_config=noise_path,
                )
            summary['runs'].append(result)
            if not cleanup['passed'] and execution['stop_on_cleanup_failure']:
                summary['stopped_early_reason'] = 'cleanup_failure'
                break
            if (
                not classification['passed']
                and execution['stop_on_run_failure']
            ):
                summary['stopped_early_reason'] = 'run_failure'
                break
    summary['completed_at_utc'] = _utc_text()
    if summary_output is None:
        stamp = start_utc.strftime('%Y%m%dT%H%M%S%fZ')
        summary_path = (
            root / 'scenario_summaries' / f"{stamp}_{suite['suite_id']}.yaml"
        )
    else:
        summary_path = Path(summary_output).expanduser().resolve()
    if not dry_run or summary_output is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_yaml(summary_path, summary)
        summary['summary_path'] = str(summary_path)
    return summary


def deepcopy_mapping(value):
    """Copy a YAML-compatible mapping without sharing nested values."""
    return yaml.safe_load(yaml.safe_dump(value))


def _parser():
    parser = argparse.ArgumentParser(
        description=(
            'Run deterministic serial Gazebo cases through ros_esc record_run.'
        )
    )
    parser.add_argument('scenario_yaml')
    parser.add_argument('--operator', required=True)
    parser.add_argument('--case-id', action='append', default=[])
    parser.add_argument('--runs-root')
    parser.add_argument('--summary-output')
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    return parser


def main(args=None):
    """Console entry point."""
    arguments = _parser().parse_args(args)
    try:
        summary = execute_suite(
            arguments.scenario_yaml,
            arguments.operator,
            case_ids=arguments.case_id,
            runs_root=arguments.runs_root,
            summary_output=arguments.summary_output,
            gui=arguments.gui,
            dry_run=arguments.dry_run,
        )
    except Exception as exc:
        print(
            f'run_scenario: {type(exc).__name__}: {exc}', file=sys.stderr
        )
        return 2
    print(yaml.safe_dump(summary, sort_keys=False))
    failed = any(
        not item.get('classification', {}).get('passed', True)
        for item in summary['runs']
    )
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
