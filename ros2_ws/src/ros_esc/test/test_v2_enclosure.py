"""Frozen enclosure construction and exact cell-union trajectory semantics."""

from copy import deepcopy
import json
import math
from pathlib import Path
import warnings

import numpy as np
import pytest
from scipy.integrate import IntegrationWarning

from ros_esc.plotting_scripts import v2_enclosure as enclosure


@pytest.fixture
def contract():
    root = Path(__file__).resolve().parents[4]
    return json.loads((root / 'docs/codex/gesc_gaussian/v2/validation/m1a_contract_v1.json').read_text())


SOURCE = {'id': 'fixture', 'x_m': 0.0, 'y_m': 0.0}


@pytest.fixture
def analytic_integrals(monkeypatch):
    """Exact angular-independent fixtures exercise the full frozen spatial grid."""
    def integrate(xy, sources, evaluate, contract):
        enclosure.validate_contract(contract)
        mean = float(evaluate(*xy, 0.0))
        return {'qualified': True, 'mean': mean, 'uncertainty': 1e-10,
                'passes': [{'mean': mean, 'reported_mean_error': 1e-10,
                            'evaluations': 1, 'warnings': [], 'exception': None}] * 2}
    monkeypatch.setattr(enclosure, 'integrate_location', integrate)
    return integrate


def _qualify(tmp_path, contract, field, **kwargs):
    return enclosure.qualify_enclosure(
        SOURCE, [SOURCE], kwargs.pop('bounds', [-2, 2, -2, 2]),
        evaluate_raw_cost=field, contract=contract,
        receipt_directory=tmp_path / 'source', provenance={'fixture': 'analytic'}, **kwargs)


def test_dual_integral_is_cycle_mean_and_records_distinct_partitions(contract):
    value = enclosure.integrate_location(
        [0.2, 0.3], [SOURCE],
        lambda x, y, angle: x*x+y*y+math.sin(angle)+0.25*math.cos(2*angle), contract)
    assert value['qualified']
    assert value['mean'] == pytest.approx(0.13, abs=1e-12)
    assert value['uncertainty'] < 1e-6
    assert value['passes'][0]['breakpoints_rad'] != value['passes'][1]['breakpoints_rad']
    bearing = math.atan2(-0.3, -0.2) % math.tau
    assert all(bearing in item['breakpoints_rad'] for item in value['passes'])
    assert all(item['evaluations'] > 0 for item in value['passes'])


@pytest.mark.parametrize('fault', ['warning', 'message', 'nonfinite', 'disagreement', 'error'])
def test_dual_integral_rejects_unreliable_numerics(contract, monkeypatch, fault):
    calls = []

    def fake_quad(callback, *args, **kwargs):
        calls.append(kwargs)
        if fault == 'warning':
            warnings.warn('unresolved integration', IntegrationWarning)
        value = math.nan if fault == 'nonfinite' else (
            3e-6*math.tau if fault == 'disagreement' and len(calls) == 2 else 0.0)
        error = 1.1e-6*math.tau if fault == 'error' else 1e-10
        result = (value, error, {'neval': 21})
        return result + ('quad failed',) if fault == 'message' else result

    monkeypatch.setattr(enclosure, 'quad', fake_quad)
    value = enclosure.integrate_location([0, 0], [SOURCE], lambda *args: 0.0, contract)
    assert not value['qualified']
    assert len(value['passes']) == 2
    assert len(calls) == 2
    assert all(item['limit'] == 128 for item in calls)


def test_nonfinite_model_output_is_unknown(contract):
    value = enclosure.integrate_location([0, 0], [SOURCE], lambda *args: math.nan, contract)
    assert not value['qualified']
    assert all('nonfinite raw cost' in item['exception'] for item in value['passes'])


def test_changed_contract_rejected_before_any_output(tmp_path, contract):
    changed = deepcopy(contract)
    changed['geometry']['quad_limit'] = 129
    with pytest.raises(ValueError, match='frozen contract changed'):
        _qualify(tmp_path, changed, lambda *args: 0.0)
    assert not list(tmp_path.iterdir())


