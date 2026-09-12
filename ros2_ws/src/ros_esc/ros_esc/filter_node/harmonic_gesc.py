"""Unwired R14 raw-signal estimator; no field truth, ROS or control decisions.

The caller supplies causal source samples and owns context/epoch admission.
Prediction gains and HC3 uncertainty are diagnostics, not universal confidence.
"""
import math

import numpy as np


HARMONICS = 3
INFORMATION_FRACTION_MIN = 0.10
SVD_RELATIVE_TOLERANCE = 1e-10


def angular_profile(coefficients, phase):
    """Angular response at the supplied fit center, without its washout-null DC."""
    return float(sum(coefficients[2*(k-1)]*math.cos(k*phase)
                     + coefficients[2*(k-1)+1]*math.sin(k*phase)
                     for k in range(1, HARMONICS+1)))


def _basis(samples, center_xy, center_time):
    phase = samples[:, 3]
    dx, dy = ((samples[:, 1:3]-center_xy)/0.15).T
    z = np.column_stack((np.ones(len(samples)),
                         (samples[:, 0]-center_time)/3., dx, dy))
    h = np.column_stack([f(k*phase) for k in range(1, HARMONICS+1)
                         for f in (np.cos, np.sin)])
    p = np.column_stack((dx*h[:, 0], dx*h[:, 1],
                         dy*h[:, 0], dy*h[:, 1]))
    return z, h, p


def _subspace(matrix):
    u, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    rank = int(np.sum(singular > singular[0]*SVD_RELATIVE_TOLERANCE))
    return u[:, :rank], rank


def _linear_fit(z, h, p, y):
    nuisance = np.column_stack((z, p))
    basis, nuisance_rank = _subspace(nuisance)
    residual_h = h-basis@(basis.T@h)
    u, singular, vh = np.linalg.svd(residual_h, full_matrices=False)
    if len(singular) != 6 or singular[-1] <= max(1., singular[0])*SVD_RELATIVE_TOLERANCE:
        raise ValueError('phase_motion_confounded')
    influence = (vh.T/singular)@u.T
    beta = influence@(y-basis@(basis.T@y))
    nuisance_coef = np.linalg.lstsq(nuisance, y-h@beta,
                                    rcond=SVD_RELATIVE_TOLERANCE)[0]
    prediction = h@beta+nuisance@nuisance_coef
    residual = y-prediction
    leverage = np.sum(basis*basis, axis=1)+np.sum(u*u, axis=1)
    if np.any(leverage >= 1.-1e-10):
        raise ValueError('insufficient_residual_degrees_of_freedom')
    hc3_influence = influence*(residual/np.maximum(1.-leverage, 1e-10))
    covariance = hc3_influence@hc3_influence.T
    if not all(np.isfinite(value).all() for value in
               (beta, nuisance_coef, residual, covariance, singular)):
        raise ValueError('nonfinite_fit')
    return dict(beta=beta, nuisance_coef=nuisance_coef, residual=residual,
                covariance=covariance, rank=nuisance_rank+6,
                influence=influence, leverage=leverage,
                nuisance_rank=nuisance_rank,
                information_fraction=float(2.*singular[-1]**2/len(y)))


