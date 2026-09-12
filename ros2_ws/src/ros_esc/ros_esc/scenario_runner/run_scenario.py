#!/usr/bin/env python3

"""Execute deterministic serial Gazebo scenarios through Phase 05 recording."""

import argparse
import bisect
import ctypes
import datetime as dt
import errno
import itertools
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
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
from ros_esc.v2_stream import (
    canonical_json, sensor_geometry_descriptor, validate_mode_identity,
    validate_stream_config,
)
from ros_esc.v2_direction_policy import THREE_CYCLE_POLICY, policy_metadata, validate_policy

from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
    GaussianFill,
)

import rosbag2_py

from std_msgs.msg import Bool

import yaml

from .m4_scenario import ARRIVAL_SUITE_IDS
from .scenario_schema import (
    configuration_file_path,
    COUNTED_OPEN_FIELD_ASSISTED_RECOVERY_STATE_PATH,
    COUNTED_OPEN_FIELD_RECOVERY_STATE_PATH,
    expand_suite,
    load_suite,
    POST_RECOVERY_ARRIVAL_CRITERION,
    STAGED_RECOVERY_STATE_PATHS,
)


def _repository_root():
    """Resolve the live checkout without assuming its module layout."""
    # Ordinary imports must not spawn Git inside a single-process science job.
    # Explicit repository/discovery/configuration overrides still belong to Git;
    # presentation settings such as GIT_PAGER do not change checkout selection.
    git_selection_overridden = any(
        name in (
            'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR',
            'GIT_CEILING_DIRECTORIES', 'GIT_DISCOVERY_ACROSS_FILESYSTEM',
        ) or name.startswith('GIT_CONFIG')
        for name in os.environ
    )
    if not git_selection_overridden:
        try:
            cwd = Path.cwd().resolve()
            for parent in (cwd, *cwd.parents):
                marker = parent / '.git'
                if marker.is_dir() or marker.is_file():
                    if (parent / 'ros2_ws/src/ros_esc').is_dir():
                        return parent
                    # A nested unrelated repository is a discovery boundary.
                    break
        except OSError:
            pass
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
SENSOR_GEOMETRY = ROS_ESC_ROOT / 'ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json'
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
MAX_TRACKED_PROCESSES = 4096
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


def build_v2_stream_config(resolved):
    """Resolve one descriptor used by every opted-in owner and retained metadata."""
    disturbances = resolved['disturbances']
    sensor_delayed = disturbances['sensor_delay_sec'] > 0.0
    pose_delayed = disturbances['pose_delay_sec'] > 0.0
    return validate_stream_config({
        'schema_version': 2, 'cost_key_basis': 'model_input_time',
        'selected_channel': 0, 'frame_id': 'odom',
        'raw_cost_topic': ('/gesc_gaussian/simulation/raw_cost_delayed' if sensor_delayed else '/turtlebot3/cost_value_chatter'),
        'source_cost_topic': ('/gesc_gaussian/simulation/source_cost_delayed' if sensor_delayed else '/gesc_gaussian/source_cost'),
        'provenance_topic': ('/gesc_gaussian/simulation/source_sample_provenance_delayed' if sensor_delayed else '/gesc_gaussian/v2/source_sample_provenance'),
        'pose_topic': ('/gesc_gaussian/simulation/pose_delayed' if pose_delayed else '/odom'),
        'encoder_topic': '/turtlebot3/encoder_chatter',
        'timekeeper_topic': '/turtlebot3/timekeeper_chatter',
        'augmented_cost_topic': '/cost_modified',
        'objective_cost_topic': '/gesc_gaussian/v2/objective_cost_samples',
        **sensor_geometry_descriptor(SENSOR_GEOMETRY),
    })


def resolve_controller_config_filepath(overrides):
    """Share explicit controller selection between launch and recorder metadata."""
    if 'controller_config_filepath' not in overrides:
        return GESC_CONTROLLER
    return configuration_file_path(overrides['controller_config_filepath'],
                                   'controller_config_filepath')


def build_launch_command(resolved, cost_path=None, gui=False, run_id=None):
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
        })
        if 'brightness_percent' in source:
            arguments[f'light_{index}_brightness_percent'] = (
                source['brightness_percent']
            )
        else:
            arguments[f'light_{index}_intensity_lumens'] = (
                source['relative_lumen_input']
            )
    arguments.update(resolved['algorithm']['launch_overrides'])
    arguments['controller_config_filepath'] = str(resolve_controller_config_filepath(
        resolved['algorithm']['launch_overrides']))
    mode = arguments.get('continuous_search_mode', 'stationary_v1')
    validate_policy(arguments.get('v2_direction_policy', THREE_CYCLE_POLICY),
                    continuous_search_mode=mode, algorithm_profile=resolved['profile'],
                    use_sim_time=True)
    if mode != 'stationary_v1':
        config = build_v2_stream_config(resolved)
        validate_mode_identity(mode, resolved['profile'], run_id, config)
        arguments.update({
            'v2_run_id': run_id,
            'v2_stream_config_json': canonical_json(config),
            'v2_algorithm_provenance_topic': config['provenance_topic'],
            'sensor_transform_config_filepath': str(SENSOR_GEOMETRY),
        })
    command = [
        'ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml'
    ]
    command.extend(
        f'{name}:={_launch_value(value)}' for name, value in arguments.items()
    )
    return command


