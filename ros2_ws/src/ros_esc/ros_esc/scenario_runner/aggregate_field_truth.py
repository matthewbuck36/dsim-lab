"""Deterministic aggregate-field ground truth for Phase 08 schema-v4 cases."""

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

from ros_esc.cost_function_node.cost_function_objects \
    import cost_function_objects

from scipy import ndimage, optimize


Multi_Light_Source_Cost = (
    cost_function_objects.Multi_Light_Source_Cost
)


ROS_ESC_ROOT = Path(__file__).resolve().parents[2]
MODEL_CONFIG_RESOURCE_PATH = (
    Path('aggregate_field_truth')
    / 'multi_light_source_photoresistor.json'
)
SENSOR_TRANSFORM_CONFIG_RESOURCE_PATH = (
    Path('aggregate_field_truth')
    / 'turtlebot_rotating_sensor.json'
)
SENSOR_GEOMETRY_RESOURCE_PATH = (
    Path('urdf') / 'turtlebot3_rotating_sensor.urdf'
)


def _ament_package_share_directory(package_name):
    from ament_index_python.packages import get_package_share_directory

    return Path(get_package_share_directory(package_name))


def _first_existing_file(label, candidates):
    checked = []
    for candidate in candidates:
        path = Path(candidate).expanduser().resolve()
        checked.append(str(path))
        if path.is_file():
            return path
    raise FileNotFoundError(
        f'unable to resolve {label}; checked: ' + ', '.join(checked)
    )


def resolve_authoritative_paths(
    package_share_resolver=None,
    source_ros_esc_root=None,
):
    """Resolve truth inputs from package shares, then a source checkout."""
    resolver = (
        package_share_resolver
        if package_share_resolver is not None
        else _ament_package_share_directory
    )
    source_root = (
        Path(source_ros_esc_root).expanduser().resolve()
        if source_ros_esc_root is not None
        else ROS_ESC_ROOT
    )
    ros_esc_share = None
    turtlebot_share = None
    try:
        ros_esc_share = Path(resolver('ros_esc'))
    except Exception:
        # A source-only test environment need not have an ament index.
        pass
    try:
        turtlebot_share = Path(resolver('turtlebot3_rotating_sensor'))
    except Exception:
        pass
    model_candidates = []
    transform_candidates = []
    geometry_candidates = []
    if ros_esc_share is not None:
        model_candidates.append(
            ros_esc_share / MODEL_CONFIG_RESOURCE_PATH
        )
        transform_candidates.append(
            ros_esc_share / SENSOR_TRANSFORM_CONFIG_RESOURCE_PATH
        )
    if turtlebot_share is not None:
        geometry_candidates.append(
            turtlebot_share / SENSOR_GEOMETRY_RESOURCE_PATH
        )
    model_candidates.append(
        source_root
        / 'paper_recreations/heavy_ball_PDE_ESC/cost_function/'
        'multi_light_source_photoresistor.json'
    )
    transform_candidates.append(
        source_root
        / 'ros_esc/sensor_pose_node/transform_config_files/'
        'turtlebot_rotating_sensor.json'
    )
    geometry_candidates.append(
        source_root.parent
        / 'turtlebot3_rotating_sensor/urdf/'
        'turtlebot3_rotating_sensor.urdf'
    )
    return {
        'model_config_path': _first_existing_file(
            'aggregate cost model',
            model_candidates,
        ),
        'sensor_transform_config_path': _first_existing_file(
            'sensor transform configuration',
            transform_candidates,
        ),
        'sensor_geometry_path': _first_existing_file(
            'sensor URDF geometry',
            geometry_candidates,
        ),
    }


_AUTHORITATIVE_PATHS = resolve_authoritative_paths()
MODEL_CONFIG_PATH = _AUTHORITATIVE_PATHS['model_config_path']
SENSOR_TRANSFORM_CONFIG_PATH = (
    _AUTHORITATIVE_PATHS['sensor_transform_config_path']
)
SENSOR_GEOMETRY_PATH = _AUTHORITATIVE_PATHS['sensor_geometry_path']
TRUTH_SCHEMA_VERSION = 2
DEFAULT_SOLVER_SETTINGS = {
    'position_spacing_m': 0.10,
    'yaw_spacing_rad': math.radians(5.0),
    'offset_position_m': 0.05,
    'offset_yaw_rad': math.radians(2.5),
    'retained_basins_per_scan': 32,
    'merge_position_tolerance_m': 0.05,
    'merge_cost_tolerance': 1.0e-4,
    'scan_agreement_tolerance': 1.0e-4,
    'global_equivalence_tolerance': 1.0e-4,
    'optimizer_method': 'differential_evolution',
    'optimizer_max_iterations': 60,
    'optimizer_population_size': 5,
    'optimizer_relative_tolerance': 1.0e-9,
    'optimizer_absolute_tolerance': 1.0e-10,
}
LOCAL_QUALIFICATION_YAW_SPACING_RAD = math.radians(0.5)


