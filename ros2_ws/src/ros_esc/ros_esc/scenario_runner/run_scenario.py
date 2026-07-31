#!/usr/bin/env python3

"""Execute deterministic serial Gazebo scenarios through Phase 05 recording."""

import argparse
import bisect
import datetime as dt
import itertools
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

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.serialization import deserialize_message

from ros_esc.experiment_recording.record_run import (
    atomic_yaml,
    validate_run_id,
)

from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
    GaussianFill,
)

import rosbag2_py

from std_msgs.msg import Bool

import yaml

from .scenario_schema import (
    COUNTED_OPEN_FIELD_ASSISTED_RECOVERY_STATE_PATH,
    COUNTED_OPEN_FIELD_RECOVERY_STATE_PATH,
    expand_suite,
    load_suite,
    STAGED_RECOVERY_STATE_PATHS,
)


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
CORNER_ORIGIN_VALIDATION_WORLD = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/turtlebot3_rotating_sensor/worlds/'
    'gesc_gaussian_corner_origin_validation.world'
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
CANCEL_ESCALATION_SEC = 5.0
# A graceful branch-boundary stop still has to close the bag, finalize Phase 05
# metadata, and run the offline completeness validator.  A full 240-second bag
# can require materially longer than the process-tree shutdown allowance, so
# keep those two bounded budgets separate.
BOUNDARY_RECORD_FINALIZATION_GRACE_SEC = 120.0


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
    validation_world = VALIDATION_WORLD
    geometry = resolved.get('geometry')
    if resolved.get('schema_version', 1) >= 5 and geometry is not None:
        world_file = geometry.get('world_file')
        if world_file != CORNER_ORIGIN_VALIDATION_WORLD.name:
            raise ValueError('resolved geometry world file is unsupported')
        validation_world = CORNER_ORIGIN_VALIDATION_WORLD
    elif (
        resolved.get('schema_version', 1) >= 5
        and resolved['validation']['world']
    ):
        raise ValueError(
            'schema-v8 open-field runs cannot request a validation world'
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
            str(validation_world)
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
    scenario_runner = {
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
    }
    if resolved.get('schema_version', 1) >= 4:
        scenario_runner.update({
            'acceptance_family': resolved['acceptance_family'],
            'acceptance_partition': resolved['acceptance_partition'],
            'repeat_reference': resolved['repeat_reference'],
            'metric_applicability': resolved['metric_applicability'],
        })
    if resolved.get('schema_version', 1) >= 5:
        scenario_runner.update({
            'known_topology': resolved['known_topology'],
            'geometry': resolved['geometry'],
        })
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
            **(
                {
                    'geometry': resolved['geometry'],
                    'known_topology': resolved['known_topology'],
                }
                if resolved.get('schema_version', 1) >= 5 else {}
            ),
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
        'scenario_runner': scenario_runner,
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


def _process_identity(pid):
    """Read one Linux process identity without trusting a reusable PID."""
    try:
        stat_text = Path(f'/proc/{int(pid)}/stat').read_text(
            encoding='utf-8'
        )
    except (OSError, ValueError):
        return None
    closing_parenthesis = stat_text.rfind(')')
    if closing_parenthesis < 0:
        return None
    fields = stat_text[closing_parenthesis + 2:].split()
    if len(fields) <= 19:
        return None
    try:
        return {
            'pid': int(pid),
            'state': fields[0],
            'parent_pid': int(fields[1]),
            'process_group_id': int(fields[2]),
            'session_id': int(fields[3]),
            'start_ticks': int(fields[19]),
        }
    except ValueError:
        return None


def _process_children(pid):
    """Read the direct children of one process from procfs."""
    try:
        children_text = Path(
            f'/proc/{int(pid)}/task/{int(pid)}/children'
        ).read_text(encoding='utf-8')
        return [int(value) for value in children_text.split()]
    except (OSError, ValueError):
        return []


def _snapshot_process_tree(root_pid):
    """Snapshot descendants, including nested sessions, before signaling."""
    snapshot = {}
    pending = [int(root_pid)]
    while pending:
        pid = pending.pop()
        if pid in snapshot:
            continue
        identity = _process_identity(pid)
        if identity is None:
            continue
        snapshot[pid] = identity
        pending.extend(_process_children(pid))
    return snapshot


def _matching_process(identity):
    """Return the current identity only when the snapshotted PID is unchanged."""
    current = _process_identity(identity['pid'])
    if current is None or current['state'] == 'Z':
        return None
    if current['start_ticks'] != identity['start_ticks']:
        return None
    return current


def _live_snapshot_processes(snapshot):
    """Return unchanged, non-zombie processes from one owned tree snapshot."""
    live = {}
    for pid, identity in snapshot.items():
        current = _matching_process(identity)
        if current is not None:
            live[pid] = current
    return live


def _owned_process_groups(snapshot, live):
    """Group live snapshotted identities without including the caller."""
    current_pid = os.getpid()
    current_group = os.getpgrp()
    groups = {}
    for pid, current in live.items():
        original = snapshot[pid]
        process_group_id = current['process_group_id']
        if (
            pid == current_pid
            or process_group_id <= 0
            or process_group_id == current_group
            or process_group_id != original['process_group_id']
        ):
            continue
        groups.setdefault(process_group_id, []).append(original)
    return groups


def _signal_owned_process_group(process_group_id, identities, signum):
    """Signal a group only while an original member still matches procfs."""
    if process_group_id <= 0 or process_group_id == os.getpgrp():
        return False
    safe_member_found = False
    for identity in identities:
        current = _matching_process(identity)
        if (
            current is not None
            and current['process_group_id'] == process_group_id
        ):
            safe_member_found = True
            break
    if not safe_member_found:
        return False
    try:
        os.killpg(process_group_id, signum)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _wait_for_cancelled_tree(
    process,
    snapshot,
    timeout_sec,
    drain_output,
):
    """Wait boundedly for the leader and every snapshotted descendant."""
    timeout_sec = max(0.0, timeout_sec)
    deadline = time.monotonic() + timeout_sec
    leader_reaped = False
    output = None
    try:
        if drain_output:
            output, unused_stderr = process.communicate(timeout=timeout_sec)
            del unused_stderr
        else:
            process.wait(timeout=timeout_sec)
        leader_reaped = True
    except BaseException:
        try:
            leader_reaped = process.poll() is not None
        except BaseException:
            leader_reaped = False
    while True:
        live = _live_snapshot_processes(snapshot)
        if leader_reaped:
            # Let the caller escalate any nested-session survivors
            # immediately once their owning recorder has exited.
            return True, live, output
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            return leader_reaped, live, output
        time.sleep(min(0.05, remaining))
        if not leader_reaped:
            try:
                leader_reaped = process.poll() is not None
            except BaseException:
                leader_reaped = False


def _cancel_scoped_process(process, shutdown_grace_sec, drain_output):
    """Stop the interrupted record tree, including its nested sessions."""
    snapshot = _snapshot_process_tree(process.pid)
    signal_levels = {}
    captured_output = None
    root_identity = snapshot.get(process.pid)
    if (
        root_identity is not None
        and root_identity['process_group_id'] == process.pid
        and _signal_owned_process_group(
            process.pid,
            [root_identity],
            signal.SIGINT,
        )
    ):
        signal_levels[process.pid] = 1
    elif process.pid != os.getpgrp():
        try:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
                signal_levels[process.pid] = 1
        except BaseException:
            pass

    leader_reaped, live, output = _wait_for_cancelled_tree(
        process,
        snapshot,
        shutdown_grace_sec,
        drain_output,
    )
    if output is not None:
        captured_output = output
    if leader_reaped and not live:
        return captured_output

    escalation_signals = (
        signal.SIGINT,
        signal.SIGTERM,
        signal.SIGKILL,
    )
    for _ in escalation_signals:
        groups = _owned_process_groups(snapshot, live)
        for process_group_id, identities in sorted(groups.items()):
            level = signal_levels.get(process_group_id, 0)
            if level >= len(escalation_signals):
                continue
            if _signal_owned_process_group(
                process_group_id,
                identities,
                escalation_signals[level],
            ):
                signal_levels[process_group_id] = level + 1
        leader_reaped, live, output = _wait_for_cancelled_tree(
            process,
            snapshot,
            CANCEL_ESCALATION_SEC,
            drain_output,
        )
        if output is not None:
            captured_output = output
        if leader_reaped and not live:
            return captured_output
    return captured_output


def _run_record_to_boundary(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    anchor_state,
    boundary_state,
    boundary_required_events,
):
    """Observe a development branch boundary and request orderly shutdown."""
    context = rclpy.context.Context()
    context_initialized = False
    node = None
    executor = None
    node_added = False
    process = None
    primary_error = None
    observed = {
        'anchor': False,
        'boundary_state': False,
        'events': set(),
    }

    def state_callback(message):
        names, unused_error = _canonical_state_sequence([message])
        del unused_error
        if not names:
            return
        if names[0] == anchor_state:
            observed['anchor'] = True
        if observed['anchor'] and names[0] == boundary_state:
            observed['boundary_state'] = True

    def event_callback(message):
        names, unused_error = _canonical_event_sequence([message])
        del unused_error
        if names:
            # The event that causes SEARCH -> VERIFY_EXTREMUM is published
            # immediately before the state transition.  Retain it so a
            # branch contract can require the complete causal boundary.
            observed['events'].add(names[0])

    timed_out = False
    boundary_stop = False
    try:
        rclpy.init(context=context)
        context_initialized = True
        node = rclpy.create_node(
            f'phase08_v3_boundary_{uuid.uuid4().hex[:8]}',
            context=context,
        )
        executor = SingleThreadedExecutor(context=context)
        executor.add_node(node)
        node_added = True
        node.create_subscription(
            AlgorithmState,
            '/gesc_gaussian/algorithm_state',
            state_callback,
            10,
        )
        node.create_subscription(
            AlgorithmEvent,
            '/gesc_gaussian/algorithm_events',
            event_callback,
            10,
        )
        with tempfile.TemporaryFile(mode='w+t', encoding='utf-8') as output:
            process = subprocess.Popen(
                command,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            deadline = time.monotonic() + wall_timeout_sec
            while process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    timed_out = True
                    break
                executor.spin_once(timeout_sec=min(0.1, remaining))
                if (
                    observed['boundary_state']
                    and set(boundary_required_events) <= observed['events']
                ):
                    boundary_stop = True
                    break
            if boundary_stop or timed_out:
                cancellation_grace_sec = shutdown_grace_sec
                if boundary_stop:
                    cancellation_grace_sec += (
                        BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
                    )
                _cancel_scoped_process(
                    process,
                    cancellation_grace_sec,
                    drain_output=False,
                )
            output.flush()
            output.seek(0)
            stdout = output.read()
    except BaseException as exc:
        primary_error = exc
        if process is not None:
            try:
                _cancel_scoped_process(
                    process,
                    shutdown_grace_sec,
                    drain_output=False,
                )
            except BaseException:
                pass
        raise
    finally:
        cleanup_error = None
        if executor is not None and node_added:
            try:
                executor.remove_node(node)
            except BaseException as exc:
                cleanup_error = exc
        if executor is not None:
            try:
                executor.shutdown()
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if node is not None:
            try:
                node.destroy_node()
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if context_initialized:
            try:
                rclpy.shutdown(context=context)
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if primary_error is None and cleanup_error is not None:
            raise cleanup_error
    return {
        'return_code': process.returncode,
        'timed_out': timed_out,
        'stdout': stdout,
        'session_id': process.pid,
        'graceful_boundary_stop': boundary_stop,
        'boundary_anchor_state': anchor_state,
        'boundary_state': boundary_state,
        'boundary_observed': observed['boundary_state'],
        'boundary_required_events': list(boundary_required_events),
        'boundary_required_events_observed': sorted(
            observed['events'] & set(boundary_required_events)
        ),
    }


def _run_record_to_global_proximity(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    resolved,
):
    """Stop only at a verified post-recovery global odometry sample."""
    context = rclpy.context.Context()
    context_initialized = False
    node = None
    executor = None
    node_added = False
    process = None
    primary_error = None
    sequence = 0
    state_messages = []
    event_messages = []
    fill_records = []
    observed = {
        'stage_a': False,
        'fill_cardinality': False,
        'stage_a_evidence': None,
        'stage_error': None,
        'stage_a_monitor_started_sim_sec': None,
        'stage_a_latest_sim_sec': None,
        'stage_a_timeout': False,
        'stage_a_timeout_sample': None,
        'global_approach': False,
        'global_approach_sample': None,
        'global_closer': False,
        'global_closer_sample': None,
        'global_proximity': False,
        'global_sample': None,
        'post_stage_a_started_sim_sec': None,
        'post_stage_a_latest_sim_sec': None,
        'post_stage_a_timeout': False,
        'post_stage_a_timeout_sample': None,
        'controller_ranked_goal': False,
        'controller_ranked_goal_evidence': None,
    }
    staged_contract = resolved['success']['staged_recovery']
    requires_ranked_goal = bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'extremum_classification_mode'
        ) == 'counted_candidates'
    )
    sources = {source['id']: source for source in resolved['sources']}
    global_source = sources[staged_contract['global_source_id']]

    def next_sequence():
        nonlocal sequence
        sequence += 1
        return sequence

    def refresh_stage_a():
        (
            stage_a_passed,
            cardinality_passed,
            evidence,
            error,
        ) = _staged_recovery_evidence(
            resolved,
            state_messages,
            event_messages,
            fill_records,
        )
        observed['stage_a'] = stage_a_passed is True
        observed['fill_cardinality'] = cardinality_passed is True
        observed['stage_a_evidence'] = evidence
        observed['stage_error'] = error

    def state_callback(message):
        state_messages.append((next_sequence(), message))
        refresh_stage_a()

    def event_callback(message):
        callback_sequence = next_sequence()
        event_messages.append((callback_sequence, message))
        if (
            requires_ranked_goal
            and message.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
        ):
            try:
                evidence = _event_value_map(message)
                required_values = [
                    float(evidence[name])
                    for name in (
                        'candidate_raw_cost_upper',
                        'candidate_ordinal',
                        'filled_candidate_count',
                        'known_source_count',
                        'comparison_filled_raw_cost_lower',
                        'candidate_strict_separation_margin',
                    )
                ]
                known_count = int(
                    resolved['algorithm']['launch_overrides'][
                        'known_source_count'
                    ]
                )
                valid = bool(
                    all(math.isfinite(value) for value in required_values)
                    and required_values[1] == float(known_count)
                    and required_values[2] == float(known_count - 1)
                    and required_values[3] == float(known_count)
                    and required_values[0] < required_values[4]
                    and required_values[5] > 0.0
                    and 'strictly lower' in message.detail
                )
            except (KeyError, TypeError, ValueError):
                valid = False
                evidence = {}
            if valid:
                observed['controller_ranked_goal'] = True
                observed['controller_ranked_goal_evidence'] = {
                    'callback_sequence': callback_sequence,
                    'detail': message.detail,
                    'values': evidence,
                }
        refresh_stage_a()

    def fill_callback(message):
        fill_records.append((next_sequence(), message))
        refresh_stage_a()

    def odometry_callback(message):
        sample_sequence = next_sequence()
        refresh_stage_a()
        try:
            x_value = float(message.pose.pose.position.x)
            y_value = float(message.pose.pose.position.y)
            stamp = message.header.stamp
            sample_sim_sec = (
                float(stamp.sec) + float(stamp.nanosec) * 1e-9
            )
        except (AttributeError, TypeError, ValueError):
            return
        if not all(
            math.isfinite(value)
            for value in (x_value, y_value, sample_sim_sec)
        ):
            return
        if observed['stage_a_monitor_started_sim_sec'] is None:
            observed['stage_a_monitor_started_sim_sec'] = sample_sim_sec
        if (
            not observed['stage_a']
            or not observed['fill_cardinality']
        ):
            observed['stage_a_latest_sim_sec'] = sample_sim_sec
            stage_a_timeout = staged_contract.get('stage_a_timeout_sec')
            if stage_a_timeout is not None:
                elapsed = max(
                    0.0,
                    sample_sim_sec
                    - observed['stage_a_monitor_started_sim_sec'],
                )
                if elapsed >= stage_a_timeout:
                    observed['stage_a_timeout'] = True
                    observed['stage_a_timeout_sample'] = {
                        'callback_sequence': sample_sequence,
                        'position': {'x_m': x_value, 'y_m': y_value},
                        'sample_sim_sec': sample_sim_sec,
                        'started_sim_sec': observed[
                            'stage_a_monitor_started_sim_sec'
                        ],
                        'elapsed_sim_sec': elapsed,
                        'timeout_sec': stage_a_timeout,
                        'interpolation_used': False,
                    }
            return
        if observed['post_stage_a_started_sim_sec'] is None:
            observed['stage_a_latest_sim_sec'] = sample_sim_sec
        completion_sequence = observed['stage_a_evidence'].get(
            'stage_a_completion_stamp'
        )
        if (
            completion_sequence is None
            or sample_sequence <= completion_sequence
        ):
            return
        if observed['post_stage_a_started_sim_sec'] is None:
            observed['post_stage_a_started_sim_sec'] = sample_sim_sec
        observed['post_stage_a_latest_sim_sec'] = sample_sim_sec
        distance = math.hypot(
            x_value - global_source['x_m'],
            y_value - global_source['y_m'],
        )
        approach_radius = staged_contract.get('global_approach_radius_m')
        if (
            approach_radius is not None
            and not observed['global_approach']
            and distance <= approach_radius
        ):
            observed['global_approach'] = True
            observed['global_approach_sample'] = {
                'callback_sequence': sample_sequence,
                'position': {'x_m': x_value, 'y_m': y_value},
                'distance_m': distance,
                'proximity_radius_m': approach_radius,
                'interpolation_used': False,
            }
        closer_radius = staged_contract.get('global_closer_radius_m')
        if (
            closer_radius is not None
            and not observed['global_closer']
            and distance <= closer_radius
        ):
            observed['global_closer'] = True
            observed['global_closer_sample'] = {
                'callback_sequence': sample_sequence,
                'position': {'x_m': x_value, 'y_m': y_value},
                'distance_m': distance,
                'proximity_radius_m': closer_radius,
                'interpolation_used': False,
            }
        if not observed['fill_cardinality']:
            return
        ranked_goal_sequence = None
        ranked_goal_ready = not requires_ranked_goal
        if requires_ranked_goal:
            ranked_goal = observed['controller_ranked_goal_evidence']
            if ranked_goal is not None:
                ranked_goal_sequence = ranked_goal['callback_sequence']
                ranked_goal_ready = sample_sequence > ranked_goal_sequence
        if (
            ranked_goal_ready
            and distance <= staged_contract['global_proximity_radius_m']
        ):
            observed['global_proximity'] = True
            observed['global_sample'] = {
                'callback_sequence': sample_sequence,
                'position': {'x_m': x_value, 'y_m': y_value},
                'distance_m': distance,
                'sample_sim_sec': sample_sim_sec,
                'proximity_radius_m': staged_contract[
                    'global_proximity_radius_m'
                ],
                'interpolation_used': False,
                'controller_ranked_goal_required': requires_ranked_goal,
                'controller_ranked_goal_sequence': ranked_goal_sequence,
            }
            return
        post_stage_a_timeout = staged_contract.get(
            'post_stage_a_timeout_sec'
        )
        if post_stage_a_timeout is not None:
            elapsed = max(
                0.0,
                sample_sim_sec
                - observed['post_stage_a_started_sim_sec'],
            )
            if elapsed >= post_stage_a_timeout:
                observed['post_stage_a_timeout'] = True
                observed['post_stage_a_timeout_sample'] = {
                    'callback_sequence': sample_sequence,
                    'position': {'x_m': x_value, 'y_m': y_value},
                    'distance_m': distance,
                    'sample_sim_sec': sample_sim_sec,
                    'started_sim_sec': observed[
                        'post_stage_a_started_sim_sec'
                    ],
                    'elapsed_sim_sec': elapsed,
                    'timeout_sec': post_stage_a_timeout,
                    'interpolation_used': False,
                }

    timed_out = False
    stage_a_timeout_stop = False
    proximity_stop = False
    post_stage_a_timeout_stop = False
    try:
        rclpy.init(context=context)
        context_initialized = True
        node = rclpy.create_node(
            f'phase08_v7_global_stop_{uuid.uuid4().hex[:8]}',
            context=context,
        )
        executor = SingleThreadedExecutor(context=context)
        executor.add_node(node)
        node_added = True
        node.create_subscription(
            AlgorithmState,
            '/gesc_gaussian/algorithm_state',
            state_callback,
            10,
        )
        node.create_subscription(
            AlgorithmEvent,
            '/gesc_gaussian/algorithm_events',
            event_callback,
            10,
        )
        node.create_subscription(
            GaussianFill,
            '/gesc_gaussian/gaussian_fills',
            fill_callback,
            10,
        )
        node.create_subscription(
            Odometry,
            '/odom',
            odometry_callback,
            10,
        )
        with tempfile.TemporaryFile(mode='w+t', encoding='utf-8') as output:
            process = subprocess.Popen(
                command,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            deadline = time.monotonic() + wall_timeout_sec
            while process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    timed_out = True
                    break
                executor.spin_once(timeout_sec=min(0.1, remaining))
                if observed['stage_a_timeout']:
                    stage_a_timeout_stop = True
                    break
                if observed['global_proximity']:
                    proximity_stop = True
                    break
                if observed['post_stage_a_timeout']:
                    post_stage_a_timeout_stop = True
                    break
            if (
                stage_a_timeout_stop
                or proximity_stop
                or post_stage_a_timeout_stop
                or timed_out
            ):
                cancellation_grace_sec = shutdown_grace_sec
                if (
                    stage_a_timeout_stop
                    or proximity_stop
                    or post_stage_a_timeout_stop
                ):
                    cancellation_grace_sec += (
                        BOUNDARY_RECORD_FINALIZATION_GRACE_SEC
                    )
                _cancel_scoped_process(
                    process,
                    cancellation_grace_sec,
                    drain_output=False,
                )
            output.flush()
            output.seek(0)
            stdout = output.read()
    except BaseException as exc:
        primary_error = exc
        if process is not None:
            try:
                _cancel_scoped_process(
                    process,
                    shutdown_grace_sec,
                    drain_output=False,
                )
            except BaseException:
                pass
        raise
    finally:
        cleanup_error = None
        if executor is not None and node_added:
            try:
                executor.remove_node(node)
            except BaseException as exc:
                cleanup_error = exc
        if executor is not None:
            try:
                executor.shutdown()
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if node is not None:
            try:
                node.destroy_node()
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if context_initialized:
            try:
                rclpy.shutdown(context=context)
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if primary_error is None and cleanup_error is not None:
            raise cleanup_error
    result = {
        'return_code': process.returncode,
        'timed_out': timed_out,
        'stdout': stdout,
        'session_id': process.pid,
        'graceful_boundary_stop': False,
        'boundary_anchor_state': None,
        'boundary_state': None,
        'boundary_observed': False,
        'boundary_required_events': [],
        'boundary_required_events_observed': [],
        'graceful_stage_a_timeout_stop': stage_a_timeout_stop,
        'graceful_global_proximity_stop': proximity_stop,
        'graceful_post_stage_a_timeout_stop': (
            post_stage_a_timeout_stop
        ),
        'stage_a_observed_live': observed['stage_a'],
        'fill_cardinality_observed_live': observed['fill_cardinality'],
        'stage_a_monitor_started_sim_sec_live': observed[
            'stage_a_monitor_started_sim_sec'
        ],
        'stage_a_latest_sim_sec_live': observed['stage_a_latest_sim_sec'],
        'stage_a_timeout_sample_live': observed[
            'stage_a_timeout_sample'
        ],
        'global_proximity_observed_live': observed['global_proximity'],
        'global_proximity_sample_live': observed['global_sample'],
        'post_stage_a_started_sim_sec_live': observed[
            'post_stage_a_started_sim_sec'
        ],
        'post_stage_a_latest_sim_sec_live': observed[
            'post_stage_a_latest_sim_sec'
        ],
        'post_stage_a_timeout_sample_live': observed[
            'post_stage_a_timeout_sample'
        ],
        'staged_monitor_error': observed['stage_error'],
        'controller_ranked_goal_observed_live': observed[
            'controller_ranked_goal'
        ],
        'controller_ranked_goal_evidence_live': observed[
            'controller_ranked_goal_evidence'
        ],
    }
    if 'global_approach_radius_m' in staged_contract:
        result.update({
            'global_approach_observed_live': observed['global_approach'],
            'global_approach_sample_live': observed[
                'global_approach_sample'
            ],
        })
    if 'global_closer_radius_m' in staged_contract:
        result.update({
            'global_closer_observed_live': observed['global_closer'],
            'global_closer_sample_live': observed['global_closer_sample'],
        })
    return result


def run_record_process(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    anchor_state=None,
    boundary_state=None,
    boundary_required_events=None,
    staged_recovery=None,
):
    """Run record_run with a wall timeout and scoped session escalation."""
    if boundary_state is not None and staged_recovery is not None:
        raise ValueError('only one live graceful-stop contract is allowed')
    if staged_recovery is not None:
        return _run_record_to_global_proximity(
            command,
            wall_timeout_sec,
            shutdown_grace_sec,
            staged_recovery,
        )
    if boundary_state is not None:
        return _run_record_to_boundary(
            command,
            wall_timeout_sec,
            shutdown_grace_sec,
            anchor_state,
            boundary_state,
            list(boundary_required_events or []),
        )
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    timed_out = False
    try:
        try:
            output, _ = process.communicate(timeout=wall_timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            output = _cancel_scoped_process(
                process,
                shutdown_grace_sec,
                drain_output=True,
            )
            if output is None:
                output = ''
    except BaseException:
        _cancel_scoped_process(
            process,
            shutdown_grace_sec,
            drain_output=True,
        )
        raise
    return {
        'return_code': process.returncode,
        'timed_out': timed_out,
        'stdout': output,
        'session_id': process.pid,
        'graceful_boundary_stop': False,
        'boundary_anchor_state': None,
        'boundary_state': None,
        'boundary_observed': False,
        'boundary_required_events': [],
        'boundary_required_events_observed': [],
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
            error = (
                'algorithm event contains unknown enum '
                f'{message.event_type}'
            )
            continue
        if canonical == 'UNSPECIFIED':
            error = 'algorithm event reports EVENT_UNSPECIFIED'
        observed.append(canonical)
    return observed, error


def _canonical_state_records(records):
    """Retain canonical state transition stamps for named result scopes."""
    observed = []
    error = None
    for stamp, message in records:
        names, message_error = _canonical_state_sequence([message])
        error = message_error or error
        if names and (not observed or names[0] != observed[-1][1]):
            observed.append((stamp, names[0]))
    return observed, error


def _canonical_event_records(records):
    """Retain canonical event stamps for named result scopes."""
    observed = []
    error = None
    for stamp, message in records:
        names, message_error = _canonical_event_sequence([message])
        error = message_error or error
        if names:
            observed.append((stamp, names[0]))
    return observed, error


def _controller_evidence(expectations, observed_states, observed_events):
    """Evaluate one controller contract over one declared result scope."""
    expected_terminal = expectations.get('expected_terminal_state')
    required_states = [
        str(name).removeprefix('STATE_')
        for name in expectations.get('required_state_sequence', [])
    ]
    required_state_path = [
        str(name).removeprefix('STATE_')
        for name in expectations.get('required_state_path', [])
    ]
    required_state_paths = [
        [
            str(name).removeprefix('STATE_')
            for name in path
        ]
        for path in expectations.get(
            'required_state_paths',
            [required_state_path],
        )
    ]
    required_events = [
        str(name).removeprefix('EVENT_')
        for name in expectations.get('required_events', [])
    ]
    required_event_sequence = [
        str(name).removeprefix('EVENT_')
        for name in expectations.get('required_event_sequence', [])
    ]
    forbidden_states = [
        str(name).removeprefix('STATE_')
        for name in expectations.get('forbidden_states', [])
    ]
    forbidden_events = [
        str(name).removeprefix('EVENT_')
        for name in expectations.get('forbidden_events', [])
    ]
    return {
        'required_state_path': any(
            _first_verification_path(path, observed_states)
            for path in required_state_paths
        ),
        'required_state_sequence': _subsequence(
            required_states,
            observed_states,
        ),
        'required_event_sequence': _subsequence(
            required_event_sequence,
            observed_events,
        ),
        'required_events': all(
            event in observed_events for event in required_events
        ),
        'no_forbidden_states': all(
            state not in observed_states for state in forbidden_states
        ),
        'no_forbidden_events': all(
            event not in observed_events for event in forbidden_events
        ),
        'expected_terminal_state': (
            expected_terminal is None
            or bool(observed_states)
            and observed_states[-1]
            == str(expected_terminal).removeprefix('STATE_')
        ),
    }


def _scope_observations(scope, state_records, event_records):
    """Slice one bag interval at a declared anchor and branch boundary."""
    anchor_index = next(
        (
            index
            for index, record in enumerate(state_records)
            if record[1] == scope['anchor_state']
        ),
        None,
    )
    if anchor_index is None:
        return {
            'anchor_observed': False,
            'boundary_observed': False,
            'observed_state_sequence': [],
            'observed_events': [],
        }
    anchor_stamp = state_records[anchor_index][0]
    event_anchor_stamp = (
        state_records[anchor_index - 1][0]
        if anchor_index > 0
        else anchor_stamp
    )
    boundary = scope['boundary_state']
    boundary_index = None
    if boundary is not None:
        boundary_index = next(
            (
                index
                for index in range(anchor_index, len(state_records))
                if state_records[index][1] == boundary
            ),
            None,
        )
    stop_index = (
        boundary_index + 1
        if boundary_index is not None
        else len(state_records)
    )
    event_stop_stamp = None
    if (
        boundary_index is not None
        and boundary_index + 1 < len(state_records)
    ):
        event_stop_stamp = state_records[boundary_index + 1][0]
    return {
        'anchor_observed': True,
        'boundary_observed': (
            boundary is None or boundary_index is not None
        ),
        'observed_state_sequence': [
            name for unused_stamp, name
            in state_records[anchor_index:stop_index]
        ],
        'observed_events': [
            name for stamp, name in event_records
            if stamp >= event_anchor_stamp
            and (event_stop_stamp is None or stamp < event_stop_stamp)
        ],
    }


def _scope_controller_expectations(scope, expectations):
    """Clip state contracts that begin before a named scope anchor."""
    scoped = dict(expectations)
    anchor = scope['anchor_state']
    for field in ('required_state_path', 'required_state_sequence'):
        values = list(scoped.get(field, []))
        normalized = [
            str(name).removeprefix('STATE_') for name in values
        ]
        if anchor in normalized:
            scoped[field] = values[normalized.index(anchor):]
    if 'required_state_paths' in scoped:
        clipped_paths = []
        for path in scoped['required_state_paths']:
            values = list(path)
            normalized = [
                str(name).removeprefix('STATE_') for name in values
            ]
            if anchor in normalized:
                values = values[normalized.index(anchor):]
            clipped_paths.append(values)
        scoped['required_state_paths'] = clipped_paths
    return scoped


def _unavailable_outcomes(reason, readiness_interval_available=False):
    """Return tri-state behavioral outcomes for invalid infrastructure."""
    return {
        'readiness_interval_available': readiness_interval_available,
        'observed_state_sequence': [],
        'observed_terminal_state': None,
        'observed_events': [],
        'controller_goal': 'unavailable',
        'counted_candidate_ranked_goal_passed': None,
        'counted_candidate_ranked_goal': None,
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
        'route_blocker_encountered_passed': None,
        'route_blocker_fill_center': None,
        'route_blocker_fill_distance_m': None,
        'observed_local_recovery_passed': None,
        'observed_local_recovery': None,
        'local_recovery_stage_passed': None,
        'local_recovery_stage': None,
        'fill_cardinality_passed': None,
        'supervisor_owned_escape_assist_passed': None,
        'supervisor_owned_escape_assist': None,
        'post_recovery_global_proximity_passed': None,
        'post_recovery_global_proximity': None,
        'collision_evidence_available': False,
        'collision_observed': None,
        'collision_expectation_passed': None,
        'result_scopes': {},
        'outcome_error': reason,
    }


def _ground_truth_targets(resolved):
    """Return manual legacy goals or schema-v4 aggregate targets."""
    ground_truth = resolved['success']['ground_truth']
    if resolved.get('schema_version', 1) >= 5:
        global_source_id = ground_truth['global_source_id']
        return [
            {
                'id': source['id'],
                'x_m': source['x_m'],
                'y_m': source['y_m'],
            }
            for source in resolved['sources']
            if source['id'] == global_source_id
        ]
    if resolved.get('schema_version', 1) >= 4:
        aggregate = ground_truth.get('aggregate_field', {})
        return [
            {
                'id': target['target_id'],
                'x_m': target['x_m'],
                'y_m': target['y_m'],
            }
            for target in aggregate.get('targets', [])
        ]
    goal_ids = set(ground_truth['goal_source_ids'])
    return [
        {
            'id': source['id'],
            'x_m': source['x_m'],
            'y_m': source['y_m'],
        }
        for source in resolved['sources']
        if source['id'] in goal_ids
    ]


def _route_blocker_encounter(resolved, fill_messages):
    """Match the first active typed fill to the precomputed route basin."""
    aggregate = (
        resolved.get('success', {})
        .get('ground_truth', {})
        .get('aggregate_field', {})
    )
    qualification = (
        aggregate.get('route_barrier_qualification')
        if isinstance(aggregate, dict)
        else None
    )
    if qualification is None:
        return None, None, None, None
    basin = qualification.get('basin', {})
    tolerance = qualification.get('fill_center_tolerance_m')
    try:
        basin_x = float(basin['x_m'])
        basin_y = float(basin['y_m'])
        limit = float(tolerance)
    except (KeyError, TypeError, ValueError):
        return None, None, None, (
            'route barrier qualification is malformed'
        )
    if not all(math.isfinite(value) for value in (basin_x, basin_y, limit)):
        return None, None, None, (
            'route barrier qualification contains nonfinite values'
        )
    active = next(
        (
            message for message in fill_messages
            if message.active and not message.superseded
        ),
        None,
    )
    if active is None:
        return False, None, None, None
    center_x = float(active.center_x)
    center_y = float(active.center_y)
    if not math.isfinite(center_x) or not math.isfinite(center_y):
        return None, None, None, 'typed fill center is nonfinite'
    distance = math.hypot(center_x - basin_x, center_y - basin_y)
    return (
        distance <= limit,
        {'x_m': center_x, 'y_m': center_y},
        distance,
        None,
    )


def _observed_local_recovery(resolved, event_messages, fill_messages):
    """Bind the first active fill to its local convergence observation."""
    contract = resolved.get('success', {}).get('local_recovery')
    if contract is None:
        return None, None, None
    active = next(
        (
            message for message in fill_messages
            if message.active and not message.superseded
        ),
        None,
    )
    if active is None:
        return False, {'reason': 'no active typed fill'}, None
    fill_stamp = float(active.source_timestamp)
    if not active.source_timestamp_valid or not math.isfinite(fill_stamp):
        return None, None, 'typed fill source timestamp is invalid'
    preceding = [
        message for unused_stamp, message in event_messages
        if (
            message.event_type
            == AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
            and message.source_timestamp_valid
            and math.isfinite(float(message.source_timestamp))
            and float(message.source_timestamp) <= fill_stamp
        )
    ]
    convergence = max(
        preceding,
        key=lambda message: float(message.source_timestamp),
        default=None,
    )
    if convergence is None:
        return False, {
            'reason': 'no preceding convergence event for active fill',
            'fill_source_timestamp': fill_stamp,
        }, None
    values = dict(zip(convergence.value_names, convergence.values))
    try:
        convergence_x = float(values['fill_center_x_m'])
        convergence_y = float(values['fill_center_y_m'])
        fill_x = float(active.center_x)
        fill_y = float(active.center_y)
    except (KeyError, TypeError, ValueError):
        return None, None, 'local recovery coordinates are malformed'
    if not all(math.isfinite(value) for value in (
        convergence_x, convergence_y, fill_x, fill_y,
    )):
        return None, None, 'local recovery coordinates are nonfinite'
    sources = {source['id']: source for source in resolved['sources']}
    local = sources[contract['local_source_id']]
    global_source = sources[contract['global_source_id']]
    local_distance = math.hypot(
        convergence_x - local['x_m'],
        convergence_y - local['y_m'],
    )
    global_distance = math.hypot(
        convergence_x - global_source['x_m'],
        convergence_y - global_source['y_m'],
    )
    fill_distance = math.hypot(
        fill_x - convergence_x,
        fill_y - convergence_y,
    )
    evidence = {
        'local_source_id': contract['local_source_id'],
        'global_source_id': contract['global_source_id'],
        'fill_source_timestamp': fill_stamp,
        'convergence_point': {'x_m': convergence_x, 'y_m': convergence_y},
        'fill_center': {'x_m': fill_x, 'y_m': fill_y},
        'convergence_to_local_m': local_distance,
        'convergence_to_global_m': global_distance,
        'fill_to_convergence_m': fill_distance,
        'thresholds': dict(contract),
    }
    return (
        local_distance <= contract['convergence_to_local_max_m']
        and global_distance >= contract['convergence_to_global_min_m']
        and fill_distance <= contract['fill_to_convergence_max_m'],
        evidence,
        None,
    )


def _message_source_timestamp(message):
    try:
        value = float(message.source_timestamp)
    except (AttributeError, TypeError, ValueError):
        return None
    if (
        not getattr(message, 'source_timestamp_valid', False)
        or not math.isfinite(value)
    ):
        return None
    return value


def _event_value_map(message):
    names = list(getattr(message, 'value_names', []))
    values = list(getattr(message, 'values', []))
    if len(names) != len(values):
        raise ValueError('algorithm event names and values have different sizes')
    return dict(zip(names, values))


def _recovery_episodes(
    state_records,
    expected_count,
    patterns=STAGED_RECOVERY_STATE_PATHS,
):
    patterns = [list(path) for path in patterns]
    episodes = []
    cursor = 0
    while cursor < len(state_records):
        matches = []
        for pattern_index, pattern in enumerate(patterns):
            for record_index in range(
                cursor,
                len(state_records) - len(pattern) + 1,
            ):
                observed_path = [
                    name
                    for unused_stamp, name
                    in state_records[
                        record_index:record_index + len(pattern)
                    ]
                ]
                if observed_path == pattern:
                    matches.append(
                        (record_index, pattern_index, pattern)
                    )
                    break
        if not matches:
            break
        match, unused_pattern_index, pattern = min(
            matches,
            key=lambda item: (item[0], item[1]),
        )
        end = match + len(pattern) - 1
        episodes.append({
            'start_stamp': state_records[match][0],
            'completion_stamp': state_records[end][0],
            'state_path': list(pattern),
        })
        if len(episodes) >= expected_count:
            break
        cursor = end
    return episodes


def _created_fill_clusters(event_messages, fill_records):
    """Join unique FILL_CREATED events to typed cluster identities."""
    typed_by_fill_id = {}
    typed_cluster_ids = set()
    for stamp, message in fill_records:
        try:
            fill_id = int(message.fill_id)
            cluster_id = int(message.cluster_id)
            revision = int(message.revision)
        except (AttributeError, TypeError, ValueError):
            return None, 'typed fill identity is malformed'
        if fill_id <= 0 or cluster_id <= 0 or revision < 0:
            return None, 'typed fill identity must be positive'
        typed_cluster_ids.add(cluster_id)
        key = (cluster_id, revision)
        existing = typed_by_fill_id.get(fill_id)
        record = {
            'bag_stamp': stamp,
            'message': message,
            'fill_id': fill_id,
            'cluster_id': cluster_id,
            'revision': revision,
            'version_key': key,
        }
        if existing is not None and (
            existing['cluster_id'] != cluster_id
            or existing['revision'] != revision
        ):
            return None, 'one typed fill_id maps to conflicting identities'
        typed_by_fill_id.setdefault(fill_id, record)

    created_by_fill_id = {}
    for bag_stamp, message in event_messages:
        if message.event_type != AlgorithmEvent.EVENT_FILL_CREATED:
            continue
        try:
            fill_id = int(message.fill_id)
        except (AttributeError, TypeError, ValueError):
            return None, 'FILL_CREATED fill_id is malformed'
        if not message.fill_id_valid or fill_id <= 0:
            return None, 'FILL_CREATED lacks a valid typed fill_id'
        try:
            values = _event_value_map(message)
            raw_cluster_id = float(values['cluster_id'])
            cluster_id = int(raw_cluster_id)
        except (KeyError, TypeError, ValueError) as exc:
            return None, f'FILL_CREATED cluster_id is malformed: {exc}'
        if (
            not math.isfinite(raw_cluster_id)
            or raw_cluster_id != cluster_id
            or cluster_id <= 0
        ):
            return None, 'FILL_CREATED cluster_id must be a positive integer'
        typed = typed_by_fill_id.get(fill_id)
        if typed is None:
            return None, 'FILL_CREATED has no matching typed fill record'
        if typed['cluster_id'] != cluster_id:
            return None, 'FILL_CREATED and typed fill cluster_id disagree'
        existing = created_by_fill_id.get(fill_id)
        if existing is not None and existing['cluster_id'] != cluster_id:
            return None, 'repeated FILL_CREATED identity is inconsistent'
        created_by_fill_id.setdefault(fill_id, {
            'bag_stamp': bag_stamp,
            'event': message,
            'fill_id': fill_id,
            'cluster_id': cluster_id,
            'typed': typed,
        })

    created = sorted(
        created_by_fill_id.values(),
        key=lambda item: (
            _message_source_timestamp(item['typed']['message'])
            if _message_source_timestamp(item['typed']['message'])
            is not None else math.inf,
            item['bag_stamp'],
            item['fill_id'],
        ),
    )
    created_cluster_ids = {item['cluster_id'] for item in created}
    active_cluster_ids = set()
    latest_by_cluster = {}
    for record in typed_by_fill_id.values():
        current = latest_by_cluster.get(record['cluster_id'])
        if current is None or (
            record['revision'],
            record['bag_stamp'],
        ) > (
            current['revision'],
            current['bag_stamp'],
        ):
            latest_by_cluster[record['cluster_id']] = record
    for cluster_id, record in latest_by_cluster.items():
        message = record['message']
        if message.active and not message.superseded:
            active_cluster_ids.add(cluster_id)
    return {
        'created': created,
        'created_cluster_ids': created_cluster_ids,
        'typed_cluster_ids': typed_cluster_ids,
        'active_cluster_ids': active_cluster_ids,
    }, None


def _staged_recovery_evidence(
    resolved,
    state_messages,
    event_messages,
    fill_records,
):
    """Evaluate Stage A and exact unique-cluster cardinality independently."""
    contract = resolved.get('success', {}).get('staged_recovery')
    if contract is None:
        return None, None, None, None
    expected_count = resolved['known_topology']['expected_local_minima']
    state_records, state_error = _canonical_state_records(state_messages)
    unused_event_records, event_error = _canonical_event_records(
        event_messages
    )
    del unused_event_records
    if state_error or event_error:
        return None, None, None, state_error or event_error
    counted_open_field = bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'extremum_classification_mode'
        ) == 'counted_candidates'
    )
    accepted_paths = (
        (
            (
                COUNTED_OPEN_FIELD_ASSISTED_RECOVERY_STATE_PATH
                if resolved.get('algorithm', {}).get(
                    'launch_overrides', {}
                ).get('open_field_escape_assist_enabled', False)
                else COUNTED_OPEN_FIELD_RECOVERY_STATE_PATH
            ),
        )
        if counted_open_field
        else STAGED_RECOVERY_STATE_PATHS
    )
    episodes = _recovery_episodes(
        state_records,
        expected_count,
        accepted_paths,
    )
    clusters, cluster_error = _created_fill_clusters(
        event_messages,
        fill_records,
    )
    if cluster_error is not None:
        return None, None, None, cluster_error

    convergence_records = []
    for bag_stamp, message in event_messages:
        if (
            message.event_type
            != AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
        ):
            continue
        source_stamp = _message_source_timestamp(message)
        if source_stamp is None:
            return None, None, None, (
                'CONVERGENCE_CONFIRMED source timestamp is invalid'
            )
        try:
            values = _event_value_map(message)
            x_value = float(values['fill_center_x_m'])
            y_value = float(values['fill_center_y_m'])
        except (KeyError, TypeError, ValueError):
            return None, None, None, (
                'CONVERGENCE_CONFIRMED coordinates are malformed'
            )
        if not all(math.isfinite(value) for value in (x_value, y_value)):
            return None, None, None, (
                'CONVERGENCE_CONFIRMED coordinates are nonfinite'
            )
        convergence_records.append({
            'bag_stamp': bag_stamp,
            'source_timestamp': source_stamp,
            'x_m': x_value,
            'y_m': y_value,
        })

    used_convergences = set()
    candidates = []
    for created in clusters['created']:
        fill = created['typed']['message']
        fill_stamp = _message_source_timestamp(fill)
        if fill_stamp is None:
            return None, None, None, (
                'typed fill source timestamp is invalid'
            )
        try:
            fill_x = float(fill.center_x)
            fill_y = float(fill.center_y)
        except (AttributeError, TypeError, ValueError):
            return None, None, None, 'typed fill center is malformed'
        if not all(math.isfinite(value) for value in (fill_x, fill_y)):
            return None, None, None, 'typed fill center is nonfinite'
        eligible = [
            (index, record)
            for index, record in enumerate(convergence_records)
            if (
                index not in used_convergences
                and record['source_timestamp'] <= fill_stamp
            )
        ]
        if not eligible:
            candidates.append({
                'cluster_id': created['cluster_id'],
                'fill_id': created['fill_id'],
                'reason': 'no unique preceding convergence',
            })
            continue
        convergence_index, convergence = max(
            eligible,
            key=lambda item: (
                item[1]['source_timestamp'],
                item[1]['bag_stamp'],
            ),
        )
        used_convergences.add(convergence_index)
        candidates.append({
            'cluster_id': created['cluster_id'],
            'fill_id': created['fill_id'],
            'fill_source_timestamp': fill_stamp,
            'fill_center': {'x_m': fill_x, 'y_m': fill_y},
            'convergence_source_timestamp': convergence[
                'source_timestamp'
            ],
            'convergence_point': {
                'x_m': convergence['x_m'],
                'y_m': convergence['y_m'],
            },
            'fill_to_convergence_m': math.hypot(
                fill_x - convergence['x_m'],
                fill_y - convergence['y_m'],
            ),
        })

    sources = {source['id']: source for source in resolved['sources']}
    global_source = sources[contract['global_source_id']]
    local_ids = list(contract['local_source_ids'])
    association_mode = contract.get(
        'local_association_mode',
        'declared_source',
    )
    best_assignment = None
    best_distance = math.inf
    if len(candidates) >= len(local_ids):
        for selected in itertools.permutations(
            candidates,
            len(local_ids),
        ):
            assignments = []
            total_distance = 0.0
            valid = True
            for local_id, candidate in zip(local_ids, selected):
                convergence = candidate.get('convergence_point')
                if convergence is None:
                    valid = False
                    break
                local = sources[local_id]
                local_distance = math.hypot(
                    convergence['x_m'] - local['x_m'],
                    convergence['y_m'] - local['y_m'],
                )
                global_distance = math.hypot(
                    convergence['x_m'] - global_source['x_m'],
                    convergence['y_m'] - global_source['y_m'],
                )
                nearest_local_id, nearest_local_distance = min(
                    (
                        (
                            candidate_local_id,
                            math.hypot(
                                convergence['x_m']
                                - sources[candidate_local_id]['x_m'],
                                convergence['y_m']
                                - sources[candidate_local_id]['y_m'],
                            ),
                        )
                        for candidate_local_id in local_ids
                    ),
                    key=lambda item: (item[1], item[0]),
                )
                declared_local_valid = (
                    local_distance
                    <= contract['convergence_to_local_max_m']
                )
                valid = valid and (
                    (
                        association_mode == 'verified_trap'
                        or declared_local_valid
                    )
                    and global_distance
                    >= contract['convergence_to_global_min_m']
                    and candidate['fill_to_convergence_m']
                    <= contract['fill_to_convergence_max_m']
                )
                assignments.append({
                    **candidate,
                    'local_source_id': local_id,
                    'convergence_to_local_m': local_distance,
                    'convergence_to_global_m': global_distance,
                    'declared_local_distance_gate_applied': (
                        association_mode == 'declared_source'
                    ),
                    'declared_local_distance_gate_passed': (
                        declared_local_valid
                    ),
                    'nearest_declared_local_source_id': nearest_local_id,
                    'nearest_declared_local_m': nearest_local_distance,
                })
                total_distance += local_distance
            if valid and total_distance < best_distance:
                best_assignment = assignments
                best_distance = total_distance

    event_names, event_error = _canonical_event_sequence([
        message for unused_stamp, message in event_messages
    ])
    if event_error is not None:
        return None, None, None, event_error
    required_event_counts = {
        name: event_names.count(name)
        for name in (
            'CONVERGENCE_CONFIRMED',
            'ESCAPE_STARTED',
            *(
                ()
                if counted_open_field
                else ('RECENTER_STARTED', 'RECENTER_COMPLETE')
            ),
        )
    }
    required_event_counts['FILL_CREATED'] = len(
        clusters['created_cluster_ids']
    )
    lifecycle_events_passed = all(
        count >= expected_count
        for count in required_event_counts.values()
    )
    fill_cardinality_passed = (
        len(clusters['created_cluster_ids']) == expected_count
        and clusters['created_cluster_ids'] == clusters['typed_cluster_ids']
        and clusters['created_cluster_ids'] == clusters['active_cluster_ids']
        and best_assignment is not None
        and {
            item['cluster_id'] for item in best_assignment
        } == clusters['created_cluster_ids']
    )
    stage_a_passed = (
        len(episodes) >= expected_count
        and best_assignment is not None
        and lifecycle_events_passed
        and (
            association_mode != 'verified_trap'
            or fill_cardinality_passed
        )
    )
    assigned_cluster_ids = {
        item['cluster_id'] for item in (best_assignment or [])
    }
    evidence = {
        'expected_local_minima': expected_count,
        'local_association_mode': association_mode,
        'required_state_path': list(
            accepted_paths[0]
        ),
        'accepted_state_paths': [
            list(path) for path in accepted_paths
        ],
        'completed_episode_count': len(episodes),
        'episodes': episodes,
        'stage_a_completion_stamp': (
            episodes[expected_count - 1]['completion_stamp']
            if len(episodes) >= expected_count else None
        ),
        'required_event_counts': required_event_counts,
        'created_cluster_ids': sorted(clusters['created_cluster_ids']),
        'typed_cluster_ids': sorted(clusters['typed_cluster_ids']),
        'active_cluster_ids': sorted(clusters['active_cluster_ids']),
        'assignments': best_assignment or [],
        'unassigned_cluster_ids': sorted(
            clusters['created_cluster_ids'] - assigned_cluster_ids
        ),
        'thresholds': dict(contract),
    }
    return stage_a_passed, fill_cardinality_passed, evidence, None


def _post_recovery_global_proximity(
    resolved,
    stage_a_passed,
    stage_a_evidence,
    odometry_records,
    radius_key='global_proximity_radius_m',
    minimum_bag_stamp=None,
):
    """Find the first finite, noninterpolated post-Stage-A global sample."""
    contract = resolved.get('success', {}).get('staged_recovery')
    if contract is None:
        return None, None, None
    if radius_key not in contract:
        return None, None, None
    if not stage_a_passed or not stage_a_evidence:
        return False, {'reason': 'Stage A did not complete'}, None
    completion_stamp = stage_a_evidence.get('stage_a_completion_stamp')
    if completion_stamp is None:
        return None, None, 'Stage A completion stamp is unavailable'
    required_stamp = completion_stamp
    if minimum_bag_stamp is not None:
        required_stamp = max(required_stamp, minimum_bag_stamp)
    sources = {source['id']: source for source in resolved['sources']}
    global_source = sources[contract['global_source_id']]
    radius = contract[radius_key]
    invalid_samples = 0
    valid_samples = 0
    for sample_index, (bag_stamp, message) in enumerate(odometry_records):
        if bag_stamp <= required_stamp:
            continue
        try:
            x_value = float(message.pose.pose.position.x)
            y_value = float(message.pose.pose.position.y)
        except (AttributeError, TypeError, ValueError):
            invalid_samples += 1
            continue
        if not all(math.isfinite(value) for value in (x_value, y_value)):
            invalid_samples += 1
            continue
        valid_samples += 1
        distance = math.hypot(
            x_value - global_source['x_m'],
            y_value - global_source['y_m'],
        )
        if distance <= radius:
            return True, {
                'global_source_id': contract['global_source_id'],
                'global_point': {
                    'x_m': global_source['x_m'],
                    'y_m': global_source['y_m'],
                },
                'proximity_radius_m': radius,
                'sample_bag_stamp': bag_stamp,
                'sample_index': sample_index,
                'position': {'x_m': x_value, 'y_m': y_value},
                'distance_m': distance,
                'post_stage_a_valid_sample_count': valid_samples,
                'post_stage_a_invalid_sample_count': invalid_samples,
                'interpolation_used': False,
                'minimum_bag_stamp': minimum_bag_stamp,
            }, None
    return False, {
        'reason': 'no qualifying post-Stage-A odometry sample',
        'global_source_id': contract['global_source_id'],
        'proximity_radius_m': radius,
        'post_stage_a_valid_sample_count': valid_samples,
        'post_stage_a_invalid_sample_count': invalid_samples,
        'interpolation_used': False,
        'minimum_bag_stamp': minimum_bag_stamp,
    }, None


def _ranked_goal_evidence(resolved, event_messages, stage_a_evidence):
    """Validate counted-candidate GOAL_REACHED evidence after local recovery."""

    overrides = resolved.get('algorithm', {}).get('launch_overrides', {})
    if overrides.get('extremum_classification_mode') != 'counted_candidates':
        return None, None, None
    completion_stamp = (
        stage_a_evidence.get('stage_a_completion_stamp')
        if stage_a_evidence
        else None
    )
    if completion_stamp is None:
        return False, {'reason': 'Stage A completion stamp is unavailable'}, None
    known_count = int(overrides['known_source_count'])
    invalid_count = 0
    for bag_stamp, message in event_messages:
        if (
            bag_stamp <= completion_stamp
            or message.event_type != AlgorithmEvent.EVENT_GOAL_REACHED
        ):
            continue
        try:
            values = _event_value_map(message)
            candidate_upper = float(values['candidate_raw_cost_upper'])
            candidate_ordinal = float(values['candidate_ordinal'])
            filled_count = float(values['filled_candidate_count'])
            reported_known_count = float(values['known_source_count'])
            comparison_lower = float(
                values['comparison_filled_raw_cost_lower']
            )
            separation_margin = float(
                values['candidate_strict_separation_margin']
            )
        except (KeyError, TypeError, ValueError):
            invalid_count += 1
            continue
        required = (
            candidate_upper,
            candidate_ordinal,
            filled_count,
            reported_known_count,
            comparison_lower,
            separation_margin,
        )
        if not all(math.isfinite(value) for value in required):
            invalid_count += 1
            continue
        if (
            candidate_ordinal != float(known_count)
            or filled_count != float(known_count - 1)
            or reported_known_count != float(known_count)
            or candidate_upper >= comparison_lower
            or separation_margin <= 0.0
            or 'strictly lower' not in message.detail
        ):
            invalid_count += 1
            continue
        return True, {
            'event_bag_stamp': bag_stamp,
            'detail': message.detail,
            'candidate_raw_cost_upper': candidate_upper,
            'comparison_filled_raw_cost_lower': comparison_lower,
            'strict_separation_margin': separation_margin,
            'candidate_ordinal': candidate_ordinal,
            'filled_candidate_count': filled_count,
            'known_source_count': reported_known_count,
            'invalid_ranked_goal_event_count': invalid_count,
        }, None
    return False, {
        'reason': 'no valid post-recovery counted-candidate GOAL_REACHED event',
        'invalid_ranked_goal_event_count': invalid_count,
    }, None


def _non_ground_collision(message):
    return any(
        state
        for state in message.states
        if (
            'ground_plane' not in state.collision1_name
            and 'ground_plane' not in state.collision2_name
        )
    )


def _collision_before_sample(contact_records, sample_evidence):
    """Return whether a non-ground contact precedes an evidence sample."""
    if not sample_evidence:
        return False
    sample_stamp = sample_evidence.get('sample_bag_stamp')
    if sample_stamp is None:
        return False
    return any(
        _non_ground_collision(message)
        for stamp, message in contact_records
        if stamp <= sample_stamp
    )


def _twist_command(message):
    """Return the repository's six-axis command convention for one Twist."""
    return [
        float(message.linear.x),
        float(message.linear.y),
        float(message.linear.z),
        float(message.angular.x),
        float(message.angular.y),
        float(message.angular.z),
    ]


def _finite_command(values):
    """Normalize one finite six-axis command or return None."""
    try:
        command = [float(value) for value in values]
    except (TypeError, ValueError):
        return None
    if len(command) != 6 or not all(math.isfinite(value) for value in command):
        return None
    return command


def _commands_close(left, right, tolerance=1e-9):
    return all(
        math.isclose(
            float(left[index]),
            float(right[index]),
            rel_tol=0.0,
            abs_tol=tolerance,
        )
        for index in range(6)
    )


def _diagnostic_saturated_command(message, combined):
    """Apply the recorded controller limits to one combined command."""
    try:
        lower = [float(value) for value in message.lower_limits]
        upper = [float(value) for value in message.upper_limits]
        limit_valid = list(message.limit_valid)
    except (TypeError, ValueError):
        return None
    if len(lower) != 6 or len(upper) != 6 or len(limit_valid) != 6:
        return None
    saturated = list(combined)
    for index, valid in enumerate(limit_valid):
        if not valid:
            continue
        if (
            not math.isfinite(lower[index])
            or not math.isfinite(upper[index])
            or lower[index] > upper[index]
        ):
            return None
        saturated[index] = min(
            upper[index],
            max(lower[index], combined[index]),
        )
    return saturated


def _supervisor_owned_escape_assist_evidence(
    resolved,
    state_messages,
    event_messages,
    diagnostic_records,
    supervisor_command_records,
    odometry_records,
):
    """Prove v8.6 command ownership and measured aligned escape."""
    enabled = bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'open_field_escape_supervisor_owned_assist_enabled',
            False,
        )
    )
    if not enabled:
        return None, None, None

    evidence = {
        'enabled': True,
        'assist_state_sample_count': 0,
        'assist_control_sample_count': 0,
        'fresh_supervisor_command_sample_count': 0,
        'nonzero_suppressed_gesc_sample_count': 0,
        'positive_supervisor_linear_sample_count': 0,
    }

    def failed(reason):
        return False, {**evidence, 'reason': reason}, None

    assist_indices = [
        index
        for index, (unused_stamp, message) in enumerate(state_messages)
        if (
            message.state_valid
            and message.state == AlgorithmState.STATE_ESCAPE_ASSIST
        )
    ]
    if not assist_indices:
        return failed('no valid ESCAPE_ASSIST state interval')
    first_assist_index = assist_indices[0]
    assist_start_stamp = state_messages[first_assist_index][0]
    post_search_index = next(
        (
            index
            for index in range(first_assist_index + 1, len(state_messages))
            if (
                state_messages[index][1].state_valid
                and state_messages[index][1].state
                == AlgorithmState.STATE_SEARCH
            )
        ),
        None,
    )
    if post_search_index is None:
        return failed('ESCAPE_ASSIST has no later SEARCH boundary')
    search_stamp, search_state = state_messages[post_search_index]
    if any(
        index >= post_search_index
        for index in assist_indices
    ):
        return failed('ESCAPE_ASSIST persisted after the SEARCH boundary')

    assist_states = [
        (stamp, message)
        for stamp, message in state_messages
        if assist_start_stamp <= stamp < search_stamp
    ]
    evidence['assist_state_sample_count'] = len(assist_states)
    if not assist_states or any(
        (
            not message.state_valid
            or message.state != AlgorithmState.STATE_ESCAPE_ASSIST
        )
        for unused_stamp, message in assist_states
    ):
        return failed('assist interval contains a non-ASSIST state sample')

    direction = None
    center = None
    for unused_stamp, message in assist_states:
        candidate_direction = _finite_command([
            message.safe_direction_x,
            message.safe_direction_y,
            0.0,
            0.0,
            0.0,
            0.0,
        ])
        candidate_center = _finite_command([
            message.escape_center_x,
            message.escape_center_y,
            0.0,
            0.0,
            0.0,
            0.0,
        ])
        if (
            not message.safe_direction_valid
            or not message.safe_direction_revision_valid
            or message.safe_direction_revision != 1
            or not message.escape_geometry_valid
            or candidate_direction is None
            or candidate_center is None
        ):
            return failed(
                'assist state lacks finite revision-one direction geometry'
            )
        norm = math.hypot(
            candidate_direction[0],
            candidate_direction[1],
        )
        if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-9):
            return failed('assist direction is not a unit vector')
        if direction is None:
            direction = candidate_direction[:2]
            center = candidate_center[:2]
        elif (
            not _commands_close(
                [*direction, 0.0, 0.0, 0.0, 0.0],
                candidate_direction,
            )
            or not _commands_close(
                [*center, 0.0, 0.0, 0.0, 0.0],
                candidate_center,
            )
        ):
            return failed('assist direction or fill center changed')

    escape_event = next(
        (
            message
            for stamp, message in reversed(event_messages)
            if (
                stamp <= assist_start_stamp
                and message.event_type == AlgorithmEvent.EVENT_ESCAPE_STARTED
            )
        ),
        None,
    )
    if escape_event is None:
        return failed('assist interval has no preceding ESCAPE_STARTED event')
    try:
        escape_values = _event_value_map(escape_event)
        event_direction = [
            float(escape_values['approach_selected_direction_x']),
            float(escape_values['approach_selected_direction_y']),
        ]
        event_center = [
            float(escape_values['escape_center_x_m']),
            float(escape_values['escape_center_y_m']),
        ]
        event_revision = float(
            escape_values['approach_direction_revision']
        )
    except (KeyError, TypeError, ValueError) as exc:
        return failed(f'ESCAPE_STARTED ownership evidence is malformed: {exc}')
    if (
        not all(math.isfinite(value) for value in event_direction + event_center)
        or event_revision != 1.0
        or not _commands_close(
            [*direction, 0.0, 0.0, 0.0, 0.0],
            [*event_direction, 0.0, 0.0, 0.0, 0.0],
        )
        or not _commands_close(
            [*center, 0.0, 0.0, 0.0, 0.0],
            [*event_center, 0.0, 0.0, 0.0, 0.0],
        )
    ):
        return failed('ESCAPE_STARTED and assist-state direction disagree')

    stale_sec = float(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'supervisor_command_stale_sec',
            0.5,
        )
    )
    if not math.isfinite(stale_sec) or stale_sec < 0.0:
        return failed('supervisor command freshness limit is invalid')
    stale_ns = stale_sec * 1e9
    commands = sorted(supervisor_command_records, key=lambda item: item[0])
    command_stamps = [stamp for stamp, unused_message in commands]
    authority_commands = [
        (stamp, message)
        for stamp, message in commands
        if (
            assist_start_stamp <= stamp < search_stamp
            and any(
                abs(value) > 1e-9
                for value in _twist_command(message)
            )
        )
    ]
    if not authority_commands:
        return failed('assist interval has no nonzero supervisor command')
    authority_start_stamp = authority_commands[0][0]
    evidence['assist_authority_start_bag_stamp'] = authority_start_stamp
    assist_diagnostics = [
        (stamp, message)
        for stamp, message in diagnostic_records
        if (
            max(assist_start_stamp, authority_start_stamp)
            <= stamp < search_stamp
        )
    ]
    evidence['assist_control_sample_count'] = len(assist_diagnostics)
    if not assist_diagnostics:
        return failed('assist interval has no control diagnostics')

    for diagnostic_stamp, message in assist_diagnostics:
        gesc = _finite_command(message.gesc_command_unsaturated)
        combined = _finite_command(message.combined_command_unsaturated)
        contribution = _finite_command(message.supervisor_contribution)
        final = _finite_command(message.final_command)
        if (
            gesc is None
            or combined is None
            or contribution is None
            or final is None
            or not message.gesc_command_unsaturated_valid
            or not message.combined_command_unsaturated_valid
            or not message.supervisor_contribution_valid
            or not message.final_command_valid
        ):
            return failed('assist control sample has invalid command evidence')
        first_candidate = bisect.bisect_left(
            command_stamps,
            diagnostic_stamp - stale_ns,
        )
        last_candidate = bisect.bisect_right(
            command_stamps,
            diagnostic_stamp + stale_ns,
        )
        candidate_commands = []
        for command_stamp, command_message in commands[
            first_candidate:last_candidate
        ]:
            if command_stamp >= search_stamp:
                continue
            raw = _finite_command(_twist_command(command_message))
            if raw is not None:
                candidate_commands.append(
                    (abs(diagnostic_stamp - command_stamp), command_stamp, raw)
                )
        if not candidate_commands:
            if commands:
                return failed(
                    'assist control sample has a stale supervisor command'
                )
            return failed(
                'assist control sample has no held supervisor command'
            )
        matching_commands = [
            candidate
            for candidate in candidate_commands
            if _commands_close(combined, candidate[2])
        ]
        if not matching_commands:
            if any(
                _commands_close(
                    combined,
                    [
                        candidate[2][index] + gesc[index]
                        for index in range(6)
                    ],
                )
                for candidate in candidate_commands
            ):
                return failed('GESC leaked into the supervisor-owned command')
            return failed(
                'assist combined command has no fresh matching supervisor '
                'command'
            )
        raw_supervisor = min(
            matching_commands,
            key=lambda item: (item[0], item[1] > diagnostic_stamp, item[1]),
        )[2]
        expected_contribution = [
            combined[index] - gesc[index] for index in range(6)
        ]
        if not _commands_close(contribution, expected_contribution):
            return failed('supervisor contribution arithmetic is inconsistent')
        saturated = _diagnostic_saturated_command(message, combined)
        if saturated is None or not _commands_close(final, saturated):
            return failed('final command does not match recorded saturation')
        evidence['fresh_supervisor_command_sample_count'] += 1
        if any(abs(value) > 1e-9 for value in gesc):
            evidence['nonzero_suppressed_gesc_sample_count'] += 1
        if raw_supervisor[0] > 1e-9:
            evidence['positive_supervisor_linear_sample_count'] += 1

    if evidence['nonzero_suppressed_gesc_sample_count'] <= 0:
        return failed('no nonzero GESC proposal was proven suppressed')
    if evidence['positive_supervisor_linear_sample_count'] <= 0:
        return failed('assist never produced positive supervisor translation')

    exit_candidates = [
        (stamp, message)
        for stamp, message in odometry_records
        if (
            assist_start_stamp <= stamp
            and abs(stamp - search_stamp) <= stale_ns
        )
    ]
    exit_odometry = (
        min(
            exit_candidates,
            key=lambda item: (
                abs(item[0] - search_stamp),
                item[0] > search_stamp,
                item[0],
            ),
        )
        if exit_candidates
        else None
    )
    if exit_odometry is None:
        return failed('SEARCH boundary has no measured exit odometry')
    exit_stamp, exit_message = exit_odometry
    exit_x = float(exit_message.pose.pose.position.x)
    exit_y = float(exit_message.pose.pose.position.y)
    exit_vector = [exit_x - center[0], exit_y - center[1]]
    exit_radius = math.hypot(*exit_vector)
    if (
        not all(math.isfinite(value) for value in [exit_x, exit_y, exit_radius])
        or exit_radius <= 1e-12
    ):
        return failed('measured fill-to-exit vector is invalid')
    exit_unit = [value / exit_radius for value in exit_vector]
    exit_alignment = sum(
        exit_unit[index] * direction[index] for index in range(2)
    )
    evidence.update({
        'assist_start_bag_stamp': assist_start_stamp,
        'post_exit_search_bag_stamp': search_stamp,
        'exit_odometry_bag_stamp': exit_stamp,
        'selected_direction': direction,
        'fill_center_m': center,
        'exit_position_m': [exit_x, exit_y],
        'fill_to_exit_distance_m': exit_radius,
        'fill_to_exit_alignment': exit_alignment,
    })
    if exit_alignment < 0.80:
        return failed('measured fill-to-exit alignment is below 0.80')

    search_weights = [
        float(search_state.sensor_weight),
        float(search_state.gaussian_weight),
        float(search_state.affine_weight),
    ]
    if (
        not search_state.weights_valid
        or search_weights != [1.0, 1.0, 0.0]
        or search_state.safe_direction_valid
        or search_state.safe_direction_revision_valid
    ):
        return failed('first post-exit SEARCH state retained escape authority')

    zero_command_record = next(
        (
            (stamp, message)
            for stamp, message in commands
            if stamp >= search_stamp
        ),
        None,
    )
    if zero_command_record is None:
        return failed('post-exit SEARCH has no supervisor command')
    zero_command_stamp, zero_command_message = zero_command_record
    zero_command = _finite_command(_twist_command(zero_command_message))
    if zero_command is None or any(abs(value) > 1e-9 for value in zero_command):
        return failed('post-exit SEARCH supervisor command is not zero')

    post_diagnostic = next(
        (
            (stamp, message)
            for stamp, message in diagnostic_records
            if stamp >= zero_command_stamp
        ),
        None,
    )
    if post_diagnostic is None:
        return failed('post-exit SEARCH has no control diagnostic sample')
    post_stamp, post_message = post_diagnostic
    post_gesc = _finite_command(post_message.gesc_command_unsaturated)
    post_combined = _finite_command(
        post_message.combined_command_unsaturated
    )
    post_contribution = _finite_command(post_message.supervisor_contribution)
    post_final = _finite_command(post_message.final_command)
    if (
        post_gesc is None
        or post_combined is None
        or post_contribution is None
        or post_final is None
        or not post_message.gesc_command_unsaturated_valid
        or not post_message.combined_command_unsaturated_valid
        or not post_message.supervisor_contribution_valid
        or not post_message.final_command_valid
        or not _commands_close(post_combined, post_gesc)
        or any(abs(value) > 1e-9 for value in post_contribution)
    ):
        return failed('post-exit SEARCH did not restore ordinary GESC ownership')
    post_saturated = _diagnostic_saturated_command(
        post_message,
        post_combined,
    )
    if post_saturated is None or not _commands_close(
        post_final,
        post_saturated,
    ):
        return failed('post-exit SEARCH final command saturation is invalid')
    evidence.update({
        'post_exit_supervisor_zero_bag_stamp': zero_command_stamp,
        'post_exit_control_bag_stamp': post_stamp,
        'post_exit_ordinary_gesc_restored': True,
    })
    return True, evidence, None


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
        '/gesc_gaussian/supervisor_command': Twist,
        '/gesc_gaussian/gaussian_fills': GaussianFill,
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

    state_messages = [
        (stamp, message) for stamp, message
        in records['/gesc_gaussian/algorithm_state'] if inside(stamp)
    ]
    event_messages = [
        (stamp, message) for stamp, message
        in records['/gesc_gaussian/algorithm_events'] if inside(stamp)
    ]
    diagnostic_records = [
        (stamp, message) for stamp, message
        in records['/gesc_gaussian/control_diagnostics'] if inside(stamp)
    ]
    diagnostics = [
        message for unused_stamp, message in diagnostic_records
    ]
    supervisor_command_records = [
        (stamp, message)
        for stamp, message
        in records['/gesc_gaussian/supervisor_command'] if inside(stamp)
    ]
    odometry_records = [
        (stamp, message)
        for stamp, message in records['/odom'] if inside(stamp)
    ]
    odometry = [message for unused_stamp, message in odometry_records]
    contact_records = [
        (stamp, message)
        for stamp, message
        in records['/gesc_gaussian/simulation/contacts'] if inside(stamp)
    ]
    fill_records = [
        (stamp, message)
        for stamp, message
        in records['/gesc_gaussian/gaussian_fills'] if inside(stamp)
    ]
    fills = [message for unused_stamp, message in fill_records]
    collision_expected = resolved['success'].get('collision_expected')
    state_records, state_error = _canonical_state_records(state_messages)
    event_records, event_error = _canonical_event_records(event_messages)
    observed_states = [name for unused_stamp, name in state_records]
    observed_events = [name for unused_stamp, name in event_records]
    saturation_samples = sum(
        1 for message in diagnostics if any(message.saturation_flags)
    )
    final_position = None
    outcome_error = state_error or event_error
    (
        route_blocker_encountered,
        route_blocker_fill_center,
        route_blocker_fill_distance,
        route_error,
    ) = _route_blocker_encounter(resolved, fills)
    outcome_error = outcome_error or route_error
    (
        local_recovery_passed,
        local_recovery_evidence,
        local_recovery_error,
    ) = _observed_local_recovery(resolved, event_messages, fills)
    outcome_error = outcome_error or local_recovery_error
    (
        stage_a_passed,
        fill_cardinality_passed,
        stage_a_evidence,
        staged_error,
    ) = _staged_recovery_evidence(
        resolved,
        state_messages,
        event_messages,
        fill_records,
    )
    outcome_error = outcome_error or staged_error
    (
        ranked_goal_passed,
        ranked_goal_evidence,
        ranked_goal_error,
    ) = _ranked_goal_evidence(
        resolved,
        event_messages,
        stage_a_evidence,
    )
    outcome_error = outcome_error or ranked_goal_error
    (
        supervisor_owned_assist_passed,
        supervisor_owned_assist_evidence,
        supervisor_owned_assist_error,
    ) = _supervisor_owned_escape_assist_evidence(
        resolved,
        state_messages,
        event_messages,
        diagnostic_records,
        supervisor_command_records,
        odometry_records,
    )
    outcome_error = outcome_error or supervisor_owned_assist_error
    ranked_goal_stamp = (
        ranked_goal_evidence.get('event_bag_stamp')
        if ranked_goal_passed and ranked_goal_evidence
        else None
    )
    (
        global_proximity_passed,
        global_proximity_evidence,
        proximity_error,
    ) = _post_recovery_global_proximity(
        resolved,
        stage_a_passed,
        stage_a_evidence,
        odometry_records,
        minimum_bag_stamp=ranked_goal_stamp,
    )
    outcome_error = outcome_error or proximity_error
    if (
        ranked_goal_passed is False
        and global_proximity_passed is True
    ):
        global_proximity_passed = False
        global_proximity_evidence = {
            **global_proximity_evidence,
            'reason': (
                'counted-candidate ranked goal was not valid before proximity'
            ),
            'ranked_goal_evidence': ranked_goal_evidence,
        }
    if (
        resolved.get('schema_version', 1) >= 5
        and global_proximity_passed
        and global_proximity_evidence
    ):
        proximity_stamp = global_proximity_evidence['sample_bag_stamp']
        (
            stage_a_passed,
            fill_cardinality_passed,
            stage_a_evidence,
            staged_error,
        ) = _staged_recovery_evidence(
            resolved,
            [
                record for record in state_messages
                if record[0] <= proximity_stamp
            ],
            [
                record for record in event_messages
                if record[0] <= proximity_stamp
            ],
            [
                record for record in fill_records
                if record[0] <= proximity_stamp
            ],
        )
        outcome_error = outcome_error or staged_error
        (
            global_proximity_passed,
            global_proximity_evidence,
            proximity_error,
        ) = _post_recovery_global_proximity(
            resolved,
            stage_a_passed,
            stage_a_evidence,
            odometry_records,
            minimum_bag_stamp=ranked_goal_stamp,
        )
        outcome_error = outcome_error or proximity_error
    if (
        resolved.get('schema_version', 1) >= 5
        and global_proximity_passed is True
        and fill_cardinality_passed is not True
    ):
        global_proximity_passed = False
        global_proximity_evidence = {
            **global_proximity_evidence,
            'reason': 'fill cardinality was not complete at proximity',
        }
    approach_radius_declared = (
        'global_approach_radius_m'
        in resolved.get('success', {}).get('staged_recovery', {})
    )
    global_approach_passed = None
    global_approach_evidence = None
    if approach_radius_declared:
        (
            global_approach_passed,
            global_approach_evidence,
            approach_error,
        ) = _post_recovery_global_proximity(
            resolved,
            stage_a_passed,
            stage_a_evidence,
            odometry_records,
            radius_key='global_approach_radius_m',
        )
        outcome_error = outcome_error or approach_error
        if global_approach_passed and global_approach_evidence:
            collision_before_approach = _collision_before_sample(
                contact_records,
                global_approach_evidence,
            )
            if collision_before_approach:
                global_approach_passed = False
                global_approach_evidence = {
                    **global_approach_evidence,
                    'reason': (
                        'non-ground collision occurred before approach'
                    ),
                    'collision_before_approach': True,
                }
    closer_radius_declared = (
        'global_closer_radius_m'
        in resolved.get('success', {}).get('staged_recovery', {})
    )
    global_closer_passed = None
    global_closer_evidence = None
    if closer_radius_declared:
        (
            global_closer_passed,
            global_closer_evidence,
            closer_error,
        ) = _post_recovery_global_proximity(
            resolved,
            stage_a_passed,
            stage_a_evidence,
            odometry_records,
            radius_key='global_closer_radius_m',
        )
        outcome_error = outcome_error or closer_error
    collision_scope_end = None
    if (
        resolved.get('schema_version', 1) >= 5
        and global_proximity_passed
        and global_proximity_evidence
    ):
        collision_scope_end = global_proximity_evidence[
            'sample_bag_stamp'
        ]
    scoped_contacts = [
        message
        for stamp, message in contact_records
        if collision_scope_end is None or stamp <= collision_scope_end
    ]
    collision_observed = any(
        _non_ground_collision(message) for message in scoped_contacts
    )
    if (
        resolved.get('schema_version', 1) >= 5
        and global_proximity_passed is True
        and collision_observed
    ):
        global_proximity_passed = False
        global_proximity_evidence = {
            **global_proximity_evidence,
            'reason': 'non-ground collision occurred before proximity',
            'collision_before_proximity': True,
        }
    if odometry:
        final_x = float(odometry[-1].pose.pose.position.x)
        final_y = float(odometry[-1].pose.pose.position.y)
        if math.isfinite(final_x) and math.isfinite(final_y):
            final_position = {
                'x_m': final_x,
                'y_m': final_y,
            }
        else:
            if resolved.get('schema_version', 1) < 5:
                outcome_error = outcome_error or (
                    'terminal odometry contains a nonfinite position'
                )
    distances = {}
    if final_position:
        for target in _ground_truth_targets(resolved):
            distance = math.hypot(
                final_position['x_m'] - target['x_m'],
                final_position['y_m'] - target['y_m'],
            )
            if not math.isfinite(distance):
                distances = {}
                outcome_error = outcome_error or (
                    'terminal goal distance is nonfinite'
                )
                break
            distances[target['id']] = distance
    controller_goal = 'not_applicable'
    if resolved['profile'] == 'robust_gaussian_v1':
        counted_mode = bool(
            resolved.get('algorithm', {}).get('launch_overrides', {}).get(
                'extremum_classification_mode'
            ) == 'counted_candidates'
        )
        controller_goal = (
            'passed'
            if (
                'GOAL_REACHED' in observed_events
                and 'GOAL_HOLD' in observed_states
                and (
                    not counted_mode
                    or ranked_goal_passed is True
                )
            )
            else 'failed'
        )
    ground_truth_targets = _ground_truth_targets(resolved)
    ground_truth = 'not_applicable'
    if outcome_error is not None:
        ground_truth = 'unavailable'
    elif resolved.get('schema_version', 1) >= 5:
        ground_truth = (
            'passed' if global_proximity_passed else 'failed'
        )
    elif ground_truth_targets:
        tolerance = resolved['success']['ground_truth'][
            'final_position_tolerance_m'
        ]
        ground_truth = (
            'passed'
            if distances and min(distances.values()) <= tolerance
            else 'failed'
        )
    contract_state_records = state_records
    contract_event_records = event_records
    if (
        resolved.get('schema_version', 1) >= 5
        and collision_scope_end is not None
    ):
        contract_state_records = [
            record for record in state_records
            if record[0] <= collision_scope_end
        ]
        contract_event_records = [
            record for record in event_records
            if record[0] <= collision_scope_end
        ]
    contract_observed_states = [
        name for unused_stamp, name in contract_state_records
    ]
    contract_observed_events = [
        name for unused_stamp, name in contract_event_records
    ]
    controller_expectations = resolved['success']['controller']
    controller_evidence = _controller_evidence(
        controller_expectations,
        contract_observed_states,
        contract_observed_events,
    )
    scope_results = {}
    for scope_name, scope in resolved['success'].get(
        'result_scopes', {}
    ).items():
        observations = _scope_observations(
            scope,
            contract_state_records,
            contract_event_records,
        )
        observations['predicate_results'] = _controller_evidence(
            _scope_controller_expectations(
                scope,
                controller_expectations,
            ),
            observations['observed_state_sequence'],
            observations['observed_events'],
        )
        scope_results[scope_name] = observations
    outcomes = {
        'readiness_interval_available': first_true is not None,
        'observed_state_sequence': observed_states,
        'observed_terminal_state': (
            observed_states[-1] if observed_states else None
        ),
        'observed_events': observed_events,
        'controller_goal': controller_goal,
        'counted_candidate_ranked_goal_passed': ranked_goal_passed,
        'counted_candidate_ranked_goal': ranked_goal_evidence,
        'simulation_ground_truth': ground_truth,
        'final_position': final_position,
        'final_goal_distances_m': distances,
        'required_state_path_passed': controller_evidence[
            'required_state_path'
        ],
        'required_state_sequence_passed': controller_evidence[
            'required_state_sequence'
        ],
        'required_event_sequence_passed': controller_evidence[
            'required_event_sequence'
        ],
        'required_events_passed': controller_evidence['required_events'],
        'forbidden_states_absent': controller_evidence[
            'no_forbidden_states'
        ],
        'forbidden_events_absent': controller_evidence[
            'no_forbidden_events'
        ],
        'expected_terminal_state_passed': controller_evidence[
            'expected_terminal_state'
        ],
        'saturation_sample_count': saturation_samples,
        'minimum_saturation_samples_passed': (
            saturation_samples
            >= resolved['success']['minimum_saturation_samples']
        ),
        'route_blocker_encountered_passed': route_blocker_encountered,
        'route_blocker_fill_center': route_blocker_fill_center,
        'route_blocker_fill_distance_m': route_blocker_fill_distance,
        'observed_local_recovery_passed': local_recovery_passed,
        'observed_local_recovery': local_recovery_evidence,
        'local_recovery_stage_passed': stage_a_passed,
        'local_recovery_stage': stage_a_evidence,
        'fill_cardinality_passed': fill_cardinality_passed,
        'post_recovery_global_proximity_passed': (
            global_proximity_passed
        ),
        'post_recovery_global_proximity': global_proximity_evidence,
        'collision_evidence_available': bool(scoped_contacts),
        'collision_observed': collision_observed,
        'collision_expectation_passed': (
            collision_expected is None
            or bool(scoped_contacts)
            and collision_observed is collision_expected
        ),
        'result_scopes': scope_results,
        'outcome_error': outcome_error,
    }
    if supervisor_owned_assist_passed is not None:
        outcomes.update({
            'supervisor_owned_escape_assist_passed': (
                supervisor_owned_assist_passed
            ),
            'supervisor_owned_escape_assist': (
                supervisor_owned_assist_evidence
            ),
        })
    if approach_radius_declared:
        outcomes.update({
            'post_recovery_global_approach_passed': (
                global_approach_passed
            ),
            'post_recovery_global_approach': global_approach_evidence,
        })
    if closer_radius_declared:
        outcomes.update({
            'post_recovery_global_closer_passed': global_closer_passed,
            'post_recovery_global_closer': global_closer_evidence,
        })
    return outcomes


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

    global_proximity = outcomes.get(
        'post_recovery_global_proximity_passed'
    )
    if (
        resolved.get('schema_version', 1) >= 5
        and global_proximity is True
    ):
        global_proximity = (
            process_result.get('graceful_global_proximity_stop') is True
        )
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
        'route_blocker_encountered': outcomes.get(
            'route_blocker_encountered_passed'
        ),
        'observed_local_recovery': outcomes.get(
            'observed_local_recovery_passed'
        ),
        'local_recovery_stage': outcomes.get(
            'local_recovery_stage_passed'
        ),
        'post_recovery_global_proximity': global_proximity,
        'fill_cardinality': outcomes.get(
            'fill_cardinality_passed'
        ),
        'supervisor_owned_escape_assist': outcomes.get(
            'supervisor_owned_escape_assist_passed'
        ),
        'collision_expectation': outcomes.get(
            'collision_expectation_passed'
        ),
    }
    scope_classifications = {}
    if resolved.get('schema_version', 1) >= 4:
        outcome_scopes = outcomes.get('result_scopes', {})
        for scope_name, scope in resolved['success'][
            'result_scopes'
        ].items():
            observed_scope = outcome_scopes.get(scope_name, {})
            controller_results = observed_scope.get(
                'predicate_results', {}
            )
            predicate_results = {}
            for predicate in scope['all_of']:
                result = facts[predicate]
                if predicate in controller_results:
                    result = controller_results[predicate]
                predicate_results[predicate] = result
            scope_passed = all(
                result is True for result in predicate_results.values()
            )
            if observed_scope.get('anchor_observed') is not True:
                scope_passed = False
            if (
                scope['boundary_state'] is not None
                and observed_scope.get('boundary_observed') is not True
            ):
                scope_passed = False
            scope_classifications[scope_name] = {
                'passed': scope_passed,
                'anchor_state': scope['anchor_state'],
                'anchor_observed': observed_scope.get(
                    'anchor_observed'
                ),
                'boundary_state': scope['boundary_state'],
                'boundary_observed': observed_scope.get(
                    'boundary_observed'
                ),
                'graceful_stop': scope['graceful_stop'],
                'required_predicates': list(scope['all_of']),
                'predicate_results': predicate_results,
            }
    all_of = resolved['success']['all_of']
    passed = all(facts[name] is True for name in all_of) and all(
        scope['passed'] for scope in scope_classifications.values()
    )
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
        _graceful_boundary_scope(resolved) is not None
        and process_result.get('graceful_boundary_stop') is not True
    ):
        infrastructure_status = 'boundary_stop_failed'
        infrastructure_reason = (
            'declared graceful activation boundary was not observed '
            'by the live runner'
        )
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
    staged_results = {}
    if resolved.get('schema_version', 1) >= 5:
        staged_results = {
            'stage_a_local_recovery': {
                'passed': facts['local_recovery_stage'],
                'evidence': outcomes.get('local_recovery_stage'),
            },
            'stage_b_post_recovery_global_proximity': {
                'passed': facts['post_recovery_global_proximity'],
                'sample_evidence_passed': outcomes.get(
                    'post_recovery_global_proximity_passed'
                ),
                'graceful_stop_triggered': process_result.get(
                    'graceful_global_proximity_stop'
                ),
                'evidence': outcomes.get(
                    'post_recovery_global_proximity'
                ),
            },
            'fill_cardinality': {
                'passed': facts['fill_cardinality'],
                'evidence': outcomes.get('local_recovery_stage'),
            },
            'combined': {
                'passed': passed,
                'infrastructure_status': infrastructure_status,
            },
        }
        if (
            'supervisor_owned_escape_assist'
            in resolved['success']['all_of']
        ):
            staged_results['supervisor_owned_escape_assist'] = {
                'passed': facts['supervisor_owned_escape_assist'],
                'evidence': outcomes.get(
                    'supervisor_owned_escape_assist'
                ),
                'gating': True,
            }
        staged_recovery = resolved.get('success', {}).get(
            'staged_recovery', {}
        )
        if 'global_approach_radius_m' in staged_recovery:
            staged_results['global_region_approach'] = {
                'passed': outcomes.get(
                    'post_recovery_global_approach_passed'
                ),
                'observed_live': process_result.get(
                    'global_approach_observed_live'
                ),
                'evidence': outcomes.get(
                    'post_recovery_global_approach'
                ),
            }
        if 'global_closer_radius_m' in staged_recovery:
            staged_results['global_closer_diagnostic'] = {
                'passed': outcomes.get(
                    'post_recovery_global_closer_passed'
                ),
                'observed_live': process_result.get(
                    'global_closer_observed_live'
                ),
                'evidence': outcomes.get(
                    'post_recovery_global_closer'
                ),
                'gating': False,
            }
        if 'post_stage_a_timeout_sec' in staged_recovery:
            staged_results['stage_b_time_budget'] = {
                'timeout_sec': staged_recovery[
                    'post_stage_a_timeout_sec'
                ],
                'expired': process_result.get(
                    'graceful_post_stage_a_timeout_stop'
                ),
                'started_sim_sec': process_result.get(
                    'post_stage_a_started_sim_sec_live'
                ),
                'latest_sim_sec': process_result.get(
                    'post_stage_a_latest_sim_sec_live'
                ),
                'evidence': process_result.get(
                    'post_stage_a_timeout_sample_live'
                ),
                'gating': True,
            }
        if 'stage_a_timeout_sec' in staged_recovery:
            staged_results['stage_a_time_budget'] = {
                'timeout_sec': staged_recovery['stage_a_timeout_sec'],
                'expired': process_result.get(
                    'graceful_stage_a_timeout_stop'
                ),
                'started_sim_sec': process_result.get(
                    'stage_a_monitor_started_sim_sec_live'
                ),
                'latest_sim_sec': process_result.get(
                    'stage_a_latest_sim_sec_live'
                ),
                'evidence': process_result.get(
                    'stage_a_timeout_sample_live'
                ),
                'gating': True,
            }
    classification = {
        'passed': passed,
        'status': status,
        'infrastructure_status': infrastructure_status,
        'infrastructure_reason': infrastructure_reason,
        'failure_stage': failure_stage,
        'required_predicates': all_of,
        'predicate_results': {name: facts[name] for name in all_of},
        'result_scopes': scope_classifications,
    }
    if staged_results:
        classification['staged_results'] = staged_results
    return classification


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