def build_metadata(resolved, operator, experiment_version, operator_notes, run_id=None):
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
    if 'purpose' in resolved:
        scenario_runner['purpose'] = resolved['purpose']
    mode = resolved['algorithm']['launch_overrides'].get('continuous_search_mode', 'stationary_v1')
    overrides = resolved['algorithm']['launch_overrides']
    policy = validate_policy(overrides.get('v2_direction_policy', THREE_CYCLE_POLICY),
                             continuous_search_mode=mode, algorithm_profile=resolved['profile'],
                             use_sim_time=True)
    if 'v2_direction_policy' in overrides:
        scenario_runner['direction_policy'] = policy_metadata(policy)
    if mode != 'stationary_v1':
        config = build_v2_stream_config(resolved)
        validate_mode_identity(mode, resolved['profile'], run_id, config)
        scenario_runner['v2_identity'] = {
            'continuous_search_mode': mode, 'run_id': run_id,
            'stream_config': config, 'time_origin_binding': 'first_valid_simulation_timekeeper',
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
            str(resolve_controller_config_filepath(resolved['algorithm']['launch_overrides'])),
            *([str(SENSOR_GEOMETRY)] if mode == 'rolling_gesc_v2' else []),
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
    command = [
        'ros2', 'run', 'ros_esc', 'record_run',
        '--mode', 'simulation',
        '--metadata-input', str(metadata_path),
        '--runs-root', str(runs_root),
        '--run-id', run_id,
        '--duration-sec', str(execution['run_timeout_sec']),
        '--preflight-timeout-sec', str(execution['preflight_timeout_sec']),
        '--target-exit-timeout-sec', str(execution['shutdown_grace_sec']),
    ]
    if execution.get('simulation_duration_sec', 0.0) > 0.0:
        command.extend(['--sim-duration-sec', str(execution['simulation_duration_sec'])])
    return [*command, '--', *launch_command]


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


def ros_graph_nodes(*, strict=False, absolute_deadline=None, require_shared_daemon=False):
    """Return the current ROS node set without changing the graph."""
    if require_shared_daemon and not strict:
        raise ValueError('shared daemon admission requires strict graph inspection')
    if strict:
        remaining = _deadline_remaining(absolute_deadline)
        if remaining <= 0:
            raise TimeoutError('ROS graph inspection deadline exhausted')
        owner = '_native_development_graph_baseline' if require_shared_daemon else '_native_ros_graph_nodes'
        command = [sys.executable, '-c',
            'import json; from ros_esc.scenario_runner.run_scenario import '
            f'{owner}; print(json.dumps(sorted({owner}())))']
        result = subprocess.run(command, check=True, capture_output=True, text=True,
                                timeout=min(5., remaining))
        names = json.loads(result.stdout)
        if not isinstance(names, list) or any(not isinstance(name, str) or not name.startswith('/')
                                               for name in names):
            raise ValueError('ROS graph inspection returned malformed names')
        return set(names)
    try:
        return _native_ros_graph_nodes()
    except Exception:
        if rclpy.ok():
            rclpy.try_shutdown()
        return set()


def _native_development_graph_baseline():
    """Admit one exact shared daemon inside the strict owner's five-second child."""
    from types import SimpleNamespace
    from ros2cli.node.daemon import DaemonNode

    def identity(daemon):
        name, namespace = daemon.get_name(), daemon.get_namespace()
        if (not isinstance(name, str) or not name or '/' in name
                or not isinstance(namespace, str) or not namespace.startswith('/')):
            raise ValueError('shared daemon identity is malformed')
        return name, namespace

    end = time.monotonic() + 5.0
    with DaemonNode(SimpleNamespace()) as daemon:
        initial = identity(daemon)
        full_name = initial[1].rstrip('/') + '/' + initial[0]
        while time.monotonic() < end:
            observed = _native_ros_graph_nodes()
            if identity(daemon) != initial:
                raise ValueError('shared daemon identity changed during graph admission')
            if full_name in observed:
                return observed
            time.sleep(.05)
    raise TimeoutError('shared daemon was absent from independent native graph')


def _native_ros_graph_nodes():
    """Native discovery probe; selected callers isolate even teardown in a child."""
    node = None
    rclpy.init(args=[])
    try:
        node = rclpy.create_node(f'phase06_graph_probe_{uuid.uuid4().hex[:8]}')
        rclpy.spin_once(node, timeout_sec=0.25)
        return {(f"{namespace.rstrip('/')}/{name}" if namespace != '/' else f'/{name}')
                for name, namespace in node.get_node_names_and_namespaces()
                if name != node.get_name()}
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


def session_processes(session_id, *, strict=False, absolute_deadline=None):
    """Return live processes in the exact session created for one run."""
    try:
        timeout = 5.0
        if strict:
            timeout = min(timeout, _deadline_remaining(absolute_deadline))
            if timeout <= 0:
                raise TimeoutError('process inspection deadline exhausted')
        output = subprocess.run(
            ['ps', '-eo', 'pid=,sid=,stat=,comm='],
            check=True, capture_output=True, text=True, timeout=timeout,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        if strict:
            raise
        return [{'pid': None, 'error': 'process inspection failed'}]
    survivors = []
    for line in output.splitlines():
        fields = line.split(None, 3)
        if len(fields) != 4:
            if strict:
                raise ValueError('malformed process inspection row')
            continue
        pid, sid, state, command = fields
        if int(sid) == int(session_id) and not state.startswith('Z'):
            survivors.append({
                'pid': int(pid), 'session_id': int(sid),
                'state': state, 'command': command,
            })
    return survivors


def cleanup_evidence(baseline_nodes, session_id, settle_sec=5.0, *, strict=False,
                     absolute_deadline=None, process_ownership=None,
                     process_ownership_mode='observed_tree_v1'):
    """Wait for graph settling and report exact-node/process contamination."""
    if process_ownership_mode not in ('observed_tree_v1', 'subreaper_v2', 'subreaper_group_v3'):
        raise ValueError('unknown process ownership mode')
    selected_reaper = process_ownership_mode in ('subreaper_v2', 'subreaper_group_v3')
    if selected_reaper and not strict:
        raise ValueError('subreaper cleanup requires strict inspection')
    if strict:
        if _deadline_remaining(absolute_deadline) <= 0:
            result = {'passed': False, 'strict': True,
                    'inspection_errors': ['cleanup deadline exhausted before inspection']}
            if selected_reaper:
                result.update(process_ownership_mode=process_ownership_mode,
                    inspection_performed=False, remaining_new_nodes=None,
                    remaining_session_processes=None, remaining_owned_processes=None,
                    absolute_deadline=absolute_deadline)
            return result
        end = min(time.monotonic() + settle_sec, absolute_deadline)
        errors, survivors, live, new_nodes = [], [], {}, set()
        inspected = {'graph': False, 'sessions': False, 'identities': False}
        ownership = process_ownership or {}
        identities = {int(item['pid']): item for item in ownership.get('identities', [])}
        root_identity = identities.get(session_id)
        if selected_reaper:
            proof = ownership.get('kernel_proof', {})
            if (ownership.get('mode') != process_ownership_mode
                    or (process_ownership_mode == 'subreaper_group_v3'
                        and ownership.get('signal_strategy') != 'initial_unreaped_root_group_sigint_then_adopted_pidfd')
                    or ownership.get('root_pid') != session_id
                    or ownership.get('inspection_complete') is not True
                    or not all(proof.get(key) is True for key in (
                        'baseline_echild', 'subreaper_verified', 'root_reaped',
                        'final_echild', 'scope_exclusive', 'sigchld_valid',
                        'state_restored', 'complete'))):
                return {'passed': False, 'strict': True,
                    'process_ownership_mode': process_ownership_mode,
                    'inspection_performed': False,
                    'inspection_errors': ['kernel descendant ownership proof is incomplete'],
                    'remaining_new_nodes': None, 'remaining_session_processes': None,
                    'remaining_owned_processes': None, 'absolute_deadline': absolute_deadline}
        elif (not ownership.get('inspection_complete') or root_identity is None
                or root_identity.get('session_id') != session_id):
            errors.append('inner recorder ownership is absent or incomplete')
        sessions = {session_id, *ownership.get('session_ids', []),
                    *(item['session_id'] for item in identities.values())}
        while not errors:
            try:
                new_nodes = ros_graph_nodes(strict=True, absolute_deadline=absolute_deadline) - set(baseline_nodes)
                inspected['graph'] = True
                survivors = [item for sid in sorted(sessions) for item in session_processes(
                    sid, strict=True, absolute_deadline=absolute_deadline)]
                inspected['sessions'] = True
                live = _live_snapshot_processes(identities, strict=True)
                inspected['identities'] = True
            except Exception as error:
                errors.append(f'{type(error).__name__}: {error}')
                break
            if not new_nodes and not survivors and not live:
                break
            remaining = min(end, absolute_deadline) - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(.25, remaining))
        result = {'passed': not errors and not new_nodes and not survivors and not live,
                'strict': True, 'inspection_errors': errors,
                'baseline_nodes': sorted(baseline_nodes),
                'remaining_new_nodes': sorted(new_nodes),
                'inspected_session_ids': sorted(sessions),
                'remaining_session_processes': survivors,
                'remaining_owned_processes': list(live.values()),
                'absolute_deadline': absolute_deadline,
                'completed_monotonic': time.monotonic()}
        if selected_reaper:
            result.update(process_ownership_mode=process_ownership_mode,
                          inspection_performed=all(inspected.values()), inspections=inspected)
            for field, check in (('remaining_new_nodes', 'graph'),
                ('remaining_session_processes', 'sessions'), ('remaining_owned_processes', 'identities')):
                if not inspected[check]:
                    result[field] = None
        return result
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


def _track_owned_processes(process, audit):
    """Retain nested-session identities in the existing selected process loop."""
    if audit is None:
        return
    if _ACTIVE_SUBREAPER is not None and audit is _ACTIVE_SUBREAPER.audit:
        _ACTIVE_SUBREAPER.observe(process)
        return
    try:
        snapshot = _snapshot_process_tree(process.pid, strict=True)
        root = snapshot[process.pid]
        if root['session_id'] != process.pid:
            raise ValueError('recorder leader does not own its new session')
        previous = {item['pid']: item for item in audit['identities']}
        if process.pid in previous and previous[process.pid]['start_ticks'] != root['start_ticks']:
            raise ValueError('recorder leader identity changed')
        sessions = set(audit['session_ids']) | {item['session_id'] for item in snapshot.values()}
        if (len(set(previous) | set(snapshot)) > MAX_TRACKED_PROCESSES
                or len(sessions) > MAX_TRACKED_PROCESSES):
            raise ValueError('owned-process tracking capacity exceeded')
        previous.update(snapshot)
        audit['identities'] = list(previous.values())
        audit['session_ids'] = sorted(sessions)
    except Exception as error:
        audit['inspection_complete'] = False
        if len(audit['inspection_errors']) < 16:
            audit['inspection_errors'].append(f'{type(error).__name__}: {error}')


def _process_tracking(enabled):
    if enabled and _ACTIVE_SUBREAPER is not None:
        return _ACTIVE_SUBREAPER.audit
    return ({'inspection_complete': True, 'inspection_errors': [], 'identities': [],
             'session_ids': [], 'capacity': MAX_TRACKED_PROCESSES,
             'scope': 'observed owned identities and sessions; no unseen-future descendant proof'}
            if enabled else None)


# The selected runner is the sole launcher/waiter during this scope. Its shared
# daemon and synchronous graph probes must be fully reaped before entry/after
# exit. Native ROS threads may exist, but may not create unrelated child jobs.
_SUBREAPER_LOCK = threading.Lock()
_ACTIVE_SUBREAPER = None
_WAIT_ALL = 0x40000000  # Linux __WALL: include non-SIGCHLD clone children.


def _subreaper_setting(value=None):
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise RuntimeError('subreaper_v2 supports the verified Linux x86_64 ABI only')
    libc = ctypes.CDLL(None, use_errno=True)
    if value is not None:
        if libc.prctl(36, ctypes.c_ulong(value), 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER failed')
    selected = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(selected), 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_GET_CHILD_SUBREAPER failed')
    return selected.value


def _subreaper_sigchld():
    """Read the native glibc action; Python's cached getsignal is insufficient."""
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise RuntimeError('SIGCHLD inspection requires verified Linux x86_64 ABI')
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        version_function = libc.gnu_get_libc_version
    except AttributeError as error:
        raise RuntimeError('SIGCHLD inspection requires the verified glibc ABI') from error
    version_function.restype = ctypes.c_char_p
    version = version_function()
    if not version:
        raise RuntimeError('native glibc version could not be verified')
    class Action(ctypes.Structure):
        _fields_ = [('handler', ctypes.c_void_p), ('mask', ctypes.c_ulong * 16),
                    ('flags', ctypes.c_int), ('restorer', ctypes.c_void_p)]
    action = Action()
    if libc.sigaction(signal.SIGCHLD, None, ctypes.byref(action)):
        raise OSError(ctypes.get_errno(), 'native SIGCHLD inspection failed')
    if action.handler is not None or action.flags & 2:  # SIG_IGN/custom or SA_NOCLDWAIT
        raise RuntimeError('subreaper requires native SIGCHLD default and no SA_NOCLDWAIT')
    return {'handler': 'SIG_DFL', 'flags': action.flags, 'libc': 'glibc',
            'libc_version': version.decode('ascii')}


def _subreaper_wait_peek():
    """Return ECHILD distinctly from a running child and an unconsumed exit."""
    try:
        return os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT | _WAIT_ALL)
    except ChildProcessError as error:
        if error.errno == errno.ECHILD:
            return 'ECHILD'
        raise


class _SubreaperOwner:
    """Exclusive, bounded kernel ancestry witness for the existing process owner.

    Procfs observations support scoped signaling and diagnostics. Only ECHILD
    after the Popen root was reaped establishes exhaustion. No auxiliary Popen
    may be launched or reaped concurrently inside this selected owner scope.
    """
    def __init__(self, absolute_deadline, shutdown_grace_sec, *, escalation_sec=None,
                 process_ownership_mode='subreaper_v2'):
        _deadline_remaining(absolute_deadline)
        if process_ownership_mode not in ('subreaper_v2', 'subreaper_group_v3'):
            raise ValueError('unknown kernel process ownership mode')
        self.mode = process_ownership_mode
        self.end, self.grace = absolute_deadline, shutdown_grace_sec
        self.escalation = CANCEL_ESCALATION_SEC if escalation_sec is None else escalation_sec
        self.work_end = self.end
        self.process, self.active, self.previous, self.closed = None, False, None, False
        self._sent = set()
        self._root_identity = None
        self._group_graceful_attempted = self._group_graceful_failed = False
        self.audit = {'mode': self.mode, 'owner_pid': os.getpid(), 'root_pid': None,
            'inspection_complete': True, 'inspection_errors': [], 'enumeration_races': [],
            'identities': [], 'session_ids': [], 'reaped_descendants': [], 'signals': [],
            'capacity': MAX_TRACKED_PROCESSES, 'absolute_deadline': self.end,
            'scope': 'exclusive child/reaping scope; kernel subreaper ancestry exhaustion',
            'kernel_proof': dict.fromkeys(('baseline_echild', 'subreaper_verified',
                'root_reaped', 'final_echild', 'scope_exclusive', 'sigchld_valid',
                'state_restored', 'complete'), False)}
        if self.mode == 'subreaper_group_v3':
            self.audit['signal_strategy'] = 'initial_unreaped_root_group_sigint_then_adopted_pidfd'

    def start(self):
        global _ACTIVE_SUBREAPER
        if not _SUBREAPER_LOCK.acquire(blocking=False):
            raise RuntimeError('another selected child/reaper scope is active')
        try:
            self.previous = _subreaper_setting()
            if self.previous != 0:
                raise RuntimeError('preexisting subreaper ownership is incompatible')
            self.audit['sigchld_action'] = _subreaper_sigchld()
            if _subreaper_wait_peek() != 'ECHILD':
                raise RuntimeError('exclusive subreaper baseline has preexisting children')
            if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
                raise RuntimeError('subreaper scoped signaling requires pidfd support')
            if _subreaper_setting(1) != 1:
                raise RuntimeError('subreaper enable verification failed')
            self.active = True
            if _subreaper_wait_peek() != 'ECHILD':
                raise RuntimeError('children appeared during exclusive scope establishment')
            self.audit['kernel_proof'].update(baseline_echild=True,
                subreaper_verified=True, scope_exclusive=True, sigchld_valid=True)
            _ACTIVE_SUBREAPER = self
            return self
        except BaseException:
            if self.active and _subreaper_wait_peek() == 'ECHILD':
                _subreaper_setting(self.previous)
            _SUBREAPER_LOCK.release()
            raise

    def _error(self, error):
        self.audit['inspection_complete'] = False
        if len(self.audit['inspection_errors']) < 16:
            self.audit['inspection_errors'].append(f'{type(error).__name__}: {error}')

    def _retain(self, snapshot):
        if self.mode == 'subreaper_group_v3' and self.process is not None:
            root = snapshot.get(self.process.pid)
            if root is not None:
                if self._root_identity is None:
                    self._root_identity = dict(root)
                elif root['start_ticks'] != self._root_identity['start_ticks']:
                    raise RuntimeError('registered root identity changed')
        identities = {(item['pid'], item['start_ticks']): item for item in self.audit['identities']}
        for item in snapshot.values():
            identities[(item['pid'], item['start_ticks'])] = item
        sessions = set(self.audit['session_ids']) | {item['session_id'] for item in snapshot.values()}
        if len(identities) > MAX_TRACKED_PROCESSES or len(sessions) > MAX_TRACKED_PROCESSES:
            raise ValueError('subreaper observed identity capacity exceeded')
        self.audit['identities'] = list(identities.values())
        self.audit['session_ids'] = sorted(sessions)

    def observe(self, process):
        if self.process is None:
            self.process = process
            self.audit['root_pid'] = process.pid
        if self.process is not process:
            self._error(ValueError('unregistered concurrent Popen owner'))
            return
        try:
            self._retain(_snapshot_process_tree(process.pid, strict=True))
        except ProcessLookupError as error:
            try:
                self._retain(getattr(error, 'owned_process_snapshot', {}))
                if len(self.audit['enumeration_races']) >= MAX_TRACKED_PROCESSES:
                    raise ValueError('subreaper enumeration race capacity exceeded')
                self.audit['enumeration_races'].append({'monotonic': time.monotonic(),
                    'error': str(error), 'partial_pids': sorted(getattr(error, 'owned_process_snapshot', {})),
                    'inspection_pid': getattr(error, 'inspection_pid', None),
                    'inspection_stage': getattr(error, 'inspection_stage', 'tree_enumeration')})
            except Exception as capacity_error:
                self._error(capacity_error)
        except Exception as error:
            self._error(error)

    def _drain(self):
        """Popen retains root status; targeted waits reap only adopted exits."""
        for _ in range(MAX_TRACKED_PROCESSES):
            status = _subreaper_wait_peek()
            if status == 'ECHILD':
                if self.process is not None and self.process.returncode is None:
                    raise RuntimeError('root disappeared from kernel wait ownership before Popen reaped it')
                self.audit['kernel_proof'].update(root_reaped=self.process is not None,
                                                  final_echild=True)
                return True
            if status is None:
                return False
            if self.process is not None and status.si_pid == self.process.pid:
                if self.process.returncode is not None:
                    raise RuntimeError('kernel root exit conflicts with recorded Popen return code')
                self.process.poll()  # The registered Popen alone owns this status.
            else:
                pid, exit_status = os.waitpid(status.si_pid, os.WNOHANG | _WAIT_ALL)
                if pid != status.si_pid:
                    raise RuntimeError('adopted child status changed during exclusive wait')
                if len(self.audit['reaped_descendants']) >= MAX_TRACKED_PROCESSES:
                    raise ValueError('subreaper adopted status capacity exceeded')
                self.audit['reaped_descendants'].append({'pid': pid, 'wait_status': exit_status})
        raise ValueError('subreaper wait-drain capacity exceeded')

    def _direct_children(self):
        """Union owner thread children; an empty census never proves exhaustion."""
        children = set()
        tasks = list(Path(f'/proc/{os.getpid()}/task').iterdir())
        if len(tasks) > MAX_TRACKED_PROCESSES:
            raise ValueError('subreaper thread census capacity exceeded')
        for task in tasks:
            try:
                children.update(_process_children(int(task.name), strict=True))
            except ProcessLookupError:
                continue  # A thread exit is discharged only by final kernel proof.
        if len(children) > MAX_TRACKED_PROCESSES:
            raise ValueError('subreaper direct-child capacity exceeded')
        return children

    def _signal_direct(self, signum):
        for pid in self._direct_children():
            identity = _process_identity(pid, strict=True)
            if identity is None:
                continue
            if identity['parent_pid'] != os.getpid():
                raise RuntimeError('candidate is not an exclusively owned direct child')
            self._retain({pid: identity})
            key = (pid, identity['start_ticks'], int(signum))
            if key in self._sent or identity['state'] == 'Z':
                continue
            # An unreaped direct child cannot have its PID recycled while this
            # exclusive waiter is paused. Recheck after opening the kernel fd.
            try:
                descriptor = os.pidfd_open(pid, 0)
            except ProcessLookupError:
                continue
            try:
                current = _process_identity(pid, strict=True)
                if current is None:
                    continue
                if (current['start_ticks'] != identity['start_ticks']
                        or current['parent_pid'] != os.getpid()):
                    raise RuntimeError('owned child identity changed before pidfd signal')
                signal.pidfd_send_signal(descriptor, signum)
                self._sent.add(key)
                self.audit['signals'].append({'pid': pid, 'start_ticks': identity['start_ticks'],
                    'signal': int(signum), 'pidfd': True,
                    **({'transport': 'adopted_or_direct_pidfd', 'sent': True,
                        'monotonic': time.monotonic(),
                        'phase': {signal.SIGINT: 'graceful', signal.SIGTERM: 'terminate',
                                  signal.SIGKILL: 'kill'}[signum]}
                       if self.mode == 'subreaper_group_v3' else {})})
            except ProcessLookupError:
                pass
            finally:
                os.close(descriptor)

    def _signal_initial_root_group(self):
        """Send one graceful SIGINT while the exclusive owner pins the root.

        The unreaped direct child reserves PID=SID=PGID. No waiter runs between
        the kernel/identity guard and killpg. Only this original group receives
        the signal; the recorder retains its separately sessioned bag/target.
        """
        self._group_graceful_attempted = True
        row = {'transport': 'killpg_unreaped_root', 'phase': 'graceful',
            'signal': int(signal.SIGINT), 'pidfd': False, 'sent': False,
            'monotonic': time.monotonic(), 'no_reap_guard': False,
            'process_group_id': self.process.pid,
            'leader_identity': dict(self._root_identity or {})}
        self.audit['signals'].append(row)
        if self.process.returncode is not None:
            row.update(context='root_already_reaped_use_adopted_pidfds',
                       completed_monotonic=time.monotonic())
            return
        try:
            if self._root_identity is None:
                raise RuntimeError('original root identity unavailable for graceful group signal')
            # WNOWAIT checks actual wait ownership, including a retained zombie,
            # without stealing the Popen status or releasing the pinned PID.
            try:
                os.waitid(os.P_PID, self.process.pid,
                    os.WEXITED | os.WNOHANG | os.WNOWAIT | _WAIT_ALL)
            except ChildProcessError as error:
                raise RuntimeError('root is no longer exclusively wait-owned') from error
            current = _process_identity(self.process.pid, strict=True)
            original = self._root_identity
            if (current is None or current['pid'] != self.process.pid
                    or original['pid'] != self.process.pid
                    or current['start_ticks'] != original['start_ticks']
                    or any(identity['parent_pid'] != os.getpid()
                        or identity['session_id'] != self.process.pid
                        or identity['process_group_id'] != self.process.pid
                        for identity in (original, current))):
                raise RuntimeError('unreaped root parent/session/group identity guard failed')
            if _deadline_remaining(self.end) <= 0:
                raise TimeoutError('graceful group signal exceeded original deadline')
            row.update(leader_identity=dict(current), no_reap_guard=True,
                       monotonic=time.monotonic())
            # Do not poll/wait/reap here: the original direct child pins the
            # group number even if it exits between this guard and the send.
            os.killpg(self.process.pid, signal.SIGINT)
            row['sent'] = True
            self._sent.add((self.process.pid, original['start_ticks'], int(signal.SIGINT)))
        except Exception as error:
            self._group_graceful_failed = True
            row['error'] = f'{type(error).__name__}: {error}'
            raise
        finally:
            row['completed_monotonic'] = time.monotonic()

    def _signal_phase(self, signum):
        if self.mode == 'subreaper_group_v3' and signum == signal.SIGINT:
            if not self._group_graceful_attempted:
                self._signal_initial_root_group()
            # A failed guard is not permission to use weaker graceful delivery.
            # While the recorder's wrapper remains, let its owner finalize all
            # resources; even previously adopted target descendants must wait.
            if self._group_graceful_failed or self.process.returncode is None:
                return
        self._signal_direct(signum)

    def cancel(self, process, grace_sec, drain_output):
        self.observe(process)
        output = None
        interrupt_end = min(self.end-2*self.escalation, time.monotonic()+grace_sec)
        term_end = min(self.end-self.escalation, max(time.monotonic(), interrupt_end)+self.escalation)
        kill_end = min(self.end, max(time.monotonic(), term_end)+self.escalation)
        phases = ((signal.SIGINT, interrupt_end), (signal.SIGTERM, term_end),
                  (signal.SIGKILL, kill_end))
        for signum, phase_end in phases:
            while True:
                try:
                    if self._drain():
                        break
                    self._signal_phase(signum)
                except Exception as error:
                    self._error(error)
                remaining = min(phase_end, self.end)-time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(.05, remaining))
            if self.audit['kernel_proof']['final_echild']:
                break
        if drain_output and process.returncode is not None:
            try:
                output, _ = process.communicate(timeout=_deadline_remaining(self.end))
            except subprocess.TimeoutExpired as error:
                output = error.output
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
        return output

    def finish(self):
        global _ACTIVE_SUBREAPER
        if self.closed:
            return self.audit
        try:
            if self.process is not None:
                if not self._drain():
                    self.cancel(self.process, self.grace, False)
                self._drain()
            else:
                self.audit['kernel_proof']['final_echild'] = _subreaper_wait_peek() == 'ECHILD'
            if _subreaper_setting() != 1 or _subreaper_sigchld() != self.audit['sigchld_action']:
                raise RuntimeError('subreaper or native SIGCHLD ownership changed')
            if not self.audit['kernel_proof']['final_echild']:
                raise RuntimeError('kernel children remain at ownership deadline')
        except Exception as error:
            self._error(error)
        finally:
            proof = self.audit['kernel_proof']
            if proof['final_echild']:
                try:
                    proof['state_restored'] = _subreaper_setting(self.previous) == self.previous
                except Exception as error:
                    self._error(error)
            proof['complete'] = bool(self.audit['inspection_complete'] and time.monotonic() <= self.end
                and all(proof[key] for key in ('baseline_echild', 'subreaper_verified', 'root_reaped',
                    'final_echild', 'scope_exclusive', 'sigchld_valid', 'state_restored')))
            self.audit['inspection_complete'] = proof['complete']
            self.audit['completed_monotonic'] = time.monotonic()
            _ACTIVE_SUBREAPER = None
            _SUBREAPER_LOCK.release()
            self.closed = True
        return self.audit


