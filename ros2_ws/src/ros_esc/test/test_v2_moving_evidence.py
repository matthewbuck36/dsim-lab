"""Synthetic source-time tests; neighborhood values are not calibration."""
import math
from copy import deepcopy
import pytest
from ros_esc_interfaces.msg import SynchronizedObservation
from ros_esc.v2_stream import set_time
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence
from ros_esc.supervisor_node.state_machine import (CandidateCostSummary,
    State, StateMachineConfig, SupervisorStateMachine, TransitionInputs)


def observation(t, *, phase=None, xy=(0., 0.), raw=None, objective=1):
    msg = SynchronizedObservation()
    msg.schema_version = 2
    msg.run_id = 'synthetic'
    msg.stream_contract_id = 'a' * 64
    msg.frame_id = 'odom'
    source = round(t * 1e9)
    for field in ('stamp', 'source_stamp', 'cost_source_stamp', 'pose_left_stamp',
                  'pose_right_stamp', 'encoder_left_stamp', 'encoder_right_stamp',
                  'receipt_stamp', 'oldest_receipt_stamp', 'admission_stamp'):
        set_time(getattr(msg, field), source)
    msg.sensor_world_phase_rad = float(2 * math.pi * t / 3 if phase is None else phase)
    msg.base_x_m, msg.base_y_m = map(float, xy)
    msg.raw_cost = float(-2 + .5 * math.cos(msg.sensor_world_phase_rad) if raw is None else raw)
    msg.augmented_cost = msg.raw_cost + objective
    msg.raw_cost_valid = msg.augmented_cost_valid = msg.synchronized_valid = True
    msg.sensor_transform_observed = True
    msg.observation_id = msg.source_sequence = source + 1
    msg.objective_revision = objective
    msg.legacy_cost_source_timestamp_sec = float(t)
    return msg


def feed(core, *, duration=9, dt=.025, position=lambda t:(0., 0.), cost=None, phase=None):
    for i in range(round(duration / dt) + 1):
        t = round(i * dt, 9)
        m = observation(t, xy=position(t), raw=cost(t) if cost else None,
                        phase=phase(t) if phase else None, objective=1 + int(t >= 4))
        core.add(m, 1 if t < 6 else 2, round((t + .01) * 1e9))


def ready(core, **kwargs):
    return core.evaluate((0., 0.), kwargs.pop('radius', .5), kwargs.pop('epsilon', .1),
                         kwargs.pop('confirmation_ns', 6_000_000_000), **kwargs)


def test_three_actual_cycles_pretrigger_provenance_and_boundary_assignment():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, duration=8.975)
    assert not ready(core).ready
    last = observation(9., objective=2)
    core.add(last, 2, 9_010_000_000)
    result = ready(core)
    assert result.ready and len(result.cycles) == 3
    assert result.summary.pretrigger_rotation_count == 2
    assert result.summary.verification_rotation_count == 1
    assert result.summary.rotation_count == 3
    assert result.summary.estimate == pytest.approx(-2.5)
    assignments = [i for a,b in result.sample_ranges for i in range(a,b)]
    assert len(assignments) == len(set(assignments)) == 360
    assert len(result.records) == 361  # final actual bracket is not a minimum
    assert result.records[-1].filter_state == 2
    assert result.amplitude > .3 and result.disagreement < .02


@pytest.mark.parametrize('dt', [.025, .04, .05])
def test_cadence_and_objective_revision_do_not_change_raw_cycle_semantics(dt):
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, dt=dt, position=lambda t:(.03*math.cos(2*math.pi*t/3), .03*math.sin(2*math.pi*t/3)))
    result = ready(core)
    assert result.ready
    assert all(math.hypot(*c.centroid) < 1e-4 for c in result.cycles)
    assert result.summary.estimate == pytest.approx(-2.5, abs=.002)


@pytest.mark.parametrize('value', [0., -3., 5.])
def test_zero_and_constant_are_uninformative_even_with_negative_minimum(value):
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, cost=lambda t:value)
    result = ready(core)
    assert not result.ready and not result.informative
    assert result.reason == 'uninformative_raw_profiles'
    assert dict(result.diagnostics)['signal_margin'] < 0


