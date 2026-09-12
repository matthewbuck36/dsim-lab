"""Independent timing, quadrature and confidence checks for the pure M2 core."""

from dataclasses import replace
import math

import pytest

from ros_esc.filter_node.rolling_gesc import (
    AugmentedCost, DemodulatedSample, EncoderSample, GescSyncConfig,
    ObjectiveIdentity, PoseSample, Provenance, RawCost, RollingGesc,
    RollingGescConfig, SourceSynchronizer, StreamIdentity,
    SynchronizedObservation, publication_time_tolerance_ns,
)


NS = 1_000_000_000
IDENTITY = StreamIdentity("run", "contract", "odom", 0)
OBJECTIVE = ObjectiveIdentity(1)


def ns(seconds):
    return round(seconds * NS)


def sync(config=None):
    value = SourceSynchronizer(config or GescSyncConfig())
    value.set_context(IDENTITY)
    return value


def pose(t, xy=(0.0, 0.0), yaw=0.0, receipt=None):
    return PoseSample(ns(t), xy, yaw, ns(t if receipt is None else receipt), "odom")


def encoder(t, phase=0.0, receipt=None):
    return EncoderSample(ns(t), phase, ns(t if receipt is None else receipt))


def components(source=1.0, publication=1.02, receipt=None, sequence=1, phase=0.6):
    receipt = publication if receipt is None else receipt
    return (
        RawCost(publication, (-2.0,), ns(receipt)),
        AugmentedCost(publication, (-1.5,), OBJECTIVE, ns(receipt)),
        Provenance(publication, sequence, ns(source), ns(publication),
                   (2.0, 3.0), phase, IDENTITY, ns(receipt)),
    )


def push_components(core, rows, now):
    output = []
    for method, value in zip((core.add_raw_cost, core.add_augmented, core.add_provenance), rows):
        batch = method(value, ns(now))
        assert not batch.faults, batch.faults
        output.extend(batch.observations)
    return output


def observation(t, phase, yaw=0.0, objective=OBJECTIVE, index=None):
    stamp = ns(t)
    return SynchronizedObservation(
        observation_id=(stamp + 1 if index is None else index), identity=IDENTITY,
        objective=objective, source_sequence=stamp + 1, source_stamp_ns=stamp,
        cost_source_stamp_ns=stamp, legacy_cost_source_timestamp_sec=t,
        pose_left_stamp_ns=stamp, pose_right_stamp_ns=stamp,
        encoder_left_stamp_ns=stamp, encoder_right_stamp_ns=stamp,
        receipt_stamp_ns=stamp, base_xy=(0.0, 0.0), base_yaw=yaw,
        encoder_phase=phase - yaw, sensor_world_phase=phase, sensor_xy=(0.18, 0.0),
        demodulation_phase_rad=phase - yaw, raw_cost=-2.0, augmented_cost=-2.0,
        sync_error_ns=0,
    )


def feed(core, times, vector=lambda t: (2.0, 0.0), phase=lambda t: 2 * math.pi * t / 3,
         yaw=lambda t: 0.0, objective=OBJECTIVE):
    results = []
    for t in times:
        world = vector(t)
        heading = yaw(t)
        c, s = math.cos(heading), math.sin(heading)
        body = (c * world[0] + s * world[1], -s * world[0] + c * world[1])
        results.append(core.update(DemodulatedSample(
            observation(t, phase(t), heading, objective), body)))
    return results


def times(stop=12, rate=40):
    return [index / rate for index in range(round(stop * rate) + 1)]


def test_join_waits_for_raw_and_interpolates_model_time_not_publication_time():
    core = sync()
    core.add_pose(pose(.95, (1.0, 2.0), .2), ns(.95))
    core.add_encoder(encoder(.95, .3), ns(.95))
    core.add_pose(pose(1.05, (3.0, 4.0), .4), ns(1.05))
    core.add_encoder(encoder(1.05, .5), ns(1.05))
    raw, augmented, provenance = components(receipt=1.05, phase=1.4)
    assert not core.add_provenance(provenance, ns(1.05)).observations
    assert not core.add_augmented(augmented, ns(1.05)).observations
    batch = core.add_raw_cost(raw, ns(1.05))
    assert not batch.faults
    assert len(batch.observations) == 1
    value = batch.observations[0]
    assert value.source_stamp_ns == NS
    assert value.cost_source_stamp_ns == ns(1.02)
    assert value.base_xy == pytest.approx((2.0, 3.0))
    assert value.base_yaw == pytest.approx(.3)
    assert value.encoder_phase == pytest.approx(.4)
    assert value.sensor_world_phase == pytest.approx(1.4)
    assert value.demodulation_phase_rad == pytest.approx(1.1)
    assert value.demodulation_phase_reconstructed
    assert value.sensor_transform_observed
    assert value.sensor_xy == (2.0, 3.0)
    assert value.sync_error_ns == 50_000_000


