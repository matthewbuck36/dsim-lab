"""Frozen M2 stationary references, subordinate to the existing bag analyzer.

This is a continuous stationary GESC counterfactual, not a spatial gradient.
No model instances, bag reads, experiments or command-line entry point live here.
"""

import cmath
import bisect
import math
import statistics
import warnings

import numpy as np
from scipy.integrate import quad


VERSION = 'm2-reference-v1'
OBSERVED_PHASE_VERSION = 'observed-phase-periodic-v1'
KERNEL_ERROR_CEILING = 1e-10
ALPHA = 1.0
SENSOR_RADIUS_M = 0.18
MAXIMUM_OBJECTIVE_EVALUATIONS = 25000
COEFFICIENT_ERROR_CEILING = 1e-6
INVENTORY_SHA256 = 'eae9b60fc2f6f3e638f7ee9e56fd52174176fb4495de78bb145640eddb93e90d'
SELECTED_FILTER_SHA256 = 'f1cfd23a9c60e08780a4477f23cacc80a9e0c75b127448291e321756de7a2dce'
DEVELOPMENT_SEEDS = (19801, 19811, 19851, 19901, 19911, 19931, 20001, 20031)


def _finite(value):
    try:
        return not isinstance(value, bool) and math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _xy(value):
    result = np.asarray(value, dtype=float)
    if result.shape != (2,) or not np.isfinite(result).all():
        raise ValueError('finite planar point required')
    return result.copy()


def selected_sensor_xy(base_xy, theta, binding):
    """Require the selected geometry; use the authoritative transform matrix."""
    base = _xy(base_xy)
    if not _finite(theta):
        raise ValueError('nonfinite sensor phase')
    joint = np.asarray(binding.get('joint_position_m'), dtype=float)
    axis = np.asarray(binding.get('rotation_axis'), dtype=float)
    transform = np.asarray(binding.get('sensor_transform'), dtype=float)
    selected = np.eye(4)
    selected[:3, 3] = [SENSOR_RADIUS_M, 0.0, 0.015]
    if (joint.shape != (3,) or transform.shape != (4, 4)
            or not np.array_equal(joint, [0.0, 0.0, 0.355])
            or not np.array_equal(axis, [0.0, 0.0, 1.0])
            or not np.array_equal(transform, selected)):
        raise ValueError('reference requires verified selected sensor geometry')
    rotation = np.asarray([[math.cos(theta), -math.sin(theta)],
                           [math.sin(theta), math.cos(theta)]])
    return base + rotation @ transform[:2, 3]


def augmented_objective(raw_owner, *, base_xy, binding, weights,
                        gaussian_fills, affine_terms):
    """Freeze complete terms evaluated at the sensor, including affine anchors.

    The caller establishes causal completeness/identity; None is deliberately
    different from an explicitly known empty term list. Affine vectors already
    include decay/expiry at the frozen composition time, owned by the composer.
    """
    base = _xy(base_xy)
    selected_sensor_xy(base, 0.0, binding)
    if (len(weights) != 3 or not all(_finite(value) for value in weights)
            or gaussian_fills is None or affine_terms is None):
        raise ValueError('complete finite objective snapshot required')
    frozen_weights = tuple(float(value) for value in weights)
    gaussians = []
    for term in gaussian_fills:
        covariance = np.asarray(term['covariance'], dtype=float)
        amplitude = float(term['amplitude'])
        if (covariance.shape != (2, 2) or not np.isfinite(covariance).all()
                or not np.array_equal(covariance, covariance.T)
                or np.min(np.linalg.eigvalsh(covariance)) <= 0
                or not math.isfinite(amplitude)):
            raise ValueError('invalid active Gaussian term')
        gaussians.append((_xy(term['center']), np.linalg.inv(covariance), amplitude))
    affines = [(_xy(term['anchor']), _xy(term['vector'])) for term in affine_terms]

    def objective(theta):
        sensor = base + SENSOR_RADIUS_M*np.asarray([math.cos(theta), math.sin(theta)])
        raw = float(raw_owner(float(base[0]), float(base[1]), float(theta)))
        gaussian = sum(amplitude * math.exp(-0.5 * float(
            (sensor-center) @ inverse @ (sensor-center)))
            for center, inverse, amplitude in gaussians)
        affine = -sum(float(vector @ (sensor-anchor)) for anchor, vector in affines)
        value = sum(weight * component for weight, component in zip(
            frozen_weights, (raw, gaussian, affine)))
        if not math.isfinite(value):
            raise ValueError('nonfinite augmented objective')
        return value

    return objective


def _breakpoints(xy, sources, shift):
    base = _xy(xy)
    points = {math.radians(value) for value in range(shift, 360, 30)}
    for source in sources:
        location = _xy([source['x_m'], source['y_m']])
        delta = location - base
        if not np.isfinite(delta).all():
            raise ValueError('source bearing overflow')
        if np.any(delta):
            bearing = math.atan2(delta[1], delta[0])
            points.update((bearing % math.tau, (bearing+math.pi) % math.tau))
    return sorted(point for point in points if 0.0 < point < math.tau)