def _graceful_boundary_scope(resolved):
    """Return the sole development-only graceful scope, when declared."""
    scopes = resolved['success'].get('result_scopes', {})
    matches = [
        scope for scope in scopes.values()
        if scope.get('graceful_stop')
    ]
    if len(matches) > 1:
        raise ValueError('only one graceful result scope may be declared')
    return matches[0] if matches else None


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
            graceful_scope = _graceful_boundary_scope(resolved)
            boundary_arguments = {}
            if resolved.get('schema_version', 1) >= 5:
                boundary_arguments['staged_recovery'] = resolved
            if graceful_scope is not None:
                controller = resolved['success']['controller']
                required_events = []
                if 'required_events' in graceful_scope['all_of']:
                    required_events.extend(
                        controller['required_events']
                    )
                if (
                    'required_event_sequence'
                    in graceful_scope['all_of']
                ):
                    required_events.extend(
                        controller['required_event_sequence']
                    )
                boundary_arguments = {
                    'anchor_state': graceful_scope['anchor_state'],
                    'boundary_state': graceful_scope['boundary_state'],
                    'boundary_required_events': sorted(
                        set(required_events)
                    ),
                }
            process_result = run_record_process(
                record,
                execution['wall_timeout_sec'],
                execution['shutdown_grace_sec'],
                **boundary_arguments,
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


def _reject_direct_v3_formal_execution(scenario_path, dry_run):
    """Route formal v3 execution through its qualified workflow owner."""
    if dry_run:
        return
    suite = load_suite(scenario_path)
    if suite.get('suite_id') in {
        'phase08_v3_activation',
        'phase08_v3_development',
    }:
        raise RuntimeError(
            'formal Phase 08 v3 suites require the '
            'validate_robustness workflow'
        )


def main(args=None):
    """Console entry point."""
    arguments = _parser().parse_args(args)
    try:
        _reject_direct_v3_formal_execution(
            arguments.scenario_yaml,
            arguments.dry_run,
        )
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
