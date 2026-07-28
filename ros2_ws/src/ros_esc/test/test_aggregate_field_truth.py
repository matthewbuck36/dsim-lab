"""Focused tests for deterministic schema-v4 aggregate-field truth."""

from copy import deepcopy
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np

import pytest

from ros_esc.scenario_runner import aggregate_field_truth


BOUNDS_M = [-2.0, 2.0, -2.0, 2.0]
NO_NOISE = {'sensor_noise': {'model': 'none'}}
FAST_SOLVER_SETTINGS = {
    'position_spacing_m': 0.5,
    'yaw_spacing_rad': math.pi / 2.0,
    'offset_position_m': 0.25,
    'offset_yaw_rad': math.pi / 4.0,
    'retained_basins_per_scan': 4,
    'optimizer_max_iterations': 60,
    'optimizer_population_size': 5,
}
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def _source(lumens=2500.0):
    return [{
        'id': 'goal',
        'x_m': 0.0,
        'y_m': 0.0,
        'relative_lumen_input': lumens,
    }]


@pytest.fixture(scope='module')
def route_barrier_truth():
    """Build one bounded two-light route proof for focused tests."""
    sources = [
        {
            'id': 'local',
            'x_m': -0.35,
            'y_m': 0.0,
            'relative_lumen_input': 650.0,
        },
        {
            'id': 'global',
            'x_m': 1.0,
            'y_m': 0.0,
            'relative_lumen_input': 2500.0,
        },
    ]
    start = {'x_m': -1.2, 'y_m': 0.0, 'yaw_rad': 0.0}
    aggregate = aggregate_field_truth.derive_aggregate_field_truth(
        sources,
        BOUNDS_M,
        NO_NOISE,
        solver_settings=FAST_SOLVER_SETTINGS,
    )
    attached = aggregate_field_truth.attach_route_barrier_qualification(
        aggregate,
        sources,
        start,
        'local',
        'global',
        NO_NOISE,
    )
    return sources, start, attached


def test_sensor_geometry_owner_is_declared_runtime_dependency():
    """Ensure isolated installs include the package that owns the URDF."""
    root = ET.parse(PACKAGE_ROOT / 'package.xml').getroot()
    runtime_dependencies = {
        element.text
        for element in root.findall('exec_depend')
    }

    assert 'turtlebot3_rotating_sensor' in runtime_dependencies


def test_low_pair_qualifies_with_independent_default_scans():
    """Resolve the narrow 450-plus-450 aggregate optimum from both lattices."""
    sources = [
        {
            'id': 'left',
            'x_m': -0.05,
            'y_m': 0.0,
            'relative_lumen_input': 450.0,
        },
        {
            'id': 'right',
            'x_m': 0.05,
            'y_m': 0.0,
            'relative_lumen_input': 450.0,
        },
    ]

    record = aggregate_field_truth.derive_aggregate_field_truth(
        sources,
        BOUNDS_M,
        NO_NOISE,
    )

    assert record['scan_agreement'] <= 1.0e-4
    assert [
        scan['shape'][2] for scan in record['scan_summaries']
    ] == [72, 72]
    assert len(record['targets']) == 2
    assert (
        record['noise_adjusted_source_score_lower_bound']
        >= record['minimum_source_score']
    )
    assert aggregate_field_truth.validate_aggregate_field_truth(
        record,
        sources,
        BOUNDS_M,
        NO_NOISE,
    ) == record