def integrate_stationary_harmonics(objective_at_angle, *, xy, sources):
    """Retain two independent normalized integrals for DC and first harmonics."""
    points = [_breakpoints(xy, sources, shift) for shift in (0, 15)]
    cache = {}

    def evaluate(angle):
        if angle not in cache:
            if len(cache) >= MAXIMUM_OBJECTIVE_EVALUATIONS:
                raise ValueError('objective_evaluation_budget')
            value = float(objective_at_angle(angle))
            if not math.isfinite(value):
                raise ValueError('nonfinite angular objective')
            cache[angle] = value
        return cache[angle]

    coefficients = {}
    for name, factor, normalization in (
            ('mean', lambda angle: 1.0, math.tau),
            ('cosine', math.cos, math.pi), ('sine', math.sin, math.pi)):
        passes = []
        for breakpoints in points:
            receipt = {'value': None, 'reported_error': None, 'evaluations': 0,
                       'breakpoints_rad': breakpoints, 'warnings': [], 'exception': None}
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                try:
                    result = quad(
                        lambda angle: evaluate(angle)*factor(angle), 0.0, math.tau,
                        points=breakpoints, full_output=True,
                        epsabs=normalization*1e-7, epsrel=1e-7, limit=128)
                    value, error = float(result[0]/normalization), float(result[1]/normalization)
                    if not math.isfinite(value) or not math.isfinite(error) or error < 0:
                        raise ValueError('invalid normalized quadrature')
                    receipt.update(value=value, reported_error=error,
                                   evaluations=int(result[2]['neval']))
                    receipt['warnings'].extend(str(item) for item in result[3:])
                except TimeoutError:
                    raise
                except Exception as exc:
                    receipt['exception'] = f'{type(exc).__name__}: {exc}'
                receipt['warnings'].extend(str(item.message) for item in caught)
            passes.append(receipt)
        valid = not any(item['exception'] or item['warnings'] for item in passes)
        value = error = None
        if valid:
            value = 0.5*passes[0]['value'] + 0.5*passes[1]['value']
            error = max(*(item['reported_error'] for item in passes),
                        abs(passes[0]['value']-passes[1]['value']))
            valid = math.isfinite(value) and math.isfinite(error)
        coefficients[name] = {
            'qualified': bool(valid and error <= COEFFICIENT_ERROR_CEILING),
            'value': value if valid else None, 'error': error if valid else None,
            'passes': passes}
    return {'version': VERSION, 'qualified': all(item['qualified'] for item in coefficients.values()),
            'coefficients': coefficients, 'objective_evaluations': len(cache)}


def continuous_transfer(omega_rad_sec):
    if not _finite(omega_rad_sec) or omega_rad_sec == 0:
        raise ValueError('finite nonzero signed angular rate required')
    argument = complex(0, float(omega_rad_sec))
    return argument / (ALPHA + argument)


def discrete_transfer(omega_rad_sec, step_sec):
    continuous_transfer(omega_rad_sec)
    if not _finite(step_sec) or not 0 < ALPHA*step_sec < 2:
        raise ValueError('uniform Euler step must satisfy 0 < alpha*h < 2')
    phase = float(omega_rad_sec)*float(step_sec)
    if not math.isfinite(phase):
        raise ValueError('nonfinite discrete phase')
    # exp(i*x)-1, written to avoid subtraction cancellation for small x.
    numerator = complex(-2*math.sin(phase/2)**2, math.sin(phase))
    return numerator / (numerator + ALPHA*step_sec)


def _reference_vector(a, b, transfer):
    return [-(transfer.real*a + transfer.imag*b)/SENSOR_RADIUS_M,
            -(transfer.real*b - transfer.imag*a)/SENSOR_RADIUS_M]


def stationary_reference(harmonics, *, omega_rad_sec, step_sec=None):
    """Primary continuous vector and optional uniform-Euler sensitivity."""
    if not harmonics.get('qualified'):
        return {'qualified': False, 'informative': False, 'reason': 'angular_integral_unqualified'}
    transfer = continuous_transfer(omega_rad_sec)
    cosine, sine = (harmonics['coefficients'][name] for name in ('cosine', 'sine'))
    values = [cosine['value'], sine['value'], cosine['error'], sine['error']]
    if (not all(_finite(value) for value in values)
            or min(cosine['error'], sine['error']) < 0
            or max(cosine['error'], sine['error']) > COEFFICIENT_ERROR_CEILING):
        raise ValueError('invalid harmonic coefficient receipt')
    vector = _reference_vector(cosine['value'], sine['value'], transfer)
    magnitude = math.hypot(*vector)
    error = abs(transfer)*math.hypot(cosine['error'], sine['error'])/SENSOR_RADIUS_M
    if not all(math.isfinite(value) for value in (*vector, magnitude, error)):
        return {'qualified': False, 'informative': False, 'reason': 'reference_overflow'}
    threshold = max(1e-6, 20*error)
    result = {'qualified': True, 'informative': magnitude > threshold,
              'reason': None if magnitude > threshold else 'uninformative_reference',
              'world_vector': vector, 'magnitude': magnitude,
              'estimated_vector_error': error, 'informative_threshold': threshold,
              'omega_rad_sec': float(omega_rad_sec),
              'nominal_joint_omega_rad_sec': math.tau/3,
              'continuous_transfer_real_imag': [transfer.real, transfer.imag],
              'discrete_sensitivity': None}
    if step_sec is not None:
        discrete = discrete_transfer(omega_rad_sec, step_sec)
        discrete_vector = _reference_vector(cosine['value'], sine['value'], discrete)
        result['discrete_sensitivity'] = {
            'step_sec': float(step_sec), 'world_vector': discrete_vector,
            'transfer_real_imag': [discrete.real, discrete.imag],
            'transfer_phase_difference_deg': math.degrees(cmath.phase(discrete/transfer)),
            'claim': 'uniform_sample_first_harmonic_sensitivity'}
    return result


def angular_error_deg(value, reference):
    """Return unavailable for nonfinite/weak signals; never normalize zero."""
    try:
        first, second = _xy(value), _xy(reference)
        lengths = [math.hypot(*first), math.hypot(*second)]
        if min(lengths) <= 1e-6 or not all(math.isfinite(x) for x in lengths):
            return None
        dot = float((first/lengths[0]) @ (second/lengths[1]))
        return math.degrees(math.acos(max(-1.0, min(1.0, dot))))
    except (ValueError, TypeError, OverflowError):
        return None