def test_annular_region_preserves_hole_and_learns_shifted_center(
        tmp_path, contract, analytic_integrals):
    def field(x, y, angle):
        radius = math.hypot(x-0.12, y+0.08)
        return -math.exp(-((radius-0.35)/0.12)**2)

    result = _qualify(tmp_path, contract, field)
    assert result['qualified']
    assert result['vertex_components'] == result['cell_components'] == 1
    assert result['center_xy'] == pytest.approx([0.12, -0.08], abs=0.025)
    assert not enclosure.point_in_positive([0.12, -0.08], result)
    assert enclosure.point_in_positive([0.47, -0.08], result)
    assert result['positive_cell_count'] >= 4
    assert result['completed_location_count'] <= 2241
    assert result['final_level']['threshold'] <= result['provisional_level']['threshold']
    assert len(result['boundary_witness_half_grid_indices_xy']) == 256
    assert len(list((tmp_path / 'source').glob('point_*.json'))) == result['completed_location_count']
    assert json.loads((tmp_path / 'source/geometry.json').read_text()) == result
    possible = np.asarray(result['low_vertices'])
    incident = possible[:-1, :-1] | possible[1:, :-1] | possible[:-1, 1:] | possible[1:, 1:]
    exclusion = np.asarray(result['exclusion_cells'])
    assert np.all(exclusion[incident])
    assert exclusion.sum() > incident.sum()
    assert np.all(exclusion[np.asarray(result['positive_cells'])])


@pytest.mark.parametrize('field,reason', [
    (lambda x, y, a: 0.0, 'unresolved_barrier'),
    (lambda x, y, a: x, 'unresolved_barrier'),
    (lambda x, y, a: -math.exp(-((x-.3)**2+y*y)/.0064)
     -math.exp(-((x+.3)**2+y*y)/.0064), 'competing_or_empty_vertex_components'),
])
def test_flat_open_and_competing_fields_remain_unknown(
        tmp_path, contract, analytic_integrals, field, reason):
    result = _qualify(tmp_path, contract, field)
    assert not result['qualified']
    assert result['reason'] == reason
    assert not result['positive_cells']


def test_diagonal_only_positive_cells_do_not_connect(tmp_path, contract, analytic_integrals):
    spacing = contract['geometry']['grid_spacing_m']

    def field(x, y, angle):
        u, v = (x+.75)/spacing, (y+.75)/spacing
        return -1.0 if ((5 <= u <= 7 and 5 <= v <= 7)
                        or (7 <= u <= 9 and 7 <= v <= 9)) else 0.0

    result = _qualify(tmp_path, contract, field)
    assert not result['qualified']
    assert result['vertex_components'] == 1
    assert result['cell_components'] == 2
    assert result['reason'] == 'disconnected_or_insufficient_positive_cells'


def test_cell_centers_must_qualify_even_when_corners_are_low(
        tmp_path, contract, analytic_integrals):
    spacing = contract['geometry']['grid_spacing_m']

    def field(x, y, angle):
        u, v = (x+.75)/spacing, (y+.75)/spacing
        if abs(u % 1 - .5) < 1e-12 and abs(v % 1 - .5) < 1e-12:
            return 10.0
        return -math.exp(-((math.hypot(x, y)-.35)/.12)**2)

    result = _qualify(tmp_path, contract, field)
    assert not result['qualified']
    assert result['vertex_components'] == 1
    assert result['positive_cell_count'] == 0
    assert result['reason'] == 'disconnected_or_insufficient_positive_cells'


def test_bounds_are_not_clipped_to_obtain_enclosure(tmp_path, contract):
    def forbidden(*args):
        pytest.fail('out-of-bounds geometry must not be evaluated')

    result = _qualify(tmp_path, contract, forbidden, bounds=[-.7, .75, -.75, .75])
    assert result['reason'] == 'exploration_square_outside_bounds'
    assert result['completed_location_count'] == 0


def test_numerical_failure_retains_completed_point_receipt(tmp_path, contract):
    result = _qualify(tmp_path, contract, lambda *args: math.nan)
    assert result['reason'] == 'angular_integration_unqualified'
    assert result['completed_location_count'] == 1
    point = json.loads(next((tmp_path / 'source').glob('point_*.json')).read_text())
    assert not point['qualified']
    assert point['enclosure_identity_sha256'] == result['enclosure_identity_sha256']


def test_timeout_preserves_partial_receipts_without_completed_geometry(
        tmp_path, contract, analytic_integrals, monkeypatch):
    calls = []

    def interrupted(*args):
        calls.append(None)
        if len(calls) == 4:
            raise TimeoutError('finite attempt interrupted')
        return analytic_integrals(*args)

    monkeypatch.setattr(enclosure, 'integrate_location', interrupted)
    with pytest.raises(TimeoutError):
        _qualify(tmp_path, contract, lambda *args: 0.0)
    assert len(list((tmp_path / 'source').glob('point_*.json'))) == 3
    assert (tmp_path / 'source/started.json').exists()
    assert not (tmp_path / 'source/geometry.json').exists()
    with pytest.raises(FileExistsError):
        _qualify(tmp_path, contract, lambda *args: 0.0)