def ensure_ros_daemon():
    """Start shared ros2cli discovery outside any per-run process session."""
    subprocess.run(
        ['ros2', 'daemon', 'start'],
        check=True, capture_output=True, text=True, timeout=15.0,
    )


def _process_identity(pid, *, strict=False):
    """Read one Linux process identity without trusting a reusable PID."""
    try:
        stat_text = Path(f'/proc/{int(pid)}/stat').read_text(
            encoding='utf-8'
        )
    except OSError as error:
        if isinstance(error, FileNotFoundError) or error.errno in (errno.ENOENT, errno.ESRCH):
            return None
        if strict:
            raise
        return None
    except ValueError:
        if strict:
            raise
        return None
    closing_parenthesis = stat_text.rfind(')')
    if closing_parenthesis < 0:
        if strict:
            raise ValueError('malformed procfs process identity')
        return None
    fields = stat_text[closing_parenthesis + 2:].split()
    if len(fields) <= 19:
        if strict:
            raise ValueError('incomplete procfs process identity')
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
        if strict:
            raise
        return None


def _process_children(pid, *, strict=False):
    """Read the direct children of one process from procfs."""
    try:
        children_text = Path(
            f'/proc/{int(pid)}/task/{int(pid)}/children'
        ).read_text(encoding='utf-8')
        return [int(value) for value in children_text.split()]
    except OSError as error:
        if strict:
            if (isinstance(error, FileNotFoundError)
                    or error.errno in (errno.ENOENT, errno.ESRCH)):
                if _process_identity(pid, strict=True) is None:
                    # A vanished process may have left unobserved descendants.
                    # Absence here cannot establish exhaustive tree inspection.
                    raise ProcessLookupError(errno.ESRCH,
                        'process disappeared before child enumeration') from error
            raise
        return []
    except ValueError:
        if strict:
            raise
        return []


def _snapshot_process_tree(root_pid, *, strict=False):
    """Snapshot descendants, including nested sessions, before signaling."""
    snapshot = {}
    pending = [int(root_pid)]
    stage = 'identity'
    try:
        while pending:
            pid = pending.pop()
            if pid in snapshot:
                continue
            stage = 'identity'
            identity = (_process_identity(pid, strict=True) if strict
                        else _process_identity(pid))
            if identity is None:
                if strict:
                    raise ProcessLookupError(errno.ESRCH,
                        'process disappeared before tree enumeration')
                continue
            snapshot[pid] = identity
            stage = 'children'
            pending.extend(_process_children(pid, strict=True) if strict
                           else _process_children(pid))
    except Exception as error:
        if strict:
            error.owned_process_snapshot = dict(snapshot)
            error.inspection_pid = pid
            error.inspection_stage = stage
        raise
    return snapshot


def _matching_process(identity, *, strict=False):
    """Return the current identity only when the snapshotted PID is unchanged."""
    current = (_process_identity(identity['pid'], strict=True) if strict
               else _process_identity(identity['pid']))
    if current is None or current['state'] == 'Z':
        return None
    if current['start_ticks'] != identity['start_ticks']:
        return None
    return current


def _live_snapshot_processes(snapshot, *, strict=False):
    """Return unchanged, non-zombie processes from one owned tree snapshot."""
    live = {}
    for pid, identity in snapshot.items():
        current = (_matching_process(identity, strict=True) if strict
                   else _matching_process(identity))
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


def _signal_owned_process_group(process_group_id, identities, signum, *, strict=False):
    """Signal a group only while an original member still matches procfs."""
    if process_group_id <= 0 or process_group_id == os.getpgrp():
        return False
    safe_member_found = False
    for identity in identities:
        current = (_matching_process(identity, strict=True) if strict
                   else _matching_process(identity))
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


def _deadline_remaining(absolute_deadline):
    """Return one monotonic budget; expiration never starts a new interval."""
    if (isinstance(absolute_deadline, bool)
            or not isinstance(absolute_deadline, (int, float))
            or not math.isfinite(absolute_deadline)):
        raise ValueError('absolute_deadline must be finite monotonic seconds')
    return max(0.0, absolute_deadline - time.monotonic())


def _wait_for_cancelled_tree(
    process,
    snapshot,
    timeout_sec,
    drain_output,
    *,
    absolute_deadline=None,
):
    """Wait boundedly for the leader and every snapshotted descendant."""
    if absolute_deadline is not None:
        _deadline_remaining(absolute_deadline)
        if (isinstance(timeout_sec, bool)
                or not isinstance(timeout_sec, (int, float))
                or not math.isfinite(timeout_sec) or timeout_sec < 0.0):
            raise ValueError('selected wait timeout must be finite nonnegative seconds')
        wait_end = min(absolute_deadline, time.monotonic() + timeout_sec)
        output = None
        remaining = _deadline_remaining(wait_end)
        if remaining > 0.0:
            try:
                if drain_output:
                    output, _ = process.communicate(timeout=remaining)
                else:
                    process.wait(timeout=remaining)
            except subprocess.TimeoutExpired as error:
                output = error.output
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
        while True:
            leader_reaped = process.poll() is not None  # WNOHANG, including at expiry.
            live = _live_snapshot_processes(snapshot, strict=True)
            if leader_reaped and not live:
                return True, live, output
            remaining = _deadline_remaining(wait_end)
            if remaining <= 0.0:
                return leader_reaped, live, output
            time.sleep(min(0.05, remaining))
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


def _cancel_scoped_process(process, shutdown_grace_sec, drain_output, *, absolute_deadline=None):
    """Stop the owned tree. Selected deadline calls return stdout plus an audit."""
    if _ACTIVE_SUBREAPER is not None and _ACTIVE_SUBREAPER.process is process:
        output = _ACTIVE_SUBREAPER.cancel(process, shutdown_grace_sec, drain_output)
        if absolute_deadline is None:
            return output
        return {'stdout': output, 'audit': _ACTIVE_SUBREAPER.audit}
    if absolute_deadline is not None:
        _deadline_remaining(absolute_deadline)
        for value in (shutdown_grace_sec, CANCEL_ESCALATION_SEC):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0.0):
                raise ValueError('selected shutdown intervals must be finite nonnegative seconds')
        audit_limit = 256
        audit = {
            'absolute_deadline': absolute_deadline,
            'started_monotonic': time.monotonic(),
            'inspection_complete': True,
            'inspection_errors': [],
            'signals': [],
            'signals_count': 0,
            'audit_truncated': False,
        }
        snapshot, live, output = {}, {}, None
        leader_reaped = False
        try:
            snapshot = _snapshot_process_tree(process.pid, strict=True)
            if process.pid not in snapshot:
                audit['inspection_complete'] = False
                audit['inspection_errors'].append('original root identity unavailable')
            live = _live_snapshot_processes(snapshot, strict=True)
        except Exception as error:
            audit['inspection_complete'] = False
            audit['inspection_errors'].append(f'{type(error).__name__}: {error}')
            snapshot.update(getattr(error, 'owned_process_snapshot', {}))
            # Failed enumeration must not hide its failure, but an independently
            # verified direct-child identity still permits a scoped stop attempt.
            try:
                root = _process_identity(process.pid, strict=True)
                if root is not None:
                    snapshot.setdefault(process.pid, root)
                live = _live_snapshot_processes(snapshot, strict=True)
            except Exception:
                live = dict(snapshot)
        audit['owned_snapshot_count'] = len(snapshot)
        audit['owned_snapshot'] = [snapshot[pid] for pid in sorted(snapshot)[:audit_limit]]
        audit['audit_truncated'] = len(snapshot) > audit_limit
        signal_levels = {}

        def signal_group(group, identities, signum):
            try:
                signalled = _signal_owned_process_group(group, identities, signum, strict=True)
            except Exception as error:
                audit['inspection_complete'] = False
                if len(audit['inspection_errors']) < 8:
                    audit['inspection_errors'].append(f'{type(error).__name__}: {error}')
                signalled = False
            audit['signals_count'] += 1
            if len(audit['signals']) < audit_limit:
                audit['signals'].append({'process_group_id': group,
                    'signal': int(signum), 'signalled': signalled})
            else:
                audit['audit_truncated'] = True
            return signalled

        def wait(interval):
            nonlocal leader_reaped, live, output
            try:
                leader_reaped, live, captured = _wait_for_cancelled_tree(
                    process, snapshot, interval, drain_output,
                    absolute_deadline=absolute_deadline)
                if captured is not None:
                    output = captured
            except Exception as error:
                audit['inspection_complete'] = False
                if len(audit['inspection_errors']) < 8:
                    audit['inspection_errors'].append(f'{type(error).__name__}: {error}')
                # Do not convert failed inspection into an empty/clean tree.
                live = dict(snapshot)
                try:
                    leader_reaped = process.poll() is not None
                except Exception:
                    leader_reaped = False

        root = snapshot.get(process.pid)
        if root is not None and root['process_group_id'] == process.pid:
            if signal_group(process.pid, [root], signal.SIGINT):
                signal_levels[process.pid] = 1
        # Unlike the default path, unavailable identity never permits a raw
        # killpg fallback. Reserve escalation before allocating graceful wait.
        graceful = min(shutdown_grace_sec, max(0.0,
            _deadline_remaining(absolute_deadline) - 3 * CANCEL_ESCALATION_SEC))
        wait(graceful)
        escalation_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGKILL)
        for _ in escalation_signals:
            if leader_reaped and not live and audit['inspection_complete']:
                break
            groups = _owned_process_groups(snapshot, live)
            for group, identities in groups.items():
                level = signal_levels.get(group, 0)
                if level < len(escalation_signals):
                    if signal_group(group, identities, escalation_signals[level]):
                        signal_levels[group] = level + 1
            wait(min(CANCEL_ESCALATION_SEC, _deadline_remaining(absolute_deadline)))
        audit.update(
            completed_monotonic=time.monotonic(), leader_reaped=leader_reaped,
            remaining_owned_count=(len(live) if audit['inspection_complete'] else None),
            remaining_owned=[live[pid] for pid in sorted(live)[:audit_limit]],
        )
        audit['audit_truncated'] |= len(live) > audit_limit
        audit['deadline_exhausted'] = audit['completed_monotonic'] >= absolute_deadline
        audit['cleanup_complete'] = bool(audit['inspection_complete']
            and not audit['audit_truncated'] and not audit['deadline_exhausted']
            and leader_reaped and not live)
        return {'stdout': output, 'audit': audit}
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
    *, strict_process_tracking=False,
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
    ownership = _process_tracking(strict_process_tracking)
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
            if _ACTIVE_SUBREAPER is not None and time.monotonic() >= _ACTIVE_SUBREAPER.work_end:
                raise TimeoutError('selected setup exhausted the original work deadline before launch')
            process = subprocess.Popen(
                command,
                cwd=REPOSITORY_ROOT,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            deadline = time.monotonic() + wall_timeout_sec
            if _ACTIVE_SUBREAPER is not None:
                deadline = min(deadline, _ACTIVE_SUBREAPER.work_end)
            _track_owned_processes(process, ownership)
            while process.poll() is None:
                _track_owned_processes(process, ownership)
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
    result = {
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
    if ownership is not None:
        result['process_ownership'] = ownership
    return result


def _requires_ranked_goal(resolved):
    return bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'extremum_classification_mode') == 'counted_candidates'
        and resolved.get('success', {}).get('criterion') != POST_RECOVERY_ARRIVAL_CRITERION
    )