def test_fast_solver_is_deterministic_and_records_authoritative_hashes():
    """Retain byte-stable solver output and validate all recorded targets."""
    first = aggregate_field_truth.derive_aggregate_field_truth(
        _source(),
        BOUNDS_M,
        NO_NOISE,
        solver_settings=FAST_SOLVER_SETTINGS,
    )
    second = aggregate_field_truth.derive_aggregate_field_truth(
        _source(),
        BOUNDS_M,
        NO_NOISE,
        solver_settings=FAST_SOLVER_SETTINGS,
    )

    assert second == first
    assert first['model_config_sha256'] == aggregate_field_truth.file_sha256(
        aggregate_field_truth.MODEL_CONFIG_PATH
    )
    assert (
        first['sensor_transform_config_sha256']
        == aggregate_field_truth.file_sha256(
            aggregate_field_truth.SENSOR_TRANSFORM_CONFIG_PATH
        )
    )
    assert first['sensor_geometry_sha256'] == (
        aggregate_field_truth.file_sha256(
            aggregate_field_truth.SENSOR_GEOMETRY_PATH
        )
    )
    assert first['sensor_offset_xyz_m'] == [0.18, 0.0, 0.015]
    assert first['result_sha256'] == aggregate_field_truth.canonical_sha256({
        key: value
        for key, value in first.items()
        if key != 'result_sha256'
    })
    with pytest.raises(ValueError, match='production contract'):
        aggregate_field_truth.validate_aggregate_field_truth(
            first,
            _source(),
            BOUNDS_M,
            NO_NOISE,
        )
    assert aggregate_field_truth.validate_aggregate_field_truth(
        first,
        _source(),
        BOUNDS_M,
        NO_NOISE,
        require_production_settings=False,
    ) == first


def test_route_barrier_proves_two_light_obstructing_local_basin(
    route_barrier_truth,
):
    """Bind a below-target local basin directly into the global route."""
    sources, start, record = route_barrier_truth
    proof = record['route_barrier_qualification']

    assert proof['source_count'] == 2
    assert proof['blocker_source_id'] == 'local'
    assert proof['global_source_id'] == 'global'
    assert 0.25 <= proof['blocker_geometry'][
        'projection_fraction'
    ] <= 0.70
    assert proof['blocker_geometry'][
        'perpendicular_distance_m'
    ] <= 0.15
    assert 0.25 <= proof['basin_geometry'][
        'projection_fraction'
    ] <= 0.70
    assert proof['basin_geometry'][
        'perpendicular_distance_m'
    ] <= 0.15
    assert proof['basin'][
        'noise_adjusted_source_score_upper_bound'
    ] < 0.95
    assert proof[
        'noise_adjusted_basin_depth_raw_cost'
    ] >= 0.015
    assert aggregate_field_truth.validate_aggregate_field_truth(
        record,
        sources,
        BOUNDS_M,
        NO_NOISE,
        require_production_settings=False,
    ) == record

    repeated = aggregate_field_truth.attach_route_barrier_qualification(
        {
            key: value for key, value in record.items()
            if key not in {
                'result_sha256',
                'route_barrier_qualification',
            }
        },
        sources,
        start,
        'local',
        'global',
        NO_NOISE,
    )
    assert repeated['route_barrier_qualification'] == proof


def test_route_barrier_rejects_out_of_scope_or_off_route_cases(
    route_barrier_truth,
):
    """Reject more than three lights and a blocker outside the route."""
    sources, unused_start, record = route_barrier_truth
    aggregate = {
        key: value for key, value in record.items()
        if key not in {
            'result_sha256',
            'route_barrier_qualification',
        }
    }
    four_lights = sources + [
        {
            'id': 'context_1',
            'x_m': 0.0,
            'y_m': 1.0,
            'relative_lumen_input': 300.0,
        },
        {
            'id': 'context_2',
            'x_m': 0.0,
            'y_m': -1.0,
            'relative_lumen_input': 300.0,
        },
    ]
    with pytest.raises(ValueError, match='exactly two or three'):
        aggregate_field_truth.derive_route_barrier_qualification(
            aggregate,
            four_lights,
            {'x_m': -1.2, 'y_m': 0.0},
            'local',
            'global',
            NO_NOISE,
        )
    with pytest.raises(ValueError, match='outside the route corridor'):
        aggregate_field_truth.derive_route_barrier_qualification(
            aggregate,
            sources,
            {'x_m': -1.2, 'y_m': 0.8},
            'local',
            'global',
            NO_NOISE,
        )


