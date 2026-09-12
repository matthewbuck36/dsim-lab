"""Observed-phase numerical checks use analytical objectives, never run bags."""

from copy import deepcopy
import json
import math
import warnings

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from ros_esc.plotting_scripts import v2_direction_reference as reference


def _observations(times=None, phases=None, *, yaw=0., sign=1):
    if times is None:
        times = np.linspace(0., 3., 121)
    if phases is None:
        phases = np.asarray(times)*math.tau/3
    return [{'qualified': True, 'readiness_eligible': True,
             'stamp_ns': round(float(t)*1e9),
             'world_phase_rad': yaw+sign*float(phase), 'xy': [0., 0.],
             'context_id': 'one', 'objective_id': 'objective'}
            for t, phase in zip(times, phases)]


def _cycle(observations=None):
    values = _observations() if observations is None else observations
    return reference.observed_phase_cycle(values, len(values)-1)


def _variable(*, dwell=False, sign=1, yaw=0.):
    times = np.linspace(0., 3., 121)
    nodes = [0., .3, 1.4, 2.1, 3.]
    phases = np.interp(times, nodes, [0., 0. if dwell else .25, 2.5, 4.9, math.tau])
    return _observations(times, phases, sign=sign, yaw=yaw)


def _evaluate(function, cycle=None, **kwargs):
    return reference.observed_phase_reference(
        function, cycle=_cycle() if cycle is None else cycle,
        xy=kwargs.get('xy', [0., 0.]), sources=kwargs.get('sources', []))


def _direct_periodic_ode(function, cycle):
    """Independent forward washout solve; no adjoint or owner quadrature calls."""
    stamps = cycle['waveform']['stamps_ns']
    times = [(stamp-stamps[0])/1e9 for stamp in stamps]
    phases = cycle['waveform']['unwrapped_world_phase_rad']

    def advance(initial, with_mean):
        state = np.asarray(initial, dtype=float)
        for left, right, first, last in zip(times, times[1:], phases, phases[1:]):
            def rhs(t, value):
                theta = first+(last-first)*(t-left)/(right-left)
                cost = function(theta)
                washout = cost-value[0]
                if not with_mean:
                    return [reference.ALPHA*washout]
                return [reference.ALPHA*washout,
                        washout*math.cos(theta), washout*math.sin(theta)]
            solved = solve_ivp(rhs, (left, right), state, method='DOP853',
                               rtol=2e-12, atol=2e-13, max_step=(right-left)/3)
            assert solved.success
            state = solved.y[:, -1]
        return state

    final_zero = advance([0.], False)[0]
    initial = final_zero/(-math.expm1(-reference.ALPHA*times[-1]))
    result = advance([initial, 0., 0.], True)
    assert result[0] == pytest.approx(initial, abs=1e-10)
    return -2*result[1:]/(reference.SENSOR_RADIUS_M*times[-1])


@pytest.mark.parametrize('sign', [-1, 1])
@pytest.mark.parametrize('a,b', [(1., 0.), (0., 1.), (-2., .25)])
def test_signed_uniform_first_harmonics_match_unchanged_owner(sign, a, b):
    cycle = _cycle(_observations(yaw=.37, sign=sign))
    objective = lambda theta: 4+a*math.cos(theta)+b*math.sin(theta)
    harmonics = reference.integrate_stationary_harmonics(objective, xy=[0, 0], sources=[])
    old = reference.stationary_reference(harmonics, omega_rad_sec=cycle['omega_rad_sec'])
    actual = _evaluate(objective, cycle)
    assert actual['qualified'] and actual['informative']
    assert actual['world_vector'] == pytest.approx(old['world_vector'], abs=2e-10)
    assert actual['estimated_vector_error'] < 1e-7
    assert actual['discrete_sensitivity'] is None


@pytest.mark.parametrize('function', [lambda theta: 4.,
                                    lambda theta: math.cos(2*theta),
                                    lambda theta: 1+math.sin(7*theta)])
def test_uniform_dc_and_higher_harmonics_do_not_manufacture_direction(function):
    result = _evaluate(function)
    assert result['qualified'] and not result['informative']
    assert result['magnitude'] < 2e-10