def _run_record_to_global_proximity(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    resolved,
    *, strict_process_tracking=False,
):
    """Stop only at a verified post-recovery global odometry sample."""
    from copy import deepcopy

    context = rclpy.context.Context()
    context_initialized = False
    node = None
    executor = None
    node_added = False
    process = None
    primary_error = None
    ownership = _process_tracking(strict_process_tracking)
    sequence = 0
    state_messages = []
    event_messages = []
    fill_records = []
    centroid_records, timekeeper_records = [], []
    centroid_selection = _m4_centroid_event_selection(resolved)
    pde_selection = _m4_pde_event_selection(resolved)
    typed_timestamp_selected = centroid_selection is not None or pde_selection is not None
    confirmation_records, legacy_records = [], []
    observed = {
        'stage_a': False,
        'fill_cardinality': False,
        'stage_a_evidence': None,
        'stage_a_completion_evidence': None,
        'stage_error': None,
        'centroid_event_timestamp_bindings': [],
        'centroid_event_timestamp_binding_error': None,
        'pde_event_timestamp_bindings': [],
        'pde_event_timestamp_binding_error': None,
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
    observes_ranked_goal = bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'extremum_classification_mode'
        ) == 'counted_candidates'
    )
    requires_ranked_goal = _requires_ranked_goal(resolved)
    sources = {source['id']: source for source in resolved['sources']}
    global_source = sources[staged_contract['global_source_id']]

    def next_sequence():
        nonlocal sequence
        sequence += 1
        return sequence

    def refresh_stage_a():
        selected_events = event_messages
        binding_error = None
        if centroid_selection is not None:
            selected_events, bindings, binding_error = _centroid_convergence_evaluation_events(
                resolved, state_messages, event_messages, centroid_records, timekeeper_records)
            observed['centroid_event_timestamp_bindings'] = bindings
            observed['centroid_event_timestamp_binding_error'] = binding_error
        elif pde_selection is not None:
            selected_events, bindings, binding_error = _moving_pde_convergence_evaluation_events(
                resolved, state_messages, event_messages, confirmation_records, legacy_records, timekeeper_records)
            observed['pde_event_timestamp_bindings'] = bindings
            observed['pde_event_timestamp_binding_error'] = binding_error
        (
            stage_a_passed,
            cardinality_passed,
            evidence,
            error,
        ) = _staged_recovery_evidence(
            resolved,
            state_messages,
            selected_events,
            fill_records,
        )
        observed['stage_a'] = stage_a_passed is True and binding_error is None
        observed['fill_cardinality'] = cardinality_passed is True and binding_error is None
        observed['stage_a_evidence'] = evidence
        observed['stage_error'] = binding_error or error
        if (
            typed_timestamp_selected
            and observed['stage_a_completion_evidence'] is None
            and observed['stage_a']
            and observed['fill_cardinality']
            and observed['stage_error'] is None
        ):
            # Historical completion advances the clock only. The current
            # full-history verdict above still controls new acceptance.
            observed['stage_a_completion_evidence'] = deepcopy(evidence)

    def centroid_callback(message):
        if message.confirmed:
            centroid_records.append((next_sequence(), message))
            refresh_stage_a()

    def confirmation_callback(message):
        confirmation_records.append((next_sequence(), message))
        refresh_stage_a()

    def legacy_callback(message):
        legacy_records.append((next_sequence(), message))
        refresh_stage_a()

    def timekeeper_callback(message):
        # Preserve all distinct origins/modes; exact heartbeat repeats add no
        # new authority. Ordinary cross-topic arrival can complete a pending join.
        if not any((old.mode, old.start_time) == (message.mode, message.start_time)
                   for _, old in timekeeper_records):
            timekeeper_records.append((next_sequence(), message))
            refresh_stage_a()

    def state_callback(message):
        state_messages.append((next_sequence(), message))
        refresh_stage_a()

    def event_callback(message):
        callback_sequence = next_sequence()
        event_messages.append((callback_sequence, message))
        if (
            observes_ranked_goal
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
        current_evidence_valid = (
            observed['stage_a'] and observed['fill_cardinality']
            and (not typed_timestamp_selected or observed['stage_error'] is None)
        )
        completion_evidence = (
            observed['stage_a_completion_evidence']
            if typed_timestamp_selected
            else observed['stage_a_evidence']
        )
        stage_a_complete = (
            completion_evidence is not None
            if typed_timestamp_selected
            else current_evidence_valid
        )
        if not stage_a_complete:
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
        completion_sequence = completion_evidence.get(
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
            current_evidence_valid
            and approach_radius is not None
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
            current_evidence_valid
            and closer_radius is not None
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
        if not typed_timestamp_selected and not observed['fill_cardinality']:
            return
        ranked_goal_sequence = None
        ranked_goal_ready = not requires_ranked_goal
        if requires_ranked_goal:
            ranked_goal = observed['controller_ranked_goal_evidence']
            if ranked_goal is not None:
                ranked_goal_sequence = ranked_goal['callback_sequence']
                ranked_goal_ready = sample_sequence > ranked_goal_sequence
        if (
            current_evidence_valid
            and ranked_goal_ready
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
        if centroid_selection is not None:
            from ros_esc_interfaces.msg import CentroidConvergenceDiagnostics, RecurrentConvergenceDiagnostics, Timekeeper
            diagnostic_type = (RecurrentConvergenceDiagnostics if centroid_selection['metric_mode'] ==
                               'recurrent_geometry_v3' else CentroidConvergenceDiagnostics)
            node.create_subscription(diagnostic_type,
                centroid_selection['diagnostic_topic'], centroid_callback, 10)
            node.create_subscription(Timekeeper,
                centroid_selection['timekeeper_topic'], timekeeper_callback, 10)
        elif pde_selection is not None:
            from ros_esc_interfaces.msg import DetectorConfirmation, StampedFloat64MultiArray, Timekeeper
            node.create_subscription(DetectorConfirmation, pde_selection['confirmation_topic'], confirmation_callback, 10)
            node.create_subscription(StampedFloat64MultiArray, pde_selection['legacy_topic'], legacy_callback, 10)
            node.create_subscription(Timekeeper, pde_selection['timekeeper_topic'], timekeeper_callback, 10)
        with tempfile.TemporaryFile(mode='w+t', encoding='utf-8') as output:
            if _ACTIVE_SUBREAPER is not None and time.monotonic() >= _ACTIVE_SUBREAPER.work_end:
                raise TimeoutError('selected setup exhausted the original work deadline before launch')
            process = subprocess.Popen(
                command,
                cwd=REPOSITORY_ROOT,
                stdout=output,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            deadline = time.monotonic() + wall_timeout_sec
            if _ACTIVE_SUBREAPER is not None:
                deadline = min(deadline, _ACTIVE_SUBREAPER.work_end)
            _track_owned_processes(process, ownership)
            while process.poll() is None:
                _track_owned_processes(process, ownership)
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
        **({'centroid_event_timestamp_bindings_live': observed['centroid_event_timestamp_bindings'],
            'centroid_event_timestamp_binding_error_live': observed['centroid_event_timestamp_binding_error'],
            'stage_a_completion_evidence_live': observed['stage_a_completion_evidence']}
           if centroid_selection is not None else {}),
        **({'pde_event_timestamp_bindings_live': observed['pde_event_timestamp_bindings'],
            'pde_event_timestamp_binding_error_live': observed['pde_event_timestamp_binding_error'],
            'stage_a_completion_evidence_live': observed['stage_a_completion_evidence']}
           if pde_selection is not None else {}),
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
    if ownership is not None:
        result['process_ownership'] = ownership
    return result


def run_record_process(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    anchor_state=None,
    boundary_state=None,
    boundary_required_events=None,
    staged_recovery=None,
    *,
    absolute_deadline=None,
    strict_process_tracking=False,
    process_ownership_mode='observed_tree_v1',
):
    """Select the preserved tree owner or an exclusive kernel ancestry witness."""
    if process_ownership_mode not in ('observed_tree_v1', 'subreaper_v2', 'subreaper_group_v3'):
        raise ValueError('unknown process ownership mode')
    arguments = dict(anchor_state=anchor_state, boundary_state=boundary_state,
        boundary_required_events=boundary_required_events, staged_recovery=staged_recovery)
    if process_ownership_mode == 'observed_tree_v1':
        return _run_record_process_observed(command, wall_timeout_sec, shutdown_grace_sec,
            **arguments, absolute_deadline=absolute_deadline,
            strict_process_tracking=strict_process_tracking)
    if absolute_deadline is None:
        raise ValueError('subreaper_v2 requires an explicit absolute deadline')
    for value in (wall_timeout_sec, shutdown_grace_sec, CANCEL_ESCALATION_SEC):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError('selected process timing must be finite nonnegative seconds')
    reserve = shutdown_grace_sec + 3*CANCEL_ESCALATION_SEC
    started = time.monotonic()
    work_end = min(started+wall_timeout_sec, absolute_deadline-reserve)
    if wall_timeout_sec <= 0 or work_end <= started:
        raise ValueError('subreaper_v2 has insufficient work and shutdown reserve')
    owner = _SubreaperOwner(absolute_deadline, shutdown_grace_sec,
        process_ownership_mode=process_ownership_mode).start()
    owner.work_end = work_end
    try:
        remaining = work_end-time.monotonic()
        if remaining <= 0:
            raise ValueError('subreaper setup exhausted its work budget')
        # The existing plain/specialized polling and scientific callbacks are
        # unchanged. Their selected tracker/cancellation use this one owner.
        result = _run_record_process_observed(command, remaining, shutdown_grace_sec,
            **arguments, strict_process_tracking=True)
    except BaseException as error:
        error.process_ownership = owner.finish()
        error.execution_deadline_audit = {'absolute_deadline': absolute_deadline,
            'started_monotonic': started, 'work_deadline': work_end,
            'shutdown_reserve_sec': reserve, 'completed_monotonic': time.monotonic(),
            'deadline_exhausted': time.monotonic() >= absolute_deadline,
            'owned_descendant_cleanup_proven': owner.audit['kernel_proof']['complete']}
        raise
    else:
        result['process_ownership'] = owner.finish()
        result['deadline_audit'] = {'absolute_deadline': absolute_deadline,
            'started_monotonic': started, 'work_deadline': work_end,
            'shutdown_reserve_sec': reserve, 'completed_monotonic': time.monotonic(),
            'deadline_exhausted': time.monotonic() >= absolute_deadline,
            'work_timed_out': result['timed_out'],
            'owned_descendant_cleanup_proven': owner.audit['kernel_proof']['complete']}
        return result


def _run_record_process_observed(
    command,
    wall_timeout_sec,
    shutdown_grace_sec,
    anchor_state=None,
    boundary_state=None,
    boundary_required_events=None,
    staged_recovery=None,
    *,
    absolute_deadline=None,
    strict_process_tracking=False,
):
    """Run record_run with a wall timeout and scoped session escalation."""
    deadline_audit = None
    if absolute_deadline is not None:
        remaining = _deadline_remaining(absolute_deadline)
        if any(value is not None for value in (
                anchor_state, boundary_state, boundary_required_events, staged_recovery)):
            raise ValueError('absolute_deadline supports only the plain outer process route')
        for value, name in ((wall_timeout_sec, 'wall_timeout_sec'),
                            (shutdown_grace_sec, 'shutdown_grace_sec'),
                            (CANCEL_ESCALATION_SEC, 'CANCEL_ESCALATION_SEC')):
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0.0):
                raise ValueError(name + ' must be finite nonnegative seconds')
        reserve = shutdown_grace_sec + 3 * CANCEL_ESCALATION_SEC
        if wall_timeout_sec <= 0.0 or remaining <= reserve:
            raise ValueError('absolute_deadline has insufficient work and shutdown reserve')
        started = time.monotonic()
        deadline_audit = {
            'absolute_deadline': absolute_deadline,
            'started_monotonic': started,
            'work_deadline': min(started + wall_timeout_sec, absolute_deadline - reserve),
            'shutdown_reserve_sec': reserve,
            'cancellation': None,
            'owned_descendant_cleanup_proven': False,
        }
    if boundary_state is not None and staged_recovery is not None:
        raise ValueError('only one live graceful-stop contract is allowed')
    if staged_recovery is not None:
        return _run_record_to_global_proximity(
            command,
            wall_timeout_sec,
            shutdown_grace_sec,
            staged_recovery,
            **({'strict_process_tracking': True} if strict_process_tracking else {}),
        )
    if boundary_state is not None:
        return _run_record_to_boundary(
            command,
            wall_timeout_sec,
            shutdown_grace_sec,
            anchor_state,
            boundary_state,
            list(boundary_required_events or []),
            **({'strict_process_tracking': True} if strict_process_tracking else {}),
        )
    if deadline_audit is not None and _deadline_remaining(absolute_deadline) <= reserve:
        raise ValueError('absolute_deadline no longer has work and shutdown reserve before launch')
    if _ACTIVE_SUBREAPER is not None and time.monotonic() >= _ACTIVE_SUBREAPER.work_end:
        raise TimeoutError('selected setup exhausted the original work deadline before launch')
    process = subprocess.Popen(
        command,
        cwd=REPOSITORY_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    timed_out = False
    ownership = _process_tracking(strict_process_tracking)
    _track_owned_processes(process, ownership)
    try:
        try:
            work_timeout = (wall_timeout_sec if deadline_audit is None
                            else _deadline_remaining(deadline_audit['work_deadline']))
            if deadline_audit is not None and work_timeout <= 0.0:
                raise subprocess.TimeoutExpired(command, 0.0)
            if ownership is None:
                output, _ = process.communicate(timeout=work_timeout)
            else:
                work_end = time.monotonic() + work_timeout
                if _ACTIVE_SUBREAPER is not None:
                    work_end = min(work_end, _ACTIVE_SUBREAPER.work_end)
                while True:
                    _track_owned_processes(process, ownership)
                    remaining = work_end - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(command, work_timeout)
                    try:
                        output, _ = process.communicate(timeout=min(.1, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        if time.monotonic() >= work_end:
                            raise
        except subprocess.TimeoutExpired as error:
            timed_out = True
            if deadline_audit is None:
                output = _cancel_scoped_process(
                    process, shutdown_grace_sec, drain_output=True)
            else:
                deadline_audit['work_end_monotonic'] = time.monotonic()
                cancellation = _cancel_scoped_process(
                    process, shutdown_grace_sec, drain_output=True,
                    absolute_deadline=absolute_deadline)
                deadline_audit['cancellation'] = cancellation['audit']
                output = cancellation['stdout']
                if output is None:
                    output = error.output
                    if isinstance(output, bytes):
                        output = output.decode('utf-8', errors='replace')
            if output is None:
                output = ''
    except BaseException as error:
        if deadline_audit is None:
            _cancel_scoped_process(process, shutdown_grace_sec, drain_output=True)
        else:
            deadline_audit.setdefault('work_end_monotonic', time.monotonic())
            try:
                cancellation = _cancel_scoped_process(
                    process, shutdown_grace_sec, drain_output=True,
                    absolute_deadline=absolute_deadline)
                deadline_audit['cancellation'] = cancellation['audit']
            except BaseException as cleanup_error:
                deadline_audit['cancellation_error'] = (
                    f'{type(cleanup_error).__name__}: {cleanup_error}')
            deadline_audit['completed_monotonic'] = time.monotonic()
            deadline_audit['deadline_exhausted'] = (
                deadline_audit['completed_monotonic'] >= absolute_deadline)
            deadline_audit['work_timed_out'] = timed_out
            if deadline_audit['cancellation'] is not None:
                deadline_audit['owned_descendant_cleanup_proven'] = (
                    deadline_audit['cancellation']['cleanup_complete'])
            error.execution_deadline_audit = deadline_audit
        raise
    result = {
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
    if deadline_audit is not None:
        deadline_audit.setdefault('work_end_monotonic', time.monotonic())
        deadline_audit['completed_monotonic'] = time.monotonic()
        deadline_audit['deadline_exhausted'] = (
            deadline_audit['completed_monotonic'] >= absolute_deadline)
        deadline_audit['work_timed_out'] = timed_out
        if deadline_audit['cancellation'] is not None:
            deadline_audit['owned_descendant_cleanup_proven'] = (
                deadline_audit['cancellation']['cleanup_complete'])
        result['deadline_audit'] = deadline_audit
    if ownership is not None:
        result['process_ownership'] = ownership
    return result


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
        'escape_command_ownership_passed': None,
        'escape_command_ownership': None,
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


def _m4_centroid_event_selection(resolved):
    """Resolve only the explicitly selected M4 centroid evaluator route."""
    from ros_esc.convergence_detector_node.centroid_contract import CENTROID_METRIC_MODES
    from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
    values = resolved.get('algorithm', {}).get('launch_overrides', {})
    if (resolved.get('suite_id') not in ('m4_pilot_v1', 'm4_pilot_v2', 'm4_pilot_v3', 'm4_pilot_v4', 'm4_pilot_v5', 'm4_pilot_v6', 'm4_pilot_v7', 'm4_pilot_v8', 'm4_pilot_v9', *ARRIVAL_SUITE_IDS, 'v2_method_development_v1')
            or values.get('convergence_metric_mode', 'pde_mean_v1') not in (*CENTROID_METRIC_MODES, RECURRENT_MODE)):
        return None
    moving = values.get('continuous_search_mode', 'stationary_v1') == 'rolling_gesc_v2'
    if values['convergence_metric_mode'] == RECURRENT_MODE and not moving:
        if resolved.get('suite_id') not in ('v2_method_development_v1', *ARRIVAL_SUITE_IDS):
            raise ValueError('stationary recurrent evaluation requires selected method development simulation')
    delayed = resolved.get('disturbances', {}).get('pose_delay_sec', 0.) > 0
    return dict(metric_mode=values['convergence_metric_mode'],
        diagnostic_topic=(values.get('recurrent_diagnostics_topic', RECURRENT_TOPIC)
            if values['convergence_metric_mode'] == RECURRENT_MODE else
            values.get('convergence_diagnostics_topic', '/gesc_gaussian/v2/convergence_diagnostics')),
        timekeeper_topic=(build_v2_stream_config(resolved)['timekeeper_topic'] if moving else
                          values.get('stationary_timekeeper_topic', '/turtlebot3/timekeeper_chatter')),
        pose_topic=values.get('algorithm_pose_topic',
            '/gesc_gaussian/simulation/pose_delayed' if delayed else '/odom'),
        window_sec=values.get('centroid_window_sec', 3.),
        epsilon_m=values.get('centroid_epsilon_m', .06),
        maximum_radius_m=values.get('centroid_maximum_radius_m', .5),
        maximum_source_gap_sec=values.get('centroid_maximum_gap_sec', .5),
        pose_freshness_sec=values.get('centroid_pose_stale_sec', .5))


def _m4_pde_event_selection(resolved):
    """Opt in only the existing explicit moving-PDE evaluation suites."""
    values = resolved.get('algorithm', {}).get('launch_overrides', {})
    if (resolved.get('suite_id') not in (*ARRIVAL_SUITE_IDS, 'v2_method_development_v1')
            or values.get('continuous_search_mode', 'stationary_v1') != 'rolling_gesc_v2'
            or values.get('convergence_metric_mode', 'pde_mean_v1') != 'pde_mean_v1'):
        return None
    config = build_v2_stream_config(resolved)
    return dict(stream_config=config, timekeeper_topic=config['timekeeper_topic'],
                confirmation_topic='/gesc_gaussian/v2/detector_confirmation',
                legacy_topic='/gesc_gaussian/convergence_status')


def _moving_pde_convergence_evaluation_events(resolved, state_messages, event_messages,
                                      confirmation_records=(), legacy_records=(),
                                      timekeeper_records=()):
    """Bind canonical PDE mirrors before adapting a detached evaluator copy.

    The public PDE coordinate is the legacy model clock. The typed confirmation
    supplies actual input support, also retained by the snapshot and fill.
    Missing cross-topic joins remain pending live and errors in the final audit.
    """
    from copy import deepcopy
    from ros_esc.experiment_recording.record_run import v2_message_identity_error
    from ros_esc.v2_lifecycle import FRESHNESS_NS, hash_payload, message_payload
    from ros_esc.v2_stream import relative_stamp_ns, time_to_ns
    selected = _m4_pde_event_selection(resolved)
    if selected is None:
        return event_messages, [], None
    audit = []
    try:
        origins = set()
        for _, message in timekeeper_records:
            if message.mode != 'sim time':
                raise ValueError('PDE Timekeeper mode is not simulation')
            origins.add(relative_stamp_ns(0, message.start_time))
        if len(origins) != 1:
            raise ValueError('PDE confirmation lacks one immutable observed Timekeeper origin')
        origin = next(iter(origins))
        runs = {m.run_id for _, m in state_messages if m.run_id_valid and m.run_id
                and m.state_valid and m.algorithm_profile == 'robust_gaussian_v1'}
        if len(runs) != 1:
            raise ValueError('PDE confirmation lacks one selected supervisor run')
        identity = dict(run_id=next(iter(runs)), stream_config=selected['stream_config'])
        confirmed, epochs = {}, {}
        for _, message in confirmation_records:
            error = v2_message_identity_error(message, identity, origin, protocol_version=1)
            if error:
                raise ValueError(error)
            times = [time_to_ns(getattr(message, key)) for key in
                     ('epoch_started_at', 'history_start', 'history_end', 'source_stamp', 'stamp')]
            epoch_start, lo, hi, source, publication = times
            vector = list(message.legacy_snapshot)
            if (message.metric_mode != 'pde_mean_v1' or message.history_kind != 'pde_input_support'
                    or message.source_stamp_kind != 'pose_input' or not message.valid
                    or not message.legacy_r_mean_valid or message.convergence_score_valid
                    or any(type(getattr(message, key)) is not int or getattr(message, key) <= 0
                           for key in ('search_epoch', 'confirmation_sequence', 'context_sequence'))
                    or not origin <= epoch_start <= lo <= hi == source <= publication
                    or publication-source > FRESHNESS_NS or len(vector) != 8
                    or not all(math.isfinite(v) for v in (*vector, message.legacy_r_mean_m2,
                                                          message.center_x_m, message.center_y_m))
                    or message.legacy_r_mean_m2 < 0 or vector[1] != message.legacy_r_mean_m2
                    or vector[3:5] != [message.center_x_m, message.center_y_m]):
                raise ValueError('PDE confirmation metric, identity or support bounds invalid')
            key = (message.search_epoch, message.confirmation_sequence)
            digest = hash_payload(message_payload(message))
            if key in confirmed and confirmed[key][0] != digest:
                raise ValueError('conflicting typed PDE confirmation identity')
            if message.search_epoch in epochs and epochs[message.search_epoch] != key:
                raise ValueError('multiple PDE confirmations in one epoch')
            epochs[message.search_epoch] = key
            confirmed[key] = (digest, message)
        fields = ('metric', 'r_mean_m2', 'decay', 'fill_center_x_m', 'fill_center_y_m',
                  'mean_old_x_m', 'mean_old_y_m', 'count_remaining')
        normalized, matched, event_identities = [], set(), {}
        for bag_stamp, event in event_messages:
            if event.event_type != AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED:
                normalized.append((bag_stamp, event))
                continue
            names = list(event.value_names)
            values = _event_value_map(event)
            original = _message_source_timestamp(event)
            if (len(names) != len(set(names)) or not set(fields).issubset(values)
                    or not all(math.isfinite(v) for v in values.values()) or original is None):
                raise ValueError('PDE public convergence fields or timestamp invalid')
            vector = [values[name] for name in fields]
            publication = time_to_ns(event.stamp)
            candidates = [(key, digest, message) for key, (digest, message) in confirmed.items()
                if vector == list(message.legacy_snapshot)
                and 0 <= publication-time_to_ns(message.stamp) <= FRESHNESS_NS]
            if len(candidates) != 1:
                raise ValueError('PDE public convergence lacks one unique typed confirmation')
            key, typed_digest, message = candidates[0]
            mirrors = {hash_payload(message_payload(m)): m for _, m in legacy_records
                if m.header == 'CONVERGENCE_STATUS' and math.isfinite(m.timestamp)
                and m.timestamp == original and list(m.data) == vector}
            if len(mirrors) != 1:
                raise ValueError('PDE public convergence lacks one exact canonical legacy mirror')
            event_digest = hash_payload(message_payload(event))
            if key in event_identities and event_identities[key] != event_digest:
                raise ValueError('conflicting public PDE convergence identity')
            event_identities[key] = event_digest
            relative = (time_to_ns(message.source_stamp)-origin)*1e-9
            private = deepcopy(event)
            private.source_timestamp, private.source_timestamp_valid = relative, True
            normalized.append((bag_stamp, private))
            matched.add(key)
            audit.append(dict(event_bag_or_callback_stamp=bag_stamp, event_sha256=event_digest,
                confirmation_sha256=typed_digest, legacy_sha256=next(iter(mirrors)),
                run_id=message.run_id, metric_mode=message.metric_mode, search_epoch=key[0],
                confirmation_sequence=key[1], time_origin_ns=origin,
                confirmation_source_stamp_ns=time_to_ns(message.source_stamp),
                confirmation_publication_stamp_ns=time_to_ns(message.stamp),
                event_publication_stamp_ns=publication, original_source_timestamp=original,
                relative_source_timestamp=relative,
                scope='private inherited evaluator coordinate; public payload and decision clock unchanged'))
        if confirmed.keys()-matched:
            raise ValueError('typed PDE confirmation lacks matching public convergence event')
        return normalized, audit, None
    except (AttributeError, TypeError, ValueError, OverflowError, KeyError) as exc:
        return event_messages, audit, 'M4 PDE convergence timestamp binding: '+str(exc)


def _centroid_convergence_evaluation_events(resolved, state_messages, event_messages,
                                            centroid_records=(), timekeeper_records=()):
    """Join typed confirmations before private inherited timestamp adaptation.

    Public AlgorithmEvent has no centroid experiment-relative timestamp. Only
    an exact named metric/geometry/epoch/sequence match and immutable observed
    origin may supply one to an evaluator copy. Bag/callback order stays intact.
    Missing cross-topic inputs are pending live and errors at final bag audit.
    """
    from copy import deepcopy
    from ros_esc.convergence_detector_node.centroid_contract import centroid_diagnostic_errors
    from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, recurrent_diagnostic_errors
    from ros_esc.stationary_fill_protocol import (
        centroid_configuration_errors, stationary_diagnostic_origin_errors,
    )
    from ros_esc.v2_lifecycle import FRESHNESS_NS, hash_payload, message_payload
    from ros_esc.v2_stream import relative_stamp_ns, time_to_ns
    selected = _m4_centroid_event_selection(resolved)
    if selected is None:
        return event_messages, [], None
    audit = []
    try:
        origins = set()
        for _, message in timekeeper_records:
            if message.mode != 'sim time':
                raise ValueError('centroid Timekeeper mode is not simulation')
            origins.add(relative_stamp_ns(0, message.start_time))
        if len(origins) != 1:
            raise ValueError('centroid confirmation lacks one immutable observed Timekeeper origin')
        origin = next(iter(origins))
        runs = {message.run_id for _, message in state_messages
                if getattr(message, 'run_id_valid', False) and message.run_id
                and message.state_valid and message.algorithm_profile == 'robust_gaussian_v1'}
        confirmed = {}
        for _, diagnostic in centroid_records:
            if diagnostic is None or not diagnostic.confirmed:
                continue
            check_diagnostic = (recurrent_diagnostic_errors if selected['metric_mode'] ==
                                RECURRENT_MODE else centroid_diagnostic_errors)
            errors = check_diagnostic([diagnostic],
                expected_source_pose_topic=selected['pose_topic'], supervisor_run_ids=runs,
                maximum_source_gap_sec=selected['maximum_source_gap_sec'], allow_clock_admission=True,
                expected_frame_id='odom', pose_freshness_sec=selected['pose_freshness_sec'],
                expected_metric_mode=selected['metric_mode'])
            if selected['metric_mode'] != RECURRENT_MODE:
                errors += centroid_configuration_errors(diagnostic, selected['window_sec'],
                    selected['epsilon_m'], selected['maximum_radius_m'],
                    expected_metric_mode=selected['metric_mode'])
            elif resolved['algorithm']['launch_overrides'].get(
                    'continuous_search_mode', 'stationary_v1') == 'stationary_v1':
                errors += stationary_diagnostic_origin_errors(diagnostic, origin, RECURRENT_MODE)
            if len(runs) != 1 or errors or time_to_ns(diagnostic.history_start) < origin:
                raise ValueError('; '.join(errors) or 'centroid confirmation run/origin binding invalid')
            key = (int(diagnostic.search_epoch), int(diagnostic.confirmation_sequence))
            digest = hash_payload(message_payload(diagnostic))
            if key in confirmed and confirmed[key][0] != digest:
                raise ValueError('conflicting typed centroid confirmation identity')
            confirmed[key] = (digest, diagnostic)
        normalized, matched, event_identities = [], set(), {}
        fields = ('score_m', 'confinement_radius_m', 'fill_center_x_m', 'fill_center_y_m',
                  'search_epoch', 'confirmation_sequence')
        for bag_stamp, message in event_messages:
            if message.event_type != AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED:
                normalized.append((bag_stamp, message))
                continue
            if len(message.value_names) != len(fields) or set(message.value_names) != set(fields):
                raise ValueError('centroid convergence event does not carry the exact typed identity fields')
            values = _event_value_map(message)
            if not all(math.isfinite(values[name]) for name in fields):
                raise ValueError('centroid convergence event values are nonfinite')
            key = (int(values['search_epoch']), int(values['confirmation_sequence']))
            if (key[0] <= 0 or key[1] <= 0 or key !=
                    (values['search_epoch'], values['confirmation_sequence']) or key not in confirmed):
                raise ValueError('centroid convergence event lacks matching typed confirmation')
            diagnostic_digest, diagnostic = confirmed[key]
            if any(values[name] != value for name, value in (
                    ('score_m', diagnostic.score_m), ('confinement_radius_m', diagnostic.confinement_radius_m),
                    ('fill_center_x_m', diagnostic.center_x_m), ('fill_center_y_m', diagnostic.center_y_m))):
                raise ValueError('centroid convergence event center/score/radius differs from typed confirmation')
            if not 0 <= time_to_ns(message.stamp)-time_to_ns(diagnostic.stamp) <= FRESHNESS_NS:
                raise ValueError('centroid convergence event publication lacks bounded typed ordering')
            support_stamp = (diagnostic.history_end if selected['metric_mode'] == RECURRENT_MODE
                             else diagnostic.source_stamp)
            relative = (time_to_ns(support_stamp)-origin)*1e-9
            if message.source_timestamp_valid and _message_source_timestamp(message) != relative:
                raise ValueError('existing centroid event relative timestamp conflicts with typed origin')
            event_digest = hash_payload(message_payload(message))
            if key in event_identities and event_identities[key] != event_digest:
                raise ValueError('conflicting convergence event identity')
            event_identities[key] = event_digest
            private = message
            if not message.source_timestamp_valid:
                private = deepcopy(message)
                private.source_timestamp, private.source_timestamp_valid = relative, True
            normalized.append((bag_stamp, private))
            matched.add(key)
            audit.append(dict(event_bag_or_callback_stamp=bag_stamp, event_sha256=event_digest,
                diagnostic_sha256=diagnostic_digest, metric_mode=diagnostic.metric_mode,
                run_id=diagnostic.run_id, search_epoch=key[0], confirmation_sequence=key[1],
                time_origin_ns=origin, diagnostic_source_stamp_ns=time_to_ns(diagnostic.source_stamp),
                diagnostic_publication_stamp_ns=time_to_ns(diagnostic.stamp),
                relative_source_timestamp=relative,
                scope='private inherited evaluator coordinate; public event and primary decision clock unchanged'))
            if selected['metric_mode'] == RECURRENT_MODE:
                audit[-1].update(diagnostic_history_end_ns=time_to_ns(diagnostic.history_end),
                    evaluator_coordinate='confirmed_history_end',
                    evaluator_source_stamp_ns=time_to_ns(support_stamp))
        if confirmed.keys()-matched:
            raise ValueError('typed centroid confirmation lacks matching convergence event')
        return normalized, audit, None
    except (AttributeError, TypeError, ValueError, OverflowError, KeyError) as exc:
        return event_messages, audit, 'M4 centroid convergence timestamp binding: '+str(exc)


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
    assist_enabled = bool(
        resolved.get('algorithm', {}).get(
            'launch_overrides', {}
        ).get('open_field_escape_assist_enabled', False)
    )
    if counted_open_field:
        if assist_enabled and resolved.get('schema_version', 1) >= 13:
            accepted_paths = (
                COUNTED_OPEN_FIELD_RECOVERY_STATE_PATH,
                COUNTED_OPEN_FIELD_ASSISTED_RECOVERY_STATE_PATH,
            )
        else:
            accepted_paths = (
                (
                    COUNTED_OPEN_FIELD_ASSISTED_RECOVERY_STATE_PATH
                    if assist_enabled
                    else COUNTED_OPEN_FIELD_RECOVERY_STATE_PATH
                ),
            )
    else:
        accepted_paths = STAGED_RECOVERY_STATE_PATHS
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
    topology_qualification = contract.get('topology_qualification')
    if isinstance(topology_qualification, dict):
        evidence['topology_qualification'] = {
            'method': topology_qualification.get('method'),
            'result_sha256': topology_qualification.get('result_sha256'),
            'local_source_id': topology_qualification.get(
                'local_source_id'
            ),
            'global_source_id': topology_qualification.get(
                'global_source_id'
            ),
            'basin_depth_raw_cost': topology_qualification.get(
                'noise_adjusted_basin_depth_raw_cost'
            ),
            'raw_cost_separation': topology_qualification.get(
                'noise_adjusted_raw_cost_separation'
            ),
            'basin_center_separation_m': topology_qualification.get(
                'basin_center_separation_m'
            ),
            'forward_alignment': topology_qualification.get(
                'route', {}
            ).get('forward_alignment'),
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


def _causal_supervisor_owned_assist_entry(
    assist_diagnostics,
    commands,
    command_stamps,
    authority_start_stamp,
    search_stamp,
    stale_ns,
    handoff_timeout_sec,
):
    """Prove bounded schema-v12 settling into supervisor-only ownership."""
    zero = [0.0] * 6
    first_owned_stamp = None
    transition_sample_count = 0
    owned_sample_count = 0
    suppressed_gesc_sample_count = 0
    positive_linear_sample_count = 0
    proven_authority_command_stamps = set()

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
            return None, (
                'causal assist-entry sample has invalid command evidence'
            )

        expected_contribution = [
            combined[index] - gesc[index] for index in range(6)
        ]
        if not _commands_close(contribution, expected_contribution):
            return None, (
                'causal assist-entry supervisor contribution is inconsistent'
            )
        saturated = _diagnostic_saturated_command(message, combined)
        if saturated is None or not _commands_close(final, saturated):
            return None, (
                'causal assist-entry final command saturation is invalid'
            )

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
            return None, (
                'causal assist-entry sample has a stale supervisor command'
            )

        nonzero_matches = [
            candidate
            for candidate in candidate_commands
            if (
                any(abs(value) > 1e-9 for value in candidate[2])
                and _commands_close(combined, candidate[2])
            )
        ]
        if nonzero_matches:
            matched_supervisor = min(
                nonzero_matches,
                key=lambda item: (
                    item[0],
                    item[1] > diagnostic_stamp,
                    item[1],
                ),
            )
            if first_owned_stamp is None:
                first_owned_stamp = diagnostic_stamp
            proven_authority_command_stamps.add(matched_supervisor[1])
            owned_sample_count += 1
            if any(abs(value) > 1e-9 for value in gesc):
                suppressed_gesc_sample_count += 1
            if matched_supervisor[2][0] > 1e-9:
                positive_linear_sample_count += 1
            continue

        additive_nonzero = any(
            (
                any(abs(value) > 1e-9 for value in candidate[2])
                and _commands_close(
                    combined,
                    [
                        candidate[2][index] + gesc[index]
                        for index in range(6)
                    ],
                )
            )
            for candidate in candidate_commands
        )
        if additive_nonzero:
            return None, (
                'GESC leaked into a nonzero supervisor command during '
                'causal assist entry'
            )
        if first_owned_stamp is not None:
            return None, (
                'supervisor ownership fell back after causal assist entry'
            )

        fresh_zero_command = any(
            _commands_close(candidate[2], zero)
            for candidate in candidate_commands
        )
        ordinary_previous_state = (
            _commands_close(combined, gesc)
            and _commands_close(contribution, zero)
        )
        zero_or_failsafe = _commands_close(combined, zero)
        recognized_transition = (
            ordinary_previous_state or zero_or_failsafe
        )
        if recognized_transition and not fresh_zero_command:
            return None, (
                'causal assist-entry transition has no fresh zero '
                'supervisor command'
            )
        if not recognized_transition:
            return None, (
                'causal assist entry contains an unrecognized command'
            )
        transition_sample_count += 1

    if first_owned_stamp is None:
        return None, (
            'causal assist entry never established supervisor ownership'
        )
    handoff_delay_ns = first_owned_stamp - authority_start_stamp
    handoff_timeout_ns = handoff_timeout_sec * 1e9
    if handoff_delay_ns < 0 or handoff_delay_ns > handoff_timeout_ns:
        return None, 'causal assist entry exceeded its timeout'

    return {
        'proven_authority_command_stamps': (
            proven_authority_command_stamps
        ),
        'fresh_supervisor_command_sample_count': owned_sample_count,
        'nonzero_suppressed_gesc_sample_count': (
            suppressed_gesc_sample_count
        ),
        'positive_supervisor_linear_sample_count': (
            positive_linear_sample_count
        ),
        'assist_entry_transition_control_sample_count': (
            transition_sample_count
        ),
        'assist_entry_first_owned_control_bag_stamp': first_owned_stamp,
        'assist_entry_handoff_delay_sec': handoff_delay_ns * 1e-9,
        'assist_entry_handoff_timeout_sec': handoff_timeout_sec,
        'assist_entry_steady_owned_control_sample_count': (
            owned_sample_count
        ),
        'assist_entry_handoff_evidence_mode': (
            'bounded_causal_schema_v12'
        ),
    }, None


def _supervisor_owned_escape_assist_evidence(
    resolved,
    state_messages,
    event_messages,
    diagnostic_records,
    supervisor_command_records,
    odometry_records,
):
    """Prove schema-versioned command ownership and measured aligned escape."""
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

    proven_authority_command_stamps = set()
    schema_version = resolved.get('schema_version', 1)
    if schema_version >= 12:
        handoff_timeout_sec = resolved.get('success', {}).get(
            'controller',
            {},
        ).get('supervisor_owned_assist_handoff_timeout_sec')
        if (
            isinstance(handoff_timeout_sec, bool)
            or not isinstance(handoff_timeout_sec, (int, float))
            or not math.isfinite(float(handoff_timeout_sec))
            or float(handoff_timeout_sec) <= 0.0
        ):
            return failed(
                'causal assist-entry handoff timeout is unavailable'
            )
        entry_evidence, entry_error = (
            _causal_supervisor_owned_assist_entry(
                assist_diagnostics,
                commands,
                command_stamps,
                authority_start_stamp,
                search_stamp,
                stale_ns,
                float(handoff_timeout_sec),
            )
        )
        if entry_error is not None:
            return failed(entry_error)
        proven_authority_command_stamps = entry_evidence.pop(
            'proven_authority_command_stamps'
        )
        evidence.update(entry_evidence)
    else:
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
                return failed(
                    'assist control sample has invalid command evidence'
                )
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
                        (
                            abs(diagnostic_stamp - command_stamp),
                            command_stamp,
                            raw,
                        )
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
                    return failed(
                        'GESC leaked into the supervisor-owned command'
                    )
                return failed(
                    'assist combined command has no fresh matching '
                    'supervisor command'
                )
            matched_supervisor = min(
                matching_commands,
                key=lambda item: (
                    item[0],
                    item[1] > diagnostic_stamp,
                    item[1],
                ),
            )
            proven_authority_command_stamps.add(matched_supervisor[1])
            raw_supervisor = matched_supervisor[2]
            expected_contribution = [
                combined[index] - gesc[index] for index in range(6)
            ]
            if not _commands_close(contribution, expected_contribution):
                return failed(
                    'supervisor contribution arithmetic is inconsistent'
                )
            saturated = _diagnostic_saturated_command(message, combined)
            if saturated is None or not _commands_close(final, saturated):
                return failed(
                    'final command does not match recorded saturation'
                )
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
    alignment_required = (
        resolved.get('success', {}).get('criterion') != POST_RECOVERY_ARRIVAL_CRITERION
    )
    if not alignment_required:
        evidence.update(exit_alignment_required=False, exit_alignment_threshold=0.80,
                        exit_alignment_passed=exit_alignment >= 0.80)
    if alignment_required and exit_alignment < 0.80:
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

    if resolved.get('schema_version', 1) >= 11:
        next_state_index = next(
            (
                index
                for index in range(
                    post_search_index + 1,
                    len(state_messages),
                )
                if (
                    state_messages[index][1].state_valid
                    and state_messages[index][1].state
                    != AlgorithmState.STATE_SEARCH
                )
            ),
            None,
        )
        search_end_stamp = (
            state_messages[next_state_index][0]
            if next_state_index is not None
            else None
        )

        def in_returned_search(stamp):
            return (
                stamp >= search_stamp
                and (
                    search_end_stamp is None
                    or stamp < search_end_stamp
                )
            )

        returned_search_states = [
            (stamp, message)
            for stamp, message in state_messages
            if in_returned_search(stamp)
        ]
        for unused_stamp, message in returned_search_states:
            weights = [
                float(message.sensor_weight),
                float(message.gaussian_weight),
                float(message.affine_weight),
            ]
            if (
                not message.state_valid
                or message.state != AlgorithmState.STATE_SEARCH
                or not message.weights_valid
                or weights != [1.0, 1.0, 0.0]
                or message.active_escape_fill_id_valid
                or message.escape_geometry_valid
                or message.safe_direction_valid
                or message.safe_direction_revision_valid
            ):
                return failed(
                    'returned SEARCH state retained escape authority'
                )

        returned_search_commands = [
            (stamp, message)
            for stamp, message in commands
            if in_returned_search(stamp)
        ]
        if not returned_search_commands:
            return failed('post-exit SEARCH has no supervisor command')
        for unused_stamp, message in returned_search_commands:
            raw = _finite_command(_twist_command(message))
            if raw is None or any(abs(value) > 1e-9 for value in raw):
                return failed(
                    'post-exit SEARCH supervisor command is not zero'
                )
        zero_command_stamp = returned_search_commands[0][0]

        controller_evidence = resolved.get('success', {}).get(
            'controller',
            {},
        )
        handoff_timeout_sec = controller_evidence.get(
            'supervisor_owned_assist_handoff_timeout_sec'
        )
        if (
            isinstance(handoff_timeout_sec, bool)
            or not isinstance(handoff_timeout_sec, (int, float))
            or not math.isfinite(float(handoff_timeout_sec))
            or float(handoff_timeout_sec) <= 0.0
        ):
            return failed(
                'causal post-exit handoff timeout is unavailable'
            )
        handoff_timeout_sec = float(handoff_timeout_sec)
        handoff_timeout_ns = handoff_timeout_sec * 1e9

        returned_search_diagnostics = [
            (stamp, message)
            for stamp, message in diagnostic_records
            if in_returned_search(stamp)
        ]
        if not returned_search_diagnostics:
            return failed(
                'post-exit SEARCH has no control diagnostic sample'
            )

        proven_authority_commands = [
            (stamp, message)
            for stamp, message in authority_commands
            if stamp in proven_authority_command_stamps
        ]
        if not proven_authority_commands:
            return failed('no assist command was proven by control evidence')
        final_assist_command_stamp, final_assist_command_message = (
            proven_authority_commands[-1]
        )
        final_assist_command = _finite_command(
            _twist_command(final_assist_command_message)
        )
        if final_assist_command is None:
            return failed('final assist command is invalid')

        first_ordinary_stamp = None
        transition_sample_count = 0
        ordinary_sample_count = 0
        zero = [0.0] * 6
        for diagnostic_stamp, message in returned_search_diagnostics:
            gesc = _finite_command(message.gesc_command_unsaturated)
            combined = _finite_command(
                message.combined_command_unsaturated
            )
            contribution = _finite_command(
                message.supervisor_contribution
            )
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
                return failed(
                    'post-exit SEARCH has invalid command evidence'
                )
            expected_contribution = [
                combined[index] - gesc[index]
                for index in range(6)
            ]
            if not _commands_close(
                contribution,
                expected_contribution,
            ):
                return failed(
                    'post-exit supervisor contribution is inconsistent'
                )
            saturated = _diagnostic_saturated_command(message, combined)
            if saturated is None or not _commands_close(final, saturated):
                return failed(
                    'post-exit SEARCH final command saturation is invalid'
                )

            ordinary = (
                _commands_close(combined, gesc)
                and _commands_close(contribution, zero)
            )
            if ordinary:
                if first_ordinary_stamp is None:
                    first_ordinary_stamp = diagnostic_stamp
                ordinary_sample_count += 1
                continue

            if first_ordinary_stamp is not None:
                return failed(
                    'supervisor authority reappeared after causal handoff'
                )

            zero_or_failsafe = _commands_close(combined, zero)
            assist_age_ns = (
                diagnostic_stamp - final_assist_command_stamp
            )
            held_final_assist = (
                0.0 <= assist_age_ns <= stale_ns
                and _commands_close(
                    combined,
                    final_assist_command,
                )
            )
            if (
                any(abs(value) > 1e-9 for value in gesc)
                and _commands_close(
                    combined,
                    [
                        final_assist_command[index] + gesc[index]
                        for index in range(6)
                    ],
                )
            ):
                return failed(
                    'GESC leaked during causal post-exit handoff'
                )
            if (
                _commands_close(combined, final_assist_command)
                and not held_final_assist
            ):
                return failed(
                    'causal post-exit handoff retained a stale assist command'
                )
            if not zero_or_failsafe and not held_final_assist:
                return failed(
                    'causal post-exit handoff contains an '
                    'unrecognized command'
                )
            transition_sample_count += 1

        if first_ordinary_stamp is None:
            return failed(
                'post-exit SEARCH never restored ordinary GESC ownership'
            )
        handoff_delay_ns = first_ordinary_stamp - search_stamp
        if handoff_delay_ns < 0 or handoff_delay_ns > handoff_timeout_ns:
            return failed(
                'causal post-exit handoff exceeded its timeout'
            )
        evidence.update({
            'post_exit_supervisor_zero_bag_stamp': zero_command_stamp,
            'post_exit_control_bag_stamp': first_ordinary_stamp,
            'post_exit_transition_control_sample_count': (
                transition_sample_count
            ),
            'post_exit_handoff_delay_sec': handoff_delay_ns * 1e-9,
            'post_exit_handoff_timeout_sec': handoff_timeout_sec,
            'post_exit_ordinary_control_sample_count': (
                ordinary_sample_count
            ),
            'post_exit_ordinary_gesc_restored': True,
            'post_exit_handoff_evidence_mode': (
                'bounded_causal_schema_v11'
            ),
        })
        return True, evidence, None

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


def _direct_escape_repulse_ownership_evidence(
    resolved,
    state_messages,
    event_messages,
    diagnostic_records,
    supervisor_command_records,
    odometry_records,
):
    """Prove a bounded direct repulse exit under ordinary GESC ownership."""
    evidence = {
        'enabled': True,
        'branch': 'direct_repulse',
        'assist_applicable': False,
        'evidence_mode': 'bounded_direct_repulse_schema_v13',
        'repulse_state_sample_count': 0,
        'repulse_control_sample_count': 0,
        'repulse_supervisor_command_sample_count': 0,
        'nonzero_gesc_control_sample_count': 0,
        'mature_radial_progress_sample_count': 0,
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
    if assist_indices:
        return failed(
            'direct recovery proof is invalid after ESCAPE_ASSIST entry'
        )

    repulse_indices = [
        index
        for index, (unused_stamp, message) in enumerate(state_messages)
        if (
            message.state_valid
            and message.state == AlgorithmState.STATE_ESCAPE_REPULSE
        )
    ]
    if not repulse_indices:
        return failed('no valid ESCAPE_REPULSE state interval')
    first_repulse_index = repulse_indices[0]
    repulse_start_stamp = state_messages[first_repulse_index][0]
    post_search_index = next(
        (
            index
            for index in range(first_repulse_index + 1, len(state_messages))
            if (
                state_messages[index][1].state_valid
                and state_messages[index][1].state
                == AlgorithmState.STATE_SEARCH
            )
        ),
        None,
    )
    if post_search_index is None:
        return failed('ESCAPE_REPULSE has no later SEARCH boundary')
    search_stamp, search_state = state_messages[post_search_index]
    if any(index >= post_search_index for index in repulse_indices):
        return failed('ESCAPE_REPULSE reappeared after the SEARCH boundary')

    repulse_states = [
        (stamp, message)
        for stamp, message in state_messages
        if repulse_start_stamp <= stamp < search_stamp
    ]
    evidence['repulse_state_sample_count'] = len(repulse_states)
    if not repulse_states or any(
        (
            not message.state_valid
            or message.state != AlgorithmState.STATE_ESCAPE_REPULSE
        )
        for unused_stamp, message in repulse_states
    ):
        return failed('direct interval contains a non-REPULSE state sample')

    stale_sec = float(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'supervisor_command_stale_sec',
            0.5,
        )
    )
    if not math.isfinite(stale_sec) or stale_sec < 0.0:
        return failed('direct evidence freshness limit is invalid')
    stale_ns = stale_sec * 1e9
    escape_events = [
        (stamp, message)
        for stamp, message in event_messages
        if (
            repulse_start_stamp - stale_ns <= stamp < search_stamp
            and message.event_type == AlgorithmEvent.EVENT_ESCAPE_STARTED
        )
    ]
    if len(escape_events) != 1:
        return failed(
            'direct interval must contain exactly one ESCAPE_STARTED event'
        )
    escape_event_stamp, escape_event = escape_events[0]
    try:
        escape_values = _event_value_map(escape_event)
        center = [
            float(escape_values['escape_center_x_m']),
            float(escape_values['escape_center_y_m']),
        ]
        direction = [
            float(escape_values['approach_selected_direction_x']),
            float(escape_values['approach_selected_direction_y']),
        ]
        exit_radius = float(escape_values['escape_exit_radius_m'])
        direction_revision = float(
            escape_values['approach_direction_revision']
        )
    except (KeyError, TypeError, ValueError) as exc:
        return failed(
            f'ESCAPE_STARTED direct ownership evidence is malformed: {exc}'
        )
    direction_norm = math.hypot(*direction)
    if (
        not all(
            math.isfinite(value)
            for value in [*center, *direction, exit_radius]
        )
        or exit_radius <= 0.0
        or direction_revision != 1.0
        or not math.isclose(
            direction_norm,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        )
    ):
        return failed(
            'ESCAPE_STARTED direct geometry is invalid or not revision one'
        )

    stalled_events = [
        message
        for stamp, message in event_messages
        if (
            repulse_start_stamp <= stamp < search_stamp
            and message.event_type == AlgorithmEvent.EVENT_ESCAPE_STALLED
        )
    ]
    if stalled_events:
        return failed('direct recovery emitted ESCAPE_STALLED without assist')

    minimum_progress = resolved.get('algorithm', {}).get(
        'launch_overrides', {}
    ).get('minimum_radial_progress_m')
    if (
        isinstance(minimum_progress, bool)
        or not isinstance(minimum_progress, (int, float))
        or not math.isfinite(float(minimum_progress))
        or float(minimum_progress) <= 0.0
    ):
        return failed('direct radial-progress threshold is invalid')
    minimum_progress = float(minimum_progress)

    radial_distances = []
    radial_progress = []
    for unused_stamp, message in repulse_states:
        try:
            weights = [
                float(message.sensor_weight),
                float(message.gaussian_weight),
                float(message.affine_weight),
            ]
            state_center = [
                float(message.escape_center_x),
                float(message.escape_center_y),
            ]
            state_direction = [
                float(message.safe_direction_x),
                float(message.safe_direction_y),
            ]
            state_radius = float(message.escape_exit_radius)
        except (AttributeError, TypeError, ValueError):
            return failed('direct repulse state geometry is malformed')
        if (
            not message.weights_valid
            or weights != [0.0, 1.0, 1.0]
            or not message.escape_geometry_valid
            or not message.safe_direction_valid
            or not message.safe_direction_revision_valid
            or message.safe_direction_revision != 1
            or not message.failsafe_valid
            or message.failsafe
            or (
                message.escape_stalled_valid
                and message.escape_stalled
            )
            or not all(
                math.isfinite(value)
                for value in [*state_center, *state_direction, state_radius]
            )
            or not _commands_close(
                [*state_center, 0.0, 0.0, 0.0, 0.0],
                [*center, 0.0, 0.0, 0.0, 0.0],
            )
            or not _commands_close(
                [*state_direction, 0.0, 0.0, 0.0, 0.0],
                [*direction, 0.0, 0.0, 0.0, 0.0],
            )
            or not math.isclose(
                state_radius,
                exit_radius,
                rel_tol=0.0,
                abs_tol=1e-9,
            )
        ):
            return failed(
                'direct repulse state changed geometry, weights, or safety'
            )
        if message.radial_distance_valid:
            distance = float(message.radial_distance)
            if not math.isfinite(distance) or distance < 0.0:
                return failed('direct radial-distance evidence is invalid')
            radial_distances.append(distance)
        if message.radial_progress_valid:
            progress = float(message.radial_progress)
            if not math.isfinite(progress):
                return failed('direct radial-progress evidence is invalid')
            if progress < minimum_progress:
                return failed(
                    'direct radial progress fell below the stall threshold'
                )
            radial_progress.append(progress)
    if not radial_distances or max(radial_distances) < exit_radius:
        return failed('direct repulse did not reach the frozen exit radius')
    if not radial_progress:
        return failed('direct repulse has no mature radial-progress evidence')
    evidence.update({
        'minimum_radial_progress_m': minimum_progress,
        'mature_radial_progress_sample_count': len(radial_progress),
        'minimum_mature_radial_progress_m': min(radial_progress),
        'maximum_mature_radial_progress_m': max(radial_progress),
        'maximum_radial_distance_m': max(radial_distances),
    })

    commands = sorted(
        supervisor_command_records,
        key=lambda item: item[0],
    )
    repulse_commands = [
        (stamp, message)
        for stamp, message in commands
        if repulse_start_stamp <= stamp < search_stamp
    ]
    evidence['repulse_supervisor_command_sample_count'] = len(
        repulse_commands
    )
    if not repulse_commands:
        return failed('direct repulse has no supervisor command evidence')
    for unused_stamp, message in repulse_commands:
        command = _finite_command(_twist_command(message))
        if command is None or any(abs(value) > 1e-9 for value in command):
            return failed(
                'direct repulse supervisor command is nonzero or invalid'
            )

    repulse_diagnostics = [
        (stamp, message)
        for stamp, message in diagnostic_records
        if repulse_start_stamp <= stamp < search_stamp
    ]
    evidence['repulse_control_sample_count'] = len(repulse_diagnostics)
    if not repulse_diagnostics:
        return failed('direct repulse has no control diagnostic evidence')
    zero = [0.0] * 6
    for unused_stamp, message in repulse_diagnostics:
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
            return failed('direct repulse has invalid command evidence')
        if (
            not _commands_close(combined, gesc)
            or not _commands_close(contribution, zero)
        ):
            return failed(
                'direct repulse command is not ordinary GESC ownership'
            )
        saturated = _diagnostic_saturated_command(message, combined)
        if saturated is None or not _commands_close(final, saturated):
            return failed('direct repulse final command saturation is invalid')
        if any(abs(value) > 1e-9 for value in gesc):
            evidence['nonzero_gesc_control_sample_count'] += 1
    if evidence['nonzero_gesc_control_sample_count'] <= 0:
        return failed('direct repulse has no nonzero GESC command evidence')

    try:
        search_weights = [
            float(search_state.sensor_weight),
            float(search_state.gaussian_weight),
            float(search_state.affine_weight),
        ]
    except (AttributeError, TypeError, ValueError):
        return failed('returned SEARCH state weights are malformed')
    if (
        not search_state.previous_state_valid
        or search_state.previous_state
        != AlgorithmState.STATE_ESCAPE_REPULSE
        or not search_state.transition_reason_valid
        or 'stable escape exit' not in search_state.transition_reason
        or not search_state.weights_valid
        or search_weights != [1.0, 1.0, 0.0]
        or search_state.active_escape_fill_id_valid
        or search_state.escape_geometry_valid
        or search_state.safe_direction_valid
        or search_state.safe_direction_revision_valid
        or not search_state.failsafe_valid
        or search_state.failsafe
    ):
        return failed(
            'returned SEARCH state did not prove a cleared stable direct exit'
        )

    next_state_index = next(
        (
            index
            for index in range(post_search_index + 1, len(state_messages))
            if (
                state_messages[index][1].state_valid
                and state_messages[index][1].state
                != AlgorithmState.STATE_SEARCH
            )
        ),
        None,
    )
    search_end_stamp = (
        state_messages[next_state_index][0]
        if next_state_index is not None
        else None
    )

    def in_returned_search(stamp):
        return (
            stamp >= search_stamp
            and (search_end_stamp is None or stamp < search_end_stamp)
        )

    returned_search_states = [
        (stamp, message)
        for stamp, message in state_messages
        if in_returned_search(stamp)
    ]
    for unused_stamp, message in returned_search_states:
        try:
            weights = [
                float(message.sensor_weight),
                float(message.gaussian_weight),
                float(message.affine_weight),
            ]
        except (AttributeError, TypeError, ValueError):
            return failed('returned SEARCH state weights are malformed')
        if (
            not message.state_valid
            or message.state != AlgorithmState.STATE_SEARCH
            or not message.weights_valid
            or weights != [1.0, 1.0, 0.0]
            or message.active_escape_fill_id_valid
            or message.escape_geometry_valid
            or message.safe_direction_valid
            or message.safe_direction_revision_valid
            or not message.failsafe_valid
            or message.failsafe
        ):
            return failed('returned SEARCH retained direct escape authority')

    returned_search_commands = [
        (stamp, message)
        for stamp, message in commands
        if in_returned_search(stamp)
    ]
    if not returned_search_commands:
        return failed('returned SEARCH has no supervisor command evidence')
    for unused_stamp, message in returned_search_commands:
        command = _finite_command(_twist_command(message))
        if command is None or any(abs(value) > 1e-9 for value in command):
            return failed('returned SEARCH supervisor command is not zero')

    exit_candidates = [
        (stamp, message)
        for stamp, message in odometry_records
        if (
            repulse_start_stamp <= stamp
            and abs(stamp - search_stamp) <= stale_ns
        )
    ]
    exit_odometry = (
        min(
            exit_candidates,
            key=lambda item: (
                abs(item[0] - search_stamp),
                item[0] < search_stamp,
                item[0],
            ),
        )
        if exit_candidates
        else None
    )
    if exit_odometry is None:
        return failed('direct SEARCH boundary has no measured exit odometry')
    exit_stamp, exit_message = exit_odometry
    try:
        exit_x = float(exit_message.pose.pose.position.x)
        exit_y = float(exit_message.pose.pose.position.y)
    except (AttributeError, TypeError, ValueError):
        return failed('direct measured exit odometry is malformed')
    exit_vector = [exit_x - center[0], exit_y - center[1]]
    measured_distance = math.hypot(*exit_vector)
    if (
        not all(
            math.isfinite(value)
            for value in [exit_x, exit_y, measured_distance]
        )
        or measured_distance <= 1e-12
    ):
        return failed('direct measured fill-to-exit vector is invalid')
    measured_unit = [
        value / measured_distance for value in exit_vector
    ]
    alignment = sum(
        measured_unit[index] * direction[index] for index in range(2)
    )
    if measured_distance < exit_radius:
        return failed('direct measured exit is inside the frozen exit radius')
    alignment_required = (
        resolved.get('success', {}).get('criterion') != POST_RECOVERY_ARRIVAL_CRITERION
    )
    if not alignment_required:
        evidence.update(exit_alignment_required=False, exit_alignment_threshold=0.80,
                        exit_alignment_passed=alignment >= 0.80)
    if alignment_required and alignment < 0.80:
        return failed('direct measured fill-to-exit alignment is below 0.80')

    evidence.update({
        'escape_started_bag_stamp': escape_event_stamp,
        'escape_started_to_repulse_state_sec': (
            repulse_start_stamp - escape_event_stamp
        ) / 1e9,
        'evidence_freshness_limit_sec': stale_sec,
        'repulse_start_bag_stamp': repulse_start_stamp,
        'post_exit_search_bag_stamp': search_stamp,
        'exit_odometry_bag_stamp': exit_stamp,
        'selected_direction': direction,
        'fill_center_m': center,
        'frozen_exit_radius_m': exit_radius,
        'exit_position_m': [exit_x, exit_y],
        'fill_to_exit_distance_m': measured_distance,
        'fill_to_exit_alignment': alignment,
        'returned_search_state_sample_count': len(
            returned_search_states
        ),
        'returned_search_zero_command_sample_count': len(
            returned_search_commands
        ),
        'ordinary_gesc_ownership_proven': True,
        'returned_search_authority_cleared': True,
    })
    return True, evidence, None


def _approach_anchor_evidence(resolved, event_messages):
    """Validate schema-v14 odometry-anchor evidence when fallback is enabled."""
    overrides = resolved.get('algorithm', {}).get('launch_overrides', {})
    enabled = bool(
        overrides.get(
            'open_field_escape_interior_anchor_fallback_enabled',
            False,
        )
    )
    if not enabled:
        return None, None, None

    evidence = {'enabled': True}

    def failed(reason):
        return False, {**evidence, 'reason': reason}, None

    try:
        minimum_displacement_m = float(
            overrides[
                'open_field_escape_interior_anchor_min_displacement_m'
            ]
        )
    except (KeyError, TypeError, ValueError):
        return failed('interior approach-anchor minimum is malformed')
    if (
        not math.isfinite(minimum_displacement_m)
        or minimum_displacement_m <= 0.0
    ):
        return failed('interior approach-anchor minimum is invalid')
    evidence['minimum_displacement_m'] = minimum_displacement_m

    escape_events = [
        (stamp, message)
        for stamp, message in event_messages
        if message.event_type == AlgorithmEvent.EVENT_ESCAPE_STARTED
    ]
    evidence['escape_started_event_count'] = len(escape_events)
    if len(escape_events) != 1:
        return failed(
            'interior approach-anchor contract requires exactly one '
            'ESCAPE_STARTED event'
        )
    event_stamp, event = escape_events[0]
    try:
        values = _event_value_map(event)
        mode_value = float(values['approach_corridor_anchor_mode'])
        displacement_m = float(
            values['approach_corridor_displacement_m']
        )
        exclusion_radius_m = float(
            values['approach_corridor_exclusion_radius_m']
        )
        anchor = [
            float(values['approach_corridor_anchor_x_m']),
            float(values['approach_corridor_anchor_y_m']),
        ]
        anchor_stamp_sec = float(
            values['approach_corridor_anchor_stamp_sec']
        )
        history_age_sec = float(
            values['approach_corridor_history_age_sec']
        )
        direction = [
            float(values['approach_corridor_direction_x']),
            float(values['approach_corridor_direction_y']),
        ]
    except (KeyError, TypeError, ValueError) as exc:
        return failed(
            f'ESCAPE_STARTED approach-anchor evidence is malformed: {exc}'
        )
    if mode_value not in {0.0, 1.0}:
        return failed('approach-anchor mode must equal zero or one')
    mode = 'outside_radius' if mode_value == 0.0 else 'interior_farthest'
    direction_norm = math.hypot(*direction)
    numeric_values = [
        displacement_m,
        exclusion_radius_m,
        *anchor,
        anchor_stamp_sec,
        history_age_sec,
        *direction,
        direction_norm,
    ]
    if (
        not all(math.isfinite(value) for value in numeric_values)
        or displacement_m <= 0.0
        or exclusion_radius_m <= 0.0
        or history_age_sec < 0.0
        or not math.isclose(
            direction_norm,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        )
    ):
        return failed('approach-anchor geometry is invalid')
    if (
        mode == 'outside_radius'
        and displacement_m <= exclusion_radius_m + 1e-12
    ):
        return failed('outside-radius anchor is not outside the exit radius')
    if mode == 'interior_farthest':
        if displacement_m > exclusion_radius_m + 1e-12:
            return failed('interior anchor is outside the exit radius')
        if displacement_m < minimum_displacement_m:
            return failed('interior anchor is below the frozen minimum')
    expected_mode = resolved.get('success', {}).get('controller', {}).get(
        'expected_approach_anchor_mode'
    )
    if expected_mode is not None and mode != expected_mode:
        return failed(
            f'approach-anchor mode {mode} does not match expected '
            f'{expected_mode}'
        )
    evidence.update({
        'escape_started_bag_stamp': event_stamp,
        'mode': mode,
        'mode_value': mode_value,
        'displacement_m': displacement_m,
        'exclusion_radius_m': exclusion_radius_m,
        'anchor_m': anchor,
        'anchor_stamp_sec': anchor_stamp_sec,
        'history_age_sec': history_age_sec,
        'direction': direction,
        'expected_mode': expected_mode,
    })
    return True, evidence, None


def _escape_command_ownership_evidence(
    resolved,
    state_messages,
    event_messages,
    diagnostic_records,
    supervisor_command_records,
    odometry_records,
):
    """Select the strict schema-v13 direct or assisted ownership proof."""
    if resolved.get('schema_version', 1) < 13:
        return None, None, None
    enabled = bool(
        resolved.get('algorithm', {}).get('launch_overrides', {}).get(
            'open_field_escape_supervisor_owned_assist_enabled',
            False,
        )
    )
    if not enabled:
        return None, None, None
    (
        anchor_passed,
        anchor_evidence,
        anchor_error,
    ) = _approach_anchor_evidence(resolved, event_messages)
    if anchor_error is not None:
        return None, None, anchor_error
    if anchor_passed is False:
        return False, {
            'branch': 'unqualified_anchor',
            'assist_applicable': None,
            'evidence_mode': 'conditional_escape_schema_v14',
            'approach_anchor': anchor_evidence,
            'reason': anchor_evidence.get(
                'reason',
                'schema-v14 approach-anchor proof failed',
            ),
        }, None

    def with_anchor(result):
        passed, branch_evidence, error = result
        if anchor_evidence is not None and branch_evidence is not None:
            branch_evidence = {
                **branch_evidence,
                'approach_anchor': anchor_evidence,
            }
        return passed, branch_evidence, error

    assist_observed = any(
        (
            message.state_valid
            and message.state == AlgorithmState.STATE_ESCAPE_ASSIST
        )
        for unused_stamp, message in state_messages
    )
    if assist_observed:
        passed, assist_evidence, error = (
            _supervisor_owned_escape_assist_evidence(
                resolved,
                state_messages,
                event_messages,
                diagnostic_records,
                supervisor_command_records,
                odometry_records,
            )
        )
        if error is not None:
            return None, None, error
        evidence = {
            **(assist_evidence or {}),
            'branch': 'assisted',
            'assist_applicable': True,
            'evidence_mode': 'conditional_escape_schema_v13',
        }
        if passed is not True:
            evidence['reason'] = (
                (assist_evidence or {}).get(
                    'reason',
                    'schema-v12 assisted ownership proof failed',
                )
            )
        return with_anchor((passed, evidence, None))
    return with_anchor(
        _direct_escape_repulse_ownership_evidence(
            resolved,
            state_messages,
            event_messages,
            diagnostic_records,
            supervisor_command_records,
            odometry_records,
        )
    )


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
    centroid_selection = _m4_centroid_event_selection(resolved)
    pde_selection = _m4_pde_event_selection(resolved)
    if centroid_selection is not None:
        from ros_esc_interfaces.msg import CentroidConvergenceDiagnostics, RecurrentConvergenceDiagnostics, Timekeeper
        wanted[centroid_selection['diagnostic_topic']] = (
            RecurrentConvergenceDiagnostics if centroid_selection['metric_mode'] ==
            'recurrent_geometry_v3' else CentroidConvergenceDiagnostics)
        wanted[centroid_selection['timekeeper_topic']] = Timekeeper
    elif pde_selection is not None:
        from ros_esc_interfaces.msg import DetectorConfirmation, StampedFloat64MultiArray, Timekeeper
        wanted[pde_selection['confirmation_topic']] = DetectorConfirmation
        wanted[pde_selection['legacy_topic']] = StampedFloat64MultiArray
        wanted[pde_selection['timekeeper_topic']] = Timekeeper
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
    centroid_bindings, centroid_binding_error = [], None
    pde_bindings, pde_binding_error = [], None
    if centroid_selection is not None:
        event_messages, centroid_bindings, centroid_binding_error = _centroid_convergence_evaluation_events(
            resolved, state_messages, event_messages,
            [(stamp, message) for stamp, message in records[centroid_selection['diagnostic_topic']]
             if inside(stamp)], records[centroid_selection['timekeeper_topic']])
    elif pde_selection is not None:
        event_messages, pde_bindings, pde_binding_error = _moving_pde_convergence_evaluation_events(
            resolved, state_messages, event_messages,
            [(stamp, message) for stamp, message in records[pde_selection['confirmation_topic']] if inside(stamp)],
            [(stamp, message) for stamp, message in records[pde_selection['legacy_topic']] if inside(stamp)],
            records[pde_selection['timekeeper_topic']])
    collision_expected = resolved['success'].get('collision_expected')
    state_records, state_error = _canonical_state_records(state_messages)
    event_records, event_error = _canonical_event_records(event_messages)
    observed_states = [name for unused_stamp, name in state_records]
    observed_events = [name for unused_stamp, name in event_records]
    saturation_samples = sum(
        1 for message in diagnostics if any(message.saturation_flags)
    )
    final_position = None
    outcome_error = pde_binding_error or centroid_binding_error or state_error or event_error
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
    (
        escape_command_ownership_passed,
        escape_command_ownership_evidence,
        escape_command_ownership_error,
    ) = _escape_command_ownership_evidence(
        resolved,
        state_messages,
        event_messages,
        diagnostic_records,
        supervisor_command_records,
        odometry_records,
    )
    outcome_error = outcome_error or escape_command_ownership_error
    ranked_goal_stamp = (
        ranked_goal_evidence.get('event_bag_stamp')
        if _requires_ranked_goal(resolved) and ranked_goal_passed and ranked_goal_evidence
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
        _requires_ranked_goal(resolved) and ranked_goal_passed is False
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
        **({'centroid_event_timestamp_bindings': centroid_bindings,
            'centroid_event_timestamp_binding_error': centroid_binding_error}
           if centroid_selection is not None else {}),
        **({'pde_event_timestamp_bindings': pde_bindings,
            'pde_event_timestamp_binding_error': pde_binding_error}
           if pde_selection is not None else {}),
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
    if escape_command_ownership_passed is not None:
        outcomes.update({
            'escape_command_ownership_passed': (
                escape_command_ownership_passed
            ),
            'escape_command_ownership': (
                escape_command_ownership_evidence
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
        'escape_command_ownership': outcomes.get(
            'escape_command_ownership_passed'
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
    elif (_m4_centroid_event_selection(resolved) is not None
          or _m4_pde_event_selection(resolved) is not None):
        if process_result.get('staged_monitor_error'):
            infrastructure_status = 'live_monitor_evidence_failed'
            infrastructure_reason = process_result['staged_monitor_error']
        elif (
            process_result.get('stage_a_completion_evidence_live') is not None
            and (
                process_result.get('stage_a_observed_live') is False
                or process_result.get('fill_cardinality_observed_live') is False
            )
        ):
            infrastructure_status = 'live_monitor_evidence_failed'
            infrastructure_reason = (
                'latest live recovery/cardinality evidence failed after '
                'Stage A completion'
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
        if 'escape_command_ownership' in resolved['success']['all_of']:
            staged_results['escape_command_ownership'] = {
                'passed': facts['escape_command_ownership'],
                'evidence': outcomes.get('escape_command_ownership'),
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
    run_id=None,
    *, strict_cleanup=False, cleanup_deadline=None,
    process_ownership_mode='observed_tree_v1',
):
    """Validate, expand, and optionally execute one serial simulation suite."""
    if process_ownership_mode not in ('observed_tree_v1', 'subreaper_v2', 'subreaper_group_v3'):
        raise ValueError('unknown process ownership mode')
    suite = load_suite(scenario_path)
    selected_modes = {'m4_pilot_v2': 'subreaper_v2', 'm4_pilot_v3': 'subreaper_group_v3',
                      'm4_pilot_v4': 'subreaper_group_v3', 'm4_pilot_v5': 'subreaper_group_v3',
                      'm4_pilot_v6': 'subreaper_group_v3',
                      'm4_pilot_v7': 'subreaper_group_v3',
                      'm4_pilot_v8': 'subreaper_group_v3',
                      'm4_pilot_v9': 'subreaper_group_v3',
                      **dict.fromkeys(ARRIVAL_SUITE_IDS, 'subreaper_group_v3'),
                      'v2_method_development_v1': 'subreaper_group_v3'}
    if (not dry_run and (suite['suite_id'] in selected_modes
            or process_ownership_mode != 'observed_tree_v1')
            and (selected_modes.get(suite['suite_id']) != process_ownership_mode or not strict_cleanup)):
        raise ValueError('M4 v2/v3 requires its exact explicit ownership mode and strict cleanup')
    resolved_runs, unsupported = expand_suite(suite, case_ids=case_ids)
    if strict_cleanup and (len(resolved_runs) != 1 or run_id is None
                           or _deadline_remaining(cleanup_deadline) <= 0):
        raise ValueError('strict cleanup requires one explicit run and a future absolute deadline')
    explicit_run_id = None
    if run_id is not None:
        if not isinstance(run_id, str):
            raise ValueError('explicit run_id must be a string')
        explicit_run_id = validate_run_id(run_id)
        if len(resolved_runs) != 1:
            raise ValueError('explicit run_id requires exactly one expanded run')
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
    if 'purpose' in suite:
        summary['purpose'] = suite['purpose']
    if not dry_run:
        ensure_ros_daemon()
    baseline_nodes = (ros_graph_nodes(strict=True, absolute_deadline=cleanup_deadline,
                      **({'require_shared_daemon': True}
                         if suite['suite_id'] in ('v2_method_development_v1', *ARRIVAL_SUITE_IDS) else {}))
                      if strict_cleanup else ros_graph_nodes()) if not dry_run else set()
    for resolved in resolved_runs:
        run_id = explicit_run_id or generate_scenario_run_id(resolved)
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
                run_id=run_id,
            )
            metadata_path = temporary_path / 'metadata.yaml'
            atomic_yaml(metadata_path, metadata)
            launch = build_launch_command(
                resolved, cost_path=noise_path,
                gui=execution['gazebo_gui'],
                run_id=run_id,
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
                if 'purpose' in resolved:
                    dry_run_record['purpose'] = resolved['purpose']
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
                **({'strict_process_tracking': True} if strict_cleanup else {}),
                **({'process_ownership_mode': process_ownership_mode,
                    'absolute_deadline': cleanup_deadline}
                   if process_ownership_mode != 'observed_tree_v1' else {}),
                **boundary_arguments,
            )
            cleanup = cleanup_evidence(
                baseline_nodes, process_result['session_id'],
                **({'strict': True, 'absolute_deadline': cleanup_deadline,
                    'process_ownership': process_result.get('process_ownership')}
                   if strict_cleanup else {}),
                **({'process_ownership_mode': process_ownership_mode}
                   if process_ownership_mode != 'observed_tree_v1' else {}),
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
            if strict_cleanup:
                result['launch_argv'] = list(launch)
                actual_cost = noise_path if noise_path is not None else MULTI_LIGHT_COST
                captured_cost = (Path(run_directory) / 'resolved_cost_function.json'
                                 if noise_path is not None and run_directory is not None
                                 else actual_cost)
                result['captured_cost_configuration'] = {
                    'argv_path': str(actual_cost), 'path': str(captured_cost),
                    'sha256': hashlib.sha256(Path(actual_cost).read_bytes()).hexdigest(),
                }
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
    parser.add_argument('--run-id', help='Explicit immutable identity; requires exactly one expanded run.')
    parser.add_argument('--runs-root')
    parser.add_argument('--summary-output')
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--strict-cleanup', action='store_true',
                        help='Require bounded explicit graph and owned nested-session cleanup evidence.')
    parser.add_argument('--cleanup-deadline', type=float,
                        help='Absolute monotonic end for selected cleanup; outer owner bounds the child.')
    parser.add_argument('--process-ownership-mode', default='observed_tree_v1',
                        choices=('observed_tree_v1', 'subreaper_v2', 'subreaper_group_v3'))
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
            run_id=arguments.run_id,
            **({'strict_cleanup': True, 'cleanup_deadline': arguments.cleanup_deadline}
               if arguments.strict_cleanup else {}),
            **({'process_ownership_mode': arguments.process_ownership_mode}
               if arguments.process_ownership_mode != 'observed_tree_v1' else {}),
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