def test_validator_rejects_hash_source_noise_and_target_drift():
    """Reject every binding input or authoritative target mismatch."""
    record = aggregate_field_truth.derive_aggregate_field_truth(
        _source(),
        BOUNDS_M,
        NO_NOISE,
        solver_settings=FAST_SOLVER_SETTINGS,
    )
    changed = deepcopy(record)
    changed['targets'][0]['raw_cost'] += 0.01

    with pytest.raises(ValueError, match='result hash drifted'):
        aggregate_field_truth.validate_aggregate_field_truth(
            changed,
            _source(),
            BOUNDS_M,
            NO_NOISE,
            require_production_settings=False,
        )

    changed['result_sha256'] = aggregate_field_truth.canonical_sha256({
        key: value
        for key, value in changed.items()
        if key != 'result_sha256'
    })
    with pytest.raises(ValueError, match='target evaluation drifted'):
        aggregate_field_truth.validate_aggregate_field_truth(
            changed,
            _source(),
            BOUNDS_M,
            NO_NOISE,
            require_production_settings=False,
        )
    with pytest.raises(ValueError, match='source_list_sha256 drifted'):
        aggregate_field_truth.validate_aggregate_field_truth(
            record,
            _source(2400.0),
            BOUNDS_M,
            NO_NOISE,
            require_production_settings=False,
        )
    with pytest.raises(ValueError, match='noise margin drifted'):
        aggregate_field_truth.validate_aggregate_field_truth(
            record,
            _source(),
            BOUNDS_M,
            {'sensor_noise': {'model': 'uniform', 'bound': 0.01}},
            require_production_settings=False,
        )


def test_sensor_transform_uses_robot_center_and_live_joint_offset():
    """Evaluate at the sensor while retaining robot-center targets."""
    transform = aggregate_field_truth._sensor_transform(
        1.0,
        2.0,
        math.pi / 2.0,
    )

    assert aggregate_field_truth.sensor_offset_m() == pytest.approx(0.18)
    assert transform[0, 3] == pytest.approx(1.0)
    assert transform[1, 3] == pytest.approx(2.18)
    assert transform[2, 3] == pytest.approx(0.37)


def test_isolated_package_shares_resolve_and_bind_matching_geometry(
    tmp_path,
):
    """Use installed resources without relying on a source-tree egg link."""
    share_root = tmp_path / 'prefix' / 'share'
    ros_esc_share = share_root / 'ros_esc'
    turtlebot_share = share_root / 'turtlebot3_rotating_sensor'
    installed_model = (
        ros_esc_share
        / aggregate_field_truth.MODEL_CONFIG_RESOURCE_PATH
    )
    installed_transform = (
        ros_esc_share
        / aggregate_field_truth.SENSOR_TRANSFORM_CONFIG_RESOURCE_PATH
    )
    installed_urdf = (
        turtlebot_share
        / aggregate_field_truth.SENSOR_GEOMETRY_RESOURCE_PATH
    )
    for destination, source in (
        (installed_model, aggregate_field_truth.MODEL_CONFIG_PATH),
        (
            installed_transform,
            aggregate_field_truth.SENSOR_TRANSFORM_CONFIG_PATH,
        ),
        (installed_urdf, aggregate_field_truth.SENSOR_GEOMETRY_PATH),
    ):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    shares = {
        'ros_esc': ros_esc_share,
        'turtlebot3_rotating_sensor': turtlebot_share,
    }
    resolved = aggregate_field_truth.resolve_authoritative_paths(
        package_share_resolver=lambda package: shares[package],
        source_ros_esc_root=tmp_path / 'absent-source-package',
    )

    assert resolved == {
        'model_config_path': installed_model.resolve(),
        'sensor_transform_config_path': installed_transform.resolve(),
        'sensor_geometry_path': installed_urdf.resolve(),
    }
    binding = aggregate_field_truth.sensor_geometry_binding(
        resolved['sensor_transform_config_path'],
        resolved['sensor_geometry_path'],
    )
    assert binding['sensor_offset_xyz_m'] == [0.18, 0.0, 0.015]
    assert binding['sensor_offset_rpy_rad'] == [0.0, 0.0, 0.0]

    source_record = aggregate_field_truth.derive_aggregate_field_truth(
        _source(),
        BOUNDS_M,
        NO_NOISE,
        solver_settings=FAST_SOLVER_SETTINGS,
    )
    assert aggregate_field_truth.validate_aggregate_field_truth(
        source_record,
        _source(),
        BOUNDS_M,
        NO_NOISE,
        model_config_path=resolved['model_config_path'],
        require_production_settings=False,
        sensor_transform_config_path=(
            resolved['sensor_transform_config_path']
        ),
        sensor_geometry_path=resolved['sensor_geometry_path'],
    ) == source_record

    mismatched_urdf = turtlebot_share / 'urdf' / 'mismatched.urdf'
    mismatched_urdf.write_text(
        Path(installed_urdf).read_text(encoding='utf-8').replace(
            'origin xyz="0.18 0 0.015"',
            'origin xyz="0.19 0 0.015"',
        ),
        encoding='utf-8',
    )
    with pytest.raises(ValueError, match='offset disagrees'):
        aggregate_field_truth.sensor_geometry_binding(
            installed_transform,
            mismatched_urdf,
        )