def _support(samples, center_xy, center_time):
    if samples.ndim != 2 or samples.shape[1] != 6 or len(samples) < 72:
        raise ValueError('invalid_sample_shape_or_count')
    if not np.isfinite(samples).all() or not np.isfinite(center_xy).all() or not math.isfinite(center_time):
        raise ValueError('nonfinite_input')
    if np.shape(center_xy) != (2,):
        raise ValueError('invalid_center')
    gaps = np.diff(samples[:, 0])
    if np.any(gaps <= 0) or np.any(gaps > .500000001):
        raise ValueError('source_gap_or_order')
    if samples[-1, 0]-samples[0, 0] > 12.000000001:
        raise ValueError('support_duration')
    excursion = float(np.max(np.linalg.norm(samples[:, 1:3]-center_xy, axis=1)))
    if excursion > .5000000001:
        raise ValueError('support_excursion')
    cycles = samples[:, 5]
    if not np.array_equal(np.unique(cycles), [0., 1., 2.]) or np.any(np.diff(cycles) < 0):
        raise ValueError('three_ordered_cycles_required')
    delta = np.remainder(np.diff(samples[:, 3])+math.pi, math.tau)-math.pi
    if np.any(np.abs(np.abs(delta)-math.pi) <= 1e-12):
        raise ValueError('ambiguous_phase_step')
    moving = delta[np.abs(delta) > 1e-12]
    if len(moving) == 0 or np.any(moving*np.sign(moving[0]) < -1e-12):
        raise ValueError('phase_reversal_or_stall')
    phase = np.r_[0., np.cumsum(delta)]
    largest_step = float(np.max(np.abs(delta)))
    sector_counts = []
    for cycle in range(3):
        indices = np.flatnonzero(cycles == cycle)
        span = abs(phase[indices[-1]]-phase[indices[0]])
        # Real samples may lie inside both clipped phase boundaries. No raw
        # endpoint is invented: retain at most one step of slack at each end.
        if not math.tau-2*largest_step-1e-8 <= span <= math.tau+largest_step+1e-8:
            raise ValueError('incomplete_cycle')
        sectors = np.minimum(11, (np.remainder(samples[indices, 3], math.tau)/(math.tau/12)).astype(int))
        counts = np.bincount(sectors, minlength=12)
        if np.any(counts < 2):
            raise ValueError('insufficient_sector_coverage')
        sector_counts.append(counts.tolist())
    return excursion, sector_counts


def fit_profile(samples, center_xy=None, center_time=None):
    """Fit Nx6 [seconds,x,y,world_phase,raw_cost,cycle_id] source samples.

    Valid denotes finite, supported and identifiable fits only. Callers must
    separately apply the frozen empirical score and direction-proxy decisions.
    """
    result = dict(valid=False, reason=None, coefficients=None, cv_gain=None,
                  cv_gains=[], harmonic_snr=None, information_fraction=None,
                  residual_rms=None, sample_count=0, rank=None)
    try:
        samples = np.asarray(samples, dtype=float)
        if samples.ndim != 2 or samples.shape[1] != 6 or len(samples) == 0:
            raise ValueError('invalid_sample_shape_or_count')
        result['sample_count'] = len(samples)
        center_xy = np.asarray(samples[-1, 1:3] if center_xy is None else center_xy, dtype=float)
        center_time = float(samples[-1, 0] if center_time is None else center_time)
        excursion, counts = _support(samples, center_xy, center_time)
        z, h, p = _basis(samples, center_xy, center_time)
        # A common DC shift changes neither information nor angular response.
        y_offset = float(np.mean(samples[:, 4]))
        y = samples[:, 4]-y_offset
        fitted = _linear_fit(z, h, p, y)
        result.update(information_fraction=fitted['information_fraction'],
                      rank=fitted['rank'], nuisance_rank=fitted['nuisance_rank'],
                      maximum_excursion_m=excursion, sector_counts=counts,
                      center_xy=center_xy.tolist(), center_time=center_time)
        if fitted['information_fraction'] < INFORMATION_FRACTION_MIN:
            raise ValueError('insufficient_angular_information')
        gains = []
        for cycle in range(3):
            held = samples[:, 5] == cycle
            trained = _linear_fit(z[~held], h[~held], p[~held], y[~held])
            angular = h[held]@trained['beta']+p[held]@trained['nuisance_coef'][4:]
            held_nuisance, _ = _subspace(z[held])
            observed = y[held]-held_nuisance@(held_nuisance.T@y[held])
            predicted = angular-held_nuisance@(held_nuisance.T@angular)
            energy = float(observed@observed)
            error = observed-predicted
            gains.append(float((energy-error@error)/max(energy, int(np.sum(held))*1e-12)))
        proxy = math.sqrt(max(0., float(np.trace(fitted['covariance'][:2, :2]))))
        magnitude = float(np.linalg.norm(fitted['beta'][:2]))
        snr = magnitude/max(proxy, 1e-12)
        residual_rms = float(np.sqrt(np.mean(fitted['residual']**2)))
        numeric = [*fitted['beta'], *gains, snr, residual_rms, proxy,
                   fitted['information_fraction'], *fitted['covariance'].ravel()]
        if not np.isfinite(numeric).all():
            raise ValueError('nonfinite_fit')
        result.update(coefficients=fitted['beta'].tolist(), cv_gains=gains,
                      cv_gain=min(gains), harmonic_snr=snr,
                      first_harmonic_uncertainty_proxy=proxy,
                      harmonic_covariance_hc3=fitted['covariance'].tolist(),
                      residual_rms=residual_rms)
        result.update(valid=True, reason='supported_identifiable_fit')
    except (ValueError, TypeError, IndexError, ArithmeticError, np.linalg.LinAlgError) as exc:
        result.update(valid=False, reason=str(exc))
    return result