def test_rejection_diagnostics_distinguish_outer_support_from_fixed_center():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, position=lambda t:(.25, 0.))
    result = ready(core)
    detail = dict(result.diagnostics)
    assert result.reason == 'missing_qualified_neighborhood_cycles'
    assert detail['qualified_cycles'] == detail['inside_radius_cycles'] == 3
    assert detail['eligible_cycles'] == 0
    assert detail['nearest_inside_centroid_m'] == pytest.approx(.25)
    assert detail['centroid_tolerance_m'] == .1


def test_negative_cost_rejection_is_separate_from_signal_amplitude():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, cost=lambda t:2.+.5*math.cos(2*math.pi*t/3))
    result = ready(core)
    detail = dict(result.diagnostics)
    assert result.reason == 'uninformative_raw_profiles'
    assert detail['signal_margin'] > 0
    assert detail['baseline_negative_margin'] < 0
    assert detail['upper_cost_negative_margin'] < 0


def test_phase_incoherent_noise_is_vetoed():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, cost=lambda t:-2+.5*math.cos(2*math.pi*t/3 + (int(t/3)%3)*2*math.pi/3))
    result = ready(core)
    assert not result.ready and result.disagreement > result.amplitude


@pytest.mark.parametrize('position', [lambda t:(.6*math.cos(2*math.pi*t/3), .6*math.sin(2*math.pi*t/3)),
                                     lambda t:(.03*t, 0.)])
def test_large_loop_and_translation_fail_frozen_neighborhood(position):
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, position=position)
    assert not ready(core).ready


def test_shifted_sector_trajectories_fail_even_when_cycle_centroids_match():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, position=lambda t:(.2*math.cos(2*math.pi*t/3 + int(t/3)*math.pi/2),
                                 .2*math.sin(2*math.pi*t/3 + int(t/3)*math.pi/2)))
    result = ready(core)
    assert not result.ready and result.reason == 'incomparable_sector_trajectories'


def test_repeat_cannot_refresh_first_filter_state_and_conflict_resets():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    first = observation(1.)
    assert core.add(first, 1, 1_010_000_000)
    repeat = deepcopy(first); set_time(repeat.stamp, 1_100_000_000)
    assert not core.add(repeat, 2, 1_100_000_000)
    assert core.records[0].filter_state == 1
    assert core.records[0].filter_stamp_ns == 1_010_000_000
    repeat.raw_cost -= 1
    assert not core.add(repeat, 2, 1_100_000_000)
    assert core.reason == 'conflicting_observation' and not core.records
    assert not core.add(first, 1, 1_200_000_000)


def test_gap_reversal_epoch_and_revocation_reset_without_retiming():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, duration=3)
    assert len(core.cycles) == 1
    core.add(observation(4.), 2, 4_000_000_000)
    assert not core.cycles and core.records[0].stamp_ns == 4_000_000_000
    core.add(observation(4.1, phase=core.records[0].phase-.1), 2, 4_100_000_000)
    core.add(observation(4.2, phase=core.records[-1].phase+.1), 2, 4_200_000_000)
    assert len(core.records) == 1
    assert core.revoke(4_200_000_000)
    assert not core.records
    core.start_epoch(2, 5_000_000_000)
    assert not core.add(observation(4.2), 1, 5_000_000_000)
    assert core.add(observation(5.), 1, 5_000_000_000)


def test_capacity_rejects_without_implicit_decimation():
    core = MovingRawEvidence(max_observations=20); core.start_epoch(1, 0)
    feed(core, duration=.5)
    assert core.reason == 'observation_capacity' and not core.records
    core = MovingRawEvidence(max_snapshot=20); core.start_epoch(1, 0)
    feed(core)
    assert ready(core).reason == 'snapshot_capacity'


def test_first_arrival_boundary_dwell_stays_in_next_cycle():
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, duration=3)
    for i in range(1,5):
        core.add(observation(3+i*.1, phase=2*math.pi), 2, round((3+i*.1)*1e9))
    assert core.cycles[0].end_ns == 3_000_000_000
    assert core.cycle_start[0] == 3_000_000_000


def moving_machine(known=1):
    return SupervisorStateMachine(0., StateMachineConfig(moving_verification_enabled=True,
        extremum_classification_mode='counted_candidates', known_source_count=known, max_fill_clusters=known-1,
        candidate_cost_required_rotations=3))