def test_lattice_basin_selection_merges_plateaus_and_keeps_distinct_minima():
    """Use connected periodic minima instead of adjacent best grid cells."""
    axis = np.arange(7, dtype=float)
    yaw = np.arange(4, dtype=float) * (math.pi / 2.0)
    plateau = np.zeros((7, 7, 4), dtype=float)

    plateau_seeds = aggregate_field_truth._basin_seeds(
        axis,
        axis,
        yaw,
        plateau,
        32,
    )

    assert len(plateau_seeds) == 1

    x_grid, y_grid, yaw_grid = np.meshgrid(
        axis,
        axis,
        np.arange(4, dtype=float),
        indexing='ij',
    )
    first = (
        (x_grid - 1.0) ** 2
        + (y_grid - 1.0) ** 2
        + np.minimum(yaw_grid, 4.0 - yaw_grid) ** 2
    )
    second = (
        (x_grid - 5.0) ** 2
        + (y_grid - 5.0) ** 2
        + np.minimum(
            np.abs(yaw_grid - 2.0),
            4.0 - np.abs(yaw_grid - 2.0),
        ) ** 2
    )
    two_basin_values = np.minimum(first, second)

    seeds = aggregate_field_truth._basin_seeds(
        axis,
        axis,
        yaw,
        two_basin_values,
        32,
    )

    assert len(seeds) == 2


def test_rejects_unreachable_source_and_offset_scan_disagreement(monkeypatch):
    """Close reachability and independent-scan qualification failures."""
    with pytest.raises(ValueError, match='below the noise-adjusted'):
        aggregate_field_truth.derive_aggregate_field_truth(
            _source(450.0),
            BOUNDS_M,
            NO_NOISE,
            solver_settings=FAST_SOLVER_SETTINGS,
        )

    def disagree(
        unused_model,
        unused_domain,
        unused_settings,
        scan_id,
        offset,
    ):
        cost = -1.0 if scan_id == 'base' else -0.9
        return {
            'scan_id': scan_id,
            'offset': {
                'x_m': offset[0],
                'y_m': offset[1],
                'yaw_rad': offset[2],
            },
            'shape': [1, 1, 1],
            'lattice_basin_count': 1,
            'lattice_best_raw_cost': cost,
            'refined_best_raw_cost': cost,
            'refinements': [],
        }

    monkeypatch.setattr(
        aggregate_field_truth,
        '_scan_and_refine',
        disagree,
    )
    with pytest.raises(ValueError, match='offset scans disagree'):
        aggregate_field_truth.derive_aggregate_field_truth(
            _source(),
            BOUNDS_M,
            NO_NOISE,
            solver_settings=FAST_SOLVER_SETTINGS,
        )
