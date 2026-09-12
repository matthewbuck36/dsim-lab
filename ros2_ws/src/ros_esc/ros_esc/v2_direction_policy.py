"""Explicit filter-policy identity, independent of source acquisition schema."""

import hashlib
import json
import math


THREE_CYCLE_POLICY = 'three_cycle_v1'
MOVING_CYCLE_POLICY = 'moving_cycle_coherence_v1'
DIRECTION_POLICIES = (THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY)
POLICY_SCHEMA_VERSION = 1
POLICY_DIAGNOSTICS_TOPIC = '/gesc_gaussian/v2/direction_policy_diagnostics'


def validate_policy(policy, *, continuous_search_mode=None,
                    algorithm_profile=None, use_sim_time=None):
    """Validate a name and, when supplied, its selected runtime environment."""
    if not isinstance(policy, str) or policy not in DIRECTION_POLICIES:
        raise ValueError('unsupported V2 direction policy')
    if policy == MOVING_CYCLE_POLICY:
        if continuous_search_mode is not None and continuous_search_mode != 'rolling_gesc_v2':
            raise ValueError('moving_cycle_coherence_v1 requires rolling_gesc_v2')
        if algorithm_profile is not None and algorithm_profile != 'robust_gaussian_v1':
            raise ValueError('moving_cycle_coherence_v1 requires robust_gaussian_v1')
        if use_sim_time is not None and use_sim_time is not True:
            raise ValueError('moving_cycle_coherence_v1 requires explicit simulation time')
    return policy


def policy_descriptor(policy):
    """Return a fresh canonical descriptor for the fixed selected runtime policy.

    Legacy core-only tests may still instantiate their historical custom
    RollingGescConfig values; this descriptor identifies the public startup
    policy, whose numerical values are fixed by the selected runtime adapter.
    """
    validate_policy(policy)
    descriptor = {
        'policy_schema_version': POLICY_SCHEMA_VERSION,
        'policy_name': policy,
        'output_units': 'cost_units_per_metre',
        'configured_mean_weight': .75 if policy == MOVING_CYCLE_POLICY else .5,
        'coverage_sectors': 12,
        'minimum_samples_per_sector': 2,
        'warmup_covered_cycles': 3,
        'absolute_magnitude_floor': 1e-6,
        'maximum_source_gap_ns': 500_000_000,
        'maximum_cycle_duration_ns': 30_000_000_000,
        'freshness_ns': 500_000_000,
        'maximum_retained_points': 20_000,
    }
    if policy == THREE_CYCLE_POLICY:
        descriptor.update(
            confidence_rule='three_cycle_angle_and_variability_v1',
            maximum_pair_angle_rad=math.pi/6,
            variability_multiplier=3.,
            zero_instant_rule='legacy_informative_mean_continuity_v1',
        )
    else:
        descriptor.update(
            confidence_rule='current_cycle_coherence_lower_bound_v1',
            coherence_threshold=.25,
            norm_representation='source_piecewise_linear_phase_clipped_v1',
            norm_integration='cached_split_minimum_quad_v1',
            norm_quad_epsabs=1e-12,
            norm_quad_epsrel=1e-10,
            norm_quad_limit=64,
            maximum_new_norm_evaluations=2048,
            maximum_window_norm_evaluations=20_000,
            maximum_normalized_denominator_error=1e-10,
            mean_absolute_margin=1e-10,
            mean_relative_margin=1e-8,
            numerator_error_rule='sqrt2_component_margin_v1',
            zero_instant_rule='informative_mixture_allowed_v1',
            weak_mixture_rule='meaningful_instant_or_invalid_v1',
        )
    return descriptor


def policy_config_sha256(policy):
    payload = json.dumps(policy_descriptor(policy), sort_keys=True,
                         separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def policy_metadata(policy):
    return {'policy_name': validate_policy(policy),
            'config': policy_descriptor(policy),
            'config_sha256': policy_config_sha256(policy)}


def validate_policy_metadata(value):
    """Validate an explicit policy record without inferring from output values."""
    if not isinstance(value, dict) or set(value) != {'policy_name', 'config', 'config_sha256'}:
        raise ValueError('direction policy metadata must contain name, config and hash')
    policy = validate_policy(value['policy_name'])
    try:
        actual = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
        expected = json.dumps(policy_metadata(policy), sort_keys=True,
                              separators=(',', ':'), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError('direction policy metadata is not finite canonical JSON') from exc
    if actual != expected:
        raise ValueError('direction policy metadata differs from its fixed descriptor')
    return policy