def test_exact_coincident_brackets_and_time_origin():
    core = SourceSynchronizer()
    identity = replace(IDENTITY, time_origin_ns=100 * NS)
    core.set_context(identity)
    core.add_pose(pose(101), 101 * NS)
    core.add_encoder(encoder(101), 101 * NS)
    raw, augmented, provenance = components(source=101, publication=1, receipt=101)
    provenance = replace(provenance, identity=identity, cost_publication_ns=101 * NS)
    values = push_components(core, (raw, augmented, provenance), 101)
    assert len(values) == 1
    assert values[0].source_stamp_ns == 101 * NS
    assert values[0].legacy_cost_source_timestamp_sec == 1


@pytest.mark.parametrize("origin,publication", [
    (1_700_000_000_123_456_768, 1_700_000_001_987_654_321),
    (0, 1_000_000_000_000_001),
])
def test_actual_publication_stamp_preserved_under_legacy_float_roundoff(origin, publication):
    legacy = publication * 1e-9 - origin * 1e-9
    reconstructed = origin + round(legacy * NS)
    tolerance = publication_time_tolerance_ns(origin, legacy, publication)
    assert abs(publication - reconstructed) <= tolerance
    identity = replace(IDENTITY, time_origin_ns=origin)
    core = SourceSynchronizer()
    core.set_context(identity)
    # A representationally future key must not reject an actually current ROS sample.
    receipt = publication
    core.add_pose(PoseSample(publication, (0., 0.), 0., receipt, "odom"), receipt)
    core.add_encoder(EncoderSample(publication, 0., receipt), receipt)
    rows = (
        RawCost(legacy, (-2.,), receipt),
        AugmentedCost(legacy, (-2.,), OBJECTIVE, receipt),
        Provenance(legacy, 1, publication, publication, (0., 0.), 0., identity, receipt),
    )
    for method, sample in zip((core.add_raw_cost, core.add_augmented, core.add_provenance), rows):
        batch = method(sample, receipt)
        assert not batch.faults
    assert batch.observations[0].cost_source_stamp_ns == publication
    assert batch.observations[0].legacy_cost_source_timestamp_sec == legacy
    assert core.add_provenance(replace(rows[2], cost_publication_ns=publication - 1_000_000), receipt).faults


@pytest.mark.parametrize("left,right", [(1.0, 1.049), (.951, 1.0), (.949999999, 1.05)])
def test_no_extrapolation_or_over_tolerance_brackets(left, right):
    core = sync()
    target = 1.05 if left == 1.0 else (.95 if right == 1.0 else 1.0)
    for t in (left, right):
        core.add_pose(pose(t), ns(t))
        core.add_encoder(encoder(t), ns(t))
    now = max(1.1, right)
    assert push_components(core, components(source=target, publication=1.1), now) == []
    assert core.poll(ns(target + .500000001)).faults[0].reason == "pending_expired"


def test_yaw_and_encoder_wrap_short_arc():
    core = sync()
    for t, angle in ((.98, math.radians(179)), (1.02, math.radians(-179))):
        core.add_pose(pose(t, yaw=angle), ns(t))
        core.add_encoder(encoder(t, angle), ns(t))
    result = push_components(core, components(), 1.02)[0]
    assert abs(result.base_yaw) == pytest.approx(math.pi)
    assert abs(result.encoder_phase) == pytest.approx(math.pi)


