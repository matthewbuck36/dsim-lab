"""Frozen M1a numerical enclosures subordinate to the existing bag analyzer.

The model callback remains owned by aggregate_field_truth. These sampled
enclosures are operational labels, never continuous attraction-basin proofs.
"""

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import warnings

import numpy as np
from scipy.integrate import quad
from scipy.ndimage import binary_dilation, label


CANONICAL_CONTRACT_SHA256 = '702b127705e811e2d594229557b05ce207397e05b1066909fd948204b3ccb9e0'


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def validate_contract(contract):
    """Reject any drift in the complete prospectively frozen contract."""
    if hashlib.sha256(_canonical(contract)).hexdigest() != CANONICAL_CONTRACT_SHA256:
        raise ValueError('M1a frozen contract changed')
    return contract['geometry']


def atomic_exclusive_json(path, document):
    """Publish a complete file atomically without replacing existing evidence."""
    path = Path(path)
    payload = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', prefix='.pending-',
                dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # A hard-link publication is atomic and fails if the destination exists.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _breakpoints(xy, sources, shift_degrees):
    values = {math.radians(angle) for angle in range(shift_degrees, 360, 30)}
    for source in sources:
        dx, dy = source['x_m'] - xy[0], source['y_m'] - xy[1]
        if dx != 0.0 or dy != 0.0:
            bearing = math.atan2(dy, dx)
            values.update((bearing % math.tau, (bearing + math.pi) % math.tau))
    return sorted(value for value in values if 0.0 < value < math.tau)


def integrate_location(xy, sources, evaluate_raw_cost, contract):
    """Return both bounded adaptive angular integrals and their uncertainty."""
    settings = validate_contract(contract)
    passes = []
    for shift in (0, settings['second_partition_shift_degrees']):
        points = _breakpoints(xy, sources, shift)
        receipt = {'breakpoints_rad': points, 'mean': None, 'reported_mean_error': None,
                   'evaluations': 0, 'warnings': [], 'exception': None}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            try:
                def integrand(angle):
                    value = float(evaluate_raw_cost(float(xy[0]), float(xy[1]), angle))
                    if not math.isfinite(value):
                        raise ValueError('nonfinite raw cost')
                    return value

                result = quad(
                    integrand, 0.0, math.tau, points=points, full_output=True,
                    epsabs=settings['epsabs_integral'], epsrel=settings['epsrel'],
                    limit=settings['quad_limit'],
                )
                mean, error = float(result[0] / math.tau), float(result[1] / math.tau)
                if not math.isfinite(mean) or not math.isfinite(error) or error < 0:
                    raise ValueError('invalid quadrature result')
                receipt.update(mean=mean, reported_mean_error=error,
                               evaluations=int(result[2]['neval']))
                receipt['warnings'].extend(str(message) for message in result[3:])
            except TimeoutError:
                raise  # Resource interruption retains an incomplete attempt.
            except Exception as exc:  # A numerical failure is retained as unknown.
                receipt['exception'] = f'{type(exc).__name__}: {exc}'
            receipt['warnings'].extend(str(item.message) for item in caught)
        passes.append(receipt)
    failed = any(item['exception'] or item['warnings'] for item in passes)
    mean = error = None
    if not failed:
        mean = 0.5 * passes[0]['mean'] + 0.5 * passes[1]['mean']
        error = max(*(item['reported_mean_error'] for item in passes),
                    abs(passes[0]['mean'] - passes[1]['mean']))
        failed = not math.isfinite(mean) or not math.isfinite(error)
        if failed:
            mean = error = None
    qualified = not failed and error <= settings['mean_error_ceiling']
    return {'qualified': bool(qualified), 'mean': mean, 'uncertainty': error,
            'passes': passes}


class _UnknownEnclosure(Exception):
    pass