def select_reference_targets(origin_ns):
    if type(origin_ns) is not int:
        raise ValueError('absolute integer source origin required')
    return [origin_ns + k*10_000_000_000 for k in range(1, 25)]


def select_causal_anchor(observations, target_ns):
    """Selection uses represented model-input time, never later publication time."""
    if target_ns is None:
        return None
    return next((index for index, item in enumerate(observations)
                 if item['qualified'] and item.get('readiness_eligible')
                 and target_ns <= item['stamp_ns'] <= target_ns+50_000_000), None)


def qualify_cycle_rates(stamps_ns, unwrapped_world_phase, *, observed_stamps_ns=None):
    """Qualify one already extracted complete measured revolution."""
    if len(stamps_ns) != len(unwrapped_world_phase) or len(stamps_ns) < 3:
        return {'qualified': False, 'reason': 'incomplete_world_cycle'}
    if not all(type(stamp) is int for stamp in stamps_ns):
        return {'qualified': False, 'reason': 'invalid_source_stamp'}
    phases = np.asarray(unwrapped_world_phase, dtype=float)
    durations = np.asarray([(b-a)/1e9 for a, b in zip(stamps_ns, stamps_ns[1:])])
    increments = np.diff(phases)
    if (not np.isfinite(phases).all() or not np.isfinite(increments).all()
            or np.any(durations <= 0) or np.any(durations > 0.5)):
        return {'qualified': False, 'reason': 'invalid_cycle_samples'}
    progress = float(phases[-1]-phases[0])
    if not math.isclose(abs(progress), math.tau, abs_tol=1e-9, rel_tol=0):
        return {'qualified': False, 'reason': 'incomplete_world_cycle'}
    direction = math.copysign(1.0, progress)
    if np.any(direction*increments < -1e-12):
        return {'qualified': False, 'reason': 'world_phase_reversal'}
    duration = float(np.sum(durations))
    if duration > 30:
        return {'qualified': False, 'reason': 'cycle_duration_bound'}
    omega = progress/duration
    rates = increments/durations
    variability = math.sqrt(float(np.sum(durations*(rates-omega)**2))/duration)/abs(omega)
    # A clipped phase boundary is not a new observation for cadence assessment.
    cadence = durations if observed_stamps_ns is None else np.asarray([
        (b-a)/1e9 for a, b in zip(observed_stamps_ns, observed_stamps_ns[1:])])
    if not len(cadence) or not np.isfinite(cadence).all() or np.any(cadence <= 0):
        return {'qualified': False, 'reason': 'invalid_observed_cadence'}
    median_step = statistics.median(cadence)
    uniform = bool(np.all(np.abs(cadence-median_step) <= 0.01*median_step))
    return {'qualified': variability <= 0.10,
            'reason': None if variability <= 0.10 else 'variable_world_rate',
            'omega_rad_sec': omega, 'duration_sec': duration,
            'rate_coefficient_of_variation': variability,
            'uniform_step_sec': float(median_step) if uniform else None,
            'discrete_sensitivity_available': uniform and 0 < ALPHA*median_step < 2}


def _reference_cycle_extract(observations, end_index):
    """Extract the latest complete monotonic world revolution without extrapolation."""
    if not 0 <= end_index < len(observations):
        return {'qualified': False, 'reason': 'missing_anchor'}, None, None
    end = observations[end_index]
    reverse = [(end['stamp_ns'], float(end['world_phase_rad']), end)]
    direction = None
    reason = 'incomplete_world_cycle'
    for previous in reversed(observations[:end_index]):
        last_stamp, last_phase, last = reverse[-1]
        if (not previous['qualified'] or not last['qualified']
                or previous['context_id'] != end['context_id']
                or previous['objective_id'] != end['objective_id']):
            reason = 'cycle_context_discontinuity'
            break
        gap = last_stamp-previous['stamp_ns']
        if gap <= 0 or gap > 500_000_000 or end['stamp_ns']-previous['stamp_ns'] > 30_000_000_000:
            reason = 'cycle_source_gap_or_bound'
            break
        delta = math.remainder(last['world_phase_rad']-previous['world_phase_rad'], math.tau)
        if not math.isfinite(delta) or abs(delta) == math.pi:
            reason = 'ambiguous_world_phase'
            break
        if abs(delta) > 1e-12:
            if direction is None:
                direction = math.copysign(1, delta)
            if direction*delta < -1e-12:
                reason = 'world_phase_reversal'
                break
        phase = last_phase-delta
        reverse.append((previous['stamp_ns'], phase, previous))
        # Continue across equal phase at the boundary to retain FIRST arrival,
        # including dwell; strict overshoot supplies its preceding bracket.
        if direction is not None and direction*(reverse[0][1]-phase) > math.tau+1e-12:
            break
    if direction is None or direction*(reverse[0][1]-reverse[-1][1]) < math.tau-1e-12:
        return {'qualified': False, 'reason': reason}, None, None
    ordered = list(reversed(reverse))
    target_phase = reverse[0][1]-direction*math.tau
    at_boundary = abs(target_phase-ordered[0][1]) <= 1e-12
    fraction = 0.0 if at_boundary else (
        (target_phase-ordered[0][1])/(ordered[1][1]-ordered[0][1]))
    stamp = round((1-fraction)*ordered[0][0]+fraction*ordered[1][0])
    clipped = [(stamp, target_phase)] + [(item[0], item[1]) for item in ordered[1:]]
    if clipped[0][0] == clipped[1][0]:
        clipped = clipped[1:]
    rates = qualify_cycle_rates(
        [item[0] for item in clipped], [item[1] for item in clipped],
        observed_stamps_ns=[item[0] for item in ordered])
    counts = [0]*12
    for actual_stamp, _, actual in ordered:
        if stamp <= actual_stamp < end['stamp_ns']:
            sector = min(11, int((actual['world_phase_rad'] % math.tau)/(math.tau/12)))
            counts[sector] += 1
    coverage = all(count >= 2 for count in counts)
    if not coverage and rates['qualified']:
        rates.update(qualified=False, reason='insufficient_input_sector_coverage')
    start_xy = (1-fraction)*_xy(ordered[0][2]['xy']) + fraction*_xy(ordered[1][2]['xy'])
    rates.update(start_ns=stamp, end_ns=end['stamp_ns'],
                 actual_observation_count=sum(counts), sector_counts=counts,
                 input_coverage_valid=coverage,
                 translation_m=float(np.linalg.norm(_xy(end['xy'])-start_xy)))
    return rates, clipped, ordered