def test_exact_pi_interpolation_rejected():
    core = sync()
    for t, angle in ((.98, 0.0), (1.02, math.pi)):
        core.add_pose(pose(t, yaw=angle), ns(t))
        core.add_encoder(encoder(t, angle), ns(t))
    raw, augmented, provenance = components()
    core.add_raw_cost(raw, ns(1.02))
    core.add_augmented(augmented, ns(1.02))
    assert core.add_provenance(provenance, ns(1.02)).faults[0].reason == "invalid_interpolation"


def test_head_of_line_missing_metadata_blocks_later_ready_cost():
    core = sync()
    for t in (1.0, 1.1):
        core.add_pose(pose(t), ns(t))
        core.add_encoder(encoder(t), ns(t))
    first = components(source=1.0, publication=1.0, receipt=1.1)
    second = components(source=1.1, publication=1.1, receipt=1.1, sequence=2)
    core.add_raw_cost(first[0], ns(1.1))
    assert push_components(core, second, 1.1) == []
    core.add_augmented(first[1], ns(1.1))
    batch = core.add_provenance(first[2], ns(1.1))
    assert [value.source_stamp_ns for value in batch.observations] == [ns(1), ns(1.1)]


def test_duplicate_consumed_key_idempotent_but_conflict_poisoned():
    core = sync()
    core.add_pose(pose(1.0), NS)
    core.add_encoder(encoder(1.0), NS)
    rows = components(publication=1.0)
    assert len(push_components(core, rows, 1.0)) == 1
    assert push_components(core, rows, 1.0) == []
    conflict = core.add_raw_cost(replace(rows[0], values=(99.0,)), NS)
    assert conflict.faults[0].reason == "conflicting_or_poisoned_key"
    assert core.add_raw_cost(rows[0], NS).faults


def test_distinct_float_cost_keys_are_not_merged_after_ns_rounding():
    core = sync()
    a = 1.0
    b = math.nextafter(a, math.inf)
    assert round(a * NS) == round(b * NS)
    core.add_raw_cost(RawCost(a, (-1.0,), NS), NS)
    core.add_raw_cost(RawCost(b, (-1.0,), NS), NS)
    assert len(core._pending) == 2


def test_duplicate_receipt_cannot_extend_pending_lifetime():
    core = sync()
    raw = RawCost(1.0, (-1.0,), NS)
    core.add_raw_cost(raw, NS)
    assert not core.add_raw_cost(replace(raw, receipt_ns=ns(1.4)), ns(1.4)).faults
    assert core._pending[1.0]["raw"].receipt_ns == NS
    assert core.poll(ns(1.500000001)).faults[0].reason == "pending_expired"


@pytest.mark.parametrize("change", [
    {"model_input_ns": ns(1.03)}, {"cost_publication_ns": ns(1.01)},
    {"sensor_world_phase": float("nan")}, {"channel_count": 0},
    {"sensor_xy": (float("inf"), 0.0)}, {"sensor_transform_valid": False},
    {"identity": replace(IDENTITY, run_id="wrong")},
])
def test_invalid_provenance_fails_closed(change):
    core = sync()
    assert core.add_provenance(replace(components()[2], **change), ns(1.02)).faults


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 1e308, -1.0])
def test_invalid_legacy_timestamp_fails_without_exception(value):
    assert sync().add_raw_cost(RawCost(value, (-1.0,), NS), NS).faults


def test_source_support_frame_rollback_capacity_and_clock_reset():
    core = sync(GescSyncConfig(max_source_samples=2))
    assert core.add_pose(replace(pose(1), frame_id="map"), NS).faults
    core.add_pose(pose(1), NS)
    core.add_pose(pose(1.01), ns(1.01))
    assert core.add_pose(pose(1.02), ns(1.02)).faults[0].reason == "support_capacity"
    core.add_encoder(encoder(1.03), ns(1.03))
    assert core.add_encoder(encoder(1.01, receipt=1.03), ns(1.03)).faults
    assert core.poll(ns(1)).faults[0].reason == "clock_rollback"
    assert not core._pending and not core._poses and not core._encoders


def test_pending_capacity_and_unchanged_context():
    core = sync(GescSyncConfig(max_pending_costs=2))
    for t in (1, 1.01):
        assert not core.add_raw_cost(RawCost(t, (-1.0,), ns(t)), ns(t)).faults
    before = core.reset_sequence
    assert not core.set_context(IDENTITY).faults
    assert core.reset_sequence == before
    assert core.add_raw_cost(RawCost(1.02, (-1.0,), ns(1.02)), ns(1.02)).faults[0].reason == "pending_capacity"