def qualify_enclosure(source, sources, bounds_m, *, evaluate_raw_cost, contract,
                      receipt_directory, provenance):
    """Build one frozen source enclosure, saving every completed point receipt.

    The caller supplies the existing model-owner callback and verified input/
    configuration provenance. Its geometry-group loop enforces the six-source
    population cap; this helper enforces the per-source numerical construction.
    A timeout leaves only completed receipts, never a fabricated final result.
    """
    settings = validate_contract(contract)
    source_id = str(source['id'])
    seed = np.asarray([source['x_m'], source['y_m']], dtype=float)
    bounds = np.asarray(bounds_m, dtype=float)
    if (not source_id or seed.shape != (2,) or not np.isfinite(seed).all()
            or bounds.shape != (4,) or not np.isfinite(bounds).all()
            or bounds[0] >= bounds[1] or bounds[2] >= bounds[3]
            or not isinstance(provenance, dict) or not provenance):
        raise ValueError('invalid enclosure inputs or absent provenance')
    for item in sources:
        if not all(math.isfinite(float(item[key])) for key in ('x_m', 'y_m')):
            raise ValueError('nonfinite source location')
    if not any(item['id'] == source_id and float(item['x_m']) == seed[0]
               and float(item['y_m']) == seed[1] for item in sources):
        raise ValueError('exploration source is absent from recorded geometry')

    output = Path(receipt_directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    width, spacing = settings['square_half_width_m'], settings['grid_spacing_m']
    count = settings['grid_vertex_count_per_axis']
    origin = seed - width
    identity = {'source': source, 'sources': sources, 'bounds_m': list(map(float, bounds)),
                'provenance': provenance, 'canonical_contract_sha256': CANONICAL_CONTRACT_SHA256,
                'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    identity_hash = hashlib.sha256(_canonical(identity)).hexdigest()
    atomic_exclusive_json(output / 'started.json', {
        **identity, 'enclosure_identity_sha256': identity_hash,
        'contract': contract, 'status': 'started',
    })
    points = {}
    receipts = []
    document = {'source_id': source_id, 'qualified': False, 'reason': None,
                'method': 'm1a_finite_sampled_enclosure_v1',
                'canonical_contract_sha256': CANONICAL_CONTRACT_SHA256,
                'enclosure_identity_sha256': identity_hash,
                'grid_origin_xy': origin.tolist(), 'grid_spacing_m': spacing,
                'grid_vertex_count_per_axis': count,
                'spatial_resolution_diagonal_m': math.sqrt(2) * spacing,
                'boundary_tolerance_m': settings['boundary_tolerance_m'],
                'claim': settings['claim'], 'positive_cells': [], 'exclusion_cells': []}

    def finish(reason=None):
        document.update(reason=reason, completed_location_count=len(receipts),
                        point_receipts=receipts)
        atomic_exclusive_json(output / 'geometry.json', document)
        return document

    def observe(ix, iy):
        key = (ix, iy)
        if key not in points:
            if len(points) >= settings['maximum_locations_per_source']:
                raise RuntimeError('frozen location budget exceeded')
            xy = origin + np.asarray(key) * (spacing / 2)
            value = integrate_location(xy, sources, evaluate_raw_cost, contract)
            point = {'half_grid_index_xy': list(key), 'xy_m': xy.tolist(),
                     'enclosure_identity_sha256': identity_hash,
                     'canonical_contract_sha256': CANONICAL_CONTRACT_SHA256, **value}
            path = output / f'point_{ix:03d}_{iy:03d}.json'
            point_hash = atomic_exclusive_json(path, point)
            receipts.append({'path': str(path), 'sha256': point_hash})
            points[key] = value
            if not value['qualified']:
                raise _UnknownEnclosure('angular_integration_unqualified')
        return points[key]

    if not (bounds[0] <= origin[0] and seed[0] + width <= bounds[1]
            and bounds[2] <= origin[1] and seed[1] + width <= bounds[3]):
        return finish('exploration_square_outside_bounds')

    try:
        upper = np.empty((count, count))
        boundary = set()
        for iy in range(count):
            for ix in range(count):
                value = observe(2 * ix, 2 * iy)
                upper[iy, ix] = value['mean'] + value['uncertainty']
                if ix in (0, count - 1) or iy in (0, count - 1):
                    boundary.add((2 * ix, 2 * iy))
        last = 2 * (count - 1)
        for index in range(count - 1):
            for key in ((2*index+1, 0), (2*index+1, last),
                        (0, 2*index+1), (last, 2*index+1)):
                observe(*key)
                boundary.add(key)
        boundary_lower = min(points[key]['mean'] - points[key]['uncertainty']
                             for key in boundary)

        def level():
            minimum_upper = min(item['mean'] + item['uncertainty'] for item in points.values())
            error = max(settings['error_floor'],
                        max(item['uncertainty'] for item in points.values()))
            depth = boundary_lower - minimum_upper
            threshold = minimum_upper + settings['level_fraction'] * depth
            if not all(math.isfinite(value) for value in (minimum_upper, depth, threshold)):
                raise _UnknownEnclosure('nonfinite_enclosure_arithmetic')
            return {'minimum_upper': minimum_upper, 'boundary_lower': boundary_lower,
                    'maximum_uncertainty': error, 'barrier_lower': depth,
                    'threshold': threshold,
                    'qualified': depth > settings['minimum_barrier_error_ratio_strict'] * error}

        provisional = level()
        document['provisional_level'] = provisional
        if not provisional['qualified']:
            return finish('unresolved_barrier')
        low = upper < provisional['threshold']
        candidates = low[:-1, :-1] & low[1:, :-1] & low[:-1, 1:] & low[1:, 1:]
        center_upper = np.full((count - 1, count - 1), np.inf)
        for iy, ix in np.argwhere(candidates):
            value = observe(2 * int(ix) + 1, 2 * int(iy) + 1)
            center_upper[iy, ix] = value['mean'] + value['uncertainty']
        final = level()
        document['final_level'] = final
        if not final['qualified']:
            return finish('unresolved_barrier_after_centers')
        if final['threshold'] > provisional['threshold']:
            raise RuntimeError('one-pass threshold unexpectedly increased')
        low = upper < final['threshold']
        vertex_components = int(label(low, structure=np.ones((3, 3), dtype=int))[1])
        accepted = (low[:-1, :-1] & low[1:, :-1] & low[:-1, 1:] & low[1:, 1:]
                    & (center_upper < final['threshold']))
        cell_components = int(label(accepted)[1])
        document.update(vertex_components=vertex_components, cell_components=cell_components,
                        positive_cell_count=int(accepted.sum()))
        if vertex_components != 1:
            return finish('competing_or_empty_vertex_components')
        if low[0].any() or low[-1].any() or low[:, 0].any() or low[:, -1].any():
            return finish('vertex_boundary_contact')
        if cell_components != 1 or accepted.sum() < settings['minimum_positive_cells']:
            return finish('disconnected_or_insufficient_positive_cells')
        if (accepted[0].any() or accepted[-1].any()
                or accepted[:, 0].any() or accepted[:, -1].any()):
            return finish('cell_boundary_contact')
        possible = low[:-1, :-1] | low[1:, :-1] | low[:-1, 1:] | low[1:, 1:]
        exclusion = binary_dilation(possible, structure=np.ones((3, 3), dtype=bool))
        indices_yx = np.argwhere(accepted)
        centers = origin + (indices_yx[:, ::-1] + 0.5) * spacing
        center = centers.mean(axis=0)
        vertices = np.concatenate([centers + np.asarray(offset) * spacing / 2
                                   for offset in ((-1, -1), (-1, 1), (1, -1), (1, 1))])
        radius = float(np.linalg.norm(vertices - center, axis=1).max())
        document.update(qualified=True, positive_cells=accepted.tolist(),
                        exclusion_cells=exclusion.tolist(), low_vertices=low.tolist(),
                        center_xy=center.tolist(), region_radius_m=radius,
                        positive_area_m2=float(accepted.sum() * spacing**2),
                        boundary_witness_half_grid_indices_xy=[list(key) for key in sorted(boundary)])
        return finish()
    except _UnknownEnclosure as exc:
        return finish(str(exc))


class EnclosureMembership:
    """Compile immutable JSON masks once for repeated trajectory queries."""

    def __init__(self, basin):
        self.qualified = bool(basin.get('qualified'))
        self.origin = np.asarray(basin.get('grid_origin_xy', []), dtype=float)
        self.spacing = float(basin.get('grid_spacing_m', math.nan))
        self.tolerance = float(basin.get('boundary_tolerance_m', 1e-9))
        self.positive = np.asarray(basin.get('positive_cells', []), dtype=bool)
        self.exclusion = np.asarray(basin.get('exclusion_cells', []), dtype=bool)
        self.qualified = bool(self.qualified and self.origin.shape == (2,)
                              and np.isfinite(self.origin).all()
                              and math.isfinite(self.spacing) and self.spacing > 0
                              and self.positive.ndim == 2 and self.positive.size
                              and self.positive.shape == self.exclusion.shape
                              and self.tolerance == 1e-9)

    def contains(self, xy, positive):
        if not self.qualified:
            return False
        try:
            point = np.asarray(xy, dtype=float)
        except (TypeError, ValueError, OverflowError):
            return False
        if point.shape != (2,) or not np.isfinite(point).all():
            return False
        with np.errstate(over='ignore', invalid='ignore'):
            coordinates = (point - self.origin) / self.spacing
        if not np.isfinite(coordinates).all():
            return False
        incident = []
        for value in coordinates:
            closest = round(float(value))
            incident.append((closest - 1, closest) if abs(value - closest) * self.spacing
                            <= self.tolerance else (math.floor(float(value)),))
        mask = self.positive if positive else self.exclusion
        values = [0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and bool(mask[y, x])
                  for x in incident[0] for y in incident[1]]
        return all(values) if positive else any(values)

    def segment(self, start, end, positive):
        if not self.qualified:
            return False
        try:
            a, b = np.asarray(start, dtype=float), np.asarray(end, dtype=float)
        except (TypeError, ValueError, OverflowError):
            return False
        if a.shape != (2,) or b.shape != (2,) or not np.isfinite([a, b]).all():
            return False
        with np.errstate(over='ignore', invalid='ignore'):
            change = b - a
            coordinates = (np.asarray([a, b]) - self.origin) / self.spacing
        if not np.isfinite(change).all() or not np.isfinite(coordinates).all():
            return False
        times = {0.0, 1.0}
        for axis, count in enumerate(self.positive.shape[::-1]):
            if change[axis] == 0:
                continue
            lines = self.origin[axis] + np.arange(count + 1) * self.spacing
            for shift in (-self.tolerance, 0.0, self.tolerance):
                crossings = (lines + shift - a[axis]) / change[axis]
                times.update(float(value) for value in crossings if 0 < value < 1)
        times = sorted(times)
        probes = times + [(left + right) / 2 for left, right in zip(times, times[1:])]
        return all(self.contains(a + time * change, positive) == positive for time in probes)


def prepare_membership(basin):
    return basin if isinstance(basin, EnclosureMembership) else EnclosureMembership(basin)


def point_in_positive(xy, basin):
    return prepare_membership(basin).contains(xy, True)


def segment_in_positive(start_xy, end_xy, basin):
    return prepare_membership(basin).segment(start_xy, end_xy, True)


def segment_outside_exclusion(start_xy, end_xy, basin):
    return prepare_membership(basin).segment(start_xy, end_xy, False)