def reference_cycle(observations, end_index):
    """Preserve the original constant-rate cycle result and CV0.10 gate."""
    return _reference_cycle_extract(observations, end_index)[0]


def observed_phase_cycle(observations, end_index):
    """Retain the same source knots; model rate variation instead of averaging it.

    The old cycle applicability fields are preserved explicitly. Readiness is
    required for every original support observation, including a clipped
    boundary's preceding bracket. No output/confidence field selects support.
    """
    if type(end_index) is not int or not 0 <= end_index < len(observations):
        return {'version': OBSERVED_PHASE_VERSION, 'qualified': False,
                'reason': 'missing_anchor', 'waveform': None}
    try:
        rates, clipped, ordered = _reference_cycle_extract(observations, end_index)
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError):
        return {'version': OBSERVED_PHASE_VERSION, 'qualified': False,
                'reason': 'invalid_cycle_samples', 'waveform': None}
    result = dict(rates, version=OBSERVED_PHASE_VERSION,
                  constant_rate_qualified=rates['qualified'],
                  constant_rate_reason=rates.get('reason'), waveform=None)
    if clipped is None:
        return result
    result['waveform'] = {
        'stamps_ns': [item[0] for item in clipped],
        'unwrapped_world_phase_rad': [item[1] for item in clipped],
        'observed_stamps_ns': [item[0] for item in ordered],
        'observed_world_phase_rad': [float(item[2]['world_phase_rad']) for item in ordered]}
    if not all(item[2].get('readiness_eligible') is True for item in ordered):
        result.update(qualified=False, reason='cycle_readiness_discontinuity')
    elif not rates['input_coverage_valid']:
        result.update(qualified=False, reason='insufficient_input_sector_coverage')
    elif rates.get('reason') in (None, 'variable_world_rate'):
        result.update(qualified=True, reason=None)
    return result


def _observed_waveform(cycle):
    """Validate the extracted numerical receipt before querying an objective."""
    waveform = cycle.get('waveform')
    if cycle.get('version') != OBSERVED_PHASE_VERSION or not isinstance(waveform, dict):
        raise ValueError('observed-phase waveform receipt required')
    stamps = waveform.get('stamps_ns', [])
    phases = waveform.get('unwrapped_world_phase_rad', [])
    observed = waveform.get('observed_stamps_ns', [])
    actual_phases = waveform.get('observed_world_phase_rad', [])
    if (not isinstance(stamps, list) or not isinstance(phases, list)
            or not isinstance(observed, list) or not isinstance(actual_phases, list)
            or len(stamps) != len(phases) or len(observed) != len(actual_phases)
            or len(stamps) < 3 or len(observed) < 3
            or not all(type(stamp) is int and stamp >= 0 for stamp in stamps+observed)
            or not all(_finite(phase) for phase in phases+actual_phases)):
        raise ValueError('invalid observed-phase samples')
    rates = qualify_cycle_rates(stamps, phases, observed_stamps_ns=observed)
    if (rates.get('reason') not in (None, 'variable_world_rate')
            or any(not 0 < b-a <= 500_000_000 for a, b in zip(observed, observed[1:]))
            or any(abs(b-a) >= math.pi for a, b in zip(phases, phases[1:]))
            or observed[0] > stamps[0] or observed[-1] != stamps[-1]
            or stamps != [stamps[0]] + [stamp for stamp in observed if stamp > stamps[0]]
            or cycle.get('start_ns') != stamps[0] or cycle.get('end_ns') != stamps[-1]
            or cycle.get('input_coverage_valid') is not True
            or len(cycle.get('sector_counts', [])) != 12
            or not all(type(n) is int and n >= 2 for n in cycle['sector_counts'])):
        raise ValueError('inconsistent observed-phase support')
    counts = [0]*12
    for stamp, phase in zip(observed, actual_phases):
        if stamps[0] <= stamp < stamps[-1]:
            counts[min(11, int((phase % math.tau)/(math.tau/12)))] += 1
    if (counts != cycle['sector_counts']
            or type(cycle.get('actual_observation_count')) is not int
            or cycle['actual_observation_count'] != sum(counts)):
        raise ValueError('inconsistent actual source coverage')
    direction = math.copysign(1., phases[-1]-phases[0])
    for first, last in zip(actual_phases, actual_phases[1:]):
        delta = math.remainder(last-first, math.tau)
        if abs(delta) == math.pi or direction*delta < -1e-12:
            raise ValueError('inconsistent actual source phase')
    actual_by_stamp = dict(zip(observed, actual_phases))
    for stamp, phase in zip(stamps[1:], phases[1:]):
        if abs(math.remainder(phase-actual_by_stamp[stamp], math.tau)) > 1e-10:
            raise ValueError('waveform omitted actual phase')
    # A fractional source-time crossing is rounded only once to integer ns by
    # the original extractor. Allow precisely that half-ns phase uncertainty.
    index = min(len(observed)-2, max(0, bisect.bisect_right(observed, stamps[0])-1))
    delta = math.remainder(actual_phases[index+1]-actual_phases[index], math.tau)
    fraction = (stamps[0]-observed[index])/(observed[index+1]-observed[index])
    expected = actual_phases[index]+fraction*delta
    phase_tolerance = 1e-10 + .5000001*abs(delta)/(observed[index+1]-observed[index])
    if abs(math.remainder(phases[0]-expected, math.tau)) > phase_tolerance:
        raise ValueError('inconsistent clipped phase boundary')
    for key in ('omega_rad_sec', 'duration_sec', 'rate_coefficient_of_variation'):
        if (not _finite(cycle.get(key)) or not math.isclose(
                cycle[key], rates[key], rel_tol=1e-12, abs_tol=1e-12)):
            raise ValueError('inconsistent observed-phase rate receipt')
    times = [(stamp-stamps[0])/1e9 for stamp in stamps]
    # Preserve increments while reducing a possibly wrapped phase origin.
    initial = math.remainder(float(phases[0]), math.tau)
    phase = [initial + float(value-phases[0]) for value in phases]
    return times, phase