@pytest.mark.parametrize('sign,dwell', [(1, False), (-1, False), (1, True), (-1, True)])
def test_nonuniform_phase_matches_independent_forward_periodic_washout(sign, dwell):
    cycle = _cycle(_variable(sign=sign, dwell=dwell, yaw=.2))
    assert cycle['qualified'] and not cycle['constant_rate_qualified']
    objective = lambda theta: 2+.7*math.cos(theta)-.4*math.sin(theta)+.3*math.cos(4*theta)
    result = _evaluate(objective, cycle)
    expected = _direct_periodic_ode(objective, cycle)
    assert result['qualified'] and result['informative']
    assert result['world_vector'] == pytest.approx(expected, abs=3e-9)
    assert result['audit']['periodic_closure_sec'] < 1e-12
    assert max(map(abs, result['audit']['normalized_kernel_dc_real_imag'])) < 1e-12


def test_variable_phase_dc_and_offset_invariance():
    cycle = _cycle(_variable(dwell=True))
    constant = _evaluate(lambda theta: 8., cycle)
    assert constant['qualified'] and not constant['informative']
    assert constant['magnitude'] == 0.
    first = _evaluate(math.cos, cycle)
    shifted = _evaluate(lambda theta: 1000+math.cos(theta), cycle)
    assert shifted['qualified'] and shifted['informative']
    assert shifted['world_vector'] == pytest.approx(first['world_vector'], abs=2e-10)
    assert shifted['audit']['maximum_sampled_objective_magnitude'] > 1000


def test_variable_rate_higher_harmonics_are_retained_in_periodic_response():
    cycle = _cycle(_variable())
    objective = lambda theta: math.cos(2*theta)
    result = _evaluate(objective, cycle)
    assert result['qualified'] and result['magnitude'] > .01
    assert result['world_vector'] == pytest.approx(_direct_periodic_ode(objective, cycle), abs=3e-9)


def test_world_coordinate_rotation_is_covariant():
    yaw = 1.31
    first = _evaluate(math.cos, _cycle(_variable()))
    rotated = _evaluate(lambda theta: math.cos(theta-yaw), _cycle(_variable(yaw=yaw)))
    x, y = first['world_vector']
    assert rotated['qualified']
    assert rotated['world_vector'] == pytest.approx(
        [math.cos(yaw)*x-math.sin(yaw)*y, math.sin(yaw)*x+math.cos(yaw)*y], abs=2e-10)


def test_cyclic_time_origin_keeps_same_periodic_response():
    observations = _variable(dwell=True)
    phases = np.asarray([row['world_phase_rad'] for row in observations])
    shift = 40
    rotated = np.r_[phases[shift:], phases[1:shift+1]+math.tau]
    first = _evaluate(math.cos, _cycle(observations))
    second = _evaluate(math.cos, _cycle(_observations(phases=rotated)))
    assert second['qualified']
    assert second['world_vector'] == pytest.approx(first['world_vector'], abs=2e-10)


def test_uniform_discrete_sensitivity_tends_to_observed_continuous_limit():
    cycle = _cycle()
    target = _evaluate(math.cos, cycle)['world_vector']
    errors = [np.linalg.norm(np.asarray(reference._reference_vector(
        1., 0., reference.discrete_transfer(cycle['omega_rad_sec'], step)))-target)
              for step in (.02, .002, .0002)]
    assert errors[0] > errors[1] > errors[2]
    assert errors[-1] < .001


def test_all_knots_and_source_bearings_are_in_both_time_partitions():
    cycle = _cycle(_variable(yaw=.1))
    result = _evaluate(math.cos, cycle, sources=[{'x_m': 1, 'y_m': 2}])
    assert result['qualified']
    stamps = cycle['waveform']['stamps_ns']
    knots = {(stamp-stamps[0])/1e9 for stamp in stamps[1:-1]}
    for coefficient in result['audit']['coefficients'].values():
        first, second = coefficient['passes']
        assert first['breakpoints_sec'] != second['breakpoints_sec']
        for item in (first, second):
            assert knots <= set(item['breakpoints_sec'])
    for points in result['audit']['angular_breakpoints_rad']:
        assert math.atan2(2, 1) in points
        assert math.atan2(2, 1)+math.pi in points


def test_narrow_analytic_peak_is_integrated_between_source_knots():
    radius, bearing = .97, math.radians(3.7)
    objective = lambda theta: (1-radius**2)/(1-2*radius*math.cos(theta-bearing)+radius**2)
    result = _evaluate(objective)
    expected = reference._reference_vector(2*radius*math.cos(bearing),
                                           2*radius*math.sin(bearing),
                                           reference.continuous_transfer(math.tau/3))
    assert result['qualified'] and result['world_vector'] == pytest.approx(expected, abs=2e-7)
    assert result['audit']['objective_evaluations'] < 25000