def test_quadrature_timeout_is_not_a_completed_unknown_source(contract):
    def interrupted(*args):
        raise TimeoutError('budget')
    with pytest.raises(TimeoutError):
        enclosure.integrate_location([0, 0], [SOURCE], interrupted, contract)


def test_atomic_publication_never_replaces_evidence_or_leaves_partial_final(tmp_path, monkeypatch):
    path = tmp_path / 'receipt.json'
    enclosure.atomic_exclusive_json(path, {'value': 1})
    with pytest.raises(FileExistsError):
        enclosure.atomic_exclusive_json(path, {'value': 2})
    assert json.loads(path.read_text()) == {'value': 1}

    def interrupted(*args):
        raise TimeoutError('before publication')
    monkeypatch.setattr(enclosure.os, 'link', interrupted)
    with pytest.raises(TimeoutError):
        enclosure.atomic_exclusive_json(tmp_path / 'absent.json', {'value': 3})
    assert not (tmp_path / 'absent.json').exists()
    assert not list(tmp_path.glob('.pending-*'))


def _membership(positive=None, exclusion=None):
    if positive is None:
        positive = np.ones((5, 5), dtype=bool)
        positive[2, 2] = False
    if exclusion is None:
        exclusion = np.zeros((5, 5), dtype=bool)
        exclusion[2, 2] = True
    return enclosure.prepare_membership({
        'qualified': True, 'grid_origin_xy': [0, 0], 'grid_spacing_m': 1.0,
        'boundary_tolerance_m': 1e-9,
        'positive_cells': positive.tolist(), 'exclusion_cells': exclusion.tolist()})


def test_positive_membership_excludes_outer_and_hole_boundaries():
    region = _membership()
    assert enclosure.point_in_positive([1.5, 1.5], region)
    assert enclosure.point_in_positive([1, 1.5], region)  # Shared internal edge.
    assert enclosure.point_in_positive([1, 1], region)  # Four incident cells.
    for xy in ([0, 1.5], [5e-10, 1.5], [2.5, 2.5], [2, 2.5], [2, 2]):
        assert not enclosure.point_in_positive(xy, region)


def test_segment_crossing_hole_is_unknown_despite_positive_endpoints():
    region = _membership()
    assert enclosure.point_in_positive([1.5, 2.5], region)
    assert enclosure.point_in_positive([3.5, 2.5], region)
    assert not enclosure.segment_in_positive([1.5, 2.5], [3.5, 2.5], region)
    assert enclosure.segment_in_positive([1, .5], [1, 4.5], region)
    assert not enclosure.segment_in_positive([.5, 0], [4.5, 0], region)


def test_negative_exclusion_uses_closed_segments_and_boundary_tolerance():
    region = _membership()
    assert not enclosure.segment_outside_exclusion([1.5, 2.5], [3.5, 2.5], region)
    assert not enclosure.segment_outside_exclusion([1.5, 2.5], [2.5, 1.5], region)
    assert not enclosure.segment_outside_exclusion([1, 2-5e-10], [4, 2-5e-10], region)
    assert enclosure.segment_outside_exclusion([1, 2-2e-9], [4, 2-2e-9], region)
    assert enclosure.segment_outside_exclusion([-1, 1.5], [6, 1.5], region)


@pytest.mark.parametrize('start,end', [([math.nan, 0], [1, 1]),
                                     ([0, 0], [math.inf, 1]),
                                     ([0], [1, 1])])
def test_invalid_segments_are_not_positive_or_negative(start, end):
    region = _membership()
    assert not enclosure.segment_in_positive(start, end, region)
    assert not enclosure.segment_outside_exclusion(start, end, region)


def test_unqualified_geometry_cannot_supply_either_label():
    unknown = {'qualified': False}
    assert not enclosure.point_in_positive([0, 0], unknown)
    assert not enclosure.segment_in_positive([0, 0], [1, 0], unknown)
    assert not enclosure.segment_outside_exclusion([0, 0], [1, 0], unknown)


def test_finite_coordinates_that_overflow_grid_scaling_remain_unknown():
    region = _membership()
    region.spacing = 0.046875
    assert not enclosure.point_in_positive([1e308, 3], region)
    assert not enclosure.segment_in_positive([1e308, 3], [1e308, 3], region)
    assert not enclosure.segment_outside_exclusion([1e308, 3], [1e308, 3], region)
    assert not enclosure.segment_outside_exclusion([-1e308, 3], [1e308, 3], region)