def _observed_adjoint(times, phases):
    """Exact backward periodic recurrence for the represented linear phase."""
    durations = [b-a for a, b in zip(times, times[1:])]
    omega = [(b-a)/h for a, b, h in zip(phases, phases[1:], durations)]
    denominator = -math.expm1(-ALPHA*times[-1])

    def segment_term(theta, rate, h):
        return cmath.exp(complex(0, theta)) * complex(
            -np.expm1(complex(-ALPHA, rate)*h)) / complex(ALPHA, -rate)

    factors = [math.exp(-ALPHA*h) for h in durations]
    terms = [segment_term(theta, rate, h)
             for theta, rate, h in zip(phases, omega, durations)]
    value = 0j
    for factor, term in reversed(list(zip(factors, terms))):
        value = factor*value+term
    terminal = value/denominator
    endpoints = [0j]*len(times)
    endpoints[-1] = terminal
    for index in range(len(durations)-1, -1, -1):
        endpoints[index] = factors[index]*endpoints[index+1]+terms[index]
    closure = abs(endpoints[0]-terminal)
    floating_kernel = 128*np.finfo(float).eps*len(times)/denominator
    if (not all(_finite(part) for value in endpoints for part in (value.real, value.imag))
            or not _finite(closure) or ALPHA*closure > KERNEL_ERROR_CEILING
            or any(abs(value) > 1/ALPHA+floating_kernel for value in endpoints)):
        raise ValueError('periodic_adjoint_closure')

    def evaluate(t):
        index = min(len(omega)-1, max(0, bisect.bisect_right(times, t)-1))
        theta = phases[index]+omega[index]*(t-times[index])
        remaining = max(0., times[index+1]-t)
        adjoint = (math.exp(-ALPHA*remaining)*endpoints[index+1]
                   + segment_term(theta, omega[index], remaining))
        return theta, cmath.exp(complex(0, theta))-ALPHA*adjoint

    return evaluate, {'periodic_closure_sec': closure,
                      'estimated_kernel_roundoff': float(floating_kernel),
                      'segment_count': len(durations),
                      'phase_interpolation': 'piecewise_linear_source_time',
                      'periodic_adjoint_initial_real_imag_sec':
                          [endpoints[0].real, endpoints[0].imag]}