def test_tiny_source_segment_retains_stable_periodic_boundary():
    times = np.sort(np.r_[np.linspace(0., 3., 121), 1e-9])
    result = _evaluate(math.cos, _cycle(_observations(times=times)))
    assert result['qualified']
    expected = reference._reference_vector(1., 0., reference.continuous_transfer(math.tau/3))
    assert result['world_vector'] == pytest.approx(expected, abs=2e-10)


def test_cycle_addition_preserves_original_fields_and_rate_rejection():
    for observations in (_observations(), _variable(), _variable(dwell=True)):
        old = reference.reference_cycle(observations, len(observations)-1)
        new = _cycle(observations)
        assert {key: new[key] for key in old if key not in ('qualified', 'reason')} == {
            key: value for key, value in old.items() if key not in ('qualified', 'reason')}
        assert new['constant_rate_qualified'] == old['qualified']
        assert new['constant_rate_reason'] == old.get('reason')
        assert new['qualified']


@pytest.mark.parametrize('fault', ['readiness', 'qualification', 'context', 'objective',
                                  'gap', 'rollback', 'reversal', 'nonfinite', 'sparse'])
def test_input_faults_do_not_become_rate_modeling_exceptions(fault):
    values = _observations()
    if fault == 'readiness':
        values[50]['readiness_eligible'] = False
    elif fault == 'qualification':
        values[50]['qualified'] = False
    elif fault == 'context':
        values[50]['context_id'] = 'other'
    elif fault == 'objective':
        values[50]['objective_id'] = 'other'
    elif fault == 'gap':
        values = values[:30]+values[70:]
    elif fault == 'rollback':
        values[50]['stamp_ns'] = values[49]['stamp_ns']
    elif fault == 'reversal':
        values[50]['world_phase_rad'] = values[49]['world_phase_rad']-.01
    elif fault == 'nonfinite':
        values[50]['world_phase_rad'] = math.nan
    else:
        values = values[::10]
    cycle = _cycle(values)
    assert not cycle['qualified']
    def forbidden(theta):
        pytest.fail('unqualified support reached the objective')
    assert not _evaluate(forbidden, cycle)['qualified']


@pytest.mark.parametrize('fault', ['missing', 'source_type', 'source_negative', 'omitted_knot',
                                  'phase_nan', 'phase_jump', 'summary', 'coverage',
                                  'count', 'advertised_sector', 'actual_phase', 'boundary_phase'])
def test_malformed_waveform_receipt_rejected_before_objective(fault):
    cycle = deepcopy(_cycle())
    waveform = cycle['waveform']
    if fault == 'missing':
        del cycle['waveform']
    elif fault == 'source_type':
        waveform['stamps_ns'][2] = float(waveform['stamps_ns'][2])
    elif fault == 'source_negative':
        waveform['stamps_ns'][0] = -1
    elif fault == 'omitted_knot':
        del waveform['stamps_ns'][2]
        del waveform['unwrapped_world_phase_rad'][2]
    elif fault == 'phase_nan':
        waveform['unwrapped_world_phase_rad'][2] = math.nan
    elif fault == 'phase_jump':
        waveform['unwrapped_world_phase_rad'][2] += math.pi
    elif fault == 'summary':
        cycle['duration_sec'] += .01
    elif fault == 'coverage':
        cycle['sector_counts'][2] = 0
    elif fault == 'count':
        cycle['actual_observation_count'] += 1
    elif fault == 'advertised_sector':
        cycle['sector_counts'][2] += 1
    elif fault == 'actual_phase':
        waveform['observed_world_phase_rad'][2] += .001
    else:
        waveform['unwrapped_world_phase_rad'][0] += .001
    def forbidden(theta):
        pytest.fail('invalid receipt reached the objective')
    with pytest.raises(ValueError):
        _evaluate(forbidden, cycle)