def fit_reduced_profile(samples, center_xy=None, center_time=None, *, spatial_degree=1):
    """R15 local constant angular profile, with descriptive time-HAC covariance.

    Same causal Nx6 raw support as ``fit_profile``. This separate entrypoint
    omits position-harmonic interactions; its approximation needs independent
    validation. A finite fit is distinct from latest-cycle predictive admission
    and the externally calibrated signal-score decision.
    """
    result = dict(valid=False, reason=None, coefficients=None,
                  covariance_hac=None, signal_score=None, cv_gains=[],
                  latest_prediction_pass=False, sample_count=0)
    try:
        samples = np.asarray(samples, dtype=float)
        if samples.ndim != 2 or samples.shape[1] != 6 or len(samples) == 0:
            raise ValueError('invalid_sample_shape_or_count')
        result['sample_count'] = len(samples)
        center_xy = np.asarray(samples[-1, 1:3] if center_xy is None else center_xy,
                               dtype=float)
        center_time = float(samples[-1, 0] if center_time is None else center_time)
        excursion, counts = _support(samples, center_xy, center_time)
        z, h, _ = _basis(samples, center_xy, center_time)
        if spatial_degree not in (1, 2) or isinstance(spatial_degree, bool):
            raise ValueError('invalid_spatial_degree')
        if spatial_degree == 2:
            dx, dy = z[:, 2], z[:, 3]
            z = np.column_stack((z, dx*dx, dx*dy, dy*dy))
        empty = np.empty((len(samples), 0))
        y = samples[:, 4]-float(np.mean(samples[:, 4]))
        fitted = _linear_fit(z, h, empty, y)
        adjusted = fitted['influence'] * (
            fitted['residual']/np.maximum(1.-fitted['leverage'], 1e-10))
        # The triangular physical-time kernel is positive semidefinite also
        # for irregular source stamps. Bandwidth is fixed at one second.
        kernel = np.maximum(0., 1.-np.abs(samples[:, 0, None]-samples[None, :, 0]))
        covariance = adjusted@kernel@adjusted.T
        covariance = (covariance+covariance.T)/2.
        eigenvalues = np.linalg.eigvalsh(covariance)
        tolerance = 1e-10*max(float(np.max(np.abs(eigenvalues))), 1e-24)
        if eigenvalues[0] < -tolerance:
            raise ValueError('nonpositive_hac_covariance')
        directional_variance = float(np.linalg.eigvalsh(covariance[:2, :2])[-1])
        proxy = math.sqrt(max(0., directional_variance))
        score = float(np.linalg.norm(fitted['beta'][:2]))/max(proxy, 1e-12)
        gains, fold_reasons = [], []
        for cycle in range(3):
            held = samples[:, 5] == cycle
            try:
                trained = _linear_fit(z[~held], h[~held], empty[~held], y[~held])
                held_nuisance, _ = _subspace(z[held])
                observed = y[held]-held_nuisance@(held_nuisance.T@y[held])
                angular = h[held]@trained['beta']
                predicted = angular-held_nuisance@(held_nuisance.T@angular)
                energy = float(observed@observed)
                error = observed-predicted
                gain = float((energy-error@error)/max(energy, int(np.sum(held))*1e-12))
                if not math.isfinite(gain):
                    raise ValueError('nonfinite_prediction_gain')
                gains.append(gain)
                fold_reasons.append(None)
            except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
                gains.append(None)
                fold_reasons.append(str(exc))
        residual_rms = float(np.sqrt(np.mean(fitted['residual']**2)))
        if not np.isfinite([*fitted['beta'], *covariance.ravel(), score,
                            residual_rms, proxy]).all():
            raise ValueError('nonfinite_fit')
        result.update(valid=True, reason='supported_reduced_fit',
                      spatial_degree=spatial_degree,
                      coefficients=fitted['beta'].tolist(),
                      covariance_hac=covariance.tolist(),
                      covariance_hc3=fitted['covariance'].tolist(),
                      covariance_bandwidth_sec=1.,
                      first_harmonic_uncertainty_proxy=proxy,
                      score_denominator_floor=1e-12, signal_score=score,
                      cv_gains=gains, cv_fold_reasons=fold_reasons,
                      latest_prediction_pass=gains[-1] is not None and gains[-1] > 0.,
                      residual_rms=residual_rms,
                      information_fraction=fitted['information_fraction'],
                      rank=fitted['rank'], nuisance_rank=fitted['nuisance_rank'],
                      maximum_excursion_m=excursion, sector_counts=counts,
                      center_xy=center_xy.tolist(), center_time=center_time)
    except (ValueError, TypeError, IndexError, ArithmeticError, np.linalg.LinAlgError) as exc:
        result.update(valid=False, reason=str(exc))
    return result