def observed_phase_harmonic_map(*, cycle):
    """Exact represented-phase map from cos/sin harmonics 1..3 to world GESC.

    The map includes the negative demodulation gain and sensor radius. Raw
    objective weight and known augmented terms belong to the caller. Error
    estimates cover floating arithmetic, not fitted-profile or phase error.
    This opt-in calculation does not evaluate an objective or change references.
    """
    result = {'version': 'observed-phase-harmonic-map-v1', 'qualified': False,
              'reason': 'observed_cycle_unqualified', 'matrix': None,
              'estimated_matrix_error': None, 'audit': {}}
    if not isinstance(cycle, dict) or cycle.get('qualified') is not True:
        return result
    try:
        times, phases = _observed_waveform(cycle)
        kernel, audit = _observed_adjoint(times, phases)
        duration = times[-1]
        audit.update(basis_order=['cos1', 'sin1', 'cos2', 'sin2', 'cos3', 'sin3'],
                     integration='analytic_piecewise_linear_phase',
                     objective_evaluations=0,
                     error_claim='floating_point_estimates_not_model_certificate')
        result['audit'] = audit
        integrals, absolute_terms = {}, {}

        def exponential_integral(z, h):
            return complex(h) if z == 0 else complex(np.expm1(z*h))/z

        # K(t_j+u) = A_j exp(i*w_j*u) + B_j exp(alpha*u), where
        # K = exp(i*theta)-alpha*p is the existing periodic-adjoint kernel.
        segments = []
        for left, right, first, last in zip(times, times[1:], phases, phases[1:]):
            h = right-left
            omega = (last-first)/h
            a = complex(0., -omega)/complex(ALPHA, -omega)*cmath.exp(1j*first)
            b = kernel(left)[1]-a
            segments.append((h, omega, first, a, b))
        for harmonic in range(-3, 4):
            terms = []
            for h, omega, theta, a, b in segments:
                phase = cmath.exp(1j*harmonic*theta)
                terms.extend((phase*a*exponential_integral(1j*(harmonic+1)*omega, h),
                              phase*b*exponential_integral(complex(ALPHA, harmonic*omega), h)))
            if not all(_finite(v) for term in terms for v in (term.real, term.imag)):
                raise ValueError('nonfinite_harmonic_integral')
            integrals[harmonic] = complex(math.fsum(t.real for t in terms),
                                          math.fsum(t.imag for t in terms))
            absolute_terms[harmonic] = math.fsum(abs(t) for t in terms)
        eps = float(np.finfo(float).eps)
        normalized = 2./duration
        dc = normalized*integrals[0]
        dc_error = normalized*128*eps*absolute_terms[0]
        kernel_error = (audit['estimated_kernel_roundoff']
                        + 2*ALPHA*audit['periodic_closure_sec'])
        if not all(_finite(v) for v in (dc.real, dc.imag, dc_error, kernel_error)):
            raise ValueError('nonfinite_harmonic_kernel')
        audit.update(normalized_kernel_dc_real_imag=[dc.real, dc.imag],
                     estimated_normalized_kernel_dc_error=dc_error)
        if abs(dc)+dc_error > KERNEL_ERROR_CEILING:
            raise ValueError('periodic_kernel_dc_residual')
        columns, errors = [], []
        for harmonic in range(1, 4):
            cosine = (integrals[harmonic]+integrals[-harmonic])/2
            sine = (integrals[harmonic]-integrals[-harmonic])/(2j)
            absolute = (absolute_terms[harmonic]+absolute_terms[-harmonic])/2
            # Match the reference's DC removal without calling an objective.
            for value, offset in ((cosine, math.cos(harmonic*phases[0])),
                                  (sine, math.sin(harmonic*phases[0]))):
                coefficient = normalized*(value-offset*integrals[0])
                arithmetic = normalized*128*eps*(absolute+abs(offset)*absolute_terms[0])
                error = arithmetic+4*(kernel_error+abs(dc)+dc_error)+16*eps
                if (not all(_finite(v) for v in (coefficient.real, coefficient.imag, error))
                        or error < 0 or error > COEFFICIENT_ERROR_CEILING):
                    raise ValueError('harmonic_map_error_unqualified')
                columns.append([-coefficient.real/SENSOR_RADIUS_M,
                                -coefficient.imag/SENSOR_RADIUS_M])
                errors.append([error/SENSOR_RADIUS_M, error/SENSOR_RADIUS_M])
        matrix = np.asarray(columns, dtype=float).T
        matrix_error = np.asarray(errors, dtype=float).T
        if not np.isfinite(matrix).all() or not np.isfinite(matrix_error).all():
            raise ValueError('harmonic_map_overflow')
        result.update(qualified=True, reason=None, matrix=matrix.tolist(),
                      estimated_matrix_error=matrix_error.tolist())
    except (ValueError, TypeError, KeyError, IndexError, ArithmeticError) as exc:
        result.update(reason=str(exc))
    return result


def _observed_time_breakpoints(times, phases, angular_points):
    points = set(times[1:-1])
    for left, right, theta0, theta1 in zip(times, times[1:], phases, phases[1:]):
        if theta0 == theta1:
            continue
        low, high = sorted((theta0, theta1))
        for angle in [0.0, *angular_points]:
            first = math.floor((low-angle)/math.tau)+1
            last = math.ceil((high-angle)/math.tau)
            for turn in range(first, last):
                phase = angle+turn*math.tau
                t = left+(phase-theta0)/(theta1-theta0)*(right-left)
                if left < t < right:
                    points.add(t)
    return sorted(points)


def _observed_quadrature(function, duration, points, *, tolerance):
    receipt = {'value': None, 'reported_error': None, 'evaluations': 0,
               'breakpoints_sec': points, 'warnings': [], 'exception': None}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            result = quad(function, 0., duration, points=points, full_output=True,
                          epsabs=duration*tolerance/2, epsrel=tolerance,
                          limit=max(128, len(points)+128))
            value, error = 2*float(result[0])/duration, 2*float(result[1])/duration
            if not _finite(value) or not _finite(error) or error < 0:
                raise ValueError('invalid normalized time quadrature')
            receipt.update(value=value, reported_error=error,
                           evaluations=int(result[2]['neval']))
            receipt['warnings'].extend(str(item) for item in result[3:])
        except TimeoutError:
            raise
        except Exception as exc:
            receipt['exception'] = f'{type(exc).__name__}: {exc}'
        receipt['warnings'].extend(str(item.message) for item in caught)
    return receipt


