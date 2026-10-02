"""Steering continuity while optional coherence work is pending; no devices."""

from dataclasses import replace
import math

import pytest

from ros_esc.gesc_v3.numerics.rolling import (
    DemodulatedSample, DirectionObservation, RollingGesc, compute_coherence,
)


def sample(index, *, frame='odom', revision=0, body=(1., .2), receipt_age=0):
    stamp = 1_000_000_000 + index*200_000_000
    return DemodulatedSample(DirectionObservation(
        index, stamp, stamp, 0., index*2*math.pi/15,
        revision, frame, stamp-receipt_age), body)


def accepted_owner(*, receipt_age=0):
    owner = RollingGesc()
    for i in range(47):
        last = sample(i, receipt_age=receipt_age)
        owner.update(last)
    assert owner.apply_coherence(compute_coherence(owner.coherence_job()))
    result = owner.evaluate(last.observation.source_stamp_ns, 0.,
                            last.observation.source_stamp_ns)
    assert result.qualified and result.actual_blend_weight == .75
    return owner, result


def test_pending_job_keeps_accepted_vector_and_original_age_with_current_yaw():
    owner, accepted = accepted_owner()
    new = sample(47, body=(-.5, -.2))
    owner.update(new)
    stamp = new.observation.source_stamp_ns
    assert owner.coherence_job().source_stamp_ns == stamp
    result = owner.evaluate(stamp, math.pi/2, stamp)
    assert result.qualified and result.actual_blend_weight == .75
    assert result.observation == accepted.observation  # no timestamp laundering
    assert result.final_body == pytest.approx((.2, -1.))
    # Deliberately stop completing jobs, but continue receiving observations.
    owner.update(sample(48, body=(-.5, -.2)))
    within = owner.evaluate(stamp+200_000_000, 0., stamp+200_000_000)
    assert within.final_body == pytest.approx((1., .2))
    expired = owner.evaluate(stamp+300_000_001, 0., stamp+300_000_001)
    assert expired.output_valid and expired.actual_blend_weight == 0.
    assert expired.final_body == pytest.approx((-.5, -.2))


def test_new_qualified_response_replaces_held_result():
    owner, accepted = accepted_owner()
    new = sample(47, body=(.8, .3))
    owner.update(new)
    response = compute_coherence(owner.coherence_job())
    assert owner.apply_coherence(response)
    result = owner.evaluate(new.observation.source_stamp_ns, 0.,
                            new.observation.source_stamp_ns)
    assert result.qualified and result.observation == new.observation
    assert result.observation != accepted.observation


def test_new_negative_coherence_result_revokes_old_acceptance():
    owner, _ = accepted_owner()
    new = sample(47, body=(-.5, -.2))
    owner.update(new)
    response = compute_coherence(owner.coherence_job())
    values = dict(response.values)
    values.update(qualified=False, reason='low_coherence')
    assert owner.apply_coherence(replace(response, values=tuple(values.items())))
    result = owner.evaluate(new.observation.source_stamp_ns, 0.,
                            new.observation.source_stamp_ns)
    assert result.actual_blend_weight == 0.
    owner.update(sample(48, body=(-.5, -.2)))
    result = owner.evaluate(10_600_000_000, 0., 10_600_000_000)
    assert result.actual_blend_weight == 0.  # rejection cannot resurrect a cache


@pytest.mark.parametrize('boundary', ['frame', 'objective', 'source_restart', 'phase_reversal'])
def test_direction_cannot_cross_context_or_history_reset(boundary):
    owner, _ = accepted_owner()
    new = sample(47, body=(-.5, -.2))
    if boundary == 'frame':
        new = replace(new, observation=replace(new.observation, frame_id='replacement'))
    elif boundary == 'objective':
        new = replace(new, observation=replace(new.observation, objective_revision=1))
    elif boundary == 'source_restart':
        owner.invalidate('source_restart')
    else:
        new = replace(new, observation=replace(new.observation,
                      sensor_world_phase=46*2*math.pi/15-.1))
    owner.update(new)
    result = owner.evaluate(new.observation.source_stamp_ns, 0.,
                            new.observation.source_stamp_ns)
    assert result.actual_blend_weight == 0.
    assert result.observation == new.observation


def test_oldest_receipt_age_can_expire_held_direction_before_source_age():
    owner, accepted = accepted_owner(receipt_age=350_000_000)
    new = sample(47, body=(-.5, -.2))
    owner.update(new)
    result = owner.evaluate(new.observation.source_stamp_ns, 0.,
                            new.observation.source_stamp_ns)
    assert result.output_valid and result.actual_blend_weight == 0.
    assert result.observation != accepted.observation


def test_cached_direction_does_not_hide_stale_live_pose_or_input():
    owner, _ = accepted_owner()
    new = sample(47)
    owner.update(new)
    stamp = new.observation.source_stamp_ns
    assert not owner.evaluate(stamp, 0., stamp-500_000_001).output_valid
    assert not owner.evaluate(stamp+500_000_001, 0., stamp+500_000_001).output_valid


def test_late_response_cannot_validate_current_snapshot():
    owner, _ = accepted_owner()
    owner.update(sample(47))
    late = compute_coherence(owner.coherence_job())
    owner.update(sample(48, body=(-.5, -.2)))
    assert not owner.apply_coherence(late)
    result = owner.evaluate(10_800_000_000, 0., 10_800_000_000)
    assert result.output_valid and result.actual_blend_weight == 0.