def _spatial_design(samples, center_xy, center_time):
    z, h, _ = _basis(samples, center_xy, center_time)
    dx, dy = z[:, 2], z[:, 3]
    z = np.column_stack((z, dx*dx, dx*dy, dy*dy))
    p = np.column_stack((dx[:, None]*h, dy[:, None]*h))
    return z, h, p, np.column_stack((z, h, p))


def _spatial_estimability(design, output_map):
    """Check the requested output against the *unregularized* null space."""
    u, singular, vh = np.linalg.svd(design, full_matrices=False)
    rank = int(np.sum(singular > singular[0]*SVD_RELATIVE_TOLERANCE))
    selector = np.zeros((2, design.shape[1]))
    selector[:, 7:13] = output_map
    # Normalize before taking norms so the relative test is invariant to units.
    normalized = selector/np.max(np.abs(output_map))
    null = vh[rank:].T
    null_ratio = (float(np.linalg.norm(normalized@null, ord=2)) /
                  float(np.linalg.norm(normalized, ord=2))) if null.size else 0.
    output_influence = ((selector@vh[:rank].T)/singular[:rank])@u[:, :rank].T
    noise_gain = float(np.linalg.norm(output_influence, ord=2))
    if not np.isfinite([*singular, null_ratio, noise_gain]).all():
        raise ValueError('nonfinite_estimability')
    return dict(output_estimable=null_ratio <= 1e-8,
                output_null_ratio=null_ratio, rank=rank,
                singular_values=singular.tolist(),
                unregularized_output_noise_gain=noise_gain)


def _spatial_solve(design, raw, regularization):
    """Augmented ridge solve and derivative with respect to original raw rows."""
    n = len(raw)
    penalty = np.zeros((12, design.shape[1]))
    penalty[:, 13:] = math.sqrt(n*regularization)*np.eye(12)
    augmented = np.vstack((design, penalty))
    u, singular, vh = np.linalg.svd(augmented, full_matrices=False)
    rank = int(np.sum(singular > singular[0]*SVD_RELATIVE_TOLERANCE))
    inverse = (vh[:rank].T/singular[:rank])@u[:, :rank].T
    uncentered_influence = inverse[:, :n]
    # Removing raw DC is an actual part of the estimator. Include that linear
    # operation in its derivative, and restore the fitted DC in the leverage.
    influence = uncentered_influence-np.mean(uncentered_influence, axis=1)[:, None]
    centered = raw-float(np.mean(raw))
    coefficients = uncentered_influence@centered
    residual = centered-design@coefficients
    leverage = np.sum(design*influence.T, axis=1)+1./n
    if not all(np.isfinite(v).all() for v in
               (coefficients, influence, residual, leverage, singular)):
        raise ValueError('nonfinite_fit')
    if np.any(leverage >= 1.-1e-10) or np.any(leverage < -1e-10):
        raise ValueError('insufficient_residual_degrees_of_freedom')
    return dict(coefficients=coefficients, influence=influence,
                residual=residual, leverage=leverage,
                augmented_rank=rank, augmented_singular_values=singular)