@pytest.mark.parametrize("direction", [-1, 1])
def test_three_real_cycles_qualify_and_same_objective_keeps_history(direction):
    core = RollingGesc()
    results = feed(core, times(9), phase=lambda t: direction * 2 * math.pi * t / 3)
    assert not any(result.qualified for result in results[:-1])
    result = results[-1]
    assert result.qualified
    assert result.completed_cycle_count == 3
    assert result.mean_world == pytest.approx((2, 0))
    assert len(result.cycles) == 3
    assert result.cycle_variability == pytest.approx(0, abs=1e-12)
    assert result.effective_magnitude_floor == pytest.approx(1e-6)
    assert result.sample_count == 120
    assert all(c.sample_count == 120 for c in result.cycles)
    before = result.reset_sequence
    assert core.set_context(IDENTITY, OBJECTIVE).reset_sequence == before
    output = core.evaluate(ns(9.05), math.pi / 2, ns(9.04))
    assert output.actual_blend_weight == .5
    assert output.final_body == pytest.approx((0, -2), abs=1e-12)
    assert output.output_valid and not output.fallback_used


def test_rotation_before_averaging_under_turning_base():
    core = RollingGesc()
    result = feed(core, times(9), vector=lambda t: (1.5, -.75),
                  yaw=lambda t: .4 * t)[-1]
    assert result.qualified
    assert result.mean_world == pytest.approx((1.5, -.75), abs=1e-12)
    assert all(c.mean_world == pytest.approx((1.5, -.75), abs=1e-12) for c in result.cycles)


def test_temporal_not_phase_weighted_quadrature_with_interpolated_start():
    core = RollingGesc()
    # Phase accelerates; q(t) is linear so time trapezoids have an exact oracle.
    phase = lambda t: .2 * t + .1 * t * t
    result = feed(core, times(10), vector=lambda t: (t, 2 * t + 1), phase=phase)[-1]
    assert result.mean_full
    start = result.rolling_start_ns / NS
    expected_t = .5 * (start + 10)
    assert result.mean_world == pytest.approx((expected_t, 2 * expected_t + 1), abs=2e-9)
    assert result.mean_world[0] != pytest.approx(8.5, abs=.01)


def test_nonuniform_sampling_linear_signal_equivalence():
    a, b = RollingGesc(), RollingGesc()
    fixed = times(9)
    irregular = [0.0] + [i / 40 + .004 * math.sin(i) for i in range(1, 360)] + [9.0]
    first = feed(a, fixed, vector=lambda t: (2 + .01 * t, -1 + .02 * t))[-1]
    second = feed(b, irregular, vector=lambda t: (2 + .01 * t, -1 + .02 * t))[-1]
    assert first.mean_world == pytest.approx(second.mean_world, abs=1e-11)
    for left, right in zip(first.cycles, second.cycles):
        assert left.mean_world == pytest.approx(right.mean_world, abs=1e-11)


def test_boundary_plateau_uses_first_crossing_and_does_not_add_revolution():
    core = RollingGesc()
    def phase(t):
        return 2 * math.pi * (t if t <= 3 else (3 if t <= 3.5 else t - .5)) / 3
    result = feed(core, times(6.5), phase=phase)[-1]
    assert result.completed_cycle_count == 2
    assert result.cycles[0].end_ns == 3 * NS
    assert result.cycles[1].start_ns == 3 * NS
    assert result.rolling_start_ns == 3 * NS
    assert result.rolling_duration_ns == ns(3.5)


def test_interpolated_boundary_points_do_not_count_as_observations():
    core = RollingGesc()
    # One actual observation per sector fails; synthetic quadrature edges cannot repair it.
    result = feed(core, times(9, rate=4))[-1]
    assert result.completed_cycle_count == 3
    assert all(c.sample_count == 12 for c in result.cycles)
    assert not result.qualified and not result.coverage_valid
    assert core.evaluate(9 * NS, 0, 9 * NS).fallback_used


