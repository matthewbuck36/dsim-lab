"""Policy-specific claims reused by the existing recorder/analyzer owners."""

import math

from ros_esc_interfaces.msg import AlgorithmState

from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, POLICY_SCHEMA_VERSION, policy_config_sha256,
)
from ros_esc.v2_lifecycle import hash_payload, message_payload
from ros_esc.v2_stream import time_to_ns


def index_policy_companions(records):
    """Retain exact publication keys; contradictions cannot select a replacement."""
    indexed, errors = {}, []
    for _, message in records:
        try:
            key = (int(message.diagnostic_sequence), time_to_ns(message.stamp))
            if key[0] <= 0:
                raise ValueError('policy diagnostic sequence must be positive')
            fingerprint = hash_payload(message_payload(message))
            if key in indexed and indexed[key][0] != fingerprint:
                raise ValueError('conflicting policy companion for one publication')
            indexed[key] = (fingerprint, message)
        except (ValueError, TypeError, AttributeError, OverflowError) as exc:
            errors.append('V2 direction policy: ' + str(exc))
    return {key: value[1] for key, value in indexed.items()}, errors


def direction_policy_pair_errors(direction, companion):
    """Check the fixed moving-policy companion and its exact original output.

    Common source/pose/freshness checks remain in v2_stream_contract_errors.
    This verifies recorded arithmetic claims, not the unrecorded field truth.
    """
    def require(condition, reason):
        if not condition:
            raise ValueError(reason)

    def close(left, right):
        return math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-12)

    def optional_equal(left, right):
        return left == right or math.isnan(left) and math.isnan(right)

    try:
        require(companion is not None, 'missing exact policy companion')
        require(companion.policy_schema_version == POLICY_SCHEMA_VERSION
                and companion.direction_policy == MOVING_CYCLE_POLICY
                and companion.policy_config_sha256 == policy_config_sha256(MOVING_CYCLE_POLICY)
                and companion.configured_mean_weight == .75
                and companion.coherence_threshold == .25
                and companion.output_units == direction.output_units == 'cost_units_per_metre',
                'policy identity/configuration/units mismatch')
        for name in ('stamp', 'time_origin', 'rolling_start', 'rolling_end'):
            require(time_to_ns(getattr(companion, name)) == time_to_ns(getattr(direction, name)),
                    'policy publication/origin/rolling interval mismatch')
        for name in ('run_id', 'stream_contract_id', 'frame_id', 'diagnostic_sequence',
                     'reset_sequence', 'reset_reason', 'objective_revision', 'objective_sha256',
                     'registry_digest', 'affine_revision', 'output_valid', 'fallback_used',
                     'blend_allowed', 'fallback_reason', 'mean_full', 'coverage_valid'):
            require(getattr(companion, name) == getattr(direction, name),
                    'policy companion differs from direction: ' + name)
        require(companion.source_schema_version == direction.schema_version
                and companion.selected_policy_qualified == direction.qualified
                and companion.actual_blend_weight == direction.blend_weight
                and optional_equal(companion.mean_magnitude, direction.mean_magnitude),
                'policy selected output fields mismatch')
        expected_permission = bool(direction.algorithm_state_valid
                                   and direction.algorithm_state in (
                                       AlgorithmState.STATE_SEARCH,
                                       AlgorithmState.STATE_VERIFY_EXTREMUM,
                                       AlgorithmState.STATE_DESIGN_OR_MERGE_FILL))
        require(direction.blend_allowed == expected_permission,
                'policy blend permission differs from recorded valid algorithm state')
        observation = direction.observation
        for name in ('source_sequence', 'observation_id'):
            require(getattr(companion, name) == getattr(observation, name),
                    'policy source/observation identity mismatch')
        for name in ('source_stamp', 'cost_source_stamp'):
            require(time_to_ns(getattr(companion, name)) == time_to_ns(getattr(observation, name)),
                    'policy original source stamp mismatch')
        if direction.mean_full:
            start, end = time_to_ns(direction.rolling_start), time_to_ns(direction.rolling_end)
            require(time_to_ns(direction.time_origin) <= start < end
                    and end == time_to_ns(observation.source_stamp)
                    and close(direction.rolling_duration_sec, (end-start)*1e-9)
                    and math.isfinite(direction.phase_start_rad)
                    and math.isfinite(direction.phase_end_rad)
                    and close(abs(direction.phase_end_rad-direction.phase_start_rad), math.tau)
                    and len(direction.sector_counts) == 12
                    and direction.rolling_sample_count == sum(direction.sector_counts)
                    and math.isfinite(direction.max_sample_gap_sec)
                    and direction.max_sample_gap_sec > 0,
                    'policy full mean has inconsistent current-cycle support')
        if direction.coverage_valid:
            require(direction.mean_full and direction.rolling_duration_sec <= 30.
                    and direction.max_sample_gap_sec <= .5
                    and min(direction.sector_counts) >= 2,
                    'policy covered mean violates current-cycle coverage limits')
        require(0 <= companion.norm_new_evaluations <= 2048
                and companion.norm_window_evaluations >= 0
                and (not companion.coherence_available or companion.norm_window_evaluations <= 20000),
                'policy norm evaluation budget exceeded')
        warmup = (direction.completed_revolutions >= 3
                  and len(direction.cycle_coverage_valid) == 3
                  and all(direction.cycle_coverage_valid)
                  and len(direction.cycle_sector_counts) == 36
                  and min(direction.cycle_sector_counts) >= 2
                  and len(direction.cycle_start) == len(direction.cycle_end) == 3)
        if warmup:
            starts = [time_to_ns(value) for value in direction.cycle_start]
            ends = [time_to_ns(value) for value in direction.cycle_end]
            warmup = (all(0 < end-start <= 30_000_000_000 for start, end in zip(starts, ends))
                      and ends[:-1] == starts[1:]
                      and ends[-1] <= time_to_ns(observation.source_stamp))
        require(companion.warmup_valid == warmup, 'policy warmup differs from covered cycle receipts')
        eligible = False
        if companion.coherence_available:
            require(direction.mean_full and direction.coverage_valid and warmup,
                    'available coherence lacks covered current mean and warmup')
            values = (companion.mean_magnitude, companion.norm_denominator,
                      companion.norm_error, companion.numerator_margin, companion.coherence,
                      companion.coherence_lower, companion.coherence_upper)
            require(all(math.isfinite(value) for value in values), 'available coherence has nonfinite values')
            require(len(direction.mean_world) == 2
                    and all(math.isfinite(value) for value in direction.mean_world),
                    'available coherence has no finite mean')
            numerator = math.hypot(*direction.mean_world)
            denominator, error = companion.norm_denominator, companion.norm_error
            margin = math.sqrt(2)*(1e-10+1e-8*numerator)
            require(0 <= error <= 1e-10 and denominator > error
                    and close(numerator, companion.mean_magnitude)
                    and close(margin, companion.numerator_margin)
                    and numerator <= denominator+error+margin,
                    'coherence denominator/error/mean/triangle inconsistency')
            lower = max(0., numerator-margin)/(denominator+error)
            upper = min(1., (numerator+margin)/(denominator-error))
            require(close(companion.coherence, min(1., numerator/denominator))
                    and close(companion.coherence_lower, lower)
                    and close(companion.coherence_upper, upper)
                    and 0 <= companion.coherence_lower <= companion.coherence_upper <= 1,
                    'coherence bounds differ from recorded numerator/denominator')
            eligible = bool(direction.mean_full and direction.coverage_valid
                            and warmup and numerator > 1e-6 and lower >= .25)
        require(direction.qualified == eligible, 'selected qualification differs from fixed coherence rule')
        if direction.output_valid:
            require(direction.blend_weight in (0., .75), 'moving-policy output uses an undeclared weight')
            require(len(direction.instant_world) == 2 and all(math.isfinite(v) for v in direction.instant_world)
                    and math.isfinite(direction.output_yaw_rad), 'valid output lacks finite instant/current yaw')
            require(len(direction.output_body) == 2 and all(math.isfinite(v) for v in direction.output_body)
                    and math.hypot(*direction.output_body) > 1e-6,
                    'moving-policy valid output is not meaningful')
            if eligible and direction.blend_allowed:
                mixture = [.25*a+.75*b for a, b in zip(direction.instant_world, direction.mean_world)]
                meaningful = all(math.isfinite(v) for v in mixture) and math.hypot(*mixture) > 1e-6
                if meaningful:
                    require(direction.blend_weight == .75, 'eligible meaningful mixture was silently bypassed')
                else:
                    require(direction.blend_weight == 0
                            and direction.fallback_reason == 'weak_or_nonfinite_mixture',
                            'weak mixture lacks its explicit instantaneous fallback')
            if direction.blend_weight:
                require(eligible and direction.blend_allowed and not direction.fallback_used,
                        'mean applied without selected eligibility/state permission')
            elif direction.blend_allowed:
                require(direction.fallback_used and len(direction.instant_world) == 2
                        and all(math.isfinite(v) for v in direction.instant_world)
                        and math.hypot(*direction.instant_world) > 1e-6,
                        'instantaneous fallback is not meaningful')
            weight = direction.blend_weight
            world = ([(1-weight)*a+weight*b for a, b in zip(direction.instant_world, direction.mean_world)]
                     if weight else list(direction.instant_world))
            cosine, sine = math.cos(direction.output_yaw_rad), math.sin(direction.output_yaw_rad)
            expected = [cosine*world[0]+sine*world[1], -sine*world[0]+cosine*world[1]]
            require(all(close(a, b) for a, b in zip(expected, direction.output_body))
                    and close(math.hypot(*direction.output_body), direction.output_magnitude),
                    'moving-policy output differs from fixed world blend/current-body rotation')
        return []
    except (ValueError, TypeError, AttributeError, IndexError, OverflowError, ZeroDivisionError) as exc:
        return ['V2 direction policy: ' + str(exc)]