def fit_spatial_profile(samples, center_xy=None, center_time=None, *,
                        regularization, output_map=None):
    """R17 spatial H1--H3 profile at an anchor, without a runtime decision.

    Input rows are [seconds,x,y,world_phase,raw_cost,cycle_id]. The supplied
    finite nonzero 2x6 map defines the output whose estimability is required;
    its default selects H1 cosine/sine. Ridge penalizes the twelve spatial
    interactions only, in mean-square-loss units. HAC covariance and the latest
    predictive gain are descriptive and do not bound shrinkage/model bias.
    """
    result = dict(valid=False, reason=None, coefficients=None,
                  covariance_hac=None, raw_output=None,
                  output_covariance_hac=None, signal_score=None,
                  latest_predictive_gain=None, latest_predictive_reason=None,
                  output_estimable=False, output_null_ratio=None, rank=None,
                  singular_values=None, unregularized_output_noise_gain=None,
                  sample_count=0)
    try:
        if isinstance(regularization, (bool, np.bool_)) or np.ndim(regularization) != 0:
            raise ValueError('invalid_regularization')
        regularization = float(regularization)
        if not math.isfinite(regularization) or regularization < 0.:
            raise ValueError('invalid_regularization')
        if output_map is None:
            output_map = np.eye(2, 6)
        output_map = np.asarray(output_map, dtype=float)
        if (output_map.shape != (2, 6) or not np.isfinite(output_map).all()
                or not np.any(output_map != 0.)):
            raise ValueError('invalid_output_map')
        samples = np.asarray(samples, dtype=float)
        if samples.ndim != 2 or samples.shape[1] != 6 or len(samples) == 0:
            raise ValueError('invalid_sample_shape_or_count')
        result['sample_count'] = len(samples)
        center_xy = np.asarray(samples[-1, 1:3] if center_xy is None else center_xy,
                               dtype=float)
        center_time = float(samples[-1, 0] if center_time is None else center_time)
        excursion, counts = _support(samples, center_xy, center_time)
        z, h, p, design = _spatial_design(samples, center_xy, center_time)
        if not np.isfinite(design).all():
            raise ValueError('nonfinite_design')
        result.update(regularization=regularization, output_map=output_map.tolist(),
                      center_xy=center_xy.tolist(), center_time=center_time,
                      maximum_excursion_m=excursion, sector_counts=counts,
                      support_duration_sec=float(samples[-1, 0]-samples[0, 0]),
                      **_spatial_estimability(design, output_map))
        if not result['output_estimable']:
            raise ValueError('output_phase_motion_confounded')
        fitted = _spatial_solve(design, samples[:, 4], regularization)
        beta = fitted['coefficients'][7:13]
        adjusted = fitted['influence'][7:13] * (
            fitted['residual']/np.maximum(1.-fitted['leverage'], 1e-10))
        kernel = np.maximum(0., 1.-np.abs(samples[:, 0, None]-samples[None, :, 0]))
        covariance = adjusted@kernel@adjusted.T
        covariance = (covariance+covariance.T)/2.
        output = output_map@beta
        output_covariance = output_map@covariance@output_map.T
        output_covariance = (output_covariance+output_covariance.T)/2.
        for value in (covariance, output_covariance):
            if not np.isfinite(value).all():
                raise ValueError('nonfinite_fit')
            eigenvalues = np.linalg.eigvalsh(value)
            tolerance = 1e-10*max(float(np.max(np.abs(eigenvalues))), 1e-24)
            if eigenvalues[0] < -tolerance:
                raise ValueError('nonpositive_hac_covariance')
        proxy = math.sqrt(max(0., float(np.linalg.eigvalsh(output_covariance)[-1])))
        score = float(np.linalg.norm(output))/max(proxy, 1e-12)
        residual_rms = float(np.sqrt(np.mean(fitted['residual']**2)))
        if not np.isfinite([*beta, *output, score, proxy, residual_rms]).all():
            raise ValueError('nonfinite_fit')

        # A failed prior-two-cycle fit is retained as a missing diagnostic; it
        # cannot discard an otherwise estimable full-window result.
        gain, predictive_reason = None, None
        try:
            held = samples[:, 5] == 2
            if not _spatial_estimability(design[~held], output_map)['output_estimable']:
                raise ValueError('output_phase_motion_confounded')
            trained = _spatial_solve(design[~held], samples[~held, 4], regularization)
            angular = (h[held]@trained['coefficients'][7:13]
                       +p[held]@trained['coefficients'][13:])
            held_basis, _ = _subspace(z[held])
            observed = samples[held, 4]-float(np.mean(samples[held, 4]))
            observed -= held_basis@(held_basis.T@observed)
            predicted = angular-held_basis@(held_basis.T@angular)
            energy = float(observed@observed)
            error = observed-predicted
            gain = float((energy-error@error)/max(energy, int(np.sum(held))*1e-12))
            if not math.isfinite(gain):
                raise ValueError('nonfinite_prediction_gain')
        except (ValueError, TypeError, ArithmeticError, np.linalg.LinAlgError) as exc:
            gain, predictive_reason = None, str(exc)
        result.update(valid=True, reason='supported_spatial_fit',
                      coefficients=beta.tolist(), covariance_hac=covariance.tolist(),
                      raw_output=output.tolist(),
                      output_covariance_hac=output_covariance.tolist(),
                      signal_score=score, output_uncertainty_proxy=proxy,
                      latest_predictive_gain=gain,
                      latest_predictive_reason=predictive_reason,
                      interaction_coefficients=fitted['coefficients'][13:].tolist(),
                      nuisance_coefficients=fitted['coefficients'][:7].tolist(),
                      residual_rms=residual_rms,
                      maximum_leverage=float(np.max(fitted['leverage'])),
                      augmented_rank=fitted['augmented_rank'],
                      augmented_singular_values=fitted['augmented_singular_values'].tolist(),
                      covariance_bandwidth_sec=1., score_denominator_floor=1e-12)
    except (ValueError, TypeError, IndexError, ArithmeticError, np.linalg.LinAlgError) as exc:
        result.update(valid=False, reason=str(exc))
    return result