def test_world_coverage_not_joint_phase_and_no_stop_for_missing_cycles():
    core = RollingGesc()
    result = feed(core, times(10), phase=lambda t: 0.0)[-1]
    assert result.completed_cycle_count == 0
    assert not result.mean_full
    output = core.evaluate(10 * NS, .3, 10 * NS)
    assert output.output_valid and output.fallback_used
    assert output.final_body == pytest.approx((2 * math.cos(.3), -2 * math.sin(.3)))


def test_reversal_discards_completed_confidence():
    core = RollingGesc()
    assert feed(core, times(9))[-1].qualified
    result = feed(core, [9.025], phase=lambda t: 6 * math.pi - .05)[-1]
    assert result.reset_reason == "phase_reversal"
    assert result.completed_cycle_count == 0 and not result.qualified
    assert core.evaluate(ns(9.025), 0, ns(9.025)).output_valid


@pytest.mark.parametrize("kind", ["gap", "rollback", "duplicate", "nan", "pi"])
def test_source_anomalies_clear_confidence(kind):
    core = RollingGesc()
    feed(core, times(9))
    t = 10 if kind == "gap" else (8 if kind == "rollback" else 9.025)
    sample = DemodulatedSample(observation(t, 2 * math.pi * t / 3), (2.0, 0.0))
    if kind == "duplicate":
        sample = DemodulatedSample(observation(9, 6 * math.pi), (9.0, 0.0))
    if kind == "nan":
        sample = replace(sample, q_body=(float("nan"), 0.0))
    if kind == "pi":
        sample = replace(sample, observation=replace(sample.observation, sensor_world_phase=7 * math.pi))
    result = core.update(sample)
    assert not result.qualified and result.completed_cycle_count == 0


def test_equal_sample_does_not_add_time_or_sector_counts():
    core = RollingGesc()
    result = feed(core, times(9))[-1]
    assert core.update(core._last_sample) == result


def test_objective_revision_resets_without_context_or_state_sequence():
    core = RollingGesc()
    feed(core, times(9))
    newer = ObjectiveIdentity(2, .5, 1, 0, "fill-new")
    result = feed(core, [9.025], objective=newer)[-1]
    assert not result.qualified and result.reset_reason == "objective_changed"
    conflict = replace(newer, gaussian_weight=.1)
    result = feed(core, [9.05], objective=conflict)[-1]
    assert result.reset_reason == "objective_revision_conflict"
    assert result.observation is None


def test_rms_vector_variability_uses_vector_not_only_magnitude():
    core = RollingGesc()
    # Continuous linear trend has exact three-cycle means 1.15,1.45,1.75.
    result = feed(core, times(9), vector=lambda t: (1 + .1 * t, 0))[-1]
    expected = math.sqrt((.3**2 + 0 + .3**2) / 3)
    assert result.cycle_variability == pytest.approx(expected, abs=1e-12)
    assert result.effective_magnitude_floor == pytest.approx(3 * expected, abs=1e-12)
    assert result.qualified


def test_all_pairs_not_only_adjacent_cycles_must_agree():
    # Reduce the configurable variability multiplier to isolate the pairwise gate;
    # production frozen default still uses 3.0 and is tested separately.
    core = RollingGesc(RollingGescConfig(variability_multiplier=0))
    result = feed(core, times(9), vector=lambda t: (math.cos(.12 * t), math.sin(.12 * t)))[-1]
    assert result.max_pair_angle_rad == pytest.approx(.72, abs=1e-10)
    assert not result.qualified
    assert result.fallback_reason == "cycle_disagreement"


@pytest.mark.parametrize("magnitude", [0.0, 1e-7, 1e-6])
def test_weak_mean_has_no_direction_confidence(magnitude):
    core = RollingGesc()
    result = feed(core, times(9), vector=lambda t: (magnitude, 0))[-1]
    assert not result.qualified and result.fallback_reason == "weak_cycle_direction"
    assert result.max_pair_angle_rad is None
    assert core.evaluate(9 * NS, 0, 9 * NS).output_valid


def test_zero_instantaneous_value_does_not_suppress_mean():
    core = RollingGesc()
    feed(core, times(9))
    result = feed(core, [9.025], vector=lambda t: (0.0, 0.0))[-1]
    assert result.qualified
    output = core.evaluate(ns(9.025), 0, ns(9.025))
    assert output.final_body[0] > .99