@pytest.mark.parametrize('fault', ['warning', 'message', 'nonfinite', 'error', 'disagree'])
def test_quadrature_faults_never_publish_a_qualified_reference(monkeypatch, fault):
    owner = reference.quad
    calls = []
    def injected(*args, **kwargs):
        value = owner(*args, **kwargs)
        calls.append(1)
        if len(calls) <= 4:  # Preserve independently checked kernel DC passes.
            return value
        if fault == 'warning':
            warnings.warn('injected quadrature warning')
        if fault == 'message':
            return value+('failed integration',)
        if fault == 'nonfinite':
            return (math.nan, value[1], value[2])
        if fault == 'error':
            return (value[0], .001, value[2])
        if fault == 'disagree' and len(calls) % 2:
            return (value[0]+.001, value[1], value[2])
        return value
    monkeypatch.setattr(reference, 'quad', injected)
    result = _evaluate(math.cos)
    assert not result['qualified'] and not result['informative']
    assert result['reason'] == 'observed_integral_unqualified'


def test_objective_budget_nonfinite_and_timeout_have_distinct_outcomes(monkeypatch):
    monkeypatch.setattr(reference, 'MAXIMUM_OBJECTIVE_EVALUATIONS', 2)
    result = _evaluate(math.cos)
    assert not result['qualified'] and result['audit']['objective_evaluations'] == 2
    assert any('objective_evaluation_budget' in (item['exception'] or '')
               for value in result['audit']['coefficients'].values() for item in value['passes'])
    monkeypatch.setattr(reference, 'MAXIMUM_OBJECTIVE_EVALUATIONS', 25000)
    result = _evaluate(lambda theta: math.inf)
    assert not result['qualified'] and result['audit']['objective_evaluations'] == 1
    def expired(theta):
        raise TimeoutError('bounded parent job expired')
    with pytest.raises(TimeoutError):
        _evaluate(expired)


def test_objective_warning_at_offset_is_retained_and_rejected():
    def warning(theta):
        warnings.warn('objective unavailable')
        return 0.
    result = _evaluate(warning)
    assert not result['qualified'] and 'objective unavailable' in result['audit']['exception']


@pytest.mark.parametrize('fault', ['warning', 'closure', 'residual'])
def test_periodic_kernel_faults_reject_before_any_objective(monkeypatch, fault):
    if fault == 'closure':
        def rejected(*args):
            raise ValueError('periodic_adjoint_closure')
        monkeypatch.setattr(reference, '_observed_adjoint', rejected)
    else:
        quad = reference.quad
        def injected(*args, **kwargs):
            result = quad(*args, **kwargs)
            if fault == 'warning':
                warnings.warn('kernel integration warning')
            else:
                result = (result[0]+.001, result[1], result[2])
            return result
        monkeypatch.setattr(reference, 'quad', injected)
    def forbidden(theta):
        pytest.fail('invalid kernel reached objective')
    if fault == 'closure':
        with pytest.raises(ValueError, match='periodic_adjoint_closure'):
            _evaluate(forbidden)
    else:
        assert not _evaluate(forbidden)['qualified']


def test_weak_reference_and_component_error_use_existing_units_and_floor():
    result = _evaluate(lambda theta: 1e-9*math.cos(theta), _cycle(_variable()))
    assert result['qualified'] and not result['informative']
    assert result['reason'] == 'uninformative_reference'
    errors = [result['audit']['coefficients'][axis]['error'] for axis in ('x', 'y')]
    assert result['estimated_vector_error'] == pytest.approx(math.hypot(*errors)/.18)
    assert result['informative_threshold'] == max(1e-6, 20*result['estimated_vector_error'])


def test_finite_extreme_objective_overflow_retains_json_safe_failed_receipt():
    result = _evaluate(lambda theta: 1e308 if math.cos(theta) >= 0 else -1e308)
    assert not result['qualified']
    assert result['reason'] == 'observed_integral_overflow'
    assert result['audit']['maximum_sampled_centered_magnitude'] is None
    json.dumps(result, allow_nan=False)


def test_clipped_source_boundary_preserves_original_knots_and_support_receipt():
    times = np.linspace(0., 3.2, 129)
    values = _observations(times=times, phases=times*2.13+.17)
    cycle = _cycle(values)
    assert cycle['qualified']
    assert cycle['waveform']['observed_stamps_ns'][0] < cycle['start_ns']
    result = _evaluate(math.cos, cycle)
    assert result['qualified']
    expected = reference._reference_vector(1., 0., reference.continuous_transfer(2.13))
    assert result['world_vector'] == pytest.approx(expected, abs=2e-9)
    json.dumps(result, allow_nan=False)