def test_constant_known_one_cannot_take_vacuous_goal_and_deadline_resumes_search():
    machine = moving_machine()
    machine.step(0., TransitionInputs(convergence_confirmed=True))
    summary = CandidateCostSummary(-3.,0.,0.,3)
    assert machine.step(1., TransitionInputs(candidate_cost_valid=True,
        candidate_cost_ready=True, candidate_cost_summary=summary, candidate_informative=False)) is None
    transition = machine.step(12., TransitionInputs(candidate_informative=False))
    assert transition.current == State.SEARCH


def test_informative_negative_known_one_retains_goal_rule():
    machine = moving_machine()
    machine.step(0., TransitionInputs(convergence_confirmed=True))
    transition = machine.step(1., TransitionInputs(candidate_cost_valid=True,
        candidate_cost_ready=True, candidate_cost_summary=CandidateCostSummary(-3.,0.,0.,3),
        candidate_informative=True))
    assert transition.current == State.GOAL_HOLD


def test_moving_design_weights_and_redesign_original_escape_deadline():
    machine = moving_machine(known=2)
    machine._transition(State.VERIFY_EXTREMUM, 0., 'test')
    machine._transition(State.DESIGN_OR_MERGE_FILL, 1., 'test')
    assert machine.weights == (1.,1.,0.)
    machine._transition(State.ESCAPE_REPULSE, 2., 'test')
    machine.design_returns_to_assist = True
    machine._transition(State.DESIGN_OR_MERGE_FILL, 10., 'test')
    assert machine.weights == (0.,1.,0.)
    original = machine.escape_started_sec
    transition = machine.step(11., TransitionInputs(fill_result='rejected'))
    assert transition.current == State.ESCAPE_ASSIST and machine.escape_started_sec == original
    assert machine.step(22., TransitionInputs()).current == State.FAILSAFE


def test_partial_cycle_times_out_at_thirty_seconds_and_reseeds():
    core=MovingRawEvidence();core.start_epoch(1,0)
    feed(core,duration=30.,dt=.1,phase=lambda t:.01*t)
    old=core.reset_sequence
    core.add(observation(30.1,phase=.301),1,30_100_000_000)
    assert core.reset_sequence==old+1 and core.reason=='cycle_timeout'
    assert core.cycle_start[0]==30_100_000_000 and len(core.records)==1


def test_negative_rotation_and_wrapped_phases_form_actual_cycles():
    core=MovingRawEvidence();core.start_epoch(1,0)
    feed(core,phase=lambda t:math.atan2(math.sin(-2*math.pi*t/3),math.cos(-2*math.pi*t/3)))
    result=ready(core)
    assert result.ready and core.direction==-1
    assert all(c.end_phase<c.start_phase for c in result.cycles)


def test_interpolated_end_bracket_raw_cost_is_excluded_from_minimum_and_information():
    core=MovingRawEvidence();core.start_epoch(1,0)
    for i in range(130):
        t=i*.07
        value=-1e300 if t>9. else None
        core.add(observation(t,raw=value),1,round(t*1e9))
    result=ready(core)
    assert result.ready
    assert result.cycles[-1].end_ns==9_000_000_000
    assert result.records[-1].stamp_ns==9_030_000_000
    assert result.summary.estimate>-3 and result.information_floor==1e-6


def test_extreme_finite_raw_profiles_never_raise_or_qualify_numerical_overflow():
    core=MovingRawEvidence();core.start_epoch(1,0)
    feed(core,cost=lambda t:1e308*math.cos(2*math.pi*t/3))
    result=ready(core)
    assert not result.ready and result.reason in ('numerical_overflow','uninformative_raw_profiles')


def test_observation_identifier_reuse_at_new_source_time_is_a_conflict():
    core=MovingRawEvidence();core.start_epoch(1,0)
    first=observation(1.);core.add(first,1,1_000_000_000)
    newer=observation(1.1);newer.observation_id=first.observation_id
    assert not core.add(newer,1,1_100_000_000)
    assert not core.records and core.reason=='conflicting_observation'
    assert not core.add(first,1,1_200_000_000)