@pytest.mark.parametrize("now,pose_stamp,yaw", [
    (9.500000001, 9.5, 0), (9.1, 8.5, 0), (8.9, 8.9, 0),
    (9.1, 9.2, 0), (9.1, 9.1, float("nan")),
])
def test_stale_or_future_output_never_fabricates_valid_zero(now, pose_stamp, yaw):
    core = RollingGesc()
    feed(core, times(9))
    result = core.evaluate(ns(now), yaw, ns(pose_stamp))
    assert not result.output_valid and result.final_body is None
    assert not result.fallback_used


def test_duration_and_capacity_are_bounded():
    duration = RollingGesc(RollingGescConfig(max_cycle_duration_ns=NS))
    result = feed(duration, times(1.1))[-1]
    assert result.reset_reason == "cycle_duration"
    capacity = RollingGesc(RollingGescConfig(max_samples=3))
    result = feed(capacity, [0, .01, .02, .03])[-1]
    assert result.reset_reason == "sample_capacity"
    assert len(capacity._points) == 1


def test_complete_boundary_before_duration_limit_is_not_rejected_by_later_sample():
    core = RollingGesc(RollingGescConfig(max_cycle_duration_ns=3 * NS))
    result = feed(core, times(2.975) + [3.025])[-1]
    assert result.completed_cycle_count == 1
    assert result.cycles[0].end_ns == 3 * NS
    assert result.reset_reason != "cycle_duration"


def test_oldest_receipt_cannot_be_hidden_by_latest_join_receipt():
    core = RollingGesc()
    sample = observation(1, 0)
    sample = replace(sample, receipt_stamp_ns=ns(1.45), oldest_receipt_stamp_ns=ns(.95))
    core.update(DemodulatedSample(sample, (2.0, 0.0)))
    assert core.evaluate(ns(1.45), 0, ns(1.45)).output_valid
    assert not core.evaluate(ns(1.451), 0, ns(1.451)).output_valid


def test_output_clock_rollback_discards_confidence_even_without_new_source():
    core = RollingGesc()
    feed(core, times(9))
    assert core.evaluate(ns(9.1), 0, ns(9.1)).qualified
    result = core.evaluate(ns(9.05), 0, ns(9.05))
    assert not result.qualified and result.reset_reason == "clock_rollback"
    assert not core.evaluate(ns(9.1), 0, ns(9.1)).output_valid


def test_invalid_objective_and_direct_revision_conflict_fail_closed():
    core = RollingGesc()
    core.set_context(IDENTITY, OBJECTIVE)
    result = core.set_context(IDENTITY, replace(OBJECTIVE, sensor_weight=.5))
    assert result.reset_reason == "objective_revision_conflict"
    assert core.objective == OBJECTIVE
    result = core.update(DemodulatedSample(replace(observation(1, 0), objective=None), (1., 0.)))
    assert result.reset_reason == "invalid_sample"


def test_history_memory_remains_bounded_over_many_cycles():
    core = RollingGesc()
    result = feed(core, times(90))[-1]
    assert result.qualified
    assert len(core._cycles) == 3 and len(core._points) < 125


@pytest.mark.parametrize("vector,yaw", [((1e308, 1e308), 0), ((1.7e308, 1.7e308), .7),
                                       ((1.7e308, 1.7e308), 0)])
def test_finite_extreme_values_never_crash_or_claim_nonfinite_metric(vector, yaw):
    core = RollingGesc()
    sample = DemodulatedSample(observation(0, 0, yaw), vector)
    result = core.update(sample)
    if result.instantaneous_magnitude is not None:
        assert math.isfinite(result.instantaneous_magnitude)
    if result.output_valid:
        assert all(math.isfinite(v) for v in result.final_body)


@pytest.mark.parametrize("cls,kwargs", [
    (GescSyncConfig, {"freshness_ns": 0}), (GescSyncConfig, {"max_pending_costs": True}),
    (RollingGescConfig, {"max_samples": 0}), (RollingGescConfig, {"sectors": 13}),
    (RollingGescConfig, {"blend_weight": float("nan")}),
])
def test_invalid_configurations_rejected(cls, kwargs):
    with pytest.raises(ValueError):
        cls(**kwargs)