def observed_phase_reference(objective_at_angle, *, cycle, xy, sources):
    """Periodic stationary-position GESC response under the observed phase.

    Numerical error estimates do not certify phase interpolation or model error.
    This function changes neither the old constant-rate reference nor runtime.
    """
    result = {'version': OBSERVED_PHASE_VERSION, 'qualified': False,
              'informative': False, 'reason': 'observed_cycle_unqualified',
              'world_vector': None, 'magnitude': None, 'estimated_vector_error': None,
              'informative_threshold': None, 'discrete_sensitivity': None, 'audit': {}}
    if cycle.get('qualified') is not True:
        return result
    times, phases = _observed_waveform(cycle)
    angular = [_breakpoints(xy, sources, shift) for shift in (0, 15)]
    partitions = [_observed_time_breakpoints(times, phases, points) for points in angular]
    kernel, audit = _observed_adjoint(times, phases)
    result.update(omega_rad_sec=cycle['omega_rad_sec'], audit=audit)
    audit.update(angular_breakpoints_rad=angular, waveform=cycle['waveform'],
                 objective_evaluations=0, coefficients={})
    dc = [[_observed_quadrature(
        lambda t, k=k: (kernel(t)[1].real if k == 0 else kernel(t)[1].imag),
        times[-1], points, tolerance=1e-11) for points in partitions] for k in (0, 1)]
    audit['normalized_kernel_dc_passes'] = dc
    if any(item['exception'] or item['warnings'] for pair in dc for item in pair):
        result['reason'] = 'periodic_kernel_unqualified'
        return result
    dc_error = [max(*(item['reported_error'] for item in pair),
                    abs(pair[0]['value']-pair[1]['value'])) for pair in dc]
    dc_value = [sum(item['value']/2 for item in pair) for pair in dc]
    audit.update(normalized_kernel_dc_real_imag=dc_value,
                 normalized_kernel_dc_error=dc_error)
    if any(abs(value)+error > KERNEL_ERROR_CEILING
           for value, error in zip(dc_value, dc_error)):
        result['reason'] = 'periodic_kernel_dc_residual'
        return result
    cache, attempted, fault = {}, set(), []

    def evaluate(theta):
        angle = theta % math.tau
        if fault:
            raise ValueError(fault[0])
        if angle not in cache:
            if len(attempted) >= MAXIMUM_OBJECTIVE_EVALUATIONS:
                raise ValueError('objective_evaluation_budget')
            attempted.add(angle)
            try:
                value = float(objective_at_angle(angle))
                if not math.isfinite(value):
                    raise ValueError('nonfinite angular objective')
            except TimeoutError:
                raise
            except Exception as exc:
                fault.append(f'{type(exc).__name__}: {exc}')
                raise
            cache[angle] = value
        return cache[angle]

    # Offset removal is exact for the periodic washout. Keep the actual value
    # and subtraction roundoff in the receipt, including absolute DC scale.
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            offset = evaluate(phases[0])
        if caught:
            raise ValueError('; '.join(str(item.message) for item in caught))
    except TimeoutError:
        raise
    except Exception as exc:
        audit.update(objective_evaluations=len(attempted), exception=f'{type(exc).__name__}: {exc}')
        result['reason'] = 'observed_integral_unqualified'
        return result
    for name, component in (('x', 0), ('y', 1)):
        def integrand(t):
            theta, weight = kernel(t)
            centered = evaluate(theta)-offset
            if not math.isfinite(centered):
                raise ValueError('objective_centering_overflow')
            return centered*(weight.real if component == 0 else weight.imag)
        passes = [_observed_quadrature(integrand, times[-1], points, tolerance=1e-7)
                  for points in partitions]
        valid = not any(item['exception'] or item['warnings'] for item in passes)
        value = sum(item['value']/2 for item in passes) if valid else None
        error = max(*(item['reported_error'] for item in passes),
                    abs(passes[0]['value']-passes[1]['value'])) if valid else None
        audit['coefficients'][name] = {'value': value, 'quadrature_error': error,
                                       'passes': passes}
    scale = max(abs(value) for value in cache.values())
    centered = max(abs(value-offset) for value in cache.values())
    kernel_error = (audit['estimated_kernel_roundoff']+2*ALPHA*audit['periodic_closure_sec']
                    + math.hypot(*dc_value)+math.hypot(*dc_error))
    floating = float(centered*(2*kernel_error)+(16*np.finfo(float).eps)*scale)
    audit.update(objective_evaluations=len(attempted), objective_offset=offset,
                 maximum_sampled_objective_magnitude=scale,
                 maximum_sampled_centered_magnitude=centered if _finite(centered) else None,
                 estimated_component_roundoff=float(floating) if _finite(floating) else None,
                 error_claim='quadrature_and_floating_point_estimates_not_model_certificate')
    if not _finite(centered) or not _finite(floating):
        result['reason'] = 'observed_integral_overflow'
        return result
    for item in audit['coefficients'].values():
        item['error'] = item['quadrature_error']+floating if item['value'] is not None else None
        item['qualified'] = (item['error'] is not None and _finite(item['error'])
                             and item['error'] <= COEFFICIENT_ERROR_CEILING)
    if not all(item['qualified'] for item in audit['coefficients'].values()):
        result['reason'] = 'observed_integral_unqualified'
        return result
    values = [audit['coefficients'][axis]['value'] for axis in ('x', 'y')]
    errors = [audit['coefficients'][axis]['error'] for axis in ('x', 'y')]
    vector = [-value/SENSOR_RADIUS_M for value in values]
    magnitude, error = math.hypot(*vector), math.hypot(*errors)/SENSOR_RADIUS_M
    threshold = max(1e-6, 20*error)
    if not all(_finite(value) for value in (*vector, magnitude, error, threshold)):
        result['reason'] = 'reference_overflow'
        return result
    result.update(qualified=True, informative=magnitude > threshold,
                  reason=None if magnitude > threshold else 'uninformative_reference',
                  world_vector=vector, magnitude=magnitude, estimated_vector_error=error,
                  informative_threshold=threshold)
    return result