def fit_affine_gesc_field(samples, center_xy, *, output_map):
    """R20 raw stationary-GESC affine field; no local-attraction decision.

    Rows are [source_seconds, base_x, base_y, UNWRAPPED_world_phase, raw_cost].
    The explicit 2x6 map includes the selected demodulation sign and gains.
    ``field_vector`` is [qx,qy,Bxx,Bxy,Byx,Byy], with B per physical metre.
    The caller owns source/context identity, full/half selection and decisions.
    Full q/B HAC cross-covariance describes noise, not model-error bounds.
    """
    result = dict(valid=False, reason=None, field_vector=None,
                  field_covariance=None, coefficients=None, sample_count=0,
                  output_estimable=False, output_null_ratio=None, rank=None)
    try:
        samples = np.asarray(samples, dtype=float)
        center = np.asarray(center_xy, dtype=float)
        mapping = np.asarray(output_map, dtype=float)
        if samples.ndim != 2 or samples.shape[1] != 5:
            raise ValueError('invalid_sample_shape_or_count')
        n = len(samples)
        result['sample_count'] = n
        if not 48 <= n <= 1024:
            raise ValueError('invalid_sample_shape_or_count')
        if center.shape != (2,) or not np.isfinite(center).all():
            raise ValueError('invalid_center')
        if (mapping.shape != (2, 6) or not np.isfinite(mapping).all()
                or not np.any(mapping != 0.)):
            raise ValueError('invalid_output_map')
        if not np.isfinite(samples).all():
            raise ValueError('nonfinite_input')
        gaps = np.diff(samples[:, 0])
        if not np.isfinite(gaps).all() or np.any(gaps <= 0.) or np.any(gaps > .100000001):
            raise ValueError('source_gap_or_order')
        duration = float(samples[-1, 0]-samples[0, 0])
        if duration > 30.000000001:
            raise ValueError('support_duration')
        delta = samples[:, 1:3]-center
        excursion = float(np.max(np.hypot(delta[:, 0], delta[:, 1])))
        if not math.isfinite(excursion) or excursion > .2500000001:
            raise ValueError('support_excursion')
        phase_steps = np.diff(samples[:, 3])
        if not np.isfinite(phase_steps).all():
            raise ValueError('nonfinite_phase_progress')
        progress = float(samples[-1, 3]-samples[0, 3])
        if not math.isfinite(progress) or abs(progress) < 3.*math.tau-1e-10:
            raise ValueError('insufficient_world_rotations')
        if np.any(phase_steps*math.copysign(1., progress) < -1e-12):
            raise ValueError('world_phase_not_monotone_unwrapped')
        sectors = np.minimum(11, (np.remainder(samples[:, 3], math.tau)/(math.tau/12)).astype(int))
        counts = np.bincount(sectors, minlength=12)
        if np.any(counts < 4):
            raise ValueError('insufficient_sector_coverage')
        result.update(center_xy=center.tolist(), output_map=mapping.tolist(),
                      source_start_sec=float(samples[0, 0]),
                      source_end_sec=float(samples[-1, 0]),
                      support_duration_sec=duration, maximum_source_gap_sec=float(np.max(gaps)),
                      maximum_excursion_m=excursion, phase_rotations=abs(progress)/math.tau,
                      phase_direction=math.copysign(1., progress), sector_counts=counts.tolist())
        _, _, _, design = _spatial_design(samples, center, float(samples[-1, 0]))
        selector = np.zeros((6, 25))
        selector[:2, 7:13] = mapping
        selector[2, 13:19] = mapping[0]/.15  # Bxx
        selector[3, 19:25] = mapping[0]/.15  # Bxy
        selector[4, 13:19] = mapping[1]/.15  # Byx
        selector[5, 19:25] = mapping[1]/.15  # Byy
        if not np.isfinite(design).all() or not np.isfinite(selector).all():
            raise ValueError('nonfinite_design_or_selector')
        u, singular, vh = np.linalg.svd(design, full_matrices=False)
        rank = int(np.sum(singular > singular[0]*SVD_RELATIVE_TOLERANCE))
        # Normalize each requested functional separately: q and B have different
        # physical units, and no weak row may hide behind a larger row's scale.
        normalized = selector/np.max(np.abs(selector))
        scales = np.linalg.norm(normalized, axis=1)
        nonzero = scales > 0.
        normalized[nonzero] /= scales[nonzero, None]
        null_ratios = np.linalg.norm(normalized@vh[rank:].T, axis=1)
        noise_influence = ((selector@vh[:rank].T)/singular[:rank])@u[:, :rank].T
        noise_gain = np.linalg.norm(noise_influence, axis=1)
        if not np.isfinite([*singular, *null_ratios, *noise_gain]).all():
            raise ValueError('nonfinite_estimability')
        output_estimable = bool(np.all(null_ratios <= 1e-8))
        result.update(output_estimable=output_estimable,
                      output_null_ratio=float(np.max(null_ratios)),
                      output_null_ratios=null_ratios.tolist(), rank=rank,
                      singular_values=singular.tolist(),
                      unregularized_noise_gain_by_component=noise_gain.tolist())
        if not output_estimable:
            raise ValueError('affine_field_not_estimable')
        fitted = _spatial_solve(design, samples[:, 4], 0.)
        coefficients = fitted['coefficients'].copy()
        # Public coefficients predict original raw cost, not DC-centered cost.
        coefficients[0] += float(np.mean(samples[:, 4]))
        field = selector@coefficients
        influence = selector@fitted['influence']
        adjusted = influence*(fitted['residual']/np.maximum(1.-fitted['leverage'], 1e-10))
        kernel = np.maximum(0., 1.-np.abs(samples[:, 0, None]-samples[None, :, 0]))
        covariance = adjusted@kernel@adjusted.T
        covariance = (covariance+covariance.T)/2.
        if not all(np.isfinite(v).all() for v in (field, coefficients, covariance)):
            raise ValueError('nonfinite_fit')
        eigenvalues = np.linalg.eigvalsh(covariance)
        tolerance = 1e-10*max(float(np.max(np.abs(eigenvalues))), 1e-24)
        if eigenvalues[0] < -tolerance:
            raise ValueError('nonpositive_hac_covariance')
        residual_rms = float(np.sqrt(np.mean(fitted['residual']**2)))
        if not math.isfinite(residual_rms):
            raise ValueError('nonfinite_fit')
        result.update(valid=True, reason='supported_affine_gesc_field',
                      field_vector=field.tolist(), field_covariance=covariance.tolist(),
                      coefficients=coefficients.tolist(), residual_rms=residual_rms,
                      maximum_leverage=float(np.max(fitted['leverage'])),
                      covariance_bandwidth_sec=1., spatial_scale_m=.15,
                      center_time_sec=float(samples[-1, 0]), regularization=0.)
    except (ValueError, TypeError, IndexError, ArithmeticError, np.linalg.LinAlgError) as exc:
        result.update(valid=False, reason=str(exc))
    return result