def canonical_json_bytes(value):
    """Return the v3 canonical JSON representation."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
        allow_nan=False,
    ).encode('utf-8')


def canonical_sha256(value):
    """Hash one JSON-compatible value canonically."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path):
    """Hash one file without loading it all into memory."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be numeric')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f'{name} must be finite')
    return result


def _normalized_sources(sources):
    if not isinstance(sources, list) or not sources:
        raise ValueError('sources must be a non-empty list')
    normalized = []
    identifiers = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f'sources[{index}] must be a mapping')
        identifier = str(source.get('id', '')).strip()
        if not identifier or identifier in identifiers:
            raise ValueError('source identifiers must be non-empty and unique')
        identifiers.add(identifier)
        intensity = _finite_number(
            source.get('relative_lumen_input'),
            f'sources[{index}].relative_lumen_input',
        )
        if intensity < 0.0:
            raise ValueError('source intensity must be nonnegative')
        normalized.append({
            'id': identifier,
            'x_m': _finite_number(source.get('x_m'), f'sources[{index}].x_m'),
            'y_m': _finite_number(source.get('y_m'), f'sources[{index}].y_m'),
            'relative_lumen_input': intensity,
        })
    return normalized


def _domain(bounds_m, wall_margin_m):
    if not isinstance(bounds_m, list) or len(bounds_m) != 4:
        raise ValueError('bounds_m must be [x_min, x_max, y_min, y_max]')
    bounds = [
        _finite_number(value, f'bounds_m[{index}]')
        for index, value in enumerate(bounds_m)
    ]
    margin = _finite_number(wall_margin_m, 'wall_margin_m')
    if margin < 0.0:
        raise ValueError('wall_margin_m must be nonnegative')
    domain = [
        bounds[0] + margin,
        bounds[1] - margin,
        bounds[2] + margin,
        bounds[3] - margin,
    ]
    if not domain[0] < domain[1] or not domain[2] < domain[3]:
        raise ValueError('wall margin leaves an empty aggregate-search domain')
    return bounds, domain, margin


def _model(sources, model_config_path, sensor_binding=None):
    path = Path(model_config_path).expanduser().resolve()
    document = json.loads(path.read_text(encoding='utf-8'))
    cost = document.get('CostFunction', {})
    if cost.get('object_name') != 'Multi_Light_Source_Cost':
        raise ValueError(
            'aggregate truth requires Multi_Light_Source_Cost'
        )
    params = deepcopy(cost.get('params', {}))
    for key, expected in (
        ('mode', 'Voltage'),
        ('scale_map', 1.0),
        ('apply_adc', False),
        ('reference_intensity_lumens', 1000.0),
    ):
        if params.get(key) != expected:
            raise ValueError(
                f'aggregate model {key} drifted: {params.get(key)!r}'
            )
    params['light_sources'] = [
        {
            'x': source['x_m'],
            'y': source['y_m'],
            'intensity_lumens': source['relative_lumen_input'],
        }
        for source in sources
    ]
    model = Multi_Light_Source_Cost(params)
    model._aggregate_sensor_binding = (  # noqa: SLF001
        sensor_binding
        if sensor_binding is not None
        else sensor_geometry_binding()
    )
    return model, path


@lru_cache(maxsize=None)
def sensor_geometry_binding(
    sensor_transform_config_path=SENSOR_TRANSFORM_CONFIG_PATH,
    sensor_geometry_path=SENSOR_GEOMETRY_PATH,
):
    """Load and cross-check the live transform config and URDF geometry."""
    transform_path = (
        Path(sensor_transform_config_path).expanduser().resolve()
    )
    geometry_path = Path(sensor_geometry_path).expanduser().resolve()
    document = json.loads(transform_path.read_text(encoding='utf-8'))
    config = document.get('rotating_frame_one', {})
    if config.get('object_name') != 'Transform_Odom_To_Sensor_Pose':
        raise ValueError(
            'sensor transform owner must be '
            'Transform_Odom_To_Sensor_Pose'
        )
    params = config.get('params', {})
    joint_position = np.asarray(
        params.get('joint_position'),
        dtype=float,
    )
    rotation_axis = np.asarray(
        params.get('rotation_axis'),
        dtype=float,
    )
    sensor_transform = np.asarray(
        params.get('sensor_transform'),
        dtype=float,
    )
    if (
        joint_position.shape != (3,)
        or rotation_axis.shape != (3,)
        or sensor_transform.shape != (4, 4)
        or not np.all(np.isfinite(joint_position))
        or not np.all(np.isfinite(rotation_axis))
        or not np.all(np.isfinite(sensor_transform))
    ):
        raise ValueError('sensor transform configuration is malformed')
    if not np.allclose(
        rotation_axis,
        np.asarray([0.0, 0.0, 1.0]),
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError(
            'aggregate solver requires a positive Z rotation axis'
        )
    if not np.allclose(
        sensor_transform[3],
        np.asarray([0.0, 0.0, 0.0, 1.0]),
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError('sensor transform is not homogeneous')

    root = ET.parse(geometry_path).getroot()
    joint = root.find(".//joint[@name='sensor_joint']")
    origin = joint.find('origin') if joint is not None else None
    if origin is None:
        raise ValueError('sensor_joint origin is missing from robot geometry')
    xyz = [
        float(value)
        for value in str(origin.get('xyz', '')).split()
    ]
    rpy = [
        float(value)
        for value in str(origin.get('rpy', '')).split()
    ]
    if (
        len(xyz) != 3
        or len(rpy) != 3
        or not all(math.isfinite(value) for value in xyz + rpy)
    ):
        raise ValueError('sensor_joint origin is malformed')
    roll, pitch, yaw = rpy
    cosine_roll = math.cos(roll)
    sine_roll = math.sin(roll)
    cosine_pitch = math.cos(pitch)
    sine_pitch = math.sin(pitch)
    cosine_yaw = math.cos(yaw)
    sine_yaw = math.sin(yaw)
    urdf_rotation = np.asarray([
        [
            cosine_yaw * cosine_pitch,
            (
                cosine_yaw * sine_pitch * sine_roll
                - sine_yaw * cosine_roll
            ),
            (
                cosine_yaw * sine_pitch * cosine_roll
                + sine_yaw * sine_roll
            ),
        ],
        [
            sine_yaw * cosine_pitch,
            (
                sine_yaw * sine_pitch * sine_roll
                + cosine_yaw * cosine_roll
            ),
            (
                sine_yaw * sine_pitch * cosine_roll
                - cosine_yaw * sine_roll
            ),
        ],
        [
            -sine_pitch,
            cosine_pitch * sine_roll,
            cosine_pitch * cosine_roll,
        ],
    ])
    if not np.allclose(
        sensor_transform[:3, 3],
        np.asarray(xyz),
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError(
            'sensor transform offset disagrees with sensor_joint geometry'
        )
    if not np.allclose(
        sensor_transform[:3, :3],
        urdf_rotation,
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ValueError(
            'sensor transform rotation disagrees with sensor_joint geometry'
        )
    return {
        'sensor_transform_config_path': str(transform_path),
        'sensor_transform_config_sha256': file_sha256(transform_path),
        'sensor_geometry_path': str(geometry_path),
        'sensor_geometry_sha256': file_sha256(geometry_path),
        'joint_position_m': [
            float(value) for value in joint_position
        ],
        'rotation_axis': [
            float(value) for value in rotation_axis
        ],
        'sensor_offset_xyz_m': [
            float(value) for value in sensor_transform[:3, 3]
        ],
        'sensor_offset_rpy_rad': [
            float(value) for value in rpy
        ],
        'sensor_transform': [
            [float(value) for value in row]
            for row in sensor_transform
        ],
    }


@lru_cache(maxsize=None)
def sensor_offset_m(
    sensor_geometry_path=SENSOR_GEOMETRY_PATH,
    sensor_transform_config_path=SENSOR_TRANSFORM_CONFIG_PATH,
):
    """Read the checked sensor-joint planar offset."""
    binding = sensor_geometry_binding(
        sensor_transform_config_path,
        sensor_geometry_path,
    )
    return binding['sensor_offset_xyz_m'][0]


def _sensor_binding_record(binding):
    return {
        'sensor_transform_config_path': (
            binding['sensor_transform_config_path']
        ),
        'sensor_transform_config_sha256': (
            binding['sensor_transform_config_sha256']
        ),
        'sensor_geometry_path': binding['sensor_geometry_path'],
        'sensor_geometry_sha256': binding['sensor_geometry_sha256'],
        'sensor_joint_position_m': binding['joint_position_m'],
        'sensor_rotation_axis': binding['rotation_axis'],
        'sensor_offset_xyz_m': binding['sensor_offset_xyz_m'],
        'sensor_offset_rpy_rad': binding['sensor_offset_rpy_rad'],
        'sensor_offset_m': binding['sensor_offset_xyz_m'][0],
    }


def _sensor_transform(x_m, y_m, yaw_rad, sensor_binding=None):
    binding = (
        sensor_binding
        if sensor_binding is not None
        else sensor_geometry_binding()
    )
    cosine = math.cos(yaw_rad)
    sine = math.sin(yaw_rad)
    joint_position = binding['joint_position_m']
    odom_transform = np.asarray([
        [1.0, 0.0, 0.0, x_m],
        [0.0, 1.0, 0.0, y_m],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float)
    joint_transform = np.asarray([
        [cosine, -sine, 0.0, joint_position[0]],
        [sine, cosine, 0.0, joint_position[1]],
        [0.0, 0.0, 1.0, joint_position[2]],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=float)
    return (
        odom_transform
        @ joint_transform
        @ np.asarray(binding['sensor_transform'], dtype=float)
    )


def evaluate_raw_cost(model, x_m, y_m, yaw_rad):
    """Evaluate the authoritative scalar cost owner at one pose."""
    value = float(
        model.cost_output(
            0.0,
            _sensor_transform(
                float(x_m),
                float(y_m),
                float(yaw_rad),
                model._aggregate_sensor_binding,  # noqa: SLF001
            ),
        )
    )
    if not math.isfinite(value):
        raise ValueError('aggregate model returned a nonfinite cost')
    return value


def derive_local_branch_qualifications(
    sources,
    source_ids,
    disturbances,
    *,
    threshold=0.95,
    model_config_path=MODEL_CONFIG_PATH,
    sensor_transform_config_path=SENSOR_TRANSFORM_CONFIG_PATH,
    sensor_geometry_path=SENSOR_GEOMETRY_PATH,
):
    """Prove that declared source coordinates stay below goal threshold."""
    normalized_sources = _normalized_sources(sources)
    by_id = {
        source['id']: source for source in normalized_sources
    }
    identifiers = [str(identifier) for identifier in source_ids]
    if (
        not identifiers
        or len(identifiers) != len(set(identifiers))
        or not set(identifiers) <= set(by_id)
    ):
        raise ValueError('local qualification source IDs are invalid')
    limit = _finite_number(threshold, 'threshold')
    sensor_binding = sensor_geometry_binding(
        sensor_transform_config_path,
        sensor_geometry_path,
    )
    model, config_path = _model(
        normalized_sources,
        model_config_path,
        sensor_binding,
    )
    noise_margin = _noise_margin(disturbances)
    yaw_values = _periodic_axis(
        2.0 * math.pi,
        LOCAL_QUALIFICATION_YAW_SPACING_RAD,
        0.0,
    )
    points = []
    for identifier in identifiers:
        source = by_id[identifier]

        def objective(vector):
            return evaluate_raw_cost(
                model,
                source['x_m'],
                source['y_m'],
                float(vector[0]) % (2.0 * math.pi),
            )

        grid_costs = np.asarray([
            objective((yaw_value,)) for yaw_value in yaw_values
        ])
        grid_index = int(np.argmin(grid_costs))
        result = optimize.differential_evolution(
            objective,
            [(0.0, 2.0 * math.pi)],
            seed=0,
            maxiter=60,
            popsize=5,
            tol=1.0e-9,
            atol=1.0e-10,
            polish=True,
            workers=1,
            updating='immediate',
        )
        optimized_yaw = float(result.x[0] % (2.0 * math.pi))
        optimized_cost = objective((optimized_yaw,))
        if float(grid_costs[grid_index]) < optimized_cost:
            optimized_yaw = float(yaw_values[grid_index])
            optimized_cost = float(grid_costs[grid_index])
        score = float(model.source_score(optimized_cost))
        noise_upper = float(
            model.source_score(optimized_cost - noise_margin)
        )
        if noise_upper >= limit:
            raise ValueError(
                f'local source {identifier} reaches score '
                f'{noise_upper:.12g}, not below {limit:.12g}'
            )
        points.append({
            'source_id': identifier,
            'robot_center_x_m': source['x_m'],
            'robot_center_y_m': source['y_m'],
            'peak_yaw_rad': optimized_yaw,
            'peak_raw_cost': optimized_cost,
            'peak_source_score': score,
            'noise_adjusted_source_score_upper_bound': noise_upper,
        })
    record = {
        'schema_version': TRUTH_SCHEMA_VERSION,
        'method': 'authoritative_yaw_peak_at_source_coordinate',
        'model_config_sha256': file_sha256(config_path),
        'source_list_sha256': canonical_sha256(normalized_sources),
        'noise_margin_raw_cost': noise_margin,
        'threshold': limit,
        'yaw_spacing_rad': LOCAL_QUALIFICATION_YAW_SPACING_RAD,
        'points': points,
    } | {
        key: value
        for key, value in _sensor_binding_record(
            sensor_binding
        ).items()
        if not key.endswith('_path')
    }
    record['result_sha256'] = canonical_sha256(record)
    return record


def attach_local_branch_qualifications(
    aggregate_record,
    sources,
    source_ids,
    disturbances,
):
    """Bind local below-threshold proofs into the aggregate result hash."""
    result = deepcopy(aggregate_record)
    result.pop('result_sha256', None)
    result['local_branch_qualifications'] = (
        derive_local_branch_qualifications(
            sources,
            source_ids,
            disturbances,
        )
    )
    result['result_sha256'] = canonical_sha256(result)
    return result


def _axis(minimum, maximum, spacing, offset):
    first = minimum + offset
    if first > maximum:
        raise ValueError('solver offset leaves an empty scan axis')
    count = int(math.floor((maximum - first) / spacing + 1.0e-12)) + 1
    return first + np.arange(count, dtype=float) * spacing


def _periodic_axis(period, spacing, offset):
    if not 0.0 <= offset < period:
        raise ValueError('periodic-axis offset must be inside the period')
    count = int(math.ceil((period - offset) / spacing - 1.0e-12))
    return offset + np.arange(count, dtype=float) * spacing


def _scan_grid(model, domain, settings, offset):
    spacing = settings['position_spacing_m']
    yaw_spacing = settings['yaw_spacing_rad']
    x_values = _axis(domain[0], domain[1], spacing, offset[0])
    y_values = _axis(domain[2], domain[3], spacing, offset[1])
    yaw_values = _periodic_axis(
        2.0 * math.pi,
        yaw_spacing,
        offset[2],
    )
    values = np.empty(
        (len(x_values), len(y_values), len(yaw_values)),
        dtype=float,
    )
    for x_index, x_value in enumerate(x_values):
        for y_index, y_value in enumerate(y_values):
            for yaw_index, yaw_value in enumerate(yaw_values):
                values[x_index, y_index, yaw_index] = evaluate_raw_cost(
                    model, x_value, y_value, yaw_value
                )
    return x_values, y_values, yaw_values, values


def _basin_seeds(x_values, y_values, yaw_values, values, count):
    local_minimum = ndimage.minimum_filter(
        values,
        size=(3, 3, 3),
        mode=('nearest', 'nearest', 'wrap'),
    )
    minimum_mask = values <= local_minimum + 1.0e-15
    labels, label_count = ndimage.label(
        minimum_mask,
        structure=np.ones((3, 3, 3), dtype=int),
    )
    parents = list(range(label_count + 1))

    def root(label):
        while parents[label] != label:
            parents[label] = parents[parents[label]]
            label = parents[label]
        return label

    def union(left, right):
        left_root = root(left)
        right_root = root(right)
        if left_root != right_root:
            parents[max(left_root, right_root)] = min(
                left_root, right_root
            )

    last_yaw = values.shape[2] - 1
    for x_index in range(values.shape[0]):
        for y_index in range(values.shape[1]):
            left_label = int(labels[x_index, y_index, 0])
            if left_label == 0:
                continue
            for x_delta in (-1, 0, 1):
                for y_delta in (-1, 0, 1):
                    other_x = x_index + x_delta
                    other_y = y_index + y_delta
                    if (
                        0 <= other_x < values.shape[0]
                        and 0 <= other_y < values.shape[1]
                    ):
                        right_label = int(
                            labels[other_x, other_y, last_yaw]
                        )
                        if right_label:
                            union(left_label, right_label)
    representatives = {}
    for index in np.argwhere(minimum_mask):
        candidate = (
            float(values[tuple(index)]),
            float(x_values[index[0]]),
            float(y_values[index[1]]),
            float(yaw_values[index[2]]),
        )
        component = root(int(labels[tuple(index)]))
        current = representatives.get(component)
        if current is None or candidate < current:
            representatives[component] = candidate
    return sorted(representatives.values())[:count]


def _refine(model, seed, domain, settings):
    def objective(vector):
        return evaluate_raw_cost(
            model,
            vector[0],
            vector[1],
            vector[2] % (2.0 * math.pi),
        )

    position_radius = 2.0 * settings['position_spacing_m']
    result = optimize.differential_evolution(
        objective,
        [
            (
                max(domain[0], seed[1] - position_radius),
                min(domain[1], seed[1] + position_radius),
            ),
            (
                max(domain[2], seed[2] - position_radius),
                min(domain[3], seed[2] + position_radius),
            ),
            (0.0, 2.0 * math.pi),
        ],
        seed=0,
        maxiter=settings['optimizer_max_iterations'],
        popsize=settings['optimizer_population_size'],
        tol=settings['optimizer_relative_tolerance'],
        atol=settings['optimizer_absolute_tolerance'],
        polish=True,
        workers=1,
        updating='immediate',
    )
    vector = np.asarray(result.x, dtype=float)
    cost = objective(vector)
    seed_cost = objective(seed[1:])
    if seed_cost < cost:
        vector = np.asarray(seed[1:], dtype=float)
        cost = seed_cost
    return {
        'x_m': float(vector[0]),
        'y_m': float(vector[1]),
        'yaw_rad': float(vector[2] % (2.0 * math.pi)),
        'raw_cost': cost,
        'optimizer_success': bool(result.success),
        'optimizer_status': int(getattr(result, 'status', 0)),
        'optimizer_iterations': int(getattr(result, 'nit', 0)),
    }


def _scan_and_refine(model, domain, settings, scan_id, offset):
    x_values, y_values, yaw_values, values = _scan_grid(
        model, domain, settings, offset
    )
    seeds = _basin_seeds(
        x_values,
        y_values,
        yaw_values,
        values,
        settings['retained_basins_per_scan'],
    )
    refinements = [
        _refine(model, seed, domain, settings)
        for seed in seeds
    ]
    refinements.sort(
        key=lambda item: (
            item['raw_cost'],
            item['x_m'],
            item['y_m'],
            item['yaw_rad'],
        )
    )
    return {
        'scan_id': scan_id,
        'offset': {
            'x_m': offset[0],
            'y_m': offset[1],
            'yaw_rad': offset[2],
        },
        'shape': [len(x_values), len(y_values), len(yaw_values)],
        'lattice_basin_count': len(seeds),
        'lattice_best_raw_cost': float(np.min(values)),
        'refined_best_raw_cost': refinements[0]['raw_cost'],
        'refinements': refinements,
    }


def _merge_refinements(refinements, settings):
    merged = []
    for candidate in sorted(
        refinements,
        key=lambda item: (
            item['raw_cost'],
            item['x_m'],
            item['y_m'],
            item['yaw_rad'],
        ),
    ):
        duplicate = any(
            math.hypot(
                candidate['x_m'] - existing['x_m'],
                candidate['y_m'] - existing['y_m'],
            ) <= settings['merge_position_tolerance_m']
            and abs(
                candidate['raw_cost'] - existing['raw_cost']
            ) <= settings['merge_cost_tolerance']
            for existing in merged
        )
        if not duplicate:
            merged.append(dict(candidate))
    return merged


def _noise_margin(disturbances):
    noise = (disturbances or {}).get('sensor_noise', {})
    model = str(noise.get('model', 'none'))
    if model == 'none':
        return 0.0
    if model == 'uniform':
        margin = _finite_number(noise.get('bound', 0.0), 'noise.bound')
    elif model == 'gaussian':
        margin = 3.0 * _finite_number(
            noise.get('std_dev', 0.0), 'noise.std_dev'
        )
    else:
        raise ValueError(f'unsupported noise model: {model}')
    if margin < 0.0:
        raise ValueError('noise margin must be nonnegative')
    return margin


def _solver_settings(overrides):
    settings = dict(DEFAULT_SOLVER_SETTINGS)
    if overrides:
        unknown = sorted(set(overrides) - set(settings))
        if unknown:
            raise ValueError(
                'unknown aggregate solver settings: ' + ', '.join(unknown)
            )
        settings.update(overrides)
    for name in (
        'position_spacing_m',
        'yaw_spacing_rad',
        'offset_position_m',
        'offset_yaw_rad',
        'merge_position_tolerance_m',
        'merge_cost_tolerance',
        'scan_agreement_tolerance',
        'global_equivalence_tolerance',
        'optimizer_relative_tolerance',
        'optimizer_absolute_tolerance',
    ):
        settings[name] = _finite_number(settings[name], name)
        if settings[name] <= 0.0:
            raise ValueError(f'{name} must be positive')
    for name in (
        'retained_basins_per_scan',
        'optimizer_max_iterations',
        'optimizer_population_size',
    ):
        value = settings[name]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f'{name} must be a positive integer')
    if settings['optimizer_method'] != 'differential_evolution':
        raise ValueError(
            'optimizer_method must remain differential_evolution'
        )
    return settings


def derive_aggregate_field_truth(
    sources,
    bounds_m,
    disturbances,
    wall_margin_m=0.35,
    minimum_source_score=0.95,
    model_config_path=MODEL_CONFIG_PATH,
    solver_settings=None,
    sensor_transform_config_path=SENSOR_TRANSFORM_CONFIG_PATH,
    sensor_geometry_path=SENSOR_GEOMETRY_PATH,
):
    """Resolve and qualify deterministic aggregate-field targets."""
    normalized_sources = _normalized_sources(sources)
    bounds, domain, margin = _domain(bounds_m, wall_margin_m)
    minimum_score = _finite_number(
        minimum_source_score, 'minimum_source_score'
    )
    if not 0.0 <= minimum_score <= 1.0:
        raise ValueError('minimum_source_score must be in [0, 1]')
    settings = _solver_settings(solver_settings)
    sensor_binding = sensor_geometry_binding(
        sensor_transform_config_path,
        sensor_geometry_path,
    )
    model, config_path = _model(
        normalized_sources,
        model_config_path,
        sensor_binding,
    )
    scans = [
        _scan_and_refine(
            model,
            domain,
            settings,
            'base',
            (0.0, 0.0, 0.0),
        ),
        _scan_and_refine(
            model,
            domain,
            settings,
            'offset',
            (
                settings['offset_position_m'],
                settings['offset_position_m'],
                settings['offset_yaw_rad'],
            ),
        ),
    ]
    agreement = abs(
        scans[0]['refined_best_raw_cost']
        - scans[1]['refined_best_raw_cost']
    )
    if agreement > settings['scan_agreement_tolerance']:
        raise ValueError(
            'aggregate offset scans disagree: '
            f'{agreement} > {settings["scan_agreement_tolerance"]}'
        )
    merged = _merge_refinements(
        [
            refinement
            for scan in scans
            for refinement in scan['refinements']
        ],
        settings,
    )
    if not merged:
        raise ValueError('aggregate solver produced no finite target')
    best_cost = merged[0]['raw_cost']
    equivalent = [
        target for target in merged
        if target['raw_cost'] - best_cost
        <= settings['global_equivalence_tolerance']
    ]
    noise_margin = _noise_margin(disturbances)
    lower_scores = [
        float(model.source_score(target['raw_cost'] + noise_margin))
        for target in equivalent
    ]
    lower_score = min(lower_scores)
    if not math.isfinite(lower_score):
        raise ValueError('aggregate reachability score is nonfinite')
    if lower_score < minimum_score:
        raise ValueError(
            'aggregate target is below the noise-adjusted source threshold: '
            f'{lower_score} < {minimum_score}'
        )
    targets = []
    for index, (target, target_lower_score) in enumerate(
        zip(equivalent, lower_scores),
        start=1,
    ):
        targets.append({
            'target_id': f'aggregate_{index:03d}',
            'x_m': target['x_m'],
            'y_m': target['y_m'],
            'yaw_rad': target['yaw_rad'],
            'raw_cost': target['raw_cost'],
            'source_score': float(model.source_score(target['raw_cost'])),
            'noise_adjusted_source_score_lower_bound': target_lower_score,
        })
    record = {
        'schema_version': TRUTH_SCHEMA_VERSION,
        'method': 'aggregate_field',
        'model_config_path': str(config_path),
        'model_config_sha256': file_sha256(config_path),
        'source_list_sha256': canonical_sha256(normalized_sources),
        'sources': normalized_sources,
        'bounds_m': bounds,
        'wall_margin_m': margin,
        'domain': {
            'x_min_m': domain[0],
            'x_max_m': domain[1],
            'y_min_m': domain[2],
            'y_max_m': domain[3],
            'yaw_min_rad': 0.0,
            'yaw_max_rad': 2.0 * math.pi,
        },
        'solver_settings': settings,
        'scan_summaries': [
            {
                key: value
                for key, value in scan.items()
                if key != 'refinements'
            }
            for scan in scans
        ],
        'scan_agreement': agreement,
        'global_best_raw_cost': best_cost,
        'noise_margin_raw_cost': noise_margin,
        'noise_adjusted_source_score_lower_bound': lower_score,
        'minimum_source_score': minimum_score,
        'targets': targets,
    } | _sensor_binding_record(sensor_binding)
    record['result_sha256'] = canonical_sha256(record)
    return record


def validate_aggregate_field_truth(
    record,
    sources,
    bounds_m,
    disturbances,
    wall_margin_m=0.35,
    minimum_source_score=0.95,
    model_config_path=MODEL_CONFIG_PATH,
    require_production_settings=True,
    sensor_transform_config_path=SENSOR_TRANSFORM_CONFIG_PATH,
    sensor_geometry_path=SENSOR_GEOMETRY_PATH,
):
    """Validate a precomputed record without rerunning the expensive solver."""
    if not isinstance(record, dict):
        raise ValueError('aggregate truth record must be a mapping')
    candidate = deepcopy(record)
    recorded_hash = candidate.pop('result_sha256', None)
    if not isinstance(recorded_hash, str) or len(recorded_hash) != 64:
        raise ValueError('aggregate truth result_sha256 is invalid')
    if canonical_sha256(candidate) != recorded_hash:
        raise ValueError('aggregate truth result hash drifted')
    normalized_sources = _normalized_sources(sources)
    bounds, domain, margin = _domain(bounds_m, wall_margin_m)
    config_path = Path(model_config_path).expanduser().resolve()
    sensor_binding = sensor_geometry_binding(
        sensor_transform_config_path,
        sensor_geometry_path,
    )
    minimum_score = _finite_number(
        minimum_source_score, 'minimum_source_score'
    )
    expected = {
        'schema_version': TRUTH_SCHEMA_VERSION,
        'method': 'aggregate_field',
        'model_config_sha256': file_sha256(config_path),
        'source_list_sha256': canonical_sha256(normalized_sources),
        'bounds_m': bounds,
        'wall_margin_m': margin,
        'minimum_source_score': minimum_score,
    } | {
        key: value
        for key, value in _sensor_binding_record(
            sensor_binding
        ).items()
        if not key.endswith('_path')
    }
    for key, value in expected.items():
        if candidate.get(key) != value:
            raise ValueError(f'aggregate truth {key} drifted')
    for path_key in (
        'model_config_path',
        'sensor_transform_config_path',
        'sensor_geometry_path',
    ):
        if (
            not isinstance(candidate.get(path_key), str)
            or not candidate[path_key].strip()
        ):
            raise ValueError(f'aggregate truth {path_key} is invalid')
    recorded_domain = candidate.get('domain', {})
    expected_domain = {
        'x_min_m': domain[0],
        'x_max_m': domain[1],
        'y_min_m': domain[2],
        'y_max_m': domain[3],
        'yaw_min_rad': 0.0,
        'yaw_max_rad': 2.0 * math.pi,
    }
    if recorded_domain != expected_domain:
        raise ValueError('aggregate truth domain drifted')
    if candidate.get('sources') != normalized_sources:
        raise ValueError('aggregate truth source list drifted')
    if candidate.get('noise_margin_raw_cost') != _noise_margin(disturbances):
        raise ValueError('aggregate truth noise margin drifted')
    local_qualifications = candidate.get(
        'local_branch_qualifications'
    )
    if local_qualifications is not None:
        if not isinstance(local_qualifications, dict):
            raise ValueError(
                'aggregate local branch qualifications are invalid'
            )
        points = local_qualifications.get('points', [])
        expected_local = derive_local_branch_qualifications(
            normalized_sources,
            [point.get('source_id') for point in points],
            disturbances,
            threshold=local_qualifications.get('threshold', 0.95),
            model_config_path=config_path,
            sensor_transform_config_path=(
                sensor_transform_config_path
            ),
            sensor_geometry_path=sensor_geometry_path,
        )
        if local_qualifications != expected_local:
            raise ValueError(
                'aggregate local branch qualification drifted'
            )
    settings = _solver_settings(candidate.get('solver_settings'))
    if (
        require_production_settings
        and settings != DEFAULT_SOLVER_SETTINGS
    ):
        raise ValueError(
            'aggregate truth solver settings are not the production contract'
        )
    scans = candidate.get('scan_summaries')
    if (
        not isinstance(scans, list)
        or len(scans) != 2
        or [scan.get('scan_id') for scan in scans] != ['base', 'offset']
    ):
        raise ValueError('aggregate truth scan summaries are invalid')
    scan_offsets = (
        (0.0, 0.0, 0.0),
        (
            settings['offset_position_m'],
            settings['offset_position_m'],
            settings['offset_yaw_rad'],
        ),
    )
    for index, (scan, offset) in enumerate(zip(scans, scan_offsets)):
        expected_offset = {
            'x_m': offset[0],
            'y_m': offset[1],
            'yaw_rad': offset[2],
        }
        expected_shape = [
            len(_axis(
                domain[0],
                domain[1],
                settings['position_spacing_m'],
                offset[0],
            )),
            len(_axis(
                domain[2],
                domain[3],
                settings['position_spacing_m'],
                offset[1],
            )),
            len(_periodic_axis(
                2.0 * math.pi,
                settings['yaw_spacing_rad'],
                offset[2],
            )),
        ]
        basin_count = scan.get('lattice_basin_count')
        if (
            scan.get('offset') != expected_offset
            or scan.get('shape') != expected_shape
            or isinstance(basin_count, bool)
            or not isinstance(basin_count, int)
            or not 1 <= basin_count <= settings[
                'retained_basins_per_scan'
            ]
        ):
            raise ValueError(
                f'aggregate truth scan {index} lattice contract drifted'
            )
        lattice_cost = _finite_number(
            scan.get('lattice_best_raw_cost'),
            f'scan_summaries[{index}].lattice_best_raw_cost',
        )
        refined_cost = _finite_number(
            scan.get('refined_best_raw_cost'),
            f'scan_summaries[{index}].refined_best_raw_cost',
        )
        if refined_cost > lattice_cost + 1.0e-12:
            raise ValueError(
                f'aggregate truth scan {index} refinement regressed'
            )
    scan_costs = [
        _finite_number(
            scan.get('refined_best_raw_cost'),
            f'scan_summaries[{index}].refined_best_raw_cost',
        )
        for index, scan in enumerate(scans)
    ]
    scan_agreement = abs(scan_costs[0] - scan_costs[1])
    if (
        candidate.get('scan_agreement') != scan_agreement
        or scan_agreement > settings['scan_agreement_tolerance']
    ):
        raise ValueError('aggregate truth scan agreement failed')
    score = candidate.get('noise_adjusted_source_score_lower_bound')
    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(float(score))
        or float(score) < minimum_score
    ):
        raise ValueError('aggregate truth reachability gate failed')
    targets = candidate.get('targets')
    if not isinstance(targets, list) or not targets:
        raise ValueError('aggregate truth has no targets')
    model, unused_path = _model(
        normalized_sources,
        config_path,
        sensor_binding,
    )
    del unused_path
    target_ids = set()
    target_costs = []
    target_lower_scores = []
    noise_margin = candidate['noise_margin_raw_cost']
    for index, target in enumerate(targets):
        identifier = target.get('target_id')
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in target_ids
        ):
            raise ValueError('aggregate target identifiers are invalid')
        target_ids.add(identifier)
        for name in (
            'x_m',
            'y_m',
            'yaw_rad',
            'raw_cost',
            'source_score',
            'noise_adjusted_source_score_lower_bound',
        ):
            _finite_number(target.get(name), f'targets[{index}].{name}')
        if not (
            domain[0] <= target['x_m'] <= domain[1]
            and domain[2] <= target['y_m'] <= domain[3]
        ):
            raise ValueError('aggregate target is outside the inset domain')
        if not 0.0 <= target['yaw_rad'] < 2.0 * math.pi:
            raise ValueError('aggregate target yaw is outside [0, 2pi)')
        evaluated_cost = evaluate_raw_cost(
            model,
            target['x_m'],
            target['y_m'],
            target['yaw_rad'],
        )
        evaluated_score = float(model.source_score(evaluated_cost))
        evaluated_lower_score = float(
            model.source_score(evaluated_cost + noise_margin)
        )
        if (
            abs(evaluated_cost - target['raw_cost']) > 1.0e-12
            or abs(evaluated_score - target['source_score']) > 1.0e-12
            or abs(
                evaluated_lower_score
                - target['noise_adjusted_source_score_lower_bound']
            ) > 1.0e-12
        ):
            raise ValueError('aggregate target evaluation drifted')
        target_costs.append(evaluated_cost)
        target_lower_scores.append(evaluated_lower_score)
    best_cost = min(target_costs)
    if (
        candidate.get('global_best_raw_cost') != best_cost
        or any(
            cost - best_cost > settings['global_equivalence_tolerance']
            for cost in target_costs
        )
        or any(abs(cost - best_cost) > settings['merge_cost_tolerance']
               for cost in scan_costs)
    ):
        raise ValueError('aggregate truth global optimum drifted')
    if (
        float(score) != min(target_lower_scores)
        or any(value < minimum_score for value in target_lower_scores)
    ):
        raise ValueError('aggregate target reachability drifted')
    return candidate | {'result_sha256': recorded_hash}