def replay_custom_filter(observations, config, *, phase_field, time_field):
    """Use the actual selected custom-filter owner on explicit matched inputs.

    Each observation has source stamp, cost, yaw, and named phase/time fields.
    This is not a reconstruction of unrecorded DDS callback order. Both arms
    start at the same first provided observation with zero first update dt.
    """
    from ros_esc.config_parsing import parse_filter_config

    custom_filter, state = parse_filter_config(config, [])
    state = np.asarray(state, dtype=float)
    previous = None
    output = []
    for observation in observations:
        stamp = observation[time_field]
        if type(stamp) is not int or (previous is not None and stamp <= previous):
            raise ValueError('replay filter requires strictly increasing integer source times')
        cost, phase, yaw = (float(observation[name])
                            for name in ('cost', phase_field, 'yaw_rad'))
        if not all(math.isfinite(value) for value in (cost, phase, yaw)):
            raise ValueError('replay filter requires finite input')
        step = 0.0 if previous is None else (stamp-previous)/1e9
        if step > 0.5:
            raise ValueError('replay source gap requires explicit new context')
        value = np.asarray([cost, phase])
        before = np.array(state, copy=True)
        body = np.asarray(custom_filter.filter_output(state, value, stamp/1e9), dtype=float)
        derivative = custom_filter.differential_equation(stamp/1e9, state, value)
        state = state + step*np.asarray(derivative)
        if body.shape != (2,) or not np.isfinite(body).all() or not np.isfinite(state).all():
            raise ValueError('replay filter nonfinite or incompatible output')
        cosine, sine = math.cos(yaw), math.sin(yaw)
        world = [cosine*body[0]-sine*body[1], sine*body[0]+cosine*body[1]]
        output.append({'stamp_ns': stamp, 'body_vector': body.tolist(),
                       'world_vector': world, 'state_before': before.tolist(),
                       'state_after': state.tolist(), 'step_sec': step})
        previous = stamp
    return output


def replay_matched_direction(observations, config):
    """Run both actual filter instances and the runtime rolling helper on one trace.

    Invalid inputs explicitly end a matched segment. First update dt is zero
    for both arms; this does not claim reconstruction of the legacy startup.
    Algorithm state controls application of the blend, not evidence production.
    """
    from ros_esc.filter_node.rolling_gesc import (
        DemodulatedSample, ObjectiveIdentity, RollingGesc,
        StreamIdentity, SynchronizedObservation,
    )
    results = [None]*len(observations)
    segments = []
    segment = []
    for index, observation in enumerate(observations):
        if (not observation['qualified'] or segment
                and (observation['context_id'] != segment[-1][1]['context_id']
                     or observation['frame_id'] != segment[-1][1]['frame_id'])):
            if segment:
                segments.append(segment)
            segment = []
        if observation['qualified']:
            segment.append((index, observation))
    if segment:
        segments.append(segment)
    for segment_number, items in enumerate(segments):
        values = [item[1] for item in items]
        old = replay_custom_filter(values, config, phase_field='latest_phase_rad', time_field='cost_stamp_ns')
        new = replay_custom_filter(values, config, phase_field='projected_phase_rad', time_field='stamp_ns')
        rolling = RollingGesc()
        identity = StreamIdentity('matched_replay', f'retained_proxy_{segment_number}',
                                  values[0]['frame_id'], 0, 0)
        revision = 0
        previous_objective = None
        for (index, value), old_value, new_value in zip(items, old, new):
            if value['objective_id'] != previous_objective:
                revision += 1
                previous_objective = value['objective_id']
            weights = value['objective']['weights']
            objective = ObjectiveIdentity(revision, *weights, value['objective_id'], revision)
            stamp = value['stamp_ns']
            # Receipts are synthetic source-aligned here; this is mathematical
            # matched replay, and never transport-timing qualification.
            observation = SynchronizedObservation(
                observation_id=index+1, identity=identity, objective=objective,
                source_sequence=index+1, source_stamp_ns=stamp,
                cost_source_stamp_ns=value['cost_stamp_ns'],
                legacy_cost_source_timestamp_sec=float(value.get('legacy_source_key', stamp/1e9)),
                pose_left_stamp_ns=value['pose_bracket_ns'][0], pose_right_stamp_ns=value['pose_bracket_ns'][1],
                encoder_left_stamp_ns=value['encoder_bracket_ns'][0], encoder_right_stamp_ns=value['encoder_bracket_ns'][1],
                receipt_stamp_ns=stamp, base_xy=tuple(value['xy']), base_yaw=value['yaw_rad'],
                encoder_phase=value['encoder_phase_rad'], sensor_world_phase=value['world_phase_rad'],
                sensor_xy=tuple(np.asarray(value['xy'])+SENSOR_RADIUS_M*np.asarray([
                    math.cos(value['world_phase_rad']), math.sin(value['world_phase_rad'])])),
                demodulation_phase_rad=value['projected_phase_rad'], raw_cost=value['raw_cost'],
                augmented_cost=value['cost'], sync_error_ns=0)
            rolling.update(DemodulatedSample(observation, tuple(new_value['body_vector'])))
            evaluation = rolling.evaluate(stamp, value['yaw_rad'], stamp)
            blended = evaluation.output_valid and evaluation.qualified and value.get('blend_allowed', False)
            world = new_value['world_vector'] if evaluation.output_valid else None
            if blended:
                body = evaluation.final_body
                cosine, sine = math.cos(value['yaw_rad']), math.sin(value['yaw_rad'])
                world = [cosine*body[0]-sine*body[1], sine*body[0]+cosine*body[1]]
            results[index] = {
                'legacy_world_vector': old_value['world_vector'],
                'synchronized_instant_world_vector': new_value['world_vector'],
                'rolling_world_vector': list(evaluation.mean_world) if evaluation.mean_world is not None else None,
                'v2_world_vector': list(world) if world is not None else None,
                'output_valid': evaluation.output_valid, 'averaging_qualified': evaluation.qualified,
                'blend_applied': bool(blended), 'fallback_reason': evaluation.fallback_reason,
                'reference_input_quality': value.get('timing_quality', 'synthetic_matched_inputs'),
                'exact_transport_reconstruction': False}
    return results
